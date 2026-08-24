<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { hashColor } from '$lib/clades';
	import type { Dialect, Language, MapMarker } from '$lib/types';
	import Map from './Map.svelte';

	let {
		language,
		dialects,
		selectedToken = ''
	}: {
		language: Language;
		dialects: Dialect[];
		selectedToken?: string;
	} = $props();

	let search = $state('');
	let sort = $state<'coverage' | 'name'>('coverage');
	let showAll = $state(false);

	const filtered = $derived.by(() => {
		const query = search.trim().toLowerCase();
		return dialects
			.filter((dialect) =>
				query
					? [dialect.name, dialect.location, dialect.id, dialect.glottocode, dialect.quality]
							.filter(Boolean)
							.some((value) => value!.toLowerCase().includes(query))
					: true
			)
			.sort((a, b) =>
				sort === 'coverage'
					? b.lemma_count - a.lemma_count || a.name.localeCompare(b.name)
					: a.name.localeCompare(b.name) || b.lemma_count - a.lemma_count
			);
	});
	const visible = $derived(showAll || search ? filtered : filtered.slice(0, 18));
	const selectedDialect = $derived(dialects.find((dialect) => dialect.token === selectedToken));
	const mappedCount = $derived(filtered.filter((dialect) => dialect.lat != null && dialect.long != null).length);
	const markers: MapMarker[] = $derived(
		filtered
			.filter((dialect) => dialect.lat != null && dialect.long != null)
			.map((dialect) => ({
				lat: dialect.lat!,
				long: dialect.long!,
				svg: language.map_marker,
				color: hashColor(dialect.color ?? language.color),
				radius: 6,
				ring: dialect.token === selectedToken,
				tooltip: `${language.name}: ${dialect.name} · ${dialect.lemma_count.toLocaleString()} forms`,
				onClick: () => goto(dialectHref(dialect))
			}))
	);

	function dialectHref(dialect: Dialect): string {
		return `${base}/languages/${language.id}?dialect=${encodeURIComponent(dialect.token)}#lexicon`;
	}
</script>

