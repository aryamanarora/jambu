<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { getFilterLanguages } from '$lib/query';
	import { PAGE_SIZE } from '$lib/types';
	import { safe } from '$lib/render';
	import { hashColor, cladeColor } from '$lib/clades';
	import FilterCell from './FilterCell.svelte';
	import type { SelectOption } from './SelectFilter.svelte';
	import CladeBars from './CladeBars.svelte';
	import RefList from './RefList.svelte';
	import Pager from './Pager.svelte';

	const list = createListState('entries');
	const from = $derived(list.result ? (list.result.page - 1) * PAGE_SIZE + 1 : 0);
	const to = $derived(list.result ? from + list.result.rows.length - 1 : 0);
	// variant word forms arrive \x1f-separated from group_concat (see query.ts)
	const variantList = (s?: string | null): string[] => (s ? [...new Set(s.split(''))] : []);

	let langOptions = $state<SelectOption[]>([]);
	$effect(() => {
		getFilterLanguages('entries').then((ls) => {
			langOptions = ls.map((l) => ({
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
			{list.result.count.toLocaleString()} entries.
		</p>
	{/if}
</div>

{#if list.error}
	<p style="color: var(--bad)">Query error: {list.error}</p>
{/if}

<div class="table-wrap">
	<table class="data accent-col">
		<thead>
			<tr>
				<FilterCell
					label="Entry"
					filterKey="word"
					sortKey="word"
					palette
					value={list.params.word ?? ''}
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
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
				<FilterCell
					label="Etymology"
					filterKey="etymology"
					palette
					value={list.params.etymology ?? ''}
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Langs"
					sortKey="nlang"
					numeric
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Reflexes"
					sortKey="nreflex"
					numeric
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Derived"
					sortKey="nderived"
					numeric
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
				{#each list.result.rows as e (e.id)}
					<tr>
						<td class="lang-cell entry-cell" style="border-left-color: {hashColor(e.language?.color)}">
							<div class="entry-inner">
								<span class="entry-word-line">
									<a href="{base}/entries/{e.id}">{@html safe(e.word)}</a>
									<span class="id-tag">[{e.id}]</span>
											</span>
								{#if e.variant_forms}{#each variantList(e.variant_forms) as vf (vf)}<span class="var-line"><span class="var-arrow">→</span>&nbsp;<span class="var-form">{@html safe(vf)}</span></span>{/each}{/if}
						<CladeBars clades={e.clades} />
							</div>
						</td>
						<td class="lang-plain">
							{e.language?.language}{#if e.language?.dialect}: <span class="font-thin"
									>{e.language.dialect}</span
								>{/if}
						</td>
						<td class="muted gloss-cell">{@html safe(e.gloss) || '—'}</td>
						<td class="muted etym-cell">{@html safe(e.etymology) || '—'}</td>
						<td class="num">{e.lang_count?.toLocaleString() ?? ''}</td>
						<td class="num">{e.reflex_count?.toLocaleString() ?? ''}</td>
						<td class="num">{e.derived_count?.toLocaleString() ?? ''}</td>
						<td><RefList references={e.references} /></td>
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
	.loader-slot {
		height: 3px;
		margin-bottom: 0.4rem;
	}
	/* the headword leads the row, with its reflex-clade spread stacked beneath it */
	.entry-inner {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.entry-cell {
		min-width: 9rem;
	}
	.entry-word-line a {
		font-family: var(--font-serif);
		font-size: 1.18rem;
		font-weight: 600;
	}
	/* language is now secondary to the headword */
	.lang-plain {
		font-size: 0.92rem;
		color: var(--muted);
		white-space: nowrap;
	}
	.gloss-cell {
		font-family: var(--font-serif);
		min-width: 7rem;
	}
	.var-line {
		display: block;
		font-family: var(--font-serif);
		font-size: 0.85rem;
		color: var(--muted);
	}
	.var-arrow {
		font-size: 0.72rem;
		color: var(--faint);
	}
	.var-form {
		white-space: nowrap;
	}
	.etym-cell {
		font-size: 0.88rem;
		line-height: 1.45;
		font-family: var(--font-serif);
	}
	.num {
		text-align: right;
		white-space: nowrap;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
	}
</style>
