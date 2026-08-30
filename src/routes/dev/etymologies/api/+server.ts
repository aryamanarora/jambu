import { dev } from '$app/environment';
import { error, json } from '@sveltejs/kit';
import { readFile, rename, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { getDb, ids } from '$lib/server/db';
import { readDeltas, readVarints, FLAG_SECTION, REL_UNLINKED } from '$lib/dbShared';
import { ETYMOLOGY_GUESS_THRESHOLD, soundSimilarity } from '$lib/etymologyGuess';
import type { RequestHandler } from './$types';

// ---- v2-schema helpers (dev-only tool, so simple full-scan caches are fine) ----

type CiteInfo = {
	short: string;
	refId: string;
	source: string | null;
	progress: string | null;
	provenance: string | null;
	editor: string | null;
	ocr: number;
	lemma_count: number;
	unetymologised_count: number;
};
let _citeInfo: Map<number, CiteInfo & { locator: string; refRid: number }> | null = null;
function citeInfo() {
	if (!_citeInfo) {
		const db = getDb();
		const refs = new Map(
			(db.prepare('SELECT rowid AS rid, * FROM "references"').all() as {
				rid: number;
				id: string;
				short: string | null;
				source: string | null;
				progress: string | null;
				provenance: string | null;
				editor: string | null;
				ocr: number;
				lemma_count: number;
				unetymologised_count: number;
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
						source: ref?.source ?? null,
						progress: ref?.progress ?? null,
						provenance: ref?.provenance ?? null,
						editor: ref?.editor ?? null,
						ocr: ref?.ocr ?? 0,
						lemma_count: ref?.lemma_count ?? 0,
						unetymologised_count: ref?.unetymologised_count ?? 0,
						locator: c.locator,
						refRid: c.ref_rid
					}
				];
			})
		);
	}
	return _citeInfo;
}

function sourcesOf(cites: Buffer | null) {
	if (!cites) return { source_ids: null, sources: null, references: [] };
	const info = citeInfo();
	const ids_ = new Set<string>();
	const labels = new Set<string>();
	const references = new Map<string, {
		id: string; short: string; source: string | null; progress: string | null;
		provenance: string | null; editor: string | null; ocr: number;
		lemma_count: number; unetymologised_count: number; locator?: string;
	}>();
	for (const cid of readVarints(new Uint8Array(cites))) {
		const c = info.get(cid);
		if (!c) continue;
		ids_.add(c.refId);
		labels.add(c.locator !== '' ? `${c.short}, ${c.locator}` : c.short);
		const existing = references.get(c.refId);
		if (existing) {
			if (c.locator && !existing.locator?.split('; ').includes(c.locator))
				existing.locator = [existing.locator, c.locator].filter(Boolean).join('; ');
		} else {
			references.set(c.refId, {
				id: c.refId,
				short: c.short,
				source: c.source,
				progress: c.progress,
				provenance: c.provenance,
				editor: c.editor,
				ocr: c.ocr,
				lemma_count: c.lemma_count,
				unetymologised_count: c.unetymologised_count,
				locator: c.locator || undefined
			});
		}
	}
	return {
		source_ids: ids_.size ? [...ids_].join(',') : null,
		sources: labels.size ? [...labels].join(',') : null,
		references: [...references.values()]
	};
}

function citeIdsOfRef(refId: string): number[] {
	const out: number[] = [];
	for (const [cid, c] of citeInfo()) if (c.refId === refId) out.push(cid);
	return out;
}

// immediate etymon rid → concept ids, and lemma rid → concept ids (decoded once from
// concepts.rids). Immediate parents matter here because a section/derived form can itself be the
// etymon that directly licenses an attestation.
let _conceptIndex: {
	byLemma: Map<number, Set<number>>;
	byEntry: Map<number, Set<number>>;
	byConcept: Map<number, Set<number>>;
} | null = null;
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
		const byConcept = new Map<number, Set<number>>();
		for (const c of db.prepare('SELECT id, rids FROM concepts WHERE rids IS NOT NULL').all() as {
			id: number;
			rids: Buffer;
		}[]) {
			for (const rid of readDeltas(new Uint8Array(c.rids))) {
				(byLemma.get(rid) ?? byLemma.set(rid, new Set()).get(rid)!).add(c.id);
				(byConcept.get(c.id) ?? byConcept.set(c.id, new Set()).get(c.id)!).add(rid);
				const info = originOf.get(rid);
				if (!info || (info.flags & 7) === REL_UNLINKED) continue;
				const entry = info.origin_rid ?? rid;
				(byEntry.get(entry) ?? byEntry.set(entry, new Set()).get(entry)!).add(c.id);
			}
		}
		_conceptIndex = { byLemma, byEntry, byConcept };
	}
	return _conceptIndex;
}

