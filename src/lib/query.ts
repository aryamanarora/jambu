/**
 * query.ts — client-side query layer, the port of neojambu's `search.py` + the entry-page
 * grouping in `app.py`. All queries run in the browser against the chunked SQLite via db.ts.
 *
 * Design notes for HTTP Range efficiency:
 *  - Text search scans the compact local lemma table with `instr`; it is gated at MIN_SEARCH_CHARS
 *    so 1–2 character partials never trigger a scan.
 *  - The small `languages` and `references` tables are loaded/queried cheaply and
 *    cached; we attach relations in JS rather than doing wide joins over 313k lemma rows.
 *  - The unfiltered list paths avoid the languages join and lean on the order indexes
 *    (idx_lemmas_order / partial idx_entries_order) so only the needed pages are fetched.
 */
import { query, queryOne } from './db.svelte';
import { CLADE_ORDER } from './clades';
import {
	PAGE_SIZE,
	MIN_SEARCH_CHARS,
	type Language,
	type Dialect,
	type Lemma,
	type Reference,
	type ListParams,
	type CognateGroup
} from './types';

// ---- small helpers --------------------------------------------------------

function placeholders(n: number): string {
	return new Array(n).fill('?').join(',');
}

/** Run an `IN (...)` query in <900-id chunks to stay under SQLite's parameter limit. */
async function inChunks<T>(ids: string[], fn: (chunk: string[]) => Promise<T[]>): Promise<T[]> {
	const out: T[] = [];
	for (let i = 0; i < ids.length; i += 900) {
		out.push(...(await fn(ids.slice(i, i + 900))));
	}
	return out;
}

// ---- precomputed counts (meta table) -------------------------------------

const metaCache = new Map<string, number>();
async function metaCount(key: string): Promise<number> {
	if (metaCache.has(key)) return metaCache.get(key)!;
	const r = await queryOne<{ value: number }>('SELECT value FROM meta WHERE key = ?', [key]);
	const v = r?.value ?? 0;
	metaCache.set(key, v);
	return v;
}

// ---- languages cache (615 rows) ------------------------------------------

let languagesCache: Map<string, Language> | null = null;

export async function getAllLanguages(): Promise<Language[]> {
	const list = await query<Language>('SELECT * FROM languages');
	if (!languagesCache) {
		languagesCache = new Map(list.map((l) => [l.id, l]));
	}
	return list;
}

let dialectsCache: Dialect[] | null = null;
export async function getAllDialects(): Promise<Dialect[]> {
	if (dialectsCache) return dialectsCache;
	dialectsCache = await query<Dialect>(
		'SELECT * FROM dialects WHERE lemma_count > 0 ORDER BY name, id'
	);
	return dialectsCache;
}

async function languageMap(): Promise<Map<string, Language>> {
	if (languagesCache) return languagesCache;
	await getAllLanguages();
	return languagesCache!;
}

// Languages that actually carry rows in a given list view — for the Language column's
// dropdown. Distinct scan over the (indexed) language_id column, cached per mode; the whole
// DB is local (OPFS) so this is a cheap one-off (~20 langs for entries, ~585 for reflexes).
const filterLangsCache = new Map<string, Language[]>();
export async function getFilterLanguages(mode: 'entries' | 'reflexes'): Promise<Language[]> {
	if (filterLangsCache.has(mode)) return filterLangsCache.get(mode)!;
	// entries → languages with an etymon OR a loan-source reflex (both are listable under /entries);
	// reflexes → every language (the reflexes list is the whole lexicon, so any node's language works).
	const where =
		mode === 'entries'
			? "WHERE (origin_lemma_id IS NULL AND relation IS NOT 'local') OR EXISTS (SELECT 1 FROM lemmas b " +
				"WHERE b.origin_lemma_id = lemmas.id AND b.relation = 'borrowed')"
			: '';
	const rows = await query<{ language_id: string }>(
		`SELECT DISTINCT language_id FROM lemmas ${where}`
	);
	const langs = await languageMap();
	const out = rows
		.map((r) => langs.get(r.language_id))
		.filter((l): l is Language => !!l)
		.sort((a, b) => a.order - b.order || a.name.localeCompare(b.name));
	filterLangsCache.set(mode, out);
	return out;
}

const filterDialectsCache = new Map<string, Dialect[]>();
/** Dialects actually present in a list mode, for inclusion beside base languages in its picker. */
export async function getFilterDialects(mode: 'entries' | 'reflexes'): Promise<Dialect[]> {
	if (filterDialectsCache.has(mode)) return filterDialectsCache.get(mode)!;
	const out = (await getAllDialects()).filter((d) => mode === 'reflexes' || d.entry_count > 0);
	filterDialectsCache.set(mode, out);
	return out;
}

// ---- relation hydration ---------------------------------------------------

async function attachLanguages(lemmas: Lemma[]): Promise<void> {
	const langs = await languageMap();
	for (const l of lemmas) l.language = langs.get(l.language_id);
}

async function attachOrigin(lemmas: Lemma[]): Promise<void> {
	const langs = await languageMap();
	const ids = [...new Set(lemmas.map((l) => l.origin_lemma_id).filter((x): x is string => !!x))];
	if (!ids.length) return;
	const rows = await inChunks<Lemma>(ids, (chunk) =>
		query<Lemma>(
			`SELECT id, word, gloss, phonemic, "order", language_id, origin_lemma_id
			 FROM lemmas WHERE id IN (${placeholders(chunk.length)})`,
			chunk
		)
	);
	const map = new Map(rows.map((r) => [r.id, r]));
	for (const r of rows) r.language = langs.get(r.language_id);
	for (const l of lemmas) l.origin_lemma = l.origin_lemma_id ? (map.get(l.origin_lemma_id) ?? null) : null;
}

async function attachReferences(lemmas: Lemma[]): Promise<void> {
	if (!lemmas.length) return;
	const ids = lemmas.map((l) => l.id);
	const rows = await inChunks<Reference & { lemma_id: string }>(ids, (chunk) =>
		query<Reference & { lemma_id: string }>(
			`SELECT l.id AS lemma_id, r.id, r.short, r.source, r.progress, r.provenance, r.editor,
			        r.lemma_count, r.unetymologised_count
			 FROM lemma_reference lr
			 JOIN lemmas l ON l.rowid = lr.lemma_rid
			 JOIN "references" r ON r.rowid = lr.reference_rid
			 WHERE l.id IN (${placeholders(chunk.length)})
			 ORDER BY r.short`,
			chunk
		)
	);
	const map = new Map<string, Reference[]>();
	for (const row of rows) {
		const ref: Reference = {
			id: row.id,
			short: row.short,
			source: row.source,
			progress: row.progress,
			provenance: row.provenance,
			editor: row.editor,
			lemma_count: row.lemma_count,
			unetymologised_count: row.unetymologised_count
		};
		const arr = map.get(row.lemma_id);
		if (arr) arr.push(ref);
		else map.set(row.lemma_id, [ref]);
	}
	for (const l of lemmas) l.references = map.get(l.id) ?? [];
}

/** For each given reflex, count the sub-nodes hanging off it: borrowed forms sourced from it
 *  (`sub_count`, the "→n" borrowed badge) and its own daughter reflexes (`reflex_sub_count`, shown
 *  when the reflex is itself an etymon with descendants — e.g. an IA head under a proto entry). */
async function attachSubCounts(lemmas: Lemma[]): Promise<void> {
	if (!lemmas.length) return;
	const ids = lemmas.map((l) => l.id);
	const borrowed = await inChunks<{ borrowed_from: string; c: number }>(ids, (chunk) =>
		query<{ borrowed_from: string; c: number }>(
			`SELECT borrowed_from, COUNT(*) AS c FROM lemmas
			 WHERE borrowed_from IN (${placeholders(chunk.length)}) GROUP BY borrowed_from`,
			chunk
		)
	);
	const bMap = new Map(borrowed.map((r) => [r.borrowed_from, r.c]));
	const reflexes = await inChunks<{ origin_lemma_id: string; c: number }>(ids, (chunk) =>
		query<{ origin_lemma_id: string; c: number }>(
			`SELECT origin_lemma_id, COUNT(*) AS c FROM lemmas
			 WHERE origin_lemma_id IN (${placeholders(chunk.length)}) AND relation = 'reflex'
			 GROUP BY origin_lemma_id`,
			chunk
		)
	);
	const rMap = new Map(reflexes.map((r) => [r.origin_lemma_id, r.c]));
	for (const l of lemmas) {
		l.sub_count = bMap.get(l.id) ?? 0;
		l.reflex_sub_count = rMap.get(l.id) ?? 0;
	}
}

