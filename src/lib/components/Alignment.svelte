<script lang="ts">
	// Etymon→reflex alignment shown as a two-row segment grid (like the entry page's alignment mode,
	// but for a single reflex): the etymon segments on top, the reflex's outcomes aligned beneath
	// them in the same columns, each coloured by its sound-change category. Insertions sit inline.
	import { alignmentGrid } from '$lib/alignmentGrid';
	import SegmentChip from './SegmentChip.svelte';
	import type { AlignSeg } from '$lib/query';

	let { segs }: { segs: AlignSeg[] } = $props();

	const etymon = $derived.by(() => {
		const m = new Map<number, string>();
		for (const s of segs) if (s.etymonIdx >= 0 && !m.has(s.etymonIdx)) m.set(s.etymonIdx, s.etymonSeg);
		return [...m.entries()].sort((a, b) => a[0] - b[0]).map(([idx, seg]) => ({ idx, seg }));
	});

	const grid = $derived(alignmentGrid(segs, etymon.map((column) => column.idx)));
</script>

{#if etymon.length}
	<div class="aln-grid">
		<table>
			<tbody>
				<tr class="ety-row">
					<th class="rl">etymon</th>
					{#each etymon as e (e.idx)}<td class="ety-cell phon">{e.seg}</td>{/each}
				</tr>
				<tr class="ref-row">
					<th class="rl">reflex</th>
					{#each grid.cells as cell, i (i)}
						<td class="ref-cell">
							{#if i === 0}{#each grid.lead as s (s.pos)}<SegmentChip segment={s} insertion />{/each}{/if}
							{#if cell.main}<SegmentChip segment={cell.main} />{/if}
							{#each cell.post as s (s.pos)}<SegmentChip segment={s} insertion />{/each}
						</td>
					{/each}
				</tr>
			</tbody>
		</table>
	</div>
{/if}

<style>
	.aln-grid {
		overflow-x: auto;
		margin-top: 0.6rem;
	}
	table {
		border-collapse: collapse;
	}
	.rl {
		font-family: var(--font-sans);
		font-size: 0.6rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--muted);
		text-align: right;
		padding-right: 0.6rem;
		font-weight: 600;
		white-space: nowrap;
	}
	.ety-cell {
		font-family: var(--font-phon);
		font-size: 1.06rem;
		color: var(--muted);
		text-align: center;
		padding: 2px 7px;
	}
	.ety-row td {
		border-bottom: 1px solid var(--border);
	}
	.ref-cell {
		text-align: center;
		padding: 4px 4px 0;
		white-space: nowrap;
	}
</style>
