<script lang="ts">
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import { compareLanguages, type CompareRow } from '$lib/query';
	import { safe, striptags } from '$lib/render';
	import type { Language, MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';

	let lang1 = $state<Language | null>(null);
	let lang2 = $state<Language | null>(null);
	let rows = $state<CompareRow[]>([]);
	let loading = $state(true);

	const ids = $derived([page.params.lang1 ?? '', page.params.lang2 ?? ''] as const);

	$effect(() => {
		const [a, b] = ids;
		loading = true;
		compareLanguages(a, b).then((r) => {
			lang1 = r.lang1;
			lang2 = r.lang2;
			rows = r.rows;
			loading = false;
		});
	});

	const markers = $derived<MapMarker[]>(
		[lang1, lang2]
			.filter((l): l is Language => !!l && l.lat != null)
			.map((l) => ({ lat: l.lat, long: l.long, svg: l.map_marker, tooltip: l.name }))
	);

	function pct(l: Language | null): string {
		if (!l || !l.lemma_count) return '';
		return ((rows.length / l.lemma_count) * 100).toFixed(2) + '%';
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
	<h1 class="headword">{lang1.name} vs. {lang2.name} <span class="id-tag">({rows.length} shared)</span></h1>

	<div class="compare-head">
		{#if markers.length}<div class="cmp-map"><Map {markers} zoom={4} height="240px" /></div>{/if}
		{#each [lang1, lang2] as l (l.id)}
			<table class="props card">
				<tbody>
					<tr><th colspan="2"><a href="{base}/languages/{l.id}">{l.name}</a></th></tr>
					<tr><th>Family</th><td>{l.clade}</td></tr>
					<tr><th>Reflexes</th><td>{l.lemma_count.toLocaleString()} <span class="muted">({pct(l)} shared)</span></td></tr>
				</tbody>
			</table>
		{/each}
	</div>

	<div class="table-wrap">
		<table class="data">
			<thead>
				<tr><th>Entry</th><th>{lang1.name}</th><th>{lang2.name}</th></tr>
			</thead>
			<tbody>
				{#each rows as row (row.entryId)}
					<tr>
						<td class="lemma-word">
							<a href="{base}/entries/{row.entryId}">{@html safe(row.entryWord)}</a>
							<span class="id-tag">[{row.entryId}]</span>
						</td>
						<td class="lemma-word">
							{#each row.left as r, i (r.id)}{#if i > 0}, {/if}<a href="{base}/reflexes/{r.id}"
									>{@html safe(r.word)}</a
								>{#if r.gloss} <span class="muted">‘{striptags(r.gloss)}’</span>{/if}{/each}
						</td>
						<td class="lemma-word">
							{#each row.right as r, i (r.id)}{#if i > 0}, {/if}<a href="{base}/reflexes/{r.id}"
									>{@html safe(r.word)}</a
								>{#if r.gloss} <span class="muted">‘{striptags(r.gloss)}’</span>{/if}{/each}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<style>
	.compare-head {
		display: grid;
		grid-template-columns: 1.4fr 1fr 1fr;
		gap: 1rem;
		align-items: start;
		margin-top: 1rem;
	}
	.compare-head .props {
		padding: 0.5rem 0.9rem;
	}
	@media (max-width: 820px) {
		.compare-head {
			grid-template-columns: 1fr;
		}
	}
</style>
