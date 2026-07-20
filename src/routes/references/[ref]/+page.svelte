<script lang="ts">
	import { md } from '$lib/render';

	let { data } = $props();
	const ref = $derived(data.reference);

	function badge(progress: string): 'ok' | 'warn' | 'bad' {
		if (progress === 'Yes') return 'ok';
		if (progress === 'Partial') return 'warn';
		return 'bad';
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

<style>
	.source {
		margin-top: 1rem;
		font-size: 1.05rem;
	}
	h1 .badge {
		vertical-align: middle;
		margin-left: 0.5rem;
	}
</style>
