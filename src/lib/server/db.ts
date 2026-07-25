/**
 * server/db.ts — BUILD-TIME SQLite access via better-sqlite3.
 *
 * Used only by `+page.server.ts` loads during prerendering (and by the dev server). The output
 * is baked into static HTML + `__data.json`, so at runtime on GitHub Pages there is no server —
 * canonical pages are already rendered. This module is under `$lib/server/` so SvelteKit will
 * never bundle better-sqlite3 into the client.
 *
 * PRERENDER_LIMIT (optional env): cap how many entry/language/reference pages are prerendered.
 * For fast LOCAL build smoke-tests only — production must prerender everything.
 */
import Database from 'better-sqlite3';
import { statSync } from 'node:fs';
import { dev } from '$app/environment';
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

let db: Database.Database | null = null;
let openedMtime = 0;
export function getDb(): Database.Database {
	// In dev the long-lived Vite server would otherwise pin a cached connection to a stale inode:
	// build_static_db.py replaces .dbwork/jambu.db in place, so reopen whenever its mtime changes.
	if (dev && db) {
		const mtime = statSync(DB_PATH).mtimeMs;
		if (mtime !== openedMtime) {
			db.close();
			db = null;
		}
	}
	if (!db) {
		db = new Database(DB_PATH, { readonly: true, fileMustExist: true });
		if (dev) openedMtime = statSync(DB_PATH).mtimeMs;
	}
	return db;
}

export const PRERENDER_LIMIT = process.env.PRERENDER_LIMIT
	? parseInt(process.env.PRERENDER_LIMIT, 10)
	: Infinity;

function limit<T>(rows: T[]): T[] {
	return Number.isFinite(PRERENDER_LIMIT) ? rows.slice(0, PRERENDER_LIMIT) : rows;
}

// ---- id enumerations for prerender `entries()` ---------------------------

