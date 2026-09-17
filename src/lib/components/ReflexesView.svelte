<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { getFilterDialects, getFilterLanguages } from '$lib/query';
	import { highlightHtml, highlightText, md, referenceLabel, safe } from '$lib/render';
	import { tagLabel } from '$lib/tags';
	import { hashColor, cladeColor } from '$lib/clades';
	import { languageOptions } from '$lib/languageOptions';
	import FilterCell from './FilterCell.svelte';
	import type { SelectOption } from '$lib/languageOptions';
	import LemmaFilters from './LemmaFilters.svelte';
	import LemmaList from './LemmaList.svelte';
	import RefList from './RefList.svelte';
	import Tags from './Tags.svelte';
	import FormWord from './FormWord.svelte';
	import type { Reference } from '$lib/types';

	let {
		mode = 'reflexes',
		languageId,
		referenceId
	}: { mode?: 'reflexes' | 'lexicon'; languageId?: string; referenceId?: string } = $props();

	const showLangCol = $derived(mode === 'reflexes');
	const list = createListState(mode, { languageId, referenceId, withOrigin: true });
	let langOptions = $state<SelectOption[]>([]);
	$effect(() => {
		if (!showLangCol) return;
		Promise.all([getFilterLanguages('reflexes'), getFilterDialects('reflexes')]).then(([ls, ds]) => {
			langOptions = languageOptions(ls, ds);
		});
	});

	// origin-language picker options (etymon / borrowing-source languages) for the Origin column
	let originLangOptions = $state<SelectOption[]>([]);
	$effect(() => {
		Promise.all([getFilterLanguages('entries'), getFilterDialects('entries')]).then(([ls, ds]) => {
			originLangOptions = languageOptions(ls, ds);
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
	<LemmaFilters params={list.params} mode="forms" showLanguage={showLangCol} languages={langOptions} originLanguages={originLangOptions} onFilter={list.setFilter} />
{/snippet}

<LemmaList {list} mode="forms" showLanguage={showLangCol} placeholder={mode === 'lexicon' ? 'Search all columns in this lexicon…' : 'Search all columns…'} {filters}>
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

</LemmaList>

<style>
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
</style>
