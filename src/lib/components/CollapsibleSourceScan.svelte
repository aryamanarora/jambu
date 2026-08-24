<script lang="ts">
	import { safe } from '$lib/render';

	let { content, scanId }: { content: string; scanId: string } = $props();
	let frame = $state<HTMLDivElement | null>(null);
	let clipped = $state(false);
	let expanded = $state(false);

	function measure() {
		if (!frame || expanded) return;
		clipped = frame.scrollHeight - frame.clientHeight > 1;
	}

	function toggle() {
		expanded = !expanded;
		if (!expanded) requestAnimationFrame(measure);
	}

	$effect(() => {
		// Entry routes reuse this component when navigating between headwords. Make the clipping
		// state belong to the current scan, and reattach load listeners to its current images.
		content;
		scanId;
		const node = frame;
		if (!node || typeof ResizeObserver === 'undefined') return;
		expanded = false;
		clipped = false;
		const observer = new ResizeObserver(measure);
		const images = [...node.querySelectorAll('img')];
		const frameId = requestAnimationFrame(measure);
		observer.observe(node);
		for (const image of images) image.addEventListener('load', measure);
		return () => {
			cancelAnimationFrame(frameId);
			observer.disconnect();
			for (const image of images) image.removeEventListener('load', measure);
		};
	});
</script>

<div class="source-scan-shell" class:clipped class:expanded>
	<div
		bind:this={frame}
		class="source-scan-frame"
		class:expanded
		id={scanId}
	>
		{@html safe(content)}
	</div>
	{#if clipped && !expanded}<div class="source-scan-fade" aria-hidden="true"></div>{/if}
	{#if clipped}
		<button
			type="button"
			class="source-scan-toggle"
			onclick={toggle}
			aria-expanded={expanded}
			aria-controls={scanId}
		>
			<span class="source-scan-state">{expanded ? 'Full KEWA scan' : 'KEWA scan clipped'}</span>
			<span>{expanded ? 'Collapse image ↑' : 'Show full image ↓'}</span>
		</button>
	{/if}
</div>

<style>
	.source-scan-shell {
		position: relative;
	}
	.source-scan-frame {
		max-height: 24rem;
		overflow: hidden;
	}
	.source-scan-frame.expanded {
		max-height: none;
		overflow: visible;
	}
	.source-scan-fade {
		position: relative;
		height: 5rem;
		margin-top: -5rem;
		background: linear-gradient(to bottom, transparent, var(--surface-2));
		pointer-events: none;
	}
	.source-scan-toggle {
		position: relative;
		display: flex;
		width: 100%;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		padding: 0.48rem 0.65rem;
		border: 1px solid var(--border-strong);
		border-radius: 6px;
		background: var(--surface);
		color: var(--plum-2);
		font-family: var(--font-sans);
		font-size: 0.78rem;
		font-weight: 600;
		cursor: pointer;
	}
	.source-scan-toggle:hover,
	.source-scan-toggle:focus-visible {
		background: var(--surface-2);
		outline: none;
	}
	.source-scan-state {
		color: var(--muted);
		font-size: 0.7rem;
		font-variant: small-caps;
		letter-spacing: 0.05em;
	}
	:global(.source-scan) {
		margin: 0;
	}
	:global(.source-scan img) {
		display: block;
		max-width: 100%;
		height: auto;
		border-radius: 3px;
		background: #fff;
	}
</style>
