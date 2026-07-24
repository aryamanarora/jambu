<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getIsoglossData,
		getIsoglossSoundChangeData,
		getAllLanguages,
		couplingModel,
		spectralEmbedding,
		conditionalOdds,
		type IsoglossData,
		type SoundAgreement
	} from '$lib/query';
	import { cladeColor, CLADE_ORDER } from '$lib/clades';
	import type { Language, MapMarker } from '$lib/types';
	import MapView from '$lib/components/Map.svelte';

	const FAMILIES = [
		{ id: 'Indo-Aryan', name: 'Indo-Aryan' },
		{ id: 'PNur', name: 'Nuristani' },
		{ id: 'PDr', name: 'Dravidian' },
		{ id: 'PMu', name: 'Munda' }
	];
	const LANG_CAP = 200;
	const HIST_CLADES = new Set(['OIA', 'MIA']);
	// rhombus marker for historical units; Map.svelte recolours the polygon fill to the point colour
	const RHOMBUS =
		'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><polygon points="8,0.5 15.5,8 8,15.5 0.5,8" fill="#000" stroke="rgba(0,0,0,0.55)" stroke-width="1"/></svg>';
	const JITTER = 0.35; // degrees of stable positional jitter to separate co-located points

	let family = $state('Indo-Aryan');
	let mode = $state<'clade' | 'lang'>('clade');
	let couplingBy = $state<'reflex' | 'sound'>('reflex'); // couple by shared reflexes vs shared sound changes
	let includeHistorical = $state(true);
	let minLemmas = $state(150);
	let selected = $state<string | null>(null);

	let data = $state<IsoglossData | null>(null);
	let coords = $state<Map<string, [number, number]> | null>(null); // langId → [lat, long]
	let loading = $state(true);

	// Presence-invariant sound-change agreement for the active (family, level). It's a heavy join over
	// the alignment layer, so fetch lazily the first time it's needed and cache per (family, level).
	let scCache = $state<Record<string, SoundAgreement>>({});
	let scLoading = $state(false);
	const scKey = $derived(`${family}:${mode}`);
	const scData = $derived(couplingBy === 'sound' ? (scCache[scKey] ?? null) : null);
	$effect(() => {
		if (couplingBy === 'sound' && !scCache[scKey] && !scLoading) {
			const [f, m, key] = [family, mode, scKey];
			scLoading = true;
			getIsoglossSoundChangeData(f, m)
				.then((d) => (scCache = { ...scCache, [key]: d }))
				.finally(() => (scLoading = false));
		}
	});

	const MIN_SHARED = 4; // ignore pairs attested together at fewer than this many proto-slots
	// agreement matrix over `items`: sim[i][j] = same-change rate where both are attested (else 0)
	function agreementMatrix(agg: SoundAgreement, items: string[]): number[][] {
		return items.map((a, i) =>
			items.map((b, j) => {
				if (i === j) return 1;
				const p = agg.pair.get(a < b ? `${a}|${b}` : `${b}|${a}`);
				return p && p.both >= MIN_SHARED ? p.agree / p.both : 0;
			})
		);
	}
	const sharedSlots = (a: string, b: string) =>
		scData?.pair.get(a < b ? `${a}|${b}` : `${b}|${a}`)?.both ?? 0;

	const isHistClade = (c: string) => HIST_CLADES.has(c);
	const isHistLang = (id: string) =>
		!!data && (HIST_CLADES.has(data.langClade[id]) || (data.langName[id] ?? '').startsWith('Old '));

	// ---- clade model -----------------------------------------------------------
	// items + reflex sets always come from the reflex incidence; the coupling is either the reflex
	// co-occurrence (Ising) or the presence-invariant sound-change agreement matrix.
	const cladeSetsF = $derived(
		!data
			? []
			: includeHistorical
				? data.cladeSets
				: data.cladeSets.map((s) => s.filter((c) => !isHistClade(c))).filter((s) => s.length)
	);
	const cladeItems = $derived(
		[...new Set(cladeSetsF.flat())].sort((a, b) => CLADE_ORDER.indexOf(a) - CLADE_ORDER.indexOf(b))
	);
	const cladeCoupling = $derived.by(() => {
		if (cladeItems.length < 2) return [];
		if (couplingBy === 'sound') return scData ? agreementMatrix(scData, cladeItems) : [];
		return couplingModel(cladeSetsF, cladeItems);
	});

	// ---- language model --------------------------------------------------------
	const maxCount = $derived(data ? Math.max(1, ...data.langCount.map(([, c]) => c)) : 1);
	const langModel = $derived.by(() => {
		if (!data)
			return { items: [] as string[], coupling: [] as number[][], sets: [] as string[][], total: 0 };
		const passing = data.langCount
			.filter(([id, c]) => c >= minLemmas && (includeHistorical || !isHistLang(id)))
			.sort((a, b) => b[1] - a[1]);
		const items = passing.slice(0, LANG_CAP).map(([id]) => id);
		const setsF = includeHistorical
			? data.langSets
			: data.langSets.map((s) => s.filter((id) => !isHistLang(id)));
		const coupling =
			items.length < 2
				? []
				: couplingBy === 'sound'
					? scData
						? agreementMatrix(scData, items)
						: []
					: couplingModel(setsF, items);
		return { items, coupling, sets: setsF, total: passing.length };
	});

	// ---- active model (whichever mode is selected) -----------------------------
	interface Active {
		items: string[];
		coupling: number[][];
		sets: string[][];
		label: (it: string) => string;
		cladeOf: (it: string) => string;
		coord: (it: string) => [number, number] | null;
		isHist: (it: string) => boolean;
	}
	const active = $derived.by<Active>(() => {
		if (mode === 'clade') {
			return {
				items: cladeItems,
				coupling: cladeCoupling,
				sets: cladeSetsF,
				label: (c) => c,
				cladeOf: (c) => c,
				coord: (c) => cladeCentroid.get(c) ?? null,
				isHist: (c) => isHistClade(c)
			};
		}
		return {
			items: langModel.items,
			coupling: langModel.coupling,
			sets: langModel.sets,
			label: (id) => data?.langName[id] ?? id,
			cladeOf: (id) => data?.langClade[id] ?? 'Other',
			coord: (id) => coords?.get(id) ?? null,
			isHist: (id) => isHistLang(id)
		};
	});

	// stable per-item positional jitter (hash → offset), so co-located points fan out without
	// wiggling on every recolour
	function jitter(id: string): [number, number] {
		let h = 2166136261;
		for (let i = 0; i < id.length; i++) {
			h ^= id.charCodeAt(i);
			h = Math.imul(h, 16777619);
		}
		const a = ((h >>> 0) % 10000) / 10000;
		const b = (((h >>> 13) >>> 0) % 10000) / 10000;
		return [(a - 0.5) * 2 * JITTER, (b - 0.5) * 2 * JITTER];
	}

	// clade centroid = mean lat/long of the family's member languages of that clade
	const cladeCentroid = $derived.by(() => {
		const m = new Map<string, [number, number]>();
		if (!data || !coords) return m;
		const acc = new Map<string, [number, number, number]>(); // clade → [sumLat, sumLong, n]
		for (const id of Object.keys(data.langClade)) {
			const c = data.langClade[id];
			const xy = coords.get(id);
			if (!xy) continue;
			const a = acc.get(c) ?? [0, 0, 0];
			a[0] += xy[0];
			a[1] += xy[1];
			a[2] += 1;
			acc.set(c, a);
		}
		for (const [c, [sl, sn, n]] of acc) if (n) m.set(c, [sl / n, sn / n]);
		return m;
	});

	const selIdx = $derived(selected ? active.items.indexOf(selected) : -1);

	// ---- colours ---------------------------------------------------------------
	// default: first 3 principal components of the affinity matrix → RGB
	const pcaColors = $derived.by(() => {
		const emb = spectralEmbedding(active.coupling, 3);
		const out = new Map<string, string>();
		if (!emb.length) return out;
		const lo = [Infinity, Infinity, Infinity];
		const hi = [-Infinity, -Infinity, -Infinity];
		for (const v of emb)
			for (let d = 0; d < 3; d++) {
				if (v[d] < lo[d]) lo[d] = v[d];
				if (v[d] > hi[d]) hi[d] = v[d];
			}
		const chan = (v: number[], d: number) => {
			const t = hi[d] > lo[d] ? (v[d] - lo[d]) / (hi[d] - lo[d]) : 0.5;
			return Math.round(55 + t * 180); // 55..235, avoid pure black/white
		};
		active.items.forEach((it, i) => {
			const v = emb[i];
			out.set(it, `rgb(${chan(v, 0)}, ${chan(v, 1)}, ${chan(v, 2)})`);
		});
		return out;
	});

	// diverging colour for affinity to the selected point (warm = share, cool = avoid); `t` is a
	// pre-normalised value in [-1, 1] (we feed it tanh(J) of the Ising coupling)
	function affinityColor(t: number): string {
		t = Math.max(-1, Math.min(1, t));
		const mix = (a: number[], b: number[], f: number) =>
			`rgb(${a.map((x, i) => Math.round(x + (b[i] - x) * f)).join(', ')})`;
		const neutral = [236, 230, 222];
		const warm = [138, 58, 134]; // plum
		const cool = [59, 110, 165]; // blue
		return t >= 0 ? mix(neutral, warm, t) : mix(neutral, cool, -t);
	}

	// ---- markers ---------------------------------------------------------------
	const markers = $derived.by<MapMarker[]>(() => {
		const out: MapMarker[] = [];
		active.items.forEach((it, i) => {
			const xy = active.coord(it);
			if (!xy) return;
			const isSel = it === selected;
			const v = selIdx >= 0 && !isSel ? (selAffinity[i] ?? 0) : 0;
			// map affinity to [-1,1] for the diverging colour: tanh(J) for reflex, 2·rate−1 for sound
			const t = couplingBy === 'sound' ? 2 * v - 1 : Math.tanh(v);
			const color =
				selIdx < 0 ? (pcaColors.get(it) ?? '#888') : isSel ? '#ffffff' : affinityColor(t);
			const [dlat, dlong] = jitter(it);
			out.push({
				lat: xy[0] + dlat,
				long: xy[1] + dlong,
				svg: active.isHist(it) ? RHOMBUS : '',
				color,
				radius: mode === 'clade' ? 9 : 6,
				ring: isSel,
				tooltip:
					selIdx >= 0 && !isSel
						? couplingBy === 'sound'
							? `${active.label(it)} · ${(v * 100).toFixed(0)}% shared change`
							: `${active.label(it)} · J ${v >= 0 ? '+' : ''}${v.toFixed(3)} · odds ${fmtOdds(Math.exp(v))}`
						: active.label(it),
				onClick: () => (selected = selected === it ? null : it)
			});
		});
		return out;
	});

	// ---- loading ---------------------------------------------------------------
	async function load(f: string) {
		loading = true;
		selected = null;
		const [d, langs] = await Promise.all([getIsoglossData(f), getAllLanguages()]);
		data = d;
		coords = new Map(
			langs
				.filter((l: Language) => l.lat != null && l.long != null)
				.map((l: Language) => [l.id, [l.lat, l.long] as [number, number]])
		);
		const counts = d.langCount.map(([, c]) => c).sort((a, b) => b - a);
		minLemmas = counts[Math.min(counts.length - 1, 40)] ?? 20;
		loading = false;
	}
	onMount(() => load(family));
	function pick(f: string) {
		if (f === family) return;
		family = f;
		load(f);
	}
	// clearing the selection when the model changes keeps the pin/affinity coherent
	function setMode(m: 'clade' | 'lang') {
		if (m === mode) return;
		mode = m;
		selected = null;
	}
	function setCoupling(c: 'reflex' | 'sound') {
		if (c === couplingBy) return;
		couplingBy = c;
		selected = null;
	}
	function toggleHist() {
		includeHistorical = !includeHistorical;
		selected = null;
	}

	const selClade = $derived(selected ? active.cladeOf(selected) : null);

	// conditional log-odds effect of every unit on the selected unit's presence (fit once per
	// selection): e^{bⱼ} is the multiplier on the odds of a shared reflex when j is present.
	// per-unit affinity to the selected unit. reflex: conditional log-odds J (fit once). sound: the
	// presence-invariant same-change agreement rate to the selected unit (row of the coupling matrix).
	const selAffinity = $derived.by(() => {
		if (selIdx < 0 || !selected) return [];
		if (couplingBy === 'sound') return active.coupling[selIdx] ?? [];
		return conditionalOdds(active.sets, active.items, selected);
	});

	// ranked affinity list for the selected unit. reflex: J = Ising log-odds, odds = e^J. sound:
	// agree = same-change rate, shared = # jointly-attested proto-slots (support).
	const affinityRanked = $derived.by(() => {
		if (selIdx < 0 || !selected) return [];
		const sel = selected;
		return active.items
			.map((it, i) => {
				const v = selAffinity[i] ?? 0;
				return {
					it,
					v,
					odds: Math.exp(v),
					shared: couplingBy === 'sound' ? sharedSlots(sel, it) : 0,
					label: active.label(it),
					clade: active.cladeOf(it)
				};
			})
			.filter((x) => x.it !== selected)
			.sort((a, b) => b.v - a.v);
	});

	// format an odds multiplier: ×2.43, ×0.412, or ≈×1 when negligible
	function fmtOdds(m: number): string {
		if (m >= 0.985 && m <= 1.015) return '≈×1';
		return '×' + (m >= 10 ? m.toFixed(1) : m.toFixed(m >= 1 ? 2 : 3));
	}