/** The borrowed sub-reflexes of a reflex (forms it was the source of), for its page. */
export async function getBorrowedReflexes(reflexId: string): Promise<Lemma[]> {
	const rows = await query<Lemma>(
		'SELECT * FROM lemmas WHERE borrowed_from = ? ORDER BY "order"',
		[reflexId]
	);
	await attachLanguages(rows);
	return rows;
}

// ---- filter / sort construction (port of search.py) ----------------------

const SORT_COLUMNS: Record<string, string> = {
	lang: 'lang.name',
	word: 'l.word',
	gloss: 'l.gloss',
	notes: 'l.notes',
	origin: 'l."order"',
	clade: 'lang.clade',
	reflexes: 'lang.lemma_count',
	nreflex: 'l.reflex_count',
	nlang: 'l.lang_count',
	nderived: '(SELECT COUNT(*) FROM derivation WHERE parent_id = l.id)'
};
// columns whose sort/filter forces the languages join
const NEEDS_LANG_JOIN = new Set(['lang', 'clade', 'reflexes']);

interface Cond {
	sql: string;
	params: unknown[];
}

function lemmaConditions(p: ListParams): { conds: Cond[]; needsLangJoin: boolean } {
	const conds: Cond[] = [];
	let needsLangJoin = false;

	// Case-insensitive substring terms. Normalising the input in JS supplies Unicode lower-casing;
	// SQLite's lower() handles the ASCII capitals present in prose and markup.
	for (const [key, col] of [
		['word', 'word'],
		['gloss', 'gloss'],
		['etymology', 'etymology'],
		['notes', 'notes']
	] as const) {
		const v = (p[key] ?? '').trim();
		if (v.length >= MIN_SEARCH_CHARS) {
			conds.push({
				sql: `instr(lower(COALESCE(l.${col}, '')), ?) > 0`,
				params: [v.toLocaleLowerCase()]
			});
		}
	}

	if (p.lang?.trim()) {
		conds.push({ sql: 'lang.name LIKE ?', params: [`%${p.lang.trim()}%`] });
		needsLangJoin = true;
	}
	if (p.clade?.trim()) {
		conds.push({ sql: 'lang.clade LIKE ?', params: [`%${p.clade.trim()}%`] });
		needsLangJoin = true;
	}
	if (p.origin_lang?.trim()) {
		const selected = p.origin_lang.trim();
		conds.push(
			selected.startsWith('dialect:')
				? {
						sql: "(' ' || COALESCE(l.tags, '') || ' ') LIKE ?",
						params: [`% ${selected} %`]
					}
				: { sql: 'l.language_id = ?', params: [selected] }
		);
	}
	if (p.etymon_lang?.trim()) {
		const selected = p.etymon_lang.trim();
		conds.push(
			selected.startsWith('dialect:')
				? {
						sql: `l.origin_lemma_id IN (SELECT id FROM lemmas
						      WHERE (' ' || COALESCE(tags, '') || ' ') LIKE ?)`,
						params: [`% ${selected} %`]
					}
				: {
						sql: 'l.origin_lemma_id IN (SELECT id FROM lemmas WHERE language_id = ?)',
						params: [selected]
					}
		);
	}
	if (p.dialect?.trim()) {
		conds.push({
			sql: "(' ' || COALESCE(l.tags, '') || ' ') LIKE ?",
			params: [`% ${p.dialect.trim()} %`]
		});
	}
	if ((p.origin ?? '').trim().length >= MIN_SEARCH_CHARS) {
		conds.push({
			sql: `l.origin_lemma_id IN
			        (SELECT id FROM lemmas WHERE instr(lower(COALESCE(word, '')), ?) > 0)`,
			params: [p.origin!.trim().toLocaleLowerCase()]
		});
	}
	if (p.source?.trim()) {
		conds.push({
			sql: `EXISTS (SELECT 1 FROM lemma_reference lr
			         JOIN "references" r ON r.rowid = lr.reference_rid
			         WHERE lr.lemma_rid = l.rowid AND r.short LIKE ?)`,
			params: [`%${p.source.trim()}%`]
		});
	}
	// tags: space-separated whole-token match on the `tags` column (AND across the selected tags)
	if (p.tags?.trim()) {
		for (const t of p.tags.trim().split(/\s+/)) {
			conds.push({
				sql: "(' ' || COALESCE(l.tags, '') || ' ') LIKE ?",
				params: [`% ${t} %`]
			});
		}
	}

	// root nodes only: entries not derived from any other etymon (no incoming derivation edge)
	if (p.rootsOnly) {
		conds.push({
			sql: 'NOT EXISTS (SELECT 1 FROM derivation WHERE child_id = l.id)',
			params: []
		});
	}

	// CDIAL section-forms only: the promoted numbered head-forms, whose ids look like `<etymon>-<n>`
	if (p.sectionsOnly) {
		conds.push({ sql: "l.id GLOB '[0-9]*-[0-9]*'", params: [] });
	}

	// a sort on a language column also needs the join
	const sortCol = p.sort?.split('-')[1];
	if (sortCol && NEEDS_LANG_JOIN.has(sortCol)) needsLangJoin = true;

	return { conds, needsLangJoin };
}

function orderBy(p: ListParams, fallback: string): string {
	const s = (p.sort ?? '').trim();
	if (s) {
		const [dir, col] = s.split('-');
		const sqlCol = SORT_COLUMNS[col];
		if (sqlCol && (dir === 'asc' || dir === 'desc')) {
			return `${sqlCol} ${dir === 'desc' ? 'DESC' : 'ASC'}, l."order"`;
		}
	}
	return fallback;
}

// ---- list views (reflexes / entries / language lexicon) ------------------

export interface ListResult {
	rows: Lemma[];
	count: number;
	page: number;
}

interface ListOpts {
	mode: 'reflexes' | 'entries' | 'lexicon';
	languageId?: string;
	referenceId?: string;
	params: ListParams;
	withOrigin?: boolean; // attach origin_lemma (reflexes/lexicon show it)
}

