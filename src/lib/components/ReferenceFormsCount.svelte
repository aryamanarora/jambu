<script lang="ts">
	import { onDestroy } from 'svelte';
	import { CLADE_ORDER, cladeColor } from '$lib/clades';
	import { highlightText } from '$lib/render';
	import Tooltip from './Tooltip.svelte';

	let { count, segments, highlight }: {
		count: number;
		segments: { clade: string; count: number }[];
		highlight: string;
	} = $props();
	let anchor = $state<HTMLButtonElement | null>(null);
	let visible = $state(false);
	let hideTimer: ReturnType<typeof setTimeout>;
	const total = $derived(segments.reduce((sum, segment) => sum + segment.count, 0));

	function show() {
		clearTimeout(hideTimer);
		visible = true;
	}
	function hide() {
		clearTimeout(hideTimer);
		hideTimer = setTimeout(() => (visible = false), 120);
	}
	onDestroy(() => clearTimeout(hideTimer));
</script>

<button
	bind:this={anchor}
	type="button"
	class="forms-count"
	aria-label={`${count.toLocaleString()} forms; show clade breakdown`}
	aria-expanded={visible}
	onmouseenter={show}
	onmouseleave={hide}
	onfocus={show}
	onblur={hide}
	onclick={show}
	onkeydown={(event) => { if (event.key === 'Escape') visible = false; }}
>{@html highlightText(count.toLocaleString(), highlight)}</button>

{#if visible}
	<Tooltip {anchor} onenter={show} onleave={hide}>
		<div class="clade-details">
			<strong>Forms by clade</strong>
			<span class="clades" role="img" aria-label={segments.map((segment) => `${segment.clade}: ${segment.count.toLocaleString()} forms${segment.count * 20 > total || segment.count > 100 ? ', highlighted' : ''}`).join('; ') || 'No forms'}>
				{#each CLADE_ORDER as clade (clade)}
					{@const n = segments.find((segment) => segment.clade === clade)?.count ?? 0}
					<span class="clade-block"
						style={n * 20 > total || n > 100 ? `background: ${cladeColor(clade)}` : ''}
						title={`${clade}: ${n.toLocaleString()} forms (${total ? (100 * n / total).toFixed(1) : '0.0'}%)`}
					></span>
				{/each}
			</span>
			<span class="muted">Highlighted: &gt;5% or &gt;100 forms.</span>
		</div>
	</Tooltip>
{/if}

<style>
	.forms-count {
		padding: 0;
		border: 0;
		border-radius: 0;
		background: transparent;
		color: inherit;
		font: inherit;
		cursor: help;
		text-decoration: underline dotted var(--muted);
		text-underline-offset: 0.2em;
	}
	.forms-count:focus-visible { outline: 2px solid var(--border-strong); outline-offset: 3px; }
	.clade-details {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 400;
		text-align: left;
	}
</style>
