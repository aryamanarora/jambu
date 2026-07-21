<script lang="ts">
	// Etymon→reflex alignment shown as a two-row segment grid (like the entry page's alignment mode,
	// but for a single reflex): the etymon segments on top, the reflex's outcomes aligned beneath
	// them in the same columns, each coloured by its sound-change category. Insertions sit inline.
	import { changeInfo, changeLabel } from '$lib/soundChange';
	import type { AlignSeg } from '$lib/query';

	let { segs }: { segs: AlignSeg[] } = $props();

	const etymon = $derived.by(() => {
		const m = new Map<number, string>();
		for (const s of segs) if (s.etymonIdx >= 0 && !m.has(s.etymonIdx)) m.set(s.etymonIdx, s.etymonSeg);
		return [...m.entries()].sort((a, b) => a[0] - b[0]).map(([idx, seg]) => ({ idx, seg }));
	});

	interface Cell {
		main: AlignSeg | null;
		post: AlignSeg[];
	}
	const grid = $derived.by(() => {
		const colOf = new Map<number, number>();
		etymon.forEach((e, i) => colOf.set(e.idx, i));
		const cells: Cell[] = Array.from({ length: etymon.length }, () => ({ main: null, post: [] }));
		const lead: AlignSeg[] = [];
		let lastCol = -1;
		for (const s of segs) {
			const c = s.etymonIdx >= 0 ? colOf.get(s.etymonIdx) : undefined;
			if (c !== undefined) {
				cells[c].main = s;
				lastCol = c;
			} else if (lastCol >= 0) cells[lastCol].post.push(s);
			else lead.push(s);
		}
		return { cells, lead };
	});
</script>

{#snippet chip(s: AlignSeg, ins: boolean)}
	{#if s.change === 'loss'}
		<span class="seg loss" title={changeLabel(s.etymonSeg, '', s.change)}>·</span>
	{:else}
		<span
			class="seg {changeInfo(s.change).cls}"
			class:ins
			title={changeLabel(s.etymonSeg, s.reflexSeg, s.change)}>{s.reflexSeg}</span
		>
	{/if}
{/snippet}

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
							{#if i === 0}{#each grid.lead as s (s.pos)}{@render chip(s, true)}{/each}{/if}
							{#if cell.main}{@render chip(cell.main, false)}{/if}
							{#each cell.post as s (s.pos)}{@render chip(s, true)}{/each}
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
	.seg + .seg {
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
