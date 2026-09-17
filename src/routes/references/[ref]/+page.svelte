<script lang="ts">
	import { referenceProgress, unetymologisedPercent } from '$lib/referenceStatus';
	import RecordHeader from '$lib/components/RecordHeader.svelte';
	import OverviewCards from '$lib/components/OverviewCards.svelte';
	import DisclosureCard from '$lib/components/DisclosureCard.svelte';
	import LexiconLayout from '$lib/components/LexiconLayout.svelte';
	import ActiveFilter from '$lib/components/ActiveFilter.svelte';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { md, referenceLabel, safe } from '$lib/render';
	import { referenceBibtex } from '$lib/bibtex';
	import Donut from '$lib/components/Donut.svelte';
	import GeoMap from '$lib/components/Map.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';
	import { getAllLanguages, getReferenceLanguageDistribution, type OriginSlice } from '$lib/query';
	import type { Language, MapMarker } from '$lib/types';
	import { cladeColor } from '$lib/clades';
	import { activePoint, highlightPoint, livePoint, mutedPoint } from '$lib/atlas';
	import { buildQuery } from '$lib/urlParams';

	let { data } = $props();
	const ref = $derived(data.reference);
	let bibtex = $state('');
	let copyState = $state<'idle' | 'copying' | 'copied' | 'error'>('idle');
	let citationError = $state(false);
	$effect(() => {
		const reference = ref;
		let cancelled = false;
		bibtex = '';
		copyState = 'idle';
		citationError = false;
		referenceBibtex(reference).then((text) => {
			if (!cancelled) bibtex = text;
		}).catch(() => { if (!cancelled) citationError = true; });
		return () => { cancelled = true; };
	});
	async function copyBibtex() {
		const id = ref.id;
		copyState = 'copying';
		try {
			await navigator.clipboard.writeText(bibtex);
			if (ref.id === id) copyState = 'copied';
		} catch { if (ref.id === id) copyState = 'error'; }
	}
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

<RecordHeader title={referenceLabel(ref)} id={ref.id} backHref={`${base}/references`} backLabel="All sources">
	<div><dt>Digitisation</dt><dd><span class="badge {referenceProgress(ref.progress)}">{ref.progress || 'No'}</span></dd></div>
	<div><dt>Forms</dt><dd>{(ref.lemma_count ?? 0).toLocaleString()}</dd></div>
	{#if languages.length}<div><dt>Languages</dt><dd>{languages.length.toLocaleString()}</dd></div>{/if}
	<div><dt>Unetymologised</dt><dd>{unetymologisedPercent(ref.lemma_count ?? 0, ref.unetymologised_count ?? 0)}</dd></div>
</RecordHeader>

<OverviewCards label="Source overview">
	<DisclosureCard title="Citation" kind="chart">

		<div class="markdown source">{@html md(ref.source || `Reference abbreviation ${ref.id}; full citation not yet catalogued.`)}</div>
		<div class="citation-actions">
			<button type="button" disabled={!bibtex || copyState === 'copying'} onclick={copyBibtex}>
				{copyState === 'copied' ? 'Copied!' : 'Copy BibTeX'}
			</button>
			<span role="status">{citationError ? 'Could not load BibTeX. Reload to retry.' : copyState === 'error' ? 'Copy failed. Please try again.' : copyState === 'copied' ? 'BibTeX copied to clipboard.' : ''}</span>
		</div>
	</DisclosureCard>
	{#if languages.length}
		<DisclosureCard title="Languages" kind="chart">
			{#snippet meta()}{languages.length.toLocaleString()}{/snippet}

			<Donut slices={languages} label="Distribution of forms cited by language" unit="forms" />
		</DisclosureCard>
	{/if}
</OverviewCards>
{#if loadError}<p role="alert" class="muted">Could not load the language distribution: {loadError}</p>{/if}

<LexiconLayout title="Cited forms" label={`${referenceLabel(ref)} cited forms`} sideId="reference-filters" sideLabel="Source map and language filters" bind:open={sideOpen}>

	{#if selectedLanguage}
		<ActiveFilter label="Forms filtered to" value={selectedLanguage.name} clearHref={buildQuery(searchParams, { origin_lang: '', dialect: '' })} clearLabel="Clear language" />
	{/if}
	{#key ref.id}<ReflexesView referenceId={ref.id} />{/key}

	{#snippet sidebar()}
		{#if markers.length}
			<DisclosureCard title="Distribution" kind="side">
				{#snippet meta()}{locatedCount.toLocaleString()} / {languages.length.toLocaleString()} located{/snippet}

				<GeoMap {markers} height="16rem" />
			</DisclosureCard>
		{/if}
		<DisclosureCard title="Languages" kind="side">
			{#snippet meta()}{shownLanguages.length.toLocaleString()} / {languages.length.toLocaleString()}{/snippet}

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
		</DisclosureCard>

	{/snippet}
</LexiconLayout>

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
		<dd>{unetymologisedPercent(ref.lemma_count ?? 0, ref.unetymologised_count ?? 0)} ({(ref.unetymologised_count ?? 0).toLocaleString()} of {(ref.lemma_count ?? 0).toLocaleString()} forms)</dd>
	</div>
</dl>

	</details>
</div>

<style>
	.citation-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem; }
	.citation-actions button { padding: 0.3rem 0.6rem; border: 1px solid var(--border-strong); border-radius: 4px; background: var(--surface-2); color: var(--ink); font: inherit; font-size: 0.78rem; cursor: pointer; }
	.citation-actions button:disabled { opacity: 0.6; cursor: default; }
	.citation-actions button:focus-visible { outline: 2px solid var(--plum-2); outline-offset: 2px; }
	.citation-actions [role='status'] { font-size: 0.75rem; color: var(--muted); }
	.source { font-size: 1.05rem; overflow-wrap: anywhere; }
	.meta { grid-area: meta; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); font-size: 0.72rem; line-height: 1.3; }
	.ref-drawers { margin-top: 2rem; }
	.reference-metadata { margin: 0.7rem 0 0; padding: 0.4rem 1.15rem; }
	.prop { display: flex; justify-content: space-between; align-items: baseline; gap: 1.5rem; padding: 0.55rem 0; border-bottom: 1px solid var(--border); }
	.prop:last-child { border-bottom: none; }
	.prop dt { color: var(--muted); font-size: 0.85rem; font-weight: 600; }
	.prop dd { margin: 0; font-weight: 500; text-align: right; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }

	@media (max-width: 640px) {
		.prop { align-items: flex-start; flex-direction: column; gap: 0.2rem; }
		.prop dd { max-width: 100%; text-align: left; }
	}
</style>
