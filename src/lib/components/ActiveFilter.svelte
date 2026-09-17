<script lang="ts">
	let { label, value, clearHref, clearLabel }: { label: string; value: string; clearHref: string; clearLabel: string } = $props();
</script>

<p class="active-filter">
	<span>{label} <strong>{value}</strong></span>
	<a href={clearHref} data-sveltekit-noscroll>{clearLabel}</a>
</p>

<style>
	.active-filter { flex-wrap: wrap; display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin: 0 0 0.6rem; padding: 0.5rem 0.7rem; border: 1px solid color-mix(in srgb, var(--berry) 35%, var(--border)); border-radius: var(--radius-sm); background: color-mix(in srgb, var(--berry) 7%, transparent); font-size: 0.85rem; }
	a { font-size: 0.8rem; font-weight: 600; }
</style>
