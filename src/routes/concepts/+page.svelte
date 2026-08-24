<script lang="ts">
	import { base } from '$app/paths';
	import { etymonSlotColor } from '$lib/etyma';
	import type { ConceptBarGroup, ConceptRow } from '$lib/types';
	import ListToolbar from '$lib/components/ListToolbar.svelte';

	let { data } = $props();
	const concepts = data.concepts as ConceptRow[];

	let search = $state('');
	let category = $state('all');
	let sort = $state('etyma');
	let splitByReflexFamily = $state(false);

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
	const groupTotal = (group: ConceptBarGroup) =>
		group.bars.reduce((sum, bar) => sum + bar.n, 0) + group.rest + group.unetym_count;
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

{#snippet filters()}
	<label class="filter-control">
		<span>Category</span>
		<select bind:value={category}>
			{#each categories as c}
				<option value={c}>{c === 'all' ? 'All categories' : c}</option>
			{/each}
		</select>
	</label>
	<label class="filter-control">
		<span>Sort results</span>
		<select bind:value={sort}>
			<option value="etyma">Most etyma</option>
			<option value="lang">Most languages</option>
			<option value="form">Most forms</option>
			<option value="name">Concept name</option>
		</select>
	</label>
	<label class="toggle">
		<input type="checkbox" bind:checked={splitByReflexFamily} />
		Split distributions by language family
	</label>
{/snippet}

<ListToolbar
	value={search}
	placeholder="Search concepts…"
	searchLabel="Search concepts"
	resultLabel={`${filtered.length.toLocaleString()} concepts`}
	filterCount={(category !== 'all' ? 1 : 0) + (splitByReflexFamily ? 1 : 0)}
	onSearch={(value) => (search = value)}
	{filters}
/>

<div class="table-wrap">
	<table class="data accent-col mobile-cards">
		<thead>
			<tr>
				<th>Concept</th>
				<th>Category</th>
				<th class="numeric">Etyma</th>
				<th class="numeric">Langs</th>
				<th class="dist-col">
					Distribution of forms
					{#if splitByReflexFamily}
						<span class="family-headings" aria-hidden="true">
							<span>Indo-Iranian</span><span>Dravidian</span><span>Other</span>
						</span>
					{/if}
				</th>
			</tr>
		</thead>
		<tbody>
			{#each filtered as c (c.id)}
				<tr>
					<td class="name-cell"><a href="{base}/concepts/{c.id}">{c.name}</a></td>
					<td class="muted" data-label="Category">{c.category}</td>
					<td class="numeric" data-label="Etyma">{c.etyma_count.toLocaleString()}</td>
					<td class="numeric" data-label="Languages">{c.lang_count.toLocaleString()}</td>
					<td class="dist-col" data-label="Distribution">
						{#if splitByReflexFamily && c.reflex_family_bars}
							<div class="family-bars">
								{#each c.reflex_family_bars as group (group.family)}
									{@const total = groupTotal(group)}
									<div
										class="cbar family-track"
										title="{group.family}: {total.toLocaleString()} reflex forms"
									>
										{#if total}
											<div class="family-fill">
												{#each group.bars as b, i (b.etymon)}
													<a
														class="eref cseg"
														data-eref={b.etymon}
														href="{base}/entries/{b.etymon}"
														style="width: {(100 * b.n) / total}%; background: {etymonSlotColor(i)}"
														aria-label="{b.etymon}: {b.n} {group.family} reflex forms"
													></a>
												{/each}
												{#if group.rest}
													<span
														class="cseg rest"
														style="width: {(100 * group.rest) / total}%"
														title="{group.rest} more"
													></span>
												{/if}
												{#if group.unetym_count}
													<span
														class="cseg unetym"
														style="width: {(100 * group.unetym_count) / total}%"
														title="{group.unetym_count} unetymologised"
													></span>
												{/if}
											</div>
										{/if}
									</div>
								{/each}
							</div>
						{:else if c.bars?.length}
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
	.filter-control {
		display: grid;
		gap: 0.3rem;
		color: var(--muted);
		font-size: 0.76rem;
		font-weight: 600;
	}
	.filter-control select {
		width: 100%;
		min-height: 38px;
		padding: 0.45rem 0.6rem;
		border: 1px solid var(--border);
		border-radius: 6px;
		background: var(--bg);
		color: inherit;
	}
	.toggle {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		white-space: nowrap;
		font-size: 0.9rem;
	}
	.toggle input {
		margin: 0;
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
	.family-headings,
	.family-bars {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 5px;
	}
	.family-headings {
		margin-top: 0.3rem;
		font-size: 0.68rem;
		font-weight: 500;
		color: var(--muted);
		text-align: center;
	}
	.cbar {
		display: flex;
		height: 15px;
		border-radius: 3px;
		overflow: hidden;
		background: var(--border);
	}
	.family-track {
		min-width: 0;
	}
	.family-fill {
		display: flex;
		width: 100%;
		height: 100%;
		overflow: hidden;
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
	@media (max-width: 640px) {
		.toggle {
			min-height: 42px;
			white-space: normal;
		}
		.cbar {
			height: 28px;
		}
		.family-bars {
			gap: 8px;
		}
	}
</style>
