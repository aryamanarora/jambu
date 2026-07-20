/**
 * query.ts — client-side query layer, the port of neojambu's `search.py` + the entry-page
 * grouping in `app.py`. All queries run in the browser against the chunked SQLite via db.ts.
 *
 * Design notes for HTTP Range efficiency:
 *  - Text search uses the FTS5 **trigram** index (substring, like the old LIKE '%x%'), gated at
 *    MIN_FTS_CHARS so 1–2 char partials never trigger a full-table scan.
 *  - The 615-row `languages` and 194-row `references` tables are loaded/queried cheaply and
 *    cached; we attach relations in JS rather than doing wide joins over 313k lemma rows.
 *  - The unfiltered list paths avoid the languages join and lean on the order indexes
 *    (idx_lemmas_order / partial idx_entries_order) so only the needed pages are fetched.
 */
import { query, queryOne } from './db.svelte';
import { CLADE_ORDER } from './clades';
import {
	PAGE_SIZE,
	MIN_FTS_CHARS,
	type Language,
	type Lemma,
	type Reference,
	type ListParams,
	type CognateGroup
} from './types';

// ---- small helpers --------------------------------------------------------

function ftsPhrase(v: string): string {
	return '"' + v.replace(/"/g, '""') + '"';
}

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
			`SELECT lr.lemma_id, r.id, r.short, r.source, r.progress
			 FROM lemma_reference lr JOIN "references" r ON r.id = lr.reference_id
			 WHERE lr.lemma_id IN (${placeholders(chunk.length)})
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

	// full-text (trigram) terms combined into one MATCH
	const fts: string[] = [];
	for (const [key, col] of [
		['word', 'word'],
		['gloss', 'gloss'],
		['notes', 'notes']
	] as const) {
		const v = (p[key] ?? '').trim();
		if (v.length >= MIN_FTS_CHARS) fts.push(`${col}:${ftsPhrase(v)}`);
	}
	if (fts.length) {
		conds.push({
			sql: 'l.rowid IN (SELECT rowid FROM lemmas_fts WHERE lemmas_fts MATCH ?)',
			params: [fts.join(' AND ')]
		});
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
	if ((p.origin ?? '').trim().length >= MIN_FTS_CHARS) {
		conds.push({
			sql: `l.origin_lemma_id IN (SELECT id FROM lemmas WHERE rowid IN
			        (SELECT rowid FROM lemmas_fts WHERE lemmas_fts MATCH ?))`,
			params: [`word:${ftsPhrase(p.origin!.trim())}`]
		});
	}
	if (p.source?.trim()) {
		conds.push({
			sql: `EXISTS (SELECT 1 FROM lemma_reference lr JOIN "references" r ON r.id = lr.reference_id
			         WHERE lr.lemma_id = l.id AND r.short LIKE ?)`,
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

	// base mode condition
	const modeConds: Cond[] = [];
	if (mode === 'entries') modeConds.push({ sql: 'l.origin_lemma_id IS NULL', params: [] });
	if (mode === 'lexicon' && languageId)
		modeConds.push({ sql: 'l.language_id = ?', params: [languageId] });

	const all = [...modeConds, ...conds];
	const whereParams = all.flatMap((c) => c.params);
	const whereSql = all.length ? 'WHERE ' + all.map((c) => c.sql).join(' AND ') : '';

	const join = needsLangJoin ? 'JOIN languages lang ON lang.id = l.language_id' : '';

	// Fast path: entries list with no filters/sort → partial index, no join, no temp sort.
	const isDefaultEntries =
		mode === 'entries' && !needsLangJoin && conds.length === 0 && !(params.sort ?? '').trim();

	const fallbackOrder =
		mode === 'entries' || mode === 'lexicon' ? 'l."order"' : 'l."order"';
	const order = orderBy(params, fallbackOrder);

	// count — use precomputed totals for the unfiltered case (a full COUNT(*) is a whole-index
	// scan = a large sequential read over the wire); only COUNT the (bounded) filtered set.
	const hasFilters = conds.length > 0;
	let count: number;
	if (!hasFilters && mode === 'entries') {
		count = await metaCount('total_entries');
	} else if (!hasFilters && mode === 'reflexes') {
		count = await metaCount('total_reflexes');
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
	// how many derived-term etyma each headword spawns (compounds/affixed forms) — entries view only
	const derivedCol =
		mode === 'entries'
			? ', (SELECT COUNT(*) FROM derivation WHERE parent_id = l.id) AS derived_count'
			: '';
	const fetchSql = isDefaultEntries
		? `SELECT l.*${derivedCol} FROM lemmas l INDEXED BY idx_entries_order
		   WHERE l.origin_lemma_id IS NULL ORDER BY l."order" LIMIT ${PAGE_SIZE} OFFSET ${offset}`
		: `SELECT l.*${derivedCol} FROM lemmas l ${join} ${whereSql}
		   ORDER BY ${order} LIMIT ${PAGE_SIZE} OFFSET ${offset}`;
	const rows = await query<Lemma>(fetchSql, isDefaultEntries ? [] : whereParams);

	await attachLanguages(rows);
	if (opts.withOrigin) await attachOrigin(rows);
	await attachReferences(rows);

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

export async function getLanguage(id: string): Promise<Language | null> {
	return queryOne<Language>('SELECT * FROM languages WHERE id = ?', [id]);
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

export async function getEntryReflexes(entryId: string): Promise<EntryReflexes> {
	const reflexes = await query<Lemma>(
		'SELECT * FROM lemmas WHERE origin_lemma_id = ? ORDER BY cognateset',
		[entryId]
	);
	await attachLanguages(reflexes);
	await attachReferences(reflexes);
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
	const reflexes = await query<Lemma>(
		'SELECT * FROM lemmas WHERE origin_lemma_id = ? ORDER BY "order"',
		[entryId]
	);
	await attachLanguages(reflexes);
	await attachReferences(reflexes);

	const rows = await query<{
		form_id: string;
		pos: number;
		etymon_idx: number;
		etymon_seg: string;
		reflex_seg: string;
		change: string;
	}>(
		`SELECT form_id, pos, etymon_idx, etymon_seg, reflex_seg, change
		 FROM alignment WHERE parameter_id = ? ORDER BY form_id, pos`,
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
		`SELECT pos, etymon_idx, etymon_seg, reflex_seg, change
		 FROM alignment WHERE form_id = ? ORDER BY pos`,
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
	return query<ProtoFamily>(
		`SELECT DISTINCT s.proto AS id, COALESCE(l.name, s.proto) AS name
		 FROM corr_seg s LEFT JOIN languages l ON l.id = s.proto ORDER BY s.proto`
	);
}

export async function getProtoSegments(proto: string): Promise<ProtoSeg[]> {
	return query<ProtoSeg>(
		`SELECT etymon_seg AS seg, total FROM corr_seg WHERE proto = ? ORDER BY total DESC`,
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
		`SELECT clade, prev_seg, next_seg, reflex_seg, change, n, example
		 FROM corr WHERE proto = ? AND etymon_seg = ?`,
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
		`SELECT cl.lang, COALESCE(l.name, cl.lang) AS langName, cl.prev_seg, cl.next_seg,
		        cl.reflex_seg, cl.change, cl.n, cl.example
		 FROM corr_lang cl LEFT JOIN languages l ON l.id = cl.lang
		 WHERE cl.proto = ? AND cl.etymon_seg = ? AND cl.clade = ?`,
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
	const conds = ['proto = ?', 'etymon_seg = ?', 'reflex_seg = ?'];
	const params: unknown[] = [q.proto, q.seg, q.reflexSeg];
	if (q.clade) {
		conds.push('clade = ?');
		params.push(q.clade);
	}
	if (q.lang) {
		conds.push('lang = ?');
		params.push(q.lang);
	}
	if (q.prev) {
		conds.push('prev_seg = ?');
		params.push(q.prev);
	}
	if (q.next) {
		conds.push('next_seg = ?');
		params.push(q.next);
	}
	return { where: conds.join(' AND '), params };
}

/** Every reflex exhibiting a given correspondence (etymon segment → reflex segment), for the
 *  drill-down page. Filters `alignment` by (etymon_seg, reflex_seg) via idx_alignment_seg, then
 *  joins lemmas/languages for the proto/clade filters + display columns — cheap on the local DB.
 *  The true total comes from the compact `corr_lang` summary. */
export async function getCorrespondenceReflexes(
	q: CorrQuery,
	limit = 300
): Promise<CorrReflexResult> {
	const conds = ['a.etymon_seg = ?', 'a.reflex_seg = ?', 'e.language_id = ?'];
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
		conds.push('a.prev_seg = ?');
		params.push(q.prev);
	}
	if (q.next) {
		conds.push('a.next_seg = ?');
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
		        a.change, a.prev_seg, a.next_seg,
		        a.parameter_id AS entryId
		 FROM alignment a
		 JOIN lemmas e     ON e.id = a.parameter_id
		 JOIN lemmas rf    ON rf.id = a.form_id
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
			`SELECT COALESCE(SUM(n), 0) AS n FROM corr_lang WHERE ${f.where}`,
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
