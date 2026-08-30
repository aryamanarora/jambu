<script lang="ts">
	import Tooltip from '$lib/components/Tooltip.svelte';
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import {
		getProtoFamilies,
		getProtoSegments,
		getSegRows,
		type ProtoFamily,
		type ProtoSeg,
		type CorrCtx,
		type LangCtx
	} from '$lib/query';
	import { cladeRank, cladeFamily, protoFamily } from '$lib/cladeTree';
	import { cladeColor } from '$lib/clades';
	import { changeInfo } from '$lib/soundChange';
	import { cladeFavRank, langFavRank } from '$lib/prefs.svelte';
	import SegPicker from '$lib/components/SegPicker.svelte';
	import GeoMap from '$lib/components/Map.svelte';
	import AtlasShell from '$lib/components/AtlasShell.svelte';
	import PanelToggle from '$lib/components/PanelToggle.svelte';
	import { activePoint, highlightPoint, livePoint, mutedPoint, pieMarker } from '$lib/atlas';
	import { getAllLanguages, getSegLangRows } from '$lib/query';
	import type { Language, MapMarker } from '$lib/types';

	let families = $state<ProtoFamily[]>([]);
	let proto = $state('Indo-Aryan');
	let segments = $state<ProtoSeg[]>([]);
	let selectedSeg = $state<string | null>(null);
	let segRows = $state<CorrCtx[]>([]);
	let prev = $state<string | null>(null); // environment: preceding etymon segment
	let next = $state<string | null>(null); // following
	let loading = $state(true);
	let loadingSeg = $state(false);

	// ---- the atlas ----------------------------------------------------------
	let segLangRows = $state<LangCtx[]>([]); // every language's outcomes for the selected segment
	let places = $state(new Map<string, Language>());
	const DEFAULT_OBS = 10; // a pie drawn from two or three forms is a shape, not a mix
	let minObs = $state(DEFAULT_OBS);
	// The pie is this map's mark, and at the icon default a three-way mix is too small to read —
	// so the pies, and the plain dots that stand in for a one-outcome language, are drawn larger.
	const PIE = 22;
	const DOT = 8;
	const DOT_HOT = 11;
	let pinnedOut = $state<string[]>([]); // outcomes drawn; the rest stand down
	let hoverOut = $state<string | null>(null);
	let scopeOpen = $state(true);
	let listOpen = $state(true);
	let hoverTimer: ReturnType<typeof setTimeout>;
	function previewOut(seg: string | null) {
		clearTimeout(hoverTimer);
		hoverTimer = setTimeout(() => (hoverOut = seg), seg ? 70 : 0);
	}
	function toggleOut(seg: string) {
		pinnedOut = pinnedOut.includes(seg) ? pinnedOut.filter((o) => o !== seg) : [...pinnedOut, seg];
	}
	const activeOut = $derived(
		hoverOut && !pinnedOut.includes(hoverOut) ? [...pinnedOut, hoverOut] : pinnedOut
	);

	onMount(async () => {
		getAllLanguages().then((list: Language[]) => {
			places = new Map(list.filter((l) => l.lat != null && l.long != null).map((l) => [l.id, l]));
		});
		families = await getProtoFamilies();
		if (families.length && !families.find((f) => f.id === proto)) proto = families[0].id;
		await loadSegments();
		loading = false;
	});

	async function loadSegments() {
		segments = await getProtoSegments(proto);
		await selectSeg(segments[0]?.seg ?? null);
	}
	async function selectProto(p: string) {
		if (p === proto) return;
		proto = p;
		await loadSegments();
	}
	async function selectSeg(s: string | null) {
		selectedSeg = s;
		prev = null;
		next = null;
		expanded = new Set();
		if (!s) {
			segRows = [];
			segLangRows = [];
			return;
		}
		loadingSeg = true;
		pinnedOut = [];
		hoverOut = null;
		[segRows, segLangRows] = await Promise.all([getSegRows(proto, s), getSegLangRows(proto, s)]);
		// The gate counts instances, and a common segment outnumbers a rare one by orders of
		// magnitude — so a threshold carried over from the last segment would silently empty this
		// one. Each segment starts from the default, and a segment too thin for it starts open.
		const totals = new Map<string, number>();
		for (const r of segLangRows) totals.set(r.lang, (totals.get(r.lang) ?? 0) + r.n);
		minObs = Math.max(0, ...totals.values()) >= DEFAULT_OBS ? DEFAULT_OBS : 0;
		loadingSeg = false;
	}

	// ---- environment options + filtering -----------------------------------
	function aggBy(rows: CorrCtx[], key: (r: CorrCtx) => string): { seg: string; n: number }[] {
		const m = new Map<string, number>();
		for (const r of rows) m.set(key(r), (m.get(key(r)) ?? 0) + r.n);
		return [...m.entries()].map(([seg, n]) => ({ seg, n })).sort((a, b) => b.n - a.n);
	}
	const prevOptions = $derived(
		aggBy(next ? segRows.filter((r) => r.next === next) : segRows, (r) => r.prev)
	);
	const nextOptions = $derived(
		aggBy(prev ? segRows.filter((r) => r.prev === prev) : segRows, (r) => r.next)
	);
	const rows = $derived(
		segRows.filter((r) => (!prev || r.prev === prev) && (!next || r.next === next))
	);

	// ---- colours + clade roll-up -------------------------------------------
	const PALETTE = [
		'#3366CC', '#DC3912', '#FF9900', '#109618', '#990099',
		'#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395'
	];
	const outcomeColor = $derived.by(() => {
		const m = new Map<string, string>();
		const by = new Map<string, number>();
		for (const r of rows) by.set(r.reflexSeg || '∅', (by.get(r.reflexSeg || '∅') ?? 0) + r.n);
		let i = 0;
		for (const [seg] of [...by.entries()].sort((a, b) => b[1] - a[1]))
			m.set(seg, seg === '∅' ? '#8b8b8b' : PALETTE[i++ % PALETTE.length]);
		return m;
	});
	const color = (seg: string) => outcomeColor.get(seg || '∅') ?? '#8b8b8b';

	interface Outcome { reflexSeg: string; change: string; n: number; example: string; }
	interface Row { key: string; total: number; outcomes: Outcome[]; }
	function rollup<T extends CorrCtx>(rs: T[], keyOf: (r: T) => string): Map<string, Row> {
		const m = new Map<string, Map<string, Outcome>>();
		for (const r of rs) {
			const g = keyOf(r);
			if (!m.has(g)) m.set(g, new Map());
			const om = m.get(g)!;
			const k = r.reflexSeg + '|' + r.change;
			if (!om.has(k))
				om.set(k, { reflexSeg: r.reflexSeg, change: r.change, n: 0, example: r.example });
			om.get(k)!.n += r.n;
		}
		const out = new Map<string, Row>();
		for (const [g, om] of m) {
			const outcomes = [...om.values()].sort((a, b) => b.n - a.n);
			out.set(g, { key: g, total: outcomes.reduce((s, o) => s + o.n, 0), outcomes });
		}
		return out;
	}
	const byClade = $derived.by<Row[]>(() => {
		const fam = protoFamily(proto);
		return [...rollup(rows, (r) => r.clade).values()].sort((a, b) => {
			// pinned clades first (in the user's order)
			const fa = cladeFavRank(a.key);
			const fb = cladeFavRank(b.key);
			if (fa !== fb) return fa - fb;
			// then clades of the chosen etymon family (e.g. Dravidian clades under Proto-Dravidian)
			const ma = cladeFamily(a.key) === fam ? 0 : 1;
			const mb = cladeFamily(b.key) === fam ? 0 : 1;
			if (ma !== mb) return ma - mb;
			return cladeRank(a.key) - cladeRank(b.key);
		});
	});
	const totalN = $derived(rows.reduce((s, r) => s + r.n, 0));

	const cladeOfLang = $derived(new Map(segLangRows.map((r) => [r.lang, r.clade])));

	/** Every language's outcome mix for the current segment and environment, before the gate. */
	const langMix = $derived.by(() => {
		const kept = segLangRows.filter((r) => (!prev || r.prev === prev) && (!next || r.next === next));
		const names = new Map(kept.map((r) => [r.lang, r.langName]));
		return [...rollup(kept, (r) => r.lang).values()].map((row) => ({
			lang: row.key,
			name: names.get(row.key) ?? row.key,
			row
		}));
	});

	// The gate's scale: how many outcomes of this segment each language actually attests, biggest
	// first. A slider laid straight over those counts would spend most of its travel on the handful
	// of best-attested languages, so the track is one notch per language and the readout is the
	// count itself.
	const gateScale = $derived(langMix.map((l) => l.row.total).sort((a, b) => b - a));
	const gatePos = $derived(gateScale.filter((c) => c < minObs).length); // languages held back
	function setGate(pos: number) {
		minObs = gateScale[gateScale.length - 1 - pos] ?? 0;
	}

	const byLang = $derived(langMix.filter((l) => l.row.total >= minObs));

	/** The outcomes themselves, corpus-wide — the map's legend and its picker. */
	const outcomes = $derived.by(() => {
		const m = new Map<string, { seg: string; change: string; n: number; langs: Set<string> }>();
		for (const { lang, row } of byLang) {
			for (const o of row.outcomes) {
				const seg = o.reflexSeg || '∅';
				const cur = m.get(seg) ?? { seg, change: o.change, n: 0, langs: new Set<string>() };
				cur.n += o.n;
				cur.langs.add(lang);
				m.set(seg, cur);
			}
		}
		const all = [...m.values()].sort((a, b) => b.n - a.n);
		const sum = all.reduce((s, o) => s + o.n, 0) || 1;
		return all.map((o) => ({ ...o, pct: (o.n / sum) * 100 }));
	});
	const mappedLangs = $derived(byLang.filter((l) => places.has(l.lang)).length);

	// One point per language, split between its outcomes. A language rarely has just one, and a
	// majority colour would hide exactly the variation an atlas exists to show — so the wedges
	// carry the mix, in proportion. Picking an outcome narrows every pie to it.
	const markers = $derived.by((): MapMarker[] => {
		const out: MapMarker[] = [];
		for (const { lang, name, row } of byLang) {
			const place = places.get(lang);
			if (!place) continue;
			const shown = activeOut.length
				? row.outcomes.filter((o) => activeOut.includes(o.reflexSeg || '∅'))
				: row.outcomes;
			const lit = shown.length > 0;
			// Pinning closes the frame in on the languages that actually show those outcomes — the
			// isogloss is the thing you asked to see. Hovering must not move the map, so this reads
			// the pins alone, not the hover preview.
			const framed =
				pinnedOut.length > 0 &&
				row.outcomes.some((o) => pinnedOut.includes(o.reflexSeg || '∅'));
			const detail = row.outcomes
				.slice(0, 6)
				.map((o) => `<br>*${selectedSeg} → ${o.reflexSeg || '∅'} · ${o.n.toLocaleString()}`)
				.join('');
			const base = {
				lat: place.lat,
				long: place.long,
				tooltip: `<strong>${name}</strong> · ${row.total.toLocaleString()} instances${detail}`
			};
			if (!lit) {
				out.push({ ...base, svg: '', ...mutedPoint() });
			} else if (shown.length === 1) {
				const only = shown[0].reflexSeg || '∅';
				const hot = hoverOut === only;
				out.push({
					...base,
					svg: '',
					...(hot ? highlightPoint(color(only)) : livePoint(color(only))),
					radius: hot ? DOT_HOT : DOT,
					focus: framed
				});
			} else {
				out.push({
					...base,
					svg: pieMarker(shown.map((o) => ({ color: color(o.reflexSeg), n: o.n }))),
					size: PIE,
					foreground: true,
					focus: framed
				});
			}
		}
		return out;
	});

	// ---- branch expansion (per-language) -----------------------------------
	let expanded = $state<Set<string>>(new Set());
	function toggleClade(clade: string) {
		const set = new Set(expanded);
		if (set.has(clade)) set.delete(clade);
		else set.add(clade);
		expanded = set;
	}
	function langRows(clade: string): { lang: string; name: string; row: Row }[] {
		return byLang
			.filter((l) => l.row.outcomes.length && cladeOfLang.get(l.lang) === clade)
			.sort((a, b) => {
				const fa = langFavRank(a.lang);
				const fb = langFavRank(b.lang);
				if (fa !== fb) return fa - fb; // pinned languages first
				return b.row.total - a.row.total;
			});
	}

	// ---- hover popover (summary) + click-through to the reflex list --------
	interface Pop { el: HTMLElement; clade: string; o: Outcome; }
	let pop = $state<Pop | null>(null);
	let popTimer: ReturnType<typeof setTimeout>;
	function enterSeg(e: Event, clade: string, o: Outcome) {
		clearTimeout(popTimer);
		pop = { el: e.currentTarget as HTMLElement, clade, o };
	}
	function leaveSeg() {
		popTimer = setTimeout(() => (pop = null), 120);
	}
	/** URL of the reflex-list page for one correspondence cell. */
	function setHref(clade: string, o: Outcome, lang?: string): string {
		const p = new URLSearchParams({ p: proto, s: selectedSeg ?? '', r: o.reflexSeg, c: clade });
		if (lang) p.set('l', lang);
		if (prev) p.set('pv', prev);
		if (next) p.set('nx', next);
		return `${base}/correspondences/set?${p.toString()}`;
	}

	const envLabel = $derived(
		`*${selectedSeg ?? ''}${prev || next ? ` / ${prev ?? ''}_${next ?? ''}` : ''}`
	);
