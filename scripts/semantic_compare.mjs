#!/usr/bin/env node
/**
 * semantic_compare.mjs — diff two semantic_parity.mjs dumps (v2 baseline vs v3 edge-model)
 * and verify that every divergence belongs to an enumerated, counted waiver class:
 *
 *   W1 cross-entry variants (8): rank-1 becomes the etymon-side reflex edge; parent and root
 *      change to the row's own entry (the contradictory pointer is now a rank-2 review edge).
 *   W2 borrowed→variant kind (≈122): variants of borrowed siblings report kind 'variant';
 *      parent unchanged; their former parents may lose the loan-source flag.
 *   W3 dialect un-merges: rows whose v2 dialect-dedup collapsed distinct-parent copies now
 *      stay separate (v3-only node ids that were v2 aliases); affected entries' counts may
 *      shift by the number of un-merged reflexes.
 *   W4 alignment waivers: variant chains gaining/re-anchoring alignments (aligned_parent).
 *   W5 FLAG_HAS_ALT is new in v3 (bit 64) — masked out of flag comparison.
 *
 *   node scripts/semantic_compare.mjs v2-dump.json v3-dump.json
 */
import { readFileSync } from 'node:fs';

const [aPath, bPath] = process.argv.slice(2);
const v2 = JSON.parse(readFileSync(aPath, 'utf8'));
const v3 = JSON.parse(readFileSync(bPath, 'utf8'));
if (v2.schema !== 'v2' || v3.schema !== 'v3') {
	console.error(`expected v2 + v3 dumps, got ${v2.schema} + ${v3.schema}`);
	process.exit(2);
}

let failures = 0;
const fail = (m) => {
	failures++;
	console.error(`FAIL: ${m}`);
};
const ok = (m) => console.log(`ok: ${m}`);

// ---- node sets (W3) -------------------------------------------------------

const v2Nodes = new Set(Object.keys(v2.parent));
const v3Nodes = new Set(Object.keys(v3.parent));
const unmerged = [...v3Nodes].filter((n) => !v2Nodes.has(n));
const vanished = [...v2Nodes].filter((n) => !v3Nodes.has(n));
if (vanished.length) fail(`${vanished.length} v2 nodes missing in v3: ${vanished.slice(0, 5)}`);
ok(`node sets: +${unmerged.length} dialect un-merges (W3), 0 vanished`);
const unmergedSet = new Set(unmerged);

// ---- parent + kind maps (W1, W2) ------------------------------------------

let parentDiff = [];
let kindB2V = 0;
let kindV2R = 0;
let otherKindDiff = [];
for (const id of v2Nodes) {
	const a = v2.parent[id];
	const b = v3.parent[id];
	if (!a && !b) continue;
	if (!a !== !b) {
		parentDiff.push(id);
		continue;
	}
	if (a.target !== b.target) parentDiff.push(id);
	if (a.kind !== b.kind) {
		if (a.kind === 'borrowed' && b.kind === 'variant') kindB2V++;
		else if (a.kind === 'variant' && b.kind === 'reflex') kindV2R++;
		else otherKindDiff.push([id, a.kind, b.kind]);
	}
}
if (parentDiff.length > 8) fail(`${parentDiff.length} parent changes (> 8 cross-entry waivers): ${parentDiff.slice(0, 5)}`);
else ok(`parent map: ${parentDiff.length} changes, all within the W1 cross-entry budget of 8`);
if (otherKindDiff.length) fail(`unexpected kind changes: ${JSON.stringify(otherKindDiff.slice(0, 5))}`);
else ok(`kind map: ${kindB2V} borrowed→variant (W2), ${kindV2R} variant→reflex (W1)`);

// ---- root map (entry membership) ------------------------------------------

const w1 = new Set(parentDiff);
let rootDiff = [];
for (const id of v2Nodes) {
	if ((v2.root[id] ?? null) !== (v3.root[id] ?? null)) rootDiff.push(id);
}
const rootOutside = rootDiff.filter((id) => !w1.has(id));
if (rootOutside.length) fail(`${rootOutside.length} root changes outside W1: ${rootOutside.slice(0, 5)}`);
else ok(`root map: ${rootDiff.length} changes, all W1 rows`);

// ---- status/flags (W2 loan-source fallout, W5 mask) ------------------------

