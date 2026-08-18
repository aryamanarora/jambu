import { createHash } from 'node:crypto';
import { access, mkdir, readFile, readdir, rename, stat, writeFile } from 'node:fs/promises';
import { homedir, tmpdir } from 'node:os';
import { basename, dirname, isAbsolute, join, resolve } from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

export const CORRECTION_FIELDS = [
	'Entry_Key',
	'Status',
	'Form',
	'POS',
	'Gloss',
	'Notes',
	'Audit_Fingerprint',
	'Updated_At'
] as const;
export const REVIEW_STATUSES = ['accepted', 'corrected', 'illegible', 'skipped'] as const;

export type ReviewStatus = (typeof REVIEW_STATUSES)[number];
export type CsvRow = Record<string, string>;

type FieldConfig = {
	form?: string;
	pos?: string;
	gloss?: string;
	raw?: string[];
	metadata?: string[];
};

type CandidateFile = { path: string; key?: string; fields?: string[] };
type DocumentConfig = {
	id: string;
	label: string;
	filename: string;
	environment?: string;
	pageField: string;
	pageOffset?: number;
	cropTopField?: string;
	cropColumnBounds?: Record<string, [number, number]>;
};
type CropConfig = {
	topField: string;
	columnField?: string;
	columnBounds?: Record<string, [number, number]>;
	left?: number;
	right?: number;
	height?: number;
	verticalPadding?: number;
	referenceWidth?: number;
	referenceHeight?: number;
};

export type OcrSourceConfig = {
	id: string;
	label: string;
	audit: string;
	corrections: string;
	keyField?: string;
	pendingStatuses?: string[];
	fields?: FieldConfig;
	candidateFiles?: CandidateFile[];
	documents?: DocumentConfig[];
	crop?: CropConfig;
	inferred?: boolean;
};

type Manifest = { version: number; sources: OcrSourceConfig[] };

export type SourceSummary = {
	id: string;
	label: string;
	available: boolean;
	inferred: boolean;
	total: number;
	pending: number;
	reviewed: number;
	stale: number;
	documents: Array<{ id: string; label: string; available: boolean; filename: string }>;
};

export type WorkbenchRow = {
	key: string;
	status: string;
	auditStatus: string;
	form: string;
	pos: string;
	gloss: string;
	notes: string;
	fingerprint: string;
	stale: boolean;
	raw: Array<{ field: string; label: string; value: string }>;
	metadata: Array<{ field: string; label: string; value: string }>;
	documents: Array<{ id: string; label: string; available: boolean; page: number | null }>;
};

const DATA_ROOT = resolve(process.env.JAMBU_DATA_ROOT || resolve(process.cwd(), '../data'));
const MANIFEST = resolve(DATA_ROOT, 'data/ocr-postcorrection.json');
const AUDIT_DIR = resolve(DATA_ROOT, 'data/other/forms/raw_data');
const OCR_CACHE_DIR = resolve(DATA_ROOT, '.cache/ocr');
const IMAGE_CACHE = resolve(tmpdir(), 'jambu-ocr-postcorrector');

function insideData(path: string): string {
	const resolved = resolve(DATA_ROOT, path);
	if (resolved !== DATA_ROOT && !resolved.startsWith(`${DATA_ROOT}/`))
		throw new Error(`OCR workbench path escapes the data repository: ${path}`);
	return resolved;
}

export function parseCsv(text: string): { headers: string[]; rows: CsvRow[] } {
	const records: string[][] = [];
	let row: string[] = [];
	let field = '';
	let quoted = false;
	for (let index = 0; index < text.length; index++) {
		const char = text[index];
		if (quoted) {
			if (char === '"' && text[index + 1] === '"') {
				field += '"';
				index++;
			} else if (char === '"') quoted = false;
			else field += char;
		} else if (char === '"') quoted = true;
		else if (char === ',') {
			row.push(field);
			field = '';
		} else if (char === '\n') {
			row.push(field.replace(/\r$/, ''));
			records.push(row);
			row = [];
			field = '';
		} else field += char;
	}
	if (field || row.length) {
		row.push(field.replace(/\r$/, ''));
		records.push(row);
	}
	const headers = records.shift() ?? [];
	return {
		headers,
		rows: records
			.filter((record) => record.some(Boolean))
			.map((record) => Object.fromEntries(headers.map((header, index) => [header, record[index] ?? ''])))
	};
}

