<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import {
		getEntryAlignment,
		getEntryVariants,
		getAncestryChain,
		getDerivedTree,
		getReflexAlignment,
		type EntryAlignment,
		type AlignedReflex,
		type AlignSeg,
		type AncestorRef,
		type DerivedNode
	} from '$lib/query';
	import { changeInfo, changeLabel } from '$lib/soundChange';
	import { cladeRank } from '$lib/cladeTree';
	import { cladeColor } from '$lib/clades';
	import { cladeFavRank, langFavRank } from '$lib/prefs.svelte';
	import { safe, md, striptags } from '$lib/render';
	import CladeBars from '$lib/components/CladeBars.svelte';
	import Ancestry from '$lib/components/Ancestry.svelte';
	import Alignment from '$lib/components/Alignment.svelte';
	import ReflexDetail from '$lib/components/ReflexDetail.svelte';
	import LangName from '$lib/components/LangName.svelte';
	import Tags from '$lib/components/Tags.svelte';
	import MapView from '$lib/components/Map.svelte';
	import type { Language, MapMarker, Lemma } from '$lib/types';

	let { data } = $props();
	const entry = $derived(data.entry);
	const graph = $derived(data.graph);
	// the ancestry line's label depends on how this node hangs off its parent
	const relLabel = $derived(
		entry.borrowed_from
			? 'Borrowed from'
			: entry.relation === 'variant'
				? 'Variant of'
				: entry.origin_lemma_id
					? 'Reflex of'
					: 'Derived from'
	);
	// a CDIAL "Add. N" stub is a redirect — forward to the real addendum entry
	$effect(() => {
		if (entry.redirect_to) goto(`${base}/entries/${entry.redirect_to}`, { replaceState: true });
	});
	const shortGloss = (g: string) => {
		const m = /['‘]([^'’]{1,60})['’]/.exec(striptags(g)); // first quoted sense
		return m ? m[1] : '';
	};

	let ea = $state<EntryAlignment | null>(null);
	let variants = $state<Lemma[]>([]);
	let ancestryChain = $state<AncestorRef[][]>([]);
	let derivedTree = $state<DerivedNode[]>([]);
	let ownSegs = $state<AlignSeg[]>([]);
	let loading = $state(true);
	let selected = $state<number | null>(null);
	let expanded = $state<Set<string>>(new Set());
	let view = $state<'align' | 'normal'>('normal');

	onMount(() => reload(entry.id));
	let curId = '';
	$effect(() => {
		if (entry.id !== curId) reload(entry.id);
	});
	function reload(id: string) {
		curId = id;
		loading = true;
		selected = null;
		expanded = new Set();
		variants = [];
		ancestryChain = [];
		derivedTree = [];
		ownSegs = [];
		getEntryVariants(id).then((v) => (variants = v));
		getAncestryChain(id).then((c) => (ancestryChain = c));
		getDerivedTree(id).then((t) => (derivedTree = t));
		// a non-etymon node (reflex / section-form) also shows how it itself aligns to its parent
		getReflexAlignment(id).then((s) => (ownSegs = s));
		getEntryAlignment(id).then((a) => {
			ea = a;
			loading = false;
		});
	}

	// ---- rows: one per reflex, aligned into etymon-segment columns -----------
	interface Cell {
		main: AlignSeg | null; // segment aligned to this etymon position (may be a loss)
		post: AlignSeg[]; // insertions that follow it
	}
	interface Row {
		r: AlignedReflex;
		clade: string;
		firstClade: boolean;
		firstLang: boolean;
		color: string;
		cells: Cell[];
		lead: AlignSeg[]; // insertions before the first etymon position
		cogCode: string;
		cogLabel: string;
	}

	const rows = $derived.by<Row[]>(() => {
		if (!ea) return [];
		const n = ea.etymon.length;
		const sorted = [...ea.reflexes].sort((a, b) => {
			const cladeA = a.lemma.language?.clade ?? 'Other';
			const cladeB = b.lemma.language?.clade ?? 'Other';
			// pinned clades (or clades of pinned languages) float to the top, in the user's order
			const fca = cladeFavRank(cladeA);
			const fcb = cladeFavRank(cladeB);
			if (fca !== fcb) return fca - fcb;
			const ca = cladeRank(cladeA);
			const cb = cladeRank(cladeB);
			if (ca !== cb) return ca - cb;
			// within a clade, pinned languages come first
			const fla = langFavRank(a.lemma.language_id);
			const flb = langFavRank(b.lemma.language_id);
			if (fla !== flb) return fla - flb;
			const la = a.lemma.language?.order ?? 0;
			const lb = b.lemma.language?.order ?? 0;
			if (la !== lb) return la - lb;
			if (a.lemma.language_id !== b.lemma.language_id)
				return a.lemma.language_id.localeCompare(b.lemma.language_id);
			return (a.lemma.cognateset ?? '').localeCompare(b.lemma.cognateset ?? '');
		});
		let lastClade = '';
		let lastLang = '';
		return sorted.map((r) => {
			const clade = r.lemma.language?.clade ?? 'Other';
			const firstClade = clade !== lastClade;
			lastClade = clade;
			const firstLang = r.lemma.language_id !== lastLang || firstClade;
			lastLang = r.lemma.language_id;

			const cells: Cell[] = Array.from({ length: n }, () => ({ main: null, post: [] }));
			const lead: AlignSeg[] = [];
			let lastCol = -1;
			for (const s of r.segs) {
				if (s.etymonIdx >= 0 && s.etymonIdx < n) {
					cells[s.etymonIdx].main = s;
					lastCol = s.etymonIdx;
				} else if (lastCol >= 0) cells[lastCol].post.push(s);
				else lead.push(s);
			}
			const cog = r.lemma.cognateset ?? '';
			const ci = cog.indexOf(':');
			return {
				r,
				clade,
				firstClade,
				firstLang,
				color: cladeColor(clade),
				cells,
				lead,
				cogCode: ci === -1 ? cog : cog.slice(0, ci),
				cogLabel: ci === -1 ? '' : cog.slice(ci + 1)
			};
		});
	});
	const totalCols = $derived(view === 'align' ? (ea?.etymon.length ?? 0) + 4 : 5);

	// ---- correspondence for the selected column (etymon segment) -------------
	interface Corr { seg: string; change: string; count: number; langs: string[] }
	const correspondence = $derived.by<Corr[]>(() => {
		if (!ea || selected == null) return [];
		const m = new Map<string, Corr>();
		for (const r of ea.reflexes) {
			const s = r.segs.find((x) => x.etymonIdx === selected);
			if (!s) continue;
			const k = s.reflexSeg + '|' + s.change;
			if (!m.has(k)) m.set(k, { seg: s.reflexSeg, change: s.change, count: 0, langs: [] });
			const c = m.get(k)!;
			c.count++;
			const nm = r.lemma.language?.name;
			if (nm && !c.langs.includes(nm)) c.langs.push(nm);
		}
		return [...m.values()].sort((a, b) => b.count - a.count);
	});
	const selSeg = $derived(selected != null && ea ? ea.etymon[selected]?.seg : null);

	function toggleSel(i: number) {
		selected = selected === i ? null : i;
	}
	function toggleExp(id: string) {
		const s = new Set(expanded);
		s.has(id) ? s.delete(id) : s.add(id);
		expanded = s;
	}

	// categorical palette for correspondence-outcome overlays (readable on the tan map)
	const PALETTE = [
		'#3366CC', '#DC3912', '#FF9900', '#109618', '#990099',
		'#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395'
	];
	// outcome segment (at the selected column) → colour, ordered by frequency; loss → grey
	const outcomeColors = $derived.by<Map<string, string>>(() => {
		const m = new Map<string, string>();
		if (selected == null) return m;
		const bySeg = new Map<string, number>();
		for (const c of correspondence) {
			const k = c.seg || '∅';
			bySeg.set(k, (bySeg.get(k) ?? 0) + c.count);
		}
		let pi = 0;
		for (const [seg] of [...bySeg.entries()].sort((a, b) => b[1] - a[1]))
			m.set(seg, seg === '∅' ? '#8b8b8b' : PALETTE[pi++ % PALETTE.length]);
		return m;
	});

	const markers = $derived.by<MapMarker[]>(() => {
		if (!ea) return [];
		const byLang = new Map<string, { lang: Language; reflexes: AlignedReflex[] }>();
		for (const r of ea.reflexes) {
			const l = r.lemma.language;
			if (!l || l.lat == null) continue;
			if (!byLang.has(l.id)) byLang.set(l.id, { lang: l, reflexes: [] });
			byLang.get(l.id)!.reflexes.push(r);
		}
		return [...byLang.values()].map(({ lang, reflexes }) => {
			let color = cladeColor(lang.clade);
			let extra = '';
			let dim = false;
			if (selected != null) {
				const seg = reflexes.map((r) => r.segs.find((s) => s.etymonIdx === selected)).find(Boolean);
				const out = seg ? seg.reflexSeg || '∅' : null;
				if (out != null) {
					color = outcomeColors.get(out) ?? '#8b8b8b';
					extra = ` · *${selSeg} → ${out}`;
				} else dim = true;
			}
			const words = reflexes.map((r) => striptags(r.lemma.word));
			const ids = reflexes.map((r) => r.lemma.id);
			return {
				lat: lang.lat,
				long: lang.long,
				svg: lang.map_marker,
				color,
				dim,
				tooltip: `${lang.name}${extra ? ` · <span class="phon">${extra.slice(3)}</span>` : ''}`,
				popupHtml: `<h3>${striptags(lang.name)}</h3><ul>${words
					.map(
						(w, i) =>
							`<li><a class="lemma-word" href="${base}/reflexes/${ids[i]}">${w}</a></li>`
					)
					.join('')}</ul>`
			};
		});
	});

	// always frame the map on South Asia (the Map flags anything outside the live view itself)
	const INDIA_BOUNDS: [[number, number], [number, number]] = [
		[4, 60],
		[37, 98]
	];

	const plainGloss = $derived(striptags(entry.gloss) || shortGloss(entry.etymology ?? ''));
	const langCount = $derived(markers.length);

	function rowClick(e: MouseEvent, id: string) {
		if ((e.target as HTMLElement).closest('a')) return;
		toggleExp(id);
	}