export async function fetchLemmaList(opts: ListOpts): Promise<ListResult> {
	const { mode, languageId, referenceId, params } = opts;
	const page = Math.max(1, params.page ?? 1);
	const { conds, needsLangJoin } = lemmaConditions(params);

	// base mode condition. The reflexes list is the whole lexicon (every node — etyma, reflexes,
	// and variants); only the per-entry reflex_count/lang_count aggregates treat variants separately.
	// Redirect stubs (CDIAL "Add. N" pointers) are never listed.
	const modeConds: Cond[] = [{ sql: 'l.redirect_to IS NULL', params: [] }];
	if (mode === 'entries') {
		// normally headwords (no parent); the loan-sources view instead lists reflexes that are
		// themselves the source of borrowings into other languages (they head a borrowing sub-tree).
		if (params.loanSourcesOnly)
			modeConds.push({
				sql: "EXISTS (SELECT 1 FROM lemmas b WHERE b.origin_lemma_id = l.id AND b.relation = 'borrowed')",
				params: []
			});
		else modeConds.push({ sql: "l.origin_lemma_id IS NULL AND l.relation IS NOT 'local'", params: [] });
	}
	if (mode === 'lexicon' && languageId)
		modeConds.push({ sql: 'l.language_id = ?', params: [languageId] });
	if (referenceId)
		modeConds.push({
			sql: `EXISTS (SELECT 1 FROM lemma_reference lr
			       JOIN "references" rr ON rr.rowid = lr.reference_rid
			       WHERE lr.lemma_rid = l.rowid AND rr.id = ?)`,
			params: [referenceId]
		});

	const all = [...modeConds, ...conds];
	const whereParams = all.flatMap((c) => c.params);
	const whereSql = all.length ? 'WHERE ' + all.map((c) => c.sql).join(' AND ') : '';

	const join = needsLangJoin ? 'JOIN languages lang ON lang.id = l.language_id' : '';

	// Fast path: entries list with no filters/sort → partial index, no join, no temp sort.
	const isDefaultEntries =
		mode === 'entries' &&
		!referenceId &&
		!needsLangJoin &&
		conds.length === 0 &&
		!params.loanSourcesOnly &&
		!(params.sort ?? '').trim();

	const fallbackOrder =
		mode === 'entries' || mode === 'lexicon' ? 'l."order"' : 'l."order"';
	const order = orderBy(params, fallbackOrder);

	// count — use precomputed totals for the unfiltered case (a full COUNT(*) is a whole-index
	// scan = a large sequential read over the wire); only COUNT the (bounded) filtered set.
	const hasFilters = conds.length > 0 || !!params.loanSourcesOnly || !!referenceId;
	let count: number;
	if (!hasFilters && mode === 'entries') {
		count = await metaCount('total_entries');
	} else if (!hasFilters && mode === 'reflexes') {
		// the reflexes list is the whole lexicon (etyma + reflexes + variants), minus redirect stubs
		count = await metaCount('total_lexicon');
	} else if (!hasFilters && mode === 'lexicon' && languageId) {
		// languages.lemma_count is exactly the per-language lemma count (verified)
		const r = await queryOne<{ c: number }>('SELECT lemma_count AS c FROM languages WHERE id = ?', [
			languageId
		]);
		count = r?.c ?? 0;
	} else {
		const countRow = await queryOne<{ c: number }>(
			`SELECT COUNT(*) AS c FROM lemmas l ${join} ${whereSql}`,
			whereParams
		);
		count = countRow?.c ?? 0;
	}

	// page
	const offset = (page - 1) * PAGE_SIZE;
	// per-entry extras (entries view only): derived-term count and the same-language variant forms
	// (concatenated, ordered, unit-separated) so the Entry column can list them beside the headword
	const derivedCol =
		mode === 'entries'
			? ', (SELECT COUNT(*) FROM derivation WHERE parent_id = l.id) AS derived_count' +
				", (SELECT group_concat(word, char(31)) FROM (SELECT word FROM lemmas WHERE " +
				"origin_lemma_id = l.id AND relation = 'variant' AND variant_of IS NULL ORDER BY \"order\")) AS variant_forms"
			: '';
	const fetchSql = isDefaultEntries
		? `SELECT l.*${derivedCol} FROM lemmas l INDEXED BY idx_entries_order
		   WHERE l.origin_lemma_id IS NULL AND l.relation IS NOT 'local' AND l.redirect_to IS NULL ORDER BY l."order" LIMIT ${PAGE_SIZE} OFFSET ${offset}`
		: `SELECT l.*${derivedCol} FROM lemmas l ${join} ${whereSql}
		   ORDER BY ${order} LIMIT ${PAGE_SIZE} OFFSET ${offset}`;
	const rows = await query<Lemma>(fetchSql, isDefaultEntries ? [] : whereParams);

	await attachLanguages(rows);
	if (opts.withOrigin) await attachOrigin(rows);
	await attachReferences(rows);
	if (mode !== 'entries') await attachSubCounts(rows);

	return { rows, count, page };
}

// ---- single-record lookups ------------------------------------------------

export async function getLemma(id: string): Promise<Lemma | null> {
	const l = await queryOne<Lemma>('SELECT * FROM lemmas WHERE id = ?', [id]);
	if (!l) return null;
	await attachLanguages([l]);
	await attachOrigin([l]);
	await attachReferences([l]);
	return l;
}

export interface AncestorRef {
	id: string;
	word: string;
	lang?: string | null;
	kind: 'entry' | 'reflex'; // link target: /entries/ vs /reflexes/
}

/** Walk up the etymology graph from a node: a reflex/variant → its etymon (origin_lemma_id); an
 *  etymon → its derivation ancestors (and so on up to the roots). Returns the ancestors level by
 *  level, nearest first. */
export async function getAncestryChain(startId: string): Promise<AncestorRef[][]> {
	const langs = await languageMap();
	const levels: AncestorRef[][] = [];
	const seen = new Set<string>([startId]);
	let frontier = [startId];
	for (let depth = 0; depth < 16 && frontier.length; depth++) {
		// step up one link: a variant → its main reflex (variant_of); anything else (reflex, borrowed
		// form, section-form's reflex) → its immediate parent via origin_lemma_id.
		const viaOrigin = await inChunks<{ pid: string }>(frontier, (chunk) =>
			query<{ pid: string }>(
				`SELECT COALESCE(variant_of, origin_lemma_id) AS pid FROM lemmas
				 WHERE id IN (${placeholders(chunk.length)}) AND COALESCE(variant_of, origin_lemma_id) IS NOT NULL`,
				chunk
			)
		);
		const viaDeriv = await inChunks<{ pid: string }>(frontier, (chunk) =>
			query<{ pid: string }>(
				`SELECT parent_id AS pid FROM derivation WHERE child_id IN (${placeholders(chunk.length)})`,
				chunk
			)
		);
		const pids = [...new Set([...viaOrigin, ...viaDeriv].map((r) => r.pid))].filter(
			(p) => p && !seen.has(p)
		);
		if (!pids.length) break;
		pids.forEach((p) => seen.add(p));
		const rows = await inChunks<{ id: string; word: string; language_id: string; olid: string | null }>(
			pids,
			(chunk) =>
				query(
					`SELECT id, word, language_id, origin_lemma_id AS olid FROM lemmas
					 WHERE id IN (${placeholders(chunk.length)})`,
					chunk
				)
		);
		levels.push(
			rows.map((r) => ({
				id: r.id,
				word: r.word,
				lang: langs.get(r.language_id)?.name,
				kind: r.olid ? ('reflex' as const) : ('entry' as const)
			}))
		);
		frontier = pids;
	}
	return levels;
}

export interface DerivedNode {
	id: string;
	word: string;
	gloss: string;
	reflex_count?: number;
	lang_count?: number;
	children: DerivedNode[];
}

/** The derived-term subtree of an entry: its derived terms, their derived terms, and so on down the
 *  derivation graph (breadth-first, deduped against cycles/diamonds, bounded for safety). */
export async function getDerivedTree(rootId: string, maxNodes = 800): Promise<DerivedNode[]> {
	const childrenOf = new Map<string, string[]>();
	const seen = new Set<string>([rootId]);
	let frontier = [rootId];
	let total = 0;
	for (let depth = 0; depth < 12 && frontier.length && total < maxNodes; depth++) {
		const edges = await inChunks<{ p: string; c: string }>(frontier, (chunk) =>
			query<{ p: string; c: string }>(
				`SELECT parent_id AS p, child_id AS c FROM derivation
				 WHERE parent_id IN (${placeholders(chunk.length)}) ORDER BY child_id`,
				chunk
			)
		);
		const next: string[] = [];
		for (const { p, c } of edges) {
			if (seen.has(c) || total >= maxNodes) continue;
			seen.add(c);
			total++;
			const arr = childrenOf.get(p);
			if (arr) arr.push(c);
			else childrenOf.set(p, [c]);
			next.push(c);
		}
		frontier = next;
	}
	const ids = [...seen].filter((id) => id !== rootId);
	const rows = await inChunks<DerivedNode>(ids, (chunk) =>
		query<DerivedNode>(
			`SELECT id, word, gloss, reflex_count, lang_count, "order" FROM lemmas
			 WHERE id IN (${placeholders(chunk.length)})`,
			chunk
		)
	);
	const info = new Map(rows.map((r) => [r.id, r]));
	const orderOf = new Map(rows.map((r) => [r.id, (r as unknown as { order: number }).order]));
	const build = (id: string): DerivedNode => {
		const r = info.get(id)!;
		const kids = (childrenOf.get(id) ?? []).sort(
			(a, b) => (orderOf.get(a) ?? 0) - (orderOf.get(b) ?? 0)
		);
		return { ...r, children: kids.map(build) };
	};
	return (childrenOf.get(rootId) ?? [])
		.sort((a, b) => (orderOf.get(a) ?? 0) - (orderOf.get(b) ?? 0))
		.map(build);
}

/** Comma-listed alternates of a reflex (its reflex-variants), for the reflex page. */
export async function getReflexVariants(reflexId: string): Promise<Lemma[]> {
	const vs = await query<Lemma>('SELECT * FROM lemmas WHERE variant_of = ? ORDER BY "order"', [
		reflexId
	]);
	await attachLanguages(vs);
	return vs;
}

export async function getLanguage(id: string): Promise<Language | null> {
	return queryOne<Language>('SELECT * FROM languages WHERE id = ?', [id]);
}