function csvCell(value: string): string {
	return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}

function writeCsv(headers: readonly string[], rows: CsvRow[]): string {
	return [
		headers.join(','),
		...rows.map((row) => headers.map((header) => csvCell(row[header] ?? '')).join(','))
	].join('\n') + '\n';
}

function prettyField(field: string): string {
	return field.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function firstField(headers: string[], candidates: string[]): string | undefined {
	return candidates
		.map((candidate) => headers.find((header) => header.toLocaleLowerCase() === candidate.toLocaleLowerCase()))
		.find((field): field is string => !!field);
}

function inferFields(headers: string[]): FieldConfig {
	const raw = headers.filter((field) => /(^raw_|ocr|printed_head|low_confidence|review_flags)/i.test(field));
	const metadata = headers.filter((field) =>
		/^(PDF_Page|Printed_Page|Page|Column|Column_Entry|Entry|Item|Mean_Confidence|Confidence|Uncertain|Status)$/.test(field)
	);
	return {
		form: firstField(headers, ['Form', 'Printed_Head', 'Headword', 'Word']),
		pos: firstField(headers, ['POS', 'Tags', 'Part_Of_Speech']),
		gloss: firstField(headers, ['Gloss', 'Definition', 'Sense', 'Meaning']),
		raw,
		metadata
	};
}

function looksLikeOcr(headers: string[], rows: CsvRow[], keyField?: string): boolean {
	return (
		!!keyField &&
		(headers.some((field) => /(ocr|low_confidence|duplicate_raw|raw_form_pos)/i.test(field)) ||
			rows.slice(0, 30).some((row) => /ocr|illegible|low.confidence/i.test(row.Status ?? '')))
	);
}

async function exists(path: string): Promise<boolean> {
	try {
		await access(path);
		return true;
	} catch {
		return false;
	}
}

async function configuredSources(): Promise<OcrSourceConfig[]> {
	const manifest = JSON.parse(await readFile(MANIFEST, 'utf8')) as Manifest;
	if (manifest.version !== 1 || !Array.isArray(manifest.sources))
		throw new Error('Unsupported OCR post-correction manifest');
	const sources = [...manifest.sources];
	const configuredAudits = new Set(sources.map((source) => resolve(DATA_ROOT, source.audit)));
	for (const filename of (await readdir(AUDIT_DIR)).filter((name) => name.endsWith('-audit.csv')).sort()) {
		const path = resolve(AUDIT_DIR, filename);
		if (configuredAudits.has(path)) continue;
		const parsed = parseCsv(await readFile(path, 'utf8'));
		const keyField = firstField(parsed.headers, ['Entry_Key']);
		if (!looksLikeOcr(parsed.headers, parsed.rows, keyField)) continue;
		const stem = filename.replace(/\.csv$/, '').replace(/^\d{8}-/, '').replace(/-audit$/, '');
		sources.push({
			id: stem,
			label: stem.replaceAll('-', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()),
			audit: path.slice(DATA_ROOT.length + 1),
			corrections: path.slice(DATA_ROOT.length + 1).replace(/-audit\.csv$/, '-corrections.csv'),
			keyField,
			fields: inferFields(parsed.headers),
			inferred: true
		});
	}
	if (await exists(OCR_CACHE_DIR)) {
		for (const directory of (await readdir(OCR_CACHE_DIR, { withFileTypes: true })).filter((entry) => entry.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))) {
			const outputDir = resolve(OCR_CACHE_DIR, directory.name, 'output');
			if (!(await exists(outputDir))) continue;
			for (const filename of (await readdir(outputDir)).filter((name) => name.endsWith('_entries.csv')).sort()) {
				const path = resolve(outputDir, filename);
				if (configuredAudits.has(path)) continue;
				const parsed = parseCsv(await readFile(path, 'utf8'));
				const keyField = firstField(parsed.headers, ['Entry_Key']);
				if (!keyField) continue;
				const id = directory.name.replace(/[^a-z0-9-]+/gi, '-').toLocaleLowerCase();
				if (sources.some((source) => source.id === id)) continue;
				sources.push({
					id,
					label: directory.name.replaceAll('-', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()),
					audit: path.slice(DATA_ROOT.length + 1),
					corrections: `data/ocr-corrections/${id}.csv`,
					keyField,
					fields: inferFields(parsed.headers),
					inferred: true
				});
			}
		}
	}
	const seen = new Set<string>();
	for (const source of sources) {
		if (!/^[a-z0-9][a-z0-9-]*$/.test(source.id)) throw new Error(`Invalid OCR source id: ${source.id}`);
		if (seen.has(source.id)) throw new Error(`Duplicate OCR source id: ${source.id}`);
		seen.add(source.id);
		insideData(source.audit);
		insideData(source.corrections);
	}
	return sources;
}

