/**
 * dbShared.ts — codecs for the compact ("v2") DB schema, shared by the browser query layer,
 * the build/prerender server layer, and scripts/parity_check.mjs.
 *
 * MUST stay in sync with scripts/compact_db.py (the Python encoder). See that file for the
 * schema overview. Everything here is environment-agnostic (no SvelteKit imports).
 */

// ── varints (unsigned LEB128) ───────────────────────────────────────────────

export function readVarints(blob: Uint8Array | null | undefined): number[] {
	if (!blob || blob.length === 0) return [];
	const out: number[] = [];
	let n = 0;
	let shift = 0;
	for (let i = 0; i < blob.length; i++) {
		const b = blob[i];
		n += (b & 0x7f) * 2 ** shift;
		if (b & 0x80) shift += 7;
		else {
			out.push(n);
			n = 0;
			shift = 0;
		}
	}
	return out;
}

/** Decode a sorted delta-encoded varint list (concepts.rids). */
export function readDeltas(blob: Uint8Array | null | undefined): number[] {
	const vals = readVarints(blob);
	let acc = 0;
	return vals.map((v) => (acc += v));
}

// ── id codec ────────────────────────────────────────────────────────────────

const F_ALPHABET = '234567abcdefghijklmnopqrstuvwxyz';
const F_INDEX = new Map([...F_ALPHABET].map((c, i) => [c, i]));

const TAG_NUM = 1,
	TAG_NM = 2,
	TAG_NUML = 3,
	TAG_D = 4,
	TAG_F = 5,
	TAG_MISC = 6;

const NUM_RE = /^(0|[1-9]\d*)$/;
const NM_RE = /^(0|[1-9]\d*)-(0|[1-9]\d*)$/;
const NUML_RE = /^(0|[1-9]\d*)([a-z])$/;
const D_RE = /^d(0|[1-9]\d*)$/;

function writeBig(rec: Uint8Array, offset: number, len: number, value: bigint): boolean {
	for (let i = len - 1; i >= 0; i--) {
		rec[offset + i] = Number(value & 0xffn);
		value >>= 8n;
	}
	return value === 0n;
}

function readBig(rec: Uint8Array, offset: number, len: number): bigint {
	let v = 0n;
	for (let i = 0; i < len; i++) v = (v << 8n) | BigInt(rec[offset + i]);
	return v;
}

/** Encode a lemma id to its 10-byte record; null if the id cannot exist in this DB
 *  (misc ids are resolved through the misc rank map instead). */
export function encodeId(id: string, miscRank: Map<string, number>): Uint8Array | null {
	const rec = new Uint8Array(10);
	if (id.startsWith('f_') && id.length === 15) {
		let n = 0n;
		let ok = true;
		for (const c of id.slice(2)) {
			const v = F_INDEX.get(c);
			if (v === undefined) {
				ok = false;
				break;
			}
			n = (n << 5n) | BigInt(v);
		}
		if (ok) {
			rec[0] = TAG_F;
			writeBig(rec, 1, 9, n);
			return rec;
		}
	}
	let m = NUM_RE.exec(id);
	if (m) {
		rec[0] = TAG_NUM;
		return writeBig(rec, 1, 9, BigInt(id)) ? rec : null;
	}
	m = NM_RE.exec(id);
	if (m) {
		const a = BigInt(m[1]),
			b = BigInt(m[2]);
		if (a < 2n ** 32n && b < 2n ** 32n) {
			rec[0] = TAG_NM;
			writeBig(rec, 1, 4, a);
			writeBig(rec, 5, 4, b);
			return rec;
		}
	}
	m = NUML_RE.exec(id);
	if (m) {
		rec[0] = TAG_NUML;
		if (!writeBig(rec, 1, 8, BigInt(m[1]))) return null;
		rec[9] = m[2].charCodeAt(0);
		return rec;
	}
	m = D_RE.exec(id);
	if (m) {
		rec[0] = TAG_D;
		return writeBig(rec, 1, 9, BigInt(m[1])) ? rec : null;
	}
	const rank = miscRank.get(id);
	if (rank === undefined) return null;
	rec[0] = TAG_MISC;
	writeBig(rec, 1, 9, BigInt(rank));
	return rec;
}

export function decodeIdRecord(data: Uint8Array, offset: number, misc: string[]): string {
	const tag = data[offset];
	switch (tag) {
		case TAG_F: {
			let n = readBig(data, offset + 1, 9);
			const chars: string[] = [];
			for (let i = 0; i < 13; i++) {
				chars.push(F_ALPHABET[Number(n & 31n)]);
				n >>= 5n;
			}
			return 'f_' + chars.reverse().join('');
		}
		case TAG_NUM:
			return readBig(data, offset + 1, 9).toString();
		case TAG_NM:
			return `${readBig(data, offset + 1, 4)}-${readBig(data, offset + 5, 4)}`;
		case TAG_NUML:
			return readBig(data, offset + 1, 8).toString() + String.fromCharCode(data[offset + 9]);
		case TAG_D:
			return 'd' + readBig(data, offset + 1, 9).toString();
		case TAG_MISC:
			return misc[Number(readBig(data, offset + 1, 9))];
		default:
			throw new Error(`bad id record tag ${tag} at ${offset}`);
	}
}

