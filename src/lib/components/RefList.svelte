<script lang="ts">
	import type { Reference } from '$lib/types';
	import ReferenceLink from './ReferenceLink.svelte';

	let { references = [] }: { references?: Reference[] } = $props();
	// attachReferences already combines repeated locators for one source; retain a defensive dedupe.
	const refs = $derived([...new Map(references.map((r) => [r.id, r])).values()]);
</script>

{#if refs.length}
	<span class="references">{#each refs as reference (reference.id)}<ReferenceLink {reference} />{/each}</span>
{:else}<span class="faint">—</span>{/if}

<style>
	.references { display: inline-flex; flex-wrap: wrap; gap: 0.28rem; max-width: 100%; }
</style>
