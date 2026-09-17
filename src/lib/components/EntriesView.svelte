<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { getFilterDialects, getFilterLanguages } from '$lib/query';
	import { highlightHtml, highlightText, md, referenceLabel, safe } from '$lib/render';
	import { tagLabel } from '$lib/tags';
	import { hashColor, cladeColor } from '$lib/clades';
	import { languageOptions } from '$lib/languageOptions';
	import FilterCell from './FilterCell.svelte';
	import Tags from './Tags.svelte';
	import type { SelectOption } from '$lib/languageOptions';
	import LemmaFilters from './LemmaFilters.svelte';
	import LemmaList from './LemmaList.svelte';
	import CladeBars from './CladeBars.svelte';
	import RefList from './RefList.svelte';
	import { getConceptReflexes } from '$lib/query';
	import type { Lemma, Reference } from '$lib/types';
	import FormWord from './FormWord.svelte';
	import Ancestry from './Ancestry.svelte';

	// `concept` restricts the list to entries expressing that Concepticon concept; `expandable`
	// lets each entry row expand to an inline reflex view (used on the concepts page).
	let { concept, expandable = false }: { concept?: string; expandable?: boolean } = $props();

	const list = createListState('entries', { conceptId: concept });

	let expanded = $state<Set<string>>(new Set());
	let reflexCache = $state<Record<string, Lemma[]>>({});
	function toggleRow(id: string) {
		const next = new Set(expanded);
		if (next.has(id)) next.delete(id);
		else {
			next.add(id);
			if (!reflexCache[id] && concept)
				getConceptReflexes(id, concept).then((r) => (reflexCache = { ...reflexCache, [id]: r }));
		}
		expanded = next;
	}
	// variant word forms arrive \x1f-separated from group_concat (see query.ts)
	const variantList = (s?: string | null): string[] => (s ? [...new Set(s.split(''))] : []);
	const ocrVariants = (s?: string | null): Set<string> => new Set(variantList(s));
	let langOptions = $state<SelectOption[]>([]);
	const optionHighlight = (options: SelectOption[], value?: string) => {
		const label = options.find((option) => option.value === value)?.label ?? '';
		return label.split(': ').filter(Boolean);
	};
	const tagHighlights = $derived(
		(list.params.tags ?? '').split(/\s+/).filter(Boolean).map(tagLabel)
	);
	const languageHighlights = $derived(optionHighlight(langOptions, list.params.origin_lang));
	const sourceHighlights = (references: Reference[] = []) => {
		const selected = references.find(
			(reference) => reference.id === list.params.source || reference.short === list.params.source
		);
		return [list.params.word, selected ? referenceLabel(selected) : ''];
	};

	$effect(() => {
		Promise.all([getFilterLanguages('entries'), getFilterDialects('entries')]).then(([ls, ds]) => {
			langOptions = languageOptions(ls, ds);
		});
	});
</script>

