<script lang="ts">
	import { base } from '$app/paths';
	import { changeInfo, changeLabel } from '$lib/soundChange';
	import { safe, md } from '$lib/render';
	import RefList from './RefList.svelte';
	import type { Lemma } from '$lib/types';
	import type { AlignSeg } from '$lib/query';

	let {
		lemma,
		segs = [],
		showOrigin = false,
		linkWord = true
	}: {
		lemma: Lemma;
		segs?: AlignSeg[];
		showOrigin?: boolean; // show "← from <etymon>" line (used on the standalone reflex page)
		linkWord?: boolean;
	} = $props();
</script>

<div class="detail">
	<div class="d-main">
		{#if linkWord}
			<a class="d-word" href="{base}/reflexes/{lemma.id}">{@html safe(lemma.word)}</a>
		{:else}
			<span class="d-word">{@html safe(lemma.word)}</span>
		{/if}
		{#if lemma.phonemic}<span class="d-phon">/{lemma.phonemic}/</span>{/if}
		{#if lemma.gloss}<span class="d-gloss">‘{@html safe(lemma.gloss)}’</span>{/if}
		{#if lemma.cognateset}<span class="d-cog">§{lemma.cognateset}</span>{/if}
		<span class="d-src"><RefList references={lemma.references} /></span>
	</div>
	{#if showOrigin && lemma.origin_lemma}
		<div class="d-from">
			← from
			<a href="{base}/entries/{lemma.origin_lemma.id}"
				>{@html safe(lemma.origin_lemma.word)} <span class="id-tag">[{lemma.origin_lemma.id}]</span
				></a
			>{#if lemma.origin_lemma.language}
				<span class="muted">({lemma.origin_lemma.language.name})</span>{/if}
		</div>
	{/if}
	{#if lemma.notes}<div class="d-notes markdown">{@html md(lemma.notes)}</div>{/if}
	{#if segs.length}
		<div class="steps">
			{#each segs as s (s.pos)}
				{@const info = changeInfo(s.change)}
				<span class="step {info.cls}">{changeLabel(s.etymonSeg, s.reflexSeg, s.change)}</span>
			{/each}
		</div>
	{/if}
</div>

<style>
	.detail {
		padding: 0.6rem 0.8rem;
		background: var(--surface-2);
		border-radius: 6px;
		border-left: 3px solid var(--berry);
		font-size: 0.92rem;
	}
	.d-main {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.5rem;
	}
	.d-word {
		font-family: var(--font-serif);
		font-size: 1.1rem;
	}
	.d-phon {
		color: var(--muted);
		font-family: var(--font-serif);
	}
	.d-gloss {
		color: var(--muted);
	}
	.d-cog,
	.d-src {
		font-size: 0.8rem;
		color: var(--muted);
	}
	.d-from {
		margin-top: 0.35rem;
		font-size: 0.88rem;
	}
	.d-notes {
		font-size: 0.88rem;
		margin-top: 0.4rem;
	}
	.steps {
		display: flex;
		flex-wrap: wrap;
		gap: 5px;
		margin-top: 0.5rem;
	}
	.step {
		font-size: 0.72rem;
		padding: 3px 9px;
		border-radius: 999px;
		background: var(--surface);
		border: 1px solid var(--border);
	}
	.step.kept {
		color: var(--faint);
	}
	.step.change {
		color: #a85713;
	}
	.step.loss {
		color: var(--bad);
	}
	.step.add {
		color: #2563a8;
	}
	:global(:root[data-theme='dark']) .step.change,
	:global(:root:not([data-theme='light'])) .step.change {
		color: #e0a35a;
	}
</style>