</script>

<svelte:head>
	<title>Sound Correspondences — Jambu</title>
	<meta
		name="description"
		content="Explore regular sound correspondences across South Asian languages, conditioned by phonological environment — how each reconstructed segment reflects in each branch."
	/>
</svelte:head>

{#snippet map()}
	{#if selectedSeg && !loadingSeg}
		<GeoMap {markers} zoom={4} height="100%" mutedTiles flush scrollZoom zoomPosition="bottomleft" />
	{/if}
{/snippet}

<!-- left: which sound, in which environment -->
{#snippet left()}
	<div class="crumb-head">
		<nav class="crumbs">Sound correspondences</nav>
		<PanelToggle open={scopeOpen} side="left" label="the segment panel" onclick={() => (scopeOpen = !scopeOpen)} />
	</div>
	<h1><span class="focus phon">{envLabel}</span></h1>
	{#if scopeOpen}
		<dl class="stats">
			<div><dt>Instances</dt><dd>{totalN.toLocaleString()}</dd></div>
			<div><dt>Languages</dt><dd>{mappedLangs.toLocaleString()}</dd></div>
			<div><dt>Outcomes</dt><dd>{outcomes.length.toLocaleString()}</dd></div>
		</dl>
		<div class="knobs">
			{#if families.length}
				<div class="toggle" role="tablist" aria-label="Proto-language">
					{#each families as f (f.id)}
						<button role="tab" aria-selected={proto === f.id} class:on={proto === f.id} onclick={() => selectProto(f.id)}>{f.name}</button>
					{/each}
				</div>
			{/if}
			<!-- the environment is the instrument: without it a map of one segment shows every
			     conditioned outcome at once and reads as noise -->
			<div class="builder">
				<SegPicker label="preceding" options={prevOptions} value={prev} onSelect={(v) => (prev = v)} />
				<span class="env-focus phon">_</span>
				<SegPicker label="following" options={nextOptions} value={next} onSelect={(v) => (next = v)} align="end" />
			</div>
			<div class="segbar">
				{#each segments as sg (sg.seg)}
					<button class="pseg" class:sel={selectedSeg === sg.seg} onclick={() => selectSeg(sg.seg)}>
						{sg.seg}<span class="cnt">{sg.total.toLocaleString()}</span>
					</button>
				{/each}
			</div>
			<!-- a pie split three ways out of four attestations is a shape, not a finding; the gate
			     holds the map to the languages that attest the segment often enough to read -->
			{#if gateScale.length > 1}
				<div class="thresh">
					<label for="minobs">min instances per language</label>
					<span class="thr-val">≥ {minObs.toLocaleString()}</span>
					<input
						id="minobs"
						type="range"
						min="0"
						max={gateScale.length - 1}
						step="1"
						value={gatePos}
						oninput={(e) => setGate(+e.currentTarget.value)}
					/>
					<span class="thr-note">
						{(gateScale.length - gatePos).toLocaleString()} of {gateScale.length.toLocaleString()} languages
					</span>
				</div>
			{/if}
		</div>
	{/if}
{/snippet}

<!-- right: the outcomes, as the map's legend and its picker -->
{#snippet right()}
	<div class="panel-head">
		<PanelToggle open={listOpen} side="right" label="the outcome panel" onclick={() => (listOpen = !listOpen)} />
		<h2>{outcomes.length.toLocaleString()} outcome{outcomes.length === 1 ? '' : 's'}</h2>
		{#if pinnedOut.length}
			<button class="clear" onclick={() => (pinnedOut = [])} title="Draw every outcome again">clear {pinnedOut.length}</button>
		{/if}
	</div>

	{#if listOpen}
		{#if loading || loadingSeg}
			<p class="empty">Loading the correspondence…</p>
		{:else if !outcomes.length}
			<p class="empty">Nothing attested for {envLabel}.</p>
		{:else}
			<p class="hint">
				Each point is a language, split between its outcomes in proportion. Pick an outcome to
				draw only where it happens.
			</p>
			<div class="list" role="group" aria-label="Outcomes of this segment">
				{#each outcomes as o (o.seg)}
					{@const info = changeInfo(o.change)}
					<div class="row" class:pinned={pinnedOut.includes(o.seg)} style="--c: {color(o.seg)}">
						<button
							class="pick"
							aria-pressed={pinnedOut.includes(o.seg)}
							onmouseenter={() => previewOut(o.seg)}
							onmouseleave={() => previewOut(null)}
							onfocus={() => previewOut(o.seg)}
							onblur={() => previewOut(null)}
							onclick={() => toggleOut(o.seg)}
						>
							<span class="dot"></span>
							<span class="word phon">{o.seg}</span>
							<span class="count">{o.pct.toFixed(o.pct < 1 ? 1 : 0)}%</span>
							<span class="meta">{info.name} · {o.langs.size} language{o.langs.size === 1 ? '' : 's'} · {o.n.toLocaleString()}</span>
						</button>
					</div>
				{/each}
			</div>

			<!-- the same distribution read by descent instead of by place; the map cannot show
			     proportion within a branch, and this cannot show contiguity -->
			<details class="branch-drawer">
				<summary>By branch<span>{byClade.length}</span></summary>
				{#each byClade as row (row.key)}
					<div class="brow">
						<button class="bname" onclick={() => toggleClade(row.key)} style="border-left-color:{cladeColor(row.key)}">
							{row.key}<span class="btot">{row.total.toLocaleString()}</span>
						</button>
						<div class="bar">
							{#each row.outcomes as o (o.reflexSeg + o.change)}
								<a
									class="seg"
									href={setHref(row.key, o)}
									style="width:{(o.n / row.total) * 100}%; background:{color(o.reflexSeg)}"
									onmouseenter={(e) => enterSeg(e, row.key, o)}
									onmouseleave={leaveSeg}
									aria-label="{o.reflexSeg || '∅'}: {o.n}"
								></a>
							{/each}
						</div>
						{#if expanded.has(row.key)}
							<ul class="blangs">
								{#each langRows(row.key) as l (l.lang)}
									<li>
										<span class="lname">{l.name}</span>
										<span class="bar small">
											{#each l.row.outcomes as o (o.reflexSeg + o.change)}
												<a
													class="seg"
													href={setHref(row.key, o, l.lang)}
													style="width:{(o.n / l.row.total) * 100}%; background:{color(o.reflexSeg)}"
													aria-label="{o.reflexSeg || '∅'}: {o.n}"
												></a>
											{/each}
										</span>
									</li>
								{/each}
							</ul>
						{/if}
					</div>
				{/each}
			</details>
		{/if}
	{/if}
{/snippet}

<AtlasShell {map} {left} {right} leftOpen={scopeOpen} rightOpen={listOpen} />

{#if pop}
	<Tooltip anchor={pop.el} prefer="above" interactive={false}>
		<span class="pop">
			<b class="phon">*{selectedSeg} → {pop.o.reflexSeg || '∅'}</b>
			<span class="pop-meta">{pop.clade} · {pop.o.n.toLocaleString()} · {changeInfo(pop.o.change).name}</span>
		</span>
	</Tooltip>
{/if}

<style>
	/* ---- the segment panel ---- */
	.focus.phon {
		display: block;
		font-family: var(--font-phon);
		font-size: clamp(1.5rem, 2.4vw, 2.1rem);
		font-weight: 700;
		line-height: 1.1;
	}
	.knobs { display: grid; gap: 0.6rem; padding: 0 0.95rem 0.85rem; }
	.builder {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.4rem;
	}
	.env-focus { color: var(--muted); font-size: 1.1rem; }
	/* 80-odd segments: a wrapped grid that scrolls rather than a wall */
	.segbar {
		display: flex;
		flex-wrap: wrap;
		gap: 0.2rem;
		max-height: 12rem;
		overflow-y: auto;
		padding-right: 0.2rem;
		scrollbar-width: thin;
		scrollbar-color: var(--border-strong) transparent;
	}

	.thresh {
		display: grid;
		grid-template-columns: 1fr auto;
		align-items: center;
		gap: 0.15rem 0.5rem;
		color: var(--muted);
		font-size: 0.72rem;
	}
	.thresh label { color: var(--muted); }
	.thresh input[type='range'] {
		grid-column: 1 / -1;
		width: 100%;
		accent-color: var(--plum);
	}
	.thr-val { color: var(--ink); font-variant-numeric: tabular-nums; font-weight: 600; }
	.thr-note { grid-column: 1 / -1; font-variant-numeric: tabular-nums; }

	/* the row grammar comes from atlas.css; only the second line is ours */
	.pick {
		grid-template-areas:
			'dot word count'
			'. meta meta';
	}
	.word.phon { font-family: var(--font-phon); font-size: 1rem; }
	.meta {
		grid-area: meta;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--muted);
		font-size: 0.72rem;
	}
	.count { font-variant-numeric: tabular-nums; }

	/* ---- the same distribution, read by descent ---- */
	.branch-drawer {
		margin: 0.6rem 0.6rem 0.8rem;
		border-top: 1px solid var(--border);
		padding-top: 0.5rem;
	}
	.branch-drawer > summary {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.5rem;
		color: var(--muted);
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		cursor: pointer;
	}
	.branch-drawer > summary span { font-weight: 400; letter-spacing: 0; }
	.brow { margin-top: 0.4rem; }
	.bname {
		display: flex;
		justify-content: space-between;
		gap: 0.5rem;
		width: 100%;
		padding: 0 0 0.15rem 0.4rem;
		border: 0;
		border-left: 3px solid var(--border);
		background: none;
		color: var(--ink);
		font: inherit;
		font-size: 0.76rem;
		text-align: left;
		cursor: pointer;
	}
	.bname:hover { color: var(--plum-2); }
	.btot { color: var(--muted); font-variant-numeric: tabular-nums; }
	.blangs { list-style: none; margin: 0.2rem 0 0.3rem; padding: 0 0 0 0.8rem; display: grid; gap: 0.15rem; }
	.blangs li { display: grid; grid-template-columns: minmax(4rem, 6.5rem) minmax(0, 1fr); gap: 0.4rem; align-items: center; }
	.lname { color: var(--muted); font-size: 0.7rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.pop { display: flex; flex-direction: column; gap: 0.15rem; font-family: var(--font-sans); font-size: 0.78rem; white-space: nowrap; }
	.pop-meta { color: var(--muted); }

	.toggle {
		display: inline-flex;
		flex-wrap: wrap;
		margin-top: 0.8rem;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		padding: 2px;
		background: var(--surface);
		gap: 2px;
	}
	.toggle button {
		font-family: var(--font-sans);
		font-size: 0.82rem;
		font-weight: 500;
		padding: 3px 14px;
		border: none;
		background: none;
		color: var(--muted);
		border-radius: 999px;
		cursor: pointer;
	}
	.toggle button.on {
		background: var(--plum);
		color: #fbeefb;
	}

	.segbar {
		display: flex;
		flex-wrap: wrap;
		gap: 5px;
		margin-top: 1rem;
	}
	.pseg {
		display: inline-flex;
		align-items: baseline;
		gap: 4px;
		font-family: var(--font-phon);
		font-size: 1.05rem;
		padding: 3px 9px;
		border: 1.5px solid var(--border-strong);
		border-radius: 7px;
		background: var(--surface);
		color: var(--ink);
		cursor: pointer;
	}
	.pseg:hover {
		border-color: var(--berry);
	}
	.pseg.sel {
		background: var(--berry);
		color: #fff;
		border-color: var(--berry);
	}
	.pseg .cnt {
		font-family: var(--font-sans);
		font-size: 0.66rem;
		opacity: 0.7;
	}

	/* environment builder */
	.builder {
		margin-top: 1.2rem;
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		gap: 0.4rem 1rem;
		align-items: center;
		padding: 0.7rem 0.9rem;
	}
	.focus {
		font-size: 1.35rem;
		font-weight: 600;
		text-align: center;
		white-space: nowrap;
		color: var(--berry);
	}

	.count {
		margin: 1.1rem 0 0.5rem;
		font-size: 0.85rem;
	}

	/* pushed to the cell's right edge so the totals read as a column of figures rather than
	   trailing each name at a different offset */
	.bar {
		display: flex;
		height: 16px;
		border-radius: 3px;
		overflow: hidden;
		background: var(--surface-2);
	}
	.bar.small {
		height: 11px;
	}
	.bar .seg {
		height: 100%;
		display: block;
		min-width: 2px;
	}
	.bar .seg:hover {
		filter: brightness(1.12) saturate(1.2);
		outline: 1px solid rgba(0, 0, 0, 0.25);
	}

	/* hover popover — the card itself is Tooltip.svelte; these are its contents */

	@media (max-width: 640px) {
		/* stack the environment builder: preceding ▸ *seg ▸ following */
		.builder {
			grid-template-columns: 1fr;
			justify-items: center;
			gap: 0.5rem;
		}
		.segbar {
			gap: 4px;
		}
		.pseg {
			font-size: 0.98rem;
			padding: 2px 7px;
			min-height: 42px;
		}
		.bar {
			height: 28px;
		}
		.bar.small {
			height: 22px;
		}
	}
</style>
