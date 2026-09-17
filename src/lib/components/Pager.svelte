<script lang="ts">
	import { PAGE_SIZE } from '$lib/types';

	let {
		count,
		page,
		pageSize = PAGE_SIZE,
		disabled = false,
		label = 'Results pages',
		always = false,
		onpage
	}: {
		count: number; page: number; pageSize?: number; disabled?: boolean;
		label?: string; always?: boolean; onpage: (n: number) => void;
	} = $props();

	const pages = $derived(Math.max(1, Math.ceil(count / pageSize)));
</script>

{#if always || pages > 1}
	<nav class="pager" aria-label={label}>
		<button type="button" class="btn" disabled={disabled || page <= 1} onclick={() => onpage(page - 1)}>← Prev</button>
		<span class="muted">Page {page} of {pages.toLocaleString()}</span>
		<button type="button" class="btn" disabled={disabled || page >= pages} onclick={() => onpage(page + 1)}>Next →</button>
	</nav>
{/if}
