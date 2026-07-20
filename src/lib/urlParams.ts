import type { ListParams } from './types';

/** Read the list filter/sort/page state out of a URL's query string. */
export function paramsFromUrl(sp: URLSearchParams): ListParams {
	const g = (k: string) => sp.get(k) ?? undefined;
	const pageStr = sp.get('page');
	const pageNum = pageStr ? parseInt(pageStr, 10) : 1;
	return {
		lang: g('lang'),
		word: g('word'),
		gloss: g('gloss'),
		notes: g('notes'),
		source: g('source'),
		origin_lang: g('origin_lang'),
		origin: g('origin'),
		clade: g('clade'),
		sort: g('sort'),
		page: Number.isFinite(pageNum) && pageNum > 0 ? pageNum : 1
	};
}

/**
 * Build the query string for a set of changes. Changing a filter/sort resets to page 1
 * (mirrors the old scripts.js behaviour); an explicit `page` update is preserved.
 */
export function buildQuery(
	current: URLSearchParams,
	updates: Record<string, string>,
	resetPage = true
): string {
	const sp = new URLSearchParams(current);
	for (const [k, v] of Object.entries(updates)) {
		if (v === '' || v == null) sp.delete(k);
		else sp.set(k, v);
	}
	if (resetPage && !('page' in updates)) sp.delete('page');
	const s = sp.toString();
	return s ? '?' + s : '?';
}
