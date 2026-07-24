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

	function badge(progress: string): 'ok' | 'warn' | 'bad' {
		if (progress === 'Yes') return 'ok';
		if (progress === 'Partial') return 'warn';
		return 'bad';
	}
	function unetymologisedPct(): string {
		return (ref.lemma_count ?? 0)
			? `${(((ref.unetymologised_count ?? 0) / ref.lemma_count) * 100).toFixed(1)}%`
			: '—';
	}
</script>

<svelte:head>
	<title>{ref.short} [{ref.id}] — Jambu</title>
</svelte:head>

<h1 class="headword">
	{ref.short} <span class="id-tag">[{ref.id}]</span>
	<span class="badge {badge(ref.progress)}">{ref.progress}</span>
</h1>

<div class="card markdown source">{@html md(ref.source)}</div>

<dl class="props card provenance">
	<div class="prop"><dt>Provenance</dt><dd>{ref.provenance || 'Not recorded'}</dd></div>
	<div class="prop"><dt>Editor</dt><dd>{ref.editor || 'Not recorded'}</dd></div>
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
	.provenance {
		margin-top: 0.75rem;
		padding: 0.7rem 1rem;
	}
	.provenance .prop {
		display: grid;
		grid-template-columns: 7rem minmax(0, 1fr);
		gap: 1rem;
	}
	.provenance .prop + .prop {
		margin-top: 0.55rem;
		padding-top: 0.55rem;
		border-top: 1px solid var(--border);
	}
	.provenance dt {
		color: var(--muted);
		font-weight: 600;
	}
	.provenance dd {
		margin: 0;
		font-family: var(--font-mono);
		font-size: 0.88rem;
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
