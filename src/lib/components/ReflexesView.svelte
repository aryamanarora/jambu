<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { getFilterLanguages } from '$lib/query';
	import { PAGE_SIZE } from '$lib/types';
	import { safe, md } from '$lib/render';
	import { hashColor, cladeColor } from '$lib/clades';
	import FilterCell from './FilterCell.svelte';
	import type { SelectOption } from './SelectFilter.svelte';
	import RefList from './RefList.svelte';
	import Pager from './Pager.svelte';
	import Tags from './Tags.svelte';
	import TagFilter from './TagFilter.svelte';

	let {
		mode = 'reflexes',
		languageId
	}: { mode?: 'reflexes' | 'lexicon'; languageId?: string } = $props();

	const showLangCol = $derived(mode === 'reflexes');
	const list = createListState(mode, { languageId, withOrigin: true });
	const from = $derived(list.result ? (list.result.page - 1) * PAGE_SIZE + 1 : 0);
	const to = $derived(list.result ? from + list.result.rows.length - 1 : 0);

	let langOptions = $state<SelectOption[]>([]);
	$effect(() => {
		if (!showLangCol) return;
		getFilterLanguages('reflexes').then((ls) => {
			langOptions = ls.map((l) => ({
				value: l.id,
				label: l.name,
				sub: l.clade ?? '',
				swatch: cladeColor(l.clade)
			}));
		});
	});

	// origin-language picker options (etymon / borrowing-source languages) for the Origin column
	let originLangOptions = $state<SelectOption[]>([]);
	$effect(() => {
		getFilterLanguages('entries').then((ls) => {
			originLangOptions = ls.map((l) => ({
				value: l.id,
				label: l.name,
				sub: l.clade ?? '',
				swatch: cladeColor(l.clade)
			}));
		});
	});
</script>

<div class="showing-line">
	<div class="loader-slot">{#if list.loading}<div class="loader-line"></div>{/if}</div>
	{#if list.result}
		<p class="muted">
			Showing {from.toLocaleString()}–{to.toLocaleString()} of
			{list.result.count.toLocaleString()} reflexes.
		</p>
	{/if}
</div>

{#if list.error}<p style="color: var(--bad)">Query error: {list.error}</p>{/if}

<div class="table-wrap">
	<table class="data" class:accent-col={showLangCol}>
		<thead>
			<tr>
				{#if showLangCol}
					<FilterCell
						label="Language"
						filterKey="origin_lang"
						type="select"
						options={langOptions}
						sortKey="lang"
						value={list.params.origin_lang ?? ''}
						activeSort={list.params.sort ?? ''}
						onFilter={list.setFilter}
						onSort={list.setSort}
					/>
				{/if}
				<FilterCell
					label="Word"
					filterKey="word"
					sortKey="word"
					palette
					value={list.params.word ?? ''}
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Origin"
					filterKey="origin"
					sortKey="origin"
					palette
					value={list.params.origin ?? ''}
					pickerKey="etymon_lang"
					pickerOptions={originLangOptions}
					pickerValue={list.params.etymon_lang ?? ''}
					pickerPlaceholder="Origin lang"
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Gloss"
					filterKey="gloss"
					sortKey="gloss"
					palette
					value={list.params.gloss ?? ''}
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<TagFilter value={list.params.tags ?? ""} onFilter={list.setFilter} />
				<FilterCell
					label="Notes"
					filterKey="notes"
					sortKey="notes"
					palette
					value={list.params.notes ?? ''}
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Source"
					filterKey="source"
					sortKey="source"
					value={list.params.source ?? ''}
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
			</tr>
		</thead>
		<tbody>
			{#if list.result}
				{#each list.result.rows as r (r.id)}
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
							<a href="{base}/entries/{r.id}">{@html safe(r.word)}</a>{#if r.phonemic}
								<span class="phonemic">/&#8288;{r.phonemic}&#8288;/</span>{/if}{#if r.sub_count}
								<a
									class="subcount"
									href="{base}/entries/{r.id}"
									title="{r.sub_count} form{r.sub_count === 1 ? '' : 's'} borrowed from this word"
									>→&#8288;{r.sub_count}</a
								>{/if}
						</td>
						<td
							class:lang-cell={!showLangCol}
							style={!showLangCol
								? `border-left-color: ${hashColor(r.origin_lemma?.language?.color)}`
								: ''}
						>
							{#if r.origin_lemma}
								{#if r.origin_lemma.language}<span class="olang"
										>{r.origin_lemma.language.name}</span
									> {/if}<a class="origin" href="{base}/entries/{r.origin_lemma.id}"
									>{@html safe(r.origin_lemma.word)} <span class="id-tag">[{r.origin_lemma.id}]</span
									></a
								>
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

{#if list.result}
	<Pager count={list.result.count} page={list.result.page} onpage={list.setPage} />
{/if}

<style>
	.showing-line {
		margin-top: 0.5rem;
	}
	/* headword/form is the focus of each row, matching the entries table */
	.lemma-word a {
		font-family: var(--font-serif);
		font-size: 1.12rem;
		font-weight: 600;
	}
	/* origin etymon: serif term with its (proto-)language muted just before it, like "Reflex of X" */
	.origin {
		font-family: var(--font-serif);
	}
	.olang {
		color: var(--muted);
		font-size: 0.9em;
		margin-right: 0.35rem;
	}
	/* borrowed-descendant count: forms in other languages borrowed FROM this reflex */
	.subcount {
		display: inline-block;
		margin-left: 0.35rem;
		padding: 0 0.3rem;
		border-radius: 999px;
		font-family: var(--font-sans);
		font-size: 0.72rem;
		font-weight: 600;
		background: color-mix(in srgb, var(--berry) 12%, transparent);
		color: var(--berry);
		white-space: nowrap;
		vertical-align: middle;
	}
	.loader-slot {
		height: 3px;
		margin-bottom: 0.4rem;
	}
</style>
