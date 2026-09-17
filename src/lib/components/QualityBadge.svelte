<script lang="ts">
	let { quality, inset = false }: { quality: string; inset?: boolean } = $props();
</script>

<span class="quality q{quality}" class:inset title="Source quality {quality}">{quality}</span>

<style>
	.quality { align-self: center; box-sizing: border-box; width: 1.15rem; border: 1px solid color-mix(in srgb, var(--plum-2) 40%, transparent); border-radius: 3px; color: var(--plum-2); font-size: 0.62rem; font-weight: 700; text-align: center; }
	.inset { margin-right: 0.35rem; }
	.qA { background: color-mix(in srgb, var(--plum-2) 26%, transparent); }
	.qB { background: color-mix(in srgb, var(--plum-2) 12%, transparent); }
	.qC { background: none; opacity: 0.75; }
</style>
