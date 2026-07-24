<script lang="ts">
	import { base } from '$app/paths';
	import { md } from '$lib/render';
	import FilterCell from '$lib/components/FilterCell.svelte';
	import type { Reference } from '$lib/types';

	let { data } = $props();
	let activeSort = $state('desc-forms');
	const sortedReferences = $derived.by(() => {
		const rows = [...data.references] as Reference[];
		if (!activeSort) return rows;
		const [direction, key] = activeSort.split('-');
		const sign = direction === 'desc' ? -1 : 1;
		const text = (r: Reference, field: keyof Reference) => String(r[field] ?? '').toLocaleLowerCase();
		return rows.sort((a, b) => {
			let comparison = 0;
			if (key === 'forms') comparison = (a.lemma_count ?? 0) - (b.lemma_count ?? 0);
			else if (key === 'unetym') {
				const ap = a.lemma_count ? a.unetymologised_count / a.lemma_count : -1;
				const bp = b.lemma_count ? b.unetymologised_count / b.lemma_count : -1;
				comparison = ap - bp;
			} else {
				const field = ({ reference: 'short', citation: 'source' }[key] ?? key) as keyof Reference;
				comparison = text(a, field).localeCompare(text(b, field));
			}
			return sign * comparison || a.short.localeCompare(b.short);
		});
	});
	function setSort(value: string) {
		activeSort = value;
	}

	// progress → badge class + border colour (mirrors the old references.html)
	function badge(progress: string): 'ok' | 'warn' | 'bad' {
		if (progress === 'Yes') return 'ok';
		if (progress === 'Partial') return 'warn';
		return 'bad';
	}
	function unetymologisedPct(total: number, unetymologised: number): string {
		return total ? `${((unetymologised / total) * 100).toFixed(1)}%` : '—';
	}
	const borderColor = { ok: 'var(--ok)', warn: 'var(--warn)', bad: 'var(--bad)' };
</script>

<svelte:head>
	<title>References — Jambu</title>
	<meta name="description" content="The bibliography of sources digitised in the Jambu etymological dictionary of South Asian languages." />
</svelte:head>

<h1>References</h1>
<p class="muted">Sources digitised for Jambu. The coloured bar shows digitisation progress.</p>

<div class="table-wrap">
	<table class="data accent-col">
		<colgroup>
			<col class="ref-col" />
			<col class="citation-col" />
			<col class="editor-col" />
			<col class="forms-col" />
			<col class="unetym-col" />
		</colgroup>
		<thead>
			<tr>
				<FilterCell label="Reference" sortKey="reference" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Citation" sortKey="citation" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Editor" sortKey="editor" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Forms" sortKey="forms" {activeSort} numeric onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Unetymologised" sortKey="unetym" {activeSort} numeric onFilter={() => {}} onSort={setSort} />
			</tr>
		</thead>
		<tbody>
			{#each sortedReferences as r (r.id)}
				{@const b = badge(r.progress)}
				<tr>
					<td class="lang-cell ref-cell" style="border-left-color: {borderColor[b]}">
						<a href="{base}/references/{r.id}">{r.short}</a>
						<span class="id-tag">[{r.id}]</span>
					</td>
					<td class="markdown">{@html md(r.source)}</td>
					<td>{r.editor || '—'}</td>
					<td class="pct">{(r.lemma_count ?? 0).toLocaleString()}</td>
					<td class="pct" title="{(r.unetymologised_count ?? 0).toLocaleString()} of {(r.lemma_count ?? 0).toLocaleString()} forms">
						{unetymologisedPct(r.lemma_count ?? 0, r.unetymologised_count ?? 0)}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.ref-cell {
		white-space: normal;
		overflow-wrap: anywhere;
	}
	table {
		width: 100%;
		min-width: 820px;
		table-layout: fixed;
	}
	.ref-col {
		width: 11rem;
	}
	.citation-col {
		width: auto;
	}
	.editor-col {
		width: 13rem;
	}
	.forms-col {
		width: 6.5rem;
	}
	.unetym-col {
		width: 8.5rem;
	}
	td.markdown {
		overflow-wrap: anywhere;
	}
	.pct {
		text-align: right;
		font-variant-numeric: tabular-nums;
		font-weight: 600;
	}
</style>