export async function getSource(sourceId: string): Promise<OcrSourceConfig> {
	const source = (await configuredSources()).find((candidate) => candidate.id === sourceId);
	if (!source) throw new Error(`Unknown OCR source: ${sourceId}`);
	return source;
}

export function auditFingerprint(headers: string[], row: CsvRow): string {
	const payload = headers.map((header) => `${header}\0${row[header] ?? ''}`).join('\x1e');
	return createHash('sha256').update(payload, 'utf8').digest('hex').slice(0, 16);
}

async function readCorrections(source: OcrSourceConfig): Promise<Map<string, CsvRow>> {
	const path = insideData(source.corrections);
	if (!(await exists(path))) return new Map();
	const { rows } = parseCsv(await readFile(path, 'utf8'));
	return new Map(rows.filter((row) => row.Entry_Key).map((row) => [row.Entry_Key, row]));
}

async function readAudit(source: OcrSourceConfig): Promise<{ headers: string[]; rows: CsvRow[] }> {
	const path = insideData(source.audit);
	return parseCsv(await readFile(path, 'utf8'));
}

async function readCandidates(source: OcrSourceConfig): Promise<Map<string, Array<{ field: string; label: string; value: string }>>> {
	const result = new Map<string, Array<{ field: string; label: string; value: string }>>();
	for (const candidate of source.candidateFiles ?? []) {
		const path = insideData(candidate.path);
		if (!(await exists(path))) continue;
		const { headers, rows } = parseCsv(await readFile(path, 'utf8'));
		const keyField = candidate.key ?? 'Entry_Key';
		const fields = candidate.fields ?? headers.filter((header) => header !== keyField);
		for (const row of rows) {
			const key = row[keyField];
			if (!key) continue;
			const values = fields
				.filter((field) => row[field])
				.map((field) => ({ field, label: prettyField(field), value: row[field] }));
			if (values.length) result.set(key, [...(result.get(key) ?? []), ...values]);
		}
	}
	return result;
}

function pendingStatus(source: OcrSourceConfig, auditStatus: string): boolean {
	if (source.pendingStatuses?.length) return source.pendingStatuses.includes(auditStatus);
	return !/^(already_reviewed|ingested|accepted|corrected|skipped|excluded)$/i.test(auditStatus);
}

async function resolveDocumentPath(document: DocumentConfig): Promise<string | null> {
	const candidates = [
		document.environment ? process.env[document.environment] : undefined,
		process.env.JAMBU_OCR_SOURCE_DIR ? join(process.env.JAMBU_OCR_SOURCE_DIR, document.filename) : undefined,
		join(homedir(), 'Downloads', document.filename),
		join(DATA_ROOT, '.cache/ocr/sources', document.filename)
	].filter((candidate): candidate is string => !!candidate);
	for (const candidate of candidates) {
		const path = isAbsolute(candidate) ? candidate : resolve(candidate);
		if (basename(path) === document.filename || candidate === process.env[document.environment ?? '']) {
			if (await exists(path)) return path;
		}
	}
	return null;
}

