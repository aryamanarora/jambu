/** Descriptive features of Jambu's normalized transcription, never inferred sound laws.
 * Shared by the explorer, evidence view and offline checks. Keep original alignment positions:
 * several old cells may jointly spell one grapheme, and one cell may contain a diphthong.
 */
export interface SegmentFeatures {
	key: string;
	kind: 'V' | 'C' | '?';
	long: boolean;
	nasal: boolean;
	aspirated: boolean;
	place: string;
	manner: string;
	voiced: boolean;
}
const VOWELS = 'aeiouæɑɒɪʊəɛεɔɨɘɜɐʌɯɤœøʉɞɚ';
const CONSONANTS: Record<string, [string, string, boolean]> = {};
for (const [place, groups] of Object.entries({
	labial: ['p', 'bɓ', 'f', 'vβ', 'm', 'w'],
	dental: ['t', 'd', 'sθ', 'zð', 'n', 'rlɾ'],
	retroflex: ['ṭʈ', 'ḍɖ', 'ṣʂ', 'ẓʐ', 'ṇɳ', 'ṛḷɽɭ'],
	palatal: ['cʧč', 'jʤǰɟ', 'śʃɕ', 'źʒʑ', 'ñɲ', 'y'],
	velar: ['k', 'gɡ', 'x', 'ɣ', 'ṅŋ', ''],
	glottal: ['ʔ', '', 'h', 'ɦ', '', '']
})) {
	groups.forEach((letters, i) => {
		for (const c of letters) CONSONANTS[c] = [place, ['stop', 'stop', 'fricative', 'fricative', 'nasal', 'sonorant'][i], i % 2 === 1 || i === 4];
	});
}
for (const c of 'cʧčjʤǰʦʣ') CONSONANTS[c] = [c === 'ʦ' || c === 'ʣ' ? 'dental' : 'palatal', 'affricate', 'jʤǰʣ'.includes(c)];
for (const c of 'ṁṃ') CONSONANTS[c] = ['unspecified', 'nasal', true];
CONSONANTS['ḥ'] = ['glottal', 'fricative', false];

function isNucleus(s: string): boolean {
	const n = s.normalize('NFD');
	return !n.includes('\u032f') && (VOWELS.includes(n[0] ?? '\0') || /^[rl]/.test(n) && /[\u0325\u0329]/.test(n));
}

/** Remove prosody on vowel nuclei only: ś is a consonant, not accented s. */
const keyCache = new Map<string, string>();
export function segmentKey(s: string): string {
	const cached = keyCache.get(s);
	if (cached != null) return cached;
	const key = s.normalize('NFD').replace(/[^\p{M}][\p{M}]*/gu, (g) =>
		isNucleus(g) ? g.replace(/[\u0300\u0301\u0302\u030c\u030b\u030f]/g, '') : g
	).normalize('NFC');
	keyCache.set(s, key);
	return key;
}

