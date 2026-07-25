<script lang="ts">
	import { base } from '$app/paths';
	import GeoMap from '$lib/components/Map.svelte';
	import EntriesView from '$lib/components/EntriesView.svelte';
	import { cladeColor } from '$lib/clades';
	import type { MapMarker } from '$lib/types';
	import type { ConceptDetail, ConceptAttestation } from '$lib/types';

	let { data } = $props();
	const detail = $derived(data as ConceptDetail);
	const concept = $derived(detail.concept);
	const etyma = $derived(detail.etyma);
	const unetym = $derived(detail.unetym);

	// a distinct, stable colour per etymon (hash its id → hue) so the map reads like an isogloss:
	// each language is coloured by the etymon it predominantly uses for this concept.
	function etymonColor(etymon: string): string {
		let h = 0;
		for (let i = 0; i < etymon.length; i++) h = (h * 31 + etymon.charCodeAt(i)) >>> 0;
		return `hsl(${h % 360} 62% 55%)`;
	}

	// one map marker per attesting language, coloured by its dominant etymon (grey if only
	// unetymologised); radius scales with the number of attesting forms there.
	const markers = $derived.by(() => {
		const byLang = new Map<
			string,
			{ lat: number; long: number; total: number; counts: Map<string, number> }
		>();
		const bump = (f: ConceptAttestation, etymon: string | null) => {
			if (f.lat == null || f.long == null || !f.language) return;
			let m = byLang.get(f.language);
			if (!m) {
				m = { lat: f.lat, long: f.long, total: 0, counts: new Map() };
				byLang.set(f.language, m);
			}
			m.total += 1;
			if (etymon) m.counts.set(etymon, (m.counts.get(etymon) ?? 0) + 1);
		};
		for (const e of etyma) for (const f of e.forms) bump(f, e.etymon);
		for (const f of unetym) bump(f, null);
		return [...byLang.entries()].map(([name, m]) => {
			let dominant: string | null = null;
			let best = 0;
			for (const [e, n] of m.counts) if (n > best) ((best = n), (dominant = e));
			const breakdown = [...m.counts.entries()]
				.sort((a, b) => b[1] - a[1])
				.map(([e, n]) => `${e}×${n}`)
				.join(', ');
			return {
				lat: m.lat,
				long: m.long,
				svg: '',
				color: dominant ? etymonColor(dominant) : '#9a958c',
				radius: Math.min(11, 4 + Math.sqrt(m.total) * 1.6),
				tooltip: `${name}: ${breakdown || 'unetymologised'}`
			};
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
		<h2>Geographic distribution</h2>
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