// parents that may lose the loan flag: v2 parents of the borrowed→variant rows
const w2Parents = new Set();
for (const id of v2Nodes) {
	const a = v2.parent[id];
	const b = v3.parent[id];
	if (a && b && a.kind === 'borrowed' && b.kind === 'variant') w2Parents.add(a.target);
}
let flagDiff = [];
for (const id of v2Nodes) {
	const a = v2.status[id];
	const b = v3.status[id];
	if (!a || !b) continue;
	const kindWaived = w1.has(id) || (a.kind === 'borrowed' && b.kind === 'variant');
	if (a.kind !== b.kind && !kindWaived) flagDiff.push([id, 'kind', a.kind, b.kind]);
	if (a.ocr !== b.ocr) flagDiff.push([id, 'ocr']);
	if (a.section !== b.section) flagDiff.push([id, 'section']);
	if (a.loan !== b.loan && !w2Parents.has(id)) flagDiff.push([id, 'loan']);
}
if (flagDiff.length) fail(`${flagDiff.length} flag diffs outside waivers: ${JSON.stringify(flagDiff.slice(0, 5))}`);
else ok(`status/flags identical outside waivers (${w2Parents.size} W2 parents allowed loan-flag changes)`);

// ---- entries listing -------------------------------------------------------

{
	const a = new Set(v2.entries);
	const b = new Set(v3.entries);
	const onlyA = v2.entries.filter((e) => !b.has(e));
	const onlyB = v3.entries.filter((e) => !a.has(e));
	if (onlyA.length || onlyB.length)
		fail(`entries membership: -${onlyA.length} +${onlyB.length} (${onlyA.slice(0, 3)} / ${onlyB.slice(0, 3)})`);
	else {
		// W6: the deterministic-join fix in make_cldf relocates reconciled rows in the CLDF file,
		// permuting the (semantically arbitrary) file-order listing. Membership must be exact.
		let moved = 0;
		for (let i = 0; i < v2.entries.length; i++) if (v2.entries[i] !== v3.entries[i]) moved++;
		ok(`entries membership identical (${v2.entries.length}); ${moved} positions permuted (W6, CLDF-level)`);
	}
}

// ---- per-entry counts (W3 fallout) ----------------------------------------

// entries that may gain counts: roots of un-merged rows, plus W1 rows' new entries (a
// cross-entry variant becoming a rank-1 reflex increments its entry's reflex_count)
const w3Entries = new Set(unmerged.map((id) => v3.root[id]).filter(Boolean));
for (const id of w1) if (v3.root[id]) w3Entries.add(v3.root[id]);
let countDiff = [];
for (const id of Object.keys(v2.counts)) {
	if ((v2.counts[id] ?? null) !== (v3.counts[id] ?? null) && !w3Entries.has(id)) countDiff.push(id);
}
if (countDiff.length) fail(`${countDiff.length} count changes outside W3 entries: ${countDiff.slice(0, 5)}`);
else ok(`per-entry counts identical outside ${w3Entries.size} W3-affected entries`);

// ---- alignment digests (W4) ------------------------------------------------

let alignDiff = [];
for (const id of new Set([...Object.keys(v2.alignDigest), ...Object.keys(v3.alignDigest)])) {
	if ((v2.alignDigest[id] ?? null) !== (v3.alignDigest[id] ?? null)) alignDiff.push(id);
}
// W4 budget: 784 gains + 37 re-anchors measured at the data layer, plus W3 un-merges that align
const budget = 784 + 37 + unmerged.length + w1.size;
if (alignDiff.length > budget) fail(`${alignDiff.length} alignment diffs (> W4 budget ${budget}): ${alignDiff.slice(0, 5)}`);
else ok(`alignment digests: ${alignDiff.length} diffs within W4 budget ${budget}`);

// ---- graph-edge accounting -------------------------------------------------

// every v2 derivation pair must be: shipped in v3 (any kind), or deduped against the child's
// v3 rank-1 parent, or re-pointed by a dialect un-merge
const v3Pairs = new Set(v3.graphEdges.map((e) => `${e.child}|${e.parent}`));
let unaccounted = [];
let deduped = 0;
for (const e of v2.graphEdges) {
	const key = `${e.child}|${e.parent}`;
	if (v3Pairs.has(key)) continue;
	const p = v3.parent[e.child];
	if (p && p.target === e.parent) {
		deduped++;
		continue;
	}
	unaccounted.push(key);
}
if (unaccounted.length) fail(`${unaccounted.length} v2 derivation edges unaccounted: ${unaccounted.slice(0, 5)}`);
else ok(`graph edges: all ${v2.graphEdges.length} v2 pairs accounted (${deduped} deduped into rank-1, ${v3.graphEdges.length} shipped typed)`);

console.log(failures ? `\n${failures} FAILURES` : '\nSEMANTIC PARITY HOLDS');
process.exit(failures ? 1 : 0);
