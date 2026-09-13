<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { md, referenceLabel, safe } from '$lib/render';
	import Donut from '$lib/components/Donut.svelte';
	import GeoMap from '$lib/components/Map.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';
	import { getAllLanguages, getReferenceLanguageDistribution, type OriginSlice } from '$lib/query';
	import type { Language, MapMarker } from '$lib/types';
	import { cladeColor } from '$lib/clades';
	import { activePoint, highlightPoint, livePoint, mutedPoint } from '$lib/atlas';
	import { buildQuery } from '$lib/urlParams';
	import '$lib/styles/atlas.css';

	let { data } = $props();
	const ref = $derived(data.reference);
	let languages = $state<OriginSlice[]>([]);
	let allLanguages = $state<Language[]>([]);
	let loadError = $state('');
	let languageSearch = $state('');
	let hovered = $state<string | null>(null);
	let sideOpen = $state(true);
	let searchParams = $state(new URLSearchParams());
	let hoverTimer: ReturnType<typeof setTimeout>;
	onMount(() => {
		sideOpen = window.matchMedia('(min-width: 1001px)').matches;
		return () => clearTimeout(hoverTimer);
	});
	$effect(() => { searchParams = new URLSearchParams(page.url.searchParams); });
	$effect(() => {
		const id = ref.id;
		let cancelled = false;
		languages = [];
		allLanguages = [];
		languageSearch = '';
		hovered = null;
		clearTimeout(hoverTimer);
		loadError = '';
		Promise.all([getReferenceLanguageDistribution(id), getAllLanguages()])
			.then(([distribution, records]) => {
				if (!cancelled) { languages = distribution; allLanguages = records; }
			})
			.catch((error) => { if (!cancelled) loadError = String(error); });
		return () => { cancelled = true; };
	});
	const selectedId = $derived(searchParams.get('origin_lang') ?? '');
	const selectedLanguage = $derived(languages.find((language) => language.lang === selectedId));
	const languageById = $derived(new Map(allLanguages.map((language) => [language.id, language])));
	const shownLanguages = $derived(languages.filter((language) => {
		const query = languageSearch.trim().toLocaleLowerCase();
		return !query || [language.name, language.lang, language.clade ?? ''].some((text) => text.toLocaleLowerCase().includes(query));
	}));
	const locatedCount = $derived(languages.filter((language) => {
		const record = languageById.get(language.lang);
		return record?.lat != null && record.long != null;
	}).length);
	function preview(id: string | null) {
		clearTimeout(hoverTimer);
		hoverTimer = setTimeout(() => (hovered = id), id ? 70 : 0);
	}
	function pickLanguage(id: string) {
		goto(buildQuery(searchParams, { origin_lang: selectedId === id ? '' : id, dialect: '' }), { keepFocus: true, noScroll: true });
	}
	const markers = $derived.by((): MapMarker[] => shownLanguages.flatMap((language) => {
		const record = languageById.get(language.lang);
		if (record?.lat == null || record.long == null) return [];
		const colour = cladeColor(language.clade);
		const pointedAt = hovered === language.lang;
		return [{
			lat: record.lat, long: record.long, svg: record.map_marker,
			...(pointedAt ? highlightPoint(colour) : selectedId === language.lang ? activePoint(colour) : selectedId ? mutedPoint() : livePoint(colour)),
			tooltipOpen: pointedAt,
			tooltip: `<strong>${safe(language.name)}</strong><br>${safe(language.clade)} · ${language.count.toLocaleString()} cited forms`,
			onClick: () => pickLanguage(language.lang)
		}];
	}));
	function badge(progress: string | null): 'ok' | 'warn' | 'bad' {
		if (progress === 'Yes') return 'ok';
		if (progress === 'Partial') return 'warn';
		return 'bad';
	}
	function unetymologisedPct(): string {
		return (ref.lemma_count ?? 0)
			? `${(((ref.unetymologised_count ?? 0) / ref.lemma_count) * 100).toFixed(1)}%`
			: '—';
	}
	function provenanceFiles(provenance: string | null): string[] {
		return provenance?.split(';').map((file) => file.trim()).filter(Boolean) ?? [];
	}
	function provenanceUrl(file: string): string | null {
		return file.startsWith('data/')
			? `https://github.com/moli-mandala/data/blob/main/${file}`
			: null;
	}
	function etymologyProvenance(value: typeof ref.etymology_provenance): string {
		return ({
			source: 'Supplied by the cited source',
			'source-mapped': 'Supplied by the source; mapped to Jambu entries by the editors',
			jambu: 'Added by the Jambu editors',
			mixed: 'Combination of source-supplied and Jambu editorial etymologies',
			none: 'No etymologies represented'
		} as Record<string, string>)[value ?? ''] ?? 'Not recorded';
	}