</script>

<svelte:head><title>Isoglosses — Jambu</title></svelte:head>

<h1>Isoglosses</h1>
<p class="muted">
	A pairwise maximum-entropy (Ising) model over which {mode === 'clade' ? 'clades' : 'languages'}
	reflect each etymon, mapped by their affinities — click a point to rank the rest.
</p>

<div class="controls">
	<div class="fam">
		{#each FAMILIES as f (f.id)}
			<button class:active={f.id === family} onclick={() => pick(f.id)}>{f.name}</button>
		{/each}
	</div>
	<div class="seg" role="group" aria-label="unit">
		<button class:active={mode === 'clade'} onclick={() => setMode('clade')}>Clades</button>
		<button class:active={mode === 'lang'} onclick={() => setMode('lang')}>Languages</button>
	</div>
	<div class="seg" role="group" aria-label="coupling">
		<button class:active={couplingBy === 'reflex'} onclick={() => setCoupling('reflex')}
			>Shared reflexes</button
		>
		<button class:active={couplingBy === 'sound'} onclick={() => setCoupling('sound')}
			>Shared sound changes</button
		>
	</div>
	<label class="hist">
		<input type="checkbox" checked={includeHistorical} onchange={toggleHist} />
		include historical (OIA/MIA, Old&nbsp;NIA)
	</label>
</div>

{#if mode === 'lang' && data}
	<div class="thresh">
		<label for="thr">min lemmas per language</label>
		<input id="thr" type="range" min="10" max={maxCount} step="10" bind:value={minLemmas} />
		<span class="thr-val">≥ {minLemmas.toLocaleString()}</span>
		<span class="thr-n">
			{langModel.items.length}
			{#if langModel.total > langModel.items.length}<span class="muted">of {langModel.total} (capped)</span>{/if}
			languages
		</span>
	</div>
{/if}

{#if loading}
	<p class="muted">Fitting the model…</p>
{:else if couplingBy === 'sound' && !scData}
	<p class="muted">Loading sound-change incidence (a heavier join over the alignment layer)…</p>
{:else if data}
	{#if active.items.length >= 2}
		<div class="layout">
			<div class="map-col">
				<MapView {markers} height="560px" fitOnce />
				<div class="statusbar">
					{#if selected}
						<span class="sel">
							<span class="dot" style="background: {cladeColor(selClade)}"></span>
							<b>{active.label(selected)}</b>
							<span class="muted">· others coloured by affinity</span>
						</span>
						<button class="clear" onclick={() => (selected = null)}>← back to PCA colours</button>
					{:else}
						<span class="muted">
							{active.items.length}
							{mode === 'clade' ? 'clades' : 'languages'} · coloured by the top-3 principal components ·
							click a point to see affinities
						</span>
					{/if}
				</div>
			</div>

			<aside class="side">
				{#if selected}
					<div class="side-head">
						<span class="dot" style="background: {cladeColor(selClade)}"></span>
						<b>{active.label(selected)}</b>
					</div>
					<p class="side-sub muted">
						{#if couplingBy === 'sound'}
							<b>agree</b> = how often the two apply the same change where both have the word
							(presence-invariant) · <b>shared</b> = # of those slots · click a row to pivot
						{:else}
							<b>J</b> = Ising coupling (log-odds) · <b>odds</b> = e<sup>J</sup> = ×multiplier on
							shared-reflex odds · click a row to pivot
						{/if}
					</p>
					<div class="table-wrap side-table">
						<table class="data accent-col">
							<thead>
								<tr>
									<th>{mode === 'clade' ? 'Clade' : 'Language'}</th>
									{#if couplingBy === 'sound'}
										<th class="num-col" title="same-change agreement rate over jointly-attested proto-slots">agree</th>
										<th class="num-col" title="number of proto-slots where both are attested (support)">shared</th>
									{:else}
										<th class="num-col" title="Ising coupling J — conditional log-odds between the two units' presence">J</th>
										<th class="num-col" title="e^J — multiplier on the odds of a shared reflex when this unit is present, all else fixed">odds</th>
									{/if}
								</tr>
							</thead>
							<tbody>
								{#each affinityRanked as r (r.it)}
									<tr onclick={() => (selected = r.it)}>
										<td class="lang-cell" style="border-left-color: {cladeColor(r.clade)}">
											{r.label}
											{#if mode === 'lang'}<span class="id-tag">{r.clade}</span>{/if}
										</td>
										{#if couplingBy === 'sound'}
											<td
												class="num-cell"
												style="color: {r.v > 0.5 ? 'var(--plum)' : r.v < 0.5 ? '#3b6ea5' : 'var(--muted)'}"
											>
												{(r.v * 100).toFixed(0)}%
											</td>
											<td class="num-cell odds-cell muted">{r.shared.toLocaleString()}</td>
										{:else}
											<td
												class="num-cell"
												style="color: {r.v > 0.02 ? 'var(--plum)' : r.v < -0.02 ? '#3b6ea5' : 'var(--muted)'}"
											>
												{r.v >= 0 ? '+' : ''}{r.v.toFixed(3)}
											</td>
											<td
												class="num-cell odds-cell"
												style="color: {r.odds > 1.03 ? 'var(--plum)' : r.odds < 0.97 ? '#3b6ea5' : 'var(--muted)'}"
											>
												{fmtOdds(r.odds)}
											</td>
										{/if}
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{:else}
					<div class="side-empty muted">
						<p>Click a {mode === 'clade' ? 'clade' : 'language'} on the map to rank the others by their affinity to it.</p>
					</div>
				{/if}
			</aside>
		</div>
	{:else}
		<p class="muted">
			Fewer than two {mode === 'clade' ? 'clades' : 'languages'} to show{mode === 'lang'
				? ' — lower the threshold'
				: ''}.
		</p>
	{/if}
{/if}

<style>
	h1 {
		margin-bottom: 0.3rem;
	}
	.controls {
		display: flex;
		gap: 0.7rem 1rem;
		margin: 1rem 0 0.7rem;
		flex-wrap: wrap;
		align-items: center;
	}
	.fam {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	.fam button {
		padding: 0.35rem 0.9rem;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		background: var(--surface);
		color: var(--ink);
		cursor: pointer;
		font-size: 0.92rem;
	}
	.fam button.active {
		background: var(--plum);
		color: var(--nav-fg);
		border-color: var(--plum);
	}
	.seg {
		display: inline-flex;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		overflow: hidden;
	}
	.seg button {
		padding: 0.35rem 0.95rem;
		border: none;
		background: var(--surface);
		color: var(--ink);
		cursor: pointer;
		font-size: 0.92rem;
	}
	.seg button + button {
		border-left: 1px solid var(--border-strong);
	}
	.seg button.active {
		background: var(--plum);
		color: var(--nav-fg);
	}
	.hist {
		font-size: 0.85rem;
		color: var(--muted);
		display: flex;
		align-items: center;
		gap: 0.3rem;
		cursor: pointer;
	}
	.hist input {
		accent-color: var(--plum);
	}
	.thresh {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		margin: 0 0 0.6rem;
		font-size: 0.88rem;
		flex-wrap: wrap;
	}
	.thresh label {
		color: var(--muted);
	}
	.thresh input[type='range'] {
		width: 16rem;
		accent-color: var(--plum);
	}
	.thr-val {
		font-variant-numeric: tabular-nums;
		font-weight: 600;
	}
	.layout {
		display: flex;
		gap: 1rem;
		align-items: flex-start;
	}
	.map-col {
		flex: 1 1 auto;
		min-width: 0;
	}
	.side {
		flex: 0 0 29rem;
		max-width: 29rem;
	}
	.side-head {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		font-size: 1rem;
	}
	.side-head .dot {
		width: 0.85rem;
		height: 0.85rem;
		border-radius: 50%;
		border: 1px solid rgba(0, 0, 0, 0.3);
	}
	.side-sub {
		margin: 0.15rem 0 0;
		font-size: 0.8rem;
	}
	.side-table {
		margin-top: 0.5rem;
		max-height: 520px;
		overflow-y: auto;
	}
	.side-table tbody tr {
		cursor: pointer;
	}
	.side-table .id-tag {
		margin-left: 0.35rem;
		font-size: 0.72rem;
		color: var(--muted);
	}
	.num-col {
		text-align: right;
		white-space: nowrap;
	}
	.num-cell {
		text-align: right;
		font-variant-numeric: tabular-nums;
		font-weight: 600;
		white-space: nowrap;
	}
	.odds-cell {
		font-size: 0.86rem;
	}
	.side-empty {
		border: 1px dashed var(--border-strong);
		border-radius: var(--radius, 8px);
		padding: 1rem;
		font-size: 0.88rem;
	}
	@media (max-width: 820px) {
		.layout {
			flex-direction: column;
		}
		.side {
			flex: 1 1 auto;
			max-width: none;
			width: 100%;
		}
	}
	.statusbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.8rem;
		flex-wrap: wrap;
		margin: 0.55rem 0;
		font-size: 0.9rem;
	}
	.sel {
		display: flex;
		align-items: center;
		gap: 0.45rem;
	}
	.sel .dot {
		width: 0.8rem;
		height: 0.8rem;
		border-radius: 50%;
		border: 1px solid rgba(0, 0, 0, 0.3);
	}
	.clear {
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		background: var(--surface);
		color: var(--ink);
		padding: 0.25rem 0.8rem;
		cursor: pointer;
		font-size: 0.85rem;
	}
	.clear:hover {
		background: var(--surface-2);
	}
</style>
