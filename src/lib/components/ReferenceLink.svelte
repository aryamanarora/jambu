<script lang="ts">
	import { base } from '$app/paths';
	import { onDestroy, tick } from 'svelte';
	import { referenceBibtex } from '$lib/bibtex';
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
	let bibtex = $state('');
	let copyState = $state<'idle' | 'copied' | 'error'>('idle');
	let loadFailed = $state(false);
	let copyButton = $state<HTMLButtonElement | null>(null);
	onDestroy(() => clearTimeout(hideTimer));
	$effect(() => {
		if (!visible) return;
		let cancelled = false;
		bibtex = '';
		loadFailed = false;
		copyState = 'idle';
		referenceBibtex(reference).then((text) => {
			if (!cancelled) bibtex = text;
		}).catch(() => { if (!cancelled) loadFailed = true; });
		return () => { cancelled = true; };
	});
	async function copyBibtex(event: MouseEvent) {
		event.stopPropagation();
		try {
			await navigator.clipboard.writeText(bibtex);
			copyState = 'copied';
		} catch { copyState = 'error'; }
	}
	async function pillKey(event: KeyboardEvent) {
		if (event.key === 'ArrowDown') {
			event.preventDefault();
			show();
			await tick();
			copyButton?.focus();
		} else if (event.key === 'Escape') visible = false;
	}
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
			onkeydown={pillKey}
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
	{#if visible}
		<Tooltip {anchor} prefer="below" portal={as === 'text'} onenter={show} onleave={hide}>
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
			<span class="copy-actions">
				<button type="button" bind:this={copyButton} disabled={!bibtex}
					onfocus={show} onblur={hide} onclick={copyBibtex}
					onkeydown={(event) => { if (event.key === 'Escape') { anchor?.focus(); visible = false; } }}
				>{copyState === 'copied' ? 'Copied!' : 'Copy BibTeX'}</button>
				<span role="status">{loadFailed ? 'Could not load citation. Reopen to retry.' : copyState === 'error' ? 'Copy failed. Please try again.' : copyState === 'copied' ? 'BibTeX copied to clipboard.' : ''}</span>
			</span>
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
	.copy-actions { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; }
	.copy-actions button { padding: 0.25rem 0.5rem; border: 1px solid var(--border-strong); border-radius: 4px; background: var(--surface-2); color: var(--ink); font: inherit; cursor: pointer; }
	.copy-actions button:disabled { opacity: 0.6; cursor: wait; }
	.copy-actions button:focus-visible { outline: 2px solid var(--plum-2); outline-offset: 2px; }
	.copy-actions [role='status'] { font-size: 0.7rem; color: var(--muted); }
</style>
