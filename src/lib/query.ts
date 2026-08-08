/**
 * query.ts — client-side query layer, the port of neojambu's `search.py` + the entry-page
 * grouping in `app.py`. All queries run in the browser against the compact ("v2") SQLite
 * schema via db.ts; scripts/compact_db.py documents that schema and src/lib/dbShared.ts
 * holds the codecs shared with the build/prerender layer.
 *
 * Design notes:
 *  - The whole DB is local (OPFS) after a one-time download, so full-column scans are cheap;
 *    what we avoid is per-row work proportional to the whole table on hot paths. Lookups go
 *    through rowids: the sorted binary id table (loaded once into this thread) maps public
 *    text ids ↔ lem rowids with no SQL index at all.
 *  - Filters run against the compact base columns (ints, interned tag/cognateset refs, varint
 *    citation blobs via the vin_any() UDF); display rows are rebuilt to the legacy Lemma shape
 *    by hydrateLem so components are unchanged.
 *  - The entries default listing keeps its partial index; the per-language default listing
 *    reads the language's precomputed `lex` rowid list instead of an index.
 */
import { query, queryOne } from './db.svelte';
import { CLADE_ORDER } from './clades';
import {
	IdIndex,
	hydrateLem,
	LEM_COLS,
	LEM_JOINS,
	readVarints,
	readDeltas,
	readCorrCells,
	readCellDict,
	aliasGroupKey,
	aliasLookup,
	FLAG_OCR,
	FLAG_SECTION,
	FLAG_LOAN_SOURCE,
	FLAG_HAS_ALT,
	REL_REFLEX,
	REL_VARIANT,
	REL_BORROWED,
	REL_UNLINKED,
	KIND_COMPONENT,
	KIND_DERIVED,
	type RawLem
} from './dbShared';
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

// ---- core caches (id table, clade mask alphabet, languages) ---------------

let ids: IdIndex | null = null;
let cladeNames: string[] = [];
let corePromise: Promise<void> | null = null;

async function ensureCore(): Promise<IdIndex> {
	if (ids) return ids;
	if (!corePromise) {
		corePromise = (async () => {
			const [idsRow, misc, clades] = await Promise.all([
				queryOne<{ data: Uint8Array }>('SELECT data FROM ids'),
				query<{ id: string }>('SELECT id FROM ids_misc ORDER BY rank'),
				query<{ name: string }>('SELECT name FROM mask_clades ORDER BY rowid'),
				getAllLanguages()
			]);
			cladeNames = clades.map((r) => r.name);
			ids = new IdIndex(
				idsRow!.data,
				misc.map((r) => r.id)
			);
		})();
	}
	await corePromise;
	return ids!;
}

/** JSON rowid-list parameter for `IN (SELECT value FROM json_each(?))` predicates. */
function jsonList(rids: number[]): string {
	return JSON.stringify(rids);
}
const IN_JSON = '(SELECT value FROM json_each(?))';

/** v3: link_rid carries only redirects, so this is a plain null check. */
const NOT_REDIRECT = 'l.link_rid IS NULL';

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
let languagesByRid: Map<number, Language> | null = null;

const LANGUAGE_COLS =
	'rowid AS rid, id, name, language, dialect, glottocode, long, lat, clade, color, ' +
	'lemma_count, "order", map_marker';

