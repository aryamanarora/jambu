<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { CLADE_ORDER, cladeColor, hashColor } from '$lib/clades';
	import { SUPER_ORDER, cladeGroup, superBranch } from '$lib/cladeTree';
	import type { DialectIndexRow, Language, MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';
	import ListToolbar from '$lib/components/ListToolbar.svelte';

	let { data } = $props();

	interface LanguageMatch {
		language: Language;
		dialects: DialectIndexRow[];
		languageMatched: boolean;
	}

	let search = $state('');
	let selectedClade = $state('');
	let familyOpen = $state(false);

	const normalizedSearch = $derived(search.trim().toLowerCase());
	const languagesById = $derived.by(
		() => new globalThis.Map<string, Language>(data.languages.map((language) => [language.id, language]))
	);
	const dialectsByLanguage = $derived.by(() => {
		const grouped = new globalThis.Map<string, DialectIndexRow[]>();
		for (const dialect of data.dialects) {
			if (!grouped.has(dialect.language_id)) grouped.set(dialect.language_id, []);
			grouped.get(dialect.language_id)!.push(dialect);
		}
		return grouped;
	});

	function includesQuery(parts: Array<string | null | undefined>, query: string): boolean {
		return parts.some((part) => part?.toLowerCase().includes(query));
	}

	const matches: LanguageMatch[] = $derived.by(() => {
		const query = normalizedSearch;
		return data.languages
			.map((language) => {
				const languageMatched =
					!query ||
					includesQuery(
						[language.name, language.language, language.dialect, language.id, language.clade],
						query
					);
				const dialects = query
					? (dialectsByLanguage.get(language.id) ?? []).filter((dialect) =>
							includesQuery(
								[dialect.name, dialect.id, dialect.token, dialect.location, dialect.quality],
								query
							)
						)
					: [];
				return { language, dialects, languageMatched };
			})
			.filter(
				(match) =>
					(!selectedClade || match.language.clade === selectedClade) &&
					(match.languageMatched || match.dialects.length > 0)
			)
			.sort((a, b) => a.language.name.localeCompare(b.language.name));
	});

	const resultGroups = $derived.by(() => {
		const grouped = new globalThis.Map<string, LanguageMatch[]>();
		for (const match of matches) {
			const clade = match.language.clade || 'Other';
			if (!grouped.has(clade)) grouped.set(clade, []);
			grouped.get(clade)!.push(match);
		}
		return [...grouped.entries()].sort(([a], [b]) => {
			const ai = CLADE_ORDER.indexOf(a);
			const bi = CLADE_ORDER.indexOf(b);
			return (ai < 0 ? 999 : ai) - (bi < 0 ? 999 : bi) || a.localeCompare(b);
		});
	});

	const cladeStats = $derived.by(() => {
		const stats = new globalThis.Map<
			string,
			{ clade: string; languages: number; dialects: number; forms: number; branch: string }
		>();
		for (const language of data.languages) {
			const clade = language.clade || 'Other';
			const current = stats.get(clade) ?? {
				clade,
				languages: 0,
				dialects: 0,
				forms: 0,
				branch: superBranch(cladeGroup(clade))
			};
			current.languages += 1;
			current.dialects += dialectsByLanguage.get(language.id)?.length ?? 0;
			current.forms += language.lemma_count;
			stats.set(clade, current);
		}
		return [...stats.values()].sort((a, b) => {
			const ai = CLADE_ORDER.indexOf(a.clade);
			const bi = CLADE_ORDER.indexOf(b.clade);
			return (ai < 0 ? 999 : ai) - (bi < 0 ? 999 : bi) || a.clade.localeCompare(b.clade);
		});
	});

	function statsForBranch(branch: string) {
		return cladeStats.filter((stat) => stat.branch === branch);
	}

	const matchedDialectCount = $derived(matches.reduce((sum, match) => sum + match.dialects.length, 0));
	const visibleDialectHits = $derived(matches.flatMap((match) => match.dialects));
	const markers: MapMarker[] = $derived.by(() => {
		if (normalizedSearch && visibleDialectHits.some((dialect) => dialect.lat != null && dialect.long != null)) {
			return visibleDialectHits
				.filter((dialect) => dialect.lat != null && dialect.long != null)
				.map((dialect) => {
					const parent = languagesById.get(dialect.language_id);
					return {
						lat: dialect.lat!,
						long: dialect.long!,
						svg: parent?.map_marker ?? '',
						color: hashColor(dialect.color ?? parent?.color),
						radius: 6,
						tooltip: `${parent?.name ?? dialect.language_id}: ${dialect.name} (${dialect.lemma_count.toLocaleString()} forms)`,
						onClick: () =>
							goto(
								`${base}/languages/${dialect.language_id}?dialect=${encodeURIComponent(dialect.token)}#lexicon`
							)
					};
				});
		}
		return matches
			.map(({ language }) => language)
			.filter((language) => language.lat != null && language.long != null)
			.map((language) => ({
				lat: language.lat,
				long: language.long,
				svg: language.map_marker,
				tooltip: `${language.name} · ${language.lemma_count.toLocaleString()} forms · ${(dialectsByLanguage.get(language.id)?.length ?? 0).toLocaleString()} dialects`,
				onClick: () => goto(`${base}/languages/${language.id}`)
			}));
	});

	function chooseClade(clade: string) {
		selectedClade = clade;
		familyOpen = false;
	}

</script>

{#snippet actions()}
	<a class="atlas-link" href="#language-map">Map</a>
{/snippet}

<svelte:head>
	<title>Languages — Jambu</title>
	<meta
		name="description"
		content="Browse the {data.languages.length} languages and {data.dialects.length} dialects represented in Jambu by family, location, and lexicon coverage."
	/>
</svelte:head>

<div class="page-heading">
	<div>
		<h1>Languages</h1>
		<p>Browse families, languages, and dialects represented in the dictionary.</p>
	</div>
	<p class="totals">
		{data.languages.length.toLocaleString()} languages · {data.dialects.length.toLocaleString()} dialects
	</p>
</div>

<ListToolbar
	value={search}
	placeholder="Search languages, dialects, families, or IDs…"
	searchLabel="Search languages and dialects"
	resultLabel={`${matches.length.toLocaleString()} language${matches.length === 1 ? '' : 's'}${normalizedSearch && matchedDialectCount ? ` · ${matchedDialectCount.toLocaleString()} dialect match${matchedDialectCount === 1 ? '' : 'es'}` : ''}`}
	onSearch={(value) => (search = value)}
	{actions}
/>

<div class="language-explorer">
	<aside class:open={familyOpen} class="family-rail" aria-label="Browse languages by family">
		<button
			type="button"
			class="family-toggle"
			aria-expanded={familyOpen}
			onclick={() => (familyOpen = !familyOpen)}
		>
			<span>{selectedClade || 'Browse by family'}</span><span aria-hidden="true">⌄</span>
		</button>
		<div class="family-options">
			<button class:active={!selectedClade} type="button" onclick={() => chooseClade('')}>
				<span>All languages</span><small>{data.languages.length}</small>
			</button>
			{#each SUPER_ORDER as branch}
				{@const branchStats = statsForBranch(branch)}
				{#if branchStats.length}
					<h2>{branch}</h2>
					{#each branchStats as stat (stat.clade)}
						<button
							class:active={selectedClade === stat.clade}
							type="button"
							onclick={() => chooseClade(stat.clade)}
						>
							<span><i style={`background:${cladeColor(stat.clade)}`}></i>{stat.clade}</span>
							<small>{stat.languages}</small>
						</button>
					{/each}
				{/if}
			{/each}
		</div>
	</aside>

	<main class="language-results" aria-live="polite">
		{#if matches.length === 0}
			<div class="empty-state">
				<h2>No matching languages or dialects</h2>
				<p>Try a language name, dialect, family, location, or Jambu ID.</p>
			</div>
		{:else}
			{#each resultGroups as [clade, group] (clade)}
				<section class="clade-group" aria-labelledby={`clade-${clade.replace(/[^a-z0-9]/gi, '-')}`}>
					<header>
						<h2 id={`clade-${clade.replace(/[^a-z0-9]/gi, '-')}`}>
							<i style={`background:${cladeColor(clade)}`}></i>{clade}
						</h2>
						<span>{group.length} language{group.length === 1 ? '' : 's'}</span>
					</header>
					<div class="language-list">
						{#each group as match (match.language.id)}
							{@const language = match.language}
							{@const dialectCount = dialectsByLanguage.get(language.id)?.length ?? 0}
							<article class="language-row" style={`--language:${hashColor(language.color)}`}>
								<a class="language-main" href={`${base}/languages/${language.id}`}>
									<strong>{language.name}</strong>
									<span>{language.clade} · <span class="id-tag">[{language.id}]</span></span>
								</a>
								<div class="language-counts">
									<span><strong>{language.lemma_count.toLocaleString()}</strong> forms</span>
									<span><strong>{dialectCount.toLocaleString()}</strong> dialect{dialectCount === 1 ? '' : 's'}</span>
								</div>
								{#if normalizedSearch && match.dialects.length}
									<div class="dialect-hits" aria-label={`Matching ${language.name} dialects`}>
										{#each match.dialects.slice(0, 6) as dialect (dialect.token)}
											<a
												href={`${base}/languages/${language.id}?dialect=${encodeURIComponent(dialect.token)}#lexicon`}
											>
												<strong>{dialect.name}</strong>
												<span>{dialect.location || 'Location not recorded'} · {dialect.lemma_count.toLocaleString()} forms</span>
											</a>
										{/each}
										{#if match.dialects.length > 6}<span class="more-hits">+{match.dialects.length - 6} more</span>{/if}
									</div>
								{/if}
							</article>
						{/each}
					</div>
				</section>
			{/each}
		{/if}
	</main>

	<details id="language-map" class="atlas-map" open>
		<summary>Atlas <span>{markers.length.toLocaleString()} mapped locations</span></summary>
		{#if markers.length}
			<Map {markers} height="min(62vh, 540px)" />
		{:else}
			<p class="muted">No mapped locations in this selection.</p>
		{/if}
	</details>
</div>

<style>
	.page-heading {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: 1rem;
	}
	.page-heading h1 { margin-bottom: 0.15rem; }
	.page-heading p { margin: 0; color: var(--muted); }
	.page-heading .totals { font-size: 0.85rem; white-space: nowrap; }
	:global(.atlas-link) {
		display: none;
		padding: 0.55rem 0.7rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		color: var(--plum-2);
		font-size: 0.82rem;
		font-weight: 600;
	}
	.language-explorer {
		display: grid;
		grid-template-areas: 'families results map';
		grid-template-columns: 13.5rem minmax(24rem, 1fr) minmax(20rem, 27rem);
		gap: 1.15rem;
		align-items: start;
		margin-top: 0.8rem;
	}
	.family-rail {
		grid-area: families;
		position: sticky;
		top: 4.75rem;
		max-height: calc(100vh - 5.75rem);
		overflow-y: auto;
		padding-right: 0.75rem;
		border-right: 1px solid var(--border);
	}
	.family-toggle {
		display: flex;
		justify-content: space-between;
		width: 100%;
		padding: 0.45rem 0;
		border: 0;
		background: transparent;
		color: var(--ink);
		font: inherit;
		font-weight: 700;
		text-align: left;
	}
	.family-options { display: grid; gap: 0.1rem; }
	.family-options h2 {
		margin: 0.75rem 0 0.2rem;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.68rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}
	.family-options button {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.6rem;
		width: 100%;
		padding: 0.38rem 0.45rem;
		border: 0;
		border-radius: var(--radius-sm);
		background: transparent;
		color: var(--ink);
		font: inherit;
		font-size: 0.84rem;
		text-align: left;
		cursor: pointer;
	}
	.family-options button:hover,
	.family-options button.active { background: var(--surface-2); color: var(--plum-2); }
	.family-options button span { display: inline-flex; align-items: center; min-width: 0; }
	.family-options i,
	.clade-group h2 i {
		display: inline-block;
		width: 0.48rem;
		height: 0.48rem;
		margin-right: 0.4rem;
		border: 1px solid color-mix(in srgb, var(--ink) 18%, transparent);
		border-radius: 50%;
		flex: 0 0 auto;
	}
	.family-options small { color: var(--muted); font-size: 0.72rem; }
	.language-results { grid-area: results; min-width: 0; }
	.clade-group + .clade-group { margin-top: 1.35rem; }
	.clade-group > header {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 0.35rem;
		padding-bottom: 0.35rem;
		border-bottom: 1px solid var(--border-strong);
	}
	.clade-group h2 { display: flex; align-items: center; margin: 0; font-size: 1rem; }
	.clade-group > header span { color: var(--muted); font-size: 0.76rem; }
	.language-list { display: grid; }
	.language-row {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		gap: 0.45rem 1rem;
		padding: 0.62rem 0.7rem;
		border-left: 3px solid var(--language);
		border-bottom: 1px solid var(--border);
	}
	.language-row:hover { background: color-mix(in srgb, var(--plum-2) 3%, var(--surface)); }
	.language-main { display: grid; gap: 0.08rem; min-width: 0; color: var(--ink); }
	.language-main:hover { color: var(--plum-2); text-decoration: none; }
	.language-main strong { font-size: 1.02rem; }
	.language-main > span { color: var(--muted); font-size: 0.76rem; }
	.language-counts {
		display: flex;
		align-items: center;
		gap: 0.85rem;
		color: var(--muted);
		font-size: 0.76rem;
		white-space: nowrap;
	}
	.language-counts strong { color: var(--ink); font-variant-numeric: tabular-nums; }
	.dialect-hits {
		grid-column: 1 / -1;
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.35rem;
		padding: 0.35rem 0 0.15rem;
	}
	.dialect-hits a {
		display: grid;
		gap: 0.05rem;
		padding: 0.38rem 0.5rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--surface-2);
		color: var(--ink);
	}
	.dialect-hits a:hover { border-color: var(--plum-2); text-decoration: none; }
	.dialect-hits strong { font-size: 0.84rem; }
	.dialect-hits span { color: var(--muted); font-size: 0.72rem; }
	.more-hits { align-self: center; padding: 0.35rem 0.5rem; color: var(--muted); font-size: 0.76rem; }
	.atlas-map {
		grid-area: map;
		position: sticky;
		top: 4.75rem;
		min-width: 0;
	}
	.atlas-map > summary {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.5rem;
		padding: 0 0 0.4rem;
		font-weight: 700;
		cursor: pointer;
	}
	.atlas-map > summary span { color: var(--muted); font-size: 0.72rem; font-weight: 400; }
	.empty-state { padding: 2rem 0; }
	.empty-state h2 { margin-bottom: 0.25rem; }
	.empty-state p { margin: 0; color: var(--muted); }
	@media (max-width: 1080px) {
		.language-explorer {
			grid-template-areas: 'families results' 'map map';
			grid-template-columns: 13rem minmax(0, 1fr);
		}
		.atlas-map { position: static; margin-top: 0.75rem; }
		:global(.atlas-link) { display: inline-flex; }
	}
	@media (max-width: 720px) {
		.page-heading { display: block; }
		.page-heading .totals { margin-top: 0.35rem; }
		.language-explorer {
			grid-template-areas: 'families' 'results' 'map';
			grid-template-columns: 1fr;
			gap: 0.75rem;
		}
		.family-rail {
			position: static;
			max-height: none;
			overflow: visible;
			padding: 0;
			border-right: 0;
			border-bottom: 1px solid var(--border);
		}
		.family-toggle { cursor: pointer; }
		.family-options { display: none; max-height: 55vh; overflow-y: auto; padding-bottom: 0.6rem; }
		.family-rail.open .family-options { display: grid; }
		.language-row { grid-template-columns: 1fr; }
		.language-counts { justify-content: flex-start; }
		.dialect-hits { grid-template-columns: 1fr; }
		.atlas-map { scroll-margin-top: 4.5rem; }
	}
</style>
