<script lang="ts">
	import { base } from '$app/paths';
	import GeoMap from '$lib/components/Map.svelte';
	import EntriesView from '$lib/components/EntriesView.svelte';
	import { cladeColor } from '$lib/clades';
	import { etymonSlotColor, ETYMON_PALETTE } from '$lib/etyma';
	import type { MapMarker } from '$lib/types';
	import type { ConceptDetail, ConceptAttestation } from '$lib/types';

	let { data } = $props();
	const detail = $derived(data as ConceptDetail);
	const concept = $derived(detail.concept);
	const etyma = $derived(detail.etyma);
	const unetym = $derived(detail.unetym);

	const NEUTRAL = '#9a958c';

	// legend entries in db order (form count desc — the same rank that colours the index-page
	// bars), each with its slot colour and number of attesting languages
	const legend = $derived(
		etyma.map((e, i) => ({
			etymon: e.etymon,
			word: e.word,
			gloss: e.gloss,
			source: e.source,
			color: etymonSlotColor(i),
			langs: e.languages.length
		}))
	);
	const wordOf = $derived(new Map(legend.map((l) => [l.etymon, l.word])));

	// etyma highlighted on the map: pinned (clicked) plus a transient hover/focus preview
	const DEFAULT_PINS = 4; // the leading etyma, pinned on load so the map opens on a real contrast
	let pinned = $state<string[]>([]);
	let pinnedFor = $state<number | null>(null);
	let hovered = $state<string | null>(null);

	// Reset to the default selection whenever the concept changes — this component is reused
	// across concept navigations, so carrying pinned ids over would dim the whole next map.
	$effect(() => {
		if (pinnedFor !== concept.id) {
			pinnedFor = concept.id;
			pinned = legend.slice(0, DEFAULT_PINS).map((l) => l.etymon);
		}
	});
	const active = $derived(hovered && !pinned.includes(hovered) ? [...pinned, hovered] : pinned);
	function toggle(etymon: string) {
		pinned = pinned.includes(etymon) ? pinned.filter((e) => e !== etymon) : [...pinned, etymon];
	}

	// Rank colours cycle every 8 slots, so two highlighted etyma far apart in rank can collide.
	// Give each active etymon its rank colour when free, else the next unused slot — chips read
	// from this too, so the legend and the map never disagree about what a colour means.
	const activeColor = $derived.by(() => {
		const used = new Set<string>();
		const out = new Map<string, string>();
		for (const e of active) {
			const rank = legend.findIndex((l) => l.etymon === e);
			if (rank < 0) continue;
			let c = etymonSlotColor(rank);
			if (used.has(c)) c = ETYMON_PALETTE.find((p) => !used.has(p)) ?? c;
			used.add(c);
			out.set(e, c);
		}
		return out;
	});
	const chipColor = (etymon: string, fallback: string) => activeColor.get(etymon) ?? fallback;

	// a language attesting 2+ highlighted etyma gets a marker split between their colours
	function pieSvg(colors: string[]): string {
		const c = 8;
		const r = 6.2;
		const pt = (i: number) => {
			const a = -Math.PI / 2 + (2 * Math.PI * i) / colors.length;
			return `${(c + r * Math.cos(a)).toFixed(2)} ${(c + r * Math.sin(a)).toFixed(2)}`;
		};
		const wedges = colors
			.map(
				(col, i) =>
					`<path d="M${c} ${c} L${pt(i)} A${r} ${r} 0 0 1 ${pt(i + 1)} Z" fill="${col}"/>`
			)
			.join('');
		return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">${wedges}<circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#ffffff" stroke-width="1.8"/></svg>`;
	}

	// one uniform-size marker per attesting place — a dialect point where the form is tagged with a
	// located dialect, else the language's own point. With nothing highlighted the map shows plain
	// coverage; highlighting an etymon recolours its places (ring) and dims the rest.
	const markers = $derived.by((): MapMarker[] => {
		const byPlace = new Map<
			string,
			{ name: string; lat: number; long: number; counts: Map<string, number> }
		>();
		const bump = (f: ConceptAttestation, etymon: string | null) => {
			for (const p of f.places) {
				let m = byPlace.get(p.key);
				if (!m)
					byPlace.set(p.key, (m = { name: p.name, lat: p.lat, long: p.long, counts: new Map() }));
				if (etymon) m.counts.set(etymon, (m.counts.get(etymon) ?? 0) + 1);
			}
		};
		for (const e of etyma) for (const f of e.forms) bump(f, e.etymon);
		for (const f of unetym) bump(f, null);
		return [...byPlace.values()].map((m) => {
			const breakdown = [...m.counts.entries()]
				.sort((a, b) => b[1] - a[1])
				.map(([e, n]) => `${wordOf.get(e) ?? e}×${n}`)
				.join(', ');
			const base = {
				lat: m.lat,
				long: m.long,
				svg: '',
				tooltip: `${m.name} — ${breakdown || 'unetymologised'}`
			};
			const matches = active.filter((e) => m.counts.has(e)).map((e) => activeColor.get(e)!);
			if (!active.length) return { ...base, color: NEUTRAL };
			if (!matches.length) return { ...base, color: NEUTRAL, dim: true };
			if (matches.length === 1) return { ...base, color: matches[0], ring: true };
			return { ...base, svg: pieSvg(matches) };
		});
	});

</script>

<svelte:head>
	<title>{concept.name} — Concepts — Jambu</title>
	<meta
		name="description"
		content="Etyma across {concept.lang_count} languages expressing the concept {concept.name} in Jambu."
	/>
</svelte:head>

<nav class="crumbs"><a href="{base}/concepts">Concepts</a> / {concept.name}</nav>
<h1 class="headword">
	{concept.name} <span class="cat">{concept.category}</span>
</h1>

<dl class="stats card">
	<div><dt>Etyma</dt><dd>{concept.etyma_count.toLocaleString()}</dd></div>
	<div><dt>Languages</dt><dd>{concept.lang_count.toLocaleString()}</dd></div>
	<div><dt>Forms</dt><dd>{concept.form_count.toLocaleString()}</dd></div>
	<div><dt>Unetymologised</dt><dd>{concept.unetym_count.toLocaleString()}</dd></div>
</dl>

{#if markers.length}
	<section class="map-section">
		<div class="legend-head">
			<h2>Geographic distribution</h2>
			{#if pinned.length}
				<button class="clear" onclick={() => (pinned = [])}>clear {pinned.length} pinned ×</button>
			{/if}
		</div>
		{#if legend.length}
			<p class="muted small">
				Hover an etymon to preview where it is used for this concept; click to pin it, and pin
				several to compare. Points are dialects where a form is tagged with one, else the language;
				a point on more than one pinned etymon gets a split marker.
			</p>
			<div class="legend" role="group" aria-label="Highlight etyma on the map">
				{#each legend as l (l.etymon)}
					<button
						class="chip"
						class:pinned={pinned.includes(l.etymon)}
						style="--c: {chipColor(l.etymon, l.color)}"
						aria-pressed={pinned.includes(l.etymon)}
						title="{l.source} {l.etymon}{l.gloss ? ` — ${l.gloss}` : ''}"
						onmouseenter={() => (hovered = l.etymon)}
						onmouseleave={() => (hovered = null)}
						onfocus={() => (hovered = l.etymon)}
						onblur={() => (hovered = null)}
						onclick={() => toggle(l.etymon)}
					>
						<span class="dot"></span>
						<span class="chip-word">{l.word}</span>
						<span class="chip-count">{l.langs}</span>
					</button>
				{/each}
			</div>
		{/if}
		<GeoMap {markers} zoom={4} height="360px" fitOnce />
	</section>
{/if}

<section>
	<h2>Etyma ({etyma.length})</h2>
	<p class="muted small">
		Entries expressing this concept across the languages of Jambu — click a row to expand its reflexes.
	</p>
	<EntriesView concept={String(concept.id)} expandable />
</section>

{#if unetym.length}
	<section>
		<h2>Unetymologised attestations ({unetym.length})</h2>
		<p class="muted small">Attested forms with this meaning that aren't (yet) linked to an etymon.</p>
		<div class="table-wrap">
			<table class="data">
				<tbody>
					{#each unetym as f (f.form_id)}
						<tr>
							<td class="rlang" style="border-left-color: {cladeColor(f.clade)}">{f.language ?? '—'}</td>
							<td class="rword">{f.word}</td>
							<td class="rgloss muted">{f.gloss}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</section>
{/if}

<style>
	.crumbs {
		font-size: 0.85rem;
		color: var(--muted);
		margin-bottom: 0.4rem;
	}
	.cat {
		font-size: 0.8rem;
		color: var(--muted);
		font-weight: 400;
		border: 1px solid var(--border);
		border-radius: 999px;
		padding: 0.1rem 0.6rem;
		vertical-align: middle;
	}
	.stats {
		display: flex;
		gap: 2rem;
		flex-wrap: wrap;
		padding: 0.8rem 1.2rem;
		margin: 1rem 0;
	}
	.stats dt {
		color: var(--muted);
		font-size: 0.8rem;
	}
	.stats dd {
		margin: 0;
		font-size: 1.3rem;
		font-weight: 600;
		font-variant-numeric: tabular-nums;
	}
	.map-section,
	section {
		margin: 1.6rem 0;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem;
		max-height: 7.6rem;
		overflow-y: auto;
		margin: 0.5rem 0 0.65rem;
	}
	.chip {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.15rem 0.6rem;
		border: 1px solid var(--border);
		border-radius: 999px;
		background: none;
		font: inherit;
		font-size: 0.82rem;
		color: inherit;
		cursor: pointer;
	}
	.chip:hover {
		border-color: var(--c);
	}
	.chip.pinned {
		border-color: var(--c);
		background: color-mix(in srgb, var(--c) 16%, transparent);
	}
	.chip .dot {
		width: 0.6rem;
		height: 0.6rem;
		border-radius: 50%;
		background: var(--c);
		flex: none;
	}
	.chip-word {
		font-family: 'Gentium', serif;
	}
	.chip-count {
		color: var(--muted);
		font-size: 0.75rem;
		font-variant-numeric: tabular-nums;
	}
	.legend-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
	}
	.clear {
		flex: none;
		padding: 0.15rem 0.6rem;
		border: 1px solid var(--border);
		border-radius: 999px;
		background: none;
		font: inherit;
		font-size: 0.78rem;
		color: var(--muted);
		white-space: nowrap;
		cursor: pointer;
	}
	.table-wrap {
		overflow-x: auto;
	}
	.rlang {
		border-left: 3px solid #ccc;
		font-weight: 500;
		white-space: nowrap;
	}
	.rword {
		font-family: 'Gentium', serif;
	}
	.small {
		font-size: 0.85rem;
	}
</style>
