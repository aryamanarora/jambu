<script lang="ts">
	import { CLADE_ORDER, CLADE_COLORS } from '$lib/clades';

	// `clades` is the comma/substring-joined clade string on a Lemma (entry).
	let { clades = '', size = 'sm' }: { clades?: string; size?: 'sm' | 'lg' } = $props();

	// Membership test mirrors the template: substring match against the clades string.
	function has(clade: string): boolean {
		return !!clades && clades.includes(clade);
	}
</script>

<span class="clades" title="Clades with reflexes">
	{#each CLADE_ORDER as clade (clade)}
		<span
			class="clade-block {size === 'lg' ? 'lg' : ''}"
			title={clade}
			style={has(clade) ? `background:#${CLADE_COLORS[clade]}` : ''}
		></span>
	{/each}
</span>
