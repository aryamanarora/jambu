import { dev } from '$app/environment';
import { error, json } from '@sveltejs/kit';
import { readFile, rename, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { getDb, ids } from '$lib/server/db';
import { readDeltas, readVarints, FLAG_SECTION, REL_LOCAL } from '$lib/dbShared';
import type { RequestHandler } from './$types';

// ---- v2-schema helpers (dev-only tool, so simple full-scan caches are fine) ----

type CiteInfo = { short: string; refId: string };
let _citeInfo: Map<number, CiteInfo & { locator: string; refRid: number }> | null = null;
function citeInfo() {
	if (!_citeInfo) {
		const db = getDb();
		const refs = new Map(
			(db.prepare('SELECT rowid AS rid, id, short FROM "references"').all() as {
				rid: number;
				id: string;
				short: string | null;
			}[]).map((r) => [r.rid, r])
		);
		_citeInfo = new Map(
			(db.prepare('SELECT rowid AS rid, ref_rid, locator FROM cites').all() as {
				rid: number;
				ref_rid: number;
				locator: string;
			}[]).map((c) => {
				const ref = refs.get(c.ref_rid);
				return [
					c.rid,
					{
						short: ref?.short || ref?.id || String(c.ref_rid),
						refId: ref?.id ?? String(c.ref_rid),
						locator: c.locator,
						refRid: c.ref_rid
					}
				];
			})
		);
	}
	return _citeInfo;
}

function sourcesOf(cites: Buffer | null): { source_ids: string | null; sources: string | null } {
	if (!cites) return { source_ids: null, sources: null };
	const info = citeInfo();
	const ids_ = new Set<string>();
	const labels = new Set<string>();
	for (const cid of readVarints(new Uint8Array(cites))) {
		const c = info.get(cid);
		if (!c) continue;
		ids_.add(c.refId);
		labels.add(c.locator !== '' ? `${c.short}, ${c.locator}` : c.short);
	}
	return {
		source_ids: ids_.size ? [...ids_].join(',') : null,
		sources: labels.size ? [...labels].join(',') : null
	};
}

function citeIdsOfRef(refId: string): number[] {
	const out: number[] = [];
	for (const [cid, c] of citeInfo()) if (c.refId === refId) out.push(cid);
	return out;
}

// entry rid → concept ids, and lemma rid → concept ids (decoded once from concepts.rids)
let _conceptIndex: { byLemma: Map<number, Set<number>>; byEntry: Map<number, Set<number>> } | null =
	null;
function conceptIndex() {
	if (!_conceptIndex) {
		const db = getDb();
		const originOf = new Map(
			(db.prepare('SELECT rowid AS rid, origin_rid, flags FROM lem').all() as {
				rid: number;
				origin_rid: number | null;
				flags: number;
			}[]).map((r) => [r.rid, r])
		);
		const byLemma = new Map<number, Set<number>>();
		const byEntry = new Map<number, Set<number>>();
		for (const c of db.prepare('SELECT id, rids FROM concepts WHERE rids IS NOT NULL').all() as {
			id: number;
			rids: Buffer;
		}[]) {
			for (const rid of readDeltas(new Uint8Array(c.rids))) {
				(byLemma.get(rid) ?? byLemma.set(rid, new Set()).get(rid)!).add(c.id);
				const info = originOf.get(rid);
				if (!info || (info.flags & 7) === REL_LOCAL) continue;
				const entry = info.origin_rid ?? rid;
				(byEntry.get(entry) ?? byEntry.set(entry, new Set()).get(entry)!).add(c.id);
			}
		}
		_conceptIndex = { byLemma, byEntry };
	}
	return _conceptIndex;
}

export const prerender = false;

const ASSIGNMENTS = resolve(process.cwd(), '../data/data/etymology-assignments.csv');
const FIELDS = ['Form_ID', 'Etymon_ID', 'Relation', 'Status', 'Notes'] as const;

function localOnly(request: Request) {
	if (!dev) error(404, 'Not found');
	const host = new URL(request.url).hostname;
	if (!['localhost', '127.0.0.1', '::1'].includes(host)) error(403, 'Development interface is local-only');
}

function parseCsv(text: string): string[][] {
	const rows: string[][] = [];
	let row: string[] = [];
	let field = '';
	let quoted = false;
	for (let i = 0; i < text.length; i++) {
		const char = text[i];
		if (quoted) {
			if (char === '"' && text[i + 1] === '"') {
				field += '"';
				i++;
			} else if (char === '"') quoted = false;
			else field += char;
		} else if (char === '"') quoted = true;
		else if (char === ',') {
			row.push(field);
			field = '';
		} else if (char === '\n') {
			row.push(field.replace(/\r$/, ''));
			rows.push(row);
			row = [];
			field = '';
		} else field += char;
	}
	if (field || row.length) {
		row.push(field);
		rows.push(row);
	}
	return rows;
}

function csvCell(value: string): string {
	return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}

type Assignment = Record<(typeof FIELDS)[number], string>;

type CandidateRow = {
	id: string;
	word: string;
	gloss: string;
	language_id: string;
	language: string;
	reflex_count: number;
	lang_count: number;
	sources: string | null;
};

function soundKey(value: string): string[] {
	return [...(value ?? '')
		.normalize('NFD')
		.toLocaleLowerCase()
		.replace(/[\p{M}\s*\-‐‑‒–—―'’ʔˀ.·|()[\]{}\/\\]/gu, '')];
}

function soundSimilarity(left: string, right: string): number {
	const a = soundKey(left);
	const b = soundKey(right);
	if (!a.length || !b.length) return 0;
	let previous = Array.from({ length: b.length + 1 }, (_, index) => index);
	for (let i = 1; i <= a.length; i++) {
		const current = [i];
		for (let j = 1; j <= b.length; j++) {
			current[j] = Math.min(
				current[j - 1] + 1,
				previous[j] + 1,
				previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)
			);
		}
		previous = current;
	}
	return Math.max(0, 1 - previous[b.length] / Math.max(a.length, b.length));
}

async function readAssignments(): Promise<Assignment[]> {
	let text = '';
	try {
		text = await readFile(ASSIGNMENTS, 'utf8');
	} catch (cause) {
		if ((cause as NodeJS.ErrnoException).code !== 'ENOENT') throw cause;
	}
	const rows = parseCsv(text);
	const header = rows.shift() ?? [...FIELDS];
	return rows
		.filter((row) => row.some(Boolean))
		.map((row) => Object.fromEntries(FIELDS.map((field) => [field, row[header.indexOf(field)] ?? ''])) as Assignment);
}

async function writeAssignments(rows: Assignment[]): Promise<void> {
	const text = [
		FIELDS.join(','),
		...rows
			.sort((a, b) => a.Form_ID.localeCompare(b.Form_ID))
			.map((row) => FIELDS.map((field) => csvCell(row[field] ?? '')).join(','))
	].join('\n') + '\n';
	const temporary = `${ASSIGNMENTS}.tmp`;
	await writeFile(temporary, text, 'utf8');
	await rename(temporary, ASSIGNMENTS);
}

export const GET: RequestHandler = async ({ request, url }) => {
	localOnly(request);
	const db = getDb();
	const mode = url.searchParams.get('mode') ?? 'queue';
	const q = (url.searchParams.get('q') ?? '').trim().toLocaleLowerCase();
	const like = `%${q}%`;

	if (mode === 'candidates') {
		const idx = ids();
		const formId = url.searchParams.get('form') ?? '';
		const formRid = idx.ridOf(formId);
		const selected = formRid
			? (db
					.prepare(
						`SELECT l.rowid AS rowid, l.word, l.phonemic, lang.id AS language_id
						 FROM lem l LEFT JOIN languages lang ON lang.rowid = l.lang_rid WHERE l.rowid = ?`
					)
					.get(formRid) as
					| { rowid: number; word: string; phonemic: string | null; language_id: string }
					| undefined)
			: undefined;
		const selectedConcepts = selected
			? [...(conceptIndex().byLemma.get(selected.rowid) ?? [])]
			: [];
		// candidate entries carrying any of the selected concepts (via any attestation)
		const conceptEntryRids: number[] = [];
		if (selectedConcepts.length) {
			const wanted = new Set(selectedConcepts);
			for (const [entry, cids] of conceptIndex().byEntry) {
				for (const c of cids)
					if (wanted.has(c)) {
						conceptEntryRids.push(entry);
						break;
					}
			}
		}
		const exactRid = idx.ridOf(q) ?? -1;
		const rows = (db
			.prepare(
				`SELECT l.rowid AS rid, l.word, l.gloss, l.counts, l.cites,
				        lang.id AS language_id, lang.name AS language
				 FROM lem l
				 LEFT JOIN languages lang ON lang.rowid = l.lang_rid
				 WHERE l.origin_rid IS NULL AND (l.flags & 7) != ${REL_LOCAL}
				   AND (? = '' OR l.rowid = ? OR instr(lower(l.word), ?) > 0
				        OR instr(lower(l.gloss), ?) > 0 OR instr(lower(lang.name), ?) > 0
				        OR l.rowid IN (SELECT value FROM json_each(?)))
				 ORDER BY CASE WHEN l.rowid = ? THEN 0 WHEN lower(l.word) = ? THEN 1
				               WHEN lower(l.gloss) = ? THEN 2 ELSE 3 END,
				          (l.counts / 1024) DESC, l.ord
				 LIMIT 400`
			)
			.all(q, exactRid, q, q, q, JSON.stringify(conceptEntryRids), exactRid, q, q) as {
			rid: number;
			word: string;
			gloss: string;
			counts: number | null;
			cites: Buffer | null;
			language_id: string;
			language: string;
		}[]).map((r) => ({
			id: idx.idOf(r.rid),
			rid: r.rid,
			word: r.word,
			gloss: r.gloss,
			language_id: r.language_id,
			language: r.language,
			reflex_count: r.counts != null ? r.counts >> 10 : 0,
			lang_count: r.counts != null ? r.counts % 1024 : 0,
			sources: sourcesOf(r.cites).sources
		})) as (CandidateRow & { rid: number })[];

		if (!selected || !rows.length) return json({ rows: rows.slice(0, 80) });
		const candidateRids = rows.map((row) => row.rid);
		const conceptsByCandidate = new Map<string, Set<number>>();
		for (const row of rows) {
			const set = conceptIndex().byEntry.get(row.rid);
			if (set) conceptsByCandidate.set(row.id, set);
		}

		const reflexRows = (db
			.prepare(
				`SELECT att.origin_rid AS origin_rid, att.word, att.phonemic,
				        lang.id AS language_id, lang.name AS language
				 FROM lem att LEFT JOIN languages lang ON lang.rowid = att.lang_rid
				 WHERE att.origin_rid IN (SELECT value FROM json_each(?))
				   AND (att.link_rid IS NULL OR (att.flags & 7) IN (2, 3))`
			)
			.all(JSON.stringify(candidateRids)) as {
			origin_rid: number;
			word: string;
			phonemic: string | null;
			language_id: string;
			language: string;
		}[]).map((r) => ({
			candidate_id: idx.idOf(r.origin_rid),
			word: r.word,
			phonemic: r.phonemic,
			language_id: r.language_id,
			language: r.language
		}));
		const selectedSound = selected.phonemic || selected.word;
		const bestReflex = new Map<string, { score: number; word: string; language: string }>();
		for (const reflex of reflexRows) {
			const raw = soundSimilarity(selectedSound, reflex.phonemic || reflex.word);
			const score = raw * (reflex.language_id === selected.language_id ? 1 : 0.82);
			if (score > (bestReflex.get(reflex.candidate_id)?.score ?? -1))
				bestReflex.set(reflex.candidate_id, { score, word: reflex.word, language: reflex.language });
		}
		const selectedConceptSet = new Set(selectedConcepts);
		const scored = rows.map((row) => {
			const candidateConcepts = conceptsByCandidate.get(row.id) ?? new Set<number>();
			const conceptMatches = [...selectedConceptSet].filter((concept) => candidateConcepts.has(concept)).length;
			const concept_score = selectedConceptSet.size ? conceptMatches / selectedConceptSet.size : 0;
			const sound_score = soundSimilarity(selectedSound, row.word);
			const cognate = bestReflex.get(row.id);
			const cognate_score = cognate?.score ?? 0;
			const confidence = Math.round(100 * (0.45 * concept_score + 0.2 * sound_score + 0.35 * cognate_score));
			return {
				...row,
				confidence,
				concept_score: Math.round(concept_score * 100),
				sound_score: Math.round(sound_score * 100),
				cognate_score: Math.round(cognate_score * 100),
				best_cognate: cognate ? `${cognate.word} · ${cognate.language}` : null
			};
		});
		scored.sort((a, b) => b.confidence - a.confidence || b.reflex_count - a.reflex_count || a.id.localeCompare(b.id));
		return json({ rows: scored.slice(0, 80) });
	}

	const idx = ids();
	const language = url.searchParams.get('language') ?? '';
	const source = url.searchParams.get('source') ?? '';
	const page = Math.max(1, Number(url.searchParams.get('page') ?? 1));
	const offset = (page - 1) * 50;
	const sourceCites = source ? citeIdsOfRef(source) : [];
	const where = `(l.flags & 7) = ${REL_LOCAL}
		AND (? = '' OR instr(lower(l.word), ?) > 0 OR instr(lower(l.gloss), ?) > 0
		     OR instr(lower(COALESCE(l.notes, '')), ?) > 0 OR instr(lower(lang.name), ?) > 0)
		AND (? = '' OR lang.id = ?)
		AND (? = '' OR vin_any(l.cites, ?) = 1)`;
	const params = [q, q, q, q, q, language, language, source, JSON.stringify(sourceCites)];
	const rows = (db
		.prepare(
			`SELECT l.rowid AS rid, l.word, l.gloss, l.phonemic, l.notes, l.cites,
			        lang.id AS language_id, lang.name AS language
			 FROM lem l JOIN languages lang ON lang.rowid = l.lang_rid
			 WHERE ${where}
			 ORDER BY lang."order", lang.name, l.ord LIMIT 50 OFFSET ?`
		)
		.all(...params, offset) as {
		rid: number;
		word: string;
		gloss: string;
		phonemic: string | null;
		notes: string | null;
		cites: Buffer | null;
		language_id: string;
		language: string;
	}[]).map((r) => ({
		id: idx.idOf(r.rid),
		word: r.word,
		gloss: r.gloss,
		phonemic: r.phonemic,
		notes: r.notes ?? '',
		language_id: r.language_id,
		language: r.language,
		...sourcesOf(r.cites)
	}));
	const count = (db.prepare(`SELECT COUNT(*) AS n FROM lem l JOIN languages lang ON lang.rowid=l.lang_rid WHERE ${where}`).get(...params) as { n: number }).n;
	const languages = db
		.prepare(`SELECT id, name FROM languages WHERE rowid IN (SELECT DISTINCT lang_rid FROM lem WHERE (flags & 7) = ${REL_LOCAL}) ORDER BY "order", name`)
		.all();
	const sources = db
		.prepare(`SELECT id, short FROM "references" WHERE unetymologised_count > 0 ORDER BY short`)
		.all();
	const assignments = await readAssignments();
	return json({ rows, count, page, languages, sources, assignments });
};

export const POST: RequestHandler = async ({ request }) => {
	localOnly(request);
	const body = (await request.json()) as Partial<Assignment> & { remove?: boolean };
	const formId = body.Form_ID?.trim() ?? '';
	if (!/^f_[a-z2-7]{13}$/.test(formId)) error(400, 'A persistent form ID is required; rebuild the data first');
	const db = getDb();
	if (ids().ridOf(formId) == null) error(400, 'Unknown form ID');

	let rows = await readAssignments();
	rows = rows.filter((row) => row.Form_ID !== formId);
	if (!body.remove) {
		const etymonId = body.Etymon_ID?.trim() ?? '';
		const etymonRid = etymonId ? ids().ridOf(etymonId) : null;
		if (
			etymonRid == null ||
			!db
				.prepare(`SELECT 1 FROM lem WHERE rowid = ? AND origin_rid IS NULL AND (flags & 7) != ${REL_LOCAL}`)
				.get(etymonRid)
		) {
			error(400, 'Choose a valid etymon');
		}
		const relation = body.Relation === 'borrowed' ? 'borrowed' : 'reflex';
		rows.push({
			Form_ID: formId,
			Etymon_ID: etymonId,
			Relation: relation,
			Status: 'accepted',
			Notes: body.Notes?.trim() ?? ''
		});
	}
	await writeAssignments(rows);
	return json({ ok: true });
};
