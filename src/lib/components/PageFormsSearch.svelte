<script lang="ts">
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { buildQuery } from '$lib/urlParams';
	import ListToolbar from './ListToolbar.svelte';

	const query = $derived(browser ? page.url.searchParams.get('word') ?? '' : '');
	function search(word: string) {
		goto(buildQuery(page.url.searchParams, { word }), { keepFocus: true, noScroll: true });
	}
</script>

<ListToolbar value={query} placeholder="Search this page’s forms…" searchLabel="Search this page’s forms" onSearch={search} />
