<script lang="ts">
	import QualityBadge from '$lib/components/QualityBadge.svelte';
	import RecordHeader from '$lib/components/RecordHeader.svelte';
	import OverviewCards from '$lib/components/OverviewCards.svelte';
	import DisclosureCard from '$lib/components/DisclosureCard.svelte';
	import LexiconLayout from '$lib/components/LexiconLayout.svelte';
	import ActiveFilter from '$lib/components/ActiveFilter.svelte';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import type { Dialect, Language, MapMarker } from '$lib/types';
	import GeoMap from '$lib/components/Map.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';
	import Donut from '$lib/components/Donut.svelte';
	import Tags from '$lib/components/Tags.svelte';
	import { cladeColor, hashColor } from '$lib/clades';
	import { activePoint, highlightPoint, livePoint, mutedPoint } from '$lib/atlas';
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
			dialectSearch = '';
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

	// ---- the dialect picker -------------------------------------------------------------------
	// the lexicon is the payload, so the column beside it can be folded away when a reader wants
	// the full width for the table
	let sideOpen = $state(true);
	onMount(() => {
		sideOpen = window.matchMedia('(min-width: 1001px)').matches;
		return () => clearTimeout(hoverTimer);
	});
	let dialectSearch = $state('');
	let hovered = $state<string | null>(null);
	// every hover repaints the points, so let the pointer settle before it does
	let hoverTimer: ReturnType<typeof setTimeout>;
	function preview(token: string | null) {
		clearTimeout(hoverTimer);
		hoverTimer = setTimeout(() => (hovered = token), token ? 70 : 0);
	}

	const selectedToken = $derived(searchParams.get('dialect') ?? '');
	const selectedDialect = $derived(dialects.find((dialect) => dialect.token === selectedToken));
	const shownDialects = $derived.by(() => {
		const query = dialectSearch.trim().toLowerCase();
		return dialects
			.filter((dialect) =>
				query
					? [dialect.name, dialect.location, dialect.id, dialect.glottocode]
							.filter(Boolean)
							.some((value) => value!.toLowerCase().includes(query))
					: true
			)
			.sort((a, b) => b.lemma_count - a.lemma_count || a.name.localeCompare(b.name));
	});
	const locatedCount = $derived(dialects.filter((dialect) => dialect.lat != null).length);

	function dialectHref(dialect: Dialect): string {
		return buildQuery(searchParams, {
			dialect: dialect.token === selectedToken ? '' : dialect.token
		});
	}
	function pickDialect(dialect: Dialect) {
		goto(dialectHref(dialect), { keepFocus: true, noScroll: true });
	}

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

	// ---- the map ------------------------------------------------------------------------------
	// The language's own point is the subject and always drawn; its dialects are live until one is
	// picked, at which point the rest stand down. Hovering a row only points its place out.
	const markers = $derived.by((): MapMarker[] => {
		const points: MapMarker[] = [];
		if (lang.lat != null && lang.long != null && !selectedToken) {
			points.push({
				lat: lang.lat,
				long: lang.long,
				svg: lang.map_marker,
				...activePoint(cladeColor(lang.clade)),
				tooltip: `<strong>${lang.name}</strong><br>${lang.clade} · ${lang.lemma_count.toLocaleString()} forms`
			});
		}
		for (const dialect of shownDialects) {
			if (dialect.lat == null || dialect.long == null) continue;
			const colour = hashColor(dialect.color ?? lang.color);
			const pointedAt = hovered === dialect.token;
			const chosen = dialect.token === selectedToken;
			points.push({
				lat: dialect.lat,
				long: dialect.long,
				svg: lang.map_marker,
				...(pointedAt
					? highlightPoint(colour)
					: chosen
						? activePoint(colour)
						: selectedToken
							? mutedPoint()
							: livePoint(colour)),
				tooltipOpen: pointedAt,
				tooltip: `<strong>${dialect.name}</strong><br>${dialect.location || 'location not recorded'} · ${dialect.lemma_count.toLocaleString()} forms`,
				onClick: () => pickDialect(dialect)
			});
		}
		return points;
	});
</script>

<svelte:head>
	<title>{lang.name} — Jambu</title>
	<meta name="description" content="The lexicon of {lang.name} ({lang.clade}) in the Jambu etymological dictionary — {lang.lemma_count} reflexes." />
</svelte:head>

