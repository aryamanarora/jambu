<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { ListState } from '$lib/listState.svelte';
	import { PAGE_SIZE } from '$lib/types';
	import { countListFilters, resultRange, type FilterMode } from '$lib/listFilters';
	import ListToolbar from './ListToolbar.svelte';
	import QueryError from './QueryError.svelte';
	import Pager from './Pager.svelte';

	let { list, mode, showLanguage = true, placeholder = 'Search all columns…', filters, children }: {
		list: ListState;
		mode: FilterMode;
		showLanguage?: boolean;
		placeholder?: string;
		filters: Snippet;
		children: Snippet;
	} = $props();
	const resultLabel = $derived(list.result
		? resultRange(list.result.count, list.result.page, list.result.rows.length, PAGE_SIZE, mode)
		: '');
</script>

<div class="loader-slot">{#if list.loading}<div class="loader-line"></div>{/if}</div>
<ListToolbar value={list.params.word} {placeholder} searchLabel="Search all shown columns" {resultLabel}
	filterCount={countListFilters(list.params, mode, showLanguage)} onSearch={(value) => list.setFilter('word', value)} {filters} />
{#if list.error}<QueryError error={list.error} />{/if}
{@render children()}
{#if list.result}<Pager count={list.result.count} page={list.result.page} onpage={list.setPage} />{/if}

<style>
	.loader-slot { height: 3px; margin-bottom: 0.4rem; }
</style>
