<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import type { Dialect, Language, MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';
	import Donut from '$lib/components/Donut.svelte';
	import Tags from '$lib/components/Tags.svelte';
	import DialectExplorer from '$lib/components/DialectExplorer.svelte';
	import {
		getLanguageDialects,
		getLanguageTags,
		getAllLanguages,
		getOriginLangDistribution,
		getReferenceDistribution,
		type OriginSlice
	} from '$lib/query';
	import { tagCategory, type TagCategory } from '$lib/tags';
	import { buildQuery } from '$lib/urlParams';

	let { data } = $props();
	const lang = $derived(data.language);

	// distribution of this language's reflexes by the language they descend from (client-side)
	let origins = $state<OriginSlice[]>([]);
	let references = $state<OriginSlice[]>([]);
	let languageTags = $state<string[]>([]);
	let dialects = $state<Dialect[]>([]);
	let languages = $state<Language[]>([]);
	let comparisonLanguage = $state('');
	let searchParams = $state(new URLSearchParams());
	let curLang = '';
	$effect(() => {
		// Search parameters are interactive state. Reading them during prerender is forbidden,
		// so hydrate a local copy once the page is running in the browser.
		searchParams = new URLSearchParams(page.url.searchParams);
	});
	$effect(() => {
		if (lang.id !== curLang) {
			curLang = lang.id;
			origins = [];
			references = [];
			languageTags = [];
			dialects = [];
			comparisonLanguage = '';
			getOriginLangDistribution(lang.id).then((o) => (origins = o));
			getReferenceDistribution(lang.id).then((r) => (references = r));
			getLanguageTags(lang.id).then((t) => (languageTags = t));
			getLanguageDialects(lang.id).then((d) => (dialects = d));
			getAllLanguages().then((list) => (languages = list));
		}
	});
	const comparisonLanguages = $derived(
		languages
			.filter((language) => language.id !== lang.id)
			.sort((a, b) => a.name.localeCompare(b.name))
	);

	function openComparison(event: SubmitEvent) {
		event.preventDefault();
		if (comparisonLanguage) goto(`${base}/languages/${lang.id}/${comparisonLanguage}`);
	}
	const tagGroups: Array<{ category: TagCategory; label: string }> = [
		{ category: 'gender', label: 'Gender' },
		{ category: 'grammatical', label: 'Grammatical' },
		{ category: 'source', label: 'Sources' },
		{ category: 'era', label: 'Eras' }
	];
	function tagsFor(category: TagCategory): string[] {
		return languageTags.filter((tag) => tagCategory(tag) === category);
	}
	const metadataTagCount = $derived(
		tagGroups.reduce((count, group) => count + tagsFor(group.category).length, 0)
	);
	const selectedDialectToken = $derived(searchParams.get('dialect') ?? '');

	const selectedOrigins = $derived(
		searchParams.get('unetym') === '1'
			? ['__unetym']
			: (searchParams.get('etymon_langs')?.split(',').filter(Boolean) ??
				(searchParams.get('etymon_lang') ? [searchParams.get('etymon_lang')!] : []))
	);
	const selectedReferences = $derived(
		searchParams.get('source_ids')?.split(',').filter(Boolean) ?? []
	);

	function filterOrigins(selected: OriginSlice[]) {
		const ids = selected.map((slice) => slice.lang);
		const active = ids.length === selectedOrigins.length && ids.every((id) => selectedOrigins.includes(id));
		const unetym = ids.length === 1 && ids[0] === '__unetym';
		goto(
			buildQuery(searchParams, {
				etymon_lang: !active && ids.length === 1 && !unetym ? ids[0] : '',
				etymon_langs: !active && ids.length > 1 ? ids.join(',') : '',
				unetym: !active && unetym ? '1' : ''
			}),
			{ keepFocus: true, noScroll: true }
		);
	}

	function filterReferences(selected: OriginSlice[]) {
		const ids = selected.map((slice) => slice.lang);
		const active = ids.length === selectedReferences.length && ids.every((id) => selectedReferences.includes(id));
		goto(
			buildQuery(searchParams, {
				source: '',
				source_ids: active ? '' : ids.join(',')
			}),
			{ keepFocus: true, noScroll: true }
		);
	}

	const markers = $derived<MapMarker[]>(
		[
			...(lang.lat != null
				? [{ lat: lang.lat, long: lang.long, svg: lang.map_marker, tooltip: lang.name }]
				: []),
			...dialects
				.filter((d) => d.lat != null && d.long != null)
				.map((d) => ({
					lat: d.lat!,
					long: d.long!,
					svg: lang.map_marker,
					tooltip: `${lang.name}: ${d.name}`
				}))
		]
	);
</script>

<svelte:head>
	<title>{lang.name} — Jambu</title>
	<meta name="description" content="The lexicon of {lang.name} ({lang.clade}) in the Jambu etymological dictionary — {lang.lemma_count} reflexes." />
</svelte:head>

<div class="language-title">
	<h1 class="headword">{lang.name} <span class="id-tag">[{lang.id}]</span></h1>
	<a class="compare-action" href="#compare">Compare</a>
</div>

<div class="lang-header">
	<dl class="props card">
		<div class="prop"><dt>Family</dt><dd>{lang.clade}</dd></div>
		<div class="prop"><dt>Forms</dt><dd>{lang.lemma_count.toLocaleString()}</dd></div>
		{#if dialects.length}<div class="prop"><dt>Dialects</dt><dd>{dialects.length.toLocaleString()}</dd></div>{/if}
		{#if references.length}<div class="prop"><dt>Sources</dt><dd>{references.length.toLocaleString()}</dd></div>{/if}
	</dl>
	{#if markers.length}
		<div class="lang-map"><Map {markers} zoom={5} height="260px" /></div>
	{/if}
</div>

<nav class="section-nav" aria-label={`${lang.name} sections`}>
	{#if dialects.length}<a href="#dialects">Dialects <span>{dialects.length.toLocaleString()}</span></a>{/if}
	<a href="#lexicon">Lexicon <span>{lang.lemma_count.toLocaleString()}</span></a>
	{#if origins.length || references.length}<a href="#coverage">Coverage</a>{/if}
	<a href="#metadata">More</a>
	<a href="#compare">Compare</a>
</nav>

{#if dialects.length}
	<DialectExplorer language={lang} {dialects} selectedToken={selectedDialectToken} />
{/if}

<section id="lexicon" class="lexicon-section" aria-labelledby="lexicon-heading">
	<div class="section-heading">
		<div>
			<h2 id="lexicon-heading">Lexicon</h2>
			<p>Search forms or narrow the lexicon by dialect, source, meaning, and origin.</p>
		</div>
		{#if selectedDialectToken}<a href={`${base}/languages/${lang.id}#lexicon`}>Clear dialect filter</a>{/if}
	</div>
	<ReflexesView mode="lexicon" languageId={lang.id} />
</section>

{#if origins.length || references.length}
	<details id="coverage" class="page-disclosure secondary-section">
		<summary>Origins and source coverage</summary>
		<div class="donut-row">
			{#if origins.length}
				<section class="origins">
					<h2>Origins</h2>
					<Donut slices={origins} selected={selectedOrigins} onselect={filterOrigins} />
				</section>
			{/if}
			{#if references.length}
				<section class="origins">
					<h2>Sources</h2>
					<Donut
						slices={references}
						unit="citations"
						label="Distribution of references"
						selected={selectedReferences}
						onselect={filterReferences}
					/>
				</section>
			{/if}
		</div>
	</details>
{/if}

<details id="metadata" class="page-disclosure secondary-section metadata-section">
	<summary>More metadata{#if metadataTagCount}<span>{metadataTagCount.toLocaleString()} descriptive tags</span>{/if}</summary>
	<div class="metadata-grid">
		<dl class="props card technical-props">
			<div class="prop"><dt>Jambu ID</dt><dd>{lang.id}</dd></div>
			{#if lang.glottocode}
				<div class="prop">
					<dt>Glottolog</dt>
					<dd><a href={`https://glottolog.org/resource/languoid/id/${lang.glottocode}`} rel="noreferrer">{lang.glottocode}</a></dd>
				</div>
			{/if}
			{#if lang.lat != null}
				<div class="prop"><dt>Coordinates</dt><dd>{lang.lat.toFixed(3)}, {lang.long?.toFixed(3)}</dd></div>
			{/if}
		</dl>
		{#if metadataTagCount}
			<div class="tag-groups card">
				{#each tagGroups as group}
					{@const found = tagsFor(group.category)}
					{#if found.length}
						<div class="tag-group">
							<h3>{group.label}</h3>
							<Tags tags={found.join(' ')} />
						</div>
					{/if}
				{/each}
			</div>
		{/if}
	</div>
</details>

<details id="compare" class="page-disclosure secondary-section">
	<summary>Compare with another language</summary>
	<form class="compare-picker" onsubmit={openComparison}>
		<div>
			<label for="comparison-language">Comparison language</label>
			<p class="muted">View shared etymological entries side by side.</p>
		</div>
		<select id="comparison-language" class="search-box" bind:value={comparisonLanguage}>
			<option value="">Choose a language…</option>
			{#each comparisonLanguages as language (language.id)}
				<option value={language.id}>{language.name} [{language.id}]</option>
			{/each}
		</select>
		<button class="btn" type="submit" disabled={!comparisonLanguage}>Compare</button>
	</form>
</details>

<style>
	.language-title {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
	}
	.language-title h1 { margin-bottom: 0; }
	.compare-action {
		padding: 0.38rem 0.7rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		font-size: 0.8rem;
		font-weight: 600;
	}
	.compare-action:hover { border-color: var(--plum-2); text-decoration: none; }
	.section-nav {
		position: sticky;
		top: 3.95rem;
		z-index: 25;
		display: flex;
		gap: 0.2rem;
		margin: 1rem 0 1.25rem;
		padding: 0.38rem;
		overflow-x: auto;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: color-mix(in srgb, var(--surface) 94%, transparent);
		box-shadow: 0 2px 10px color-mix(in srgb, var(--ink) 7%, transparent);
		backdrop-filter: blur(8px);
	}
	.section-nav a {
		display: inline-flex;
		align-items: baseline;
		gap: 0.28rem;
		padding: 0.35rem 0.62rem;
		border-radius: var(--radius-sm);
		color: var(--ink);
		font-size: 0.8rem;
		font-weight: 600;
		white-space: nowrap;
	}
	.section-nav a:hover { background: var(--surface-2); color: var(--plum-2); text-decoration: none; }
	.section-nav span { color: var(--muted); font-size: 0.7rem; font-weight: 400; }
	.lexicon-section,
	.page-disclosure { scroll-margin-top: 7.25rem; }
	.lexicon-section { margin: 1.8rem 0 1.25rem; }
	.section-heading {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 0.4rem;
	}
	.section-heading h2 { margin: 0; }
	.section-heading p { margin: 0.15rem 0 0; color: var(--muted); font-size: 0.84rem; }
	.section-heading > a { font-size: 0.78rem; font-weight: 600; white-space: nowrap; }
	.compare-picker {
		display: grid;
		grid-template-columns: minmax(13rem, 1fr) minmax(12rem, 1fr) auto;
		gap: 1rem;
		align-items: center;
		margin: 0;
		padding: 0.85rem 1.15rem;
	}
	.page-disclosure {
		margin: 0.75rem 0;
		border-bottom: 1px solid var(--border);
	}
	.page-disclosure > summary {
		display: flex;
		align-items: baseline;
		gap: 0.45rem;
		padding: 0.65rem 0;
		color: var(--plum-2);
		font-weight: 600;
		cursor: pointer;
	}
	.page-disclosure > summary span {
		color: var(--muted);
		font-size: 0.8rem;
		font-weight: 400;
	}
	.page-disclosure[open] { padding-bottom: 0.9rem; }
	.compare-picker label {
		font-weight: 600;
	}
	.compare-picker p {
		margin: 0.15rem 0 0;
		font-size: 0.85rem;
	}
	.compare-picker .btn {
		white-space: nowrap;
	}
	.donut-row {
		display: flex;
		gap: 2.5rem;
		flex-wrap: wrap;
		align-items: flex-start;
	}
	.origins {
		margin: 1.6rem 0;
	}
	.secondary-section { margin-top: 0.4rem; }
	.metadata-grid {
		display: grid;
		grid-template-columns: minmax(15rem, 0.65fr) minmax(20rem, 1.35fr);
		gap: 1rem;
	}
	.technical-props { margin: 0; padding: 0.4rem 1rem; }
	.tag-groups {
		display: grid;
		gap: 0.8rem;
		padding: 1rem 1.15rem;
	}
	.tag-group {
		display: grid;
		grid-template-columns: 8rem minmax(0, 1fr);
		align-items: start;
		gap: 0.75rem;
	}
	.tag-group h3 {
		margin: 0;
		font-size: 0.85rem;
		color: var(--muted);
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
		.compare-picker {
			grid-template-columns: 1fr;
		}
		.lang-header {
			grid-template-columns: 1fr;
		}
		.section-nav { top: 3.55rem; margin-inline: -0.15rem; }
		.section-heading { align-items: flex-start; }
		.section-heading > a { display: none; }
		.metadata-grid { grid-template-columns: 1fr; }
		.tag-group {
			grid-template-columns: 1fr;
		}
	}
</style>