/** Structured tags attested by at least one row in a language. */
export async function getLanguageTags(languageId: string): Promise<string[]> {
	const rows = await query<{ tags: string }>(
		`SELECT DISTINCT tags FROM lemmas
		 WHERE language_id = ? AND tags IS NOT NULL AND tags <> ''`,
		[languageId]
	);
	return [...new Set(rows.flatMap((r) => r.tags.split(/\s+/).filter(Boolean)))];
}

/** Dialect-tag definitions retain the geography and Glottolog metadata removed from languages. */
export async function getLanguageDialects(languageId: string): Promise<Dialect[]> {
	return query<Dialect>(
		`SELECT * FROM dialects WHERE language_id = ? AND lemma_count > 0
		 ORDER BY name, id`,
		[languageId]
	);
}

export interface OriginSlice {
	lang: string;
	name: string;
	clade: string | null;
	count: number;
	color?: string; // explicit slice colour (used by the references donut; else clade-derived)
}

/** Deterministic distinct colour for a reference slice (no clade to key off). */
function refColor(s: string): string {
	let h = 0;
	for (let i = 0; i < s.length; i++) h = (Math.imul(h, 31) + s.charCodeAt(i)) >>> 0;
	return `hsl(${h % 360} 52% 58%)`;
}

/** For one language, the distribution of its reflexes across the references that cite them — for a
 *  donut. A reflex cited by several references contributes to each (so counts are citations). */
export async function getReferenceDistribution(languageId: string): Promise<OriginSlice[]> {
	const rows = await query<{ id: string; short: string; c: number }>(
		`SELECT ref.id AS id, ref.short AS short, COUNT(*) AS c
		 FROM lemmas l
		 JOIN lemma_reference lr ON lr.lemma_rid = l.rowid
		 JOIN "references" ref ON ref.rowid = lr.reference_rid
		 WHERE l.language_id = ?
		 GROUP BY ref.id ORDER BY c DESC`,
		[languageId]
	);
	return rows.map((r) => ({
		lang: r.id,
		name: r.short || r.id,
		clade: null,
		count: r.c,
		color: refColor(r.short || r.id)
	}));
}

/** For one language, the distribution of its reflexes by the language of their immediate origin
 *  (the etymon they descend from, or the reflex they were borrowed from) — for a donut chart. */
export async function getOriginLangDistribution(languageId: string): Promise<OriginSlice[]> {
	const rows = await query<{ lang: string; c: number }>(
		`SELECT o.language_id AS lang, COUNT(*) AS c
		 FROM lemmas r JOIN lemmas o ON o.id = r.origin_lemma_id
		 WHERE r.language_id = ? AND r.relation IN ('reflex','borrowed')
		 GROUP BY o.language_id ORDER BY c DESC`,
		[languageId]
	);
	const langs = await languageMap();
	const slices: OriginSlice[] = rows.map((r) => {
		const l = langs.get(r.lang);
		return { lang: r.lang, name: l?.name ?? r.lang, clade: l?.clade ?? null, count: r.c };
	});
	// lone (unetymologised) forms have no origin — surface them as their own "origin unknown" slice
	const un = await queryOne<{ c: number }>(
		"SELECT COUNT(*) AS c FROM lemmas WHERE language_id = ? AND relation = 'local'",
		[languageId]
	);
	if (un?.c) slices.push({ lang: '__unetym', name: 'unetymologised', clade: null, count: un.c });
	return slices;
}

export async function getReference(id: string): Promise<Reference | null> {
	return queryOne<Reference>('SELECT * FROM "references" WHERE id = ?', [id]);
}

export async function listReferences(): Promise<Reference[]> {
	return query<Reference>('SELECT * FROM "references" ORDER BY short');
}

/** Distribution of every lemma cited by one reference over its attested languages. */
export async function getReferenceLanguageDistribution(referenceId: string): Promise<OriginSlice[]> {
	const rows = await query<{ lang: string; name: string; clade: string | null; c: number }>(
		`SELECT l.language_id AS lang, lang.name, lang.clade, COUNT(*) AS c
		 FROM lemma_reference lr
		 JOIN "references" r ON r.rowid = lr.reference_rid
		 JOIN lemmas l ON l.rowid = lr.lemma_rid
		 JOIN languages lang ON lang.id = l.language_id
		 WHERE r.id = ?
		 GROUP BY l.language_id, lang.name, lang.clade
		 ORDER BY c DESC, lang.name`,
		[referenceId]
	);
	return rows.map((r) => ({ lang: r.lang, name: r.name, clade: r.clade, count: r.c }));
}

// ---- entry page (headword + grouped reflexes + map dots) -----------------

export interface EntryReflexes {
	groups: CognateGroup[];
	langGroups: Array<[Language, Lemma[]]>;
	total: number;
}

/** Parse a cognateset key "CODE:label" into its display parts. */
export function parseCognateset(key: string | null): { code: string | null; label: string } {
	if (!key) return { code: null, label: '' };
	const idx = key.indexOf(':');
	if (idx === -1) return { code: null, label: key };
	return { code: key.slice(0, idx), label: key.slice(idx + 1) };
}

/** Same-language variant forms of an etymon (alternate spellings / reconstructions), shown apart
 *  from the daughter-language reflexes. */
export async function getEntryVariants(entryId: string): Promise<Lemma[]> {
	// head variants only (same-language alternates of the etymon head); reflex-variants (variant_of
	// set) are shown grouped under their main reflex instead.
	const variants = await query<Lemma>(
		"SELECT * FROM lemmas WHERE origin_lemma_id = ? AND relation = 'variant' " +
			'AND variant_of IS NULL ORDER BY "order"',
		[entryId]
	);
	await attachLanguages(variants);
	await attachReferences(variants);
	return variants;
}

export async function getEntryReflexes(entryId: string): Promise<EntryReflexes> {
	const reflexes = await query<Lemma>(
		"SELECT * FROM lemmas WHERE origin_lemma_id = ? AND relation IN ('reflex','borrowed') " +
			'ORDER BY cognateset',
		[entryId]
	);
	await attachLanguages(reflexes);
	await attachReferences(reflexes);
	await attachSubCounts(reflexes);
	const total = reflexes.length;

	// group by cognateset, then by language (mirrors app.py:336-381, defaulting to grouped view)
	const byCog = new Map<string | null, Lemma[]>();
	for (const r of reflexes) {
		const key = r.cognateset || null;
		const arr = byCog.get(key);
		if (arr) arr.push(r);
		else byCog.set(key, [r]);
	}
	const groups: CognateGroup[] = [];
	// non-null cognatesets first (sorted by first member id), then the Unclassified bucket
	const keys = [...byCog.keys()].sort((a, b) => {
		if (a === null) return 1;
		if (b === null) return -1;
		return (byCog.get(a)![0].id ?? '').localeCompare(byCog.get(b)![0].id ?? '');
	});
	const langComparator = (a: Lemma, b: Lemma) =>
		(a.language!.order - b.language!.order) || a.language!.name.localeCompare(b.language!.name);
	for (const key of keys) {
		const members = byCog.get(key)!.slice().sort(langComparator);
		const byLang: Array<[Language, Lemma[]]> = [];
		let cur: [Language, Lemma[]] | null = null;
		for (const m of members) {
			if (!cur || cur[0].id !== m.language!.id) {
				cur = [m.language!, [m]];
				byLang.push(cur);
			} else cur[1].push(m);
		}
		groups.push([key, byLang]);
	}

	// map dots: one per language, ordered by (order, name)
	const langSorted = reflexes.slice().sort(langComparator);
	const langGroups: Array<[Language, Lemma[]]> = [];
	let curL: [Language, Lemma[]] | null = null;
	for (const r of langSorted) {
		if (!curL || curL[0].id !== r.language!.id) {
			curL = [r.language!, [r]];
			langGroups.push(curL);
		} else curL[1].push(r);
	}

	return { groups, langGroups, total };
}

// ---- descent + sound-change (materialised alignments) --------------------

export interface AlignSeg {
	pos: number;
	etymonIdx: number; // -1 for an insertion
	etymonSeg: string;
	reflexSeg: string;
	change: string; // category code (see soundChange.ts)
}
export interface AlignedReflex {
	lemma: Lemma;
	segs: AlignSeg[];
}
export interface EntryAlignment {
	etymon: { idx: number; seg: string }[];
	reflexes: AlignedReflex[];
}

