<script lang="ts">
	// The frame every full-bleed atlas page shares: an edge-to-edge map with a panel floating over
	// each side. The panels' contents are the page's business; their geometry, chrome and
	// narrow-screen behaviour are not, and live in atlas.css alongside the row grammar the lists
	// inside them use.
	import type { Snippet } from 'svelte';
	import '$lib/styles/atlas.css';

	let {
		map,
		left,
		right,
		leftOpen = true,
		rightOpen = true
	}: {
		map: Snippet;
		left: Snippet;
		right: Snippet;
		leftOpen?: boolean; // folded panels keep their head and shrink to it
		rightOpen?: boolean;
	} = $props();
</script>

<div class="atlas">
	<div class="atlas-map">{@render map()}</div>
	<aside class="atlas-panel left" class:collapsed={!leftOpen}>{@render left()}</aside>
	<aside class="atlas-panel right" class:collapsed={!rightOpen}>{@render right()}</aside>
</div>
