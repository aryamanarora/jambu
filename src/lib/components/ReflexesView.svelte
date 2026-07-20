<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { PAGE_SIZE } from '$lib/types';
	import { safe, md } from '$lib/render';
	import { hashColor } from '$lib/clades';
	import FilterCell from './FilterCell.svelte';
	import RefList from './RefList.svelte';
	import Pager from './Pager.svelte';
	import Tags from './Tags.svelte';

	let {
		mode = 'reflexes',
		languageId
	}: { mode?: 'reflexes' | 'lexicon'; languageId?: string } = $props();

	const showLangCol = $derived(mode === 'reflexes');
	const state = createListState(mode, { languageId, withOrigin: true });
	const from = $derived(state.result ? (state.result.page - 1) * PAGE_SIZE + 1 : 0);
	const to = $derived(state.result ? from + state.result.rows.length - 1 : 0);
</script>

<div class="showing-line">
	<div class="loader-slot">{#if state.loading}<div class="loader-line"></div>{/if}</div>
	{#if state.result}
		<p class="muted">
			Showing {from.toLocaleString()}–{to.toLocaleString()} of
			{state.result.count.toLocaleString()} reflexes.
		</p>
	{/if}
</div>

{#if state.error}<p style="color: var(--bad)">Query error: {state.error}</p>{/if}

<div class="table-wrap">
	<table class="data">
		<thead>
			<tr>
				{#if showLangCol}
					<FilterCell
						label="Language"
						filterKey="lang"
						sortKey="lang"
						value={state.params.lang ?? ''}
						activeSort={state.params.sort ?? ''}
						onFilter={state.setFilter}
						onSort={state.setSort}
					/>
				{/if}
				<FilterCell
					label="Word"
					filterKey="word"
					sortKey="word"
					palette
					value={state.params.word ?? ''}
					activeSort={state.params.sort ?? ''}
					onFilter={state.setFilter}
					onSort={state.setSort}
				/>
				<FilterCell
					label="Origin"
					filterKey="origin"
					sortKey="origin"
					palette
					value={state.params.origin ?? ''}
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
				<th>Tags</th>
				<FilterCell
					label="Notes"
					filterKey="notes"
					sortKey="notes"
					palette
					value={state.params.notes ?? ''}
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
			</tr>
		</thead>
		<tbody>
			{#if state.result}
				{#each state.result.rows as r (r.id)}
					<tr>
						{#if showLangCol}
							<td class="lang-cell" style="border-left-color: {hashColor(r.language?.color)}">
								<a href="{base}/languages/{r.language_id}"
									>{r.language?.language}{#if r.language?.dialect}: <span class="font-thin"
											>{r.language.dialect}</span
										>{/if}</a
								>
							</td>
						{/if}
						<td class="lemma-word">
							<a href="{base}/reflexes/{r.id}">{@html safe(r.word)}</a>{#if r.phonemic}
								<span class="phonemic">/&#8288;{r.phonemic}&#8288;/</span>{/if}
						</td>
						<td
							class:lang-cell={!showLangCol}
							style={!showLangCol
								? `border-left-color: ${hashColor(r.origin_lemma?.language?.color)}`
								: ''}
						>
							{#if r.origin_lemma}
								<a href="{base}/entries/{r.origin_lemma.id}"
									>{@html safe(r.origin_lemma.word)} <span class="id-tag">[{r.origin_lemma.id}]</span
									></a
								>
								{#if !showLangCol && r.origin_lemma.language}
									<div><small class="muted">{r.origin_lemma.language.name}</small></div>
								{/if}
							{:else}<span class="faint">—</span>{/if}
						</td>
						<td class="muted">{@html safe(r.gloss) || '—'}</td>
						<td><Tags tags={r.tags} /></td>
						<td class="muted markdown">{@html md(r.notes)}</td>
						<td><RefList references={r.references} /></td>
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
</style>
