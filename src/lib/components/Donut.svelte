<script lang="ts">
	import { cladeColor } from '$lib/clades';
	import type { OriginSlice } from '$lib/query';
	import ReferenceLink from './ReferenceLink.svelte';
	import { referenceLabel } from '$lib/render';
	import Tooltip from './Tooltip.svelte';

	// A donut (pie with a hole) of a language's reflexes by the language of their origin, with a
	// legend. Rendered as pure SVG (stroke-dasharray arcs on a circle of circumference 100).
	let {
		slices,
		size = 168,
		label = 'Distribution of origin languages',
		unit = 'forms',
		selected = [],
		onselect
	}: {
		slices: OriginSlice[];
		size?: number;
		label?: string;
		unit?: string;
		selected?: string[];
		onselect?: (slices: OriginSlice[]) => void;
	} = $props();

	const OTHER = '#c3bcc9';
	const UNETYM = '#8a8276'; // warm grey for "origin unknown" (unetymologised), distinct from OTHER
	const R = 15.915; // 2πR ≈ 100, so a slice's dash length is its percentage

	// keep the biggest sources; fold the long tail into one "others" slice. The unetymologised slice
	// is pinned (never folded) and always drawn last, so it reads as its own "origin unknown" wedge.
	const grouped = $derived.by(() => {
		const unetym = slices.find((s) => s.lang === '__unetym');
		const sorted = slices.filter((s) => s.lang !== '__unetym').sort((a, b) => b.count - a.count);
		const top = sorted.slice(0, 8);
		const rest = sorted.slice(8);
		const withMembers = top.map((slice) => ({ ...slice, members: [slice] }));
		if (rest.length) {
			const count = rest.reduce((s, x) => s + x.count, 0);
			withMembers.push({ lang: '__other', name: `${rest.length} others`, clade: null, count, members: rest });
		}
		if (unetym) withMembers.push({ ...unetym, members: [unetym] });
		return withMembers;
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
				color:
					s.lang === '__other'
						? OTHER
						: s.lang === '__unetym'
							? UNETYM
							: (s.color ?? cladeColor(s.clade)),
				members: s.members,
				selected:
					selected.length === s.members.length &&
					s.members.every((member) => selected.includes(member.lang))
			};
			cum += pct;
			return a;
		});
	});

	function activate(a: (typeof arcs)[number]) {
		onselect?.(a.members);
	}

	// A slice that *is* one source carries its record, so the legend can show the standard pill
	// and its citation card instead of a bare string.
	const referenceOf = (a: (typeof arcs)[number]) =>
		a.members.length === 1 ? a.members[0].reference : undefined;
	/** What to call a slice out loud — a source goes by its citation label, not its short code. */
	function displayName(a: (typeof arcs)[number]): string {
		const ref = referenceOf(a);
		return ref
			? referenceLabel({ id: ref.id, short: ref.short ?? null, source: ref.source ?? null })
			: a.name;
	}

	// hover card for a wedge — the legend row it belongs to says the same thing, but the wedge is
	// what the pointer is usually over
	let hoverArc = $state<string | null>(null);
	let hoverEl = $state<HTMLElement | null>(null);
	let hideTimer: ReturnType<typeof setTimeout>;
	function showArc(name: string, event: MouseEvent | FocusEvent) {
		clearTimeout(hideTimer);
		hoverArc = name;
		hoverEl = event.currentTarget as HTMLElement;
	}
	function hideArc() {
		clearTimeout(hideTimer);
		hideTimer = setTimeout(() => (hoverArc = null), 80);
	}
	const hovered = $derived(arcs.find((a) => a.name === hoverArc) ?? null);

	function onArcKeydown(event: KeyboardEvent, a: (typeof arcs)[number]) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			activate(a);
		}
	}
</script>

