<script lang="ts">
	// Hover popover for cross-reference links (`.eref`, carrying data-eref="<entry id>"). The target
	// entry is fetched lazily on first hover and cached, so nothing loads until the user hovers.
	import { getLemma } from '$lib/query';
	import { safe } from '$lib/render';
	import { base } from '$app/paths';
	import type { Lemma } from '$lib/types';

	let visible = $state(false);
	let x = $state(0);
	let y = $state(0);
	let below = $state(true);
	let loading = $state(false);
	let current = $state<Lemma | null>(null);
	let activeId = '';
	const cache = new Map<string, Lemma | null>();
	let hideTimer: ReturnType<typeof setTimeout>;

	async function show(el: HTMLElement) {
		const id = el.getAttribute('data-eref');
		if (!id) return;
		clearTimeout(hideTimer);
		const r = el.getBoundingClientRect();
		// clamp horizontally so a wide card never runs off the right edge
		x = Math.min(r.left, window.innerWidth - 360);
		below = r.bottom + 140 < window.innerHeight; // flip above near the viewport bottom
		y = below ? r.bottom + 6 : window.innerHeight - r.top + 6;
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
	<div
		class="peek"
		class:above={!below}
		style="left:{x}px; {below ? 'top' : 'bottom'}:{y}px"
		role="tooltip"
		onmouseenter={() => clearTimeout(hideTimer)}
		onmouseleave={scheduleHide}
	>
		{#if loading}
			<span class="peek-muted">loading…</span>
		{:else if current}
			<a class="peek-head" href="{base}/entries/{current.id}">
				<span class="peek-lang">{current.language?.name ?? current.language_id}</span>
				<span class="peek-word">{@html safe(current.word)}</span>
				<span class="peek-id">[{current.id}]</span>
			</a>
			{#if current.gloss}<div class="peek-gloss">{@html safe(current.gloss)}</div>{/if}
		{:else}
			<span class="peek-muted">entry not found</span>
		{/if}
	</div>
{/if}

<style>
	.peek {
		position: fixed;
		z-index: 1000;
		max-width: 22rem;
		padding: 0.5rem 0.7rem;
		background: var(--surface);
		border: 1px solid var(--border-strong);
		border-radius: 8px;
		box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
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