<RecordHeader title={lang.name} id={lang.id} backHref={`${base}/languages`} backLabel="All languages">
	<div><dt>Family</dt><dd>{lang.clade}</dd></div>
	<div><dt>Forms</dt><dd>{lang.lemma_count.toLocaleString()}</dd></div>
	{#if dialects.length}<div><dt>Dialects</dt><dd>{dialects.length.toLocaleString()}</dd></div>{/if}
	{#if references.length}<div><dt>Sources</dt><dd>{references.length.toLocaleString()}</dd></div>{/if}
</RecordHeader>

<OverviewCards label="Lexicon distributions">
	{#if origins.length}
		<DisclosureCard title="Origins" kind="chart">
			{#snippet meta()}{origins.length.toLocaleString()}{/snippet}
			<Donut slices={origins} selected={selectedOrigins} onselect={filterOrigins} />
		</DisclosureCard>
	{/if}
	{#if references.length}
		<DisclosureCard title="Sources" kind="chart">
			{#snippet meta()}{references.length.toLocaleString()}{/snippet}
			<Donut
				slices={references}
				unit="citations"
				label="Distribution of references"
				selected={selectedReferences}
				onselect={filterReferences}
			/>
		</DisclosureCard>
	{/if}

</OverviewCards>

<LexiconLayout title="Lexicon" label={`${lang.name} lexicon`} sideId="language-filters" sideLabel={`${lang.name} map and filters`} bind:open={sideOpen}>

	{#if selectedDialect}
		<ActiveFilter label="Lexicon filtered to" value={selectedDialect.name} clearHref={buildQuery(searchParams, { dialect: '' })} clearLabel="Clear dialect" />
	{/if}
	<ReflexesView mode="lexicon" languageId={lang.id} />
	{#snippet sidebar()}
		{#if markers.length}
			<DisclosureCard title="Distribution" kind="side">
				{#snippet meta()}{#if dialects.length}{locatedCount.toLocaleString()} / {dialects.length.toLocaleString()} located{:else}1 location{/if}{/snippet}
				<GeoMap {markers} height="16rem" />
			</DisclosureCard>
		{/if}

		{#if dialects.length}
			<DisclosureCard title="Dialects" kind="side">
				{#snippet meta()}{shownDialects.length.toLocaleString()} / {dialects.length.toLocaleString()}{/snippet}
			<div class="controls">
				<input class="search" type="search" aria-label="Filter dialects or places" placeholder="Filter dialects or places…" bind:value={dialectSearch} />
			</div>
			<p class="hint">Select a dialect to filter the lexicon.</p>
			<div class="list" role="group" aria-label="Dialects of {lang.name}">
				{#each shownDialects as dialect (dialect.token)}
					{@const chosen = dialect.token === selectedToken}
					<div class="row" class:pinned={chosen} style="--c: {hashColor(dialect.color ?? lang.color)}">
						<button
							class="pick"
							aria-pressed={chosen}
							title={chosen ? 'Show all forms again' : `Narrow the lexicon to ${dialect.name}`}
							onmouseenter={() => preview(dialect.token)}
							onmouseleave={() => preview(null)}
							onfocus={() => preview(dialect.token)}
							onblur={() => preview(null)}
							onclick={() => pickDialect(dialect)}
						>
							<span class="dot"></span>
							<span class="word">{dialect.name}</span>
							<span class="count">{dialect.lemma_count.toLocaleString()}</span>
							<span class="meta">
								{dialect.location || 'location not recorded'}{#if dialect.lat == null} · not located{/if}
							</span>
						</button>
						{#if dialect.quality}
							<QualityBadge quality={dialect.quality} inset />
						{/if}
					</div>
				{:else}
					<p class="empty">No dialect matches “{dialectSearch}”.</p>
				{/each}
			</div>
			</DisclosureCard>
		{/if}

	{/snippet}
</LexiconLayout>

<!-- reference material: read once, then never again -->
<div class="lang-drawers">
	<details id="metadata" class="page-disclosure">
		<summary>Language metadata{#if metadataTagCount}<span>{metadataTagCount.toLocaleString()} descriptive tags</span>{/if}</summary>
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

	{#if dialects.length}
		<details class="page-disclosure">
			<summary>Dialect metadata<span>{dialects.length.toLocaleString()}</span></summary>
			<div class="table-wrap">
				<table class="data">
					<thead>
						<tr><th>Dialect</th><th>ID</th><th>Glottocode</th><th>Location</th><th>Quality</th><th>Coordinates</th></tr>
					</thead>
					<tbody>
						{#each dialects as dialect (dialect.token)}
							<tr>
								<td><a href={dialectHref(dialect)}>{dialect.name}</a></td>
								<td class="muted">{dialect.id}</td>
								<td>{#if dialect.glottocode}<a href={`https://glottolog.org/resource/languoid/id/${dialect.glottocode}`} rel="noreferrer">{dialect.glottocode}</a>{/if}</td>
								<td>{dialect.location ?? ''}</td>
								<td>{dialect.quality ?? ''}</td>
								<td class="muted">{dialect.lat != null ? `${dialect.lat.toFixed(3)}, ${dialect.long?.toFixed(3)}` : ''}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</details>
	{/if}

	<details id="compare" class="page-disclosure">
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
</div>

<style>
	.meta {
		grid-area: meta;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--muted);
		font-size: 0.72rem;
		line-height: 1.3;
	}

	.lang-drawers { margin-top: 2rem; }
	.page-disclosure + .page-disclosure { margin-top: 0.5rem; }
	.metadata-grid {
		display: grid;
		grid-template-columns: minmax(0, 18rem) minmax(0, 1fr);
		gap: 1rem;
		align-items: start;
		margin-top: 0.7rem;
	}
	.tag-groups { display: grid; gap: 0.7rem; padding: 0.8rem; }
	.tag-group h3 {
		margin: 0 0 0.25rem;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.7rem;
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}
	.compare-picker {
		display: flex;
		flex-wrap: wrap;
		align-items: flex-end;
		gap: 0.75rem;
		margin-top: 0.7rem;
	}
	.compare-picker > div { flex: 1 1 16rem; }
	.compare-picker select { flex: 1 1 14rem; min-width: 0; max-width: 100%; }
	.compare-picker label { font-weight: 600; }
	.compare-picker p { margin: 0.15rem 0 0; font-size: 0.82rem; }

	@media (max-width: 1000px) {
		.metadata-grid { grid-template-columns: 1fr; }
	}
</style>