/** The in-memory id table: rowid i (1-based) ↔ the i-th 10-byte record of the sorted array. */
export class IdIndex {
	readonly count: number;
	private data: Uint8Array;
	private misc: string[];
	private miscRank: Map<string, number>;

	constructor(data: Uint8Array, misc: string[]) {
		this.data = data;
		this.misc = misc;
		this.count = data.length / 10;
		this.miscRank = new Map(misc.map((id, i) => [id, i]));
	}

	idOf(rid: number): string {
		if (rid < 1 || rid > this.count) throw new Error(`lemma rowid ${rid} out of range`);
		return decodeIdRecord(this.data, (rid - 1) * 10, this.misc);
	}

	ridOf(id: string): number | null {
		const rec = encodeId(id, this.miscRank);
		if (!rec) return null;
		let lo = 0,
			hi = this.count - 1;
		while (lo <= hi) {
			const mid = (lo + hi) >> 1;
			const cmp = this.compare(mid * 10, rec);
			if (cmp === 0) return mid + 1;
			if (cmp < 0) lo = mid + 1;
			else hi = mid - 1;
		}
		return null;
	}

	private compare(offset: number, rec: Uint8Array): number {
		for (let i = 0; i < 10; i++) {
			const d = this.data[offset + i] - rec[i];
			if (d !== 0) return d;
		}
		return 0;
	}
}

// ── lem flags ───────────────────────────────────────────────────────────────

export const FLAG_OCR = 8;
export const FLAG_SECTION = 16;
export const FLAG_LOAN_SOURCE = 32;
export const FLAG_HAS_ALT = 64;
export const REL_NONE = 0,
	REL_REFLEX = 1,
	REL_VARIANT = 2,
	REL_BORROWED = 3,
	REL_UNLINKED = 4;
/** Typed-edge kind codes in the shipped `edges` table (attestation kinds reuse 1-3). */
export const KIND_COMPONENT = 5,
	KIND_DERIVED = 6;

const RELATION_NAME: (string | null)[] = [null, 'reflex', 'variant', 'borrowed', 'unlinked'];

export function relationName(flags: number): string | null {
	return RELATION_NAME[flags & 7] ?? null;
}

// ── clade masks ─────────────────────────────────────────────────────────────

/** Reconstruct the legacy `clades` string: names of the set bits, alphabetically sorted. */
export function decodeCladeMask(mask: number | null, names: string[]): string | null {
	if (!mask) return null;
	const out: string[] = [];
	// no bitwise ops: masks can exceed 32 bits and JS `&` truncates to 32
	for (let i = 0; i < names.length; i++) if (Math.floor(mask / 2 ** i) % 2 === 1) out.push(names[i]);
	return out.sort().join(',');
}

// ── lem row hydration ───────────────────────────────────────────────────────

/** Column list reconstructing the legacy lemma row shape (aliases `ord` back to "order").
 *  Use with `FROM lem l ${LEM_JOINS}`. */
export const LEM_COLS = `l.rowid AS rid, l.word, l.gloss, l.native, l.phonemic, l.notes,
	l.etymology, l.ord AS ord, l.lang_rid, l.origin_rid, l.etymon_rid, l.link_rid,
	ts.txt AS tags, cs.txt AS cognateset, l.clades_mask, l.counts, l.flags,
	l.cites, l.children`;
export const LEM_JOINS = `LEFT JOIN tagsets ts ON ts.rowid = l.tagset_rid
	LEFT JOIN cogsets cs ON cs.rowid = l.cogset_rid`;

export interface RawLem {
	rid: number;
	word: string | null;
	gloss: string | null;
	native: string | null;
	phonemic: string | null;
	notes: string | null;
	etymology: string | null;
	ord: number;
	lang_rid: number | null;
	origin_rid: number | null;
	etymon_rid: number | null;
	link_rid: number | null;
	tags: string | null;
	cognateset: string | null;
	clades_mask: number | null;
	counts: number | null;
	flags: number;
	cites: Uint8Array | null;
	children: Uint8Array | null;
}

export interface HydrateCtx {
	ids: IdIndex;
	/** languages.rowid → languages.id (the textual language id). */
	langIdOf: (rid: number) => string;
	/** mask_clades names, bit i ↔ names[i]. */
	cladeNames: string[];
}

/** Internal fields carried on hydrated lemmas for follow-up queries (rowid + raw blobs). */
export interface LemInternal {
	rid: number;
	citeIds: number[];
	childRids: number[];
}

