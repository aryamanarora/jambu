<script lang="ts">
	import { base } from '$app/paths';
	import type { MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';
	import Donut from '$lib/components/Donut.svelte';
	import { getOriginLangDistribution, type OriginSlice } from '$lib/query';

	let { data } = $props();
	const lang = $derived(data.language);

	// distribution of this language's reflexes by the language they descend from (client-side)
	let origins = $state<OriginSlice[]>([]);
	let curLang = '';
	$effect(() => {
		if (lang.id !== curLang) {
			curLang = lang.id;
			origins = [];
			getOriginLangDistribution(lang.id).then((o) => (origins = o));
		}
	});

	const markers = $derived<MapMarker[]>(
		lang.lat != null
			? [{ lat: lang.lat, long: lang.long, svg: lang.map_marker, tooltip: lang.name }]
			: []
	);
</script>

<svelte:head>
	<title>{lang.name} — Jambu</title>
	<meta name="description" content="The lexicon of {lang.name} ({lang.clade}) in the Jambu etymological dictionary — {lang.lemma_count} reflexes." />
</svelte:head>

<h1 class="headword">{lang.name} <span class="id-tag">[{lang.id}]</span></h1>

<div class="lang-header">
	<dl class="props card">
		<div class="prop"><dt>Family</dt><dd>{lang.clade}</dd></div>
		{#if lang.glottocode}
			<div class="prop">
				<dt>Glottolog</dt>
				<dd>
					<a href="https://glottolog.org/resource/languoid/id/{lang.glottocode}" rel="noreferrer"
						>{lang.glottocode}</a
					>
				</dd>
			</div>
		{/if}
		{#if lang.lat != null}
			<div class="prop">
				<dt>Coordinates</dt>
				<dd class="muted">{lang.lat?.toFixed(3)}, {lang.long?.toFixed(3)}</dd>
			</div>
		{/if}
		<div class="prop"><dt>Reflexes</dt><dd>{lang.lemma_count.toLocaleString()}</dd></div>
	</dl>
	{#if markers.length}
		<div class="lang-map"><Map {markers} zoom={5} height="260px" /></div>
	{/if}
</div>

{#if origins.length}
	<section class="origins">
		<h2>Origins</h2>
		<Donut slices={origins} />
	</section>
{/if}

<h2>Lexicon</h2>
<ReflexesView mode="lexicon" languageId={lang.id} />

<style>
	.origins {
		margin: 1.6rem 0;
	}
	.lang-header {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 1.2rem;
		align-items: start;
		margin-top: 1rem;
	}
	.lang-header .props {
		margin: 0;
		padding: 0.4rem 1.15rem;
		align-self: start;
	}
	.prop {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1.5rem;
		padding: 0.55rem 0;
		border-bottom: 1px solid var(--border);
	}
	.prop:last-child {
		border-bottom: none;
	}
	.prop dt {
		color: var(--muted);
		font-size: 0.85rem;
		font-weight: 600;
	}
	.prop dd {
		margin: 0;
		font-weight: 500;
		text-align: right;
		font-variant-numeric: tabular-nums;
	}
	@media (max-width: 720px) {
		.lang-header {
			grid-template-columns: 1fr;
		}
	}
</style>
