<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { hashColor } from '$lib/clades';
	import type { MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';

	let { data } = $props();

	let langFilter = $state('');
	let cladeFilter = $state('');
	let sortKey = $state<'name' | 'clade' | 'reflexes'>('name');
	let sortDir = $state<'asc' | 'desc'>('asc');
	let showTooltips = $state(false);

	function setSort(key: 'name' | 'clade' | 'reflexes', dir: 'asc' | 'desc') {
		sortKey = key;
		sortDir = dir;
	}

	const filtered = $derived(
		data.languages
			.filter(
				(l) =>
					(!langFilter || l.name.toLowerCase().includes(langFilter.toLowerCase())) &&
					(!cladeFilter || (l.clade ?? '').toLowerCase().includes(cladeFilter.toLowerCase()))
			)
			.sort((a, b) => {
				let cmp = 0;
				if (sortKey === 'name') cmp = a.name.localeCompare(b.name);
				else if (sortKey === 'clade') cmp = (a.clade ?? '').localeCompare(b.clade ?? '');
				else cmp = a.lemma_count - b.lemma_count;
				if (cmp === 0) cmp = a.order - b.order;
				return sortDir === 'asc' ? cmp : -cmp;
			})
	);

	const markers = $derived<MapMarker[]>(
		filtered
			.filter((l) => l.lat != null && l.long != null)
			.map((l) => ({
				lat: l.lat,
				long: l.long,
				svg: l.map_marker,
				tooltip: `${l.name} (${l.lemma_count})`,
				onClick: () => goto(`${base}/languages/${l.id}`)
			}))
	);

</script>

{#snippet sortArrows(key: 'name' | 'clade' | 'reflexes')}
	<span class="sort">
		<button
			class="up"
			class:active={sortKey === key && sortDir === 'asc'}
			aria-label="Sort ascending"
			onclick={() => setSort(key, 'asc')}
		></button>
		<button
			class="down"
			class:active={sortKey === key && sortDir === 'desc'}
			aria-label="Sort descending"
			onclick={() => setSort(key, 'desc')}
		></button>
	</span>
{/snippet}

<svelte:head>
	<title>Languages — Jambu</title>
	<meta name="description" content="The {data.languages.length} languages of the Jambu etymological dictionary of South Asia, with a map and reflex counts." />
</svelte:head>

<h1>Languages</h1>

<Map {markers} height="500px" showAllTooltips={showTooltips} />
<label class="tooltip-toggle">
	<input type="checkbox" bind:checked={showTooltips} /> Show all labels
</label>

<p class="muted">Showing {filtered.length.toLocaleString()} of {data.languages.length.toLocaleString()} languages.</p>

<div class="table-wrap">
	<table class="data accent-col">
		<thead>
			<tr>
				<th>
					<div class="field">
						<div class="filter-box">
							<input class="search-box" placeholder="Language" bind:value={langFilter} />
						</div>
						{@render sortArrows('name')}
					</div>
				</th>
				<th>
					<div class="field">
						<div class="filter-box">
							<input class="search-box" placeholder="Clade" bind:value={cladeFilter} />
						</div>
						{@render sortArrows('clade')}
					</div>
				</th>
				<th>
					<div class="field"><span>Coordinates</span></div>
				</th>
				<th class="numeric">
					<div class="field"><span>Reflexes</span>{@render sortArrows('reflexes')}</div>
				</th>
			</tr>
		</thead>
		<tbody>
			{#each filtered as l (l.id)}
				<tr>
					<td class="lang-cell" style="border-left-color: {hashColor(l.color)}">
						<a href="{base}/languages/{l.id}"
							>{l.language}{#if l.dialect}: <span class="font-thin">{l.dialect}</span>{/if}</a
						>
						<span class="id-tag">[{l.id}]</span>
					</td>
					<td>{l.clade}</td>
					<td class="muted">{l.lat?.toFixed(2)}, {l.long?.toFixed(2)}</td>
					<td>{l.lemma_count.toLocaleString()}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.tooltip-toggle {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		margin: 0.5rem 0;
		font-size: 0.9rem;
		color: var(--muted);
	}
</style>
