<script lang="ts">
	// The shared hover card. Callers own *when* it shows — and the small close delay that lets a
	// pointer cross between adjacent targets without flicker — while this owns everything about
	// where it sits and how it looks, so the popovers around the app stop drifting apart.
	//
	// It takes the anchor element rather than coordinates, which is what lets it re-place itself
	// when the page or a panel scrolls underneath it. And it is `fixed`: bar segments, table cells
	// and inline links all live inside boxes that clip or scroll, and an absolutely-positioned card
	// would be cut off by them.
	import type { Snippet } from 'svelte';

	let {
		anchor,
		prefer = 'above',
		interactive = true,
		portal = false,
		onenter,
		onleave,
		children
	}: {
		anchor: HTMLElement | null;
		prefer?: 'above' | 'below'; // which side to take when both fit
		interactive?: boolean; // false for a pure tooltip the pointer should fall through
		portal?: boolean; // escape a parent control when the card contains its own actions
		onenter?: () => void; // pointer moved onto the card — callers cancel their close timer
		onleave?: () => void;
		children: Snippet;
	} = $props();

	let el = $state<HTMLElement | null>(null);
	let placed = $state<{ left: number; top: number } | null>(null);
	function mountPortal(node: HTMLElement) {
		if (!portal) return;
		document.body.appendChild(node);
		return { destroy: () => node.remove() };
	}

	function place() {
		if (!el || !anchor) return;
		const a = anchor.getBoundingClientRect();
		const r = el.getBoundingClientRect();
		const M = 8; // keep this far clear of every viewport edge
		const GAP = 9;
		const fitsAbove = a.top - r.height - GAP >= M;
		const fitsBelow = a.bottom + r.height + GAP <= window.innerHeight - M;
		const below = prefer === 'below' ? fitsBelow || !fitsAbove : !fitsAbove && fitsBelow;
		placed = {
			left: Math.max(M, Math.min(a.left + a.width / 2 - r.width / 2, window.innerWidth - r.width - M)),
			top: below ? a.bottom + GAP : a.top - r.height - GAP
		};
	}

	// Follow the page for as long as the card is mounted. This effect reads nothing reactive on
	// purpose, so the listeners are attached once and torn down only on destroy rather than
	// churning every time the content changes. Capture-phase scroll catches a scrolling panel,
	// not just the window.
	$effect(() => {
		window.addEventListener('scroll', place, true);
		window.addEventListener('resize', place);
		return () => {
			window.removeEventListener('scroll', place, true);
			window.removeEventListener('resize', place);
		};
	});

	// Re-place when the anchor, the side, or the content changes — content because a card that
	// grew a line needs to move up to keep its bottom edge on the anchor.
	$effect(() => {
		anchor;
		prefer;
		children;
		place();
	});
</script>

<div
	use:mountPortal
	class="tip"
	class:measuring={!placed}
	class:inert={!interactive}
	bind:this={el}
	style={placed ? `left: ${placed.left}px; top: ${placed.top}px` : ''}
	role="tooltip"
	onmouseenter={onenter}
	onmouseleave={onleave}
>
	{@render children()}
</div>

<style>
	.tip {
		position: fixed;
		top: 0;
		left: 0;
		z-index: 1200;
		min-width: 9.5rem;
		max-width: min(22.5rem, calc(100vw - 1rem));
		padding: 0.55rem 0.72rem;
		border: 1px solid var(--border-strong);
		border-radius: 9px;
		background: var(--surface);
		color: var(--ink);
		box-shadow: 0 10px 30px rgba(20, 12, 18, 0.3);
	}
	/* the first frame exists only to be measured; showing it would flash the card at 0,0 */
	.tip.measuring {
		visibility: hidden;
	}
	.tip.inert {
		pointer-events: none;
	}
</style>
