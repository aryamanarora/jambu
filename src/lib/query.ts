/**
 * query.ts — client-side query layer, the port of neojambu's `search.py` + the entry-page
 * grouping in `app.py`. All queries run in the browser against the chunked SQLite via db.ts.
 *
 * Design notes for HTTP Range efficiency:
 *  - Text search scans the compact local lemma table with `instr`; it is gated at MIN_SEARCH_CHARS
 *    so 1–2 character partials never trigger a scan.
 *  - The 615-row `languages` and 194-row `references` tables are loaded/queried cheaply and
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
			? "WHERE origin_lemma_id IS NULL OR EXISTS (SELECT 1 FROM lemmas b " +
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
			`SELECT l.id AS lemma_id, r.id, r.short, r.source, r.progress
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
		const ref: Reference = { id: row.id, short: row.short, source: row.source, progress: row.progress };
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
		conds.push({ sql: 'l.language_id = ?', params: [p.origin_lang.trim()] });
	}
	if (p.etymon_lang?.trim()) {
		conds.push({
			sql: 'l.origin_lemma_id IN (SELECT id FROM lemmas WHERE language_id = ?)',
			params: [p.etymon_lang.trim()]
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
	params: ListParams;
	withOrigin?: boolean; // attach origin_lemma (reflexes/lexicon show it)
}

export async function fetchLemmaList(opts: ListOpts): Promise<ListResult> {
	const { mode, languageId, params } = opts;
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
		else modeConds.push({ sql: 'l.origin_lemma_id IS NULL', params: [] });
	}
	if (mode === 'lexicon' && languageId)
		modeConds.push({ sql: 'l.language_id = ?', params: [languageId] });

	const all = [...modeConds, ...conds];
	const whereParams = all.flatMap((c) => c.params);
	const whereSql = all.length ? 'WHERE ' + all.map((c) => c.sql).join(' AND ') : '';

	const join = needsLangJoin ? 'JOIN languages lang ON lang.id = l.language_id' : '';

	// Fast path: entries list with no filters/sort → partial index, no join, no temp sort.
	const isDefaultEntries =
		mode === 'entries' &&
		!needsLangJoin &&
		conds.length === 0 &&
		!params.loanSourcesOnly &&
		!(params.sort ?? '').trim();

	const fallbackOrder =
		mode === 'entries' || mode === 'lexicon' ? 'l."order"' : 'l."order"';
	const order = orderBy(params, fallbackOrder);

	// count — use precomputed totals for the unfiltered case (a full COUNT(*) is a whole-index
	// scan = a large sequential read over the wire); only COUNT the (bounded) filtered set.
	const hasFilters = conds.length > 0 || !!params.loanSourcesOnly;
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
		   WHERE l.origin_lemma_id IS NULL AND l.redirect_to IS NULL ORDER BY l."order" LIMIT ${PAGE_SIZE} OFFSET ${offset}`
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

export interface OriginSlice {
	lang: string;
	name: string;
	clade: string | null;
	count: number;
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
	return rows.map((r) => {
		const l = langs.get(r.lang);
		return { lang: r.lang, name: l?.name ?? r.lang, clade: l?.clade ?? null, count: r.c };
	});
}

export async function getReference(id: string): Promise<Reference | null> {
	return queryOne<Reference>('SELECT * FROM "references" WHERE id = ?', [id]);
}

export async function listReferences(): Promise<Reference[]> {
	return query<Reference>('SELECT * FROM "references" ORDER BY short');
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
