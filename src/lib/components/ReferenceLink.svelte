<script lang="ts">
	import { base } from '$app/paths';
	import { md, referenceLabel } from '$lib/render';
	import type { Reference } from '$lib/types';

	let { reference }: { reference: Reference } = $props();
	let anchor = $state<HTMLAnchorElement | null>(null);
	let visible = $state(false);
	let left = $state(0);
	let top = $state(0);
	let above = $state(false);
	let hideTimer: ReturnType<typeof setTimeout>;
	const label = $derived(referenceLabel(reference));

	function place() {
		if (!anchor) return;
		const rect = anchor.getBoundingClientRect();
		const width = Math.min(360, window.innerWidth - 16);
		left = Math.max(8, Math.min(rect.left, window.innerWidth - width - 8));
		above = rect.bottom + 190 > window.innerHeight && rect.top > 190;
		top = above ? rect.top - 7 : rect.bottom + 7;
	}
	function show() {
		clearTimeout(hideTimer);
		place();
		visible = true;
	}
	function hide() {
		clearTimeout(hideTimer);
		hideTimer = setTimeout(() => (visible = false), 80);
	}
	const accessibleLabel = $derived(
		`${label}${reference.locator ? `, ${reference.locator}` : ''}${reference.ocr ? ', OCR-derived' : ''}`
	);

	$effect(() => {
		if (!visible) return;
		window.addEventListener('scroll', place, true);
		window.addEventListener('resize', place);
		return () => {
			window.removeEventListener('scroll', place, true);
			window.removeEventListener('resize', place);
		};
	});
</script>

<span class="reference">
	<a
		bind:this={anchor}
		class="reference-link"
		href="{base}/references/{reference.id}"
		onmouseenter={show}
		onmouseleave={hide}
		onfocus={show}
		onblur={hide}
		aria-label={accessibleLabel}
	>
		<span class="mark" aria-hidden="true">§</span>
		<span class="short">{label}</span>
	</a>
	{#if visible}
		<span
			class="tooltip"
			class:above
			role="tooltip"
			style="left:{left}px; top:{top}px"
		>
			<span class="tooltip-head">
				<span class="tooltip-short">{label}</span>
				<span class="tooltip-id">{reference.short || reference.id} · {reference.id}</span>
			</span>
			{#if reference.locator}<span class="tooltip-locator">Cited at {reference.locator}</span>{/if}
			{#if reference.source}<span class="tooltip-citation markdown">{@html md(reference.source)}</span>{/if}
			<span class="tooltip-meta">
				{reference.lemma_count.toLocaleString()} forms{#if reference.editor}{' · '}edited by {reference.editor}{/if}{#if reference.ocr}{' · '}OCR-derived{/if}
			</span>
		</span>
	{/if}
</span>

<style>
	.reference { display: inline-flex; min-width: 0; }
	.reference-link {
		display: inline-flex;
		align-items: baseline;
		gap: 0.28rem;
		max-width: 100%;
		padding: 0.13rem 0.42rem 0.15rem 0.25rem;
		border: 1px solid var(--border);
		border-radius: 999px;
		background: var(--surface);
		font-family: var(--font-sans);
		font-size: 0.78rem;
		line-height: 1.25;
		text-decoration: none;
		white-space: nowrap;
	}
	.reference-link:hover, .reference-link:focus-visible { border-color: var(--border-strong); background: var(--surface-2); outline: none; }
	.mark { display: inline-flex; align-items: center; justify-content: center; width: 1rem; height: 1rem; border-radius: 50%; background: color-mix(in srgb, var(--plum-2) 9%, transparent); color: var(--muted); font-family: var(--font-serif); font-size: 0.65rem; font-weight: 600; }
	.short { overflow: hidden; color: var(--ink); text-overflow: ellipsis; font-weight: 400; }
	.tooltip {
		position: fixed;
		z-index: 1200;
		display: flex;
		flex-direction: column;
		width: min(22.5rem, calc(100vw - 1rem));
		padding: 0.65rem 0.75rem;
		border: 1px solid var(--border-strong);
		border-radius: 9px;
		background: var(--surface);
		box-shadow: 0 8px 26px rgba(0, 0, 0, 0.2);
		color: var(--ink);
		font-family: var(--font-sans);
		font-size: 0.78rem;
		line-height: 1.4;
		white-space: normal;
		pointer-events: none;
	}
	.tooltip.above { transform: translateY(-100%); }
	.tooltip-head { display: flex; align-items: baseline; gap: 0.45rem; }
	.tooltip-short { color: var(--ink); font-family: var(--font-serif); font-size: 0.96rem; font-weight: 600; }
	.tooltip-id { color: var(--faint); font-size: 0.68rem; }
	.tooltip-locator { margin-top: 0.12rem; color: var(--berry); font-weight: 600; }
	.tooltip-citation { display: block; margin-top: 0.3rem; color: var(--ink); }
	.tooltip-citation :global(p) { margin: 0; }
	.tooltip-meta { margin-top: 0.4rem; padding-top: 0.35rem; border-top: 1px solid var(--border); color: var(--muted); font-size: 0.7rem; }
</style>
