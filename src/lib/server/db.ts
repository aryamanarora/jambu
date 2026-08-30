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
import { cladeFamily } from '$lib/cladeTree';
import { bestEtymologyGuess } from '$lib/etymologyGuess';
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
	REL_VARIANT,
	type RawLem,
	type HydrateCtx
} from '$lib/dbShared';
import type {
	AttestationPlace,
	ConceptAttestation,
	ConceptBarGroup,
	ConceptDetail,
	ConceptEtymon,
	ConceptRow,
	GlobalStats,
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
let _dialectPoints: Map<string, { name: string; lat: number; long: number }> | null = null;
let _guessReflexes: Map<
	number,
	Array<{ word: string; phonemic: string | null; language_id: string | null }>
> | null = null;

function resetCaches(): void {
	_ids = null;
	_cladeNames = null;
	_langById = null;
	_dialectPoints = null;
	_guessReflexes = null;
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

/** The concept the atlas opens on when no id is given: the most widely attested one. */
export function defaultConceptId(): string | null {
	const row = getDb()
		.prepare(`SELECT id FROM concepts WHERE form_count > 0 ORDER BY form_count DESC, name LIMIT 1`)
		.get() as { id: number } | undefined;
	return row ? String(row.id) : null;
}

// ---- concepts -------------------------------------------------------------

const BAR_SEGMENTS = 16;
const REFLEX_FAMILIES = ['Indo-Iranian', 'Dravidian', 'Other'] as const;

// Iranian languages currently have the generic `Other` clade in languages.csv. Keep this
// explicit until the source data has a first-class Iranian clade, so they are not lost from the
// Indo-Iranian reflex rollup.
const IRANIAN_LANGUAGE_IDS = new Set([
	'Av',
	'Bal',
	'Chvar',
	'Ir',
	'Ishk',
	'Khot',
	'Kurd',
	'Mj',
	'MPrs',
	'OPers',
	'Orm',
	'Oss',
	'Pahl',
	'Par',
	'Parth',
	'Pers',
	'Psht',
	'Rosh',
	'Sang',
	'Sar',
	'Shgh',
	'Sogd',
	'Wj',
	'Wkh',
	'X',
	'Yazgh',
	'Yghn',
	'Yid',
	'Darw'
]);

function reflexFamily(id: string, clade: string | null): (typeof REFLEX_FAMILIES)[number] {
	if (IRANIAN_LANGUAGE_IDS.has(id)) return 'Indo-Iranian';
	const family = clade ? cladeFamily(clade) : 'Other';
	if (family === 'Indo-Aryan') return 'Indo-Iranian';
	if (family === 'Dravidian') return 'Dravidian';
	return 'Other';
}

/** The dictionary a numeric/prefixed etymon id comes from. */
function etymonSource(id: string): string {
	if (/^d\d/.test(id)) return 'DEDR';
	if (/^m\d/.test(id)) return 'Munda';
	if (/^r\d/.test(id)) return 'CDIAL'; // Sanskrit verbal roots (√…), the deepest IA etyma
	if (/^\d/.test(id)) return 'CDIAL';
	return 'other';
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
	const langFamilies = new Map(
		(dbh.prepare('SELECT rowid AS rid, id, clade FROM languages').all() as {
			rid: number;
			id: string;
			clade: string | null;
		}[]).map((r) => [r.rid, reflexFamily(r.id, r.clade)])
	);
	// Per-form origin, relation, and reflex language for every concept-linked lemma, fetched once.
	const lemInfo = new Map(
		(dbh.prepare('SELECT rowid AS rid, origin_rid, lang_rid, flags FROM lem').all() as {
			rid: number;
			origin_rid: number | null;
			lang_rid: number | null;
			flags: number;
		}[]).map((r) => [r.rid, r])
	);
	for (const c of concepts) {
		// Count each concept-linked form under the immediate entry it belongs to.
		const byImm = new Map<number, number>();
		const byFamilyImm = new Map(REFLEX_FAMILIES.map((family) => [family, new Map<number, number>()]));
		const familyUnetym = new Map(REFLEX_FAMILIES.map((family) => [family, 0]));
		for (const rid of readDeltas(c.rids ? new Uint8Array(c.rids) : null)) {
			const info = lemInfo.get(rid);
			if (!info) continue;
			const family = info.lang_rid == null ? 'Other' : (langFamilies.get(info.lang_rid) ?? 'Other');
			if ((info.flags & 7) === REL_UNLINKED) {
				familyUnetym.set(family, (familyUnetym.get(family) ?? 0) + 1);
				continue;
			}
			const imm = info.origin_rid ?? rid;
			byImm.set(imm, (byImm.get(imm) ?? 0) + 1);
			const familyCounts = byFamilyImm.get(family)!;
			familyCounts.set(imm, (familyCounts.get(imm) ?? 0) + 1);
		}
		const list = [...byImm.entries()]
			.map(([entry, n]) => ({ etymon: idx.idOf(entry), n }))
			.sort((a, b) => b.n - a.n || a.etymon.localeCompare(b.etymon));
		c.bars = list.slice(0, BAR_SEGMENTS);
		c.rest = list.slice(BAR_SEGMENTS).reduce((s, b) => s + b.n, 0);
		c.reflex_family_bars = REFLEX_FAMILIES.map((family): ConceptBarGroup => {
			const familyList = [...byFamilyImm.get(family)!]
				.map(([entry, n]) => ({ etymon: idx.idOf(entry), n }))
				.sort((a, b) => b.n - a.n || a.etymon.localeCompare(b.etymon));
			return {
				family,
				bars: familyList.slice(0, BAR_SEGMENTS),
				rest: familyList.slice(BAR_SEGMENTS).reduce((sum, b) => sum + b.n, 0),
				unetym_count: familyUnetym.get(family) ?? 0
			};
		});
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

/** All direct reflexes grouped once for concept-page guessing. The compact DB intentionally has
 * no origin index, so one build-wide scan is far cheaper than rescanning `lem` for every concept. */
function guessReflexes() {
	if (_guessReflexes) return _guessReflexes;
	_guessReflexes = new Map();
	for (const reflex of getDb()
		.prepare(
			`SELECT att.origin_rid, att.word, att.phonemic, lang.id AS language_id
			 FROM lem att LEFT JOIN languages lang ON lang.rowid = att.lang_rid
			 WHERE att.origin_rid IS NOT NULL AND att.link_rid IS NULL`
		)
		.all() as Array<{
		origin_rid: number;
		word: string;
		phonemic: string | null;
		language_id: string | null;
	}>) {
		const rows = _guessReflexes.get(reflex.origin_rid) ?? [];
		rows.push(reflex);
		_guessReflexes.set(reflex.origin_rid, rows);
	}
	return _guessReflexes;
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
					`SELECT l.rowid AS rid, l.ord AS ord, l.word, l.gloss, l.phonemic, l.flags, l.origin_rid,
					        ts.txt AS tags,
					        lang.id AS language_id, lang.name AS language, lang.clade AS clade,
					        lang.color AS color, lang.lat AS lat, lang.long AS long,
					        lang."order" AS lorder, lang.map_marker AS map_marker
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
				phonemic: string | null;
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
				map_marker: string | null;
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

	// A variant's edge points at the form it varies, not at an etymon — so an alternate of a
	// reflex would otherwise be grouped under that reflex, inventing an "etymon" that is really
	// just another attestation. Resolve each variant through its target to the target's own
	// etymon (and drop it into the unetymologised pile if the target has none).
	const variantTargets = [
		...new Set(
			linked
				.filter((r) => (r.flags & 7) === REL_VARIANT && r.origin_rid != null)
				.map((r) => r.origin_rid as number)
		)
	];
	const targetOf = new Map<number, { flags: number; origin_rid: number | null }>();
	if (variantTargets.length) {
		for (const t of dbh
			.prepare(
				`SELECT rowid AS rid, flags, origin_rid FROM lem
				 WHERE rowid IN (SELECT value FROM json_each(?))`
			)
			.all(JSON.stringify(variantTargets)) as {
			rid: number;
			flags: number;
			origin_rid: number | null;
		}[]) {
			targetOf.set(t.rid, { flags: t.flags, origin_rid: t.origin_rid });
		}
	}
	/** The etymon a concept-linked row belongs under, or null if it has none. */
	const etymonRidFor = (r: { rid: number; flags: number; origin_rid: number | null }): number | null => {
		const rel = r.flags & 7;
		if (rel === REL_UNLINKED) return null;
		if (rel !== REL_VARIANT) return r.origin_rid ?? r.rid;
		if (r.origin_rid == null) return null;
		const target = targetOf.get(r.origin_rid);
		if (!target) return r.origin_rid;
		// the target is itself an entry (no origin) → that entry is the etymon
		return (target.flags & 7) === REL_UNLINKED ? null : (target.origin_rid ?? r.origin_rid);
	};

	const entryRids = [
		...new Set(linked.map(etymonRidFor).filter((rid): rid is number => rid != null))
	];
	const heads = new Map<
		number,
		{ word: string; gloss: string; ocr: boolean | number; language: string | null; clade: string | null }
	>();
	if (entryRids.length) {
		for (const r of dbh
			.prepare(
				`SELECT l.rowid AS rid, l.word, l.gloss, l.flags,
				        lang.name AS language, lang.clade AS clade
				 FROM lem l
				 LEFT JOIN languages lang ON lang.rowid = l.lang_rid
				 WHERE l.rowid IN (SELECT value FROM json_each(?))`
			)
			.all(JSON.stringify(entryRids)) as {
			rid: number;
			word: string;
			gloss: string;
			flags: number;
			language: string | null;
			clade: string | null;
		}[]) {
			heads.set(r.rid, {
				word: r.word,
				gloss: r.gloss,
				ocr: r.flags & FLAG_OCR ? 1 : 0,
				language: r.language,
				clade: r.clade
			});
		}
	}

	const byEtymon = new Map<number, ConceptEtymon>();
	const unetym: ConceptAttestation[] = [];
	const soundByForm = new Map<string, string>();
	for (const r of linked) {
		const formId = idx.idOf(r.rid);
		const att: ConceptAttestation = {
			form_id: formId,
			word: r.word,
			gloss: r.gloss,
			language_id: r.language_id,
			language: r.language,
			clade: r.clade,
			color: r.color,
			lat: r.lat,
			long: r.long,
			places: placesFor(r.tags, r.language, r.lat, r.long),
			ocr: r.flags & FLAG_OCR ? 1 : 0,
			// the curated per-language marker is a rhombus for historical and reconstructed
			// languages and a circle for living ones — the same distinction the atlas draws
			historical: (r.map_marker ?? '').includes('polygon')
		};
		soundByForm.set(formId, r.phonemic || r.word);
		const entry = etymonRidFor(r);
		if (entry == null) {
			unetym.push(att);
			continue;
		}
		let e = byEtymon.get(entry);
		if (!e) {
			const entryId = idx.idOf(entry);
			const head = heads.get(entry);
			e = {
				etymon: entryId,
				word: head?.word || entryId,
				gloss: head?.gloss ?? '',
				source: etymonSource(entryId),
				language: head?.language ?? null,
				clade: head?.clade ?? null,
				languages: [],
				forms: [],
				ocr: head?.ocr ?? false
			};
			byEtymon.set(entry, e);
		}
		e.forms.push(att);
		if (att.language && !e.languages.includes(att.language)) e.languages.push(att.language);
	}
	// ranked by how many languages attest the etymon, not how many forms: a single language with
	// a dozen variant spellings is not better evidence than a dozen languages with one each
	const etyma = [...byEtymon.values()].sort(
		(a, b) => b.languages.length - a.languages.length || b.forms.length - a.forms.length
	);
	// A concept page may preview unlinked forms under a best-guess etymon. The candidate pool is
	// deliberately only these already-attested etyma; this never proposes an etymon on semantic
	// evidence from some other concept, and it remains a display-only suggestion.
	if (unetym.length && byEtymon.size) {
		const reflexesByEtymon = guessReflexes();
		const guessCandidates = [...byEtymon.entries()].map(([rid, etymon]) => ({
			value: etymon.etymon,
			headword: etymon.word,
			reflexes: reflexesByEtymon.get(rid) ?? []
		}));
		for (const form of unetym) {
			const guess = bestEtymologyGuess(
				{
					word: form.word,
					phonemic: soundByForm.get(form.form_id),
					language_id: form.language_id
				},
				guessCandidates
			);
			if (guess)
				form.best_guess = {
					etymon: guess.value,
					similarity: guess.similarity,
					matched_word: guess.matchedWord
				};
		}
	}
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
	e.references = referencesForCiteIds(e.citeIds);
	e.text_blocks = getTextBlocks(rid);
	const language = (dbh
		.prepare(`SELECT ${LANGUAGE_COLS} FROM languages WHERE id = ?`)
		.get(e.language_id) ?? null) as Language | null;
	const eRec = e as unknown as Record<string, unknown>;
	delete eRec.citeIds;
	delete eRec.childRids;
	delete eRec.rid;
	return { ...e, language };
}

function referencesForCiteIds(citeIds: number[]): Reference[] {
	if (!citeIds.length) return [];
	const placeholders = citeIds.map(() => '?').join(',');
	const rows = getDb()
		.prepare(
			`SELECT r.rowid AS reference_rid, r.id, r.short, r.source, r.progress,
			        r.provenance, r.editor, r.ocr, r.etymology_provenance,
			        r.lemma_count, r.unetymologised_count,
			        c.locator
			 FROM cites c JOIN "references" r ON r.rowid = c.ref_rid
			 WHERE c.rowid IN (${placeholders}) ORDER BY r.short, c.rowid`
		)
		.all(...citeIds) as Array<Reference & { reference_rid: number }>;
	const byReference = new Map<number, Reference>();
	for (const row of rows) {
		const existing = byReference.get(row.reference_rid);
		if (existing) {
			if (row.locator && !existing.locator?.split('; ').includes(row.locator))
				existing.locator = [existing.locator, row.locator].filter(Boolean).join('; ');
			continue;
		}
		byReference.set(row.reference_rid, {
			id: row.id,
			short: row.short,
			source: row.source,
			progress: row.progress,
			provenance: row.provenance,
			editor: row.editor,
			ocr: row.ocr,
			etymology_provenance: row.etymology_provenance,
			lemma_count: row.lemma_count,
			unetymologised_count: row.unetymologised_count,
			locator: row.locator || undefined
		});
	}
	return [...byReference.values()];
}

function getTextBlocks(rid: number): Lemma['text_blocks'] {
	return getDb()
		.prepare(
			`SELECT t.pos AS position, t.kind, t.format, t.content,
			        r.id AS source_id, r.short AS source_label, r.source AS source_citation,
			        r.progress AS source_progress, r.provenance AS source_provenance,
			        r.editor AS source_editor, r.ocr AS source_ocr,
			        r.lemma_count AS source_lemma_count,
			        r.unetymologised_count AS source_unetymologised_count, t.locator
			 FROM texts t LEFT JOIN "references" r ON r.rowid = t.ref_rid
			 WHERE t.lemma_rid = ? ORDER BY t.pos`
		)
		.all(rid) as Lemma['text_blocks'];
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

// ---- global corpus stats --------------------------------------------------

/**
 * The headline size of the corpus, for the homepage. Entry/form/reflex totals come from the
 * precomputed `meta` table (built by build_static_db.py) so they match the counts the list
 * pages show; the rest are cheap table counts.
 */
export function globalStats(): GlobalStats {
	const dbh = getDb();
	const meta = new Map(
		(dbh.prepare('SELECT key, value FROM meta').all() as { key: string; value: number }[]).map(
			(r) => [r.key, Number(r.value)]
		)
	);
	const count = (sql: string) => (dbh.prepare(sql).get() as { n: number }).n;
	return {
		entries: meta.get('total_entries') ?? 0,
		forms: meta.get('total_lexicon') ?? 0,
		reflexes: meta.get('total_reflexes') ?? 0,
		languages: count('SELECT COUNT(*) AS n FROM languages'),
		dialects: count('SELECT COUNT(*) AS n FROM dialects WHERE lemma_count > 0'),
		references: count('SELECT COUNT(*) AS n FROM "references"'),
		concepts: count('SELECT COUNT(*) AS n FROM concepts WHERE form_count > 0')
	};
}