export const prerender = false;

const ASSIGNMENTS = resolve(process.cwd(), '../data/data/etymology-assignments.csv');
const FIELDS = ['Form_ID', 'Etymon_ID', 'Kind', 'Rank', 'Status', 'Source', 'Notes'] as const;

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

type SelectedFormRow = {
	rid: number;
	id: string;
	word: string;
	gloss: string;
	phonemic: string | null;
	language_id: string;
	language: string;
};

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
			.sort((a, b) => a.Form_ID.localeCompare(b.Form_ID) || (a.Etymon_ID ?? '').localeCompare(b.Etymon_ID ?? ''))
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

	if (mode === 'review') {
		const idx = ids();
		const flagged = db
			.prepare(
				`SELECT e.child_rid, e.parent_rid, e.kind, e.rank, e.note,
				        c.word AS child_word, c.gloss AS child_gloss, cl.name AS child_lang,
				        p.word AS parent_word, p.gloss AS parent_gloss, pl.name AS parent_lang,
				        p.origin_rid IS NULL AS parent_is_entry
				 FROM edges e
				 JOIN lem c ON c.rowid = e.child_rid
				 JOIN lem p ON p.rowid = e.parent_rid
				 LEFT JOIN languages cl ON cl.rowid = c.lang_rid
				 LEFT JOIN languages pl ON pl.rowid = p.lang_rid
				 WHERE e.note LIKE 'review:%' ORDER BY e.note, c.word`
			)
			.all() as Array<Record<string, unknown>>;
		const KINDS: Record<number, string> = { 1: 'reflex', 2: 'variant', 3: 'borrowed', 5: 'component', 6: 'derived' };
		const assignments = await readAssignments();
		const resolved = new Set(
			assignments.map((a) => `${a.Form_ID}|${a.Etymon_ID}`)
		);
		const rows = flagged.map((e) => ({
			form_id: idx.idOf(e.child_rid as number),
			form_word: e.child_word,
			form_gloss: e.child_gloss,
			form_lang: e.child_lang,
			etymon_id: idx.idOf(e.parent_rid as number),
			etymon_word: e.parent_word,
			etymon_gloss: e.parent_gloss,
			etymon_lang: e.parent_lang,
			etymon_is_entry: !!e.parent_is_entry,
			kind: KINDS[e.kind as number] ?? String(e.kind),
			rank: e.rank,
			note: e.note
		}));
		return json({
			rows: rows.filter((r) => !resolved.has(`${r.form_id}|${r.etymon_id}`)),
			total: rows.length
		});
	}

	if (mode === 'related') {
		const idx = ids();
		const formId = url.searchParams.get('form') ?? '';
		const formRid = idx.ridOf(formId);
		if (formRid == null) error(400, 'Choose a valid seed form');
		const selected = db
			.prepare(
				`SELECT l.rowid AS rid, l.word, l.gloss, l.phonemic,
				        lang.id AS language_id, lang.name AS language
				 FROM lem l JOIN languages lang ON lang.rowid = l.lang_rid
				 WHERE l.rowid = ? AND (l.flags & 7) = ${REL_UNLINKED}`
			)
			.get(formRid) as Omit<SelectedFormRow, 'id'> | undefined;
		if (!selected) error(400, 'Choose an unetymologised seed form');

		const concepts = conceptIndex();
		const selectedConcepts = concepts.byLemma.get(selected.rid) ?? new Set<number>();
		const pool = new Set<number>();
		for (const concept of selectedConcepts)
			for (const rid of concepts.byConcept.get(concept) ?? []) pool.add(rid);
		pool.delete(selected.rid);

		// A few imported forms carry their concept label only as a gloss. Always union exact
		// gloss matches so those rows can join forms that do have a concepts.rids mapping.
		if (selected.gloss.trim()) {
			for (const row of db
				.prepare(
					`SELECT rowid AS rid FROM lem
					 WHERE (flags & 7) = ${REL_UNLINKED} AND rowid != ?
					   AND lower(trim(gloss)) = lower(trim(?)) LIMIT 500`
				)
				.all(selected.rid, selected.gloss) as { rid: number }[]) pool.add(row.rid);
		}

		if (!pool.size) return json({ rows: [] });
		const saved = new Set(
			(await readAssignments())
				.filter((row) => row.Status !== 'rejected' && (!row.Rank || row.Rank === '1'))
				.map((row) => row.Form_ID)
		);
		const related = (db
			.prepare(
				`SELECT l.rowid AS rid, l.word, l.gloss, l.phonemic, l.notes, l.cites,
				        lang.id AS language_id, lang.name AS language, lang.color AS language_color
				 FROM lem l JOIN languages lang ON lang.rowid = l.lang_rid
				 WHERE l.rowid IN (SELECT value FROM json_each(?))
				   AND (l.flags & 7) = ${REL_UNLINKED}`
			)
			.all(JSON.stringify([...pool])) as {
			rid: number;
			word: string;
			gloss: string;
			phonemic: string | null;
			notes: string | null;
			cites: Buffer | null;
			language_id: string;
			language: string;
			language_color: string | null;
		}[])
			.map((row) => {
				const id = idx.idOf(row.rid);
				const rowConcepts = concepts.byLemma.get(row.rid) ?? new Set<number>();
				const shared = [...selectedConcepts].filter((concept) => rowConcepts.has(concept)).length;
				const exactGloss =
					row.gloss.trim().toLocaleLowerCase() === selected.gloss.trim().toLocaleLowerCase();
				const conceptScore = Math.max(
					selectedConcepts.size
						? (2 * shared) / Math.max(1, selectedConcepts.size + rowConcepts.size)
						: 0,
					exactGloss ? 1 : 0
				);
				const soundScore = soundSimilarity(
					selected.phonemic || selected.word,
					row.phonemic || row.word
				);
				const confidence = Math.round(100 * (0.58 * conceptScore + 0.42 * soundScore));
				return {
					id,
					word: row.word,
					gloss: row.gloss,
					phonemic: row.phonemic ?? '',
					notes: row.notes ?? '',
					language_id: row.language_id,
					language: row.language,
					...sourcesOf(row.cites),
					confidence,
					concept_score: Math.round(conceptScore * 100),
					sound_score: Math.round(soundScore * 100),
					suggested: conceptScore > 0 && soundScore >= 0.32 && confidence >= 70,
					assigned: saved.has(id)
				};
			})
			.filter((row) => !row.assigned)
			.sort(
				(a, b) =>
					b.confidence - a.confidence ||
					b.sound_score - a.sound_score ||
					a.language.localeCompare(b.language) ||
					a.word.localeCompare(b.word)
			)
			.slice(0, 60);
		return json({ rows: related });
	}

	if (mode === 'candidates') {
		const idx = ids();
		const requestedIds = (url.searchParams.get('forms') || url.searchParams.get('form') || '')
			.split(',')
			.map((id) => id.trim())
			.filter(Boolean)
			.slice(0, 100);
		const requestedRids = requestedIds
			.map((id) => idx.ridOf(id))
			.filter((rid): rid is number => rid != null);
		const selectedForms = requestedRids.length
			? ((db
					.prepare(
						`SELECT l.rowid AS rid, l.word, l.gloss, l.phonemic,
						        lang.id AS language_id, lang.name AS language
						 FROM lem l LEFT JOIN languages lang ON lang.rowid = l.lang_rid
						 WHERE l.rowid IN (SELECT value FROM json_each(?))`
					)
					.all(JSON.stringify(requestedRids)) as Omit<SelectedFormRow, 'id'>[]).map((row) => ({
					...row,
					id: idx.idOf(row.rid)
				})) as SelectedFormRow[])
			: [];
		const selectedConcepts = new Set<number>();
		for (const form of selectedForms)
			for (const concept of conceptIndex().byLemma.get(form.rid) ?? []) selectedConcepts.add(concept);
		// candidate entries carrying any of the selected concepts (via any attestation)
		const candidateEntryRids = new Set<number>();
		if (selectedConcepts.size) {
			for (const [entry, cids] of conceptIndex().byEntry) {
				for (const c of cids)
					if (selectedConcepts.has(c)) {
						candidateEntryRids.add(entry);
						break;
					}
			}
		}
		// Imported comparative vocabularies often preserve their concept label in the
		// gloss/source metadata without contributing a concepts.rids mapping. Exact gloss
		// matches on already-linked attestations recover their immediate etyma, including
		// section/derived nodes that are not graph roots.
		const selectedGlosses = [
			...new Set(
				selectedForms
					.map((form) => form.gloss.trim().toLocaleLowerCase())
					.filter(Boolean)
			)
		];
		if (selectedGlosses.length) {
			for (const row of db
				.prepare(
					`SELECT DISTINCT origin_rid AS rid FROM lem
					 WHERE origin_rid IS NOT NULL AND (flags & 7) != ${REL_UNLINKED}
					   AND lower(trim(gloss)) IN (SELECT value FROM json_each(?))`
				)
				.all(JSON.stringify(selectedGlosses)) as { rid: number }[]) candidateEntryRids.add(row.rid);
		}
		const exactRid = idx.ridOf(q) ?? -1;
		const rows = (db
			.prepare(
				`SELECT l.rowid AS rid, l.word, l.gloss, l.counts, l.cites,
				        lang.id AS language_id, lang.name AS language
				 FROM lem l
				 LEFT JOIN languages lang ON lang.rowid = l.lang_rid
				 WHERE (l.flags & 7) != ${REL_UNLINKED}
				   AND (l.rowid = ? OR (
				        (l.origin_rid IS NULL OR l.children IS NOT NULL)
				        AND (? = '' OR instr(lower(l.word), ?) > 0
				             OR instr(lower(l.gloss), ?) > 0 OR instr(lower(lang.name), ?) > 0
				             OR l.rowid IN (SELECT value FROM json_each(?)))))
				 ORDER BY CASE WHEN l.rowid = ? THEN 0 WHEN lower(l.word) = ? THEN 1
				               WHEN lower(l.gloss) = ? THEN 2 ELSE 3 END,
				          (l.counts / 1024) DESC, l.ord
				 LIMIT 400`
			)
			.all(exactRid, q, q, q, q, JSON.stringify([...candidateEntryRids]), exactRid, q, q) as {
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

		if (!selectedForms.length || !rows.length) return json({ rows: rows.slice(0, 80) });
		const candidateRids = rows.map((row) => row.rid);
		const conceptsByCandidate = new Map<string, Set<number>>();
		for (const row of rows) {
			const set = conceptIndex().byEntry.get(row.rid);
			if (set) conceptsByCandidate.set(row.id, set);
		}

		const reflexRows = (db
			.prepare(
				`SELECT att.origin_rid AS origin_rid, att.word, att.gloss, att.phonemic,
				        lang.id AS language_id, lang.name AS language
				 FROM lem att LEFT JOIN languages lang ON lang.rowid = att.lang_rid
				 WHERE att.origin_rid IN (SELECT value FROM json_each(?))
				   AND att.link_rid IS NULL`
			)
			.all(JSON.stringify(candidateRids)) as {
			origin_rid: number;
			word: string;
			gloss: string;
			phonemic: string | null;
			language_id: string;
			language: string;
		}[]).map((r) => ({
			candidate_id: idx.idOf(r.origin_rid),
			word: r.word,
			gloss: r.gloss,
			phonemic: r.phonemic,
			language_id: r.language_id,
			language: r.language
		}));
		const reflexesByCandidate = new Map<string, typeof reflexRows>();
		for (const reflex of reflexRows)
			(reflexesByCandidate.get(reflex.candidate_id) ??
				reflexesByCandidate.set(reflex.candidate_id, []).get(reflex.candidate_id)!).push(reflex);
		const scored = rows.map((row) => {
			const candidateConcepts = conceptsByCandidate.get(row.id) ?? new Set<number>();
			const candidateGlosses = new Set(
				(reflexesByCandidate.get(row.id) ?? [])
					.map((reflex) => reflex.gloss.trim().toLocaleLowerCase())
					.filter(Boolean)
			);
			const conceptScores: number[] = [];
			const soundScores: number[] = [];
			const cognateScores: number[] = [];
			let supportedForms = 0;
			let cognate: { score: number; word: string; language: string; form: string } | undefined;
			for (const form of selectedForms) {
				const formConcepts = conceptIndex().byLemma.get(form.rid) ?? new Set<number>();
				const conceptMatches = [...formConcepts].filter((concept) => candidateConcepts.has(concept)).length;
				const glossMatch = candidateGlosses.has(form.gloss.trim().toLocaleLowerCase()) ? 1 : 0;
				const formConceptScore = formConcepts.size
					? Math.max(conceptMatches / formConcepts.size, glossMatch)
					: glossMatch;
				conceptScores.push(formConceptScore);
				const formSound = form.phonemic || form.word;
				const headSoundScore = soundSimilarity(formSound, row.word);
				soundScores.push(headSoundScore);
				let best: { score: number; word: string; language: string; form: string } | undefined;
				for (const reflex of reflexesByCandidate.get(row.id) ?? []) {
					const raw = soundSimilarity(formSound, reflex.phonemic || reflex.word);
					const score = raw * (reflex.language_id === form.language_id ? 1 : 0.82);
					if (!best || score > best.score)
						best = { score, word: reflex.word, language: reflex.language, form: form.word };
				}
				const bestScore = best?.score ?? 0;
				cognateScores.push(bestScore);
				if (
					formConceptScore > 0 &&
					Math.max(headSoundScore, bestScore) >= ETYMOLOGY_GUESS_THRESHOLD
				)
					supportedForms++;
				if (best && (!cognate || best.score > cognate.score)) cognate = best;
			}
			const average = (values: number[]) =>
				values.length ? values.reduce((total, value) => total + value, 0) / values.length : 0;
			const concept_score = average(conceptScores);
			const sound_score = average(soundScores);
			const cognate_score = average(cognateScores);
			const confidence = Math.round(100 * (0.45 * concept_score + 0.2 * sound_score + 0.35 * cognate_score));
			return {
				...row,
				word: row.word || cognate?.word || '',
				gloss: row.gloss || selectedForms[0]?.gloss || '',
				confidence,
				concept_score: Math.round(concept_score * 100),
				sound_score: Math.round(sound_score * 100),
				cognate_score: Math.round(cognate_score * 100),
				best_cognate: cognate ? `${cognate.word} · ${cognate.language} ↔ ${cognate.form}` : null,
				supported_forms: supportedForms,
				group_size: selectedForms.length
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
	const where = `(l.flags & 7) = ${REL_UNLINKED}
		AND (? = '' OR instr(lower(l.word), ?) > 0 OR instr(lower(l.gloss), ?) > 0
		     OR instr(lower(COALESCE(l.notes, '')), ?) > 0 OR instr(lower(lang.name), ?) > 0)
		AND (? = '' OR lang.id = ?)
		AND (? = '' OR vin_any(l.cites, ?) = 1)`;
	const params = [q, q, q, q, q, language, language, source, JSON.stringify(sourceCites)];
	const rows = (db
		.prepare(
			`SELECT l.rowid AS rid, l.word, l.gloss, l.phonemic, l.notes, l.cites,
			        lang.id AS language_id, lang.name AS language, lang.color AS language_color
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
		language_color: string | null;
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
		.prepare(`SELECT id, name FROM languages WHERE rowid IN (SELECT DISTINCT lang_rid FROM lem WHERE (flags & 7) = ${REL_UNLINKED}) ORDER BY "order", name`)
		.all();
	const sources = db
		.prepare(`SELECT id, short, source, progress, provenance, editor, ocr,
		                 lemma_count, unetymologised_count
		          FROM "references" WHERE unetymologised_count > 0 ORDER BY short`)
		.all();
	const assignments = await readAssignments();
	return json({ rows, count, page, languages, sources, assignments });
};

export const POST: RequestHandler = async ({ request }) => {
	localOnly(request);
	const body = (await request.json()) as Partial<Assignment> & {
		remove?: boolean;
		reject?: boolean; // review queue: reject a generated rank>=2 hypothesis edge
		Relation?: string; // legacy client field name for Kind
		assignments?: Array<Partial<Assignment> & { Relation?: string }>;
	};
	const db = getDb();
	const validatedAssignment = (
		input: Partial<Assignment> & { Relation?: string }
	): Assignment => {
		const formId = input.Form_ID?.trim() ?? '';
		if (!/^f_[a-z2-7]{13}$/.test(formId))
			error(400, 'A persistent form ID is required; rebuild the data first');
		if (ids().ridOf(formId) == null) error(400, `Unknown form ID: ${formId}`);
		const etymonId = input.Etymon_ID?.trim() ?? '';
		const etymonRid = etymonId ? ids().ridOf(etymonId) : null;
		if (
			etymonRid == null ||
			!db
				.prepare(`SELECT 1 FROM lem WHERE rowid = ? AND (flags & 7) != ${REL_UNLINKED}`)
				.get(etymonRid)
		)
			error(400, `Choose a valid etymon for ${formId}`);
		const rank = /^[1-9]\d*$/.test(input.Rank ?? '') ? (input.Rank as string) : '1';
		return {
			Form_ID: formId,
			Etymon_ID: etymonId,
			Kind: (input.Kind ?? input.Relation) === 'borrowed' ? 'borrowed' : 'reflex',
			Rank: rank,
			Status: 'accepted',
			Source: input.Source?.trim() ?? '',
			Notes: input.Notes?.trim() ?? ''
		};
	};

	if (body.assignments) {
		if (!body.assignments.length || body.assignments.length > 100)
			error(400, 'A group must contain between 1 and 100 forms');
		const additions = body.assignments.map(validatedAssignment);
		const uniqueForms = new Set(additions.map((row) => row.Form_ID));
		if (uniqueForms.size !== additions.length) error(400, 'A form can only occur once in a group');
		let rows = await readAssignments();
		for (const addition of additions) {
			rows = rows.filter(
				(row) =>
					!(
						row.Form_ID === addition.Form_ID &&
						(addition.Rank === '1'
							? row.Rank === '1' || !row.Rank
							: row.Etymon_ID === addition.Etymon_ID)
					)
			);
			rows.push(addition);
		}
		await writeAssignments(rows);
		return json({ ok: true, count: additions.length });
	}

	const formId = body.Form_ID?.trim() ?? '';
	if (!/^f_[a-z2-7]{13}$/.test(formId)) error(400, 'A persistent form ID is required; rebuild the data first');
	if (ids().ridOf(formId) == null) error(400, 'Unknown form ID');

	const rank = /^[1-9]\d*$/.test(body.Rank ?? '') ? (body.Rank as string) : '1';
	let rows = await readAssignments();
	if (body.reject) {
		// a rejection is a durable overlay row: apply_assignments deletes the generated edge
		const etymonId = body.Etymon_ID?.trim() ?? '';
		if (!etymonId) error(400, 'Rejection needs the proposed etymon');
		rows = rows.filter((row) => !(row.Form_ID === formId && row.Etymon_ID === etymonId));
		rows.push({
			Form_ID: formId,
			Etymon_ID: etymonId,
			Kind: (body.Kind === 'borrowed' ? 'borrowed' : 'reflex') as string,
			Rank: rank,
			Status: 'rejected',
			Source: body.Source?.trim() ?? '',
			Notes: body.Notes?.trim() ?? ''
		});
		await writeAssignments(rows);
		return json({ ok: true });
	}
	if (body.remove) {
		rows = rows.filter((row) => row.Form_ID !== formId);
		await writeAssignments(rows);
		return json({ ok: true });
	}
	const addition = validatedAssignment(body);
	const etymonId = addition.Etymon_ID;
	// rank-1 rows are unique per form; rank>=2 rows are keyed (form, etymon)
	rows = rows.filter(
		(row) =>
			!(row.Form_ID === formId && (rank === '1' ? row.Rank === '1' || !row.Rank : row.Etymon_ID === etymonId))
	);
	rows.push(addition);
	await writeAssignments(rows);
	return json({ ok: true });
};
