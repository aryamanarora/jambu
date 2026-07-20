<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import {
		getProtoFamilies,
		getProtoSegments,
		getSegRows,
		getCladeLangRows,
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

	let families = $state<ProtoFamily[]>([]);
	let proto = $state('Indo-Aryan');
	let segments = $state<ProtoSeg[]>([]);
	let selectedSeg = $state<string | null>(null);
	let segRows = $state<CorrCtx[]>([]);
	let prev = $state<string | null>(null); // environment: preceding etymon segment
	let next = $state<string | null>(null); // following
	let loading = $state(true);
	let loadingSeg = $state(false);

	onMount(async () => {
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
		langRaw = new Map();
		if (!s) {
			segRows = [];
			return;
		}
		loadingSeg = true;
		segRows = await getSegRows(proto, s);
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

	// ---- branch expansion (per-language) -----------------------------------
	let expanded = $state<Set<string>>(new Set());
	let langRaw = $state<Map<string, LangCtx[]>>(new Map());
	async function toggleClade(clade: string) {
		const s = new Set(expanded);
		if (s.has(clade)) s.delete(clade);
		else {
			s.add(clade);
			if (!langRaw.has(clade) && selectedSeg) {
				const r = await getCladeLangRows(proto, selectedSeg, clade);
				langRaw = new Map(langRaw).set(clade, r);
			}
		}
		expanded = s;
	}
	function langRows(clade: string): { lang: string; name: string; row: Row }[] {
		const raw = (langRaw.get(clade) ?? []).filter(
			(r) => (!prev || r.prev === prev) && (!next || r.next === next)
		);
		const names = new Map(raw.map((r) => [r.lang, r.langName]));
		return [...rollup(raw, (r) => r.lang).values()]
			.sort((a, b) => {
				const fa = langFavRank(a.key);
				const fb = langFavRank(b.key);
				if (fa !== fb) return fa - fb; // pinned languages first
				return b.total - a.total;
			})
			.map((row) => ({ lang: row.key, name: names.get(row.key) ?? row.key, row }));
	}

	// ---- hover popover (summary) + click-through to the reflex list --------
	interface Pop { x: number; y: number; clade: string; o: Outcome; }
	let pop = $state<Pop | null>(null);
	let popTimer: ReturnType<typeof setTimeout>;
	function enterSeg(e: MouseEvent, clade: string, o: Outcome) {
		clearTimeout(popTimer);
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		pop = { x: rect.left + rect.width / 2, y: rect.top, clade, o };
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

<h1>Sound Correspondences</h1>

{#if families.length}
	<div class="toggle" role="tablist" aria-label="Proto-language">
		{#each families as f (f.id)}
			<button role="tab" aria-selected={proto === f.id} class:on={proto === f.id} onclick={() => selectProto(f.id)}>{f.name}</button>
		{/each}
	</div>
{/if}

<div class="segbar">
	{#each segments as s (s.seg)}
		<button class="pseg" class:sel={selectedSeg === s.seg} onclick={() => selectSeg(s.seg)}>
			{s.seg}<span class="cnt">{s.total.toLocaleString()}</span>
		</button>
	{/each}
</div>

{#if loading || loadingSeg}
	<div class="loader-line" style="margin-top:1.5rem"></div>
{:else if selectedSeg}
	<!-- environment builder -->
	<div class="builder card">
		<SegPicker label="preceding" options={prevOptions} value={prev} onSelect={(v) => (prev = v)} />
		<div class="focus phon">{envLabel}</div>
		<SegPicker
			label="following"
			options={nextOptions}
			value={next}
			onSelect={(v) => (next = v)}
			align="end"
		/>
	</div>

	<p class="count muted">
		{totalN.toLocaleString()} instances of {envLabel} across {byClade.length} branches
	</p>

	<div class="table-wrap">
		<table class="corr">
			<tbody>
				{#each byClade as row (row.key)}
					<tr class="crow">
						<td class="c-clade" style="border-left-color:{cladeColor(row.key)}">
							<button class="expander" onclick={() => toggleClade(row.key)} aria-label="expand branch">
								{expanded.has(row.key) ? '▾' : '▸'}
							</button>
							<span class="cname">{row.key}</span>
							<span class="rowtot">{row.total.toLocaleString()}</span>
						</td>
						<td class="c-dist">
							<div class="bar">
								{#each row.outcomes as o (o.reflexSeg + o.change)}
									<a
										class="seg"
										href={setHref(row.key, o)}
										style="width:{(o.n / row.total) * 100}%; background:{color(o.reflexSeg)}"
										onmouseenter={(e) => enterSeg(e, row.key, o)}
										onmouseleave={leaveSeg}
										aria-label="{o.reflexSeg || '∅'} {o.n}"
									></a>
								{/each}
							</div>
						</td>
					</tr>
					{#if expanded.has(row.key)}
						{#each langRows(row.key) as lr (lr.lang)}
							<tr class="lrow">
								<td class="c-clade lang-sub">
									<span class="cname">{lr.name}</span>
									<span class="rowtot">{lr.row.total.toLocaleString()}</span>
								</td>
								<td class="c-dist">
									<div class="bar small">
										{#each lr.row.outcomes as o (o.reflexSeg + o.change)}
											<a
												class="seg"
												href={setHref(row.key, o, lr.lang)}
												style="width:{(o.n / lr.row.total) * 100}%; background:{color(o.reflexSeg)}"
												onmouseenter={(e) => enterSeg(e, row.key, o)}
												onmouseleave={leaveSeg}
												aria-label="{o.reflexSeg || '∅'} {o.n}"
											></a>
										{/each}
									</div>
								</td>
							</tr>
						{/each}
					{/if}
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<!-- hover popover (summary; click the bar for the reflex list) -->
{#if pop}
	{@const info = changeInfo(pop.o.change)}
	<div class="pop" style="left:{pop.x}px; top:{pop.y}px" role="tooltip">
		<div class="pop-head">
			<span class="sw" style="background:{color(pop.o.reflexSeg)}"></span>
			<b class="phon">*{selectedSeg} → {pop.o.reflexSeg || '∅'}</b>
			<span class="pop-n">{pop.o.n.toLocaleString()}</span>
		</div>
		<div class="pop-sub muted">{pop.clade} · {info.name} — click for reflexes</div>
	</div>
{/if}

<style>
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

	table.corr {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.92rem;
	}
	table.corr td {
		padding: 0.3rem 0.6rem;
		vertical-align: middle;
		border-bottom: 1px solid var(--border);
	}
	.c-clade {
		width: 180px;
		white-space: nowrap;
		border-left: 3px solid var(--clade-empty);
	}
	.expander {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--muted);
		font-size: 0.7rem;
		padding: 0 4px 0 0;
	}
	.cname {
		font-weight: 600;
		font-size: 0.85rem;
	}
	.lang-sub {
		padding-left: 1.6rem;
		border-left-color: transparent;
	}
	.lang-sub .cname {
		font-weight: 400;
		color: var(--muted);
	}
	.rowtot {
		color: var(--faint);
		font-weight: 400;
		font-size: 0.74rem;
		margin-left: 6px;
	}
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

	/* hover popover */
	.pop {
		position: fixed;
		transform: translate(-50%, calc(-100% - 8px));
		z-index: 1200;
		background: var(--surface);
		border: 1px solid var(--border-strong);
		border-radius: 8px;
		box-shadow: var(--shadow-md);
		padding: 0.5rem 0.7rem;
		min-width: 150px;
		max-width: 260px;
		pointer-events: auto;
	}
	.pop-head {
		display: flex;
		align-items: baseline;
		gap: 6px;
	}
	.pop-head b {
		font-size: 1.05rem;
	}
	.sw {
		width: 11px;
		height: 11px;
		border-radius: 50%;
		align-self: center;
		border: 1px solid rgba(0, 0, 0, 0.25);
	}
	.pop-n {
		margin-left: auto;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		font-size: 0.85rem;
	}
	.pop-sub {
		font-size: 0.75rem;
		margin: 2px 0 0;
	}

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
		}
		.c-clade {
			width: 130px;
		}
	}
</style>