{#snippet filters()}
	<LemmaFilters params={list.params} mode="entries" languages={langOptions} onFilter={list.setFilter} />
{/snippet}

<LemmaList {list} mode="entries" {filters}>
<div class="table-wrap">
	<table class="data mobile-cards">
		<thead>
			<tr>
				<FilterCell
					label="Entry"
					sortKey="word"
					accent
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Language"
					sortKey="lang"
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
				{#if !expandable}
					<FilterCell
						label="Etymology"
						activeSort={list.params.sort ?? ''}
						onFilter={list.setFilter}
						onSort={list.setSort}
					/>
					<FilterCell label="Tags" activeSort={list.params.sort ?? ''} onFilter={list.setFilter} onSort={list.setSort} />
				{/if}
				<FilterCell
					label="Lang."
					sortKey="nlang"
					numeric
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				<FilterCell
					label="Refl."
					sortKey="nreflex"
					numeric
					activeSort={list.params.sort ?? ''}
					onFilter={list.setFilter}
					onSort={list.setSort}
				/>
				{#if !expandable}
					<FilterCell
						label="Der."
						sortKey="nderived"
						numeric
						activeSort={list.params.sort ?? ''}
						onFilter={list.setFilter}
						onSort={list.setSort}
					/>
				{/if}
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
				{#each list.result.rows as e (e.id)}
					<tr class:expandable-row={expandable} onclick={expandable ? () => toggleRow(e.id) : undefined}>
						<td class="lang-cell entry-cell" style="border-left-color: {hashColor(e.language?.color)}">
							<div class="entry-inner">
								<span class="entry-word-line">
									{#if expandable}<span class="chev row-caret" class:right={!expanded.has(e.id)} aria-hidden="true"></span>{/if}
									{#if e.word?.trim()}
										<a href="{base}/entries/{e.id}"><FormWord word={e.word} references={e.references} highlight={[list.params.word, list.params.form]} relaxed={list.params.relaxed} /></a>
										<span class="id-tag">[{@html highlightText(e.id, list.params.word, list.params.relaxed)}]</span>
									{:else}
										<a href="{base}/entries/{e.id}" class="id-link">[{@html highlightText(e.id, list.params.word, list.params.relaxed)}]</a>
									{/if}
											</span>
								{#if e.variant_forms}{#each variantList(e.variant_forms) as vf (vf)}<span class="var-line"><span class="var-arrow">→</span>&nbsp;<span class="var-form"><FormWord word={vf} ocr={ocrVariants(e.ocr_variant_forms).has(vf)} highlight={[list.params.word, list.params.form]} relaxed={list.params.relaxed} /></span></span>{/each}{/if}
						<CladeBars clades={e.clades} />
							</div>
						</td>
						<td class="lang-plain" data-label="Language">
							{@html highlightText(e.language?.language, [list.params.word, ...languageHighlights], list.params.relaxed)}{#if e.language?.dialect}: <span class="font-thin"
									>{@html highlightText(e.language.dialect, [list.params.word, ...languageHighlights], list.params.relaxed)}</span
								>{/if}
						</td>
						<td class="muted gloss-cell" data-label="Meaning">{@html highlightHtml(safe(e.gloss), [list.params.word, list.params.gloss], list.params.relaxed) || '—'}</td>
						{#if !expandable}
							<td class="muted etym-cell" data-label="Etymology">
								<div class="etym-stack">
									{#if e.ancestry?.length}
										<Ancestry
											label="<"
											chain={e.ancestry}
											startLang={e.language?.name}
											compact
											highlight={[list.params.word, list.params.etymology]}
											relaxed={list.params.relaxed}
										/>
									{/if}
									{#if e.comparisons?.length}
										<div class="cross-lines">
											{#each e.comparisons as comparison (comparison.id)}
												<div class="cross-line" title={comparison.evidence}>
													<span class="cross-relation">cf.</span>
													<a class="cross-word" href="{base}/entries/{comparison.other_id}"
												><FormWord word={comparison.other_word || comparison.other_id} highlight={[list.params.word, list.params.etymology]} relaxed={list.params.relaxed} /></a
											>
											<span class="id-tag">[{@html highlightText(comparison.other_id, [list.params.word, list.params.etymology], list.params.relaxed)}]</span>
												</div>
											{/each}
										</div>
									{/if}
									{#if !e.ancestry?.length && !e.comparisons?.length}—{/if}
								</div>
							</td>
							<td class="tag-cell" data-label="Tags"><Tags tags={e.tags} highlight={[list.params.word, ...tagHighlights]} relaxed={list.params.relaxed} /></td>
						{/if}
						<td class="num" data-label="Languages">{@html highlightText(e.lang_count?.toLocaleString() ?? '', list.params.word, list.params.relaxed)}</td>
						<td class="num" data-label="Forms">{@html highlightText((expandable ? e.concept_match : e.reflex_count)?.toLocaleString() ?? '', list.params.word, list.params.relaxed)}</td>
						{#if !expandable}
							<td class="num" data-label="Derived">{@html highlightText(e.derived_count?.toLocaleString() ?? '', list.params.word, list.params.relaxed)}</td>
						{/if}
						<td data-label="Source"><RefList references={e.references} highlight={sourceHighlights(e.references)} relaxed={list.params.relaxed} /></td>
					</tr>
					{#if expandable && expanded.has(e.id)}
						<tr class="reflex-detail">
							<td colspan="6">
								{#if reflexCache[e.id]}
									<table class="reflex-sub">
										<tbody>
											{#each reflexCache[e.id] as r (r.id)}
												<tr>
													<td class="rlang" style="border-left-color: {hashColor(r.language?.color)}">
														<a href="{base}/languages/{r.language_id}"
															>{r.language?.language}{#if r.language?.dialect}: <span class="font-thin"
																	>{r.language.dialect}</span
																>{/if}</a
														>
													</td>
													<td class="rword"
														><a href="{base}/reflexes/{r.id}"><FormWord word={r.word} references={r.references} /></a>{#if r.phonemic}
															<span class="phonemic">/&#8288;{r.phonemic}&#8288;/</span>{/if}</td
													>
													<td class="muted">{@html safe(r.gloss) || '—'}</td>
													<td class="muted markdown">{@html md(r.notes)}</td>
													<td><RefList references={r.references} /></td>
												</tr>
											{/each}
											{#if !reflexCache[e.id].length}
												<tr><td class="muted">no matching reflexes</td></tr>
											{/if}
										</tbody>
									</table>
								{:else}
									<span class="muted">loading reflexes…</span>
								{/if}
							</td>
						</tr>
					{/if}
				{/each}
			{/if}
		</tbody>
	</table>
</div>

</LemmaList>

<style>
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
	/* word-less entries (e.g. PDr reconstructions): the id is the clickable label */
	.entry-word-line a.id-link {
		font-family: inherit;
		font-size: 0.9rem;
		font-weight: 500;
	}
	/* language is secondary to the headword */
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
	.etym-stack {
		display: grid;
		gap: 0.35rem;
	}
	.cross-lines {
		display: grid;
		gap: 0.12rem;
	}
	.cross-line {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.25rem;
		font-family: var(--font-sans);
		font-size: 0.7rem;
		line-height: 1.35;
	}
	.cross-relation { color: var(--muted); }
	.cross-word {
		font-family: var(--font-serif);
		font-size: 0.82rem;
		font-weight: 600;
	}
	.num {
		width: 1%;
		padding-inline: 0.35rem;
		text-align: right;
		white-space: nowrap;
		font-variant-numeric: tabular-nums;
		font-size: 0.84rem;
		color: var(--muted);
	}
	/* Keep the three count columns content-sized instead of letting the table
	   distribute spare width to them. FilterCell owns the header markup, so
	   these header selectors need to cross the component boundary. */
	:global(table.data th.numeric) {
		width: 1%;
		padding-inline: 0.35rem;
		white-space: nowrap;
		font-size: 0.82rem;
	}
	.expandable-row {
		cursor: pointer;
	}
	.expandable-row:hover {
		background: var(--hover, rgba(0, 0, 0, 0.03));
	}
	.row-caret {
		margin-right: 0.3em;
		color: var(--muted);
	}
	.reflex-detail > td {
		padding: 0.2rem 0.6rem 0.6rem 2rem;
		background: var(--panel, rgba(0, 0, 0, 0.02));
	}
	table.reflex-sub {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.9rem;
	}
	table.reflex-sub td {
		padding: 0.2rem 0.6rem;
		border-top: 1px solid var(--border);
	}
	.reflex-sub .rlang {
		border-left: 3px solid #ccc;
		white-space: nowrap;
		font-weight: 500;
	}
	.reflex-sub .rword {
		font-family: var(--font-phon);
	}
</style>