export function allEntryIds(): { entry: string }[] {
	const rows = getDb()
		.prepare(`SELECT id FROM lemmas WHERE origin_lemma_id IS NULL ORDER BY "order"`)
		.all() as { id: string }[];
	return limit(rows.map((r) => ({ entry: String(r.id) })));
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

export function allConcepts(): ConceptRow[] {
	const dbh = getDb();
	const concepts = dbh
		.prepare(
			`SELECT id, name, category, etyma_count, unetym_count, lang_count, form_count
			 FROM concepts WHERE form_count > 0 ORDER BY etyma_count DESC, name`
		)
		.all() as ConceptRow[];
	// per-concept etymon sizes (form counts) for the stacked bar; grouped once for the whole table
	const rows = dbh
		.prepare(
			`SELECT lc.concept_id AS cid, COALESCE(NULLIF(l.origin_lemma_id, ''), l.id) AS etymon,
			        COUNT(*) AS n
			 FROM lemma_concept lc JOIN lemmas l ON l.rowid = lc.lemma_rid
			 WHERE l.relation IS NOT 'local'
			 GROUP BY lc.concept_id, etymon`
		)
		.all() as { cid: number; etymon: string; n: number }[];
	// aggregate by the most-ancestral (root) etymon so the bar reflects deep etymological families
	const byConcept = new Map<number, Map<string, number>>();
	for (const r of rows) {
		const root = toRoot(r.etymon);
		let m = byConcept.get(r.cid);
		if (!m) byConcept.set(r.cid, (m = new Map()));
		m.set(root, (m.get(root) ?? 0) + r.n);
	}
	for (const c of concepts) {
		const list = [...(byConcept.get(c.id) ?? new Map()).entries()]
			.map(([etymon, n]) => ({ etymon, n }))
			.sort((a, b) => b.n - a.n);
		c.bars = list.slice(0, BAR_SEGMENTS);
		c.rest = list.slice(BAR_SEGMENTS).reduce((s, b) => s + b.n, 0);
	}
	return concepts;
}

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
let _rootMap: Map<string, string> | null = null;
function rootEtymonMap(): Map<string, string> {
	if (_rootMap) return _rootMap;
	const edges = getDb().prepare('SELECT child_id, parent_id FROM derivation').all() as {
		child_id: string;
		parent_id: string;
	}[];
	const parents = new Map<string, string[]>();
	for (const e of edges) {
		const arr = parents.get(e.child_id);
		if (arr) arr.push(e.parent_id);
		else parents.set(e.child_id, [e.parent_id]);
	}
	const memo = new Map<string, string>();
	function resolve(id: string, seen: Set<string>): string {
		const cached = memo.get(id);
		if (cached) return cached;
		const ps = parents.get(id);
		if (!ps || seen.has(id)) return id; // a root, or a cycle — stop here
		seen.add(id);
		let best: string | null = null;
		for (const p of ps) {
			const r = resolve(p, seen);
			if (isIA(r)) {
				best = r;
				break;
			}
			if (best === null) best = r;
		}
		seen.delete(id);
		const root = best ?? id;
		memo.set(id, root);
		return root;
	}
	for (const c of parents.keys()) resolve(c, new Set());
	_rootMap = memo;
	return _rootMap;
}

/** The most-ancestral etymon for an immediate etymon id (itself if it heads no derivation edge). */
function toRoot(id: string): string {
	return rootEtymonMap().get(id) ?? id;
}

// Dialect tokens that carry coordinates, keyed by the token as it appears in lemmas.tags.
// Built once, memoised (443 of 585 dialects are located).
let _dialectPoints: Map<string, { name: string; lat: number; long: number }> | null = null;
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
 * to the language's own point when it carries no located dialect tag. Mirrors the entry-page map,
 * so a dialectally-tagged form lands on the dialect rather than the language centroid.
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
	const concept = dbh
		.prepare(
			`SELECT id, name, category, etyma_count, unetym_count, lang_count, form_count
			 FROM concepts WHERE id = ?`
		)
		.get(id) as ConceptRow | undefined;
	if (!concept) return null;

	const linked = dbh
		.prepare(
			`SELECT l.id AS form_id, l.word, l.gloss, l.relation, l.tags,
			        COALESCE(NULLIF(l.origin_lemma_id, ''), l.id) AS etymon,
			        lang.name AS language, lang.clade AS clade, lang.color AS color,
			        lang.lat AS lat, lang.long AS long, lang."order" AS lorder
			 FROM lemma_concept lc
			 JOIN lemmas l ON l.rowid = lc.lemma_rid
			 LEFT JOIN languages lang ON lang.id = l.language_id
			 WHERE lc.concept_id = ?
			 ORDER BY etymon, lorder, l.word`
		)
		.all(id) as Array<
		ConceptAttestation & { etymon: string; relation: string | null; tags: string | null }
	>;

	// group by the most-ancestral (root) etymon so the map colours by deep etymological family
	// (the per-concept table keeps immediate etyma; this only feeds the map)
	const rootOf = (r: { etymon: string }) => toRoot(r.etymon);
	const etymonIds = [...new Set(linked.filter((r) => r.relation !== 'local').map(rootOf))];
	const heads = new Map<string, { word: string; gloss: string }>();
	if (etymonIds.length) {
		const qs = etymonIds.map(() => '?').join(',');
		for (const r of dbh
			.prepare(`SELECT id, word, gloss FROM lemmas WHERE id IN (${qs})`)
			.all(...etymonIds) as { id: string; word: string; gloss: string }[]) {
			heads.set(r.id, { word: r.word, gloss: r.gloss });
		}
	}

	const byEtymon = new Map<string, ConceptEtymon>();
	const unetym: ConceptAttestation[] = [];
	for (const r of linked) {
		const att: ConceptAttestation = {
			form_id: r.form_id,
			word: r.word,
			gloss: r.gloss,
			language: r.language,
			clade: r.clade,
			color: r.color,
			lat: r.lat,
			long: r.long,
			places: placesFor(r.tags, r.language, r.lat, r.long)
		};
		if (r.relation === 'local') {
			unetym.push(att);
			continue;
		}
		const root = rootOf(r);
		let e = byEtymon.get(root);
		if (!e) {
			const head = heads.get(root);
			e = {
				etymon: root,
				word: head?.word || root,
				gloss: head?.gloss ?? '',
				source: etymonSource(root),
				languages: [],
				forms: []
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

export function getEntryMeta(id: string): EntryMeta | null {
	const dbh = getDb();
	const e = dbh.prepare('SELECT * FROM lemmas WHERE id = ?').get(id) as Lemma | undefined;
	if (!e) return null;
	const language = (dbh.prepare('SELECT * FROM languages WHERE id = ?').get(e.language_id) ??
		null) as Language | null;
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
	if (!tableExists(dbh, 'derivation')) return { ancestors: [], derived: [] };
	const ancestors = dbh
		.prepare(
			`SELECT l.id, l.word FROM derivation d JOIN lemmas l ON l.id = d.parent_id
			 WHERE d.child_id = ? ORDER BY d.rowid`
		)
		.all(id) as { id: string; word: string }[];
	// derived TERMS are same-language derived etyma (headwords: origin_lemma_id IS NULL); a child
	// with origin set is an alternate-etymology reflex, shown under the entry's reflexes instead.
	const derived = dbh
		.prepare(
			`SELECT l.id, l.word, l.gloss, l.reflex_count, l.lang_count
			 FROM derivation d JOIN lemmas l ON l.id = d.child_id
			 WHERE d.parent_id = ? AND l.origin_lemma_id IS NULL ORDER BY l."order"`
		)
		.all(id) as DerivedTerm[];
	return { ancestors, derived };
}

function tableExists(dbh: Database.Database, name: string): boolean {
	return !!dbh.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?").get(name);
}

export function getLanguageRow(id: string): Language | null {
	return (getDb().prepare('SELECT * FROM languages WHERE id = ?').get(id) ?? null) as Language | null;
}

export function getDialectLanguageId(id: string): string | null {
	const row = getDb().prepare('SELECT language_id FROM dialects WHERE id = ?').get(id) as
		| { language_id: string }
		| undefined;
	return row?.language_id ?? null;
}

export function allLanguages(): Language[] {
	return getDb().prepare('SELECT * FROM languages ORDER BY "order", name').all() as Language[];
}

export function getReferenceRow(id: string): Reference | null {
	return (getDb().prepare('SELECT * FROM "references" WHERE id = ?').get(id) ??
		null) as Reference | null;
}

export function allReferences(): Reference[] {
	return getDb().prepare('SELECT * FROM "references" ORDER BY short').all() as Reference[];
}
