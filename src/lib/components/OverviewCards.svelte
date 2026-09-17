<script lang="ts">
	import type { Snippet } from 'svelte';
	let { label, children }: { label: string; children: Snippet } = $props();
</script>

<div class="overview-cards" aria-label={label}>{@render children()}</div>

<style>
	.overview-cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 1.25rem; }
	.overview-cards:empty { display: none; }
	@media (max-width: 760px) { .overview-cards { grid-template-columns: 1fr; } }
</style>