export async function getAllLanguages(): Promise<Language[]> {
	if (languagesCache) return [...languagesCache.values()];
	const list = await query<Language & { rid: number }>(`SELECT ${LANGUAGE_COLS} FROM languages`);
	if (!languagesCache) {
		languagesCache = new Map(list.map((l) => [l.id, l]));
		languagesByRid = new Map(list.map((l) => [l.rid, l]));
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

function langByRid(rid: number): Language | undefined {
	return languagesByRid?.get(rid);
}

function langRidOf(id: string): number | null {
	const l = languagesCache?.get(id) as (Language & { rid: number }) | undefined;
	return l?.rid ?? null;
}

// ---- lemma row hydration --------------------------------------------------

/** Lemma plus the internal v2 fields every hydrated row carries. */
type HLemma = Lemma & { rid: number; citeIds: number[]; childRids: number[] };

function hydrate(row: RawLem): HLemma {
	const l = hydrateLem(row, {
		ids: ids!,
		langIdOf: (rid) => langByRid(rid)?.id ?? '',
		cladeNames
	}) as unknown as HLemma;
	// carry through any computed extras (e.g. `secondary` from UNION queries)
	const raw = row as unknown as Record<string, unknown>;
	for (const k of Object.keys(raw)) {
		if (!(k in l) && k !== 'cites' && k !== 'children' && k !== 'clades_mask' && k !== 'counts')
			(l as unknown as Record<string, unknown>)[k] = raw[k];
	}
	return l;
}

const LEM_SELECT = `SELECT ${LEM_COLS} FROM lem l ${LEM_JOINS}`;

/** Fetch + hydrate rows for an explicit rowid list, preserving the list's order. */
async function lemmasByRids(rids: number[]): Promise<HLemma[]> {
	if (!rids.length) return [];
	await ensureCore();
	const rows = await query<RawLem>(`${LEM_SELECT} WHERE l.rowid IN ${IN_JSON}`, [jsonList(rids)]);
	const byRid = new Map(rows.map((r) => [r.rid, hydrate(r)]));
	return rids.map((r) => byRid.get(r)).filter((l): l is HLemma => !!l);
}

/** The children blob of one node (its reflexes/variants/borrowed forms, in display order). */
async function childRidsOf(rid: number): Promise<number[]> {
	const r = await queryOne<{ children: Uint8Array | null }>(
		'SELECT children FROM lem WHERE rowid = ?',
		[rid]
	);
	return readVarints(r?.children);
}

// ---- citation cache (15.5k distinct citation edges) -----------------------

interface CiteRow {
	ref: number;
	locator: string;
}
let citesCache: Map<number, CiteRow> | null = null;
let referencesByRid: Map<number, Reference> | null = null;
let citesPromise: Promise<void> | null = null;

async function ensureCites(): Promise<void> {
	if (citesCache) return;
	if (!citesPromise) {
		citesPromise = (async () => {
			const [cites, refs] = await Promise.all([
				query<{ rid: number; ref_rid: number; locator: string }>(
					'SELECT rowid AS rid, ref_rid, locator FROM cites'
				),
				query<Reference & { rid: number }>('SELECT rowid AS rid, * FROM "references"')
			]);
			citesCache = new Map(cites.map((c) => [c.rid, { ref: c.ref_rid, locator: c.locator }]));
			referencesByRid = new Map(refs.map((r) => [r.rid, r]));
		})();
	}
	await citesPromise;
}

/** Cite ids whose reference matches a predicate (for source / reference filters). */
async function citeIdsWhere(refPred: (r: Reference & { rid: number }) => boolean): Promise<number[]> {
	await ensureCites();
	const wanted = new Set<number>();
	for (const r of referencesByRid!.values()) {
		if (refPred(r as Reference & { rid: number })) wanted.add((r as Reference & { rid: number }).rid);
	}
	const out: number[] = [];
	for (const [cid, c] of citesCache!) if (wanted.has(c.ref)) out.push(cid);
	return out;
}

// ---- relation hydration ---------------------------------------------------

async function attachLanguages(lemmas: Lemma[]): Promise<void> {
	const langs = await languageMap();
	for (const l of lemmas) l.language = langs.get(l.language_id);
}

async function attachOrigin(lemmas: HLemma[]): Promise<void> {
	const idx = await ensureCore();
	const rids = [
		...new Set(
			lemmas
				.map((l) => (l.origin_lemma_id ? idx.ridOf(l.origin_lemma_id) : null))
				.filter((r): r is number => r != null)
		)
	];
	if (!rids.length) return;
	const rows = await lemmasByRids(rids);
	await attachLanguages(rows);
	const map = new Map(rows.map((r) => [r.id, r]));
	for (const l of lemmas) l.origin_lemma = l.origin_lemma_id ? (map.get(l.origin_lemma_id) ?? null) : null;
}

async function attachReferences(lemmas: HLemma[]): Promise<void> {
	if (!lemmas.length) return;
	await ensureCites();
	for (const l of lemmas) {
		const perRef = new Map<number, Reference>();
		for (const cid of l.citeIds) {
			const cite = citesCache!.get(cid);
			if (!cite) continue;
			const refRow = referencesByRid!.get(cite.ref);
			if (!refRow) continue;
			const existing = perRef.get(cite.ref);
			if (existing) {
				if (cite.locator && !existing.locator?.split('; ').includes(cite.locator))
					existing.locator = [existing.locator, cite.locator].filter(Boolean).join('; ');
				continue;
			}
			perRef.set(cite.ref, {
				id: refRow.id,
				short: refRow.short,
				source: refRow.source,
				progress: refRow.progress,
				provenance: refRow.provenance,
				editor: refRow.editor,
				ocr: refRow.ocr,
				lemma_count: refRow.lemma_count,
				unetymologised_count: refRow.unetymologised_count,
				locator: cite.locator || undefined
			});
		}
		l.references = [...perRef.values()].sort((a, b) =>
			(a.short ?? '').localeCompare(b.short ?? '')
		);
	}
}

/** For each given reflex, count the sub-nodes hanging off it: borrowed forms sourced from it
 *  (`sub_count`) and its own daughter reflexes (`reflex_sub_count`). Children rowids are already
 *  on the hydrated rows, so one flags lookup covers both counts. */
async function attachSubCounts(lemmas: HLemma[]): Promise<void> {
	if (!lemmas.length) return;
	const allKids = [...new Set(lemmas.flatMap((l) => l.childRids))];
	const flagsOf = new Map<number, number>();
	if (allKids.length) {
		const rows = await query<{ rid: number; flags: number }>(
			`SELECT rowid AS rid, flags FROM lem WHERE rowid IN ${IN_JSON}`,
			[jsonList(allKids)]
		);
		for (const r of rows) flagsOf.set(r.rid, r.flags);
	}
	for (const l of lemmas) {
		let borrowed = 0;
		let reflexes = 0;
		for (const k of l.childRids) {
			const rel = (flagsOf.get(k) ?? 0) & 7;
			if (rel === REL_BORROWED) borrowed++;
			else if (rel === REL_REFLEX) reflexes++;
		}
		l.sub_count = borrowed;
		l.reflex_sub_count = reflexes;
	}
}

/** The borrowed sub-reflexes of a reflex (forms it was the source of), for its page. */
export async function getBorrowedReflexes(reflexId: string): Promise<Lemma[]> {
	const idx = await ensureCore();
	const rid = idx.ridOf(reflexId);
	if (!rid) return [];
	const rows = (await lemmasByRids(await childRidsOf(rid))).filter(
		(l) => l.relation === 'borrowed'
	);
	await attachLanguages(rows);
	return rows;
}

/** Reflexes of one etymon that match a given concept — the inline expansion on the concepts view. */
export async function getConceptReflexes(entryId: string, conceptId: string): Promise<Lemma[]> {
	const idx = await ensureCore();
	const entryRid = idx.ridOf(entryId);
	const blob = await queryOne<{ rids: Uint8Array | null }>(
		'SELECT rids FROM concepts WHERE id = ?',
		[conceptId]
	);
	if (!entryRid || !blob?.rids) return [];
	const linked = readDeltas(blob.rids);
	const rows = await query<RawLem>(
		`${LEM_SELECT} WHERE l.rowid IN ${IN_JSON}
		   AND (l.origin_rid = ? OR (l.origin_rid IS NULL AND l.rowid = ?))
		   AND (l.flags & 7) != ${REL_UNLINKED} AND ${NOT_REDIRECT}
		 ORDER BY l.ord`,
		[jsonList(linked), entryRid, entryRid]
	);
	const out = rows.map(hydrate);
	await attachLanguages(out);
	await attachReferences(out);
	return out;
}

// ---- filter / sort construction (port of search.py) ----------------------

const SORT_COLUMNS: Record<string, string> = {
	lang: 'lang.name',
	word: 'l.word',
	gloss: 'l.gloss',
	notes: 'l.notes',
	origin: 'l.ord',
	clade: 'lang.clade',
	reflexes: 'lang.lemma_count',
	nreflex: '(l.counts / 1024)',
	nlang: '(l.counts % 1024)',
	nderived:
		`(SELECT COUNT(*) FROM edges d JOIN lem c ON c.rowid = d.child_rid WHERE d.parent_rid = l.rowid AND d.kind IN (${KIND_COMPONENT}, ${KIND_DERIVED}) AND d.rank = 1 AND c.origin_rid IS NULL)`
};
// columns whose sort/filter forces the languages join
const NEEDS_LANG_JOIN = new Set(['lang', 'clade', 'reflexes']);

interface Cond {
	sql: string;
	params: unknown[];
}

/** Whole-token tagset match: rows whose interned tag string contains the token. */
function tagCond(token: string): Cond {
	return {
		sql: `l.tagset_rid IN (SELECT rowid FROM tagsets WHERE (' ' || txt || ' ') LIKE ?)`,
		params: [`% ${token} %`]
	};
}

async function lemmaConditions(p: ListParams): Promise<{ conds: Cond[]; needsLangJoin: boolean }> {
	const conds: Cond[] = [];
	let needsLangJoin = false;

	// Case-insensitive substring terms over the base text columns.
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
		if (selected.startsWith('dialect:')) conds.push(tagCond(selected));
		else conds.push({ sql: 'l.lang_rid = ?', params: [langRidOf(selected) ?? -1] });
	}
	if (p.etymon_lang?.trim()) {
		const selected = p.etymon_lang.trim();
		conds.push(
			selected.startsWith('dialect:')
				? {
						sql: `l.origin_rid IN (SELECT rowid FROM lem
						      WHERE tagset_rid IN (SELECT rowid FROM tagsets WHERE (' ' || txt || ' ') LIKE ?))`,
						params: [`% ${selected} %`]
					}
				: { sql: 'l.origin_rid IN (SELECT rowid FROM lem WHERE lang_rid = ?)', params: [langRidOf(selected) ?? -1] }
		);
	}
	if (p.dialect?.trim()) {
		conds.push(tagCond(p.dialect.trim()));
	}
	if ((p.origin ?? '').trim().length >= MIN_SEARCH_CHARS) {
		conds.push({
			sql: `l.origin_rid IN (SELECT rowid FROM lem WHERE instr(lower(COALESCE(word, '')), ?) > 0)`,
			params: [p.origin!.trim().toLocaleLowerCase()]
		});
	}
	if (p.source?.trim()) {
		const needle = p.source.trim().toLowerCase();
		const cids = await citeIdsWhere((r) => (r.short ?? '').toLowerCase().includes(needle));
		conds.push({ sql: 'vin_any(l.cites, ?) = 1', params: [jsonList(cids)] });
	}
	// tags: whole-token match (AND across the selected tags)
	if (p.tags?.trim()) {
		for (const t of p.tags.trim().split(/\s+/)) conds.push(tagCond(t));
	}

	// root nodes only: entries not derived from any other etymon (no incoming derivation edge)
	if (p.rootsOnly) {
		conds.push({
			sql: `NOT EXISTS (SELECT 1 FROM edges WHERE child_rid = l.rowid AND kind IN (${KIND_COMPONENT}, ${KIND_DERIVED}) AND rank = 1)`,
			params: []
		});
	}

	// CDIAL section-forms only (precomputed flag; ids like `<etymon>-<n>`)
	if (p.sectionsOnly) {
		conds.push({ sql: `(l.flags & ${FLAG_SECTION}) != 0`, params: [] });
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
			return `${sqlCol} ${dir === 'desc' ? 'DESC' : 'ASC'}, l.ord`;
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
	conceptId?: string; // restrict to entries expressing this Concepticon concept
	params: ListParams;
	withOrigin?: boolean; // attach origin_lemma (reflexes/lexicon show it)
}

/** Per-entry extras for the entries view: derived-term counts + variant word lists, computed
 *  from the page's rows (the legacy correlated group_concat subqueries can't see blobs). */
async function attachEntryExtras(rows: HLemma[]): Promise<void> {
	if (!rows.length) return;
	const rids = rows.map((r) => r.rid);
	const derived = await query<{ p: number; c: number }>(
		`SELECT d.parent_rid AS p, COUNT(*) AS c FROM edges d
		 JOIN lem c2 ON c2.rowid = d.child_rid
		 WHERE d.parent_rid IN ${IN_JSON} AND d.kind IN (${KIND_COMPONENT}, ${KIND_DERIVED}) AND d.rank = 1
		   AND c2.origin_rid IS NULL GROUP BY d.parent_rid`,
		[jsonList(rids)]
	);
	const dMap = new Map(derived.map((r) => [r.p, r.c]));
	const parentOf = new Map<number, HLemma>();
	for (const r of rows) for (const k of r.childRids) parentOf.set(k, r);
	const allKids = [...parentOf.keys()];
	const variants = allKids.length
		? await query<{ rid: number; word: string; flags: number }>(
				`SELECT rowid AS rid, word, flags FROM lem
				 WHERE rowid IN ${IN_JSON} AND (flags & 7) = ${REL_VARIANT} AND link_rid IS NULL
				 ORDER BY ord`,
				[jsonList(allKids)]
			)
		: [];
	const vf = new Map<number, string[]>();
	const ovf = new Map<number, string[]>();
	for (const v of variants) {
		const parent = parentOf.get(v.rid);
		if (!parent) continue;
		(vf.get(parent.rid) ?? vf.set(parent.rid, []).get(parent.rid)!).push(v.word);
		if (v.flags & FLAG_OCR)
			(ovf.get(parent.rid) ?? ovf.set(parent.rid, []).get(parent.rid)!).push(v.word);
	}
	for (const r of rows) {
		r.derived_count = dMap.get(r.rid) ?? 0;
		r.variant_forms = vf.get(r.rid)?.join('\x1f') ?? null;
		r.ocr_variant_forms = ovf.get(r.rid)?.join('\x1f') ?? null;
	}
}

export async function fetchLemmaList(opts: ListOpts): Promise<ListResult> {
	const { mode, languageId, referenceId, conceptId, params } = opts;
	await ensureCore();
	const page = Math.max(1, params.page ?? 1);
	const { conds, needsLangJoin } = await lemmaConditions(params);

	// base mode condition (see the v1 layer for semantics; redirect stubs are never listed)
	const modeConds: Cond[] = [{ sql: NOT_REDIRECT, params: [] }];
	if (mode === 'entries') {
		if (params.loanSourcesOnly)
			modeConds.push({ sql: `(l.flags & ${FLAG_LOAN_SOURCE}) != 0`, params: [] });
		else modeConds.push({ sql: `l.origin_rid IS NULL AND (l.flags & 7) != ${REL_UNLINKED}`, params: [] });
	}
	if (mode === 'lexicon' && languageId)
		modeConds.push({ sql: 'l.lang_rid = ?', params: [langRidOf(languageId) ?? -1] });
	if (referenceId) {
		const cids = await citeIdsWhere((r) => r.id === referenceId);
		modeConds.push({ sql: 'vin_any(l.cites, ?) = 1', params: [jsonList(cids)] });
	}

	// concept restriction: entries that are the immediate etymon of a form mapped to the concept.
	// The matching entry set is small, so it is resolved in JS (also yielding concept_match).
	let conceptMatch: Map<number, number> | null = null;
	if (conceptId) {
		const blob = await queryOne<{ rids: Uint8Array | null }>(
			'SELECT rids FROM concepts WHERE id = ?',
			[conceptId]
		);
		conceptMatch = new Map();
		const linked = blob?.rids ? readDeltas(blob.rids) : [];
		if (linked.length) {
			const rows = await query<{ rid: number; origin_rid: number | null; flags: number }>(
				`SELECT rowid AS rid, origin_rid, flags FROM lem WHERE rowid IN ${IN_JSON}`,
				[jsonList(linked)]
			);
			for (const r of rows) {
				if ((r.flags & 7) === REL_UNLINKED) continue;
				const entry = r.origin_rid ?? r.rid;
				conceptMatch.set(entry, (conceptMatch.get(entry) ?? 0) + 1);
			}
		}
		modeConds.push({ sql: `l.rowid IN ${IN_JSON}`, params: [jsonList([...conceptMatch.keys()])] });
	}

	const all = [...modeConds, ...conds];
	const whereParams = all.flatMap((c) => c.params);
	const whereSql = all.length ? 'WHERE ' + all.map((c) => c.sql).join(' AND ') : '';
	const join = needsLangJoin ? 'JOIN languages lang ON lang.rowid = l.lang_rid' : '';

	// Fast path 1: entries list with no filters/sort → partial index, no join, no temp sort.
	const isDefaultEntries =
		mode === 'entries' &&
		!referenceId &&
		!conceptId &&
		!needsLangJoin &&
		conds.length === 0 &&
		!params.loanSourcesOnly &&
		!(params.sort ?? '').trim();
	// Fast path 2: per-language lexicon with no filters/sort → the language's `lex` rowid list.
	const isDefaultLexicon =
		mode === 'lexicon' &&
		!!languageId &&
		!referenceId &&
		!conceptId &&
		!needsLangJoin &&
		conds.length === 0 &&
		!(params.sort ?? '').trim();

	const hasFilters = conds.length > 0 || !!params.loanSourcesOnly || !!referenceId || !!conceptId;
	let count: number;
	if (!hasFilters && mode === 'entries') {
		count = await metaCount('total_entries');
	} else if (!hasFilters && mode === 'reflexes') {
		count = await metaCount('total_lexicon');
	} else if (!hasFilters && mode === 'lexicon' && languageId) {
		const r = await queryOne<{ c: number }>('SELECT lemma_count AS c FROM languages WHERE id = ?', [
			languageId
		]);
		count = r?.c ?? 0;
	} else if (conceptId) {
		count = -1; // resolved below from the full matching set
	} else {
		const countRow = await queryOne<{ c: number }>(
			`SELECT COUNT(*) AS c FROM lem l ${join} ${whereSql}`,
			whereParams
		);
		count = countRow?.c ?? 0;
	}

	const offset = (page - 1) * PAGE_SIZE;
	const fallbackOrder = 'l.ord';
	const order = orderBy(params, fallbackOrder);

	let rows: HLemma[];
	if (isDefaultLexicon) {
		const lex = await queryOne<{ lex: Uint8Array | null }>(
			'SELECT lex FROM languages WHERE id = ?',
			[languageId]
		);
		const rids = readVarints(lex?.lex);
		rows = await lemmasByRids(rids.slice(offset, offset + PAGE_SIZE));
	} else if (isDefaultEntries) {
		const raw = await query<RawLem>(
			`SELECT ${LEM_COLS} FROM lem l INDEXED BY idx_entries_ord ${LEM_JOINS}
			 WHERE l.origin_rid IS NULL AND (l.flags & 7) != ${REL_UNLINKED} AND l.link_rid IS NULL
			 ORDER BY l.ord LIMIT ${PAGE_SIZE} OFFSET ${offset}`
		);
		rows = raw.map(hydrate);
	} else if (conceptId && conceptMatch) {
		// bounded set: fetch all matches, order + paginate here so concept_match can sort
		const raw = await query<RawLem>(
			`${LEM_SELECT} ${join} ${whereSql} ORDER BY ${order}`,
			whereParams
		);
		let full = raw.map(hydrate);
		for (const r of full) r.concept_match = conceptMatch.get(r.rid) ?? 0;
		if (!(params.sort ?? '').trim())
			full = full.sort((a, b) => (b.concept_match! - a.concept_match!) || a.order - b.order);
		count = full.length;
		rows = full.slice(offset, offset + PAGE_SIZE);
	} else {
		const raw = await query<RawLem>(
			`${LEM_SELECT} ${join} ${whereSql} ORDER BY ${order} LIMIT ${PAGE_SIZE} OFFSET ${offset}`,
			whereParams
		);
		rows = raw.map(hydrate);
	}

	await attachLanguages(rows);
	if (opts.withOrigin) await attachOrigin(rows);
	await attachReferences(rows);
	if (mode !== 'entries') await attachSubCounts(rows);
	if (mode === 'entries') await attachEntryExtras(rows);

	return { rows, count, page };
}

// ---- single-record lookups ------------------------------------------------

const aliasGroupCache = new Map<string, Uint8Array | null>();

/** Resolve a public id to its lem rowid, following legacy-id aliases first (they shadow). */
async function canonicalRid(id: string): Promise<number | null> {
	const idx = await ensureCore();
	const key = aliasGroupKey(id);
	if (key) {
		if (!aliasGroupCache.has(key.prefix)) {
			const g = await queryOne<{ data: Uint8Array }>('SELECT data FROM aliases WHERE prefix = ?', [
				key.prefix
			]);
			aliasGroupCache.set(key.prefix, g?.data ?? null);
		}
		const g = aliasGroupCache.get(key.prefix);
		if (g) {
			const rid = aliasLookup(g, key.m);
			if (rid != null) return rid;
		}
	}
	const miscAlias = await queryOne<{ lemma_rid: number }>(
		'SELECT lemma_rid FROM aliases_misc WHERE alias = ?',
		[id]
	);
	if (miscAlias) return miscAlias.lemma_rid;
	return idx.ridOf(id);
}

export async function getLemma(id: string): Promise<Lemma | null> {
	const rid = await canonicalRid(id);
	if (!rid) return null;
	const [l] = await lemmasByRids([rid]);
	if (!l) return null;
	await attachLanguages([l]);
	await attachOrigin([l]);
	await attachReferences([l]);
	return l;
}

export interface EntryGraph {
	ancestors: { id: string; word: string }[];
	derived: { id: string; word: string; gloss: string; reflex_count: number; lang_count: number }[];
}

/** Client-side counterpart of the prerender query, used when a reflex entry was not emitted as HTML. */
export async function getEntryGraph(id: string): Promise<EntryGraph> {
	const idx = await ensureCore();
	const rid = await canonicalRid(id);
	if (!rid) return { ancestors: [], derived: [] };
	const [ancestors, derived] = await Promise.all([
		query<{ rid: number; word: string }>(
			`SELECT l.rowid AS rid, l.word FROM edges d JOIN lem l ON l.rowid = d.parent_rid
			 WHERE d.child_rid = ? AND d.kind IN (${KIND_COMPONENT}, ${KIND_DERIVED}) AND d.rank = 1
			 ORDER BY COALESCE(d.pos, 0), d.rowid`,
			[rid]
		),
		query<{ rid: number; word: string; gloss: string; counts: number | null }>(
			`SELECT l.rowid AS rid, l.word, l.gloss, l.counts
			 FROM edges d JOIN lem l ON l.rowid = d.child_rid
			 WHERE d.parent_rid = ? AND d.kind IN (${KIND_COMPONENT}, ${KIND_DERIVED}) AND d.rank = 1
			   AND l.origin_rid IS NULL ORDER BY l.ord`,
			[rid]
		)
	]);
	return {
		ancestors: ancestors.map((r) => ({ id: idx.idOf(r.rid), word: r.word })),
		derived: derived.map((r) => ({
			id: idx.idOf(r.rid),
			word: r.word,
			gloss: r.gloss,
			reflex_count: r.counts != null ? r.counts >> 10 : 0,
			lang_count: r.counts != null ? r.counts % 1024 : 0
		}))
	};
}

export interface AncestorRef {
	id: string;
	word: string;
	lang?: string | null;
	kind: 'entry' | 'reflex'; // link target: /entries/ vs /reflexes/
	ocr: boolean;
}

/** Walk up the etymology graph from a node, level by level, nearest first. */
export async function getAncestryChain(startId: string): Promise<AncestorRef[][]> {
	const idx = await ensureCore();
	const startRid = idx.ridOf(startId);
	if (!startRid) return [];
	const levels: AncestorRef[][] = [];
	const seen = new Set<number>([startRid]);
	let frontier = [startRid];
	for (let depth = 0; depth < 16 && frontier.length; depth++) {
		// one step up: the rank-1 attestation edge target (uniform for all kinds), plus
		// rank-1 component/derived parents; rank>=2 alternates stay out of the chain and are
		// surfaced at the node via getAlternates instead
		const viaOrigin = await query<{ pid: number }>(
			`SELECT origin_rid AS pid FROM lem WHERE rowid IN ${IN_JSON} AND origin_rid IS NOT NULL`,
			[jsonList(frontier)]
		);
		const viaDeriv = await query<{ pid: number }>(
			`SELECT parent_rid AS pid FROM edges
			 WHERE child_rid IN ${IN_JSON} AND kind IN (${KIND_COMPONENT}, ${KIND_DERIVED}) AND rank = 1`,
			[jsonList(frontier)]
		);
		const pids = [...new Set([...viaOrigin, ...viaDeriv].map((r) => r.pid))].filter(
			(p) => p && !seen.has(p)
		);
		if (!pids.length) break;
		pids.forEach((p) => seen.add(p));
		const rows = await query<{
			rid: number;
			word: string;
			lang_rid: number | null;
			olid: number | null;
			flags: number;
		}>(
			`SELECT rowid AS rid, word, lang_rid, origin_rid AS olid, flags FROM lem WHERE rowid IN ${IN_JSON}`,
			[jsonList(pids)]
		);
		levels.push(
			rows.map((r) => ({
				id: idx.idOf(r.rid),
				word: r.word,
				lang: r.lang_rid != null ? langByRid(r.lang_rid)?.name : null,
				kind: r.olid ? ('reflex' as const) : ('entry' as const),
				ocr: !!(r.flags & FLAG_OCR)
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
	ocr?: boolean | number;
}

/** The derived-term subtree of an entry (breadth-first, deduped, bounded). */
export async function getDerivedTree(rootId: string, maxNodes = 800): Promise<DerivedNode[]> {
	const idx = await ensureCore();
	const rootRid = idx.ridOf(rootId);
	if (!rootRid) return [];
	const childrenOf = new Map<number, number[]>();
	const seen = new Set<number>([rootRid]);
	let frontier = [rootRid];
	let total = 0;
	for (let depth = 0; depth < 12 && frontier.length && total < maxNodes; depth++) {
		const edges = await query<{ p: number; c: number }>(
			`SELECT d.parent_rid AS p, d.child_rid AS c FROM edges d
			 JOIN lem l ON l.rowid = d.child_rid
			 WHERE d.parent_rid IN ${IN_JSON} AND d.kind IN (${KIND_COMPONENT}, ${KIND_DERIVED}) AND d.rank = 1
			   AND l.origin_rid IS NULL
			 ORDER BY d.child_rid`,
			[jsonList(frontier)]
		);
		const next: number[] = [];
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
	const nodeRids = [...seen].filter((r) => r !== rootRid);
	const rows = nodeRids.length
		? await query<{ rid: number; word: string; gloss: string; counts: number | null; ord: number; flags: number }>(
				`SELECT rowid AS rid, word, gloss, counts, ord, flags FROM lem WHERE rowid IN ${IN_JSON}`,
				[jsonList(nodeRids)]
			)
		: [];
	const info = new Map(
		rows.map((r) => [
			r.rid,
			{
				id: idx.idOf(r.rid),
				word: r.word,
				gloss: r.gloss,
				reflex_count: r.counts != null ? r.counts >> 10 : undefined,
				lang_count: r.counts != null ? r.counts % 1024 : undefined,
				ocr: !!(r.flags & FLAG_OCR)
			}
		])
	);
	const orderOf = new Map(rows.map((r) => [r.rid, r.ord]));
	const build = (rid: number): DerivedNode => {
		const r = info.get(rid)!;
		const kids = (childrenOf.get(rid) ?? []).sort(
			(a, b) => (orderOf.get(a) ?? 0) - (orderOf.get(b) ?? 0)
		);
		return { ...r, children: kids.map(build) };
	};
	return (childrenOf.get(rootRid) ?? [])
		.sort((a, b) => (orderOf.get(a) ?? 0) - (orderOf.get(b) ?? 0))
		.map(build);
}

/** Comma-listed alternates of a reflex (its reflex-variants), for the reflex page. */
export async function getReflexVariants(reflexId: string): Promise<Lemma[]> {
	const idx = await ensureCore();
	const rid = idx.ridOf(reflexId);
	if (!rid) return [];
	const kids = await childRidsOf(rid);
	if (!kids.length) return [];
	const rows = await query<RawLem>(
		`${LEM_SELECT} WHERE l.rowid IN ${IN_JSON} AND (l.flags & 7) = ${REL_VARIANT} ORDER BY l.ord`,
		[jsonList(kids)]
	);
	const vs = rows.map(hydrate);
	await attachLanguages(vs);
	await attachReferences(vs);
	return vs;
}

export async function getLanguage(id: string): Promise<Language | null> {
	return queryOne<Language>(`SELECT ${LANGUAGE_COLS} FROM languages WHERE id = ?`, [id]);
}

/** Structured tags attested by at least one row in a language. */
export async function getLanguageTags(languageId: string): Promise<string[]> {
	await ensureCore();
	const rows = await query<{ txt: string }>(
		`SELECT DISTINCT ts.txt AS txt FROM lem l JOIN tagsets ts ON ts.rowid = l.tagset_rid
		 WHERE l.lang_rid = ?`,
		[langRidOf(languageId) ?? -1]
	);
	return [...new Set(rows.flatMap((r) => r.txt.split(/\s+/).filter(Boolean)))];
}

/** Every structured tag in the corpus with its row count — for the (auto-built) tag filter. */
export async function getAllTags(): Promise<{ tag: string; count: number }[]> {
	const rows = await query<{ tags: string; c: number }>(
		`SELECT ts.txt AS tags, COUNT(*) AS c FROM lem l JOIN tagsets ts ON ts.rowid = l.tagset_rid
		 GROUP BY l.tagset_rid`
	);
	const counts = new Map<string, number>();
	for (const r of rows)
		for (const t of r.tags.split(/\s+/).filter(Boolean)) counts.set(t, (counts.get(t) ?? 0) + r.c);
	return [...counts.entries()]
		.map(([tag, count]) => ({ tag, count }))
		.sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));
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

/** For one language, the distribution of its reflexes across the references that cite them. */
export async function getReferenceDistribution(languageId: string): Promise<OriginSlice[]> {
	await ensureCore();
	await ensureCites();
	const rows = await query<{ cites: Uint8Array }>(
		'SELECT cites FROM lem WHERE lang_rid = ? AND cites IS NOT NULL',
		[langRidOf(languageId) ?? -1]
	);
	const perRef = new Map<number, number>(); // ref rowid → cited-lemma count
	for (const r of rows) {
		const refs = new Set<number>();
		for (const cid of readVarints(r.cites)) {
			const c = citesCache!.get(cid);
			if (c) refs.add(c.ref);
		}
		for (const ref of refs) perRef.set(ref, (perRef.get(ref) ?? 0) + 1);
	}
	return [...perRef.entries()]
		.map(([refRid, c]) => {
			const ref = referencesByRid!.get(refRid);
			const short = ref?.short || ref?.id || String(refRid);
			return { lang: ref?.id ?? String(refRid), name: short, clade: null, count: c, color: refColor(short) };
		})
		.sort((a, b) => b.count - a.count);
}

/** For one language, the distribution of its reflexes by the language of their immediate origin. */
export async function getOriginLangDistribution(languageId: string): Promise<OriginSlice[]> {
	await ensureCore();
	const rows = await query<{ lrid: number; c: number }>(
		`SELECT o.lang_rid AS lrid, COUNT(*) AS c
		 FROM lem r JOIN lem o ON o.rowid = r.origin_rid
		 WHERE r.lang_rid = ? AND (r.flags & 7) IN (${REL_REFLEX}, ${REL_BORROWED})
		 GROUP BY o.lang_rid ORDER BY c DESC`,
		[langRidOf(languageId) ?? -1]
	);
	const slices: OriginSlice[] = rows.map((r) => {
		const l = langByRid(r.lrid);
		return { lang: l?.id ?? String(r.lrid), name: l?.name ?? String(r.lrid), clade: l?.clade ?? null, count: r.c };
	});
	const un = await queryOne<{ c: number }>(
		`SELECT COUNT(*) AS c FROM lem WHERE lang_rid = ? AND (flags & 7) = ${REL_UNLINKED}`,
		[langRidOf(languageId) ?? -1]
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
	await ensureCore();
	const cids = await citeIdsWhere((r) => r.id === referenceId);
	const rows = await query<{ lrid: number; c: number }>(
		`SELECT l.lang_rid AS lrid, COUNT(*) AS c FROM lem l
		 WHERE vin_any(l.cites, ?) = 1 GROUP BY l.lang_rid`,
		[jsonList(cids)]
	);
	return rows
		.map((r) => {
			const l = langByRid(r.lrid);
			return { lang: l?.id ?? String(r.lrid), name: l?.name ?? String(r.lrid), clade: l?.clade ?? null, count: r.c };
		})
		.sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
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

/** Variant forms of a node = its variant-kind children (in v3 a variant's edge points at its
 *  true target, so head variants of an entry and alternates of a reflex are one shape). */
export async function getEntryVariants(entryId: string): Promise<Lemma[]> {
	const idx = await ensureCore();
	const rid = idx.ridOf(entryId);
	if (!rid) return [];
	const kids = await childRidsOf(rid);
	if (!kids.length) return [];
	const rows = await query<RawLem>(
		`${LEM_SELECT} WHERE l.rowid IN ${IN_JSON} AND (l.flags & 7) = ${REL_VARIANT}
		 ORDER BY l.ord`,
		[jsonList(kids)]
	);
	const variants = rows.map(hydrate);
	await attachLanguages(variants);
	await attachReferences(variants);
	return variants;
}

/** The reflexes of an entry: its rank-1 children plus SECONDARY reflexes — forms whose accepted
 *  etymon is elsewhere but which carry a rank>=2 alternate-etymology edge into this entry. */
async function entryChildRows(entryRid: number, relations: number[]): Promise<HLemma[]> {
	const kids = await childRidsOf(entryRid);
	const relList = relations.join(', ');
	const rows = await query<RawLem & { secondary: number }>(
		`SELECT ${LEM_COLS}, 0 AS secondary FROM lem l ${LEM_JOINS}
		   WHERE l.rowid IN ${IN_JSON} AND (l.flags & 7) IN (${relList})
		 UNION ALL
		 SELECT ${LEM_COLS}, 1 AS secondary FROM lem l ${LEM_JOINS}
		   WHERE l.origin_rid IS NOT NULL AND (l.flags & 7) IN (${relList})
		     AND l.rowid IN (SELECT child_rid FROM edges WHERE parent_rid = ? AND rank >= 2)
		 ORDER BY l.ord`,
		[jsonList(kids), entryRid]
	);
	return rows.map(hydrate);
}

export async function getEntryReflexes(entryId: string): Promise<EntryReflexes> {
	const idx = await ensureCore();
	const entryRid = idx.ridOf(entryId);
	if (!entryRid) return { groups: [], langGroups: [], total: 0 };
	const reflexes = await entryChildRows(entryRid, [REL_REFLEX, REL_BORROWED]);
	await attachLanguages(reflexes);
	await attachReferences(reflexes);
	await attachSubCounts(reflexes);
	const total = reflexes.length;

	// group by cognateset, then by language (mirrors app.py:336-381)
	const byCog = new Map<string | null, Lemma[]>();
	for (const r of reflexes) {
		const key = r.cognateset || null;
		const arr = byCog.get(key);
		if (arr) arr.push(r);
		else byCog.set(key, [r]);
	}
	const groups: CognateGroup[] = [];
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

// alignment metadata caches (symbols / pairs / contexts / the cell dictionary)
interface AlignMeta {
	symbol: Map<number, string>;
	symbolIdOf: Map<string, number>;
	pair: Map<number, { e: number; r: number; c: number }>;
	context: Map<number, { p: number; n: number }>;
	cells: { pairId: number; ctxId: number }[];
}
let alignMeta: AlignMeta | null = null;
let alignMetaPromise: Promise<AlignMeta> | null = null;

async function ensureAlignMeta(): Promise<AlignMeta> {
	if (alignMeta) return alignMeta;
	if (!alignMetaPromise) {
		alignMetaPromise = (async () => {
			const [symbols, pairs, contexts, cellsRow] = await Promise.all([
				query<{ id: number; value: string }>('SELECT id, value FROM symbols'),
				query<{ id: number; etymon_sid: number; reflex_sid: number; change_sid: number }>(
					'SELECT id, etymon_sid, reflex_sid, change_sid FROM align_pair'
				),
				query<{ id: number; prev_sid: number; next_sid: number }>(
					'SELECT id, prev_sid, next_sid FROM align_context'
				),
				queryOne<{ data: Uint8Array }>('SELECT data FROM cells')
			]);
			alignMeta = {
				symbol: new Map(symbols.map((s) => [s.id, s.value])),
				symbolIdOf: new Map(symbols.map((s) => [s.value, s.id])),
				pair: new Map(pairs.map((p) => [p.id, { e: p.etymon_sid, r: p.reflex_sid, c: p.change_sid }])),
				context: new Map(contexts.map((c) => [c.id, { p: c.prev_sid, n: c.next_sid }])),
				cells: cellsRow ? readCellDict(cellsRow.data) : []
			};
			return alignMeta;
		})();
	}
	return alignMetaPromise;
}

/** Decode one form's segs blob into AlignSeg[] (etymonIdx = running non-gap count). */
function decodeSegs(meta: AlignMeta, blob: Uint8Array | null): AlignSeg[] {
	const cellIds = readVarints(blob);
	const out: AlignSeg[] = [];
	let idxCount = 0;
	for (let pos = 0; pos < cellIds.length; pos++) {
		const cell = meta.cells[cellIds[pos] - 1];
		const pair = meta.pair.get(cell.pairId)!;
		const etymonSeg = meta.symbol.get(pair.e) ?? '';
		let etymonIdx = -1;
		if (etymonSeg !== '') {
			etymonIdx = idxCount;
			idxCount++;
		}
		out.push({
			pos,
			etymonIdx,
			etymonSeg,
			reflexSeg: meta.symbol.get(pair.r) ?? '',
			change: meta.symbol.get(pair.c) ?? ''
		});
	}
	return out;
}

export async function getEntryAlignment(entryId: string): Promise<EntryAlignment> {
	const idx = await ensureCore();
	const meta = await ensureAlignMeta();
	const entryRid = idx.ridOf(entryId);
	if (!entryRid) return { etymon: [], reflexes: [] };
	const reflexes = await entryChildRows(entryRid, [REL_REFLEX, REL_BORROWED]);
	await attachLanguages(reflexes);
	await attachReferences(reflexes);
	await attachSubCounts(reflexes);

	// attach each main reflex's comma-listed alternates: its own variant-kind children
	const reflexKids = [...new Set(reflexes.flatMap((r) => r.childRids))];
	const rvarRows = reflexKids.length
		? await query<RawLem>(
				`${LEM_SELECT} WHERE l.rowid IN ${IN_JSON} AND (l.flags & 7) = ${REL_VARIANT}
				 ORDER BY l.ord`,
				[jsonList(reflexKids)]
			)
		: [];
	const rvars = rvarRows.map(hydrate);
	await attachReferences(rvars);
	const byMain = new Map<string, Lemma[]>();
	for (const v of rvars) {
		const arr = byMain.get(v.variant_of!);
		if (arr) arr.push(v);
		else byMain.set(v.variant_of!, [v]);
	}
	for (const r of reflexes) r.variants = byMain.get(r.id) ?? [];

	// alignment blobs for all shown reflexes
	const rids = reflexes.map((r) => r.rid);
	const blobs = rids.length
		? await query<{ form_rid: number; segs: Uint8Array }>(
				`SELECT form_rid, segs FROM alignment WHERE form_rid IN ${IN_JSON}`,
				[jsonList(rids)]
			)
		: [];
	const segsByRid = new Map(blobs.map((b) => [b.form_rid, decodeSegs(meta, b.segs)]));
	const etymonMap = new Map<number, string>();
	for (const segs of segsByRid.values()) {
		for (const s of segs) if (s.etymonIdx >= 0 && !etymonMap.has(s.etymonIdx)) etymonMap.set(s.etymonIdx, s.etymonSeg);
	}
	const etymon = [...etymonMap.entries()]
		.sort((a, b) => a[0] - b[0])
		.map(([i, seg]) => ({ idx: i, seg }));
	const aligned = reflexes.map((l) => ({ lemma: l as Lemma, segs: segsByRid.get(l.rid) ?? [] }));
	return { etymon, reflexes: aligned };
}

/** The materialised alignment (etymon→reflex sound-change steps) for a single reflex. */
export async function getReflexAlignment(formId: string): Promise<AlignSeg[]> {
	const idx = await ensureCore();
	const meta = await ensureAlignMeta();
	const rid = idx.ridOf(formId);
	if (!rid) return [];
	const row = await queryOne<{ segs: Uint8Array }>(
		'SELECT segs FROM alignment WHERE form_rid = ?',
		[rid]
	);
	return row ? decodeSegs(meta, row.segs) : [];
}

export interface AlternateEtymon {
	id: string; // proposed parent id
	word: string;
	gloss: string;
	kind: string; // reflex | borrowed | variant
	rank: number;
	note: string | null; // review marker or source attribution
	lang?: string | null;
	isEntry: boolean; // link to /entries vs /reflexes
}

/** Rank>=2 alternate-etymology hypotheses of one node ("also proposed: from X"). */
export async function getAlternates(id: string): Promise<AlternateEtymon[]> {
	const idx = await ensureCore();
	const rid = idx.ridOf(id);
	if (!rid) return [];
	const rows = await query<{
		prid: number;
		kind: number;
		rank: number;
		note: string | null;
		word: string;
		gloss: string;
		lang_rid: number | null;
		origin_rid: number | null;
	}>(
		`SELECT e.parent_rid AS prid, e.kind AS kind, e.rank AS rank, e.note AS note,
		        l.word, l.gloss, l.lang_rid, l.origin_rid
		 FROM edges e JOIN lem l ON l.rowid = e.parent_rid
		 WHERE e.child_rid = ? AND e.rank >= 2 ORDER BY e.rank, e.rowid`,
		[rid]
	);
	const KINDS: Record<number, string> = { 1: 'reflex', 2: 'variant', 3: 'borrowed', 5: 'component', 6: 'derived' };
	return rows.map((r) => ({
		id: idx.idOf(r.prid),
		word: r.word,
		gloss: r.gloss,
		kind: KINDS[r.kind] ?? String(r.kind),
		rank: r.rank,
		note: r.note,
		lang: r.lang_rid != null ? langByRid(r.lang_rid)?.name : null,
		isEntry: r.origin_rid == null
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
/** A clade-level, environment-conditioned correspondence cell. */
export interface CorrCtx {
	clade: string;
	prev: string;
	next: string;
	reflexSeg: string;
	change: string;
	n: number;
	example: string;
}
/** A language-level correspondence cell (for branch expansion). */
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
	ocr: boolean | number;
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

/** Fetch + decode the corr_lang2 groups for one (proto, segment). */
async function corrGroups(
	proto: string,
	seg: string
): Promise<{ langRid: number; cells: { cellId: number; n: number; exampleRid: number }[] }[]> {
	await ensureCore();
	const meta = await ensureAlignMeta();
	const sid = meta.symbolIdOf.get(seg);
	const protoRid = langRidOf(proto);
	if (sid == null || protoRid == null) return [];
	const rows = await query<{ lang_rid: number; data: Uint8Array }>(
		'SELECT lang_rid, data FROM corr_lang2 WHERE proto_rid = ? AND etymon_sid = ?',
		[protoRid, sid]
	);
	return rows.map((r) => ({ langRid: r.lang_rid, cells: readCorrCells(r.data) }));
}

/** All clade-level context rows for one proto-segment — the clade rollup formerly precomputed
 *  in `corr`, aggregated here from corr_lang2 (identical cells: n summed, example = min id). */
export async function getSegRows(proto: string, seg: string): Promise<CorrCtx[]> {
	const idx = await ensureCore();
	const meta = await ensureAlignMeta();
	const groups = await corrGroups(proto, seg);
	const agg = new Map<string, { clade: string; cellId: number; n: number; example: string }>();
	for (const g of groups) {
		const clade = langByRid(g.langRid)?.clade ?? '';
		for (const c of g.cells) {
			const key = `${clade}|${c.cellId}`;
			const example = idx.idOf(c.exampleRid);
			const cur = agg.get(key);
			if (!cur) agg.set(key, { clade, cellId: c.cellId, n: c.n, example });
			else {
				cur.n += c.n;
				if (example < cur.example) cur.example = example;
			}
		}
	}
	return [...agg.values()].map((a) => {
		const cell = meta.cells[a.cellId - 1];
		const pair = meta.pair.get(cell.pairId)!;
		const ctx = meta.context.get(cell.ctxId)!;
		return {
			clade: a.clade,
			prev: meta.symbol.get(ctx.p) ?? '',
			next: meta.symbol.get(ctx.n) ?? '',
			reflexSeg: meta.symbol.get(pair.r) ?? '',
			change: meta.symbol.get(pair.c) ?? '',
			n: a.n,
			example: a.example
		};
	});
}

/** Per-language context rows for one clade (loaded when a branch is expanded). */
export async function getCladeLangRows(
	proto: string,
	seg: string,
	clade: string
): Promise<LangCtx[]> {
	const idx = await ensureCore();
	const meta = await ensureAlignMeta();
	const groups = await corrGroups(proto, seg);
	const out: LangCtx[] = [];
	for (const g of groups) {
		const lang = langByRid(g.langRid);
		if (!lang || lang.clade !== clade) continue;
		for (const c of g.cells) {
			const cell = meta.cells[c.cellId - 1];
			const pair = meta.pair.get(cell.pairId)!;
			const ctx = meta.context.get(cell.ctxId)!;
			out.push({
				lang: lang.id,
				langName: lang.name,
				clade,
				prev: meta.symbol.get(ctx.p) ?? '',
				next: meta.symbol.get(ctx.n) ?? '',
				reflexSeg: meta.symbol.get(pair.r) ?? '',
				change: meta.symbol.get(pair.c) ?? '',
				n: c.n,
				example: idx.idOf(c.exampleRid)
			});
		}
	}
	return out;
}

/** True match count for a correspondence query, from the compact summary blobs. */
async function corrLangTotal(q: CorrQuery): Promise<number> {
	const meta = await ensureAlignMeta();
	const groups = await corrGroups(q.proto, q.seg);
	const rSid = meta.symbolIdOf.get(q.reflexSeg);
	const pSid = q.prev ? meta.symbolIdOf.get(q.prev) : null;
	const nSid = q.next ? meta.symbolIdOf.get(q.next) : null;
	let total = 0;
	for (const g of groups) {
		const lang = langByRid(g.langRid);
		if (q.clade && lang?.clade !== q.clade) continue;
		if (q.lang && lang?.id !== q.lang) continue;
		for (const c of g.cells) {
			const cell = meta.cells[c.cellId - 1];
			const pair = meta.pair.get(cell.pairId)!;
			if (pair.r !== rSid) continue;
			const ctx = meta.context.get(cell.ctxId)!;
			if (pSid != null && ctx.p !== pSid) continue;
			if (nSid != null && ctx.n !== nSid) continue;
			total += c.n;
		}
	}
	return total;
}

/** Every reflex exhibiting a given correspondence, for the drill-down page. Candidate cells are
 *  resolved in JS from the cell dictionary; matching forms come from a vin_any() scan of the
 *  per-form alignment blobs, then each matching position becomes one row. */
export async function getCorrespondenceReflexes(
	q: CorrQuery,
	limit = 300
): Promise<CorrReflexResult> {
	const idx = await ensureCore();
	const meta = await ensureAlignMeta();
	const eSid = meta.symbolIdOf.get(q.seg);
	const rSid = meta.symbolIdOf.get(q.reflexSeg);
	const protoRid = langRidOf(q.proto);
	if (eSid == null || rSid == null || protoRid == null)
		return { rows: [], total: 0, truncated: false };
	const pSid = q.prev ? meta.symbolIdOf.get(q.prev) : null;
	const nSid = q.next ? meta.symbolIdOf.get(q.next) : null;
	const candidates = new Set<number>();
	for (let cellId = 1; cellId <= meta.cells.length; cellId++) {
		const cell = meta.cells[cellId - 1];
		const pair = meta.pair.get(cell.pairId)!;
		if (pair.e !== eSid || pair.r !== rSid) continue;
		const ctx = meta.context.get(cell.ctxId)!;
		if (pSid != null && ctx.p !== pSid) continue;
		if (nSid != null && ctx.n !== nSid) continue;
		candidates.add(cellId);
	}
	if (!candidates.size) return { rows: [], total: 0, truncated: false };

	const conds = ['vin_any(a.segs, ?) = 1', 'e.lang_rid = ?'];
	const params: unknown[] = [jsonList([...candidates]), protoRid];
	if (q.clade) {
		conds.push('rl.clade = ?');
		params.push(q.clade);
	}
	if (q.lang) {
		conds.push('rl.id = ?');
		params.push(q.lang);
	}
	const forms = await query<{
		rid: number;
		word: string;
		gloss: string;
		phonemic: string;
		flags: number;
		lang: string;
		langName: string;
		language: string;
		dialect: string;
		color: string;
		origin_rid: number;
		segs: Uint8Array;
	}>(
		`SELECT rf.rowid AS rid, rf.word, rf.gloss, rf.phonemic, rf.flags,
		        rl.id AS lang, COALESCE(rl.name, rl.id) AS langName,
		        rl.language AS language, rl.dialect AS dialect, rl.color AS color,
		        rf.origin_rid AS origin_rid, a.segs AS segs
		 FROM alignment a
		 JOIN lem rf ON rf.rowid = a.form_rid
		 JOIN lem e ON e.rowid = rf.origin_rid
		 JOIN languages rl ON rl.rowid = rf.lang_rid
		 WHERE ${conds.join(' AND ')}
		 ORDER BY rl."order", rl.id, rf.ord
		 LIMIT ?`,
		[...params, limit]
	);
	const rows: CorrReflex[] = [];
	for (const f of forms) {
		for (const cellId of readVarints(f.segs)) {
			if (!candidates.has(cellId)) continue;
			const cell = meta.cells[cellId - 1];
			const pair = meta.pair.get(cell.pairId)!;
			const ctx = meta.context.get(cell.ctxId)!;
			rows.push({
				id: idx.idOf(f.rid),
				word: f.word,
				gloss: f.gloss,
				phonemic: f.phonemic,
				ocr: f.flags & FLAG_OCR ? 1 : 0,
				lang: f.lang,
				langName: f.langName,
				language: f.language,
				dialect: f.dialect,
				color: f.color,
				change: meta.symbol.get(pair.c) ?? '',
				prev: meta.symbol.get(ctx.p) ?? '',
				next: meta.symbol.get(ctx.n) ?? '',
				entryId: f.origin_rid ? idx.idOf(f.origin_rid) : null
			});
		}
	}
	let total = rows.length;
	if (forms.length >= limit) total = await corrLangTotal(q);
	return { rows, total, truncated: rows.length < total };
}

// ---- compare two languages ------------------------------------------------

export interface CompareRow {
	entryId: string;
	entryWord: string;
	entryOcr: boolean | number;
	left: Lemma[];
	right: Lemma[];
}

export async function compareLanguages(
	id1: string,
	id2: string
): Promise<{ lang1: Language | null; lang2: Language | null; rows: CompareRow[] }> {
	const idx = await ensureCore();
	const [lang1, lang2] = await Promise.all([getLanguage(id1), getLanguage(id2)]);
	const load = async (lid: string) => {
		const rows = await query<{
			rid: number;
			word: string;
			gloss: string;
			phonemic: string;
			ord: number;
			lang_rid: number;
			origin_rid: number;
			flags: number;
		}>(
			`SELECT rowid AS rid, word, gloss, phonemic, ord, lang_rid, origin_rid, flags
			 FROM lem WHERE lang_rid = ? AND origin_rid IS NOT NULL ORDER BY ord`,
			[langRidOf(lid) ?? -1]
		);
		return rows.map(
			(r) =>
				({
					id: idx.idOf(r.rid),
					word: r.word,
					gloss: r.gloss,
					phonemic: r.phonemic,
					order: r.ord,
					language_id: langByRid(r.lang_rid)?.id ?? '',
					origin_lemma_id: idx.idOf(r.origin_rid),
					ocr: r.flags & FLAG_OCR ? 1 : 0
				}) as Lemma
		);
	};
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

	const headRids = shared.map((k) => idx.ridOf(k)).filter((r): r is number => r != null);
	const heads = headRids.length
		? await query<{ rid: number; word: string; flags: number }>(
				`SELECT rowid AS rid, word, flags FROM lem WHERE rowid IN ${IN_JSON}`,
				[jsonList(headRids)]
			)
		: [];
	const headMap = new Map(heads.map((h) => [idx.idOf(h.rid), h]));

	const rows: CompareRow[] = shared
		.map((k) => ({
			entryId: k,
			entryWord: headMap.get(k)?.word ?? k,
			entryOcr: (headMap.get(k)?.flags ?? 0) & FLAG_OCR ? 1 : 0,
			left: d1.get(k)!,
			right: d2.get(k)!
		}))
		.sort((a, b) => a.entryId.localeCompare(b.entryId, undefined, { numeric: true }));

	return { lang1, lang2, rows };
}

export { CLADE_ORDER };

// Languages that actually carry rows in a given list view — for the Language column's dropdown.
const filterLangsCache = new Map<string, Language[]>();
export async function getFilterLanguages(mode: 'entries' | 'reflexes'): Promise<Language[]> {
	if (filterLangsCache.has(mode)) return filterLangsCache.get(mode)!;
	await ensureCore();
	// entries → languages with an etymon OR a loan-source reflex; reflexes → every language.
	const where =
		mode === 'entries'
			? `WHERE (origin_rid IS NULL AND (flags & 7) != ${REL_UNLINKED}) OR (flags & ${FLAG_LOAN_SOURCE}) != 0`
			: '';
	const rows = await query<{ lang_rid: number }>(`SELECT DISTINCT lang_rid FROM lem ${where}`);
	const out = rows
		.map((r) => langByRid(r.lang_rid))
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
	await ensureCore();
	const rows = await query<{ entry: number; lrid: number }>(
		`SELECT DISTINCT l.origin_rid AS entry, l.lang_rid AS lrid
		 FROM lem l JOIN languages lang ON lang.rowid = l.lang_rid
		 WHERE (l.flags & 7) = ${REL_REFLEX} AND lang.clade IS NOT NULL AND lang.clade != ''
		   AND l.origin_rid IN (SELECT rowid FROM lem WHERE origin_rid IS NULL AND lang_rid = ?)`,
		[langRidOf(family) ?? -1]
	);
	const cladeByEntry = new Map<number, Set<string>>();
	const langByEntry = new Map<number, Set<string>>();
	const langName: Record<string, string> = {};
	const langClade: Record<string, string> = {};
	for (const r of rows) {
		const lang = langByRid(r.lrid);
		if (!lang?.clade) continue;
		let cs = cladeByEntry.get(r.entry);
		if (!cs) cladeByEntry.set(r.entry, (cs = new Set()));
		cs.add(lang.clade);
		let ls = langByEntry.get(r.entry);
		if (!ls) langByEntry.set(r.entry, (ls = new Set()));
		ls.add(lang.id);
		langName[lang.id] = lang.name;
		langClade[lang.id] = lang.clade;
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

/** Presence-invariant sound-change isogloss model (see the v1 layer for the definition). For each
 *  proto-slot (etymon × aligned position) every clade/language *present* has an outcome (its
 *  reflex segment); a pair of units both present at a slot contributes 1 to `both`, and one per
 *  shared distinct outcome to `agree`. Decoded from the per-form alignment blobs in JS. */
export interface SoundAgreement {
	pair: Map<string, { both: number; agree: number }>;
}
export async function getIsoglossSoundChangeData(
	family: string,
	level: 'clade' | 'lang'
): Promise<SoundAgreement> {
	await ensureCore();
	const meta = await ensureAlignMeta();
	const rows = await query<{ e: number; lrid: number; segs: Uint8Array }>(
		`SELECT l.origin_rid AS e, l.lang_rid AS lrid, a.segs AS segs
		 FROM alignment a JOIN lem l ON l.rowid = a.form_rid
		 JOIN languages lang ON lang.rowid = l.lang_rid
		 WHERE (l.flags & 7) = ${REL_REFLEX} AND lang.clade IS NOT NULL AND lang.clade != ''
		   AND l.origin_rid IN (SELECT rowid FROM lem WHERE origin_rid IS NULL AND lang_rid = ?)`,
		[langRidOf(family) ?? -1]
	);
	// per (etymon, pos): unit → set of outcomes (reflex symbol ids)
	const slots = new Map<string, Map<string, Set<number>>>();
	for (const r of rows) {
		const lang = langByRid(r.lrid);
		if (!lang) continue;
		const unit = level === 'clade' ? lang.clade : lang.id;
		const cellIds = readVarints(r.segs);
		for (let pos = 0; pos < cellIds.length; pos++) {
			const cell = meta.cells[cellIds[pos] - 1];
			const outcome = meta.pair.get(cell.pairId)!.r;
			const key = `${r.e}|${pos}`;
			let units = slots.get(key);
			if (!units) slots.set(key, (units = new Map()));
			let outcomes = units.get(unit);
			if (!outcomes) units.set(unit, (outcomes = new Set()));
			outcomes.add(outcome);
		}
	}
	const pair = new Map<string, { both: number; agree: number }>();
	for (const units of slots.values()) {
		const names = [...units.keys()].sort();
		for (let i = 0; i < names.length; i++) {
			for (let j = i + 1; j < names.length; j++) {
				const key = `${names[i]}|${names[j]}`;
				let p = pair.get(key);
				if (!p) pair.set(key, (p = { both: 0, agree: 0 }));
				p.both += 1;
				const a = units.get(names[i])!;
				const b = units.get(names[j])!;
				for (const o of a) if (b.has(o)) p.agree += 1;
			}
		}
	}
	return { pair };
}