<section id="dialects" class="dialect-browser" aria-labelledby="dialect-heading">
	<header class="dialect-heading">
		<div>
			<h2 id="dialect-heading">Dialects</h2>
			<p>{dialects.length.toLocaleString()} represented · {dialects.filter((dialect) => dialect.lat != null).length.toLocaleString()} mapped</p>
		</div>
		<a href="#lexicon">Jump to lexicon</a>
	</header>

	{#if selectedDialect}
		<div class="active-dialect">
			<span>Lexicon filtered to <strong>{selectedDialect.name}</strong></span>
			<a href={`${base}/languages/${language.id}#lexicon`}>Show all forms</a>
		</div>
	{/if}

	<div class="dialect-controls">
		<label>
			<span class="visually-hidden">Search dialects</span>
			<input type="search" placeholder="Search dialects or locations…" bind:value={search} />
		</label>
		<div class="sort-toggle" aria-label="Sort dialects">
			<button class:active={sort === 'coverage'} type="button" onclick={() => (sort = 'coverage')}>Coverage</button>
			<button class:active={sort === 'name'} type="button" onclick={() => (sort = 'name')}>Name</button>
		</div>
		<span class="dialect-result">{filtered.length.toLocaleString()} dialect{filtered.length === 1 ? '' : 's'}</span>
	</div>

	<div class="dialect-layout">
		<div class="dialect-list">
			{#if visible.length === 0}
				<p class="dialect-empty">No dialects match that search.</p>
			{:else}
				{#each visible as dialect (dialect.token)}
					<a
						class:selected={dialect.token === selectedToken}
						class="dialect-row"
						href={dialectHref(dialect)}
					>
						<span class="dialect-name">
							<strong>{dialect.name}</strong>
							<small>{dialect.location || 'Location not recorded'}</small>
						</span>
						<span class="dialect-stats">
							<strong>{dialect.lemma_count.toLocaleString()}</strong> forms
							{#if dialect.quality}<small title="Survey quality">quality {dialect.quality}</small>{/if}
						</span>
					</a>
				{/each}
			{/if}
			{#if !search && !showAll && filtered.length > visible.length}
				<button class="show-all" type="button" onclick={() => (showAll = true)}>
					Show all {filtered.length.toLocaleString()} dialects
				</button>
			{/if}
		</div>

		<div class="dialect-map">
			<div class="map-label">
				<strong>Dialect atlas</strong><span>{mappedCount.toLocaleString()} visible locations</span>
			</div>
			{#if markers.length}
				<Map {markers} height="420px" />
			{:else}
				<div class="no-map">No coordinates recorded for this selection.</div>
			{/if}
		</div>
	</div>

	<details class="technical-dialects">
		<summary>Technical metadata for all dialects</summary>
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
</section>

<style>
	.dialect-browser {
		scroll-margin-top: 4.5rem;
		margin: 1.5rem 0;
		padding-top: 0.25rem;
	}
	.dialect-heading,
	.dialect-controls,
	.map-label,
	.active-dialect {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}
	.dialect-heading { align-items: flex-end; margin-bottom: 0.75rem; }
	.dialect-heading h2 { margin: 0; }
	.dialect-heading p { margin: 0.15rem 0 0; color: var(--muted); font-size: 0.84rem; }
	.dialect-heading > a { font-size: 0.82rem; font-weight: 600; }
	.active-dialect {
		margin-bottom: 0.7rem;
		padding: 0.55rem 0.7rem;
		border-left: 3px solid var(--berry);
		background: color-mix(in srgb, var(--plum-2) 6%, var(--surface));
		font-size: 0.84rem;
	}
	.active-dialect a { white-space: nowrap; font-weight: 600; }
	.dialect-controls {
		justify-content: flex-start;
		padding: 0.65rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--surface-2);
	}
	.dialect-controls label { flex: 1 1 22rem; }
	.dialect-controls input {
		width: 100%;
		min-height: 40px;
		padding: 0.5rem 0.7rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--ink);
		font: inherit;
	}
	.dialect-controls input:focus {
		outline: 3px solid color-mix(in srgb, var(--berry) 16%, transparent);
		border-color: var(--plum-2);
	}
	.sort-toggle {
		display: inline-flex;
		padding: 2px;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		background: var(--surface);
	}
	.sort-toggle button {
		padding: 0.28rem 0.65rem;
		border: 0;
		border-radius: 999px;
		background: transparent;
		color: var(--muted);
		font: inherit;
		font-size: 0.76rem;
		cursor: pointer;
	}
	.sort-toggle button.active { background: var(--plum); color: white; }
	.dialect-result { margin-left: auto; color: var(--muted); font-size: 0.78rem; white-space: nowrap; }
	.dialect-layout {
		display: grid;
		grid-template-columns: minmax(18rem, 1fr) minmax(22rem, 0.95fr);
		gap: 1rem;
		align-items: start;
		margin-top: 0.85rem;
	}
	.dialect-list {
		display: grid;
		align-content: start;
		max-height: 460px;
		overflow-y: auto;
		border-top: 1px solid var(--border);
	}
	.dialect-row {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		gap: 0.75rem;
		padding: 0.55rem 0.65rem;
		border-bottom: 1px solid var(--border);
		color: var(--ink);
	}
	.dialect-row:hover,
	.dialect-row.selected { background: color-mix(in srgb, var(--plum-2) 6%, var(--surface)); text-decoration: none; }
	.dialect-row.selected { box-shadow: inset 3px 0 var(--berry); }
	.dialect-name,
	.dialect-stats { display: grid; gap: 0.06rem; min-width: 0; }
	.dialect-name strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.dialect-name small,
	.dialect-stats small { color: var(--muted); font-size: 0.72rem; }
	.dialect-stats { text-align: right; color: var(--muted); font-size: 0.72rem; white-space: nowrap; }
	.dialect-stats strong { color: var(--ink); font-size: 0.84rem; font-variant-numeric: tabular-nums; }
	.show-all {
		padding: 0.65rem;
		border: 0;
		border-bottom: 1px solid var(--border);
		background: transparent;
		color: var(--plum-2);
		font: inherit;
		font-size: 0.82rem;
		font-weight: 600;
		cursor: pointer;
	}
	.map-label { align-items: baseline; margin-bottom: 0.35rem; }
	.map-label span { color: var(--muted); font-size: 0.74rem; }
	.no-map { display: grid; place-items: center; min-height: 240px; border: 1px dashed var(--border-strong); color: var(--muted); }
	.dialect-empty { padding: 1rem 0.65rem; color: var(--muted); }
	.technical-dialects { margin-top: 0.85rem; border-bottom: 1px solid var(--border); }
	.technical-dialects > summary { padding: 0.6rem 0; color: var(--muted); font-size: 0.78rem; cursor: pointer; }
	.technical-dialects .table-wrap { max-height: 65vh; margin-bottom: 0.8rem; }
	.technical-dialects table { font-size: 0.78rem; }
	@media (max-width: 820px) {
		.dialect-layout { grid-template-columns: 1fr; }
		.dialect-list { max-height: 420px; }
	}
	@media (max-width: 640px) {
		.dialect-heading { align-items: flex-start; }
		.dialect-heading > a { display: none; }
		.dialect-controls { flex-wrap: wrap; }
		.dialect-controls label { flex-basis: 100%; }
		.dialect-result { order: 3; width: 100%; margin-left: 0; }
		.active-dialect { align-items: flex-start; }
	}
</style>
