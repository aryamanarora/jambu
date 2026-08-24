<script lang="ts">
	import { base } from '$app/paths';
	import GeoMap from '$lib/components/Map.svelte';
	import EntriesView from '$lib/components/EntriesView.svelte';
	import { cladeColor } from '$lib/clades';
	import { etymonSlotColor, ETYMON_PALETTE } from '$lib/etyma';
	import { safe, striptags } from '$lib/render';
	import type { MapMarker } from '$lib/types';
	import type { ConceptDetail, ConceptAttestation } from '$lib/types';
	import FormWord from '$lib/components/FormWord.svelte';

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
			ocr: e.ocr,
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
	const tooltipText = (value: string) =>
		striptags(value)
			.replaceAll('&', '&amp;')
			.replaceAll('<', '&lt;')
			.replaceAll('>', '&gt;')
			.replaceAll('"', '&quot;');

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
		return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">${wedges}<circle cx="${c}" cy="${c}" r="6.7" fill="none" stroke="rgba(48,35,47,.86)" stroke-width="1.7"/></svg>`;
	}

	// one uniform-size marker per attesting place — a dialect point where the form is tagged with a
	// located dialect, else the language's own point. With nothing highlighted the map shows plain
	// coverage; highlighting an etymon recolours its places (ring) and dims the rest.
	const markers = $derived.by((): MapMarker[] => {
		const byPlace = new Map<
			string,
			{
				name: string;
				lat: number;
				long: number;
				counts: Map<string, number>;
				forms: Map<string, ConceptAttestation[]>;
				unetym: ConceptAttestation[];
			}
		>();
		const bump = (f: ConceptAttestation, etymon: string | null) => {
			for (const p of f.places) {
				let m = byPlace.get(p.key);
				if (!m)
					byPlace.set(
						p.key,
						(m = {
							name: p.name,
							lat: p.lat,
							long: p.long,
							counts: new Map(),
							forms: new Map(),
							unetym: []
						})
					);
				if (etymon) {
					m.counts.set(etymon, (m.counts.get(etymon) ?? 0) + 1);
					const forms = m.forms.get(etymon) ?? [];
					forms.push(f);
					m.forms.set(etymon, forms);
				} else m.unetym.push(f);
			}
		};
		for (const e of etyma) for (const f of e.forms) bump(f, e.etymon);
		for (const f of unetym) bump(f, null);
		return [...byPlace.values()].map((m) => {
			const entries = [...m.counts.entries()].sort(
				(a, b) => Number(active.includes(b[0])) - Number(active.includes(a[0])) || b[1] - a[1]
			);
			const total = entries.reduce((sum, [, n]) => sum + n, 0) + m.unetym.length;
			const details = entries.slice(0, 6).map(([e, n]) => {
				const words = [...new Set((m.forms.get(e) ?? []).map((f) => tooltipText(f.word || f.form_id)))];
				const examples = words.slice(0, 3).join(', ');
				const rest = words.length > 3 ? `, +${words.length - 3} more` : '';
				return `<br><strong>${tooltipText(wordOf.get(e) ?? e)}</strong> (${n}): ${examples}${rest}`;
			});
			if (entries.length > 6) details.push(`<br>+${entries.length - 6} more etyma`);
			if (m.unetym.length) {
				const words = [...new Set(m.unetym.map((f) => tooltipText(f.word || f.form_id)))];
				details.push(
					`<br><strong>Unetymologised</strong> (${m.unetym.length}): ${words.slice(0, 3).join(', ')}${words.length > 3 ? `, +${words.length - 3} more` : ''}`
				);
			}
			const base = {
				lat: m.lat,
				long: m.long,
				svg: '',
				tooltip: `<strong>${tooltipText(m.name)}</strong><br>${total} ${total === 1 ? 'attestation' : 'attestations'} · ${entries.length} ${entries.length === 1 ? 'etymon' : 'etyma'}${details.join('')}`
			};
			const matches = active.filter((e) => m.counts.has(e)).map((e) => activeColor.get(e)!);
			if (!active.length) return { ...base, color: NEUTRAL, radius: 4 };
			if (!matches.length) return { ...base, color: NEUTRAL, radius: 2.5, dim: true };
			if (matches.length === 1)
				return { ...base, color: matches[0], radius: 5.5, ring: true, foreground: true };
			return { ...base, svg: pieSvg(matches), foreground: true };
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
						class:preview={hovered === l.etymon}
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
						<span class="chip-word"><FormWord word={l.word} ocr={l.ocr} /></span>
						<span class="chip-count">{l.langs}</span>
					</button>
				{/each}
			</div>
		{/if}
		<GeoMap {markers} zoom={4} height="min(68vh, 560px)" fitOnce mutedTiles />
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
							<td class="rlang" style="border-left-color: {cladeColor(f.clade)}">
								{#if f.language_id}
									<a href="{base}/languages/{f.language_id}">{f.language ?? '—'}</a>
								{:else}
									{f.language ?? '—'}
								{/if}
							</td>
							<td class="rword"><a href="{base}/reflexes/{f.form_id}"><FormWord word={f.word} ocr={f.ocr} /></a></td>
							<td class="rgloss muted">{@html safe(f.gloss) || '—'}</td>
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
		gap: 0.5rem;
		max-height: 10rem;
		overflow-y: auto;
		margin: 0.65rem 0 0.8rem;
		padding: 0.1rem 0.1rem 0.2rem;
		scrollbar-width: thin;
		scrollbar-color: var(--border-strong) transparent;
	}
	.chip {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		min-height: 2rem;
		padding: 0.25rem 0.65rem;
		border: 1.5px solid var(--border-strong);
		border-radius: 999px;
		background: color-mix(in srgb, var(--surface) 88%, transparent);
		font: inherit;
		font-size: 0.86rem;
		color: inherit;
		cursor: pointer;
		transition: border-color 120ms ease, background 120ms ease, transform 120ms ease;
	}
	.chip:hover,
	.chip.preview {
		border-color: var(--c);
		background: color-mix(in srgb, var(--c) 13%, var(--surface));
		transform: translateY(-1px);
	}
	.chip:focus-visible {
		outline: 2px solid var(--c);
		outline-offset: 2px;
	}
	.chip.pinned {
		border: 2px solid var(--c);
		padding: calc(0.25rem - 0.5px) calc(0.65rem - 0.5px);
		background: color-mix(in srgb, var(--c) 24%, var(--surface));
		box-shadow: 0 2px 8px color-mix(in srgb, var(--c) 24%, transparent);
	}
	.chip .dot {
		width: 0.72rem;
		height: 0.72rem;
		border-radius: 50%;
		background: var(--c);
		flex: none;
		box-shadow: 0 0 0 2px var(--surface), 0 0 0 3px var(--c);
	}
	.chip-word {
		font-family: var(--font-phon);
	}
	.chip-count {
		color: var(--muted);
		font-size: 0.75rem;
		font-variant-numeric: tabular-nums;
		padding: 0.05rem 0.35rem;
		border-radius: 999px;
		background: color-mix(in srgb, var(--surface-2) 78%, transparent);
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
	.clear:hover {
		border-color: var(--border-strong);
		background: var(--surface-2);
		color: var(--ink);
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
		font-family: var(--font-phon);
	}
	.small {
		font-size: 0.85rem;
	}
	@media (max-width: 640px) {
		.stats {
			display: grid;
			grid-template-columns: repeat(2, minmax(0, 1fr));
			gap: 0.8rem 1rem;
		}
		.chip,
		.clear {
			min-height: 40px;
		}
		.legend-head {
			align-items: flex-start;
		}
	}
</style>