{#if total}
	<div class="donut-wrap">
		<svg
			viewBox="0 0 36 36"
			width={size}
			height={size}
			class="donut"
			role="group"
			aria-label={label}
		>
			<circle cx="18" cy="18" r={R} fill="none" stroke="var(--border)" stroke-width="4" />
			{#each arcs as a (a.name)}
				<!-- SVG circles can act as buttons here; the adjacent legend exposes native buttons too. -->
				<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
				<circle
					class:interactive={!!onselect}
					class:selected={a.selected}
					cx="18"
					cy="18"
					r={R}
					fill="none"
					stroke={a.color}
					stroke-width="4"
					stroke-dasharray="{a.pct} {100 - a.pct}"
					stroke-dashoffset={a.offset}
					transform="rotate(-90 18 18)"
					role={onselect ? 'button' : undefined}
					tabindex={onselect ? 0 : undefined}
					aria-pressed={onselect ? a.selected : undefined}
					aria-label={onselect ? `Filter by ${displayName(a)}` : undefined}
					onmouseenter={(event) => showArc(a.name, event)}
					onmouseleave={hideArc}
					onfocus={(event) => showArc(a.name, event)}
					onblur={hideArc}
					onclick={() => activate(a)}
					onkeydown={(event) => onArcKeydown(event, a)}
				></circle>
			{/each}
			<text x="18" y="17.4" class="d-total">{total.toLocaleString()}</text>
			<text x="18" y="21.4" class="d-sub">{unit}</text>
		</svg>
		{#if hovered}
			<Tooltip anchor={hoverEl} prefer="above" interactive={false}>
				<span class="arc-card">
					<span class="arc-name"><span class="sw" style="background:{hovered.color}"></span>{displayName(hovered)}</span>
					<span class="arc-figures">
						{hovered.count.toLocaleString()}
						{unit} · {hovered.pct.toFixed(hovered.pct < 1 ? 1 : 0)}%
					</span>
					{#if onselect}<span class="arc-hint">{hovered.selected ? 'click to clear' : 'click to filter'}</span>{/if}
				</span>
			</Tooltip>
		{/if}
		<ul class="legend">
			{#each arcs as a (a.name)}
				<li class:selected={a.selected}>
					<button
						type="button"
						disabled={!onselect}
						aria-pressed={onselect ? a.selected : undefined}
						title={onselect ? `${a.selected ? 'Clear' : 'Apply'} ${displayName(a)} filter` : undefined}
						onclick={() => activate(a)}
					>
						<span class="sw" style="background:{a.color}"></span>
						{#if referenceOf(a)}
							<span class="nm"><ReferenceLink reference={referenceOf(a)!} as="text" /></span>
						{:else}
							<span class="nm">{a.name}</span>
						{/if}
						<span class="ct">{a.count.toLocaleString()} · {a.pct.toFixed(a.pct < 1 ? 1 : 0)}%</span>
					</button>
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
	.donut circle.interactive {
		cursor: pointer;
		transition: opacity 120ms ease, stroke-width 120ms ease;
	}
	.donut:has(circle.selected) circle.interactive:not(.selected) {
		opacity: 0.35;
	}
	.donut circle.interactive:hover,
	.donut circle.interactive:focus,
	.donut circle.selected {
		stroke-width: 5;
		outline: none;
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
		border-radius: var(--radius-sm);
	}
	.legend button {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		width: 100%;
		padding: 0.16rem 0.25rem;
		border: 0;
		border-radius: inherit;
		font: inherit;
		color: inherit;
		background: transparent;
		text-align: left;
		cursor: pointer;
	}
	.legend button:disabled {
		cursor: default;
	}
	.legend button:not(:disabled):hover,
	.legend button:not(:disabled):focus-visible,
	.legend li.selected button {
		background: color-mix(in srgb, var(--berry) 10%, transparent);
		outline: none;
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
		min-width: 0;
	}
	.arc-card {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
		font-family: var(--font-sans);
		font-size: 0.78rem;
		white-space: nowrap;
	}
	.arc-name {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		color: var(--ink);
		font-weight: 600;
	}
	.arc-figures { color: var(--muted); font-variant-numeric: tabular-nums; }
	.arc-hint {
		color: var(--faint);
		font-size: 0.66rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.ct {
		color: var(--muted);
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
	@media (max-width: 640px) {
		.donut-wrap {
			justify-content: center;
			gap: 1rem;
		}
		.legend {
			width: 100%;
			min-width: 0;
		}
		.legend button {
			min-width: 0;
		}
		.nm {
			min-width: 0;
			overflow-wrap: anywhere;
		}
	}
</style>