const featureCache = new Map<string, SegmentFeatures>();
export function isDetachedNotation(raw: string): boolean {
	return !!raw && /^[\p{M}ʰʱʲʸʷːˈˌ'ʹˊ*#√(){}¹²³°?,]+$/u.test(raw);
}
export function segmentFeatures(raw: string, old = false): SegmentFeatures {
	const cacheKey = `${old}:${raw}`;
	const cached = featureCache.get(cacheKey);
	if (cached) return cached;
	const key = segmentKey(raw);
	const n = key.normalize('NFD');
	const nucleus = isNucleus(n);
	const base = key.replace(/[ʰʱːʲʸʷ]/g, '').normalize('NFC');
	const c = CONSONANTS[base] ?? CONSONANTS[base[0]];
	const features: SegmentFeatures = {
		key, kind: nucleus ? 'V' : c ? 'C' : '?',
		long: /[\u0304ː]/.test(n) || old && /^(ai|au|e|o)$/.test(n),
		nasal: n.includes('\u0303'), aspirated: /[ʰʱ]/.test(raw),
		place: c?.[0] ?? '', manner: c?.[1] ?? '', voiced: nucleus || (c?.[2] ?? false)
	};
	featureCache.set(cacheKey, features);
	return features;
}

export interface Syllable {
	start: number; end: number; nucleus: number; long: boolean;
	weight: 'light' | 'heavy'; closed: boolean; accent: string; mora: number | null;
}
export interface Prosody {
	syllables: Syllable[];
	count: number | null;
	accentPosition: number | null;
	accentFromRight: number | null;
	accentClass: 'barytone' | 'oxytone' | 'unknown' | 'multiple' | 'svarita';
	accentType: string;
	notation: string;
	quantityPattern: string;
	weightPattern: string;
	issues: string[];
	segmentSyllables: Array<number | null>;
}

function notationFor(old: boolean, sources: string[]): string {
	if (old) return 'OIA';
	const systems = new Set<string>();
	for (const s of sources) {
		if (s === 'liljegren') systems.add('Palula contours');
		else if (s === 'degener-shina2008') systems.add('Gilgit acute/grave');
		else if (s === 'CDIAL') systems.add('Turner stress/tone');
	}
	return systems.size === 1 ? [...systems][0] : systems.size > 1 ? 'Mixed notation' : 'Uninterpreted notation';
}

export function analyzeProsody(tokens: string[], options: { old?: boolean; sources?: string[]; word?: string } = {}): Prosody {
	const old = options.old ?? false;
	const notation = notationFor(old, options.sources ?? []);
	// Grapheme ownership survives combining marks split into their own legacy alignment cells.
	const gs: Array<{ text: string; owners: number[] }> = [];
	tokens.forEach((t, owner) => {
		for (const c of t.normalize('NFD')) {
			if (/\p{M}/u.test(c) && gs.length) {
				gs[gs.length - 1].text += c;
				if (!gs[gs.length - 1].owners.includes(owner)) gs[gs.length - 1].owners.push(owner);
			} else gs.push({ text: c, owners: [owner] });
		}
	});
	const issues: string[] = [];
	if (/\s|[\/,;=()]/.test(options.word ?? tokens.join(''))) issues.push('multiword-or-alternatives');
	const vs: Array<{ start: number; end: number; long: boolean; accent: string; mora: number | null }> = [];
	for (let i = 0; i < gs.length; i++) {
		if (!isNucleus(gs[i].text)) continue;
		let end = i;
		if (old && gs[i].text[0] === 'a' && !gs[i].text.includes('\u0304') && i + 1 < gs.length && /^[iu]/.test(gs[i + 1].text)) end++;
		const text = gs.slice(i, end + 1).map(g => g.text).join('');
		const long = /\u0304/.test(text) || old && ('eo'.includes(text[0]) || end > i) || gs[end + 1]?.text === 'ː';
		let accent = text.includes('\u0301') ? 'acute' : text.includes('\u0300') ? 'grave' : text.includes('\u0302') ? 'falling' : text.includes('\u030c') ? 'rising' : '';
		let mora: number | null = null;
		if (old && accent === 'grave') accent = 'svarita';
		if (notation === 'Palula contours' && long) mora = accent === 'falling' ? 1 : accent === 'rising' ? 2 : null;
		if (notation === 'Gilgit acute/grave' && long) mora = accent === 'grave' ? 1 : accent === 'acute' ? 2 : null;
		if (accent && !long && (notation === 'Palula contours' || notation === 'Gilgit acute/grave')) mora = 1;
		vs.push({ start: i, end, long, accent, mora });
		i = end;
	}
	// Stress signs precede an onset, not necessarily its nucleus.
	for (let i = 0; i < gs.length; i++) {
		if (!/[ˈʹ'ˊ]/.test(gs[i].text)) continue;
		const v = vs.find(v => v.start > i);
		if (v && !v.accent) v.accent = 'stress';
	}
	for (let i = 1; i < vs.length; i++) {
		const between = gs.slice(vs[i - 1].end + 1, vs[i].start).filter(g => !/^[ːˈʹ'ˊ]$/.test(g.text));
		if (!between.length) issues.push('vowel-sequence-needs-reading');
	}
	if (!vs.length) issues.push('no-readable-nucleus');
	if (gs.some(g => !isNucleus(g.text) && segmentFeatures(g.text.normalize('NFC')).kind === '?' && !/^[\p{M}ʰʱʲʸʷːˈˌʹ'ˊ*#\-\s]+$/u.test(g.text))) issues.push('unrecognized-segment');
	const syllables: Syllable[] = vs.map((v, i) => {
		const after = gs.slice(v.end + 1, vs[i + 1]?.start ?? gs.length);
		const consonants = after.filter(g => segmentFeatures(g.text.normalize('NFC')).kind === 'C');
		const longConsonant = after.some((g, j) => g.text === 'ː' && j > 0 && segmentFeatures(after[j - 1].text.normalize('NFC')).kind === 'C');
		const closed = consonants.length >= (i + 1 < vs.length ? 2 : 1) || longConsonant;
		// Conventional V.CV / VC.CV division. Coda assignment is descriptive and explicit in Help.
		const last = after.findLastIndex(g => segmentFeatures(g.text.normalize('NFC')).kind === 'C');
		const end = i + 1 < vs.length ? last >= 0 ? v.end + last : v.end : gs.length - 1;
		return { start: 0, end, nucleus: v.start, long: v.long, closed, weight: v.long || closed ? 'heavy' : 'light', accent: v.accent, mora: v.mora };
	});
	syllables.forEach((s, i) => s.start = i === 0 ? 0 : syllables[i - 1].end + 1);
	const segmentSyllables: Array<number | null> = tokens.map(() => null);
	syllables.forEach((s, i) => { for (let k = s.start; k <= s.end; k++) for (const owner of gs[k]?.owners ?? []) segmentSyllables[owner] = i; });
	const count = issues.length ? null : syllables.length;
	const accented = syllables.flatMap((s, i) => s.accent ? [i] : []);
	const ai = count != null && accented.length === 1 ? accented[0] : null;
	const svarita = old && accented.length === 1 && syllables[accented[0]].accent === 'svarita';
	return {
		syllables, count, accentPosition: ai == null ? null : ai + 1,
		accentFromRight: ai == null ? null : syllables.length - ai,
		accentClass: accented.length > 1 ? 'multiple' : svarita ? 'svarita' : ai == null ? 'unknown' : ai === syllables.length - 1 ? 'oxytone' : 'barytone',
		accentType: ai == null ? accented.length > 1 ? 'multiple' : 'unmarked' : syllables[ai].mora != null ? `mora-${syllables[ai].mora}` : syllables[ai].accent,
		notation, quantityPattern: syllables.map(s => s.long ? 'L' : 'S').join(''),
		weightPattern: syllables.map(s => s.weight === 'heavy' ? 'H' : 'L').join(''),
		issues: [...new Set(issues)], segmentSyllables
	};
}

export function matchesSound(raw: string, expression: string, old = true): boolean {
	if (!expression) return true;
	if (!expression.startsWith(':')) return segmentKey(raw) === segmentKey(expression);
	const f = segmentFeatures(raw, old);
	return ({ ':V': f.kind === 'V', ':C': f.kind === 'C', ':short': f.kind === 'V' && !f.long,
		':long': f.kind === 'V' && f.long, ':nasal': f.manner === 'nasal', ':stop': f.manner === 'stop',
		':sibilant': /^(s|ś|ṣ|ʃ|ʂ|z|ẓ|ź)$/.test(f.key), ':retroflex': f.place === 'retroflex',
		':aspirated': f.aspirated, ':high': f.kind === 'V' && /^[iuɨɪʊ]/.test(f.key.normalize('NFD'))
	} as Record<string, boolean>)[expression] ?? false;
}

/** All observable segment differences, rather than a first-match historical diagnosis. */
export function segmentChanges(a: string, b: string, old = true): string[] {
	if (!a) return ['add'];
	if (!b) return ['loss'];
	if (segmentKey(a) === segmentKey(b)) return ['kept'];
	const e = segmentFeatures(a, old), r = segmentFeatures(b);
	const out: string[] = [];
	if (e.kind === 'V' && r.kind === 'V') {
		if (e.nasal !== r.nasal) out.push(r.nasal ? 'nasalization' : 'denasalization');
		if (e.long !== r.long) out.push(r.long ? 'lengthening' : 'shortening');
		const quality = (s: string) => segmentKey(s).normalize('NFD').replace(/[\u0304\u0303ː]/g, '');
		if (quality(a) !== quality(b)) out.push('vowel');
	} else if (e.kind === 'C' && r.kind === 'C') {
		if (e.voiced !== r.voiced) out.push(r.voiced ? 'voicing' : 'devoicing');
		if (e.aspirated !== r.aspirated) out.push(r.aspirated ? 'aspiration' : 'deaspiration');
		if (e.place !== r.place) out.push(r.place === 'retroflex' ? 'retroflexion' : 'place');
		if (e.manner !== r.manner) out.push(r.manner === 'nasal' ? 'nasalization' : 'cons');
	}
	return out.length ? out : ['cons'];
}

export interface SoundColumn { pos: number; etymonSeg: string; reflexSeg: string }
export interface SoundEvent { positions: number[]; from: string; to: string; labels: string[] }
/** Group adjacent changed columns for inspection. Labels describe spans, not causal histories. */
export function alignmentEvents(columns: SoundColumn[]): SoundEvent[] {
	const events: SoundEvent[] = [];
	let run: SoundColumn[] = [];
	const flush = () => {
		if (!run.length) return;
		const from = run.map(c => segmentKey(c.etymonSeg)).join('');
		const to = run.map(c => segmentKey(c.reflexSeg)).join('');
		const labels = [...new Set(run.flatMap(c => segmentChanges(c.etymonSeg, c.reflexSeg)).filter(x => x !== 'kept'))];
		events.push({ positions: run.map(c => c.pos), from, to, labels });
		run = [];
	};
	for (const c of columns) {
		if (segmentKey(c.etymonSeg) === segmentKey(c.reflexSeg)) flush(); else run.push(c);
	}
	flush();
	return events;
}
