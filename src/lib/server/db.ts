/**
 * server/db.ts — BUILD-TIME SQLite access via better-sqlite3.
 *
 * Used only by `+page.server.ts` loads during prerendering (and by the dev server). The output
 * is baked into static HTML + `__data.json`, so at runtime on GitHub Pages there is no server —
 * canonical pages are already rendered. This module is under `$lib/server/` so SvelteKit will
 * never bundle better-sqlite3 into the client.
 *
 * Queries run against the compact ("v2") schema (see scripts/compact_db.py); rows are rebuilt
 * to the legacy shapes with the codecs in $lib/dbShared.
 *
 * PRERENDER_LIMIT (optional env): cap how many entry/language/reference pages are prerendered.
 * For fast LOCAL build smoke-tests only — production must prerender everything.
 */
import Database from 'better-sqlite3';
import { statSync } from 'node:fs';
import { dev } from '$app/environment';
import {
	IdIndex,
	hydrateLem,
	LEM_COLS,
	LEM_JOINS,
	readVarints,
	readDeltas,
	aliasGroupKey,
	aliasLookup,
	makeVinAny,
	FLAG_OCR,
	REL_UNLINKED,
	type RawLem,
	type HydrateCtx
} from '$lib/dbShared';
import type {
	AttestationPlace,
	ConceptAttestation,
	ConceptDetail,
	ConceptEtymon,
	ConceptRow,
	Language,
	Lemma,
	Reference
} from '$lib/types';

const DB_PATH = process.env.JAMBU_DB ?? '.dbwork/jambu.db';

const LANGUAGE_COLS =
	'id, name, language, dialect, glottocode, long, lat, clade, color, ' +
	'lemma_count, "order", map_marker';

let db: Database.Database | null = null;
let openedMtime = 0;

// per-connection caches (reset when the dev server reopens a rebuilt DB)
let _ids: IdIndex | null = null;
let _cladeNames: string[] | null = null;
let _langById: Map<number, string> | null = null;
let _rootMap: Map<number, number> | null = null;
let _dialectPoints: Map<string, { name: string; lat: number; long: number }> | null = null;

function resetCaches(): void {
	_ids = null;
	_cladeNames = null;
	_langById = null;
	_rootMap = null;
	_dialectPoints = null;
}

export function getDb(): Database.Database {
	// In dev the long-lived Vite server would otherwise pin a cached connection to a stale inode:
	// build_static_db.py replaces .dbwork/jambu.db in place, so reopen whenever its mtime changes.
	if (dev && db) {
		const mtime = statSync(DB_PATH).mtimeMs;
		if (mtime !== openedMtime) {
			db.close();
			db = null;
			resetCaches();
		}
	}
	if (!db) {
		db = new Database(DB_PATH, { readonly: true, fileMustExist: true });
		if (dev) openedMtime = statSync(DB_PATH).mtimeMs;
		const vinAny = makeVinAny();
		db.function('vin_any', { deterministic: true }, (blob: unknown, json: unknown) =>
			vinAny(blob ? new Uint8Array(blob as Buffer) : null, String(json))
		);
	}
	return db;
}

export function ids(): IdIndex {
	if (!_ids) {
		const dbh = getDb();
		const data = (dbh.prepare('SELECT data FROM ids').get() as { data: Buffer }).data;
		const misc = (dbh.prepare('SELECT id FROM ids_misc ORDER BY rank').all() as { id: string }[]).map(
			(r) => r.id
		);
		_ids = new IdIndex(new Uint8Array(data), misc);
	}
	return _ids;
}

function hydrateCtx(): HydrateCtx {
	const dbh = getDb();
	if (!_cladeNames)
		_cladeNames = (dbh.prepare('SELECT name FROM mask_clades ORDER BY rowid').all() as {
			name: string;
		}[]).map((r) => r.name);
	if (!_langById)
		_langById = new Map(
			(dbh.prepare('SELECT rowid AS rid, id FROM languages').all() as { rid: number; id: string }[]).map(
				(r) => [r.rid, r.id]
			)
		);
	return {
		ids: ids(),
		langIdOf: (rid) => _langById!.get(rid) ?? '',
		cladeNames: _cladeNames
	};
}

