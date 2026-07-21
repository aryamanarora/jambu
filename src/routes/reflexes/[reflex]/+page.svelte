<script lang="ts">
	import { page } from '$app/state';
	import { base } from '$app/paths';
	import {
		getLemma,
		getReflexAlignment,
		getAncestryChain,
		getReflexVariants,
		type AlignSeg,
		type AncestorRef
	} from '$lib/query';
	import { striptags, safe } from '$lib/render';
	import type { Lemma, MapMarker } from '$lib/types';
	import MapView from '$lib/components/Map.svelte';
	import ReflexDetail from '$lib/components/ReflexDetail.svelte';
	import Ancestry from '$lib/components/Ancestry.svelte';
	import LangName from '$lib/components/LangName.svelte';

	let reflex = $state<Lemma | null>(null);
	let segs = $state<AlignSeg[]>([]);
	let chain = $state<AncestorRef[][]>([]);
	let variants = $state<Lemma[]>([]);
	let notFound = $state(false);
	let loading = $state(true);

	const id = $derived(page.params.reflex ?? '');

	$effect(() => {
		const rid = id;
		loading = true;
		notFound = false;
		chain = [];
		variants = [];
		getAncestryChain(rid).then((c) => (chain = c));
		getReflexVariants(rid).then((v) => (variants = v));
		Promise.all([getLemma(rid), getReflexAlignment(rid)]).then(([l, a]) => {
			reflex = l;
			segs = a;
			notFound = !l;
			loading = false;
		});
	});

	// the "from" line's label depends on how this node relates to its etymon
	const relLabel = $derived(reflex?.relation === 'variant' ? 'Variant of' : 'Reflex of');

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
	<Ancestry label={relLabel} {chain} startLang={reflex.language?.name} />
	{#if variants.length}
		<div class="rvariants">
			<span class="rv-label">Variant{variants.length === 1 ? '' : 's'}</span>
			{#each variants as v (v.id)}<span class="rv-line"><span class="rv-arrow">→</span>&nbsp;<a
						class="rv phon"
						href="{base}/reflexes/{v.id}">{@html safe(v.word)}</a
					></span>{/each}
		</div>
	{/if}

	<div class="body">
		<ReflexDetail lemma={reflex} {segs} linkWord={false} />
		{#if markers.length}
			<MapView {markers} zoom={5} height="300px" />
		{/if}
	</div>
{/if}

<style>
	.rvariants {
		margin: -0.4rem 0 0.9rem;
	}
	.rv-label {
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
		margin-right: 0.5rem;
	}
	.rv-line {
		display: block;
		font-size: 0.9rem;
		color: var(--muted);
	}
	.rv-arrow {
		font-size: 0.72rem;
		color: var(--faint);
	}
	.rv {
		font-family: var(--font-phon);
	}
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
