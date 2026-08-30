<script lang="ts">
	// Hover popover for cross-reference links (`.eref`, carrying data-eref="<entry id>"). The target
	// entry is fetched lazily on first hover and cached, so nothing loads until the user hovers.
	import { getLemma } from '$lib/query';
	import { safe } from '$lib/render';
	import { base } from '$app/paths';
	import type { Lemma } from '$lib/types';
	import FormWord from './FormWord.svelte';
	import Tooltip from './Tooltip.svelte';

	let visible = $state(false);
	let anchor = $state<HTMLElement | null>(null);
	let loading = $state(false);
	let current = $state<Lemma | null>(null);
	let activeId = '';
	const cache = new Map<string, Lemma | null>();
	let hideTimer: ReturnType<typeof setTimeout>;

	async function show(el: HTMLElement) {
		const id = el.getAttribute('data-eref');
		if (!id) return;
		clearTimeout(hideTimer);
		anchor = el; // Tooltip places, clamps and follows scrolling from here
		activeId = id;
		visible = true;
		if (cache.has(id)) {
			current = cache.get(id)!;
			loading = false;
			return;
		}
		loading = true;
		current = null;
		const l = await getLemma(id).catch(() => null);
		cache.set(id, l);
		if (activeId === id) {
			current = l;
			loading = false;
		}
	}

	function scheduleHide() {
		clearTimeout(hideTimer);
		hideTimer = setTimeout(() => (visible = false), 150);
	}

	function hideNow() {
		clearTimeout(hideTimer);
		visible = false;
	}

	function onOver(e: MouseEvent) {
		const el = (e.target as HTMLElement)?.closest?.('.eref') as HTMLElement | null;
		if (el) show(el);
	}
	function onOut(e: MouseEvent) {
		if ((e.target as HTMLElement)?.closest?.('.eref')) scheduleHide();
	}
</script>

<svelte:document onmouseover={onOver} onmouseout={onOut} onclick={hideNow} />

{#if visible}
	<Tooltip {anchor} prefer="below" onenter={() => clearTimeout(hideTimer)} onleave={scheduleHide}>
		<div class="peek">
		{#if loading}
			<span class="peek-muted">loading…</span>
		{:else if current}
			<a class="peek-head" href="{base}/entries/{current.id}">
				<span class="peek-lang">{current.language?.name ?? current.language_id}</span>
				<span class="peek-word"><FormWord word={current.word} references={current.references} /></span>
				<span class="peek-id">[{current.id}]</span>
			</a>
			{#if current.gloss}<div class="peek-gloss">{@html safe(current.gloss)}</div>{/if}
		{:else}
			<span class="peek-muted">entry not found</span>
		{/if}
		</div>
	</Tooltip>
{/if}

<style>
	/* the card chrome is Tooltip.svelte's; this is just the peek's own type */
	.peek {
		font-size: 0.9rem;
		line-height: 1.45;
	}
	.peek-head {
		display: flex;
		align-items: baseline;
		gap: 0.4rem;
		text-decoration: none;
		color: inherit;
	}
	.peek-lang {
		font-size: 0.75rem;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.03em;
	}
	.peek-word {
		font-family: var(--font-serif);
		font-weight: 600;
	}
	.peek-id {
		font-size: 0.72rem;
		color: var(--faint);
	}
	.peek-gloss {
		margin-top: 0.15rem;
		font-family: var(--font-serif);
		color: var(--ink);
	}
	.peek-muted {
		color: var(--muted);
	}
</style>
