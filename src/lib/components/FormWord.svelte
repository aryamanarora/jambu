<script lang="ts">
	import { safe } from '$lib/render';
	import type { Reference } from '$lib/types';

	let {
		word,
		references = [],
		ocr = false
	}: { word: string; references?: Reference[]; ocr?: boolean | number } = $props();

	const parsedByOcr = $derived(Boolean(ocr) || references.some((reference) => Boolean(reference.ocr)));
	const explanation =
		'Parsed automatically with optical character recognition (OCR). The spelling may contain transcription errors; check the original source when accuracy matters.';
</script>

<span class:ocr-word={parsedByOcr}>{@html safe(word)}</span>{#if parsedByOcr}<span
		class="ocr-badge"
		role="img"
		aria-label={explanation}
		title={explanation}
		data-tooltip={explanation}>OCR</span
	>{/if}

<style>
	.ocr-word {
		text-decoration-line: underline;
		text-decoration-style: dotted;
		text-decoration-color: #b97812;
		text-decoration-thickness: 1.5px;
		text-underline-offset: 0.18em;
		background: color-mix(in srgb, #e8a62a 10%, transparent);
		border-radius: 2px;
	}
	.ocr-badge {
		position: relative;
		display: inline-flex;
		align-items: center;
		margin-left: 0.32rem;
		padding: 0.08rem 0.34rem;
		border: 1px solid color-mix(in srgb, #b97812 55%, transparent);
		border-radius: 999px;
		background: color-mix(in srgb, #e8a62a 16%, var(--surface));
		color: color-mix(in srgb, #8b5708 88%, var(--ink));
		font-family: var(--font-sans);
		font-size: 0.58rem;
		font-style: normal;
		font-weight: 700;
		line-height: 1.25;
		letter-spacing: 0.055em;
		vertical-align: 0.14em;
		white-space: nowrap;
		cursor: help;
	}
	.ocr-badge::after {
		content: attr(data-tooltip);
		position: absolute;
		z-index: 1200;
		left: 50%;
		bottom: calc(100% + 0.45rem);
		width: max-content;
		max-width: min(19rem, 75vw);
		padding: 0.48rem 0.62rem;
		border: 1px solid var(--border-strong);
		border-radius: 6px;
		background: var(--surface);
		box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16);
		color: var(--ink);
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 400;
		line-height: 1.35;
		letter-spacing: normal;
		white-space: normal;
		text-align: left;
		transform: translateX(-50%);
		opacity: 0;
		visibility: hidden;
		pointer-events: none;
		transition: opacity 0.12s ease;
	}
	.ocr-badge:hover::after,
	:global(a:focus-visible) .ocr-badge::after {
		opacity: 1;
		visibility: visible;
	}
</style>
