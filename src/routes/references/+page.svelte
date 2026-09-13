<script lang="ts">
	import { highlightText, referenceLabel } from '$lib/render';
	import { unicodeSearchIncludes } from '$lib/unicodeSearch';
	import FilterCell from '$lib/components/FilterCell.svelte';
	import ListToolbar from '$lib/components/ListToolbar.svelte';
	import SearchMatchToggle from '$lib/components/SearchMatchToggle.svelte';
	import ReferenceLink from '$lib/components/ReferenceLink.svelte';
	import ReferenceFormsCount from '$lib/components/ReferenceFormsCount.svelte';
	import type { Reference } from '$lib/types';

	let { data } = $props();
	let search = $state('');
	let relaxed = $state(false);
	let activeSort = $state('desc-forms');
	const extractionLabel = (reference: Reference) => reference.ocr ? 'OCR' : '—';
	const numericHighlight = (value: string) => {
		const query = search.trim();
		return value.toLocaleLowerCase().includes(query.toLocaleLowerCase())
			? query
			: (query && value.replaceAll(',', '').includes(query.replaceAll(',', '')) ? value : '');
	};
	const sortedReferences = $derived.by(() => {
		const needle = search.trim();
		const rows = ([...data.references] as Reference[]).filter((reference) =>
			!needle || [
				reference.id,
				reference.short,
				reference.source,
				reference.editor,
				...(data.cladeDistributions[reference.id] ?? []).map((segment) => segment.clade),
				extractionLabel(reference),
				(reference.lemma_count ?? 0).toLocaleString(),
				(reference.lemma_count ?? 0).toString(),
				unetymologisedPct(reference.lemma_count ?? 0, reference.unetymologised_count ?? 0)
			].some((field) => unicodeSearchIncludes(field ?? '', needle, relaxed))
		);
		if (!activeSort) return rows;
		const [direction, key] = activeSort.split('-');
		const sign = direction === 'desc' ? -1 : 1;
		const text = (r: Reference, field: keyof Reference) => String(r[field] ?? '').toLocaleLowerCase();
		return rows.sort((a, b) => {
			let comparison = 0;
			if (key === 'forms') comparison = (a.lemma_count ?? 0) - (b.lemma_count ?? 0);
			else if (key === 'reference') comparison = referenceLabel(a).localeCompare(referenceLabel(b));
			else if (key === 'extraction') comparison = Number(a.ocr) - Number(b.ocr);
			else if (key === 'unetym') {
				const ap = a.lemma_count ? a.unetymologised_count / a.lemma_count : -1;
				const bp = b.lemma_count ? b.unetymologised_count / b.lemma_count : -1;
				comparison = ap - bp;
			} else {
				const field = key as keyof Reference;
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
	const borderColor = { ok: 'var(--ok)', warn: 'var(--warn)', bad: 'var(--bad)' };
</script>

<svelte:head>
	<title>Sources — Jambu</title>
	<meta name="description" content="The bibliography of sources digitised in the Jambu etymological dictionary of South Asian languages." />
</svelte:head>

<h1>Sources</h1>
<p class="muted">Sources digitised for Jambu. The coloured bar shows digitisation progress.</p>

{#snippet filters()}
	<SearchMatchToggle {relaxed} onToggle={(value) => (relaxed = value)} />
{/snippet}

<ListToolbar
	value={search}
	placeholder="Search all columns…"
	searchLabel="Search all shown columns"
	resultLabel={`${sortedReferences.length.toLocaleString()} sources`}
	filterCount={relaxed ? 1 : 0}
	onSearch={(value) => (search = value)}
	{filters}
/>

<div class="table-wrap">
	<table class="data mobile-cards">
		<colgroup>
			<col class="ref-col" />
			<col class="editor-col" />
			<col class="extraction-col" />
			<col class="forms-col" />
			<col class="unetym-col" />
		</colgroup>
		<thead>
			<tr>
				<FilterCell label="Reference" sortKey="reference" accent {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Editor" sortKey="editor" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Extraction" sortKey="extraction" {activeSort} onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Forms" sortKey="forms" {activeSort} numeric onFilter={() => {}} onSort={setSort} />
				<FilterCell label="Unetymologised" sortKey="unetym" {activeSort} numeric onFilter={() => {}} onSort={setSort} />
			</tr>
		</thead>
		<tbody>
			{#each sortedReferences as r (r.id)}
				{@const b = badge(r.progress)}
				{@const segments = data.cladeDistributions[r.id] ?? []}
				<tr>
					<td class="lang-cell ref-cell" style="border-left-color: {borderColor[b]}">
						<ReferenceLink reference={r} highlight={search} {relaxed} />
					</td>
					<td data-label="Editor">{@html highlightText(r.editor || '—', search, relaxed)}</td>
					<td data-label="Extraction">{#if r.ocr}<span class="ocr-ref" title="Forms from this reference were parsed with optical character recognition">{@html highlightText('OCR', search, relaxed)}</span>{:else}<span class="faint">{@html highlightText('—', search, relaxed)}</span>{/if}</td>
					<td class="pct" data-label="Forms">
						<ReferenceFormsCount count={r.lemma_count ?? 0} {segments} highlight={numericHighlight((r.lemma_count ?? 0).toLocaleString())} />
					</td>
					<td class="pct" data-label="Unetymologised" title="{(r.unetymologised_count ?? 0).toLocaleString()} of {(r.lemma_count ?? 0).toLocaleString()} forms">
						{@html highlightText(unetymologisedPct(r.lemma_count ?? 0, r.unetymologised_count ?? 0), search, relaxed)}
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
		min-width: 800px;
		table-layout: fixed;
	}
	.ref-col {
		width: auto;
	}
	.editor-col {
		width: 13rem;
	}
	.extraction-col {
		width: 6.5rem;
	}
	.forms-col {
		width: 6.5rem;
	}
	/* wide enough for the header label plus its sort control, so neither spills into Forms */
	.unetym-col {
		width: 11rem;
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