function rowDocuments(source: OcrSourceConfig, row: CsvRow, availability: Map<string, boolean>) {
	return (source.documents ?? []).map((document) => {
		const rawPage = Number(row[document.pageField]);
		const page = Number.isFinite(rawPage) && rawPage > 0 ? rawPage + (document.pageOffset ?? 0) : null;
		return {
			id: document.id,
			label: document.label,
			available: availability.get(document.id) ?? false,
			page: page && page > 0 ? page : null
		};
	});
}

async function sourceRows(source: OcrSourceConfig): Promise<{ headers: string[]; rows: WorkbenchRow[] }> {
	const { headers, rows } = await readAudit(source);
	const keyField = source.keyField ?? firstField(headers, ['Entry_Key']);
	if (!keyField) throw new Error(`${source.audit} has no Entry_Key column`);
	const seenKeys = new Set<string>();
	for (const row of rows) {
		const key = row[keyField];
		if (!key) throw new Error(`${source.audit} contains an empty ${keyField}`);
		if (seenKeys.has(key)) throw new Error(`${source.audit} contains duplicate entry key ${key}`);
		seenKeys.add(key);
	}
	const fields = { ...inferFields(headers), ...(source.fields ?? {}) };
	const corrections = await readCorrections(source);
	const candidates = await readCandidates(source);
	const availability = new Map<string, boolean>();
	for (const document of source.documents ?? []) availability.set(document.id, !!(await resolveDocumentPath(document)));
	return {
		headers,
		rows: rows.map((row) => {
			const key = row[keyField];
			const correction = corrections.get(key);
			const fingerprint = auditFingerprint(headers, row);
			const auditStatus = row.Status || 'needs_review';
			const stale = !!correction?.Audit_Fingerprint && correction.Audit_Fingerprint !== fingerprint;
			const status = correction?.Status || (pendingStatus(source, auditStatus) ? 'pending' : auditStatus);
			const rawFields = (fields.raw ?? [])
				.filter((field) => row[field])
				.map((field) => ({ field, label: prettyField(field), value: row[field] }));
			return {
				key,
				status,
				auditStatus,
				form: correction?.Form || row[fields.form ?? ''] || '',
				pos: correction?.POS || row[fields.pos ?? ''] || '',
				gloss: correction?.Gloss || row[fields.gloss ?? ''] || '',
				notes: correction?.Notes || '',
				fingerprint,
				stale,
				raw: [...rawFields, ...(candidates.get(key) ?? [])],
				metadata: (fields.metadata ?? [])
					.filter((field) => row[field])
					.map((field) => ({ field, label: prettyField(field), value: row[field] })),
				documents: rowDocuments(source, row, availability)
			};
		})
	};
}

export async function listSources(): Promise<SourceSummary[]> {
	const summaries: SourceSummary[] = [];
	for (const source of await configuredSources()) {
		const auditPath = insideData(source.audit);
		if (!(await exists(auditPath))) {
			summaries.push({ id: source.id, label: source.label, available: false, inferred: !!source.inferred, total: 0, pending: 0, reviewed: 0, stale: 0, documents: [] });
			continue;
		}
		const { rows } = await sourceRows(source);
		const documents = await Promise.all((source.documents ?? []).map(async (document) => ({
			id: document.id,
			label: document.label,
			available: !!(await resolveDocumentPath(document)),
			filename: document.filename
		})));
		summaries.push({
			id: source.id,
			label: source.label,
			available: true,
			inferred: !!source.inferred,
			total: rows.length,
			pending: rows.filter((row) => row.status === 'pending').length,
			reviewed: rows.filter((row) => REVIEW_STATUSES.includes(row.status as ReviewStatus)).length,
			stale: rows.filter((row) => row.stale).length,
			documents
		});
	}
	return summaries;
}

