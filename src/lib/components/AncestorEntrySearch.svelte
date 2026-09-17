<script lang="ts">
	import { base } from '$app/paths';
	import { paramsFromUrl, buildQuery } from '$lib/urlParams';
	import ListToolbar from './ListToolbar.svelte';
	import LemmaFilters from './LemmaFilters.svelte';
	import { countListFilters } from '$lib/listFilters';
	let {value,onChange,onSubmit,language}:{value:string;onChange:(value:string)=>void;onSubmit:()=>void;language:string}=$props();
	const params=$derived(paramsFromUrl(new URLSearchParams(value)));
	const count=$derived(countListFilters(params, 'entries', false));
	function change(key:string,v:string){onChange(buildQuery(new URLSearchParams(value),{[key]:v}).slice(1));}
	const entriesHref=$derived(`${base}/entries${buildQuery(new URLSearchParams(value),{origin_lang:language})}`);
</script>

{#snippet filters()}
	<LemmaFilters {params} mode="entries" showLanguage={false} debounceMs={0} onFilter={change} />
{/snippet}
<ListToolbar value={params.word} placeholder="Search ancestor entries…" searchLabel="Search ancestor entries" onSearch={v=>change('word',v)} {onSubmit} debounceMs={0} filterCount={count} filterAlign="start" {filters} />
<div class="search-note"><span>Same search and filters as Entries.</span><a href={entriesHref}>Preview entries ↗</a>{#if value}<button type="button" onclick={()=>onChange('')}>Clear</button>{/if}</div>
<style>
	.search-note{display:flex;flex-wrap:wrap;gap:.3rem .7rem;font-size:.66rem;color:var(--muted);margin-bottom:.7rem}.search-note button{border:0;background:none;color:var(--muted);text-decoration:underline;font:inherit;cursor:pointer}
</style>