export async function getEntryAlignment(entryId: string): Promise<EntryAlignment> {
	// a node's children: an etymon/section-form's daughter reflexes, or a reflex's borrowed sub-reflexes
	const reflexes = await query<Lemma>(
		"SELECT * FROM lemmas WHERE origin_lemma_id = ? AND relation IN ('reflex','borrowed') " +
			'ORDER BY "order"',
		[entryId]
	);
	await attachLanguages(reflexes);
	await attachReferences(reflexes);
	await attachSubCounts(reflexes);

	// attach each main reflex's comma-listed alternates (reflex-variants) for inline display
	const rvars = await query<Lemma>(
		"SELECT * FROM lemmas WHERE origin_lemma_id = ? AND relation = 'variant' " +
			'AND variant_of IS NOT NULL ORDER BY "order"',
		[entryId]
	);
	const byMain = new Map<string, Lemma[]>();
	for (const v of rvars) {
		const arr = byMain.get(v.variant_of!);
		if (arr) arr.push(v);
		else byMain.set(v.variant_of!, [v]);
	}
	for (const r of reflexes) r.variants = byMain.get(r.id) ?? [];

	const rows = await query<{
		form_id: string;
		pos: number;
		etymon_idx: number;
		etymon_seg: string;
		reflex_seg: string;
		change: string;
	}>(
		`SELECT rf.id AS form_id, a.pos,
		        CASE WHEN es.value = '' THEN -1 ELSE
		          SUM(es.value <> '') OVER
		            (PARTITION BY a.form_rid ORDER BY a.pos ROWS UNBOUNDED PRECEDING) - 1
		        END AS etymon_idx,
		        es.value AS etymon_seg, rs.value AS reflex_seg, cs.value AS change
		 FROM lemmas rf
		 JOIN alignment a ON a.form_rid = rf.rowid
		 JOIN align_pair p ON p.id = a.pair_id
		 JOIN symbols es ON es.id = p.etymon_sid
		 JOIN symbols rs ON rs.id = p.reflex_sid
		 JOIN symbols cs ON cs.id = p.change_sid
		 WHERE rf.origin_lemma_id = ?
		 ORDER BY rf.id, a.pos`,
		[entryId]
	);

	const byForm = new Map<string, AlignSeg[]>();
	const etymonMap = new Map<number, string>();
	for (const r of rows) {
		const seg: AlignSeg = {
			pos: r.pos,
			etymonIdx: r.etymon_idx,
			etymonSeg: r.etymon_seg,
			reflexSeg: r.reflex_seg,
			change: r.change
		};
		const arr = byForm.get(r.form_id);
		if (arr) arr.push(seg);
		else byForm.set(r.form_id, [seg]);
		if (r.etymon_idx >= 0 && !etymonMap.has(r.etymon_idx)) etymonMap.set(r.etymon_idx, r.etymon_seg);
	}
	const etymon = [...etymonMap.entries()]
		.sort((a, b) => a[0] - b[0])
		.map(([idx, seg]) => ({ idx, seg }));
	// keep ALL reflexes (those without a materialised alignment render plain)
	const aligned = reflexes.map((l) => ({ lemma: l, segs: byForm.get(l.id) ?? [] }));
	return { etymon, reflexes: aligned };
}

/** The materialised alignment (etymon→reflex sound-change steps) for a single reflex. */
export async function getReflexAlignment(formId: string): Promise<AlignSeg[]> {
	const rows = await query<{
		pos: number;
		etymon_idx: number;
		etymon_seg: string;
		reflex_seg: string;
		change: string;
	}>(
		`SELECT a.pos,
		        CASE WHEN es.value = '' THEN -1 ELSE
		          SUM(es.value <> '') OVER (ORDER BY a.pos ROWS UNBOUNDED PRECEDING) - 1
		        END AS etymon_idx,
		        es.value AS etymon_seg, rs.value AS reflex_seg, cs.value AS change
		 FROM alignment a
		 JOIN align_pair p ON p.id = a.pair_id
		 JOIN symbols es ON es.id = p.etymon_sid
		 JOIN symbols rs ON rs.id = p.reflex_sid
		 JOIN symbols cs ON cs.id = p.change_sid
		 WHERE a.form_rid = (SELECT rowid FROM lemmas WHERE id = ?) ORDER BY a.pos`,
		[formId]
	);
	return rows.map((r) => ({
		pos: r.pos,
		etymonIdx: r.etymon_idx,
		etymonSeg: r.etymon_seg,
		reflexSeg: r.reflex_seg,
		change: r.change
	}));
}

// ---- sound correspondence explorer ---------------------------------------

export interface ProtoFamily {
	id: string;
	name: string;
}
export interface ProtoSeg {
	seg: string;
	total: number;
}
/** A clade-level, environment-conditioned correspondence cell (from `corr`). */
export interface CorrCtx {
	clade: string;
	prev: string;
	next: string;
	reflexSeg: string;
	change: string;
	n: number;
	example: string;
}
/** A language-level correspondence cell (from `corr_lang`, for branch expansion). */
export interface LangCtx extends CorrCtx {
	lang: string;
	langName: string;
}
/** One reflex row on the correspondence drill-down page. */
export interface CorrReflex {
	id: string; // reflex lemma id
	word: string;
	gloss: string;
	phonemic: string;
	lang: string; // language id
	langName: string; // full "Language: Dialect" name
	language: string; // base language
	dialect: string;
	color: string; // the language's assigned colour (for the clade-tinted row border)
	change: string;
	prev: string;
	next: string;
	entryId: string | null; // origin etymon id (link target; headword not fetched here)
}
export interface CorrQuery {
	proto: string;
	seg: string;
	reflexSeg: string;
	clade?: string | null;
	lang?: string | null;
	prev?: string | null;
	next?: string | null;
}
export interface CorrReflexResult {
	rows: CorrReflex[];
	total: number; // true match count (may exceed rows.length when capped)
	truncated: boolean;
}

export async function getProtoFamilies(): Promise<ProtoFamily[]> {
	// only the four reconstructed proto-families make sense as correspondence sets; the alignment
	// table also carries daughter-language "protos" (e.g. from borrowings), which we exclude here.
	return query<ProtoFamily>(
		`SELECT p.id, p.name FROM (SELECT DISTINCT proto_rid FROM corr_seg) s
		 JOIN languages p ON p.rowid = s.proto_rid
		 WHERE p.id IN ('Indo-Aryan','PDr','PMu','PNur')
		 ORDER BY CASE p.id WHEN 'Indo-Aryan' THEN 0 WHEN 'PDr' THEN 1 WHEN 'PMu' THEN 2 ELSE 3 END`
	);
}

export async function getProtoSegments(proto: string): Promise<ProtoSeg[]> {
	return query<ProtoSeg>(
		`SELECT s.value AS seg, c.total FROM corr_seg c JOIN symbols s ON s.id = c.etymon_sid
		 WHERE c.proto_rid = (SELECT rowid FROM languages WHERE id = ?) ORDER BY c.total DESC`,
		[proto]
	);
}

/** All clade-level context rows for one proto-segment (processed client-side for any environment). */
export async function getSegRows(proto: string, seg: string): Promise<CorrCtx[]> {
	const rows = await query<{
		clade: string;
		prev_seg: string;
		next_seg: string;
		reflex_seg: string;
		change: string;
		n: number;
		example: string;
	}>(
		`SELECT d.name AS clade, ps.value AS prev_seg, ns.value AS next_seg,
		        rs.value AS reflex_seg, cs.value AS change, c.n,
		        ex.id AS example
		 FROM corr c
		 JOIN clades d ON d.id = c.clade_rid
		 JOIN align_pair p ON p.id = c.pair_id
		 JOIN align_context x ON x.id = c.context_id
		 JOIN symbols rs ON rs.id = p.reflex_sid
		 JOIN symbols cs ON cs.id = p.change_sid
		 JOIN symbols ps ON ps.id = x.prev_sid
		 JOIN symbols ns ON ns.id = x.next_sid
		 JOIN lemmas ex ON ex.rowid = c.example_rid
		 WHERE c.proto_rid = (SELECT rowid FROM languages WHERE id = ?)
		   AND c.etymon_sid = (SELECT id FROM symbols WHERE value = ?)`,
		[proto, seg]
	);
	return rows.map((r) => ({
		clade: r.clade,
		prev: r.prev_seg,
		next: r.next_seg,
		reflexSeg: r.reflex_seg,
		change: r.change,
		n: r.n,
		example: r.example
	}));
}

