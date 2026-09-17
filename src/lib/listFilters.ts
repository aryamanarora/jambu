import type { ListParams } from './types';

export type FilterMode = 'entries' | 'forms';

export const ENTRY_TYPES = [
	{ key: 'roots', state: 'rootsOnly', label: 'Roots only', title: 'Show only root nodes — entries not derived from any other etymon' },
	{ key: 'sections', state: 'sectionsOnly', label: 'Section-forms', title: "Show only CDIAL section-forms — numbered derived forms promoted from an entry's header" },
	{ key: 'loans', state: 'loanSourcesOnly', label: 'Loan sources', title: 'Show only loan sources — reflexes that words in other languages were borrowed from' },
	{ key: 'comparisons', state: 'crossFamilyOnly', label: 'Cross-family', title: 'Show only entries linked to another language family by a sourced DEDR or CDIAL comparison' }
] as const;

/** Count the filters represented by LemmaFilters, including an active dialect from the sidebar. */
export function countListFilters(params: ListParams, mode: FilterMode, showLanguage = true): number {
	const keys: (keyof ListParams)[] = ['relaxed', 'form', 'gloss', 'tags', 'source'];
	if (showLanguage) keys.push('origin_lang');
	if (mode === 'entries') keys.push('etymology', ...ENTRY_TYPES.map((type) => type.state));
	else keys.push('dialect', 'origin', 'etymon_lang', 'notes');
	return keys.filter((key) => Boolean(params[key])).length;
}

export function resultRange(count: number, page: number, rows: number, pageSize: number, unit: string): string {
	const from = rows ? (page - 1) * pageSize + 1 : 0;
	const to = rows ? from + rows - 1 : 0;
	return `${from.toLocaleString()}–${to.toLocaleString()} of ${count.toLocaleString()} ${unit}`;
}
