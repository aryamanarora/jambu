import { segmentFeatures, segmentKey } from './phonology';
import type { Language } from './types';
import { DEFAULT_SOUND_FILTERS, FILTER_LABELS, readSoundFilters, soundSearch, summarizeSounds, type SoundFilters, type SoundObservation } from './soundExplorer';

export const INPUT_FACET_GROUPS: Array<{ label: string; options: Array<[string, string]> }> = [
	{ label: 'Sound properties', options: [
		['sound', 'Target sound sequence'], ['context', 'Full sequence, including context'], ['shape', 'Consonant / vowel sequence'],
		['place', 'Place of articulation'], ['manner', 'Manner of articulation'],
		['voicing', 'Voicing'], ['aspiration', 'Aspiration']
	] },
	{ label: 'Form properties', options: [
		['accent', 'Accent class'], ['syllables', 'Syllable count'],
		['weightPattern', 'Syllable weight pattern'], ['quantityPattern', 'Vowel quantity pattern'],
		['reconstruction', 'Starred / unstarred headword'],
		['weight', 'Matched syllable weight'], ['quantity', 'Matched nucleus quantity'],
		['closed', 'Matched syllable closure']
	] }
];
export const INPUT_FACETS: Array<[string, string]> = [
	['none', 'Keep all inputs together'], ...INPUT_FACET_GROUPS.flatMap(group => group.options)
];
export const inputFacetLabel = (facet: string) => INPUT_FACETS.find(([key]) => key === facet)?.[1] ?? INPUT_FACETS[0][1];
export const OUTCOME_GROUPS = [['segments', 'Aligned sound sequence'], ['accent', 'Accent position class'], ['tone', 'Tone / accent type'], ['syllables', 'Syllable count'], ['delta', 'Syllables gained or lost'], ['place', 'Place of articulation'], ['manner', 'Manner of articulation']];
export const CONDITIONS: Array<{ key: keyof SoundFilters; label: string; values: string[][] }> = [
	{ key: 'accent', label: 'Accent class', values: [['barytone','Barytone'],['oxytone','Oxytone'],['unknown','Unmarked / unknown'],['svarita','Svarita'],['multiple','Multiple marks']] },
	{ key: 'syllables', label: 'Syllable count', values: [['1','1'],['2','2'],['3','3'],['4+','4+'],['unknown','Unknown']] },
	{ key: 'weight', label: 'Matched syllable weight', values: [['light','Light'],['heavy','Heavy']] },
	{ key: 'quantity', label: 'Matched nucleus quantity', values: [['short','Short'],['long','Long']] },
	{ key: 'closed', label: 'Matched syllable closure', values: [['open','Open'],['closed','Closed']] },
	{ key: 'relative', label: 'Position relative to accent', values: [['0','Accented syllable'],['-1','Immediately before'],['1','Immediately after'],['pre','Before'],['post','After'],['unknown','Unknown']] },
	{ key: 'position', label: 'Matched syllable position', values: [['1','First'],['2','Second'],['final','Final'],['unknown','Unknown']] },
	{ key: 'cluster', label: 'Consonant structure', values: [['singleton','Singleton'],['geminate','Geminate'],['cluster','Cluster']] },
	{ key: 'reconstruction', label: 'Ancestor headword', values: [['reconstructed','Starred'],['unstarred','Unstarred']] },
	{ key: 'era', label: 'Ancestor era', values: ['Early-Vedic','Late-Vedic','Epic','Classical','Medieval'].map(s=>[s,s]) }
];