/** Per-language context rows for one clade (loaded when a branch is expanded). */
export async function getCladeLangRows(
	proto: string,
	seg: string,
	clade: string
): Promise<LangCtx[]> {
	const rows = await query<{
		lang: string;
		langName: string;
		prev_seg: string;
		next_seg: string;
		reflex_seg: string;
		change: string;
		n: number;
		example: string;
	}>(
		`SELECT l.id AS lang, l.name AS langName, ps.value AS prev_seg,
		        ns.value AS next_seg, rs.value AS reflex_seg, cs.value AS change,
		        cl.n, ex.id AS example
		 FROM corr_lang cl
		 JOIN languages l ON l.rowid = cl.lang_rid
		 JOIN align_pair p ON p.id = cl.pair_id
		 JOIN align_context x ON x.id = cl.context_id
		 JOIN symbols rs ON rs.id = p.reflex_sid
		 JOIN symbols cs ON cs.id = p.change_sid
		 JOIN symbols ps ON ps.id = x.prev_sid
		 JOIN symbols ns ON ns.id = x.next_sid
		 JOIN lemmas ex ON ex.rowid = cl.example_rid
		 WHERE cl.proto_rid = (SELECT rowid FROM languages WHERE id = ?)
		   AND cl.etymon_sid = (SELECT id FROM symbols WHERE value = ?) AND l.clade = ?`,
		[proto, seg, clade]
	);
	return rows.map((r) => ({
		lang: r.lang,
		langName: r.langName,
		clade,
		prev: r.prev_seg,
		next: r.next_seg,
		reflexSeg: r.reflex_seg,
		change: r.change,
		n: r.n,
		example: r.example
	}));
}

/** Build the WHERE fragment for the `corr_lang` summary (used for the true total). */
function corrLangFilter(q: CorrQuery): { where: string; params: unknown[] } {
	const conds = [
		'cl.proto_rid = (SELECT rowid FROM languages WHERE id = ?)',
		'cl.etymon_sid = (SELECT id FROM symbols WHERE value = ?)',
		`cl.pair_id IN (SELECT p.id FROM align_pair p
		                  JOIN symbols s ON s.id = p.reflex_sid WHERE s.value = ?)`
	];
	const params: unknown[] = [q.proto, q.seg, q.reflexSeg];
	if (q.clade) {
		conds.push('cl.lang_rid IN (SELECT rowid FROM languages WHERE clade = ?)');
		params.push(q.clade);
	}
	if (q.lang) {
		conds.push('cl.lang_rid = (SELECT rowid FROM languages WHERE id = ?)');
		params.push(q.lang);
	}
	if (q.prev) {
		conds.push(`cl.context_id IN (SELECT x.id FROM align_context x
		                            JOIN symbols s ON s.id = x.prev_sid WHERE s.value = ?)`);
		params.push(q.prev);
	}
	if (q.next) {
		conds.push(`cl.context_id IN (SELECT x.id FROM align_context x
		                            JOIN symbols s ON s.id = x.next_sid WHERE s.value = ?)`);
		params.push(q.next);
	}
	return { where: conds.join(' AND '), params };
}

/** Every reflex exhibiting a given correspondence (etymon segment → reflex segment), for the
 *  drill-down page. Scans the compact integer-coded alignment rows, then joins lemmas/languages
 *  for the proto/clade filters and display columns. The true total comes from `corr_lang`. */
export async function getCorrespondenceReflexes(
	q: CorrQuery,
	limit = 300
): Promise<CorrReflexResult> {
	const conds = ['es.value = ?', 'rs.value = ?', 'e.language_id = ?'];
	const params: unknown[] = [q.seg, q.reflexSeg, q.proto];
	if (q.clade) {
		conds.push('rl.clade = ?');
		params.push(q.clade);
	}
	if (q.lang) {
		conds.push('rf.language_id = ?');
		params.push(q.lang);
	}
	if (q.prev) {
		conds.push('ps.value = ?');
		params.push(q.prev);
	}
	if (q.next) {
		conds.push('ns.value = ?');
		params.push(q.next);
	}
	const rows = await query<{
		id: string;
		word: string;
		gloss: string;
		phonemic: string;
		lang: string;
		langName: string;
		language: string;
		dialect: string;
		color: string;
		change: string;
		prev_seg: string;
		next_seg: string;
		entryId: string | null;
	}>(
		`SELECT rf.id, rf.word, rf.gloss, rf.phonemic,
		        rf.language_id AS lang, COALESCE(rl.name, rf.language_id) AS langName,
		        rl.language AS language, rl.dialect AS dialect, rl.color AS color,
		        cs.value AS change, ps.value AS prev_seg, ns.value AS next_seg,
		        e.id AS entryId
		 FROM alignment a
		 JOIN align_pair p ON p.id = a.pair_id
		 JOIN align_context x ON x.id = a.context_id
		 JOIN symbols es ON es.id = p.etymon_sid
		 JOIN symbols rs ON rs.id = p.reflex_sid
		 JOIN symbols cs ON cs.id = p.change_sid
		 JOIN symbols ps ON ps.id = x.prev_sid
		 JOIN symbols ns ON ns.id = x.next_sid
		 JOIN lemmas rf    ON rf.rowid = a.form_rid
		 JOIN lemmas e     ON e.id = rf.origin_lemma_id
		 JOIN languages rl ON rl.id = rf.language_id
		 WHERE ${conds.join(' AND ')}
		 ORDER BY rl."order", rf.language_id, rf."order"
		 LIMIT ?`,
		[...params, limit]
	);
	const mapped = rows.map((r) => ({
		id: r.id,
		word: r.word,
		gloss: r.gloss,
		phonemic: r.phonemic,
		lang: r.lang,
		langName: r.langName,
		language: r.language,
		dialect: r.dialect,
		color: r.color,
		change: r.change,
		prev: r.prev_seg,
		next: r.next_seg,
		entryId: r.entryId
	}));
	// True total from the compact summary table — cheap indexed lookup, no big-table COUNT.
	let total = mapped.length;
	if (mapped.length >= limit) {
		const f = corrLangFilter(q);
		const c = await queryOne<{ n: number }>(
			`SELECT COALESCE(SUM(cl.n), 0) AS n FROM corr_lang cl WHERE ${f.where}`,
			f.params
		);
		total = c?.n ?? mapped.length;
	}
	return { rows: mapped, total, truncated: mapped.length < total };
}

// ---- compare two languages ------------------------------------------------

export interface CompareRow {
	entryId: string;
	entryWord: string;
	left: Lemma[];
	right: Lemma[];
}

export async function compareLanguages(
	id1: string,
	id2: string
): Promise<{ lang1: Language | null; lang2: Language | null; rows: CompareRow[] }> {
	const [lang1, lang2] = await Promise.all([getLanguage(id1), getLanguage(id2)]);
	const load = (lid: string) =>
		query<Lemma>(
			`SELECT id, word, gloss, phonemic, "order", language_id, origin_lemma_id
			 FROM lemmas WHERE language_id = ? AND origin_lemma_id IS NOT NULL ORDER BY "order"`,
			[lid]
		);
	const [r1, r2] = await Promise.all([load(id1), load(id2)]);

	const dict = (rows: Lemma[]) => {
		const m = new Map<string, Lemma[]>();
		for (const r of rows) {
			const k = r.origin_lemma_id!;
			const a = m.get(k);
			if (a) a.push(r);
			else m.set(k, [r]);
		}
		return m;
	};
	const d1 = dict(r1);
	const d2 = dict(r2);
	const shared = [...d1.keys()].filter((k) => d2.has(k));

	// fetch headwords for the shared entries
	const heads = await inChunks<Lemma>(shared, (chunk) =>
		query<Lemma>(`SELECT id, word FROM lemmas WHERE id IN (${placeholders(chunk.length)})`, chunk)
	);
	const headMap = new Map(heads.map((h) => [h.id, h.word]));

	const rows: CompareRow[] = shared
		.map((k) => ({
			entryId: k,
			entryWord: headMap.get(k) ?? k,
			left: d1.get(k)!,
			right: d2.get(k)!
		}))
		.sort((a, b) => a.entryId.localeCompare(b.entryId, undefined, { numeric: true }));

	return { lang1, lang2, rows };
}

