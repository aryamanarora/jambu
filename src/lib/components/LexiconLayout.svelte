<script lang="ts">
	import type { Snippet } from 'svelte';
	import '$lib/styles/atlas.css';
	let { title, label, sideId, sideLabel, open = $bindable(true), sidebar, children }: {
		title: string; label: string; sideId: string; sideLabel: string;
		open?: boolean; sidebar: Snippet; children: Snippet;
	} = $props();
</script>

<div class="lexicon-toolbar">
	<h2>{title}</h2>
	<button type="button" class="side-fold" aria-expanded={open} aria-controls={sideId} onclick={() => open = !open}>
		{open ? 'Hide map & filters' : 'Show map & filters'}
	</button>
</div>
<div class="lexicon-body" class:no-side={!open}>
	<section class="lexicon-col" id="lexicon" aria-label={label}>{@render children()}</section>
	<aside id={sideId} class="side-col atlas" hidden={!open} aria-label={sideLabel}>{@render sidebar()}</aside>
</div>

<style>
	.lexicon-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.8rem 0; margin-top: 1.2rem; border-top: 1px solid var(--border); }
	h2 { margin: 0; font-size: 1.1rem; }
	.side-fold { padding: 0.5rem 0.7rem; border: 1px solid var(--border-strong); border-radius: var(--radius-sm); background: none; color: var(--muted); font: inherit; font-size: 0.8rem; font-weight: 600; white-space: nowrap; cursor: pointer; }
	.side-fold:hover { border-color: var(--plum-2); color: var(--plum-2); }
	.lexicon-body { display: grid; grid-template-columns: minmax(0, 1fr) minmax(17rem, 21rem); gap: 1.5rem; align-items: start; }
	.lexicon-body.no-side { grid-template-columns: minmax(0, 1fr); }
	.lexicon-col { min-width: 0; }
	.side-col { padding: 0 0.85rem 0.85rem; border: 1px solid var(--border); border-radius: var(--radius-sm); position: sticky; top: 4.5rem; max-height: calc(100vh - 5.5rem); overflow-y: auto; min-width: 0; scrollbar-width: thin; scrollbar-color: var(--border-strong) transparent; }
	.side-col[hidden] { display: none; }
	.side-col :global(.pick) { grid-template-areas: 'dot word count' '. meta meta'; }
	.side-col :global(.controls) { padding: 0.35rem 0 0.3rem; }
	.side-col :global(.list) { padding: 0 0 0.5rem; max-height: 18rem; overflow-y: auto; scrollbar-width: thin; }
	.side-col :global(.hint) { padding: 0 0 0.45rem; }
	.side-col :global(.row) { align-items: center; }
	@media (max-width: 1000px) {
		.lexicon-body, .lexicon-body.no-side { grid-template-columns: 1fr; }
		.side-col { position: static; max-height: none; overflow: visible; grid-row: 1; }
	}
</style>
