<script lang="ts">
	import { base } from '$app/paths';
	import type { Reference } from '$lib/types';

	let { references = [] }: { references?: Reference[] } = $props();
</script>

{#if references && references.length}
	{#each references as r, i (r.id)}{#if i > 0}, {/if}<a
			href="{base}/references/{r.id}"
			title={r.short}>{r.short}</a
		>{/each}
{:else}<span class="faint">—</span>{/if}