export async function queryRows(sourceId: string, query: string, status: string, page: number, pageSize = 50) {
	const source = await getSource(sourceId);
	const { rows } = await sourceRows(source);
	const q = query.trim().toLocaleLowerCase();
	const filtered = rows.filter((row) => {
		if (status && status !== 'all') {
			if (status === 'reviewed' && !REVIEW_STATUSES.includes(row.status as ReviewStatus)) return false;
			else if (status === 'stale' && !row.stale) return false;
			else if (!['reviewed', 'stale'].includes(status) && row.status !== status) return false;
		}
		if (!q) return true;
		return [row.key, row.form, row.pos, row.gloss, row.auditStatus, ...row.raw.map((field) => field.value)]
			.some((value) => value.toLocaleLowerCase().includes(q));
	});
	const safePage = Math.max(1, page);
	return {
		source: { id: source.id, label: source.label, inferred: !!source.inferred },
		rows: filtered.slice((safePage - 1) * pageSize, safePage * pageSize),
		count: filtered.length,
		page: safePage,
		pageSize,
		counts: {
			all: rows.length,
			pending: rows.filter((row) => row.status === 'pending').length,
			reviewed: rows.filter((row) => REVIEW_STATUSES.includes(row.status as ReviewStatus)).length,
			stale: rows.filter((row) => row.stale).length
		}
	};
}

export async function saveCorrection(sourceId: string, input: CsvRow & { remove?: boolean }): Promise<ReviewStatus | null> {
	const source = await getSource(sourceId);
	const { headers, rows: auditRows } = await readAudit(source);
	const keyField = source.keyField ?? firstField(headers, ['Entry_Key']);
	if (!keyField) throw new Error(`${source.audit} has no Entry_Key column`);
	const entryKey = input.Entry_Key?.trim();
	const auditRow = auditRows.find((row) => row[keyField] === entryKey);
	if (!entryKey || !auditRow) throw new Error('Choose a valid OCR audit entry');
	const path = insideData(source.corrections);
	let rows: CsvRow[] = [];
	if (await exists(path)) rows = parseCsv(await readFile(path, 'utf8')).rows;
	rows = rows.filter((row) => row.Entry_Key !== entryKey);
	if (!input.remove) {
		if (!REVIEW_STATUSES.includes(input.Status as ReviewStatus)) throw new Error('Choose a valid review status');
		const form = (input.Form ?? '').normalize('NFC').trim();
		if ((input.Status === 'accepted' || input.Status === 'corrected') && !form)
			throw new Error('Accepted and corrected entries require a form');
		const fields = { ...inferFields(headers), ...(source.fields ?? {}) };
		const baseline = {
			form: (auditRow[fields.form ?? ''] ?? '').normalize('NFC').trim(),
			pos: (auditRow[fields.pos ?? ''] ?? '').normalize('NFC').trim(),
			gloss: (auditRow[fields.gloss ?? ''] ?? '').normalize('NFC').trim()
		};
		const pos = (input.POS ?? '').normalize('NFC').trim();
		const gloss = (input.Gloss ?? '').normalize('NFC').trim();
		const status: ReviewStatus = input.Status === 'accepted' && (form !== baseline.form || pos !== baseline.pos || gloss !== baseline.gloss)
			? 'corrected'
			: input.Status as ReviewStatus;
		const currentFingerprint = auditFingerprint(headers, auditRow);
		if (input.Audit_Fingerprint && input.Audit_Fingerprint !== currentFingerprint)
			throw new Error('The OCR audit changed since this entry was loaded; reload before saving');
		rows.push({
			Entry_Key: entryKey,
			Status: status,
			Form: form,
			POS: pos,
			Gloss: gloss,
			Notes: (input.Notes ?? '').normalize('NFC').trim(),
			Audit_Fingerprint: currentFingerprint,
			Updated_At: new Date().toISOString()
		});
	}
	rows.sort((left, right) => left.Entry_Key.localeCompare(right.Entry_Key));
	await mkdir(dirname(path), { recursive: true });
	const temporary = `${path}.${process.pid}.tmp`;
	await writeFile(temporary, writeCsv(CORRECTION_FIELDS, rows), 'utf8');
	await rename(temporary, path);
	return input.remove ? null : rows.find((row) => row.Entry_Key === entryKey)?.Status as ReviewStatus;
}

