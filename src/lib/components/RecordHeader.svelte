<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, id, backHref, backLabel, children }: {
		title: string; id: string; backHref: string; backLabel: string; children: Snippet;
	} = $props();
</script>

<header class="record-head">
	<div class="record-title">
		<a class="back-link" href={backHref}>{backLabel}</a>
		<h1 class="headword">{title} <span class="id-tag">[{id}]</span></h1>
	</div>
	<dl class="head-stats">{@render children()}</dl>
</header>

<style>
	.record-head { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem 1.5rem; margin-bottom: 0.9rem; }
	h1 { margin: 0.25rem 0 0; }
	.record-title { min-width: 0; overflow-wrap: anywhere; }
	.back-link { font-size: 0.8rem; color: var(--muted); }
	.head-stats { display: flex; gap: 0.8rem 1.4rem; flex-wrap: wrap; margin: 0; }
	.head-stats :global(dt) { color: var(--muted); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; }
	.head-stats :global(dd) { margin: 0; font-size: 1rem; font-weight: 600; font-variant-numeric: tabular-nums; }
</style>
