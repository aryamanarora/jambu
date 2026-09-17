<script lang="ts">
	import { changeInfo, changeLabel } from '$lib/soundChange';
	import type { AlignSeg } from '$lib/query';
	let { segment, insertion = false }: { segment: AlignSeg; insertion?: boolean } = $props();
</script>

<span class="seg {changeInfo(segment.change).cls}" class:ins={insertion && segment.change !== 'loss'}
	title={changeLabel(segment.etymonSeg, segment.change === 'loss' ? '' : segment.reflexSeg, segment.change)}
	>{segment.change === 'loss' ? '·' : segment.reflexSeg}</span>

<style>
	.seg {
		display: inline-block;
		font-family: var(--font-phon);
		font-size: 1.06rem;
		line-height: 1;
		min-width: 0.9em;
		padding: 4px 7px;
		border-radius: 6px;
		vertical-align: middle;
	}
	:global(.seg) + .seg {
		margin-left: 3px;
	}
	.seg.change {
		color: #a85713;
		background: rgba(181, 100, 26, 0.16);
	}
	.seg.loss {
		color: var(--faint);
		padding: 4px 5px;
	}
	.seg.add,
	.seg.ins {
		color: #2563a8;
		background: rgba(46, 111, 181, 0.16);
		font-size: 0.86em;
		padding: 3px 5px;
	}
	:global(:root[data-theme='dark']) .seg.change,
	:global(:root:not([data-theme='light'])) .seg.change {
		color: #e0a35a;
	}
	:global(:root[data-theme='dark']) .seg.add,
	:global(:root[data-theme='dark']) .seg.ins,
	:global(:root:not([data-theme='light'])) .seg.add,
	:global(:root:not([data-theme='light'])) .seg.ins {
		color: #7fb0e0;
	}
</style>
