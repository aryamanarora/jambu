<script lang="ts">
	import { base } from '$app/paths';
	import { createListState } from '$lib/listState.svelte';
	import { getFilterDialects, getFilterLanguages } from '$lib/query';
	import { PAGE_SIZE } from '$lib/types';
	import { safe, md } from '$lib/render';
	import { hashColor, cladeColor } from '$lib/clades';
	import FilterCell from './FilterCell.svelte';
	import TagFilter from './TagFilter.svelte';
	import Tags from './Tags.svelte';
	import type { SelectOption } from './SelectFilter.svelte';
	import CladeBars from './CladeBars.svelte';
	import RefList from './RefList.svelte';
	import Pager from './Pager.svelte';
	import { getConceptReflexes } from '$lib/query';
	import type { Lemma } from '$lib/types';
	import FormWord from './FormWord.svelte';

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
	const from = $derived(list.result ? (list.result.page - 1) * PAGE_SIZE + 1 : 0);
	const to = $derived(list.result ? from + list.result.rows.length - 1 : 0);
	// variant word forms arrive \x1f-separated from group_concat (see query.ts)
	const variantList = (s?: string | null): string[] => (s ? [...new Set(s.split(''))] : []);
	const ocrVariants = (s?: string | null): Set<string> => new Set(variantList(s));

	let langOptions = $state<SelectOption[]>([]);
	$effect(() => {
		Promise.all([getFilterLanguages('entries'), getFilterDialects('entries')]).then(([ls, ds]) => {
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
</script>

<div class="showing-line">
	<div class="loader-slot">{#if list.loading}<div class="loader-line"></div>{/if}</div>
	<div class="showing-row">
		{#if list.result}
			<p class="muted">
				Showing {from.toLocaleString()}–{to.toLocaleString()} of
				{list.result.count.toLocaleString()} entries.
			</p>
		{/if}
		<div class="toggle-group">
			<button
				class="roots-toggle"
				class:on={list.params.rootsOnly}
				aria-pressed={list.params.rootsOnly}
				title="Show only root nodes — entries not derived from any other etymon"
				onclick={() => list.setFilter('roots', list.params.rootsOnly ? '' : '1')}
			>
				Roots only
			</button>
			<button
				class="roots-toggle"
				class:on={list.params.sectionsOnly}
				aria-pressed={list.params.sectionsOnly}
				title="Show only CDIAL section-forms — numbered derived forms promoted from an entry's header"
				onclick={() => list.setFilter('sections', list.params.sectionsOnly ? '' : '1')}
			>
				Section-forms
			</button>
			<button
				class="roots-toggle"
				class:on={list.params.loanSourcesOnly}
				aria-pressed={list.params.loanSourcesOnly}
				title="Show only loan sources — reflexes that words in other languages were borrowed from"
				onclick={() => list.setFilter('loans', list.params.loanSourcesOnly ? '' : '1')}
			>
				Loan sources
			</button>
		</div>
	</div>
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
				{#if !expandable}
					<FilterCell
						label="Etymology"
						filterKey="etymology"
						palette
						value={list.params.etymology ?? ''}
						activeSort={list.params.sort ?? ''}
						onFilter={list.setFilter}
						onSort={list.setSort}
					/>
					<TagFilter value={list.params.tags ?? ''} onFilter={list.setFilter} />
				{/if}
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
				{#if !expandable}
					<FilterCell
						label="Derived"
						sortKey="nderived"
						numeric
						activeSort={list.params.sort ?? ''}
						onFilter={list.setFilter}
						onSort={list.setSort}
					/>
				{/if}
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
					<tr class:expandable-row={expandable} onclick={expandable ? () => toggleRow(e.id) : undefined}>
						<td class="lang-cell entry-cell" style="border-left-color: {hashColor(e.language?.color)}">
							<div class="entry-inner">
								<span class="entry-word-line">
									{#if expandable}<span class="row-caret">{expanded.has(e.id) ? '▾' : '▸'}</span>{/if}
									{#if e.word?.trim()}
										<a href="{base}/entries/{e.id}"><FormWord word={e.word} references={e.references} /></a>
										<span class="id-tag">[{e.id}]</span>
									{:else}
										<a href="{base}/entries/{e.id}" class="id-link">[{e.id}]</a>
									{/if}
											</span>
								{#if e.variant_forms}{#each variantList(e.variant_forms) as vf (vf)}<span class="var-line"><span class="var-arrow">→</span>&nbsp;<span class="var-form"><FormWord word={vf} ocr={ocrVariants(e.ocr_variant_forms).has(vf)} /></span></span>{/each}{/if}
						<CladeBars clades={e.clades} />
							</div>
						</td>
						<td class="lang-plain">
							{e.language?.language}{#if e.language?.dialect}: <span class="font-thin"
									>{e.language.dialect}</span
								>{/if}
						</td>
						<td class="muted gloss-cell">{@html safe(e.gloss) || '—'}</td>
						{#if !expandable}
							<td class="muted etym-cell">{@html safe(e.etymology) || '—'}</td>
							<td><Tags tags={e.tags} /></td>
						{/if}
						<td class="num">{e.lang_count?.toLocaleString() ?? ''}</td>
						<td class="num">{(expandable ? e.concept_match : e.reflex_count)?.toLocaleString() ?? ''}</td>
						{#if !expandable}
							<td class="num">{e.derived_count?.toLocaleString() ?? ''}</td>
						{/if}
						<td><RefList references={e.references} /></td>
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

{#if list.result}
	<Pager count={list.result.count} page={list.result.page} onpage={list.setPage} />
{/if}

<style>
	.showing-line {
		margin-top: 0.5rem;
	}
	.showing-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}
	.toggle-group {
		display: flex;
		gap: 0.4rem;
	}
	.roots-toggle {
		font-family: var(--font-sans);
		font-size: 0.82rem;
		font-weight: 500;
		padding: 3px 14px;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		background: var(--surface);
		color: var(--muted);
		cursor: pointer;
		white-space: nowrap;
		transition:
			background 0.12s,
			color 0.12s,
			border-color 0.12s;
	}
	.roots-toggle:hover {
		color: var(--ink);
	}
	.roots-toggle.on {
		background: var(--plum);
		border-color: var(--plum);
		color: #fbeefb;
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
	.num {
		text-align: right;
		white-space: nowrap;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
	}
	.expandable-row {
		cursor: pointer;
	}
	.expandable-row:hover {
		background: var(--hover, rgba(0, 0, 0, 0.03));
	}
	.row-caret {
		display: inline-block;
		width: 1em;
		color: var(--muted);
		font-size: 0.8em;
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