export interface StudyState extends SoundFilters {
	entry: string;
	langs: string; facet: string; groupBy: string; mapGroup: string;
	detail: string; cellInput: string;
	totalMin: string; totalMax: string; outcomeMin: string; outcomeMax: string;
}
export const LANGUAGE_COUNT_FIELDS = ['totalMin', 'totalMax', 'outcomeMin', 'outcomeMax'] as const;
export type LanguageCountFilters = Pick<StudyState, typeof LANGUAGE_COUNT_FIELDS[number]>;
export const DEFAULT_STUDY: StudyState = { ...DEFAULT_SOUND_FILTERS, view: 'table', entry: '', langs: '', facet: 'none', groupBy: 'segments', mapGroup: '', detail: '', cellInput: '', totalMin: '', totalMax: '', outcomeMin: '', outcomeMax: '' };
export function readStudy(params: URLSearchParams): StudyState {
	const old = readSoundFilters(params);
	const state = { ...DEFAULT_STUDY, ...old };
	for (const key of ['entry','langs','facet','groupBy','mapGroup','detail','cellInput'] as const) state[key] = params.get(key) ?? DEFAULT_STUDY[key];
	for (const key of LANGUAGE_COUNT_FIELDS) {
		const value = params.get(key)?.trim() ?? '';
		state[key] = /^\d+$/.test(value) && Number.isSafeInteger(Number(value)) ? String(Number(value)) : '';
	}
	state.view = old.view === 'map' ? 'map' : 'table';
	if (old.view === 'compare' && !params.has('facet')) state.facet = 'accent';
	if (old.view === 'evidence') state.detail = old.l || '*';
	if (old.l && !state.langs) state.langs = old.l;
	state.l = '';
	if (!INPUT_FACETS.some(([key])=>key === state.facet)) state.facet = 'none';
	if (!OUTCOME_GROUPS.some(([key])=>key === state.groupBy)) state.groupBy = 'segments';
	return state;
}
export function studySearch(state: StudyState): string {
	const params = new URLSearchParams(soundSearch(state));
	for (const [key,value] of Object.entries(state)) if (value === DEFAULT_STUDY[key as keyof StudyState] || value === '') params.delete(key);
	return params.toString();
}
export function selectedLanguages(state: Pick<StudyState,'langs'>): string[] { return state.langs ? state.langs.split('|').filter(Boolean) : []; }
export function queryKey(state: StudyState): string {
	const { view, mapGroup, detail, cellInput, r, text, unit, ...query } = state;
	return JSON.stringify(query);
}
export function loadKey(state: StudyState): string {
	const { facet, groupBy, langs, totalMin, totalMax, outcomeMin, outcomeMax, ...query } = JSON.parse(queryKey(state));
	return JSON.stringify(query);
}

/** Count distinct descendant forms across all input groups, before language thresholds. */
export function languageOutcomeCounts(rows: SoundObservation[]): Map<string, number> {
	const forms = new Map<string, Set<string>>();
	for (const { form } of rows) {
		if (!forms.has(form.language)) forms.set(form.language, new Set());
		forms.get(form.language)!.add(form.id);
	}
	return new Map([...forms].map(([id, ids]) => [id, ids.size]));
}
export function matchesLanguageCounts(language: Pick<Language, 'lemma_count'>, outcomes: number | undefined, filters: LanguageCountFilters): boolean {
	const inRange = (count: number | undefined, min: string, max: string) => count == null || ((!min || count >= Number(min)) && (!max || count <= Number(max)));
	return inRange(language.lemma_count, filters.totalMin, filters.totalMax) && inRange(outcomes, filters.outcomeMin, filters.outcomeMax);
}
export function languageCountError(filters: LanguageCountFilters): string {
	for (const [label, min, max] of [['Total forms', filters.totalMin, filters.totalMax], ['Outcome forms', filters.outcomeMin, filters.outcomeMax]]) {
		for (const value of [min, max]) if (value && (!/^\d+$/.test(value) || !Number.isSafeInteger(Number(value)))) return `${label}: enter a whole number of zero or more.`;
		if (min && max && Number(min) > Number(max)) return `${label}: minimum must not exceed maximum.`;
	}
	return '';
}
export function queryFilters(state: StudyState): Partial<SoundFilters> {
	const result: Record<string,string> = {};
	for (const key of Object.keys(FILTER_LABELS)) if (!['r','text','l'].includes(key) && state[key as keyof StudyState]) result[key] = state[key as keyof StudyState];
	return result;
}
export function conditionLabel(key: string, value: string): string {
	const condition = CONDITIONS.find(c=>c.key === key);
	return `${condition?.label ?? FILTER_LABELS[key] ?? key}: ${condition?.values.find(([v])=>v === value)?.[1] ?? value}`;
}

