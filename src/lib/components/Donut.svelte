<script lang="ts">
	import { cladeColor } from '$lib/clades';
	import type { OriginSlice } from '$lib/query';

	// A donut (pie with a hole) of a language's reflexes by the language of their origin, with a
	// legend. Rendered as pure SVG (stroke-dasharray arcs on a circle of circumference 100).
	let { slices, size = 168 }: { slices: OriginSlice[]; size?: number } = $props();

	const OTHER = '#c3bcc9';
	const R = 15.915; // 2πR ≈ 100, so a slice's dash length is its percentage

	// keep the biggest sources; fold the long tail into one "others" slice
	const grouped = $derived.by(() => {
		const sorted = [...slices].sort((a, b) => b.count - a.count);
		const top = sorted.slice(0, 8);
		const rest = sorted.slice(8);
		if (rest.length) {
			const count = rest.reduce((s, x) => s + x.count, 0);
			top.push({ lang: '__other', name: `${rest.length} others`, clade: null, count });
		}
		return top;
	});
	const total = $derived(grouped.reduce((s, x) => s + x.count, 0));
	const arcs = $derived.by(() => {
		let cum = 0;
		return grouped.map((s) => {
			const pct = total ? (s.count / total) * 100 : 0;
			const a = {
				name: s.name,
				count: s.count,
				pct,
				offset: -cum,
				color: s.lang === '__other' ? OTHER : cladeColor(s.clade)
			};
			cum += pct;
			return a;
		});
	});
</script>

{#if total}
	<div class="donut-wrap">
		<svg
			viewBox="0 0 36 36"
			width={size}
			height={size}
			class="donut"
			role="img"
			aria-label="Distribution of origin languages"
		>
			<circle cx="18" cy="18" r={R} fill="none" stroke="var(--border)" stroke-width="4" />
			{#each arcs as a (a.name)}
				<circle
					cx="18"
					cy="18"
					r={R}
					fill="none"
					stroke={a.color}
					stroke-width="4"
					stroke-dasharray="{a.pct} {100 - a.pct}"
					stroke-dashoffset={a.offset}
					transform="rotate(-90 18 18)"><title>{a.name}: {a.count.toLocaleString()}</title></circle
				>
			{/each}
			<text x="18" y="17.4" class="d-total">{total.toLocaleString()}</text>
			<text x="18" y="21.4" class="d-sub">reflexes</text>
		</svg>
		<ul class="legend">
			{#each arcs as a (a.name)}
				<li>
					<span class="sw" style="background:{a.color}"></span>
					<span class="nm">{a.name}</span>
					<span class="ct">{a.count.toLocaleString()} · {a.pct.toFixed(a.pct < 1 ? 1 : 0)}%</span>
				</li>
			{/each}
		</ul>
	</div>
{/if}

<style>
	.donut-wrap {
		display: flex;
		align-items: center;
		gap: 1.4rem;
		flex-wrap: wrap;
	}
	.donut {
		flex: none;
	}
	.d-total {
		font-family: var(--font-sans);
		font-size: 5px;
		font-weight: 700;
		fill: var(--ink);
		text-anchor: middle;
	}
	.d-sub {
		font-family: var(--font-sans);
		font-size: 2.6px;
		fill: var(--muted);
		text-anchor: middle;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.legend {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		gap: 0.28rem;
		font-size: 0.86rem;
		min-width: 12rem;
	}
	.legend li {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
	}
	.sw {
		flex: none;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 2px;
		transform: translateY(1px);
	}
	.nm {
		flex: 1;
	}
	.ct {
		color: var(--muted);
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
</style>