function toRaw(row: Record<string, unknown>): RawLem {
	return {
		...(row as unknown as RawLem),
		cites: row.cites ? new Uint8Array(row.cites as Buffer) : null,
		children: row.children ? new Uint8Array(row.children as Buffer) : null
	};
}

function hydrate(row: Record<string, unknown>): Lemma & { rid: number; citeIds: number[] } {
	return hydrateLem(toRaw(row), hydrateCtx()) as unknown as Lemma & {
		rid: number;
		citeIds: number[];
	};
}

export const PRERENDER_LIMIT = process.env.PRERENDER_LIMIT
	? parseInt(process.env.PRERENDER_LIMIT, 10)
	: Infinity;

function limit<T>(rows: T[]): T[] {
	return Number.isFinite(PRERENDER_LIMIT) ? rows.slice(0, PRERENDER_LIMIT) : rows;
}

// ---- id enumerations for prerender `entries()` ---------------------------

export function allEntryIds(): { entry: string }[] {
	const idx = ids();
	const rows = getDb()
		.prepare('SELECT rowid AS rid FROM lem WHERE origin_rid IS NULL ORDER BY ord')
		.all() as { rid: number }[];
	return limit(rows.map((r) => ({ entry: idx.idOf(r.rid) })));
}

export function allLanguageIds(): { lang1: string }[] {
	const rows = getDb().prepare(`SELECT id FROM languages ORDER BY "order", name`).all() as {
		id: string;
	}[];
	return limit(rows.map((r) => ({ lang1: String(r.id) })));
}

export function allDialectIds(): { lang1: string }[] {
	const rows = getDb().prepare(`SELECT id FROM dialects ORDER BY language_id, name, id`).all() as {
		id: string;
	}[];
	return limit(rows.map((r) => ({ lang1: String(r.id) })));
}

export function allReferenceIds(): { ref: string }[] {
	const rows = getDb().prepare(`SELECT id FROM "references" ORDER BY short`).all() as {
		id: string;
	}[];
	return limit(rows.map((r) => ({ ref: String(r.id) })));
}

export function allConceptIds(): { id: string }[] {
	const rows = getDb()
		.prepare(`SELECT id FROM concepts WHERE form_count > 0 ORDER BY etyma_count DESC, name`)
		.all() as { id: number }[];
	return limit(rows.map((r) => ({ id: String(r.id) })));
}

// ---- concepts -------------------------------------------------------------

const BAR_SEGMENTS = 16;

/** The dictionary a numeric/prefixed etymon id comes from. */
function etymonSource(id: string): string {
	if (/^d\d/.test(id)) return 'DEDR';
	if (/^m\d/.test(id)) return 'Munda';
	if (/^r\d/.test(id)) return 'CDIAL'; // Sanskrit verbal roots (√…), the deepest IA etyma
	if (/^\d/.test(id)) return 'CDIAL';
	return 'other';
}

// IA etyma are CDIAL entries (numeric ids) and Sanskrit roots (r-prefixed) — both are Indo-Aryan;
// used to prefer the Indo-Aryan branch when the derivation graph forks.
const isIA = (id: string) => /^(\d|r\d)/.test(id);

// Resolve each entry to its most-ancestral etymon by walking the derivation graph (child → parent)
// to a root (no parent). On branching, the branch leading to an IA root wins. Built once, memoised.
function rootEtymonMap(): Map<number, number> {
	if (_rootMap) return _rootMap;
	const idx = ids();
	const edges = getDb()
		.prepare(
			`SELECT child_rid, parent_rid FROM edges
			 WHERE kind IN (5, 6) AND rank = 1 ORDER BY COALESCE(pos, 0), rowid`
		)
		.all() as {
		child_rid: number;
		parent_rid: number;
	}[];
	const parents = new Map<number, number[]>();
	for (const e of edges) {
		const arr = parents.get(e.child_rid);
		if (arr) arr.push(e.parent_rid);
		else parents.set(e.child_rid, [e.parent_rid]);
	}
	const memo = new Map<number, number>();
	function resolve(rid: number, seen: Set<number>): number {
		const cached = memo.get(rid);
		if (cached) return cached;
		const ps = parents.get(rid);
		if (!ps || seen.has(rid)) return rid; // a root, or a cycle — stop here
		seen.add(rid);
		let best: number | null = null;
		for (const p of ps) {
			const r = resolve(p, seen);
			if (isIA(idx.idOf(r))) {
				best = r;
				break;
			}
			if (best === null) best = r;
		}
		seen.delete(rid);
		const root = best ?? rid;
		memo.set(rid, root);
		return root;
	}
	for (const c of parents.keys()) resolve(c, new Set());
	_rootMap = memo;
	return _rootMap;
}

