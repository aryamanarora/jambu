import { matchesSound, segmentFeatures, type Prosody } from './phonology';

export const SOUND_CLASSES = [
	[':V', 'Any vowel'], [':short', 'Short vowel'], [':long', 'Long vowel'], [':high', 'High vowel'],
	[':C', 'Any consonant'], [':stop', 'Stop'], [':nasal', 'Nasal consonant'],
	[':sibilant', 'Sibilant'], [':retroflex', 'Retroflex'], [':aspirated', 'Aspirate']
];
export type SoundView = 'table' | 'distribution' | 'map' | 'compare' | 'evidence' | 'help';
export interface SoundFilters {
	p: string; s: string; view: SoundView; unit: 'occurrences' | 'forms' | 'families';
	pv: string; nx: string; accent: string; syllables: string; position: string;
	weight: string; quantity: string; closed: string; relative: string; cluster: string;
	modernSyllables: string; delta: string; modernAccent: string;
	l: string; c: string; dialect: string; source: string; relation: string; era: string; tag: string;
	reconstruction: string; reading: string; r: string; text: string;
}
export const DEFAULT_SOUND_FILTERS: SoundFilters = {
	p: 'Indo-Aryan', s: 'a', view: 'distribution', unit: 'forms',
	pv: '', nx: '', accent: '', syllables: '', position: '', weight: '', quantity: '', closed: '', relative: '', cluster: '',
	modernSyllables: '', delta: '', modernAccent: '', l: '', c: '', dialect: '', source: '', relation: '', era: '', tag: '',
	reconstruction: '', reading: '', r: '', text: ''
};
export const FILTER_LABELS: Record<string, string> = {
	pv: 'Before', nx: 'After', accent: 'Ancestor accent', syllables: 'Ancestor syllables', position: 'Syllable position',
	weight: 'Weight', quantity: 'Vowel quantity', closed: 'Syllable closure', relative: 'Accent distance', cluster: 'Cluster',
	modernSyllables: 'Reflex syllables', delta: 'Syllable change', modernAccent: 'Reflex accent',
	l: 'Language', c: 'Branch', dialect: 'Dialect', source: 'Source', relation: 'Relation', era: 'Ancestor era', tag: 'Morphology tag',
	reconstruction: 'Headword', reading: 'Reading', r: 'Outcome', text: 'Word or gloss'
};
export function readSoundFilters(params: URLSearchParams): SoundFilters {
	const f = { ...DEFAULT_SOUND_FILTERS };
	for (const key of Object.keys(f) as Array<keyof SoundFilters>) {
		const value = params.get(key);
		if (value != null) (f as unknown as Record<string, string>)[key] = value;
	}
	if (!['table', 'distribution', 'map', 'compare', 'evidence', 'help'].includes(f.view)) f.view = 'distribution';
	if (!['occurrences', 'forms', 'families'].includes(f.unit)) f.unit = 'forms';
	return f;
}
export function soundSearch(f: SoundFilters): string {
	const params = new URLSearchParams();
	for (const [key, value] of Object.entries(f)) if (value !== '' && value !== DEFAULT_SOUND_FILTERS[key as keyof SoundFilters]) params.set(key, value);
	return params.toString();
}
export interface SoundSource { id: string; label: string; locator: string }
export interface SoundForm {
	id: string; word: string; gloss: string; language: string; languageName: string; clade: string;
	parentId: string; parentWord: string; familyId: string; relation: string;
	tags: string[]; parentTags: string[]; sources: SoundSource[]; ocr: boolean;
	ancestor: Prosody; modern: Prosody;
	columns: Array<{ pos: number; etymonSeg: string; reflexSeg: string }>;
}
export interface SoundObservation {
	form: SoundForm; pos: number; index: number; sound: string; outcome: string; prev: string; next: string;
	endPos?: number; positions?: number[]; contextStart?: number; contextEnd?: number;
	changes: string[]; syllable: number | null; cluster: 'singleton' | 'geminate' | 'cluster' | 'vowel' | 'unknown';
}