</script>

<svelte:head>
	<title>{referenceLabel(ref)} [{ref.id}] — Jambu</title>
	<meta name="description" content={`Forms cited in ${referenceLabel(ref)} in the Jambu etymological dictionary.`} />
</svelte:head>

<header class="ref-head">
	<div class="reference-title">
		<a class="back-link" href={`${base}/references`}>All sources</a>
		<h1 class="headword">{referenceLabel(ref)} <span class="id-tag">[{ref.id}]</span></h1>
	</div>
	<dl class="head-stats">
		<div><dt>Digitisation</dt><dd><span class="badge {badge(ref.progress)}">{ref.progress || 'No'}</span></dd></div>
		<div><dt>Forms</dt><dd>{(ref.lemma_count ?? 0).toLocaleString()}</dd></div>
		{#if languages.length}<div><dt>Languages</dt><dd>{languages.length.toLocaleString()}</dd></div>{/if}
		<div><dt>Unetymologised</dt><dd>{unetymologisedPct()}</dd></div>
	</dl>
</header>

<div class="reference-charts" aria-label="Source overview">
	<details class="chart-card" open>
		<summary>Citation</summary>
		<div class="markdown source">{@html md(ref.source || `Reference abbreviation ${ref.id}; full citation not yet catalogued.`)}</div>
	</details>
	{#if languages.length}
		<details class="chart-card" open>
			<summary>Languages<span>{languages.length.toLocaleString()}</span></summary>
			<Donut slices={languages} label="Distribution of forms cited by language" unit="forms" />
		</details>
	{/if}
</div>
{#if loadError}<p role="alert" class="muted">Could not load the language distribution: {loadError}</p>{/if}

<div class="lexicon-toolbar">
	<h2>Cited forms</h2>
	<button class="side-fold" aria-expanded={sideOpen} aria-controls="reference-filters" onclick={() => (sideOpen = !sideOpen)}>
		{sideOpen ? 'Hide map & filters' : 'Show map & filters'}
	</button>
</div>
<div class="ref-body" class:no-side={!sideOpen}>
	<section class="lexicon-col" id="lexicon" aria-label={`${referenceLabel(ref)} cited forms`}>
		{#if selectedLanguage}
			<p class="active-filter">Forms filtered to <strong>{selectedLanguage.name}</strong>
				<a href={buildQuery(searchParams, { origin_lang: '', dialect: '' })} data-sveltekit-noscroll>Clear language</a>
			</p>
		{/if}
		{#key ref.id}<ReflexesView referenceId={ref.id} />{/key}
	</section>
	<aside id="reference-filters" class="side-col atlas" hidden={!sideOpen} aria-label="Source map and language filters">
		{#if markers.length}
			<details class="side-drawer" open>
				<summary>Distribution<span>{locatedCount.toLocaleString()} / {languages.length.toLocaleString()} located</span></summary>
				<GeoMap {markers} height="16rem" />
			</details>
		{/if}
		<details class="side-drawer" open>
			<summary>Languages<span>{shownLanguages.length.toLocaleString()} / {languages.length.toLocaleString()}</span></summary>
			<div class="controls"><input class="search" type="search" aria-label="Filter languages or clades" placeholder="Filter languages or clades…" bind:value={languageSearch} /></div>
			<p class="hint">Select a language to filter the cited forms.</p>
			<div class="list" role="group" aria-label="Languages cited by this source">
				{#each shownLanguages as language (language.lang)}
					{@const chosen = selectedId === language.lang}
					<div class="row" class:pinned={chosen} style={`--c: ${cladeColor(language.clade)}`}>
						<button class="pick" aria-pressed={chosen}
							title={chosen ? 'Show all forms again' : `Narrow the cited forms to ${language.name}`}
							onmouseenter={() => preview(language.lang)} onmouseleave={() => preview(null)}
							onfocus={() => preview(language.lang)} onblur={() => preview(null)}
							onclick={() => pickLanguage(language.lang)}>
							<span class="dot"></span><span class="word">{language.name}</span><span class="count">{language.count.toLocaleString()}</span>
							<span class="meta">{language.clade || 'Clade not recorded'}</span>
						</button>
					</div>
				{:else}<p class="empty">{languageSearch ? `No language matches “${languageSearch}”.` : 'No cited languages available.'}</p>{/each}
			</div>
		</details>
	</aside>
</div>

<div class="ref-drawers">
	<details id="metadata" class="page-disclosure">
		<summary>Source metadata</summary>
<dl class="props card reference-metadata">
	<div class="prop">
		<dt>Provenance</dt>
		<dd>
			{#each provenanceFiles(ref.provenance) as file, index}
				{@const url = provenanceUrl(file)}
				{#if index > 0}; {/if}
				{#if url}<a href={url} rel="noreferrer">{file}</a>{:else}{file}{/if}
			{:else}
				Not recorded
			{/each}
		</dd>
	</div>
	<div class="prop"><dt>Editor</dt><dd>{ref.editor || 'Not recorded'}</dd></div>
	<div class="prop"><dt>Extraction</dt><dd>{ref.ocr ? 'Optical character recognition (OCR)' : 'Not marked as OCR'}</dd></div>
	<div class="prop"><dt>Etymologies</dt><dd>{etymologyProvenance(ref.etymology_provenance)}</dd></div>
	<div class="prop">
		<dt>Unetymologised</dt>
		<dd>{unetymologisedPct()} ({(ref.unetymologised_count ?? 0).toLocaleString()} of {(ref.lemma_count ?? 0).toLocaleString()} forms)</dd>
	</div>
</dl>

	</details>
</div>

<style>

	.reference-charts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 1.25rem; }
	.chart-card { min-width: 0; padding: 0.8rem 1rem; border: 1px solid var(--border); border-radius: var(--radius-sm); }
	.chart-card summary { cursor: pointer; font-weight: 600; font-size: 0.85rem; }
	.chart-card[open] summary { margin-bottom: 0.65rem; }
	.chart-card summary span { float: right; color: var(--muted); font-weight: 400; }
	.chart-card :global(.legend) { flex: 1; min-width: 0; max-height: 11rem; overflow-y: auto; scrollbar-width: thin; }
	.source { font-size: 1.05rem; overflow-wrap: anywhere; }
	.ref-head { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem 1.5rem; margin-bottom: 0.9rem; }
	.ref-head h1 { margin: 0.25rem 0 0; }
	.reference-title { min-width: 0; overflow-wrap: anywhere; }
	.back-link { font-size: 0.8rem; color: var(--muted); }
	.head-stats { display: flex; gap: 0.8rem 1.4rem; flex-wrap: wrap; margin: 0; }
	.head-stats dt { color: var(--muted); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; }
	.head-stats dd { margin: 0; font-size: 1rem; font-weight: 600; font-variant-numeric: tabular-nums; }
	.lexicon-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.8rem 0; margin-top: 1.2rem; border-top: 1px solid var(--border); }
	.lexicon-toolbar h2 { margin: 0; font-size: 1.1rem; }
	.side-fold { padding: 0.5rem 0.7rem; border: 1px solid var(--border-strong); border-radius: var(--radius-sm); background: none; color: var(--muted); font: inherit; font-size: 0.8rem; font-weight: 600; white-space: nowrap; cursor: pointer; }
	.side-fold:hover { border-color: var(--plum-2); color: var(--plum-2); }
	.ref-body { display: grid; grid-template-columns: minmax(0, 1fr) minmax(17rem, 21rem); gap: 1.5rem; align-items: start; }
	.ref-body.no-side { grid-template-columns: minmax(0, 1fr); }
	.lexicon-col { min-width: 0; }
	.side-col { padding: 0 0.85rem 0.85rem; border: 1px solid var(--border); border-radius: var(--radius-sm); position: sticky; top: 4.5rem; max-height: calc(100vh - 5.5rem); overflow-y: auto; min-width: 0; scrollbar-width: thin; scrollbar-color: var(--border-strong) transparent; }
	.side-col[hidden] { display: none; }
	.active-filter { flex-wrap: wrap; display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin: 0 0 0.6rem; padding: 0.5rem 0.7rem; border: 1px solid color-mix(in srgb, var(--berry) 35%, var(--border)); border-radius: var(--radius-sm); background: color-mix(in srgb, var(--berry) 7%, transparent); font-size: 0.85rem; }
	.active-filter a { font-size: 0.8rem; font-weight: 600; }
	.side-col :global(.pick) { grid-template-areas: 'dot word count' '. meta meta'; }
	.side-col :global(.controls) { padding: 0.35rem 0 0.3rem; }
	.side-col :global(.list) { padding: 0 0 0.5rem; max-height: 18rem; overflow-y: auto; scrollbar-width: thin; }
	.side-col :global(.hint) { padding: 0 0 0.45rem; }
	.side-col :global(.row) { align-items: center; }
	.meta { grid-area: meta; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); font-size: 0.72rem; line-height: 1.3; }
	.side-drawer { margin-top: 0.75rem; border-top: 1px solid var(--border); padding-top: 0.6rem; }
	.side-drawer:first-child { border-top: 0; margin-top: 0; }
	.side-drawer > summary { display: list-item; padding: 0.35rem 0; font-size: 0.8rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; cursor: pointer; }
	.side-drawer[open] > summary { margin-bottom: 0.6rem; }
	.side-drawer > summary span { float: right; font-weight: 400; letter-spacing: 0; text-transform: none; }
	.ref-drawers { margin-top: 2rem; }
	.reference-metadata { margin: 0.7rem 0 0; padding: 0.4rem 1.15rem; }
	.prop { display: flex; justify-content: space-between; align-items: baseline; gap: 1.5rem; padding: 0.55rem 0; border-bottom: 1px solid var(--border); }
	.prop:last-child { border-bottom: none; }
	.prop dt { color: var(--muted); font-size: 0.85rem; font-weight: 600; }
	.prop dd { margin: 0; font-weight: 500; text-align: right; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
	@media (max-width: 1000px) {
		.ref-body, .ref-body.no-side { grid-template-columns: 1fr; }
		.side-col { position: static; max-height: none; overflow: visible; grid-row: 1; }
	}
	@media (max-width: 760px) { .reference-charts { grid-template-columns: 1fr; } }
	@media (max-width: 640px) {
		.chart-card :global(.donut) { width: 112px; height: 112px; }
		.chart-card :global(.donut-wrap) { gap: 0.8rem; }
		.chart-card :global(.legend button) { display: grid; grid-template-columns: 0.7rem minmax(0, 1fr); gap: 0.15rem 0.4rem; }
		.chart-card :global(.ct) { grid-column: 2; font-size: 0.72rem; }
		.prop { align-items: flex-start; flex-direction: column; gap: 0.2rem; }
		.prop dd { max-width: 100%; text-align: left; }
	}
</style>
