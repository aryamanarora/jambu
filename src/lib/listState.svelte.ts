/**
 * listState.svelte.ts — reactive filter/sort/paginate state for the list views.
 * Reads state from the URL, re-queries on change, and writes changes back to the URL
 * (client-side navigation) — the SPA equivalent of the old AJAX fragment refresh.
 */
import { page } from '$app/state';
import { goto } from '$app/navigation';
import { base } from '$app/paths';
import { browser } from '$app/environment';
import { paramsFromUrl, buildQuery } from './urlParams';
import { fetchLemmaList, type ListResult } from './query';
import type { ListParams } from './types';

export interface ListState {
	readonly params: ListParams;
	readonly result: ListResult | null;
	readonly loading: boolean;
	readonly error: string | null;
	setFilter: (key: string, value: string) => void;
	setSort: (sortValue: string) => void;
	setPage: (n: number) => void;
}

export function createListState(
	mode: 'reflexes' | 'entries' | 'lexicon',
	opts: { languageId?: string; referenceId?: string; withOrigin?: boolean } = {}
): ListState {
	let result = $state<ListResult | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// `url.searchParams` is off-limits during prerender; the interactive list is client-only anyway,
	// so on the server we render an empty default frame and populate params after hydration.
	const params = $derived(browser ? paramsFromUrl(page.url.searchParams) : {});

	$effect(() => {
		const p = params; // track
		let cancelled = false;
		loading = true;
		error = null;
		fetchLemmaList({
			mode,
			languageId: opts.languageId,
			referenceId: opts.referenceId,
			params: p,
			withOrigin: opts.withOrigin
		})
			.then((r) => {
				if (!cancelled) {
					result = r;
					loading = false;
				}
			})
			.catch((e) => {
				if (!cancelled) {
					error = String(e);
					loading = false;
				}
			});
		return () => {
			cancelled = true;
		};
	});

	function nav(qs: string) {
		goto(base + page.url.pathname.slice(base.length) + qs, {
			keepFocus: true,
			noScroll: true,
			replaceState: false
		});
	}

	return {
		get params() {
			return params;
		},
		get result() {
			return result;
		},
		get loading() {
			return loading;
		},
		get error() {
			return error;
		},
		setFilter: (key, value) => nav(buildQuery(page.url.searchParams, { [key]: value })),
		setSort: (sortValue) => nav(buildQuery(page.url.searchParams, { sort: sortValue })),
		setPage: (n) => nav(buildQuery(page.url.searchParams, { page: String(n) }, false))
	};
}
