<script lang="ts">
	import { base } from '$app/paths';
	import type { Reference } from '$lib/types';

	let { references = [] }: { references?: Reference[] } = $props();
	// attachReferences already combines repeated locators for one source; retain a defensive dedupe.
	const refs = $derived([...new Map(references.map((r) => [r.id, r])).values()]);
</script>

{#if refs.length}
		{#each refs as r, i (r.id)}{#if i > 0}, {/if}<a
			href="{base}/references/{r.id}"
			title={`${r.short || r.id}${r.locator ? `, ${r.locator}` : ''}${r.ocr ? ' · OCR-derived' : ''}`}>{r.short || r.id}{#if r.locator}, {r.locator}{/if}</a
		>{/each}
{:else}<span class="faint">—</span>{/if}
