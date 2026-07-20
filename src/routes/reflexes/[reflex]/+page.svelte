<script lang="ts">
	import { page } from '$app/state';
	import { getLemma, getReflexAlignment, type AlignSeg } from '$lib/query';
	import { striptags, safe } from '$lib/render';
	import type { Lemma, MapMarker } from '$lib/types';
	import MapView from '$lib/components/Map.svelte';
	import ReflexDetail from '$lib/components/ReflexDetail.svelte';
	import LangName from '$lib/components/LangName.svelte';

	let reflex = $state<Lemma | null>(null);
	let segs = $state<AlignSeg[]>([]);
	let notFound = $state(false);
	let loading = $state(true);

	const id = $derived(page.params.reflex ?? '');

	$effect(() => {
		const rid = id;
		loading = true;
		notFound = false;
		Promise.all([getLemma(rid), getReflexAlignment(rid)]).then(([l, a]) => {
			reflex = l;
			segs = a;
			notFound = !l;
			loading = false;
		});
	});

	const markers = $derived<MapMarker[]>(
		reflex?.language && reflex.language.lat != null
			? [
					{
						lat: reflex.language.lat,
						long: reflex.language.long,
						svg: reflex.language.map_marker,
						tooltip: reflex.language.name
					}
				]
			: []
	);
</script>

<svelte:head>
	<title>{reflex ? `${striptags(reflex.word)} [${reflex.id}] — Jambu` : 'Reflex — Jambu'}</title>
</svelte:head>

{#if loading}
	<div class="loader-line" style="margin-top: 2rem"></div>
{:else if notFound || !reflex}
	<h1>Reflex not found</h1>
	<p class="muted">No lemma with id <code>{id}</code>.</p>
{:else}
	<h1 class="headword">
		<span class="faint"><LangName lang={reflex.language} /></span>
		<span class="lemma-word">{@html safe(reflex.word)}</span>
		<span class="id-tag">[{reflex.id}]</span>
	</h1>

	<div class="body">
		<ReflexDetail lemma={reflex} {segs} showOrigin linkWord={false} />
		{#if markers.length}
			<MapView {markers} zoom={5} height="300px" />
		{/if}
	</div>
{/if}

<style>
	.body {
		display: grid;
		grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
		gap: 1.2rem;
		align-items: start;
		margin-top: 1rem;
	}
	@media (max-width: 720px) {
		.body {
			grid-template-columns: 1fr;
		}
	}
</style>
