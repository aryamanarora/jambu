<script lang="ts">
	import { base } from '$app/paths';
	import { highlightText, md, referenceLabel, type HighlightQuery } from '$lib/render';
	import type { Reference } from '$lib/types';

	type PartialReference = Partial<Reference> & { id: string };
	import Tooltip from './Tooltip.svelte';

	// The source pill: `§ Label`, with the citation on hover. One implementation, wherever a source
	// is named — a form's citation, a changelog entry, a donut legend.
	//
	// `as="text"` renders the same pill without the anchor, for the places it has to sit inside
	// another control (a legend row that is itself a filter button); nested interactive elements
	// are invalid and unreachable by keyboard.
	//
	// `reference` may be partial: a caller that only knows an id and a label still gets the pill,
	// just without the parts of the card it has no data for.
	let {
		reference,
		as = 'link',
		highlight,
		relaxed = false
	}: {
		reference: PartialReference;
		as?: 'link' | 'text';
		highlight?: HighlightQuery;
		relaxed?: boolean;
	} = $props();
	let anchor = $state<HTMLElement | null>(null);
	let visible = $state(false);
	let hideTimer: ReturnType<typeof setTimeout>;
	// referenceLabel condenses a full citation down to "authors year"; with no citation to read it
	// would strip a caller's own label to whatever year it happens to contain. A caller that
	// supplies a label and nothing else already knows what the source is called.
	const label = $derived(
		reference.source
			? referenceLabel({
					id: reference.id,
					short: reference.short ?? null,
					source: reference.source
				})
			: (reference.short ?? reference.id)
	);
	// with nothing but an id and a label there is no card worth showing
	const hasCard = $derived(
		Boolean(reference.source || reference.editor || reference.lemma_count != null)
	);

	function show() {
		clearTimeout(hideTimer);
		visible = true;
	}
	function hide() {
		clearTimeout(hideTimer);
		hideTimer = setTimeout(() => (visible = false), 80);
	}
	const accessibleLabel = $derived(
		`${label}${reference.locator ? `, ${reference.locator}` : ''}${reference.ocr ? ', OCR-derived' : ''}`
	);

</script>

{#snippet pill()}
	<span class="mark" aria-hidden="true">§</span>
	<span class="short">{@html highlightText(label, highlight, relaxed)}</span>
{/snippet}

<span class="reference">
	{#if as === 'link'}
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
			{@render pill()}
		</a>
	{:else}
		<span
			bind:this={anchor}
			class="reference-link"
			role="note"
			onmouseenter={show}
			onmouseleave={hide}
			aria-label={accessibleLabel}
		>
			{@render pill()}
		</span>
	{/if}
	{#if visible && hasCard}
		<Tooltip {anchor} prefer="below" interactive={false}>
			<span class="tooltip">
			<span class="tooltip-head">
				<span class="tooltip-short">{label}</span>
				<span class="tooltip-id">{reference.short || reference.id} · {reference.id}</span>
			</span>
			{#if reference.locator}<span class="tooltip-locator">Cited at {reference.locator}</span>{/if}
			{#if reference.source}<span class="tooltip-citation markdown">{@html md(reference.source)}</span>{/if}
			{#if reference.lemma_count != null || reference.editor || reference.ocr}
				<span class="tooltip-meta">
					{#if reference.lemma_count != null}{reference.lemma_count.toLocaleString()} forms{/if}{#if reference.editor}{reference.lemma_count != null ? ' · ' : ''}edited by {reference.editor}{/if}{#if reference.ocr}{' · '}OCR-derived{/if}
				</span>
			{/if}
			</span>
		</Tooltip>
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
	/* the text variant sits inside someone else's control, so it must not eat the pointer */
	span.reference-link { cursor: inherit; }
	.mark { display: inline-flex; align-items: center; justify-content: center; width: 1rem; height: 1rem; border-radius: 50%; background: color-mix(in srgb, var(--plum-2) 9%, transparent); color: var(--muted); font-family: var(--font-serif); font-size: 0.65rem; font-weight: 600; }
	.short { overflow: hidden; color: var(--ink); text-overflow: ellipsis; font-weight: 400; }
	/* the card chrome is Tooltip.svelte's; this is the citation's own layout and type */
	.tooltip {
		display: flex;
		flex-direction: column;
		font-family: var(--font-sans);
		font-size: 0.78rem;
		line-height: 1.4;
		white-space: normal;
	}
	.tooltip-head { display: flex; align-items: baseline; gap: 0.45rem; }
	.tooltip-short { color: var(--ink); font-family: var(--font-serif); font-size: 0.96rem; font-weight: 600; }
	.tooltip-id { color: var(--faint); font-size: 0.68rem; }
	.tooltip-locator { margin-top: 0.12rem; color: var(--berry); font-weight: 600; }
	.tooltip-citation { display: block; margin-top: 0.3rem; color: var(--ink); }
	.tooltip-citation :global(p) { margin: 0; }
	.tooltip-meta { margin-top: 0.4rem; padding-top: 0.35rem; border-top: 1px solid var(--border); color: var(--muted); font-size: 0.7rem; }
</style>