/** The most-ancestral etymon for an immediate etymon rowid (itself if it heads no edge). */
function toRoot(rid: number): number {
	return rootEtymonMap().get(rid) ?? rid;
}

export function allConcepts(): ConceptRow[] {
	const dbh = getDb();
	const idx = ids();
	const concepts = dbh
		.prepare(
			`SELECT id, name, category, etyma_count, unetym_count, lang_count, form_count, rids
			 FROM concepts WHERE form_count > 0 ORDER BY etyma_count DESC, name`
		)
		.all() as (ConceptRow & { rids: Buffer | null })[];
	// per-form (origin, relation) for every concept-linked lemma, fetched once
	const lemInfo = new Map(
		(dbh.prepare('SELECT rowid AS rid, origin_rid, flags FROM lem').all() as {
			rid: number;
			origin_rid: number | null;
			flags: number;
		}[]).map((r) => [r.rid, r])
	);
	for (const c of concepts) {
		// per-immediate-etymon counts first, accumulated into roots in ascending etymon-id order —
		// this reproduces the v1 GROUP BY output order, which decides bar order among tied counts
		const byImm = new Map<number, number>();
		for (const rid of readDeltas(c.rids ? new Uint8Array(c.rids) : null)) {
			const info = lemInfo.get(rid);
			if (!info || (info.flags & 7) === REL_UNLINKED) continue;
			byImm.set(info.origin_rid ?? rid, (byImm.get(info.origin_rid ?? rid) ?? 0) + 1);
		}
		const byRoot = new Map<number, number>();
		for (const [imm, n] of [...byImm.entries()]
			.map(([r, n]) => [idx.idOf(r), r, n] as const)
			.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0))
			.map(([, r, n]) => [r, n] as const)) {
			const root = toRoot(imm);
			byRoot.set(root, (byRoot.get(root) ?? 0) + n);
		}
		const list = [...byRoot.entries()]
			.map(([root, n]) => ({ etymon: idx.idOf(root), n }))
			.sort((a, b) => b.n - a.n);
		c.bars = list.slice(0, BAR_SEGMENTS);
		c.rest = list.slice(BAR_SEGMENTS).reduce((s, b) => s + b.n, 0);
		delete (c as unknown as Record<string, unknown>).rids;
	}
	return concepts;
}

// Dialect tokens that carry coordinates, keyed by the token as it appears in lemma tags.
function dialectPoints() {
	if (_dialectPoints) return _dialectPoints;
	const rows = getDb()
		.prepare('SELECT token, name, lat, long FROM dialects WHERE lat IS NOT NULL AND long IS NOT NULL')
		.all() as { token: string; name: string; lat: number; long: number }[];
	_dialectPoints = new Map(rows.map((r) => [r.token, { name: r.name, lat: r.lat, long: r.long }]));
	return _dialectPoints;
}

/**
 * Where a form should be plotted: one point per located dialect it is tagged with, falling back
 * to the language's own point when it carries no located dialect tag.
 */
function placesFor(
	tags: string | null,
	language: string | null,
	lat: number | null,
	long: number | null
): AttestationPlace[] {
	const points = dialectPoints();
	const tagged = (tags ?? '')
		.split(/\s+/)
		.map((t) => {
			const d = points.get(t);
			return d && { key: t, name: `${language ?? '—'}: ${d.name}`, lat: d.lat, long: d.long };
		})
		.filter((p): p is AttestationPlace => !!p);
	if (tagged.length) return tagged;
	if (language && lat != null && long != null)
		return [{ key: `language:${language}`, name: language, lat, long }];
	return [];
}

