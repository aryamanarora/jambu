#!/usr/bin/env node
/**
 * semantic_parity.mjs — schema-independent semantic dump of the compact browser DB.
 *
 *   node scripts/semantic_parity.mjs DB_PATH OUT.json
 *
 * Extracts the *meaning* of the etymological graph in a form that is comparable across the
 * v2 (origin_rid + link_rid + derivation) and v3 (rank-1 edge + etymon_rid + typed edges)
 * schemas, so the edge-table migration can prove semantic parity:
 *
 *   parent[id]    = { target, kind }   — the immediate parent link a reader follows
 *                    (v2: COALESCE(variant_of, origin) trick; v3: origin_rid directly)
 *   root[id]      = attestation-tree root reached by following parent[] (entry membership)
 *   status[id]    = { kind, ocr, section, loan }  (v2 'local' normalized to 'unlinked')
 *   entries[]     = ordered entries listing (partial-index query)
 *   counts[id]    = packed reflex/lang counts on entries
 *   alignDigest[id] = sha1 of the decoded per-form alignment cell sequence
 *   graphEdges[]  = v2: derivation rows (order-preserved); v3: typed edge rows
 *
 * All maps are keyed by public text id. The Phase-3 comparator diffs two dumps and applies
 * the enumerated waiver classes (8 cross-entry variants, Khowar dedup, alternate-edge
 * reclassification) with exact expected counts.
 */
import Database from 'better-sqlite3';
import { createHash } from 'node:crypto';
import { writeFileSync } from 'node:fs';
import { IdIndex, readCellDict, readVarints, relationName } from '../src/lib/dbShared.ts';

const [dbPath, outPath] = process.argv.slice(2);
if (!dbPath || !outPath) {
	console.error('usage: semantic_parity.mjs DB_PATH OUT.json');
	process.exit(2);
}
const db = new Database(dbPath, { readonly: true, fileMustExist: true });

const hasTable = (name) =>
	!!db.prepare(`SELECT 1 FROM sqlite_master WHERE type='table' AND name=?`).get(name);
const hasColumn = (table, col) =>
	db.prepare(`SELECT 1 FROM pragma_table_info(?) WHERE name=?`).get(table, col) !== undefined;

const isV3 = hasColumn('lem', 'etymon_rid');
console.log(`schema: ${isV3 ? 'v3 (typed edges)' : 'v2 (origin/link/derivation)'}`);

const ids = new IdIndex(
	new Uint8Array(db.prepare('SELECT data FROM ids').get().data),
	db.prepare('SELECT id FROM ids_misc ORDER BY rank').all().map((r) => r.id)
);
const idOf = (rid) => (rid == null ? null : ids.idOf(rid));

// ---- per-node structural row --------------------------------------------------------------

const lemCols = isV3
	? 'rowid AS rid, origin_rid, link_rid, etymon_rid, counts, flags'
	: 'rowid AS rid, origin_rid, link_rid, counts, flags';
const lems = db.prepare(`SELECT ${lemCols} FROM lem`).all();

const KIND_NAME = { 0: null, 1: 'reflex', 2: 'variant', 3: 'borrowed', 4: 'unlinked' };

const parent = {};
const status = {};
const counts = {};
const parentRidOf = new Map(); // rid → parent rid (for root walk)

for (const l of lems) {
	const id = idOf(l.rid);
	const rel = l.flags & 7;
	let target;
	if (isV3) {
		target = l.origin_rid;
	} else {
		// legacy immediate-parent: variant/borrowed rows follow variant_of (link_rid) when set
		target = (rel === 2 || rel === 3) && l.link_rid ? l.link_rid : l.origin_rid;
	}
	if (target != null) parentRidOf.set(l.rid, target);
	parent[id] = target != null ? { target: idOf(target), kind: KIND_NAME[rel] ?? String(rel) } : null;
	status[id] = {
		kind: rel === 4 ? 'unlinked' : (relationName(l.flags) ?? 'none'),
		ocr: l.flags & 8 ? 1 : 0,
		section: l.flags & 16 ? 1 : 0,
		loan: l.flags & 32 ? 1 : 0
	};
	if (l.counts != null) counts[id] = l.counts;
}

// ---- attestation-tree root (entry membership) --------------------------------------------

