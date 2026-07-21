<script lang="ts">
	import { base } from '$app/paths';
	import { safe } from '$lib/render';
	import type { AncestorRef } from '$lib/query';

	// A node's place in the etymon graph: the "from" chain shown under the headword on both entry and
	// reflex pages. `chain` is the ancestry level by level (nearest first); the first level uses
	// `label` ("Reflex of" / "Variant of" / "Derived from"), deeper levels the "↳ from" continuation.
	// A term's language is printed before it, but only when it differs from the preceding node's.
	let {
		label,
		chain,
		startLang
	}: { label: string; chain: AncestorRef[][]; startLang?: string | null } = $props();

	const rendered = $derived.by(() => {
		let running = startLang ?? null;
		return chain.map((level) =>
			level.map((p) => {
				const showLang = !!p.lang && p.lang !== running;
				running = p.lang ?? running;
				return { ...p, showLang };
			})
		);
	});
</script>

{#if rendered.length && rendered[0].length}
	<div class="ancestry">
		{#each rendered as level, li (li)}
			<div class="anc-line">
				<span class="kind">{li === 0 ? label : '↳ from'}</span>
				{#each level as p, i (p.id)}{#if p.showLang}<span class="lang">{p.lang}</span> {/if}<a
						class="anc"
						href="{base}/{p.kind === 'reflex' ? 'reflexes' : 'entries'}/{p.id}"
						>{@html safe(p.word)} <span class="id-tag">[{p.id}]</span></a
					>{#if i < level.length - 1}<span class="sep">, </span>{/if}{/each}
			</div>
		{/each}
	</div>
{/if}

<style>
	.ancestry {
		margin: 0.1rem 0 0.9rem;
	}
	.anc-line {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.4rem;
		font-size: 0.95rem;
		margin-bottom: 0.15rem;
	}
	.kind {
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-size: 0.72rem;
		font-weight: 600;
		color: var(--muted);
		padding-top: 0.12rem;
		white-space: nowrap;
	}
	.lang {
		color: var(--muted);
		margin-right: -0.2rem;
	}
	.anc {
		font-family: var(--font-serif);
	}
	.sep {
		margin-left: -0.25rem;
	}
</style>
