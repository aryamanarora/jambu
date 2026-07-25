<script lang="ts">
	import { base } from '$app/paths';
	import { etymonSlotColor } from '$lib/etyma';
	import type { ConceptRow } from '$lib/types';

	let { data } = $props();
	const concepts = data.concepts as ConceptRow[];

	let search = $state('');
	let category = $state('all');
	let sort = $state('etyma');

	const categories = $derived(['all', ...new Set(concepts.map((c) => c.category).filter(Boolean))]);

	const filtered = $derived.by(() => {
		const q = search.trim().toLowerCase();
		let rows = concepts.filter(
			(c) =>
				(category === 'all' || c.category === category) &&
				(!q || c.name.toLowerCase().includes(q))
		);
		const key = sort as keyof ConceptRow;
		rows = [...rows].sort((a, b) =>
			sort === 'name'
				? a.name.localeCompare(b.name)
				: (Number(b[key]) || 0) - (Number(a[key]) || 0)
		);
		return rows;
	});

	// total forms behind a concept's shown bar (segments + remainder + unetymologised), for widths
	const barTotal = (c: ConceptRow) =>
		Math.max(1, (c.bars ?? []).reduce((s, b) => s + b.n, 0) + (c.rest ?? 0) + (c.unetym_count ?? 0));
</script>

<svelte:head>
	<title>Concepts — Jambu</title>
	<meta
		name="description"
		content="Browse {concepts.length} Concepticon concepts and see which etymological sources across languages express each one."
	/>
</svelte:head>

<h1 class="headword">Concepts</h1>
<p class="lede">
	{concepts.length.toLocaleString()} Concepticon concepts mapped from glosses. For each, see the etyma
	— and their dictionary sources — used across the languages of Jambu to express it.
</p>

<div class="controls">
	<input class="search" placeholder="Search concepts…" bind:value={search} />
	<select bind:value={category}>
		{#each categories as c}
			<option value={c}>{c === 'all' ? 'All categories' : c}</option>
		{/each}
	</select>
	<select bind:value={sort}>
		<option value="etyma">Sort: etyma</option>
		<option value="lang">Sort: languages</option>
		<option value="form">Sort: forms</option>
		<option value="name">Sort: name</option>
	</select>
	<span class="count">{filtered.length.toLocaleString()} shown</span>
</div>

<div class="table-wrap">
	<table class="data accent-col">
		<thead>
			<tr>
				<th>Concept</th>
				<th>Category</th>
				<th class="numeric">Etyma</th>
				<th class="numeric">Langs</th>
				<th class="dist-col">Distribution of forms</th>
			</tr>
		</thead>
		<tbody>
			{#each filtered as c (c.id)}
				<tr>
					<td class="name-cell"><a href="{base}/concepts/{c.id}">{c.name}</a></td>
					<td class="muted">{c.category}</td>
					<td class="numeric">{c.etyma_count.toLocaleString()}</td>
					<td class="numeric">{c.lang_count.toLocaleString()}</td>
					<td class="dist-col">
						{#if c.bars?.length}
							{@const total = barTotal(c)}
							<div class="cbar">
								{#each c.bars as b, i (b.etymon)}
									<a
										class="eref cseg"
										data-eref={b.etymon}
										href="{base}/entries/{b.etymon}"
										style="width: {(100 * b.n) / total}%; background: {etymonSlotColor(i)}"
										aria-label="{b.etymon} ({b.n})"
									></a>
								{/each}
								{#if c.rest}
									<span
										class="cseg rest"
										style="width: {(100 * c.rest) / total}%"
										title="{c.rest} more"
									></span>
								{/if}
								{#if c.unetym_count}
									<span
										class="cseg unetym"
										style="width: {(100 * c.unetym_count) / total}%"
										title="{c.unetym_count} unetymologised"
									></span>
								{/if}
							</div>
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.lede {
		color: var(--muted);
		max-width: 60ch;
		margin: 0.4rem 0 1.2rem;
	}
	.controls {
		display: flex;
		gap: 0.6rem;
		align-items: center;
		flex-wrap: wrap;
		margin-bottom: 1rem;
	}
	.search {
		flex: 1;
		min-width: 12rem;
		padding: 0.45rem 0.7rem;
		border: 1px solid var(--border);
		border-radius: 6px;
		background: var(--bg);
		color: inherit;
	}
	.controls select {
		padding: 0.45rem 0.6rem;
		border: 1px solid var(--border);
		border-radius: 6px;
		background: var(--bg);
		color: inherit;
	}
	.count {
		color: var(--muted);
		font-size: 0.85rem;
	}
	.table-wrap {
		overflow-x: auto;
	}
	.name-cell a {
		font-weight: 600;
	}
	.dist-col {
		width: 40%;
		min-width: 14rem;
	}
	.cbar {
		display: flex;
		height: 15px;
		border-radius: 3px;
		overflow: hidden;
		background: var(--border);
	}
	.cseg {
		display: block;
		height: 100%;
		min-width: 2px;
	}
	.cseg:hover {
		filter: brightness(1.12);
		outline: 1px solid rgba(0, 0, 0, 0.35);
		outline-offset: -1px;
	}
	.cseg.rest {
		background: repeating-linear-gradient(
			45deg,
			var(--muted, #9a958c),
			var(--muted, #9a958c) 3px,
			transparent 3px,
			transparent 6px
		);
	}
	/* forms with this meaning that aren't linked to an etymon — solid neutral, matching the
	   unetymologised markers on the per-concept map */
	.cseg.unetym {
		background: #9a958c;
	}
</style>
