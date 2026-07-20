<script lang="ts">
	import { PAGE_SIZE } from '$lib/types';

	let {
		count,
		page,
		onpage
	}: { count: number; page: number; onpage: (n: number) => void } = $props();

	const pages = $derived(Math.max(1, Math.ceil(count / PAGE_SIZE)));
</script>

{#if pages > 1}
	<div class="pager">
		<button class="btn" disabled={page <= 1} onclick={() => onpage(page - 1)}>← Prev</button>
		<span class="muted">Page {page} of {pages.toLocaleString()}</span>
		<button class="btn" disabled={page >= pages} onclick={() => onpage(page + 1)}>Next →</button>
	</div>
{/if}
