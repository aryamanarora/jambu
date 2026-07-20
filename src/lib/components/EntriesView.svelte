<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { PAGE_SIZE } from '$lib/types';
	import { safe } from '$lib/render';
	import { hashColor } from '$lib/clades';
	import FilterCell from './FilterCell.svelte';
	import CladeBars from './CladeBars.svelte';
	import RefList from './RefList.svelte';
	import Pager from './Pager.svelte';

	const state = createListState('entries');
	const from = $derived(state.result ? (state.result.page - 1) * PAGE_SIZE + 1 : 0);
	const to = $derived(state.result ? from + state.result.rows.length - 1 : 0);
</script>

<div class="showing-line">
	<div class="loader-slot">{#if state.loading}<div class="loader-line"></div>{/if}</div>
	{#if state.result}
		<p class="muted">
			Showing {from.toLocaleString()}–{to.toLocaleString()} of
			{state.result.count.toLocaleString()} entries.
		</p>
	{/if}
</div>

{#if state.error}
	<p style="color: var(--bad)">Query error: {state.error}</p>
{/if}

<div class="table-wrap">
	<table class="data">
		<thead>
			<tr>
				<FilterCell
					label="Language"
					filterKey="lang"
					sortKey="lang"
					value={state.params.lang ?? ''}
					activeSort={state.params.sort ?? ''}
					onFilter={state.setFilter}
					onSort={state.setSort}
				/>
				<FilterCell
					label="Entry"
					filterKey="word"
					sortKey="word"
					palette
					value={state.params.word ?? ''}
					activeSort={state.params.sort ?? ''}
					onFilter={state.setFilter}
					onSort={state.setSort}
				/>
				<FilterCell
					label="Gloss"
					filterKey="gloss"
					sortKey="gloss"
					palette
					value={state.params.gloss ?? ''}
					activeSort={state.params.sort ?? ''}
					onFilter={state.setFilter}
					onSort={state.setSort}
				/>
				<FilterCell
					label="Source"
					filterKey="source"
					sortKey="source"
					value={state.params.source ?? ''}
					activeSort={state.params.sort ?? ''}
					onFilter={state.setFilter}
					onSort={state.setSort}
				/>
				<FilterCell
					label="Langs"
					sortKey="nlang"
					numeric
					activeSort={state.params.sort ?? ''}
					onFilter={state.setFilter}
					onSort={state.setSort}
				/>
				<FilterCell
					label="Reflexes"
					sortKey="nreflex"
					numeric
					activeSort={state.params.sort ?? ''}
					onFilter={state.setFilter}
					onSort={state.setSort}
				/>
			</tr>
		</thead>
		<tbody>
			{#if state.result}
				{#each state.result.rows as e (e.id)}
					<tr>
						<td class="lang-cell" style="border-left-color: {hashColor(e.language?.color)}">
							<div class="lang-inner">
								<span>
									{e.language?.language}{#if e.language?.dialect}: <span class="font-thin"
											>{e.language.dialect}</span
										>{/if}
								</span>
								<CladeBars clades={e.clades} />
							</div>
						</td>
						<td class="lemma-word">
							<a href="{base}/entries/{e.id}">{@html safe(e.word)}</a>
							<span class="id-tag">[{e.id}]</span>
						</td>
						<td class="muted">{@html safe(e.gloss) || '—'}</td>
						<td><RefList references={e.references} /></td>
						<td class="num">{e.lang_count?.toLocaleString() ?? ''}</td>
						<td class="num">{e.reflex_count?.toLocaleString() ?? ''}</td>
					</tr>
				{/each}
			{/if}
		</tbody>
	</table>
</div>

{#if state.result}
	<Pager count={state.result.count} page={state.result.page} onpage={state.setPage} />
{/if}

<style>
	.showing-line {
		margin-top: 0.5rem;
	}
	.loader-slot {
		height: 3px;
		margin-bottom: 0.4rem;
	}
	.lang-inner {
		display: flex;
		flex-direction: column;
		gap: 3px;
	}
	.num {
		text-align: right;
		white-space: nowrap;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
	}
</style>