async function pdfPageSize(path: string, page: number): Promise<[number, number]> {
	const { stdout } = await execFileAsync('pdfinfo', ['-f', String(page), '-l', String(page), path], { maxBuffer: 1024 * 1024 });
	const match = stdout.match(/Page\s+(?:\d+\s+)?size:\s*([\d.]+)\s+x\s+([\d.]+)\s+pts/i);
	if (!match) throw new Error(`Could not read PDF page size for page ${page}`);
	return [Number(match[1]), Number(match[2])];
}

export async function renderDocumentImage(sourceId: string, documentId: string, entryKey: string, view: 'crop' | 'page'): Promise<Uint8Array> {
	const source = await getSource(sourceId);
	const document = source.documents?.find((candidate) => candidate.id === documentId);
	if (!document) throw new Error('Unknown source document');
	const documentPath = await resolveDocumentPath(document);
	if (!documentPath) throw new Error(`${document.filename} is unavailable; set ${document.environment || 'JAMBU_OCR_SOURCE_DIR'}`);
	const { rows } = await readAudit(source);
	const headers = rows.length ? Object.keys(rows[0]) : [];
	const keyField = source.keyField ?? firstField(headers, ['Entry_Key']);
	const row = rows.find((candidate) => keyField && candidate[keyField] === entryKey);
	if (!row) throw new Error('Unknown OCR audit entry');
	const page = Number(row[document.pageField]) + (document.pageOffset ?? 0);
	if (!Number.isInteger(page) || page < 1) throw new Error('This entry has no valid source page');
	const sourceStat = await stat(documentPath);
	const auditStat = await stat(insideData(source.audit));
	const cacheKey = createHash('sha256')
		.update(`${documentPath}\0${sourceStat.mtimeMs}\0${auditStat.mtimeMs}\0${page}\0${entryKey}\0${view}\0${JSON.stringify(source.crop ?? {})}\0${JSON.stringify(document)}`)
		.digest('hex').slice(0, 20);
	const outputDir = resolve(IMAGE_CACHE, source.id, document.id);
	const outputPath = resolve(outputDir, `${cacheKey}.png`);
	if (await exists(outputPath)) return new Uint8Array(await readFile(outputPath));
	await mkdir(outputDir, { recursive: true });
	const prefix = resolve(outputDir, `${cacheKey}.rendering`);
	const args = ['-f', String(page), '-l', String(page), '-singlefile', '-png', '-r', '180'];
	if (view === 'crop' && source.crop) {
		const [pageWidth, pageHeight] = await pdfPageSize(documentPath, page);
		const crop = source.crop;
		const column = crop.columnField ? row[crop.columnField] : '';
		const columnBounds = document.cropColumnBounds ?? crop.columnBounds;
		const bounds = (column && columnBounds?.[column]) || (crop.left != null && crop.right != null ? [crop.left, crop.right] as [number, number] : null);
		const topValue = row[document.cropTopField ?? crop.topField];
		const top = topValue === '' || topValue == null ? Number.NaN : Number(topValue);
		if (bounds && Number.isFinite(top)) {
			const dpiScale = 180 / 72;
			const xScale = pageWidth / (crop.referenceWidth ?? pageWidth);
			const yScale = pageHeight / (crop.referenceHeight ?? pageHeight);
			const padding = crop.verticalPadding ?? 6;
			const left = Math.max(0, bounds[0] * xScale);
			const right = Math.min(pageWidth, bounds[1] * xScale);
			const cropTop = Math.max(0, (top - padding) * yScale);
			const cropHeight = Math.min(pageHeight - cropTop, (crop.height ?? 40) * yScale);
			args.push('-x', String(Math.round(left * dpiScale)), '-y', String(Math.round(cropTop * dpiScale)), '-W', String(Math.round((right - left) * dpiScale)), '-H', String(Math.round(cropHeight * dpiScale)));
		}
	}
	args.push(documentPath, prefix);
	await execFileAsync('pdftoppm', args, { maxBuffer: 4 * 1024 * 1024 });
	const rendered = `${prefix}.png`;
	await rename(rendered, outputPath);
	return new Uint8Array(await readFile(outputPath));
}