export function getConceptDetail(id: string): ConceptDetail | null {
	const dbh = getDb();
	const idx = ids();
	const concept = dbh
		.prepare(
			`SELECT id, name, category, etyma_count, unetym_count, lang_count, form_count, rids
			 FROM concepts WHERE id = ?`
		)
		.get(id) as (ConceptRow & { rids: Buffer | null }) | undefined;
	if (!concept) return null;
	const linkedRids = readDeltas(concept.rids ? new Uint8Array(concept.rids) : null);
	delete (concept as unknown as Record<string, unknown>).rids;

	const linked = linkedRids.length
		? (dbh
				.prepare(
					`SELECT l.rowid AS rid, l.ord AS ord, l.word, l.gloss, l.flags, l.origin_rid,
					        ts.txt AS tags,
					        lang.id AS language_id, lang.name AS language, lang.clade AS clade,
					        lang.color AS color, lang.lat AS lat, lang.long AS long,
					        lang."order" AS lorder
					 FROM lem l
					 LEFT JOIN tagsets ts ON ts.rowid = l.tagset_rid
					 LEFT JOIN languages lang ON lang.rowid = l.lang_rid
					 WHERE l.rowid IN (SELECT value FROM json_each(?))
					 ORDER BY lorder, l.word`,
					)
				.all(JSON.stringify(linkedRids)) as Array<{
				rid: number;
				ord: number;
				word: string;
				gloss: string;
				flags: number;
				origin_rid: number | null;
				tags: string | null;
				language_id: string | null;
				language: string | null;
				clade: string | null;
				color: string | null;
				lat: number | null;
				long: number | null;
				lorder: number | null;
			}>)
		: [];
	// legacy row order: immediate etymon id (binary), then language order (NULLs first), then word
	linked.sort((a, b) => {
		const ea = idx.idOf(a.origin_rid ?? a.rid);
		const eb = idx.idOf(b.origin_rid ?? b.rid);
		if (ea !== eb) return ea < eb ? -1 : 1;
		const la = a.lorder ?? -Infinity;
		const lb = b.lorder ?? -Infinity;
		if (la !== lb) return la - lb;
		const wa = a.word ?? '';
		const wb = b.word ?? '';
		if (wa !== wb) return wa < wb ? -1 : 1;
		return a.ord - b.ord;
	});

	const rootRids = [
		...new Set(
			linked.filter((r) => (r.flags & 7) !== REL_UNLINKED).map((r) => toRoot(r.origin_rid ?? r.rid))
		)
	];
	const heads = new Map<number, { word: string; gloss: string; ocr: boolean | number }>();
	if (rootRids.length) {
		for (const r of dbh
			.prepare(
				`SELECT rowid AS rid, word, gloss, flags FROM lem
				 WHERE rowid IN (SELECT value FROM json_each(?))`
			)
			.all(JSON.stringify(rootRids)) as { rid: number; word: string; gloss: string; flags: number }[]) {
			heads.set(r.rid, { word: r.word, gloss: r.gloss, ocr: r.flags & FLAG_OCR ? 1 : 0 });
		}
	}

	const byEtymon = new Map<number, ConceptEtymon>();
	const unetym: ConceptAttestation[] = [];
	for (const r of linked) {
		const att: ConceptAttestation = {
			form_id: idx.idOf(r.rid),
			word: r.word,
			gloss: r.gloss,
			language_id: r.language_id,
			language: r.language,
			clade: r.clade,
			color: r.color,
			lat: r.lat,
			long: r.long,
			places: placesFor(r.tags, r.language, r.lat, r.long),
			ocr: r.flags & FLAG_OCR ? 1 : 0
		};
		if ((r.flags & 7) === REL_UNLINKED) {
			unetym.push(att);
			continue;
		}
		const root = toRoot(r.origin_rid ?? r.rid);
		let e = byEtymon.get(root);
		if (!e) {
			const rootId = idx.idOf(root);
			const head = heads.get(root);
			e = {
				etymon: rootId,
				word: head?.word || rootId,
				gloss: head?.gloss ?? '',
				source: etymonSource(rootId),
				languages: [],
				forms: [],
				ocr: head?.ocr ?? false
			};
			byEtymon.set(root, e);
		}
		e.forms.push(att);
		if (att.language && !e.languages.includes(att.language)) e.languages.push(att.language);
	}
	const etyma = [...byEtymon.values()].sort((a, b) => b.forms.length - a.forms.length);
	return { concept, etyma, unetym };
}

// ---- single-record loads --------------------------------------------------

export type EntryMeta = Omit<Lemma, 'language'> & { language: Language | null };

