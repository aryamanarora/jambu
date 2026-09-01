<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { getFilterDialects, getFilterLanguages } from '$lib/query';
	import { PAGE_SIZE } from '$lib/types';
	import { highlightHtml, highlightText, md, referenceLabel, safe } from '$lib/render';
	import { tagLabel } from '$lib/tags';
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
	import SearchMatchToggle from './SearchMatchToggle.svelte';
	import type { Reference } from '$lib/types';

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
			list.params.relaxed,
			list.params.form,
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
	const optionHighlight = (options: SelectOption[], value?: string) => {
		const label = options.find((option) => option.value === value)?.label ?? '';
		return label.split(': ').filter(Boolean);
	};
	const languageHighlights = $derived(optionHighlight(langOptions, list.params.origin_lang));
	const originLanguageHighlights = $derived(optionHighlight(originLangOptions, list.params.etymon_lang));
	const tagHighlights = $derived([
		...(list.params.tags ?? '').split(/\s+/).filter(Boolean).map(tagLabel),
		...(list.params.dialect ? [tagLabel(list.params.dialect)] : [])
	]);
	const sourceHighlights = (references: Reference[] = []) => {
		const selected = references.find(
			(reference) => reference.id === list.params.source || reference.short === list.params.source
		);
		return [list.params.word, selected ? referenceLabel(selected) : ''];
	};

</script>

{#snippet filters()}
	<SearchMatchToggle
		relaxed={list.params.relaxed}
		onToggle={(relaxed) => list.setFilter('relaxed', relaxed ? '1' : '')}
	/>
	<FilterField
		label="Form"
		placeholder="Filter forms…"
		palette
		value={list.params.form ?? ''}
		onValue={(value) => list.setFilter('form', value)}
	/>
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
	placeholder={mode === 'lexicon' ? 'Search all columns in this lexicon…' : 'Search all columns…'}
	searchLabel="Search all shown columns"
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
									>{@html highlightText(r.language?.language, [list.params.word, ...languageHighlights], list.params.relaxed)}{#if r.language?.dialect}: <span class="font-thin"
											>{@html highlightText(r.language.dialect, [list.params.word, ...languageHighlights], list.params.relaxed)}</span
										>{/if}</a
								>
							</td>
						{/if}
						<td class="lemma-word" data-label="Form">
							<a href="{base}/entries/{r.id}"><FormWord word={r.word} references={r.references} highlight={[list.params.word, list.params.form]} relaxed={list.params.relaxed} /></a>{#if r.phonemic}
								<span class="phonemic">/&#8288;{@html highlightText(r.phonemic, list.params.word, list.params.relaxed)}&#8288;/</span>{/if}{#if r.sub_count}
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
										>{@html highlightText(r.origin_lemma.language.name, [list.params.word, ...originLanguageHighlights], list.params.relaxed)}</span
									> {/if}<a class="origin" href="{base}/entries/{r.origin_lemma.id}"
									><FormWord word={r.origin_lemma.word} ocr={r.origin_lemma.ocr} highlight={[list.params.word, list.params.origin]} relaxed={list.params.relaxed} /> <span class="id-tag">[{@html highlightText(r.origin_lemma.id, list.params.word, list.params.relaxed)}]</span
									></a
								>
							{:else}<span class="faint">—</span>{/if}
						</td>
						<td class="muted" data-label="Meaning">{@html highlightHtml(safe(r.gloss), [list.params.word, list.params.gloss], list.params.relaxed) || '—'}</td>
						<td class="tag-cell" data-label="Tags"><Tags tags={r.tags} highlight={[list.params.word, ...tagHighlights]} relaxed={list.params.relaxed} /></td>
						<td class="muted markdown" data-label="Notes">{@html highlightHtml(md(r.notes), [list.params.word, list.params.notes], list.params.relaxed)}</td>
						<td data-label="Source"><RefList references={r.references} highlight={sourceHighlights(r.references)} relaxed={list.params.relaxed} /></td>
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