const names: Record<string,string> = { unknown: 'Unknown', barytone: 'Barytone', oxytone: 'Oxytone', svarita: 'Svarita', multiple: 'Multiple marks', unmarked: 'Unmarked / unknown', light: 'Light', heavy: 'Heavy' };
export const categoryLabel = (value: string) => names[value] ?? value;
function segmentProperty(o: SoundObservation, ancestor: boolean, property: 'place' | 'manner' | 'shape' | 'voicing' | 'aspiration'): string {
	const segments = o.form.columns.filter(c => c.pos >= o.pos && c.pos <= (o.endPos ?? o.pos)).map(c => ancestor ? c.etymonSeg : c.reflexSeg).filter(Boolean);
	if (!segments.length) return '∅';
	return segments.map(s => {
		const f = segmentFeatures(s);
		if (property === 'shape') return f.kind;
		if (f.kind === '?') return 'unknown';
		if (property === 'voicing') return f.voiced ? 'voiced' : 'voiceless';
		if (property === 'aspiration') return f.kind === 'V' ? 'vowel' : f.aspirated ? 'aspirated' : 'unaspirated';
		return f.kind === 'V' ? 'vowel' : f[property] || 'unknown';
	}).join(property === 'shape' ? '' : ' → ');
}
export function inputCategory(o: SoundObservation, facet: string): string {
	const a = o.form.ancestor;
	if (facet === 'sound') return o.sound;
	if (facet === 'context') return o.form.columns
		.filter(c => c.pos >= (o.contextStart ?? o.pos) && c.pos <= (o.contextEnd ?? o.endPos ?? o.pos))
		.map(c => segmentKey(c.etymonSeg)).join('');
	if (facet === 'accent') return a.accentClass;
	if (facet === 'syllables') return a.count == null ? 'unknown' : `${a.count} syllable${a.count === 1 ? '' : 's'}`;
	if (facet === 'weightPattern') return a.count != null ? a.weightPattern : 'unknown';
	if (facet === 'quantityPattern') return a.count != null ? a.quantityPattern : 'unknown';
	if (facet === 'reconstruction') return o.form.parentWord.trim().startsWith('*') ? 'Starred' : 'Unstarred';
	const syllable = a.count != null && o.syllable != null ? a.syllables[o.syllable] : null;
	if (facet === 'weight') return syllable?.weight ?? 'unknown';
	if (facet === 'quantity') return syllable ? syllable.long ? 'Long' : 'Short' : 'unknown';
	if (facet === 'closed') return syllable ? syllable.closed ? 'Closed' : 'Open' : 'unknown';
	if (facet === 'place' || facet === 'manner' || facet === 'shape' || facet === 'voicing' || facet === 'aspiration') return segmentProperty(o,true,facet);
	return 'all';
}
export function outcomeCategory(o: SoundObservation, grouping: string): string {
	const m = o.form.modern;
	if (grouping === 'accent') return m.accentClass;
	if (grouping === 'tone') {
		if (m.accentClass === 'unknown') return 'unknown';
		if (m.accentType === 'multiple') return 'multiple';
		const mark = m.accentType.replace('mora-', 'Mora ');
		return `${mark} · ${m.notation}`;
	}
	if (grouping === 'syllables') return m.count == null ? 'unknown' : `${m.count} syllable${m.count === 1 ? '' : 's'}`;
	if (grouping === 'delta') {
		if (m.count == null || o.form.ancestor.count == null) return 'unknown';
		const delta = m.count - o.form.ancestor.count;
		return delta === 0 ? 'Same count' : `${Math.abs(delta)} ${delta > 0 ? 'gained' : 'lost'}`;
	}
	if (grouping === 'place' || grouping === 'manner') return o.outcome === '?' ? '?' : segmentProperty(o,false,grouping);
	return o.outcome;
}
export interface StudyObservation extends SoundObservation { input: string; alignedOutcome: string }
export function groupStudy(rows: SoundObservation[], state: StudyState): StudyObservation[] {
	return rows.map(o => ({ ...o, alignedOutcome: o.outcome, input: inputCategory(o,state.facet), outcome: outcomeCategory(o,state.groupBy) }));
}
export function inputColumns(rows: StudyObservation[]): string[] {
	const preferred = ['all','barytone','oxytone','svarita','multiple','unknown'];
	return [...new Set(rows.map(o=>o.input))].sort((a,b) => {
		if (preferred.includes(a) && preferred.includes(b)) return preferred.indexOf(a)-preferred.indexOf(b);
		if (a === 'unknown' || b === 'unknown') return a === 'unknown' ? 1 : -1;
		return a.localeCompare(b, undefined, { numeric: true });
	});
}
export function buildMatrix(rows: StudyObservation[], unit: SoundFilters['unit']) {
	const cells = new Map<string,Map<string,StudyObservation[]>>();
	for (const o of rows) {
		if (!cells.has(o.form.language)) cells.set(o.form.language,new Map());
		const row = cells.get(o.form.language)!;
		if (!row.has(o.input)) row.set(o.input,[]);
		row.get(o.input)!.push(o);
	}
	return new Map([...cells].map(([lang,groups]) => [lang,new Map([...groups].map(([group,items])=>[group,summarizeSounds(items,unit)]))]));
}
