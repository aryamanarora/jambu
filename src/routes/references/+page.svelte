<script lang="ts">
	import { base } from '$app/paths';
	import { md } from '$lib/render';
	import FilterCell from '$lib/components/FilterCell.svelte';
	import ListToolbar from '$lib/components/ListToolbar.svelte';
	import type { Reference } from '$lib/types';

	let { data } = $props();
	let search = $state('');
	let activeSort = $state('desc-forms');
	const sortedReferences = $derived.by(() => {
		const needle = search.trim().toLocaleLowerCase();
		const rows = ([...data.references] as Reference[]).filter((reference) =>
			!needle || [reference.id, reference.short, reference.source, reference.editor].some((field) =>
				(field ?? '').toLocaleLowerCase().includes(needle)
			)
		);
		if (!activeSort) return rows;
		const [direction, key] = activeSort.split('-');
		const sign = direction === 'desc' ? -1 : 1;
		const text = (r: Reference, field: keyof Reference) => String(r[field] ?? '').toLocaleLowerCase();
		return rows.sort((a, b) => {
			let comparison = 0;
			if (key === 'forms') comparison = (a.lemma_count ?? 0) - (b.lemma_count ?? 0);
			else if (key === 'extraction') comparison = Number(a.ocr) - Number(b.ocr);
			else if (key === 'etymology') comparison = text(a, 'etymology_provenance').localeCompare(text(b, 'etymology_provenance'));
			else if (key === 'unetym') {
				const ap = a.lemma_count ? a.unetymologised_count / a.lemma_count : -1;
				const bp = b.lemma_count ? b.unetymologised_count / b.lemma_count : -1;
				comparison = ap - bp;
			} else {
				const field = ({ reference: 'short', citation: 'source' }[key] ?? key) as keyof Reference;
				comparison = text(a, field).localeCompare(text(b, field));
			}
			return sign * comparison || (a.short || a.id).localeCompare(b.short || b.id);
		});
	});
	function setSort(value: string) {
		activeSort = value;
	}

	// progress → badge class + border colour (mirrors the old references.html)
	function badge(progress: string | null): 'ok' | 'warn' | 'bad' {
		if (progress === 'Yes') return 'ok';
		if (progress === 'Partial') return 'warn';
		return 'bad';
	}
	function unetymologisedPct(total: number, unetymologised: number): string {
		return total ? `${((unetymologised / total) * 100).toFixed(1)}%` : '—';
	}
	function etymologyLabel(value: Reference['etymology_provenance']): string {
		return ({
			source: 'Source',
			'source-mapped': 'Source · mapped',
			jambu: 'Jambu',
			mixed: 'Source + Jambu',
			none: 'None'
		} as Record<string, string>)[value ?? ''] ?? 'Not recorded';
	}
	const borderColor = { ok: 'var(--ok)', warn: 'var(--warn)', bad: 'var(--bad)' };
</script>

<svelte:head>
	<title>Sources — Jambu</title>
	<meta name="description" content="The bibliography of sources digitised in the Jambu etymological dictionary of South Asian languages." />
</svelte:head>

<h1>Sources</h1>
<p class="muted">Sources digitised for Jambu. The coloured bar shows digitisation progress.</p>

<ListToolbar
	value={search}
	placeholder="Search sources, citations, or editors…"
	searchLabel="Search sources"
	resultLabel={`${sortedReferences.length.toLocaleString()} sources`}
	onSearch={(value) => (search = value)}
/>

<div class="table-wrap">
	<table class="data accent-col mobile-cards">
		<colgroup>
			<col class="ref-col" />
			<col class="citation-col" />
			<col class="editor-col" />
			<col class="extraction-col" />
			<col class="etymology-col" />
			<col class="forms-col" />
			<col class="unetym-col" />
		</colgroup>
		<thead>
			<tr>
				<FilterCell label="Reference" sortKey="reference" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Citation" sortKey="citation" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Editor" sortKey="editor" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Extraction" sortKey="extraction" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Etymologies" sortKey="etymology" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Forms" sortKey="forms" {activeSort} numeric onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Unetymologised" sortKey="unetym" {activeSort} numeric onFilter={() => {}} onSort={setSort} />
			</tr>
		</thead>
		<tbody>
			{#each sortedReferences as r (r.id)}
				{@const b = badge(r.progress)}
				<tr>
					<td class="lang-cell ref-cell" style="border-left-color: {borderColor[b]}">
						<a href="{base}/references/{r.id}">{r.short || r.id}</a>
						<span class="id-tag">[{r.id}]</span>
					</td>
					<td class="markdown" data-label="Citation">{@html md(r.source)}</td>
					<td data-label="Editor">{r.editor || '—'}</td>
					<td data-label="Extraction">{#if r.ocr}<span class="ocr-ref" title="Forms from this reference were parsed with optical character recognition">OCR</span>{:else}<span class="faint">—</span>{/if}</td>
					<td data-label="Etymology">{etymologyLabel(r.etymology_provenance)}</td>
					<td class="pct" data-label="Forms">{(r.lemma_count ?? 0).toLocaleString()}</td>
					<td class="pct" data-label="Unetymologised" title="{(r.unetymologised_count ?? 0).toLocaleString()} of {(r.lemma_count ?? 0).toLocaleString()} forms">
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
		min-width: 980px;
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
	.extraction-col {
		width: 6.5rem;
	}
	.etymology-col {
		width: 9.5rem;
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
	.ocr-ref {
		display: inline-block;
		padding: 0.08rem 0.42rem;
		border: 1px solid color-mix(in srgb, #b97812 55%, transparent);
		border-radius: 999px;
		background: color-mix(in srgb, #e8a62a 16%, var(--surface));
		color: color-mix(in srgb, #8b5708 88%, var(--ink));
		font-size: 0.68rem;
		font-weight: 700;
		letter-spacing: 0.05em;
	}
</style>
