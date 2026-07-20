<script lang="ts">
	import { base } from '$app/paths';
	import type { MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';

	let { data } = $props();
	const lang = $derived(data.language);

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
	<table class="props card">
		<tbody>
			<tr><th>Family</th><td>{lang.clade}</td></tr>
			{#if lang.glottocode}
				<tr>
					<th>Glottolog</th>
					<td><a href="https://glottolog.org/resource/languoid/id/{lang.glottocode}" rel="noreferrer">{lang.glottocode}</a></td>
				</tr>
			{/if}
			<tr><th>Coordinates</th><td class="muted">{lang.lat?.toFixed(3)}, {lang.long?.toFixed(3)}</td></tr>
			<tr><th>Reflexes</th><td>{lang.lemma_count.toLocaleString()}</td></tr>
		</tbody>
	</table>
	{#if markers.length}
		<div class="lang-map"><Map {markers} zoom={5} height="260px" /></div>
	{/if}
</div>

<h2>Lexicon</h2>
<ReflexesView mode="lexicon" languageId={lang.id} />

<style>
	.lang-header {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 1.2rem;
		align-items: start;
		margin-top: 1rem;
	}
	.lang-header .props {
		padding: 0.6rem 1rem;
	}
	@media (max-width: 720px) {
		.lang-header {
			grid-template-columns: 1fr;
		}
	}
</style>
