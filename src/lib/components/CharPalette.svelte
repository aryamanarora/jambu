<script lang="ts">
	// Special-character palette, ported from neojambu/scripts.js.
	import { floatingPanel } from '$lib/floatingPanel';
	const CHARS = ['ŋ', 'ṭ', 'ḍ', 'ṇ', 'ṣ', 'ṛ', 'r̩', 'r̆', 'ṁ', 'ʰ'];
	let { oninsert, anchor = null }: { oninsert: (c: string) => void; anchor?: HTMLElement | null } =
		$props();
</script>

<div class="palette" role="toolbar" aria-label="Insert special character" use:floatingPanel={anchor}>
	{#each CHARS as c (c)}
		<!-- mousedown+preventDefault so the click doesn't blur the input before we insert -->
		<button
			type="button"
			tabindex="-1"
			onmousedown={(e) => {
				e.preventDefault();
				oninsert(c);
			}}>{c}</button
		>
	{/each}
</div>