export { CLADE_ORDER };


// ---- isoglosses: pairwise coupling between clades / languages -----------------------------------
//
// The data are binary presence variables: for each etymon, which clades (or languages) reflect it.
// Two related reads of the pairwise "Ising" coupling over these variables, each picked for its job:
//
//   • couplingModel   — a cheap Gaussian graphical model (partial correlations from the shrunk
//                       inverse covariance). Recomputed on every filter change to colour the map,
//                       where we only need similar units to land near each other in colour space.
//   • conditionalOdds — the exact pairwise-maximum-entropy conditional P(x_i = 1 | the rest), fit by
//                       logistic pseudo-likelihood. Run once per click for the quantitative J / odds
//                       shown in the affinity table.

/** Gauss-Jordan inverse of a small square matrix (item count is at most a couple hundred). */
function invert(A: number[][]): number[][] {
	const n = A.length;
	const M = A.map((row, i) => [...row, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
	for (let col = 0; col < n; col++) {
		let piv = col;
		for (let r = col + 1; r < n; r++) if (Math.abs(M[r][col]) > Math.abs(M[piv][col])) piv = r;
		[M[col], M[piv]] = [M[piv], M[col]];
		const d = M[col][col];
		if (Math.abs(d) < 1e-12) continue;
		for (let j = 0; j < 2 * n; j++) M[col][j] /= d;
		for (let r = 0; r < n; r++)
			if (r !== col) {
				const f = M[r][col];
				for (let j = 0; j < 2 * n; j++) M[r][j] -= f * M[col][j];
			}
	}
	return M.map((row) => row.slice(n));
}

/** Cyclic Jacobi eigen-decomposition of a symmetric matrix (Numerical-Recipes rotations). Returns
 *  eigenvalues and their eigenvectors as the COLUMNS of `vectors`. n is at most a couple hundred, so
 *  the O(n^3) sweeps are cheap. */
function jacobiEigen(Ain: number[][]): { values: number[]; vectors: number[][] } {
	const n = Ain.length;
	const a = Ain.map((r) => r.slice());
	const v = Array.from({ length: n }, (_, i) =>
		Array.from({ length: n }, (_, j): number => (i === j ? 1 : 0))
	);
	for (let iter = 0; iter < 100; iter++) {
		let off = 0;
		for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += a[p][q] * a[p][q];
		if (off < 1e-16) break;
		for (let p = 0; p < n; p++)
			for (let q = p + 1; q < n; q++) {
				const apq = a[p][q];
				if (Math.abs(apq) < 1e-18) continue;
				const theta = (a[q][q] - a[p][p]) / (2 * apq);
				const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
				const c = 1 / Math.sqrt(t * t + 1);
				const s = t * c;
				const tau = s / (1 + c);
				a[p][p] -= t * apq;
				a[q][q] += t * apq;
				a[p][q] = a[q][p] = 0;
				for (let k = 0; k < n; k++)
					if (k !== p && k !== q) {
						const akp = a[k][p];
						const akq = a[k][q];
						a[k][p] = a[p][k] = akp - s * (akq + tau * akp);
						a[k][q] = a[q][k] = akq + s * (akp - tau * akq);
					}
				for (let k = 0; k < n; k++) {
					const vkp = v[k][p];
					const vkq = v[k][q];
					v[k][p] = vkp - s * (vkq + tau * vkp);
					v[k][q] = vkq + s * (vkp - tau * vkq);
				}
			}
	}
	return { values: a.map((row, i) => row[i]), vectors: v };
}

/** Spectral embedding of an affinity/coupling matrix: the eigenvectors of the `dims` largest
 *  eigenvalues, each scaled by sqrt(eigenvalue) so the leading axes dominate — i.e. the principal
 *  components of the affinity matrix. Returns one `dims`-vector per item (item order preserved).
 *  Signs are fixed deterministically (largest-magnitude entry made positive) so colours are stable. */
export function spectralEmbedding(coupling: number[][], dims = 3): number[][] {
	const n = coupling.length;
	if (n === 0) return [];
	const { values, vectors } = jacobiEigen(coupling);
	const top = [...values.keys()].sort((i, j) => values[j] - values[i]).slice(0, dims);
	// deterministic sign per component
	const sign = top.map((j) => {
		let m = 0;
		let sg = 1;
		for (let i = 0; i < n; i++) {
			const val = vectors[i][j];
			if (Math.abs(val) > m) {
				m = Math.abs(val);
				sg = val >= 0 ? 1 : -1;
			}
		}
		return sg;
	});
	return Array.from({ length: n }, (_, i) =>
		top.map((j, d) => sign[d] * vectors[i][j] * Math.sqrt(Math.max(values[j], 0)))
	);
}

/** Pairwise coupling matrix for a set of binary presence variables — the Gaussian graphical model
 *  used to colour the map. Covariance of the indicators over `sets` → fixed-intensity shrinkage of
 *  the off-diagonals toward zero (keeps the matrix well-conditioned for inversion) → precision →
 *  partial correlation rho_ij = -P_ij / sqrt(P_ii P_jj), with rho_ii = 1. */
export function couplingModel(sets: string[][], items: string[]): number[][] {
	const n = items.length;
	if (n === 0) return [];
	const idx = new Map(items.map((it, i) => [it, i]));
	const N = sets.length || 1;
	const co = Array.from({ length: n }, () => new Array<number>(n).fill(0));
	const cnt = new Array<number>(n).fill(0);
	for (const s of sets) {
		const ii: number[] = [];
		for (const it of s) {
			const k = idx.get(it);
			if (k !== undefined) ii.push(k);
		}
		for (let a = 0; a < ii.length; a++) {
			cnt[ii[a]]++;
			for (let b = a + 1; b < ii.length; b++) {
				co[ii[a]][ii[b]]++;
				co[ii[b]][ii[a]]++;
			}
		}
	}
	const cov = Array.from({ length: n }, () => new Array<number>(n).fill(0));
	for (let a = 0; a < n; a++)
		for (let b = 0; b < n; b++) {
			const pa = cnt[a] / N,
				pb = cnt[b] / N;
			const pab = a === b ? pa : co[a][b] / N;
			cov[a][b] = pab - pa * pb;
		}
	const shrink = 0.1;
	for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) if (a !== b) cov[a][b] *= 1 - shrink;
	for (let a = 0; a < n; a++) if (cov[a][a] < 1e-9) cov[a][a] = 1e-9;
	const prec = invert(cov);
	const coupling = Array.from({ length: n }, () => new Array<number>(n).fill(0));
	for (let a = 0; a < n; a++)
		for (let b = 0; b < n; b++) {
			if (a === b) coupling[a][b] = 1;
			else {
				const den = Math.sqrt(prec[a][a] * prec[b][b]);
				coupling[a][b] = den ? -prec[a][b] / den : 0;
			}
		}
	return coupling;
}

/** Exact pairwise-maximum-entropy conditional: fit P(x_target = 1 | all other units) by
 *  L2-regularised logistic pseudo-likelihood and return each other unit's log-odds effect bⱼ.
 *  e^{bⱼ} is the multiplier on the target's presence odds when unit j is present vs absent, holding
 *  every other unit fixed — the tangible "odds of a shared reflex" read of the Ising coupling.
 *  Solved by Newton/IRLS on the mean logistic loss, which reaches the optimum in a handful of steps
 *  (a couple hundred units, one fit per click). Returns log-odds aligned to `items`; target's own
 *  entry is 0. */
export function conditionalOdds(sets: string[][], items: string[], target: string): number[] {
	const n = items.length;
	const idx = new Map(items.map((it, i) => [it, i]));
	const ti = idx.get(target);
	if (ti === undefined || n < 2) return new Array<number>(n).fill(0);
	// parameter layout: column 0 is the intercept, then one column per non-target unit (so m = n)
	const col = new Array<number>(n).fill(-1);
	let m = 1;
	for (let k = 0; k < n; k++) if (k !== ti) col[k] = m++;
	// each etymon → the columns of its present non-target units + whether the target is present (y)
	const rows: { cols: number[]; y: number }[] = [];
	let yc = 0;
	for (const s of sets) {
		const cols: number[] = [];
		let y = 0;
		for (const it of s) {
			const k = idx.get(it);
			if (k === undefined) continue;
			if (k === ti) y = 1;
			else cols.push(col[k]);
		}
		rows.push({ cols, y });
		yc += y;
	}
	const N = rows.length || 1;
	const lambda = 1 / N; // mild L2 on the couplings (the intercept is left unpenalised)
	const theta = new Array<number>(m).fill(0);
	theta[0] = Math.log((yc + 1) / (N - yc + 1)); // init at the target's marginal log-odds

	// mean logistic loss + ridge, evaluated at an arbitrary parameter vector (for the line search)
	const loss = (th: number[]): number => {
		let nll = 0;
		for (const { cols, y } of rows) {
			let z = th[0];
			for (const c of cols) z += th[c];
			// softplus(z) − y·z, in the numerically stable branch
			nll += (z > 0 ? z + Math.log1p(Math.exp(-z)) : Math.log1p(Math.exp(z))) - y * z;
		}
		let pen = 0;
		for (let c = 1; c < m; c++) pen += th[c] * th[c];
		return nll / N + 0.5 * lambda * pen;
	};

	// Newton / IRLS with a backtracking line search. The raw Newton step can overshoot into the
	// region where the sigmoid saturates (the fit becomes separable for sparse units), so we only
	// accept a step that actually decreases the loss — this keeps the fast convergence while
	// guaranteeing the couplings stay at the finite regularised optimum.
	const cand = new Array<number>(m).fill(0);
	for (let iter = 0; iter < 50; iter++) {
		const g = new Array<number>(m).fill(0);
		const H = Array.from({ length: m }, () => new Array<number>(m).fill(0));
		for (const { cols, y } of rows) {
			let z = theta[0];
			for (const c of cols) z += theta[c];
			const p = 1 / (1 + Math.exp(-z));
			const w = p * (1 - p);
			const e = p - y;
			g[0] += e;
			H[0][0] += w;
			for (const c of cols) {
				g[c] += e;
				H[0][c] += w;
				H[c][0] += w;
			}
			for (let x = 0; x < cols.length; x++) {
				const ca = cols[x];
				H[ca][ca] += w;
				for (let z2 = x + 1; z2 < cols.length; z2++) {
					const cb = cols[z2];
					H[ca][cb] += w;
					H[cb][ca] += w;
				}
			}
		}
		for (let i = 0; i < m; i++) {
			g[i] /= N;
			for (let j = 0; j < m; j++) H[i][j] /= N;
		}
		for (let c = 1; c < m; c++) {
			g[c] += lambda * theta[c]; // ridge keeps H positive-definite even under collinearity
			H[c][c] += lambda;
		}
		const Hinv = invert(H);
		const delta = new Array<number>(m).fill(0);
		for (let i = 0; i < m; i++) {
			let d = 0;
			for (let j = 0; j < m; j++) d += Hinv[i][j] * g[j];
			delta[i] = d;
		}
		// backtracking: halve the step until the loss decreases
		const cur = loss(theta);
		let s = 1;
		for (let bt = 0; bt < 40; bt++) {
			for (let i = 0; i < m; i++) cand[i] = theta[i] - s * delta[i];
			if (loss(cand) <= cur) break;
			s *= 0.5;
		}
		let step = 0;
		for (let i = 0; i < m; i++) {
			const d = s * delta[i];
			theta[i] -= d;
			if (Math.abs(d) > step) step = Math.abs(d);
		}
		if (step < 1e-9) break; // converged
	}
	const b = new Array<number>(n).fill(0);
	for (let k = 0; k < n; k++) if (k !== ti) b[k] = theta[col[k]];
	return b;
}

export interface IsoglossData {
	family: string;
	entryCount: number;
	cladeSets: string[][]; // per-etymon clade lists (models built client-side so filters can apply)
	// raw per-etymon language sets + per-language etyma counts, so the language model can be
	// thresholded / filtered and recomputed client-side without another query
	langSets: string[][];
	langCount: [string, number][];
	langName: Record<string, string>;
	langClade: Record<string, string>;
}

/** Fetch the reflex clade/language incidence for a proto-family's etyma and build the clade-level
 *  Ising coupling; language-level coupling is built on demand (thresholded) via couplingModel. */
export async function getIsoglossData(family: string): Promise<IsoglossData> {
	const rows = await query<{ entry: string; clade: string; lang: string; lname: string }>(
		`SELECT DISTINCT l.origin_lemma_id AS entry, lang.clade AS clade, lang.id AS lang, lang.name AS lname
		 FROM lemmas l JOIN languages lang ON lang.id = l.language_id
		 WHERE l.relation = 'reflex' AND lang.clade IS NOT NULL AND lang.clade != ''
		   AND l.origin_lemma_id IN (SELECT id FROM lemmas WHERE origin_lemma_id IS NULL AND language_id = ?)`,
		[family]
	);
	const cladeByEntry = new Map<string, Set<string>>();
	const langByEntry = new Map<string, Set<string>>();
	const langName: Record<string, string> = {};
	const langClade: Record<string, string> = {};
	for (const r of rows) {
		let cs = cladeByEntry.get(r.entry);
		if (!cs) cladeByEntry.set(r.entry, (cs = new Set()));
		cs.add(r.clade);
		let ls = langByEntry.get(r.entry);
		if (!ls) langByEntry.set(r.entry, (ls = new Set()));
		ls.add(r.lang);
		langName[r.lang] = r.lname;
		langClade[r.lang] = r.clade;
	}
	const cladeSets = [...cladeByEntry.values()].map((s) => [...s]);
	const langSets = [...langByEntry.values()].map((s) => [...s]);
	const langCount = new Map<string, number>();
	for (const s of langSets) for (const l of s) langCount.set(l, (langCount.get(l) ?? 0) + 1);
	return {
		family,
		entryCount: cladeByEntry.size,
		cladeSets,
		langSets,
		langCount: [...langCount.entries()],
		langName,
		langClade
	};
}

/** Presence-invariant sound-change isogloss model. For each proto-slot (etymon x aligned position)
 *  every clade/language *present* has an outcome (its reflex segment); two units "agree" at a slot
 *  when both are present with the same outcome. Returns, per unit pair, the number of jointly-
 *  attested slots (both) and how many of those agree (agree), computed in SQL so only the small pair
 *  matrix crosses the wire. Absence is pairwise-deleted, so a pair's agreement rate agree/both
 *  depends only on how the two behave where both have the word -- invariant to lexical presence
 *  (which the reflex-coupling model already captures). Keyed "a|b" with a < b. */
export interface SoundAgreement {
	pair: Map<string, { both: number; agree: number }>;
}
export async function getIsoglossSoundChangeData(
	family: string,
	level: 'clade' | 'lang'
): Promise<SoundAgreement> {
	const unit = level === 'clade' ? 'clade' : 'id'; // controlled column, not user input
	const rows = await query<{ i: string; j: string; both: number; agree: number }>(
		`WITH base AS (
		   SELECT l.origin_lemma_id AS e, a.pos AS p, lang.${unit} AS u, ap.reflex_sid AS o
		   FROM alignment a JOIN lemmas l ON l.rowid = a.form_rid
		   JOIN languages lang ON lang.id = l.language_id JOIN align_pair ap ON ap.id = a.pair_id
		   WHERE l.relation = 'reflex' AND lang.clade IS NOT NULL AND lang.clade != ''
		     AND l.origin_lemma_id IN (SELECT id FROM lemmas WHERE origin_lemma_id IS NULL AND language_id = ?)),
		 present AS (SELECT DISTINCT e, p, u FROM base),
		 shared  AS (SELECT DISTINCT e, p, u, o FROM base),
		 both AS (SELECT pa.u i, pb.u j, COUNT(*) n FROM present pa JOIN present pb
		            ON pa.e = pb.e AND pa.p = pb.p AND pa.u < pb.u GROUP BY pa.u, pb.u),
		 agr  AS (SELECT sa.u i, sb.u j, COUNT(*) n FROM shared sa JOIN shared sb
		            ON sa.e = sb.e AND sa.p = sb.p AND sa.o = sb.o AND sa.u < sb.u GROUP BY sa.u, sb.u)
		 SELECT b.i AS i, b.j AS j, b.n AS both, COALESCE(a.n, 0) AS agree
		 FROM both b LEFT JOIN agr a ON a.i = b.i AND a.j = b.j`,
		[family]
	);
	const pair = new Map<string, { both: number; agree: number }>();
	for (const r of rows) pair.set(`${r.i}|${r.j}`, { both: r.both, agree: r.agree });
	return { pair };
}