export function numberMatches(n: number | null, value: string): boolean {
	if (!value) return true;
	if (value === 'unknown') return n == null;
	if (n == null) return false;
	if (value.endsWith('+')) return n >= Number(value.slice(0, -1));
	return n === Number(value);
}
export function matchesObservation(o: SoundObservation, f: SoundFilters): boolean {
	const a = o.form.ancestor, m = o.form.modern;
	const sy = a.count != null && o.syllable != null ? a.syllables[o.syllable] : null;
	const old = ['Indo-Aryan', 'OIA', 'PIA'].includes(f.p);
	if (!matchesSound(o.prev, f.pv, old) || !matchesSound(o.next, f.nx, old)) return false;
	if (f.r && o.outcome !== f.r) return false;
	if (f.accent && a.accentClass !== f.accent) return false;
	if (!numberMatches(a.count, f.syllables) || !numberMatches(m.count, f.modernSyllables)) return false;
	if (f.position === 'final' ? !sy || o.syllable !== a.count! - 1 : f.position && !numberMatches(sy ? o.syllable! + 1 : null, f.position)) return false;
	if (f.quantity && (!sy || (sy.long ? 'long' : 'short') !== f.quantity)) return false;
	if (f.weight && (!sy || sy.weight !== f.weight)) return false;
	if (f.closed && (!sy || (sy.closed ? 'closed' : 'open') !== f.closed)) return false;
	const distance = a.accentPosition != null && sy ? o.syllable! + 1 - a.accentPosition : null;
	if (f.relative === 'unknown' ? distance != null : f.relative && (distance == null || f.relative === 'pre' && distance >= 0 || f.relative === 'post' && distance <= 0 || !['pre', 'post'].includes(f.relative) && distance !== Number(f.relative))) return false;
	if (f.cluster && o.cluster !== f.cluster) return false;
	if (f.modernAccent && (f.modernAccent === 'unknown' ? m.accentClass !== 'unknown' : f.modernAccent.startsWith('mora-') ? m.accentType !== f.modernAccent : m.accentClass !== f.modernAccent)) return false;
	const delta = a.count != null && m.count != null ? m.count - a.count : null;
	if (f.delta === 'unknown' ? delta != null : f.delta && (delta == null || f.delta === 'loss' && delta >= 0 || f.delta === 'gain' && delta <= 0 || f.delta === 'same' && delta !== 0)) return false;
	if (f.l && o.form.language !== f.l || f.c && (o.form.clade || '__unclassified__') !== f.c) return false;
	if (f.dialect && !o.form.tags.includes(f.dialect)) return false;
	if (f.source && !o.form.sources.some(s => s.id === f.source)) return false;
	if (f.relation && o.form.relation !== f.relation) return false;
	if (f.era && !o.form.parentTags.includes(f.era)) return false;
	if (f.tag && !o.form.tags.includes(f.tag) && !o.form.parentTags.includes(f.tag)) return false;
	if (f.reconstruction && (o.form.parentWord.trim().startsWith('*') ? 'reconstructed' : 'unstarred') !== f.reconstruction) return false;
	if (f.reading === 'clear' && (a.issues.length || m.issues.length) || f.reading === 'review' && !a.issues.length && !m.issues.length) return false;
	if (f.text && ![o.form.word, o.form.parentWord, o.form.gloss, o.form.id, o.form.parentId].some(s => s.toLowerCase().includes(f.text.toLowerCase()))) return false;
	return true;
}

export interface SoundSummary {
	total: number; occurrences: number; forms: number; families: number;
	outcomes: Array<{ sound: string; weight: number; support: number; percent: number }>;
}
/** Each unit votes once; conflicting outcomes divide its vote equally, independently of citations.
 * Family mode counts a root within each language once, retaining geographical comparability.
 */
export function summarizeSounds(rows: SoundObservation[], unit: SoundFilters['unit']): SoundSummary {
	const units = new Map<string, Set<string>>();
	const forms = new Set<string>(), families = new Set<string>();
	for (const o of rows) {
		forms.add(o.form.id); families.add(o.form.familyId);
		const id = unit === 'occurrences' ? `${o.form.id}:${o.pos}` : unit === 'forms' ? o.form.id : `${o.form.language}:${o.form.familyId}`;
		const set = units.get(id) ?? new Set<string>(); set.add(o.outcome); units.set(id, set);
	}
	const outcomes = new Map<string, { sound: string; weight: number; support: number; percent: number }>();
	for (const set of units.values()) for (const sound of set) {
		const o = outcomes.get(sound) ?? { sound, weight: 0, support: 0, percent: 0 };
		o.weight += 1 / set.size; o.support++; outcomes.set(sound, o);
	}
	return { total: units.size, occurrences: rows.length, forms: forms.size, families: families.size,
		outcomes: [...outcomes.values()].map(o => ({ ...o, percent: units.size ? 100 * o.weight / units.size : 0 })).sort((a, b) => b.weight - a.weight || a.sound.localeCompare(b.sound)) };
}

export function clusterAt(segments: string[], i: number): SoundObservation['cluster'] {
	const kind = segmentFeatures(segments[i]).kind;
	if (kind !== 'C') return kind === 'V' ? 'vowel' : 'unknown';
	let l = i, r = i;
	while (l > 0 && segmentFeatures(segments[l - 1]).kind === 'C') l--;
	while (r + 1 < segments.length && segmentFeatures(segments[r + 1]).kind === 'C') r++;
	return l === r ? /ː/.test(segments[i]) ? 'geminate' : 'singleton' : segments.slice(l, r + 1).every(s => s === segments[i]) ? 'geminate' : 'cluster';
}
