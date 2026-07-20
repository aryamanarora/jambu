<script lang="ts">
	import { base } from '$app/paths';
	import { safe } from '$lib/render';

	// A node's place in the etymon graph: the "from" line shown under the headword on both entry and
	// reflex pages (the two are one node type — this is the shared piece that merges them).
	let {
		label,
		parents
	}: {
		label: string; // "Reflex of" (a reflex) | "Derived from" (a compound/derived etymon)
		parents: { id: string; word: string; lang?: string | null }[];
	} = $props();
</script>

{#if parents.length}
	<div class="ancestry">
		<span class="kind">{label}</span>
		{#each parents as p, i (p.id)}<a class="anc" href="{base}/entries/{p.id}"
				>{@html safe(p.word)} <span class="id-tag">[{p.id}]</span></a
			>{#if p.lang}<span class="muted">&nbsp;({p.lang})</span>{/if}{#if i < parents.length - 1}<span
					class="sep">, </span
				>{/if}{/each}
	</div>
{/if}

<style>
	.ancestry {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.4rem;
		margin: 0.1rem 0 0.9rem;
		font-size: 0.95rem;
	}
	.kind {
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-size: 0.72rem;
		font-weight: 600;
		color: var(--muted);
		padding-top: 0.12rem;
	}
	.anc {
		font-family: var(--font-serif);
	}
	.sep {
		margin-left: -0.25rem;
	}
</style>
