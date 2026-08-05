<script lang="ts">
	import { md } from '$lib/render';
	import Donut from '$lib/components/Donut.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';
	import { getReferenceLanguageDistribution, type OriginSlice } from '$lib/query';

	let { data } = $props();
	const ref = $derived(data.reference);
	let languages = $state<OriginSlice[]>([]);
	let currentRef = '';
	$effect(() => {
		if (ref.id !== currentRef) {
			currentRef = ref.id;
			languages = [];
			getReferenceLanguageDistribution(ref.id).then((rows) => (languages = rows));
		}
	});

	function badge(progress: string | null): 'ok' | 'warn' | 'bad' {
		if (progress === 'Yes') return 'ok';
		if (progress === 'Partial') return 'warn';
		return 'bad';
	}
	function unetymologisedPct(): string {
		return (ref.lemma_count ?? 0)
			? `${(((ref.unetymologised_count ?? 0) / ref.lemma_count) * 100).toFixed(1)}%`
			: '—';
	}
	function provenanceFiles(provenance: string | null): string[] {
		return provenance?.split(';').map((file) => file.trim()).filter(Boolean) ?? [];
	}
	function provenanceUrl(file: string): string | null {
		return file.startsWith('data/')
			? `https://github.com/moli-mandala/data/blob/main/${file}`
			: null;
	}
</script>

<svelte:head>
	<title>{ref.short || ref.id} [{ref.id}] — Jambu</title>
</svelte:head>

<h1 class="headword">
	{ref.short || ref.id} <span class="id-tag">[{ref.id}]</span>
	<span class="badge {badge(ref.progress)}">{ref.progress || 'No'}</span>
</h1>

<div class="card markdown source">
	{@html md(ref.source || `Reference abbreviation ${ref.id}; full citation not yet catalogued.`)}
</div>

<dl class="props card reference-metadata">
	<div class="prop">
		<dt>Provenance</dt>
		<dd>
			{#each provenanceFiles(ref.provenance) as file, index}
				{@const url = provenanceUrl(file)}
				{#if index > 0}; {/if}
				{#if url}<a href={url} rel="noreferrer">{file}</a>{:else}{file}{/if}
			{:else}
				Not recorded
			{/each}
		</dd>
	</div>
	<div class="prop"><dt>Editor</dt><dd>{ref.editor || 'Not recorded'}</dd></div>
	<div class="prop"><dt>Extraction</dt><dd>{ref.ocr ? 'Optical character recognition (OCR)' : 'Not marked as OCR'}</dd></div>
	<div class="prop">
		<dt>Unetymologised</dt>
		<dd>{unetymologisedPct()} ({(ref.unetymologised_count ?? 0).toLocaleString()} of {(ref.lemma_count ?? 0).toLocaleString()} forms)</dd>
	</div>
</dl>

{#if languages.length}
	<section>
		<h2>Language distribution</h2>
		<Donut slices={languages} label="Distribution of forms cited by language" unit="forms" />
	</section>
{/if}

<section>
	<h2>Cited forms</h2>
	<ReflexesView referenceId={ref.id} />
</section>

<style>
	.source {
		margin-top: 1rem;
		font-size: 1.05rem;
	}
	.reference-metadata {
		margin: 1rem 0 0;
		padding: 0.4rem 1.15rem;
	}
	.prop {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1.5rem;
		padding: 0.55rem 0;
		border-bottom: 1px solid var(--border);
	}
	.prop:last-child {
		border-bottom: none;
	}
	.prop dt {
		color: var(--muted);
		font-size: 0.85rem;
		font-weight: 600;
	}
	.prop dd {
		margin: 0;
		font-weight: 500;
		text-align: right;
		font-variant-numeric: tabular-nums;
		overflow-wrap: anywhere;
	}
	section {
		margin-top: 1.6rem;
	}
	h1 .badge {
		vertical-align: middle;
		margin-left: 0.5rem;
	}
</style>
