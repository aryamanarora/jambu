<script lang="ts">
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
	import '$lib/styles/atlas.css';

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

<header class="lang-head">
	<div class="language-title">
		<a class="back-link" href={`${base}/languages`}>All languages</a>
		<h1 class="headword">{lang.name} <span class="id-tag">[{lang.id}]</span></h1>
	</div>
	<div class="head-right">
		<dl class="head-stats">
			<div><dt>Family</dt><dd>{lang.clade}</dd></div>
			<div><dt>Forms</dt><dd>{lang.lemma_count.toLocaleString()}</dd></div>
			{#if dialects.length}<div><dt>Dialects</dt><dd>{dialects.length.toLocaleString()}</dd></div>{/if}
			{#if references.length}<div><dt>Sources</dt><dd>{references.length.toLocaleString()}</dd></div>{/if}
		</dl>
	</div>
</header>

<div class="language-charts" aria-label="Lexicon distributions">
		{#if origins.length}
			<details class="chart-card" open>
				<summary>Origins<span>{origins.length.toLocaleString()}</span></summary>
				<Donut slices={origins} selected={selectedOrigins} onselect={filterOrigins} />
			</details>
		{/if}
		{#if references.length}
			<details class="chart-card" open>
				<summary>Sources<span>{references.length.toLocaleString()}</span></summary>
				<Donut
					slices={references}
					unit="citations"
					label="Distribution of references"
					selected={selectedReferences}
					onselect={filterReferences}
				/>
			</details>
		{/if}

</div>

<div class="lexicon-toolbar">
	<h2>Lexicon</h2>
	<button class="side-fold" aria-expanded={sideOpen} aria-controls="language-filters" onclick={() => (sideOpen = !sideOpen)}>
		{sideOpen ? 'Hide map & filters' : 'Show map & filters'}
	</button>
</div>

<div class="lang-body" class:no-side={!sideOpen}>
	<section class="lexicon-col" id="lexicon" aria-label={`${lang.name} lexicon`}>
		{#if selectedDialect}
			<p class="active-filter">
				Lexicon filtered to <strong>{selectedDialect.name}</strong>
				<a href={buildQuery(searchParams, { dialect: '' })} data-sveltekit-noscroll>Clear dialect</a>
			</p>
		{/if}
		<ReflexesView mode="lexicon" languageId={lang.id} />
	</section>

	<!-- everything that narrows the lexicon, beside the lexicon -->
	<aside id="language-filters" class="side-col atlas" hidden={!sideOpen} aria-label={`${lang.name} map and filters`}>
		{#if markers.length}
			<details class="side-drawer map-drawer" open>
				<summary>Distribution<span>{#if dialects.length}{locatedCount.toLocaleString()} / {dialects.length.toLocaleString()} located{:else}1 location{/if}</span></summary>
				<GeoMap {markers} height="16rem" />
			</details>
		{/if}

		{#if dialects.length}
			<details class="side-drawer" open>
			<summary>Dialects<span>{shownDialects.length.toLocaleString()} / {dialects.length.toLocaleString()}</span></summary>
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
							<span class={`dq q${dialect.quality}`} title={`Source quality ${dialect.quality}`}>{dialect.quality}</span>
						{/if}
					</div>
				{:else}
					<p class="empty">No dialect matches “{dialectSearch}”.</p>
				{/each}
			</div>
			</details>
		{/if}

	</aside>
</div>

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
	.language-charts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 1.25rem; }
	.language-charts:empty { display: none; }
	.chart-card { min-width: 0; padding: 0.8rem 1rem; border: 1px solid var(--border); border-radius: var(--radius-sm); }
	.chart-card summary { cursor: pointer; font-weight: 600; font-size: 0.85rem; }
	.chart-card[open] summary { margin-bottom: 0.65rem; }
	.chart-card summary span { float: right; color: var(--muted); font-weight: 400; }
	.chart-card :global(.legend) { flex: 1; min-width: 0; max-height: 11rem; overflow-y: auto; scrollbar-width: thin; }
	@media (max-width: 760px) { .language-charts { grid-template-columns: 1fr; } }
	@media (max-width: 640px) {
		.chart-card :global(.donut) { width: 112px; height: 112px; }
		.chart-card :global(.donut-wrap) { gap: 0.8rem; }
		.chart-card :global(.legend button) { display: grid; grid-template-columns: 0.7rem minmax(0, 1fr); gap: 0.15rem 0.4rem; }
		.chart-card :global(.ct) { grid-column: 2; font-size: 0.72rem; }
	}
	/* ---- header: the name, then the four figures on one line ---- */
	.lang-head {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		flex-wrap: wrap;
		gap: 0.5rem 1.5rem;
		margin-bottom: 0.9rem;
	}
	.lang-head h1 { margin: 0.25rem 0 0; }
	.language-title { min-width: 0; overflow-wrap: anywhere; }
	.back-link { font-size: 0.8rem; color: var(--muted); }
	.lexicon-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.8rem 0; margin-top: 1.2rem; border-top: 1px solid var(--border); }
	.lexicon-toolbar h2 { margin: 0; font-size: 1.1rem; }
	.head-right {
		display: flex;
		align-items: baseline;
		gap: 1.4rem;
		flex-wrap: wrap;
	}
	.head-stats {
		display: flex;
		gap: 0.8rem 1.4rem;
		flex-wrap: wrap;
		margin: 0;
	}
	.side-fold {
		padding: 0.5rem 0.7rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: none;
		color: var(--muted);
		font: inherit;
		font-size: 0.8rem;
		font-weight: 600;
		white-space: nowrap;
		cursor: pointer;
	}
	.side-fold:hover { border-color: var(--plum-2); color: var(--plum-2); }
	.head-stats dt {
		color: var(--muted);
		font-size: 0.66rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.head-stats dd {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		font-variant-numeric: tabular-nums;
	}

	/* ---- body: the lexicon, and the instrument that narrows it ---- */
	.lang-body {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(17rem, 21rem);
		gap: 1.5rem;
		align-items: start;
	}
	.lang-body.no-side { grid-template-columns: minmax(0, 1fr); }
	.lexicon-col { min-width: 0; }
	.side-col {
		padding: 0 0.85rem 0.85rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		position: sticky;
		top: 4.5rem;
		max-height: calc(100vh - 5.5rem);
		overflow-y: auto;
		min-width: 0;
		scrollbar-width: thin;
		scrollbar-color: var(--border-strong) transparent;
	}
	.side-col[hidden] { display: none; }
	.active-filter {
		flex-wrap: wrap;
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
		margin: 0 0 0.6rem;
		padding: 0.5rem 0.7rem;
		border: 1px solid color-mix(in srgb, var(--berry) 35%, var(--border));
		border-radius: var(--radius-sm);
		background: color-mix(in srgb, var(--berry) 7%, transparent);
		font-size: 0.85rem;
	}
	.active-filter a { font-size: 0.8rem; font-weight: 600; }

	/* the row grammar comes from atlas.css via the `atlas` class; only the second line differs */
	.side-col :global(.pick) {
		grid-template-areas:
			'dot word count'
			'. meta meta';
	}
	.side-col :global(.controls) { padding: 0.35rem 0 0.3rem; }
	.side-col :global(.list) { padding: 0 0 0.5rem; max-height: 18rem; overflow-y: auto; scrollbar-width: thin; }
	.side-col :global(.hint) { padding: 0 0 0.45rem; }
	.side-col :global(.row) { align-items: center; }
	.meta {
		grid-area: meta;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--muted);
		font-size: 0.72rem;
		line-height: 1.3;
	}
	/* how good the record behind a dialect is — A best, C weakest */
	.dq {
		align-self: center;
		box-sizing: border-box;
		width: 1.15rem;
		margin-right: 0.35rem;
		border: 1px solid color-mix(in srgb, var(--plum-2) 40%, transparent);
		border-radius: 3px;
		color: var(--plum-2);
		font-size: 0.62rem;
		font-weight: 700;
		text-align: center;
	}
	.qA { background: color-mix(in srgb, var(--plum-2) 26%, transparent); }
	.qB { background: color-mix(in srgb, var(--plum-2) 12%, transparent); }
	.qC { background: none; opacity: 0.75; }

	.side-drawer {
		margin-top: 0.75rem;
		border-top: 1px solid var(--border);
		padding-top: 0.6rem;
	}
	.side-drawer:first-child { border-top: 0; margin-top: 0; }
	.side-drawer > summary {
		display: list-item;
		padding: 0.35rem 0;
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
		cursor: pointer;
	}
	.side-drawer[open] > summary { margin-bottom: 0.6rem; }
	.side-drawer > summary span { float: right; font-weight: 400; letter-spacing: 0; text-transform: none; }

	/* ---- reference drawers ---- */
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
		.lang-body,
		.lang-body.no-side { grid-template-columns: 1fr; }
		.side-col {
			position: static;
			max-height: none;
			overflow: visible;
			grid-row: 1;
		}
		.metadata-grid { grid-template-columns: 1fr; }
	}
</style>
