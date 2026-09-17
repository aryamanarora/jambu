<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, kind = 'chart', open = $bindable(true), meta, children }: {
		title: string; kind?: 'chart' | 'side'; open?: boolean; meta?: Snippet; children: Snippet;
	} = $props();
</script>

<details class:chart-card={kind === 'chart'} class:side-drawer={kind === 'side'} bind:open>
	<summary>{title}{#if meta}<span class="card-meta">{@render meta()}</span>{/if}</summary>
	{@render children()}
</details>

<style>
	.chart-card { min-width: 0; padding: 0.8rem 1rem; border: 1px solid var(--border); border-radius: var(--radius-sm); }
	.chart-card summary { cursor: pointer; font-weight: 600; font-size: 0.85rem; }
	.chart-card[open] summary { margin-bottom: 0.65rem; }
	.card-meta { float: right; color: var(--muted); font-weight: 400; letter-spacing: 0; text-transform: none; }
	.chart-card :global(.legend) { flex: 1; min-width: 0; max-height: 11rem; overflow-y: auto; scrollbar-width: thin; }
	.side-drawer { margin-top: 0.75rem; border-top: 1px solid var(--border); padding-top: 0.6rem; }
	.side-drawer:first-child { border-top: 0; margin-top: 0; }
	.side-drawer > summary { display: list-item; padding: 0.35rem 0; font-size: 0.8rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; cursor: pointer; }
	.side-drawer[open] > summary { margin-bottom: 0.6rem; }
	@media (max-width: 640px) {
		.chart-card :global(.donut) { width: 112px; height: 112px; }
		.chart-card :global(.donut-wrap) { gap: 0.8rem; }
		.chart-card :global(.legend button) { display: grid; grid-template-columns: 0.7rem minmax(0, 1fr); gap: 0.15rem 0.4rem; }
		.chart-card :global(.ct) { grid-column: 2; font-size: 0.72rem; }
	}
</style>
