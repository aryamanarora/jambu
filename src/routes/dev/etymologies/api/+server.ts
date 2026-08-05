import { dev } from '$app/environment';
import { error, json } from '@sveltejs/kit';
import { readFile, rename, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { getDb } from '$lib/server/db';
import type { RequestHandler } from './$types';

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
		const formId = url.searchParams.get('form') ?? '';
		const selected = db
			.prepare('SELECT rowid, word, phonemic, language_id FROM lemmas WHERE id = ?')
			.get(formId) as
			| { rowid: number; word: string; phonemic: string | null; language_id: string }
			| undefined;
		const selectedConcepts = selected
			? (db.prepare('SELECT concept_id FROM lemma_concept WHERE lemma_rid = ?').all(selected.rowid) as { concept_id: number }[]).map(
					(row) => row.concept_id
				)
			: [];
		const conceptPlaceholders = selectedConcepts.map(() => '?').join(',');
		const conceptPrefilter = selectedConcepts.length
			? `EXISTS (
			     SELECT 1 FROM lemmas att JOIN lemma_concept lc ON lc.lemma_rid = att.rowid
			     WHERE COALESCE(NULLIF(att.origin_lemma_id, ''), att.id) = l.id
			       AND lc.concept_id IN (${conceptPlaceholders})
			   )`
			: '0';
		const rows = db
			.prepare(
				`SELECT l.id, l.word, l.gloss, l.language_id, lang.name AS language,
				        l.reflex_count, l.lang_count,
				        group_concat(DISTINCT CASE
				          WHEN lr.locator != '' THEN coalesce(r.short, r.id) || ', ' || lr.locator
				          ELSE coalesce(r.short, r.id)
				        END) AS sources
				 FROM lemmas l
				 LEFT JOIN languages lang ON lang.id = l.language_id
				 LEFT JOIN lemma_reference lr ON lr.lemma_rid = l.rowid
				 LEFT JOIN "references" r ON r.rowid = lr.reference_rid
				 WHERE l.origin_lemma_id IS NULL AND l.relation IS NOT 'local'
				   AND (? = '' OR lower(l.id) = ? OR instr(lower(l.word), ?) > 0
				        OR instr(lower(l.gloss), ?) > 0 OR instr(lower(lang.name), ?) > 0
				        OR ${conceptPrefilter})
				 GROUP BY l.rowid
				 ORDER BY CASE WHEN lower(l.id) = ? THEN 0 WHEN lower(l.word) = ? THEN 1
				               WHEN lower(l.gloss) = ? THEN 2 ELSE 3 END,
				          l.reflex_count DESC, l."order"
				 LIMIT 400`
			)
			.all(q, q, q, q, q, ...selectedConcepts, q, q, q) as CandidateRow[];

		if (!selected || !rows.length) return json({ rows: rows.slice(0, 80) });
		const ids = rows.map((row) => row.id);
		const placeholders = ids.map(() => '?').join(',');
		const conceptRows = db
			.prepare(
				`SELECT COALESCE(NULLIF(att.origin_lemma_id, ''), att.id) AS candidate_id,
				        lc.concept_id
				 FROM lemma_concept lc JOIN lemmas att ON att.rowid = lc.lemma_rid
				 WHERE COALESCE(NULLIF(att.origin_lemma_id, ''), att.id) IN (${placeholders})`
			)
			.all(...ids) as { candidate_id: string; concept_id: number }[];
		const conceptsByCandidate = new Map<string, Set<number>>();
		for (const row of conceptRows) {
			const concepts = conceptsByCandidate.get(row.candidate_id) ?? new Set<number>();
			concepts.add(row.concept_id);
			conceptsByCandidate.set(row.candidate_id, concepts);
		}

		const reflexRows = db
			.prepare(
				`SELECT att.origin_lemma_id AS candidate_id, att.word, att.phonemic,
				        att.language_id, lang.name AS language
				 FROM lemmas att LEFT JOIN languages lang ON lang.id = att.language_id
				 WHERE att.origin_lemma_id IN (${placeholders}) AND att.redirect_to IS NULL`
			)
			.all(...ids) as {
			candidate_id: string;
			word: string;
			phonemic: string | null;
			language_id: string;
			language: string;
		}[];
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

	const language = url.searchParams.get('language') ?? '';
	const source = url.searchParams.get('source') ?? '';
	const page = Math.max(1, Number(url.searchParams.get('page') ?? 1));
	const offset = (page - 1) * 50;
	const where = `l.relation = 'local'
		AND (? = '' OR instr(lower(l.word), ?) > 0 OR instr(lower(l.gloss), ?) > 0
		     OR instr(lower(l.notes), ?) > 0 OR instr(lower(lang.name), ?) > 0)
		AND (? = '' OR l.language_id = ?)
		AND (? = '' OR EXISTS (
			SELECT 1 FROM lemma_reference slr JOIN "references" sr ON sr.rowid = slr.reference_rid
			WHERE slr.lemma_rid = l.rowid AND sr.id = ?
		))`;
	const params = [q, q, q, q, q, language, language, source, source];
	const rows = db
		.prepare(
			`SELECT l.id, l.word, l.gloss, l.phonemic, l.notes, l.language_id,
			        lang.name AS language, group_concat(DISTINCT r.id) AS source_ids,
			        group_concat(DISTINCT CASE
			          WHEN lr.locator != '' THEN coalesce(r.short, r.id) || ', ' || lr.locator
			          ELSE coalesce(r.short, r.id)
			        END) AS sources
			 FROM lemmas l JOIN languages lang ON lang.id = l.language_id
			 LEFT JOIN lemma_reference lr ON lr.lemma_rid = l.rowid
			 LEFT JOIN "references" r ON r.rowid = lr.reference_rid
			 WHERE ${where}
			 GROUP BY l.rowid ORDER BY lang."order", lang.name, l."order" LIMIT 50 OFFSET ?`
		)
		.all(...params, offset);
	const count = (db.prepare(`SELECT COUNT(*) AS n FROM lemmas l JOIN languages lang ON lang.id=l.language_id WHERE ${where}`).get(...params) as { n: number }).n;
	const languages = db
		.prepare(`SELECT id, name FROM languages WHERE EXISTS (SELECT 1 FROM lemmas l WHERE l.language_id=languages.id AND l.relation='local') ORDER BY "order", name`)
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
	if (!db.prepare('SELECT 1 FROM lemmas WHERE id=?').get(formId)) error(400, 'Unknown form ID');

	let rows = await readAssignments();
	rows = rows.filter((row) => row.Form_ID !== formId);
	if (!body.remove) {
		const etymonId = body.Etymon_ID?.trim() ?? '';
		if (!etymonId || !db.prepare(`SELECT 1 FROM lemmas WHERE id=? AND origin_lemma_id IS NULL AND relation IS NOT 'local'`).get(etymonId)) {
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
