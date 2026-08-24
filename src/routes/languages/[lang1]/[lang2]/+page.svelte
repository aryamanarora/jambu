<script lang="ts">
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import {
		compareLanguages,
		compareLanguageConcepts,
		type CompareRow,
		type ConceptCompareRow
	} from '$lib/query';
	import { striptags } from '$lib/render';
	import type { Language, Lemma, MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';
	import FormWord from '$lib/components/FormWord.svelte';

	let lang1 = $state<Language | null>(null);
	let lang2 = $state<Language | null>(null);
	interface AlignmentRow {
		id: string;
		label: string;
		category?: string;
		ocr?: boolean | number;
		left: Lemma[];
		right: Lemma[];
		sharedEtyma?: ConceptCompareRow['sharedEtyma'];
	}

	let etymonRows = $state<CompareRow[]>([]);
	let conceptRows = $state<ConceptCompareRow[]>([]);
	let loading = $state(true);
	let alignment = $state<'etymon' | 'concept'>('etymon');
	let search = $state('');
	let view = $state<'all' | 'one-to-one' | 'variant-rich' | 'shared-etymon' | 'different-etyma'>('all');
	let sort = $state<'headword' | 'compact' | 'variants'>('headword');
	let visibleCount = $state(40);
	let expanded = $state<Set<string>>(new Set());

	const ids = $derived([page.params.lang1 ?? '', page.params.lang2 ?? ''] as const);

	$effect(() => {
		const [a, b] = ids;
		loading = true;
		Promise.all([compareLanguages(a, b), compareLanguageConcepts(a, b)]).then(([comparison, concepts]) => {
			lang1 = comparison.lang1;
			lang2 = comparison.lang2;
			etymonRows = comparison.rows;
			conceptRows = concepts;
			loading = false;
		});
	});

	const markers = $derived<MapMarker[]>(
		[lang1, lang2]
			.filter((l): l is Language => !!l && l.lat != null)
			.map((l) => ({ lat: l.lat, long: l.long, svg: l.map_marker, tooltip: l.name }))
	);
	const comparisonSides = $derived(
		lang1 && lang2
			? [
					{ side: 'left' as const, language: lang1 },
					{ side: 'right' as const, language: lang2 }
				]
			: []
	);
	const alignmentRows = $derived<AlignmentRow[]>(
		alignment === 'etymon'
			? etymonRows.map((row) => ({
					id: row.entryId,
					label: row.entryWord,
					ocr: row.entryOcr,
					left: row.left,
					right: row.right
				}))
			: conceptRows.map((row) => ({
					id: String(row.conceptId),
					label: row.name,
					category: row.category,
					left: row.left,
					right: row.right,
					sharedEtyma: row.sharedEtyma
				}))
	);
	const oneToOneCount = $derived(alignmentRows.filter((row) => row.left.length === 1 && row.right.length === 1).length);
	const variantRichCount = $derived(alignmentRows.filter((row) => row.left.length + row.right.length >= 8).length);
	const conceptOverlapCount = $derived(conceptRows.filter((row) => row.sharedEtyma.length > 0).length);
	const filteredRows = $derived.by(() => {
		const needle = search.trim().toLocaleLowerCase();
		const result = alignmentRows.filter((row) => {
			if (view === 'one-to-one' && (row.left.length !== 1 || row.right.length !== 1)) return false;
			if (view === 'variant-rich' && row.left.length + row.right.length < 8) return false;
			if (view === 'shared-etymon' && !row.sharedEtyma?.length) return false;
			if (view === 'different-etyma' && row.sharedEtyma?.length) return false;
			if (!needle) return true;
			const text = [
				row.label,
				row.id,
				row.category ?? '',
				...(row.sharedEtyma ?? []).flatMap((etymon) => [etymon.id, etymon.word]),
				...row.left.flatMap((form) => [form.word, striptags(form.gloss ?? '')]),
				...row.right.flatMap((form) => [form.word, striptags(form.gloss ?? '')])
			]
				.join(' ')
				.toLocaleLowerCase();
			return text.includes(needle);
		});
		return result.sort((a, b) => {
			if (sort === 'compact') {
				const difference = a.left.length + a.right.length - (b.left.length + b.right.length);
				if (difference) return difference;
			}
			if (sort === 'variants') {
				const difference = b.left.length + b.right.length - (a.left.length + a.right.length);
				if (difference) return difference;
			}
			return a.label.localeCompare(b.label);
		});
	});
	const visibleRows = $derived(filteredRows.slice(0, visibleCount));

	function coverage(language: Language | null): number {
		if (!language?.lemma_count) return 0;
		return (etymonRows.length / language.lemma_count) * 100;
	}

	function setAlignment(next: typeof alignment) {
		alignment = next;
		view = 'all';
		search = '';
		visibleCount = 40;
		expanded = new Set();
	}

	function setView(next: typeof view) {
		view = next;
		visibleCount = 40;
	}

	function setSearch(value: string) {
		search = value;
		visibleCount = 40;
	}

	function expansionKey(row: AlignmentRow, side: 'left' | 'right'): string {
		return `${alignment}:${row.id}:${side}`;
	}

	function shownForms(row: AlignmentRow, side: 'left' | 'right'): Lemma[] {
		const forms = side === 'left' ? row.left : row.right;
		return expanded.has(expansionKey(row, side)) ? forms : forms.slice(0, 3);
	}

	function toggleForms(row: AlignmentRow, side: 'left' | 'right') {
		const key = expansionKey(row, side);
		const next = new Set(expanded);
		if (next.has(key)) next.delete(key);
		else next.add(key);
		expanded = next;
	}
</script>

<svelte:head>
	<title>{lang1?.name ?? '…'} vs {lang2?.name ?? '…'} — Jambu</title>
</svelte:head>

{#if loading}
	<div class="loader-line" style="margin-top: 2rem"></div>
{:else if !lang1 || !lang2}
	<h1>Language not found</h1>
{:else}
	<section class="comparison-hero">
		<div class="hero-main">
			<a class="back-link" href="{base}/languages">← Language atlas</a>
			<p class="eyebrow">Language comparison</p>
			<div class="title-line">
				<h1>{lang1.name} <span>and</span> {lang2.name}</h1>
				<a class="swap-link" href="{base}/languages/{lang2.id}/{lang1.id}" aria-label="Swap compared languages">⇄ Swap</a>
			</div>
			<p class="lede">
				{#if alignment === 'etymon'}
					Browse the etyma represented in both languages. A shared row means common ancestry in the
					dictionary graph; it does not imply that every listed sense is identical.
				{:else}
					Compare forms assigned to the same curated concept, regardless of whether their histories
					are related. This is the meaning-first view of the two lexicons.
				{/if}
			</p>

			<div class="headline-stats" aria-label="Comparison summary">
				<div><strong>{alignmentRows.length.toLocaleString()}</strong><span>shared {alignment === 'etymon' ? 'etyma' : 'concepts'}</span></div>
				{#if alignment === 'etymon'}
					<div><strong>{oneToOneCount.toLocaleString()}</strong><span>one-to-one rows</span></div>
					<div><strong>{variantRichCount.toLocaleString()}</strong><span>variant-rich rows</span></div>
				{:else}
					<div><strong>{conceptOverlapCount.toLocaleString()}</strong><span>with shared etyma</span></div>
					<div><strong>{(conceptRows.length - conceptOverlapCount).toLocaleString()}</strong><span>different etyma</span></div>
				{/if}
			</div>

			<div class="language-pair">
				{#each [lang1, lang2] as language (language.id)}
					<article class="language-card">
						<div class="language-name">
							<span class="language-dot" style:background={language.color}></span>
							<a href="{base}/languages/{language.id}">{language.name}</a>
						</div>
						<span class="family">{language.clade}</span>
						<div class="coverage-line">
							<span>{language.lemma_count.toLocaleString()} reflexes</span>
							<strong>{coverage(language).toFixed(1)}% etyma shared</strong>
						</div>
						<div class="coverage-track" aria-hidden="true">
							<span style:width={`${Math.min(coverage(language), 100)}%`}></span>
						</div>
					</article>
				{/each}
			</div>
		</div>

		{#if markers.length}
			<div class="cmp-map" aria-label="Map of the compared languages">
				<Map {markers} zoom={5} height="100%" />
			</div>
		{/if}
	</section>

	<section class="shared-section" aria-labelledby="shared-heading">
		<div class="section-intro">
			<div>
				<p class="eyebrow">Evidence browser</p>
				<h2 id="shared-heading">Shared {alignment === 'etymon' ? 'etyma' : 'concepts'}</h2>
			</div>
			<p>Forms are collapsed to three per language. Expand a side only when you need its full dialect and source variation.</p>
		</div>

		<div class="alignment-tabs" aria-label="Alignment basis">
			<button class:active={alignment === 'etymon'} type="button" onclick={() => setAlignment('etymon')}>
				<span>By etymon</span>
				<small>{etymonRows.length.toLocaleString()} rows · common ancestry</small>
			</button>
			<button class:active={alignment === 'concept'} type="button" onclick={() => setAlignment('concept')}>
				<span>By concept</span>
				<small>{conceptRows.length.toLocaleString()} rows · shared meaning</small>
			</button>
		</div>

		<div class="comparison-toolbar">
			<label class="search-field">
				<span class="search-icon" aria-hidden="true">⌕</span>
				<span class="visually-hidden">Search shared etyma</span>
				<input
					type="search"
					placeholder={alignment === 'etymon' ? 'Search etymon, reflex, or gloss…' : 'Search concept, form, or gloss…'}
					value={search}
					oninput={(event) => setSearch(event.currentTarget.value)}
				/>
			</label>
			<div class="view-tabs" aria-label="Comparison view">
				<button class:active={view === 'all'} type="button" onclick={() => setView('all')}>All <span>{alignmentRows.length}</span></button>
				{#if alignment === 'etymon'}
					<button class:active={view === 'one-to-one'} type="button" onclick={() => setView('one-to-one')}>One-to-one <span>{oneToOneCount}</span></button>
					<button class:active={view === 'variant-rich'} type="button" onclick={() => setView('variant-rich')}>Variant-rich <span>{variantRichCount}</span></button>
				{:else}
					<button class:active={view === 'shared-etymon'} type="button" onclick={() => setView('shared-etymon')}>Shared etymon <span>{conceptOverlapCount}</span></button>
					<button class:active={view === 'different-etyma'} type="button" onclick={() => setView('different-etyma')}>Different etyma <span>{conceptRows.length - conceptOverlapCount}</span></button>
				{/if}
			</div>
			<label class="sort-field">
				<span>Sort</span>
				<select bind:value={sort} onchange={() => (visibleCount = 40)}>
					<option value="headword">Headword</option>
					<option value="compact">Fewest forms</option>
					<option value="variants">Most forms</option>
				</select>
			</label>
		</div>

		<div class="result-line">
			<strong>{filteredRows.length.toLocaleString()}</strong>
			{filteredRows.length === 1 ? 'match' : 'matches'}
			{#if search}<span>for “{search}”</span>{/if}
		</div>

		{#if filteredRows.length}
			<div class:concept-mode={alignment === 'concept'} class="match-list">
				<div class="column-head" aria-hidden="true">
					<span>{alignment === 'etymon' ? 'Etymon' : 'Concept'}</span>
					<span>{lang1.name}</span>
					<span>{lang2.name}</span>
				</div>
				{#each visibleRows as row (row.id)}
					<article class="match-row">
						<div class="etymon-cell">
							<span class="mobile-label">{alignment === 'etymon' ? 'Etymon' : 'Concept'}</span>
							{#if alignment === 'etymon'}
								<a class="etymon-word lemma-word" href="{base}/entries/{row.id}">
									<FormWord word={row.label} ocr={row.ocr} />
								</a>
								<span class="entry-id id-tag">{row.id}</span>
							{:else}
								<a class="concept-name" href="{base}/concepts/{row.id}">{row.label}</a>
								<span class="concept-category">{row.category || `Concept ${row.id}`}</span>
								{#if row.sharedEtyma?.length}
									<div class="etymon-overlap">
										<span>Shared {row.sharedEtyma.length === 1 ? 'etymon' : 'etyma'}</span>
										{#each row.sharedEtyma.slice(0, 2) as etymon (etymon.id)}
											<a href="{base}/entries/{etymon.id}"><FormWord word={etymon.word} ocr={etymon.ocr} /></a>
										{/each}
										{#if row.sharedEtyma.length > 2}<small>+{row.sharedEtyma.length - 2}</small>{/if}
									</div>
								{:else}
									<span class="no-overlap">No etymon overlap</span>
								{/if}
							{/if}
						</div>

						{#each comparisonSides as { side, language } (side)}
							<div class="forms-cell">
								<span class="mobile-label">{language.name}</span>
								<div class="forms">
									{#each shownForms(row, side) as form (form.id)}
										<a class="form-chip" href="{base}/reflexes/{form.id}">
											<strong class="lemma-word"><FormWord word={form.word} ocr={form.ocr} /></strong>
											{#if form.gloss}<span class="form-gloss muted">‘{striptags(form.gloss)}’</span>{/if}
										</a>
									{/each}
								</div>
								{#if (side === 'left' ? row.left : row.right).length > 3}
									<button class="more-forms" type="button" onclick={() => toggleForms(row, side)}>
										{#if expanded.has(expansionKey(row, side))}
											Show fewer
										{:else}
											+{(side === 'left' ? row.left : row.right).length - 3} more
										{/if}
									</button>
								{/if}
							</div>
						{/each}
					</article>
				{/each}
			</div>

			{#if visibleRows.length < filteredRows.length}
				<div class="load-more">
					<button type="button" onclick={() => (visibleCount += 40)}>
						Show next {Math.min(40, filteredRows.length - visibleRows.length)}
					</button>
					<span>{visibleRows.length} of {filteredRows.length} shown</span>
				</div>
			{/if}
		{:else}
			<div class="empty-state">
				<strong>No shared etyma match this view.</strong>
				<button type="button" onclick={() => { search = ''; view = 'all'; }}>Clear search and filters</button>
			</div>
		{/if}
	</section>
{/if}

<style>
	.comparison-hero {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(17rem, 0.42fr);
		gap: 1.5rem;
		padding: 1.6rem;
		margin-top: 1.4rem;
		border: 1px solid var(--border);
		border-radius: 14px;
		background: linear-gradient(145deg, var(--surface), color-mix(in srgb, var(--surface-2) 48%, var(--surface)));
		box-shadow: var(--shadow-sm);
	}
	.hero-main { min-width: 0; }
	.back-link {
		display: inline-block;
		margin-bottom: 1.2rem;
		font-family: var(--font-sans);
		font-size: 0.78rem;
		font-weight: 650;
	}
	.eyebrow {
		margin: 0 0 0.25rem;
		color: var(--berry);
		font-family: var(--font-sans);
		font-size: 0.7rem;
		font-weight: 750;
		letter-spacing: 0.12em;
		text-transform: uppercase;
	}
	.title-line {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
	}
	.title-line h1 {
		margin: 0;
		font-size: clamp(2rem, 4.5vw, 3.25rem);
		line-height: 1.05;
		letter-spacing: -0.025em;
	}
	.title-line h1 span {
		color: var(--muted);
		font-size: 0.58em;
		font-style: italic;
		font-weight: 400;
	}
	.swap-link {
		flex: 0 0 auto;
		padding: 0.42rem 0.65rem;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		background: var(--surface);
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 650;
	}
	.swap-link:hover { text-decoration: none; border-color: var(--plum-2); }
	.lede {
		max-width: 46rem;
		margin: 0.8rem 0 1.2rem;
		color: var(--muted);
		font-size: 1rem;
		line-height: 1.5;
	}
	.headline-stats {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		margin: 0 -0.65rem 1.25rem;
	}
	.headline-stats > div {
		display: flex;
		flex-direction: column;
		gap: 0.08rem;
		padding: 0.35rem 0.65rem;
		border-right: 1px solid var(--border);
	}
	.headline-stats > div:last-child { border-right: 0; }
	.headline-stats strong { font-size: 1.35rem; line-height: 1.1; }
	.headline-stats span {
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.72rem;
	}
	.language-pair {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.65rem;
	}
	.language-card {
		min-width: 0;
		padding: 0.85rem;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background: color-mix(in srgb, var(--surface) 86%, transparent);
	}
	.language-name {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		font-family: var(--font-serif);
		font-size: 1.05rem;
		font-weight: 700;
	}
	.language-dot {
		width: 0.65rem;
		height: 0.65rem;
		border: 2px solid var(--surface);
		border-radius: 50%;
		box-shadow: 0 0 0 1px var(--border-strong);
	}
	.family {
		display: block;
		margin: 0.12rem 0 0.75rem 1.1rem;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.72rem;
	}
	.coverage-line {
		display: flex;
		justify-content: space-between;
		gap: 0.6rem;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.7rem;
	}
	.coverage-line strong { color: var(--ink); font-weight: 650; white-space: nowrap; }
	.coverage-track {
		height: 3px;
		margin-top: 0.38rem;
		border-radius: 99px;
		background: var(--border);
		overflow: hidden;
	}
	.coverage-track span { display: block; height: 100%; background: var(--berry); }
	.cmp-map {
		min-height: 20rem;
		overflow: hidden;
		border: 1px solid var(--border-strong);
		border-radius: 10px;
		background: var(--surface-2);
	}

	.shared-section { margin-top: 2.4rem; }
	.section-intro {
		display: flex;
		align-items: end;
		justify-content: space-between;
		gap: 2rem;
	}
	.section-intro h2 { margin: 0; font-size: 1.8rem; }
	.section-intro > p {
		max-width: 36rem;
		margin: 0;
		color: var(--muted);
		font-size: 0.88rem;
		line-height: 1.45;
		text-align: right;
	}
	.alignment-tabs {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.55rem;
		max-width: 36rem;
		margin-top: 1rem;
	}
	.alignment-tabs button {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.75rem;
		padding: 0.65rem 0.75rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--muted);
		font-family: var(--font-sans);
		text-align: left;
		cursor: pointer;
	}
	.alignment-tabs button:hover,
	.alignment-tabs button.active { border-color: var(--plum-2); }
	.alignment-tabs button.active {
		background: color-mix(in srgb, var(--berry) 8%, var(--surface));
		color: var(--plum-2);
		box-shadow: inset 3px 0 0 var(--berry);
	}
	.alignment-tabs span { font-size: 0.8rem; font-weight: 750; white-space: nowrap; }
	.alignment-tabs small { color: var(--muted); font-size: 0.68rem; font-weight: 450; }
	.comparison-toolbar {
		position: sticky;
		top: 3.65rem;
		z-index: 20;
		display: flex;
		align-items: center;
		gap: 0.65rem;
		padding: 0.7rem;
		margin-top: 1rem;
		border: 1px solid var(--border);
		border-radius: 10px;
		background: color-mix(in srgb, var(--paper) 92%, transparent);
		box-shadow: var(--shadow-sm);
		backdrop-filter: blur(10px);
	}
	.search-field { position: relative; flex: 1 1 18rem; }
	.search-field input {
		width: 100%;
		min-height: 40px;
		padding: 0.5rem 0.7rem 0.5rem 2rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--ink);
		font: inherit;
	}
	.search-field input:focus,
	.sort-field select:focus {
		outline: none;
		border-color: var(--plum-2);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--berry) 15%, transparent);
	}
	.search-icon {
		position: absolute;
		left: 0.7rem;
		top: 50%;
		z-index: 1;
		transform: translateY(-53%);
		color: var(--muted);
		pointer-events: none;
	}
	.view-tabs {
		display: inline-flex;
		padding: 3px;
		border: 1px solid var(--border);
		border-radius: 7px;
		background: var(--surface-2);
	}
	.view-tabs button {
		min-height: 32px;
		padding: 0.25rem 0.55rem;
		border: 0;
		border-radius: 4px;
		background: transparent;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.7rem;
		font-weight: 650;
		cursor: pointer;
		white-space: nowrap;
	}
	.view-tabs button span { margin-left: 0.2rem; font-variant-numeric: tabular-nums; opacity: 0.75; }
	.view-tabs button.active { background: var(--surface); color: var(--plum-2); box-shadow: var(--shadow-sm); }
	.sort-field { display: flex; align-items: center; gap: 0.4rem; }
	.sort-field span { color: var(--muted); font-family: var(--font-sans); font-size: 0.7rem; }
	.sort-field select {
		min-height: 40px;
		padding: 0.45rem 1.7rem 0.45rem 0.55rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--ink);
		font: 0.72rem var(--font-sans);
	}
	.result-line {
		min-height: 2.2rem;
		padding: 0.65rem 0.2rem 0.4rem;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.76rem;
	}
	.result-line strong { color: var(--ink); }
	.result-line span { margin-left: 0.2rem; }
	.match-list {
		border: 1px solid var(--border);
		border-radius: 10px;
		background: var(--surface);
		overflow: clip;
	}
	.column-head,
	.match-row {
		display: grid;
		grid-template-columns: minmax(8.5rem, 0.55fr) minmax(0, 1fr) minmax(0, 1fr);
		gap: 1rem;
	}
	.concept-mode .column-head,
	.concept-mode .match-row {
		grid-template-columns: minmax(10rem, 0.72fr) minmax(0, 1fr) minmax(0, 1fr);
	}
	.column-head {
		position: sticky;
		top: 8.35rem;
		z-index: 10;
		padding: 0.55rem 0.85rem;
		border-bottom: 1px solid var(--border-strong);
		background: var(--surface-2);
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.68rem;
		font-weight: 750;
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}
	.match-row {
		align-items: start;
		padding: 0.8rem 0.85rem;
		border-bottom: 1px solid var(--border);
	}
	.match-row:last-child { border-bottom: 0; }
	.match-row:hover { background: color-mix(in srgb, var(--surface-2) 45%, var(--surface)); }
	.etymon-cell,
	.forms-cell { min-width: 0; }
	.etymon-word {
		display: block;
		width: fit-content;
		font-family: var(--font-phon);
		font-size: 1.08rem;
		font-weight: 600;
	}
	.concept-name {
		display: block;
		width: fit-content;
		font-family: var(--font-serif);
		font-size: 1rem;
		font-weight: 600;
	}
	.concept-category {
		display: block;
		margin-top: 0.16rem;
		color: var(--faint);
		font-family: var(--font-sans);
		font-size: 0.62rem;
	}
	.etymon-overlap {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.22rem;
		margin-top: 0.45rem;
		font-family: var(--font-serif);
		font-size: 0.72rem;
	}
	.etymon-overlap > span {
		width: 100%;
		color: var(--ok);
		font-family: var(--font-sans);
		font-size: 0.58rem;
		font-weight: 750;
		letter-spacing: 0.03em;
		text-transform: uppercase;
	}
	.etymon-overlap a {
		padding: 0.06rem 0.25rem;
		border-radius: 3px;
		background: color-mix(in srgb, var(--ok) 10%, transparent);
		color: var(--plum-2);
		font-family: var(--font-phon);
		font-size: 0.8rem;
		font-weight: 600;
	}
	.etymon-overlap small { color: var(--muted); font-family: var(--font-sans); }
	.no-overlap {
		display: block;
		margin-top: 0.42rem;
		color: var(--faint);
		font-family: var(--font-sans);
		font-size: 0.6rem;
	}
	.entry-id {
		display: block;
		margin-top: 0.15rem;
		color: var(--faint);
		font-family: var(--font-sans);
		font-size: 0.62rem;
	}
	.forms { display: flex; flex-wrap: wrap; gap: 0.35rem; }
	.form-chip {
		display: inline-flex;
		align-items: baseline;
		gap: 0.28rem;
		max-width: 100%;
		padding: 0.28rem 0.45rem;
		border: 1px solid var(--border);
		border-radius: 5px;
		background: var(--surface);
		color: var(--ink);
		font-family: var(--font-serif);
		line-height: 1.25;
	}
	.form-chip:hover { border-color: var(--plum-2); text-decoration: none; }
	.form-chip strong {
		color: var(--plum-2);
		font-family: var(--font-phon);
		font-size: 0.98rem;
		font-weight: 600;
		white-space: nowrap;
	}
	.form-gloss {
		font-family: var(--font-serif);
		font-size: 0.78rem;
		font-weight: 400;
		overflow-wrap: anywhere;
	}
	.more-forms {
		padding: 0.2rem 0;
		margin-top: 0.25rem;
		border: 0;
		background: none;
		color: var(--plum-2);
		font-family: var(--font-sans);
		font-size: 0.68rem;
		font-weight: 650;
		cursor: pointer;
	}
	.mobile-label { display: none; }
	.load-more {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.45rem;
		padding: 1.25rem;
	}
	.load-more button,
	.empty-state button {
		padding: 0.55rem 0.9rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--plum-2);
		font: 650 0.76rem var(--font-sans);
		cursor: pointer;
	}
	.load-more span { color: var(--muted); font: 0.68rem var(--font-sans); }
	.empty-state {
		display: grid;
		place-items: center;
		gap: 0.8rem;
		min-height: 12rem;
		padding: 2rem;
		border: 1px dashed var(--border-strong);
		border-radius: 10px;
		color: var(--muted);
		text-align: center;
	}

	@media (max-width: 980px) {
		.comparison-hero { grid-template-columns: 1fr 16rem; }
		.cmp-map { min-height: 17rem; }
		.comparison-toolbar { flex-wrap: wrap; }
		.search-field { flex-basis: 100%; }
		.view-tabs { flex: 1 1 auto; }
		.sort-field { margin-left: auto; }
		.column-head { top: 11.15rem; }
	}

	@media (max-width: 720px) {
		.comparison-hero {
			grid-template-columns: 1fr;
			padding: 1rem;
			margin: 0.8rem -0.25rem 0;
		}
		.cmp-map { min-height: 13rem; order: 2; }
		.section-intro { align-items: start; flex-direction: column; gap: 0.45rem; }
		.section-intro > p { text-align: left; }
		.comparison-toolbar { position: static; }
		.column-head { display: none; }
		.match-row,
		.concept-mode .match-row {
			grid-template-columns: minmax(6.5rem, 0.42fr) minmax(0, 1fr);
			gap: 0.75rem;
		}
		.etymon-cell { grid-row: 1 / span 2; }
		.mobile-label {
			display: block;
			margin-bottom: 0.25rem;
			color: var(--muted);
			font-family: var(--font-sans);
			font-size: 0.62rem;
			font-weight: 700;
			letter-spacing: 0.04em;
			text-transform: uppercase;
		}
	}

	@media (max-width: 520px) {
		.title-line { align-items: end; }
		.title-line h1 { font-size: 2rem; }
		.swap-link { padding-inline: 0.5rem; }
		.headline-stats { margin-inline: -0.4rem; }
		.headline-stats > div { padding-inline: 0.4rem; }
		.headline-stats strong { font-size: 1.15rem; }
		.language-pair { grid-template-columns: 1fr; }
		.alignment-tabs { grid-template-columns: 1fr; }
		.view-tabs { width: 100%; overflow-x: auto; }
		.view-tabs button { flex: 1 0 auto; }
		.sort-field { width: 100%; }
		.sort-field select { flex: 1; }
		.match-row,
		.concept-mode .match-row { grid-template-columns: 1fr; padding: 0.85rem 0.75rem; }
		.etymon-cell {
			grid-row: auto;
			padding-bottom: 0.55rem;
			border-bottom: 1px solid var(--border);
		}
		.form-chip { width: 100%; }
	}
</style>