const rootMemo = new Map();
function rootOf(rid) {
	const seen = [];
	let cur = rid;
	while (cur != null && !rootMemo.has(cur)) {
		seen.push(cur);
		const p = parentRidOf.get(cur);
		if (p == null || seen.includes(p)) break; // root or cycle guard
		cur = p;
	}
	const root = rootMemo.get(cur) ?? cur;
	for (const s of seen) rootMemo.set(s, root);
	return root;
}
const root = {};
for (const l of lems) root[idOf(l.rid)] = idOf(rootOf(l.rid));

// v3 self-check: materialized etymon_rid must equal the walk (for nodes that have one)
if (isV3) {
	let bad = 0;
	for (const l of lems) {
		const expected = l.origin_rid == null ? null : rootOf(l.rid);
		if ((l.etymon_rid ?? null) !== (expected === l.rid ? null : expected)) bad++;
	}
	if (bad) console.error(`WARNING: ${bad} etymon_rid values disagree with the parent walk`);
}

// ---- entries listing ---------------------------------------------------------------------

const entryPred = isV3
	? `origin_rid IS NULL AND (flags & 7) != 4 AND link_rid IS NULL`
	: `origin_rid IS NULL AND (flags & 7) != 4 AND (link_rid IS NULL OR (flags & 7) IN (2, 3))`;
const entries = db
	.prepare(`SELECT rowid AS rid FROM lem WHERE ${entryPred} ORDER BY ord`)
	.all()
	.map((r) => idOf(r.rid));

// ---- alignment digest --------------------------------------------------------------------

// Digest the DECODED per-position symbol strings, not the raw blob: cell/pair/context/symbol
// ids are interned per build (frequency-ranked cells), so raw blobs are not comparable.
const symbol = new Map(db.prepare('SELECT id, value FROM symbols').all().map((r) => [r.id, r.value]));
const pair = new Map(
	db.prepare('SELECT id, etymon_sid, reflex_sid, change_sid FROM align_pair').all()
		.map((r) => [r.id, [r.etymon_sid, r.reflex_sid, r.change_sid]])
);
const context = new Map(
	db.prepare('SELECT id, prev_sid, next_sid FROM align_context').all()
		.map((r) => [r.id, [r.prev_sid, r.next_sid]])
);
const cells = readCellDict(new Uint8Array(db.prepare('SELECT data FROM cells').get().data));
const alignDigest = {};
for (const r of db.prepare('SELECT form_rid, segs FROM alignment').all()) {
	const parts = [];
	for (const cellId of readVarints(new Uint8Array(r.segs))) {
		const c = cells[cellId - 1];
		const p = pair.get(c.pairId);
		const x = context.get(c.ctxId);
		parts.push([...p.map((s) => symbol.get(s)), ...x.map((s) => symbol.get(s))].join('\u0001'));
	}
	alignDigest[idOf(r.form_rid)] = createHash('sha1')
		.update(parts.join('\u0002'))
		.digest('hex')
		.slice(0, 16);
}

// ---- graph edges (raw; interpreted by the comparator) ------------------------------------

let graphEdges;
if (isV3) {
	graphEdges = db
		.prepare('SELECT child_rid, parent_rid, kind, rank, pos, note FROM edges ORDER BY rowid')
		.all()
		.map((e) => ({
			child: idOf(e.child_rid),
			parent: idOf(e.parent_rid),
			kind: e.kind,
			rank: e.rank,
			pos: e.pos,
			note: e.note ?? null
		}));
} else {
	graphEdges = db
		.prepare('SELECT child_rid, parent_rid FROM derivation ORDER BY rowid')
		.all()
		.map((e) => ({ child: idOf(e.child_rid), parent: idOf(e.parent_rid) }));
}

// ---- write -------------------------------------------------------------------------------

const dump = {
	schema: isV3 ? 'v3' : 'v2',
	nodeCount: lems.length,
	parent,
	root,
	status,
	counts,
	entries,
	alignDigest,
	graphEdges
};
writeFileSync(outPath, JSON.stringify(dump));
console.log(
	`wrote ${outPath}: ${lems.length} nodes, ${entries.length} entries, ` +
		`${Object.keys(alignDigest).length} aligned forms, ${graphEdges.length} graph edges`
);
