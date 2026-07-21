<script lang="ts">
	import { base } from '$app/paths';
	import type { Reference } from '$lib/types';

	let { references = [] }: { references?: Reference[] } = $props();
	// dedupe by id — an entry can end up citing the same reference twice (e.g. after an addenda merge)
	const refs = $derived([...new Map(references.map((r) => [r.id, r])).values()]);
</script>

{#if refs.length}
	{#each refs as r, i (r.id)}{#if i > 0}, {/if}<a
			href="{base}/references/{r.id}"
			title={r.short}>{r.short}</a
		>{/each}
{:else}<span class="faint">—</span>{/if}
