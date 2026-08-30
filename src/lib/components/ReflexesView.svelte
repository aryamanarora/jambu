<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { getFilterDialects, getFilterLanguages } from '$lib/query';
	import { PAGE_SIZE } from '$lib/types';
	import { safe, md } from '$lib/render';
	import { hashColor, cladeColor } from '$lib/clades';
	import FilterCell from './FilterCell.svelte';
	import FilterField from './FilterField.svelte';
	import ListToolbar from './ListToolbar.svelte';
	import QueryError from './QueryError.svelte';
	import SelectFilter, { type SelectOption } from './SelectFilter.svelte';
	import RefList from './RefList.svelte';
	import Pager from './Pager.svelte';
	import Tags from './Tags.svelte';
	import FormWord from './FormWord.svelte';
	import TagFilter from './TagFilter.svelte';
	import SourceFilter from './SourceFilter.svelte';

	let {
		mode = 'reflexes',
		languageId,
		referenceId
	}: { mode?: 'reflexes' | 'lexicon'; languageId?: string; referenceId?: string } = $props();

	const showLangCol = $derived(mode === 'reflexes');
	const list = createListState(mode, { languageId, referenceId, withOrigin: true });
	const from = $derived(list.result ? (list.result.page - 1) * PAGE_SIZE + 1 : 0);
	const to = $derived(list.result ? from + list.result.rows.length - 1 : 0);
	const resultLabel = $derived(
		list.result
			? `${from.toLocaleString()}–${to.toLocaleString()} of ${list.result.count.toLocaleString()} forms`
			: ''
	);
	const activeFilterCount = $derived(
		[
			showLangCol ? list.params.origin_lang : '',
			list.params.dialect,
			list.params.origin,
			list.params.etymon_lang,
			list.params.gloss,
			list.params.tags,
			list.params.notes,
			list.params.source
		].filter(Boolean).length
	);

	let langOptions = $state<SelectOption[]>([]);
	$effect(() => {
		if (!showLangCol) return;
		Promise.all([getFilterLanguages('reflexes'), getFilterDialects('reflexes')]).then(([ls, ds]) => {
			const byId = new Map(ls.map((l) => [l.id, l]));
			langOptions = [...ls.map((l) => ({
				value: l.id,
				label: l.name,
				sub: l.clade ?? '',
				swatch: cladeColor(l.clade)
			})), ...ds.map((d) => {
				const parent = byId.get(d.language_id);
				return {
					value: d.token,
					label: `${parent?.name ?? d.language_id}: ${d.name}`,
					sub: `dialect · ${parent?.clade ?? ''}`,
					swatch: cladeColor(parent?.clade ?? '')
				};
			})];
		});
	});

	// origin-language picker options (etymon / borrowing-source languages) for the Origin column
	let originLangOptions = $state<SelectOption[]>([]);
	$effect(() => {
		Promise.all([getFilterLanguages('entries'), getFilterDialects('entries')]).then(([ls, ds]) => {
			const byId = new Map(ls.map((l) => [l.id, l]));
			originLangOptions = [...ls.map((l) => ({
				value: l.id,
				label: l.name,
				sub: l.clade ?? '',
				swatch: cladeColor(l.clade)
			})), ...ds.map((d) => {
				const parent = byId.get(d.language_id);
				return {
					value: d.token,
					label: `${parent?.name ?? d.language_id}: ${d.name}`,
					sub: `dialect · ${parent?.clade ?? ''}`,
					swatch: cladeColor(parent?.clade ?? '')
				};
			})];
		});
	});

</script>

{#snippet filters()}
	{#if showLangCol}
		<label class="filter-control">
			<span>Language</span>
			<SelectFilter
				placeholder="Any language"
				options={langOptions}
				value={list.params.origin_lang ?? ''}
				onSelect={(value) => list.setFilter('origin_lang', value)}
			/>
		</label>
	{/if}
	<label class="filter-control">
		<span>Origin language</span>
		<SelectFilter
			placeholder="Any origin language"
			options={originLangOptions}
			value={list.params.etymon_lang ?? ''}
			onSelect={(value) => list.setFilter('etymon_lang', value)}
		/>
	</label>
	<FilterField
		label="Origin form"
		palette
		value={list.params.origin ?? ''}
		onValue={(value) => list.setFilter('origin', value)}
	/>
	<FilterField
		label="Meaning"
		palette
		value={list.params.gloss ?? ''}
		onValue={(value) => list.setFilter('gloss', value)}
	/>
	<FilterField
		label="Notes"
		palette
		value={list.params.notes ?? ''}
		onValue={(value) => list.setFilter('notes', value)}
	/>
	<TagFilter standalone value={list.params.tags ?? ''} onFilter={list.setFilter} />
	<SourceFilter
		standalone
		value={list.params.source ?? ''}
		activeSort={list.params.sort ?? ''}
		onFilter={list.setFilter}
		onSort={list.setSort}
	/>
{/snippet}

<div class="loader-slot">{#if list.loading}<div class="loader-line"></div>{/if}</div>
<ListToolbar
	value={list.params.word ?? ''}
	placeholder={mode === 'lexicon' ? 'Search this lexicon…' : 'Search all forms…'}
	searchLabel={mode === 'lexicon' ? 'Search this lexicon' : 'Search all forms'}
	{resultLabel}
	filterCount={activeFilterCount}
	onSearch={(value) => list.setFilter('word', value)}
	{filters}
/>

{#if list.error}<QueryError error={list.error} />{/if}

<div class="table-wrap">
	<table class="data mobile-cards">
		<thead>
			<tr>
				{#if showLangCol}
					<FilterCell
						label="Language"
						sortKey="lang"
						accent
						activeSort={list.params.sort ?? ''}
						onFilter={list.setFilter}
						onSort={list.setSort}
					/>
				{/if}
				<FilterCell
					label="Word"
					sortKey="word"
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Origin"
					sortKey="origin"
					accent={!showLangCol}
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Gloss"
					sortKey="gloss"
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell label="Tags" activeSort={list.params.sort ?? ''} onFilter={list.setFilter} onSort={list.setSort} />
				<FilterCell
					label="Notes"
					sortKey="notes"
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Source"
					sortKey="source"
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
						<td class="lemma-word" data-label="Form">
							<a href="{base}/entries/{r.id}"><FormWord word={r.word} references={r.references} /></a>{#if r.phonemic}
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
							data-label="Origin"
							style={!showLangCol
								? `border-left-color: ${hashColor(r.origin_lemma?.language?.color)}`
								: ''}
						>
							{#if r.origin_lemma}
								{#if r.origin_lemma.language}<span class="olang"
										>{r.origin_lemma.language.name}</span
									> {/if}<a class="origin" href="{base}/entries/{r.origin_lemma.id}"
									><FormWord word={r.origin_lemma.word} ocr={r.origin_lemma.ocr} /> <span class="id-tag">[{r.origin_lemma.id}]</span
									></a
								>
							{:else}<span class="faint">—</span>{/if}
						</td>
						<td class="muted" data-label="Meaning">{@html safe(r.gloss) || '—'}</td>
						<td class="tag-cell" data-label="Tags"><Tags tags={r.tags} /></td>
						<td class="muted markdown" data-label="Notes">{@html md(r.notes)}</td>
						<td data-label="Source"><RefList references={r.references} /></td>
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
	.filter-control {
		display: grid;
		gap: 0.3rem;
		min-width: 0;
		color: var(--muted);
		font-size: 0.76rem;
		font-weight: 600;
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