</script>

{#snippet segChip(s: AlignSeg, ins: boolean)}
	{@const info = changeInfo(s.change)}
	{#if s.change === 'loss'}
		<span class="seg loss" title={changeLabel(s.etymonSeg, '', s.change)}>·</span>
	{:else}
		<span
			class="seg {info.cls}"
			class:ins
			title={changeLabel(s.etymonSeg, s.reflexSeg, s.change)}>{s.reflexSeg}</span
		>
	{/if}
{/snippet}

<svelte:head>
	<title>{striptags(entry.word)} [{entry.id}] — Jambu</title>
	<meta
		name="description"
		content="{striptags(entry.word)} ({plainGloss}) — {entry.language?.name} headword [{entry.id}] in the Jambu etymological dictionary, aligned with its reflexes and sound changes across South Asian languages."
	/>
</svelte:head>

<!-- header -->
<div class="entry-head">
	<h1 class="headword">
		<a href="{base}/languages/{entry.language?.id}" class="faint">{entry.language?.name}</a>
		<span class="lemma-word">{@html safe(entry.word)}</span>
		<span class="id-tag">[{entry.id}]</span>
	</h1>
	<CladeBars clades={entry.clades} size="lg" />
</div>
{#if ancestryChain.length}
	<Ancestry label={relLabel} chain={ancestryChain} startLang={entry.language?.name} />
{/if}
{#if entry.gloss || entry.tags}
	<p class="gloss serif">
		{@html safe(entry.gloss)}{#if entry.tags}
			<Tags tags={entry.tags} />{/if}
	</p>
{/if}
{#if variants.length}
	<div class="variants">
		<span class="v-label">Variant{variants.length === 1 ? '' : 's'}</span>
		{#each variants as v (v.id)}<span class="v-one"
				><a class="v-item phon" href="{base}/reflexes/{v.id}">{@html safe(v.word)}</a
				>{#if v.gloss}<span class="v-gloss muted">&nbsp;‘{striptags(v.gloss)}’</span>{/if}</span
			>{/each}
	</div>
{/if}
{#if entry.etymology}
	<!-- a main entry and its merged addenda each keep their own CDIAL snippet, joined in the DB by
	     an addendum-delimiter comment; render one accented block per snippet so none is dropped. -->
	{#each entry.etymology.split('<!--addendum-->') as block, i (i)}
		{#if block.trim()}<div class="etymology serif">{@html safe(block)}</div>{/if}
	{/each}
{/if}
{#if entry.notes}
	<details class="notes">
		<summary>Etymological notes</summary>
		<div class="markdown">{@html md(entry.notes)}</div>
	</details>
{/if}

<!-- how this node itself aligns to its parent (only non-etyma have a segment alignment) -->
{#if ownSegs.length}
	<div class="own-align">
		<span class="oa-label">Sound changes</span>
		<Alignment segs={ownSegs} />
	</div>
{/if}

<!-- derived terms (compound / affixed etyma built on this one) — before the reflexes -->
{#snippet dnode(d: DerivedNode)}
	<li>
		<div class="drow">
			<a class="d-word phon" href="{base}/entries/{d.id}">{@html safe(d.word)}</a>
			<span class="id-tag">[{d.id}]</span>
			{#if shortGloss(d.gloss) || striptags(d.gloss)}<span class="d-gloss"
					>‘{shortGloss(d.gloss) || striptags(d.gloss)}’</span
				>{/if}
			{#if d.reflex_count}<span class="d-count muted"
					>{d.reflex_count} reflex{d.reflex_count === 1 ? '' : 'es'} · {d.lang_count} lang{d.lang_count ===
					1
						? ''
						: 's'}</span
				>{/if}
		</div>
		{#if d.children.length}<ul class="dtree">
				{#each d.children as c (c.id)}{@render dnode(c)}{/each}
			</ul>{/if}
	</li>
{/snippet}

{#if graph.derived.length}
	<details class="derived" open={graph.derived.length <= 12}>
		<summary>Derived terms <span class="muted">({graph.derived.length})</span></summary>
		<ul class="dtree">
			{#each derivedTree as d (d.id)}{@render dnode(d)}{/each}
		</ul>
	</details>
{/if}

<!-- view toggle -->
{#if ea}
	<div class="toggle" role="tablist" aria-label="View">
		<button role="tab" aria-selected={view === 'align'} class:on={view === 'align'} onclick={() => (view = 'align')}>Alignment</button>
		<button role="tab" aria-selected={view === 'normal'} class:on={view === 'normal'} onclick={() => (view = 'normal')}>Normal</button>
	</div>
{/if}

<!-- correspondence readout for the selected column -->
{#if ea && view === 'align' && selected != null}
	<div class="corrbar active">
		<span class="corr-head">*{selSeg} →</span>
		{#each correspondence as c (c.seg + c.change)}
			{@const info = changeInfo(c.change)}
			<span class="corr-chip {info.cls}" title={c.langs.join(', ')}>
				<span class="sw" style="background:{outcomeColors.get(c.seg || '∅')}"></span><b
					>{c.seg || '∅'}</b
				><span class="x">×{c.count}</span><span class="corr-name">{info.name}</span>
			</span>
		{/each}
		<button class="clear" onclick={() => (selected = null)}>clear</button>
	</div>
{/if}

<!-- alignment matrix -->
{#if loading}
	<div class="loader-line" style="margin:1.5rem 0"></div>
{:else if ea}
	<p class="count muted">{ea.reflexes.length.toLocaleString()} reflexes · {langCount} languages</p>
	<div class="entry-body">
		<div class="matrix-col">
			<div class="table-wrap aln-wrap">
				<table class="aln">
			<thead>
				<tr>
					<th class="c-clade">Clade</th>
					<th class="c-lang">Language</th>
					{#if view === 'align'}
						{#each ea.etymon as seg (seg.idx)}
							<th
								class="c-seg seg-head"
								class:sel={selected === seg.idx}
								onclick={() => toggleSel(seg.idx)}>{seg.seg}</th
							>
						{/each}
					{:else}
						<th class="c-form">Form</th>
					{/if}
					<th class="c-gloss">Gloss</th>
					<th class="c-cog">§</th>
				</tr>
			</thead>
			<tbody>
				{#each rows as row (row.r.lemma.id)}
					<tr
						class="rrow"
						class:clade-first={row.firstClade}
						class:open={expanded.has(row.r.lemma.id)}
						style="--clade:{row.color}"
						onclick={(e) => rowClick(e, row.r.lemma.id)}
					>
						<td class="c-clade clade-cell">{row.firstClade ? row.clade : ''}</td>
						<td class="c-lang">
							{#if row.firstLang}<LangName lang={row.r.lemma.language} />{/if}
						</td>
						{#if view === 'normal'}
							<td class="c-form formcell">
								<span class="lemma-word">{@html safe(row.r.lemma.word)}</span>{#if row.r.lemma.phonemic}
									<span class="phon">/{row.r.lemma.phonemic}/</span>{/if}{#if row.r.lemma.reflex_sub_count}&nbsp;<a class="refcount" href="{base}/entries/{row.r.lemma.id}" title="{row.r.lemma.reflex_sub_count} reflex(es) of this word">→&#8288;{row.r.lemma.reflex_sub_count}</a>{/if}{#if row.r.lemma.sub_count}&nbsp;<a class="subcount" href="{base}/entries/{row.r.lemma.id}" title="{row.r.lemma.sub_count} form(s) borrowed from this word">→&#8288;{row.r.lemma.sub_count}</a>{/if}
								{#each row.r.lemma.variants ?? [] as v (v.id)}<span class="rvar-line"
										><span class="rvar-arrow">→</span>&nbsp;<span class="rvar"
											>{@html safe(v.word)}</span
										></span
									>{/each}
							</td>
						{:else if row.r.segs.length}
							{#each row.cells as cell, i (i)}
								<td class="c-seg cell" class:sel={selected === i}>
									{#if i === 0}{#each row.lead as s (s.pos)}{@render segChip(s, true)}{/each}{/if}
									{#if cell.main}{@render segChip(cell.main, false)}{/if}
									{#each cell.post as s (s.pos)}{@render segChip(s, true)}{/each}
								</td>
							{/each}
						{:else}
							<td class="c-seg plainform" colspan={ea.etymon.length}
								>{@html safe(row.r.lemma.word)}</td
							>
						{/if}
						<td class="c-gloss gloss-cell"
							>{@html safe(row.r.lemma.gloss)}{#if row.r.lemma.tags}
								<Tags tags={row.r.lemma.tags} />{/if}</td
						>
						<td class="c-cog cog-cell" title={striptags(row.cogLabel)}>{row.cogCode}</td>
					</tr>
					{#if expanded.has(row.r.lemma.id)}
						{@const r = row.r}
						<tr class="detail-row">
							<td></td>
							<td colspan={totalCols - 1} class="detail-cell">
								<ReflexDetail lemma={r.lemma} segs={r.segs} />
							</td>
						</tr>
					{/if}
				{/each}
			</tbody>
		</table>
		</div>
		</div>

		<aside class="map-col">
			{#if markers.length}<MapView {markers} height="64vh" bounds={INDIA_BOUNDS} />{/if}
			<div class="map-cap muted">
				{#if selected != null}marker colour = <b class="phon">*{selSeg}</b> outcome{:else}select a
					column to map its outcomes{/if}
			</div>
		</aside>
	</div>
{/if}

<style>
	.derived {
		margin: 1rem 0 1.25rem;
		border: 1px solid var(--border);
		border-radius: 8px;
		background: var(--surface-2);
		padding: 0.55rem 0.85rem;
	}
	.derived > summary {
		cursor: pointer;
		font-weight: 600;
		font-size: 1rem;
		list-style-position: inside;
	}
	.derived[open] > summary {
		margin-bottom: 0.55rem;
	}
	.dtree {
		list-style: none;
		margin: 0;
		padding: 0;
		font-size: 0.92rem;
	}
	/* nested derived terms indent, with a hairline guide */
	.dtree .dtree {
		margin-left: 0.5rem;
		padding-left: 0.7rem;
		border-left: 1px solid var(--border);
	}
	.drow {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.4rem;
		padding: 0.16rem 0;
	}
	.derived .d-word {
		font-weight: 600;
	}
	.derived .d-gloss {
		color: var(--muted);
		font-style: italic;
	}
	.derived .d-count {
		font-size: 0.8rem;
		white-space: nowrap;
		margin-left: auto;
	}
	.entry-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		margin-top: 1rem;
	}
	.entry-head :global(.clades) {
		margin-top: 0.9rem;
		flex-shrink: 0;
	}
	.gloss {
		font-size: 1.2rem;
		margin: 0.1rem 0 0.5rem;
	}
	/* this node's own alignment to its parent (shown on reflex / section-form pages) */
	.own-align {
		margin: 0.4rem 0 0.9rem;
	}
	.oa-label {
		display: block;
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
		margin-bottom: 0.3rem;
	}
	/* the free-text etymological entry (CDIAL dictionary text: sub-forms, sources, cross-refs) */
	.etymology {
		font-size: 1rem;
		line-height: 1.55;
		color: var(--ink);
		margin: 0.4rem 0 0.8rem;
		padding: 0.7rem 1rem;
		background: var(--surface-2);
		border-left: 3px solid var(--berry);
		border-radius: 0 8px 8px 0;
	}
	.etymology :global(a[data-entry]) {
		color: var(--plum-2);
	}
	/* same-language variant / reconstructed forms, kept apart from the daughter reflexes */
	.variants {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.25rem 1.4rem;
		font-size: 0.95rem;
		margin: 0 0 0.7rem;
	}
	.variants .v-label {
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
	}
	.variants .v-item {
		font-family: var(--font-phon);
	}
	.notes summary {
		cursor: pointer;
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--plum-2);
	}
	.notes .markdown {
		font-size: 0.92rem;
		margin-top: 0.4rem;
	}

	/* view toggle */
	.toggle {
		display: inline-flex;
		margin-top: 0.8rem;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		padding: 2px;
		background: var(--surface);
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

	.formcell {
		text-align: left;
	}
	.formcell .lemma-word {
		font-size: 1.1rem;
	}
	.formcell .phon {
		font-size: 0.82rem;
		color: var(--muted);
		margin-left: 3px;
	}
	/* borrowed-descendant count badge (forms borrowed from this reflex) */
	.subcount {
		display: inline-block;
		padding: 0 0.3rem;
		border-radius: 999px;
		font-size: 0.7rem;
		font-weight: 600;
		background: color-mix(in srgb, var(--berry) 12%, transparent);
		color: var(--berry);
		white-space: nowrap;
		vertical-align: middle;
	}
	/* daughter-reflex count badge (this reflex is itself an etymon with descendants) —
	   outlined, to read distinctly from the filled borrowed badge above */
	.refcount {
		display: inline-block;
		padding: 0 0.3rem;
		border-radius: 999px;
		font-size: 0.7rem;
		font-weight: 600;
		background: transparent;
		border: 1px solid color-mix(in srgb, var(--plum) 45%, transparent);
		color: var(--plum);
		white-space: nowrap;
		vertical-align: middle;
	}
	/* comma-listed alternates of a reflex, one per line beneath it */
	.rvar-line {
		display: block;
		font-size: 0.85rem;
		color: var(--muted);
	}
	.rvar-arrow {
		font-size: 0.72rem;
		color: var(--faint);
	}
	.rvar {
		font-family: var(--font-phon);
		white-space: nowrap;
	}
	th.c-form {
		text-align: left;
	}

	/* correspondence bar */
	.corrbar {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 6px;
		margin-top: 0.8rem;
		padding: 0.55rem 0.8rem;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background: var(--surface);
		font-size: 0.85rem;
		min-height: 1.2rem;
	}
	.corrbar.active {
		border-color: var(--berry);
	}
	.corr-head {
		font-family: var(--font-phon);
		font-size: 1.1rem;
		font-weight: 600;
	}
	.corr-chip {
		display: inline-flex;
		align-items: baseline;
		gap: 5px;
		padding: 3px 11px;
		border-radius: 999px;
		font-size: 0.8rem;
		border: 1px solid var(--border-strong);
	}
	.corr-chip b {
		font-family: var(--font-phon);
		font-size: 0.98rem;
	}
	.corr-chip .sw {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		border: 1px solid rgba(0, 0, 0, 0.25);
		flex-shrink: 0;
	}
	.corr-chip .x {
		color: var(--muted);
	}
	.corr-name {
		font-size: 0.68rem;
		color: var(--muted);
	}
	.clear {
		margin-left: auto;
		background: none;
		border: none;
		color: var(--muted);
		cursor: pointer;
		font-size: 0.78rem;
		text-decoration: underline;
	}

	.count {
		margin: 1rem 0 0.4rem;
		font-size: 0.85rem;
	}

	/* alignment matrix — scroll box so the header can pin while the rows scroll */
	.aln-wrap {
		max-height: 74vh;
		overflow: auto;
	}
	table.aln {
		border-collapse: collapse;
		font-size: 0.92rem;
		min-width: 100%;
	}
	table.aln th {
		text-align: left;
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 0.78rem;
		color: var(--muted);
		background: var(--surface-2);
		border-bottom: 1px solid var(--border-strong);
		padding: 0.3rem 0.5rem;
		vertical-align: middle;
		position: sticky;
		top: 0;
		z-index: 6;
	}
	.c-clade {
		width: 88px;
	}
	/* header rail lining up with the coloured clade accent on the cells below */
	table.aln th.c-clade {
		border-left: 3px solid var(--border-strong);
	}
	.c-lang {
		width: 130px;
	}
	.c-seg {
		text-align: center;
		width: 2.4em;
	}
	table.aln th.seg-head {
		text-align: center;
		font-family: var(--font-phon);
		font-size: 1.08rem;
		font-weight: 600;
		color: var(--ink);
		cursor: pointer;
		user-select: none;
	}
	table.aln th.seg-head:hover {
		color: var(--berry);
	}
	table.aln th.seg-head.sel {
		background: var(--berry);
		color: #fff;
	}
	.c-gloss {
		width: auto;
	}
	.c-cog {
		text-align: center;
		width: 2em;
	}

	table.aln td {
		padding: 0.26rem 0.55rem;
		vertical-align: middle;
	}
	.rrow {
		cursor: pointer;
	}
	.rrow:hover td {
		background: color-mix(in srgb, var(--surface-2) 60%, transparent);
	}
	.rrow.open td {
		background: var(--surface-2);
	}
	/* divide only between clade groups, not every row */
	.rrow.clade-first td {
		border-top: 1px solid var(--border);
	}
	.clade-cell {
		font-size: 0.8rem;
		font-weight: 600;
		border-left: 3px solid var(--clade);
		white-space: nowrap;
	}
	td.c-lang {
		font-size: 0.86rem;
	}
	td.c-seg {
		text-align: center;
		white-space: nowrap;
		padding-left: 0.3rem;
		padding-right: 0.3rem;
	}
	td.c-seg.sel {
		background: color-mix(in srgb, var(--berry) 11%, transparent) !important;
	}
	.plainform {
		text-align: left;
		font-family: var(--font-phon);
		font-size: 1.1rem;
		color: var(--muted);
	}
	/* every segment is a uniform padded slot; changed/inserted ones are filled */
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
	.gloss-cell {
		color: var(--muted);
		font-size: 0.88rem;
	}
	.cog-cell {
		text-align: center;
		font-size: 0.8rem;
		color: var(--faint);
	}

	/* expanded detail */
	.detail-row td {
		border-bottom: none;
		padding-top: 0;
	}
	.detail-cell {
		padding-bottom: 8px;
	}

	/* two-column body with a sticky map that floats as you scroll */
	.entry-body {
		display: flex;
		gap: 1.5rem;
		align-items: flex-start;
	}
	.matrix-col {
		flex: 1 1 auto;
		min-width: 0;
	}
	.map-col {
		flex: 0 0 340px;
		width: 340px;
		position: sticky;
		top: 66px;
	}
	.map-cap {
		font-size: 0.78rem;
		text-align: center;
		margin-top: 0.45rem;
	}
	@media (max-width: 900px) {
		.entry-body {
			flex-direction: column;
			align-items: stretch; /* fill width so the matrix scrolls internally, not the page */
		}
		.matrix-col {
			width: 100%;
		}
		.map-col {
			position: static;
			width: 100%;
			flex-basis: auto;
		}
	}
	@media (max-width: 640px) {
		/* let the clade strip drop below the headword instead of overflowing */
		.entry-head {
			flex-wrap: wrap;
		}
		.entry-head :global(.clades) {
			flex-wrap: wrap;
			margin-top: 0.4rem;
		}
	}
</style>