export function hydrateLem(row: RawLem, ctx: HydrateCtx): Record<string, unknown> & LemInternal {
	const relation = relationName(row.flags);
	// v3: origin_rid IS the rank-1 edge target (a variant's actual target); link_rid = redirect
	const origin = row.origin_rid ? ctx.ids.idOf(row.origin_rid) : null;
	return {
		rid: row.rid,
		citeIds: readVarints(row.cites),
		childRids: readVarints(row.children),
		id: ctx.ids.idOf(row.rid),
		word: row.word,
		gloss: row.gloss,
		native: row.native,
		phonemic: row.phonemic,
		notes: row.notes ?? '',
		etymology: row.etymology,
		order: row.ord,
		language_id: row.lang_rid != null ? ctx.langIdOf(row.lang_rid) : (null as unknown as string),
		origin_lemma_id: origin,
		etymon_id: row.etymon_rid ? ctx.ids.idOf(row.etymon_rid) : null,
		variant_of: relation === 'variant' ? origin : null,
		redirect_to: row.link_rid ? ctx.ids.idOf(row.link_rid) : null,
		borrowed_from: relation === 'borrowed' ? origin : null,
		tags: row.tags,
		// legacy shape: attested rows (CLDF pass 2) stored '' rather than NULL
		cognateset: row.cognateset ?? (row.origin_rid ? '' : null),
		clades: decodeCladeMask(row.clades_mask, ctx.cladeNames),
		reflex_count: row.counts != null ? row.counts >> 10 : undefined,
		lang_count: row.counts != null ? row.counts & 1023 : undefined,
		relation,
		ocr: row.flags & FLAG_OCR ? 1 : 0,
		hasAlternates: row.flags & FLAG_HAS_ALT ? 1 : 0
	};
}

// ── varint-blob membership (the one SQL UDF both drivers register) ──────────

/** `vin_any(blob, json)` — does the varint blob contain any int of the JSON array?
 *  The parsed set is memoized on the JSON string (the driver calls this once per row). */
export function makeVinAny(): (blob: Uint8Array | null, json: string) => number {
	let lastJson = '';
	let lastSet: Set<number> = new Set();
	return (blob, json) => {
		if (json !== lastJson) {
			lastJson = json;
			lastSet = new Set(JSON.parse(json) as number[]);
		}
		if (!blob || lastSet.size === 0) return 0;
		let n = 0;
		let shift = 0;
		for (let i = 0; i < blob.length; i++) {
			const b = blob[i];
			n += (b & 0x7f) * 2 ** shift;
			if (b & 0x80) shift += 7;
			else {
				if (lastSet.has(n)) return 1;
				n = 0;
				shift = 0;
			}
		}
		return 0;
	};
}

// ── alias lookup ────────────────────────────────────────────────────────────

/** Split an alias/legacy id into its (prefix, M) group form; null if it has no such form. */
export function aliasGroupKey(alias: string): { prefix: string; m: number } | null {
	const i = alias.lastIndexOf('-');
	if (i < 0) return null;
	const mStr = alias.slice(i + 1);
	if (!NUM_RE.test(mStr)) return null;
	return { prefix: alias.slice(0, i), m: parseInt(mStr, 10) };
}

/** Find M in a (ΔM varint, rid varint) group blob; returns the lemma rowid or null. */
export function aliasLookup(data: Uint8Array, m: number): number | null {
	let acc = 0;
	let n = 0;
	let shift = 0;
	let field = 0; // 0 = delta, 1 = rid
	let curM = 0;
	for (let i = 0; i < data.length; i++) {
		const b = data[i];
		n += (b & 0x7f) * 2 ** shift;
		if (b & 0x80) {
			shift += 7;
			continue;
		}
		if (field === 0) {
			acc += n;
			curM = acc;
			field = 1;
		} else {
			if (curM === m) return n;
			if (curM > m) return null;
			field = 0;
		}
		n = 0;
		shift = 0;
	}
	return null;
}

// ── alignment / correspondence blob decoding ────────────────────────────────

/** Decode the single-row `cells` dictionary blob: (pair_id, context_id) per cell id (1-based). */
export function readCellDict(blob: Uint8Array): { pairId: number; ctxId: number }[] {
	const v = readVarints(blob);
	const out: { pairId: number; ctxId: number }[] = [];
	for (let i = 0; i + 1 < v.length; i += 2) out.push({ pairId: v[i], ctxId: v[i + 1] });
	return out;
}

export interface CorrCell {
	cellId: number;
	n: number;
	exampleRid: number;
}

/** Decode a corr_lang2 data blob: repeating (cell_id, n, example_rid) varints. */
export function readCorrCells(blob: Uint8Array): CorrCell[] {
	const v = readVarints(blob);
	const out: CorrCell[] = [];
	for (let i = 0; i + 2 < v.length; i += 3) out.push({ cellId: v[i], n: v[i + 1], exampleRid: v[i + 2] });
	return out;
}