/** Resolve a public id to its lem rowid, following legacy-id aliases first (they shadow). */
export function resolveEntryRid(id: string): number | null {
	const dbh = getDb();
	const key = aliasGroupKey(id);
	if (key) {
		const g = dbh.prepare('SELECT data FROM aliases WHERE prefix = ?').get(key.prefix) as
			| { data: Buffer }
			| undefined;
		if (g) {
			const rid = aliasLookup(new Uint8Array(g.data), key.m);
			if (rid != null) return rid;
		}
	}
	const miscAlias = dbh.prepare('SELECT lemma_rid FROM aliases_misc WHERE alias = ?').get(id) as
		| { lemma_rid: number }
		| undefined;
	if (miscAlias) return miscAlias.lemma_rid;
	return ids().ridOf(id);
}

export function resolveEntryId(id: string): string {
	const rid = resolveEntryRid(id);
	return rid == null ? id : ids().idOf(rid);
}

export function getEntryMeta(id: string): EntryMeta | null {
	const dbh = getDb();
	const rid = resolveEntryRid(id);
	if (rid == null) return null;
	const row = dbh
		.prepare(`SELECT ${LEM_COLS} FROM lem l ${LEM_JOINS} WHERE l.rowid = ?`)
		.get(rid) as Record<string, unknown> | undefined;
	if (!row) return null;
	const e = hydrate(row);
	const language = (dbh
		.prepare(`SELECT ${LANGUAGE_COLS} FROM languages WHERE id = ?`)
		.get(e.language_id) ?? null) as Language | null;
	const eRec = e as unknown as Record<string, unknown>;
	delete eRec.citeIds;
	delete eRec.childRids;
	delete eRec.rid;
	return { ...e, language };
}

export interface DerivedTerm {
	id: string;
	word: string;
	gloss: string;
	reflex_count: number;
	lang_count: number;
}
export interface EntryGraph {
	ancestors: { id: string; word: string }[]; // etyma this one derives from
	derived: DerivedTerm[]; // etyma derived from this one
}

/** The derivation-graph neighbours of an entry (few per node, so prerendered for SEO). */
export function getEntryGraph(id: string): EntryGraph {
	const dbh = getDb();
	const idx = ids();
	const rid = idx.ridOf(id);
	if (rid == null) return { ancestors: [], derived: [] };
	const ancestors = (dbh
		.prepare(
			`SELECT l.rowid AS rid, l.word FROM edges d JOIN lem l ON l.rowid = d.parent_rid
			 WHERE d.child_rid = ? AND d.kind IN (5, 6) AND d.rank = 1
			 ORDER BY COALESCE(d.pos, 0), d.rowid`
		)
		.all(rid) as { rid: number; word: string }[]).map((r) => ({ id: idx.idOf(r.rid), word: r.word }));
	const derived = (dbh
		.prepare(
			`SELECT l.rowid AS rid, l.word, l.gloss, l.counts
			 FROM edges d JOIN lem l ON l.rowid = d.child_rid
			 WHERE d.parent_rid = ? AND d.kind IN (5, 6) AND d.rank = 1
			   AND l.origin_rid IS NULL ORDER BY l.ord`
		)
		.all(rid) as { rid: number; word: string; gloss: string; counts: number | null }[]).map((r) => ({
		id: idx.idOf(r.rid),
		word: r.word,
		gloss: r.gloss,
		reflex_count: r.counts != null ? r.counts >> 10 : 0,
		lang_count: r.counts != null ? r.counts % 1024 : 0
	}));
	return { ancestors, derived };
}

export function getLanguageRow(id: string): Language | null {
	return (getDb().prepare(`SELECT ${LANGUAGE_COLS} FROM languages WHERE id = ?`).get(id) ??
		null) as Language | null;
}

export function getDialectLanguageId(id: string): string | null {
	const row = getDb().prepare('SELECT language_id FROM dialects WHERE id = ?').get(id) as
		| { language_id: string }
		| undefined;
	return row?.language_id ?? null;
}

export function allLanguages(): Language[] {
	return getDb()
		.prepare(`SELECT ${LANGUAGE_COLS} FROM languages ORDER BY "order", name`)
		.all() as Language[];
}

export function getReferenceRow(id: string): Reference | null {
	return (getDb().prepare('SELECT * FROM "references" WHERE id = ?').get(id) ??
		null) as Reference | null;
}

export function allReferences(): Reference[] {
	return getDb().prepare('SELECT * FROM "references" ORDER BY short').all() as Reference[];
}
