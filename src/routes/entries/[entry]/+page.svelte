<script lang="ts">
	import PageFormsSearch from '$lib/components/PageFormsSearch.svelte';
	import { base } from '$app/paths';
	import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { unicodeSearchIncludes } from '$lib/unicodeSearch';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import {
		getEntryAlignment,
		getEntryVariants,
		getAncestryChain,
		getDerivedTree,
		getAllDialects,
		getReflexAlignment,
		type EntryAlignment,
		type AlignedReflex,
		type AlignSeg,
		type AncestorRef,
		type AlternateEtymon,
		getAlternates,
		getCrossFamilyComparisons,
		type DerivedNode
	} from '$lib/query';
	import { changeInfo, changeLabel } from '$lib/soundChange';
	import { cladeRank } from '$lib/cladeTree';
	import { cladeColor } from '$lib/clades';
	import { cladeFavRank, langFavRank } from '$lib/prefs.svelte';
	import { safe, md, relationLabel, striptags } from '$lib/render';
	import { comparisonLabel } from '$lib/comparisons';
	import CladeBars from '$lib/components/CladeBars.svelte';
	import Ancestry from '$lib/components/Ancestry.svelte';
	import Alignment from '$lib/components/Alignment.svelte';
	import ReflexDetail from '$lib/components/ReflexDetail.svelte';
	import LangName from '$lib/components/LangName.svelte';
	import Tags from '$lib/components/Tags.svelte';
	import MapView from '$lib/components/Map.svelte';
	import { activePoint, mutedPoint, pieMarker } from '$lib/atlas';
	import FormWord from '$lib/components/FormWord.svelte';
	import ReferenceLink from '$lib/components/ReferenceLink.svelte';
	import RefList from '$lib/components/RefList.svelte';
	import CollapsibleSourceScan from '$lib/components/CollapsibleSourceScan.svelte';
	import type {
		CrossFamilyComparison,
		Dialect,
		EntryTextBlock,
		Language,
		MapMarker,
		Lemma,
		Reference
	} from '$lib/types';

	let { data } = $props();
	const entry = $derived(data.entry);
	const graph = $derived(data.graph);
	// the ancestry line's label depends on how this node hangs off its parent
	const relLabel = $derived(relationLabel(entry));
	// a CDIAL "Add. N" stub is a redirect — forward to the real addendum entry
	$effect(() => {
		if (entry.redirect_to) goto(`${base}/entries/${entry.redirect_to}`, { replaceState: true });
	});
	const shortGloss = (g: string) => {
		const m = /['‘]([^'’]{1,60})['’]/.exec(striptags(g)); // first quoted sense
		return m ? m[1] : '';
	};
	const blockReference = (block: EntryTextBlock): Reference | null =>
		block.source_id
			? {
					id: block.source_id,
					short: block.source_label,
					source: block.source_citation,
					progress: block.source_progress,
					provenance: block.source_provenance,
					editor: block.source_editor,
					ocr: block.source_ocr ?? false,
					lemma_count: block.source_lemma_count ?? 0,
					unetymologised_count: block.source_unetymologised_count ?? 0,
					locator: block.locator ?? undefined
				}
			: null;
	const isKewaBlock = (block: EntryTextBlock) => block.source_id === 'mayrhofer-kewa';
	function referenceSummary(references: Reference[]): Reference[] {
		const byId = new Map<string, Reference>();
		for (const reference of references) {
			const existing = byId.get(reference.id);
			if (!existing) {
				byId.set(reference.id, { ...reference });
			} else if (
				reference.locator &&
				!existing.locator?.split('; ').includes(reference.locator)
			) {
				existing.locator = [existing.locator, reference.locator].filter(Boolean).join('; ');
			}
		}
		return [...byId.values()].sort((a, b) =>
			(a.short ?? a.id).localeCompare(b.short ?? b.id)
		);
	}

	let ea = $state<EntryAlignment | null>(null);
	let variants = $state<Lemma[]>([]);
	let ancestryChain = $state<AncestorRef[][]>([]);
	let alternates = $state<AlternateEtymon[]>([]);
	let comparisons = $state<CrossFamilyComparison[]>([]);
	let derivedTree = $state<DerivedNode[]>([]);
	let ownSegs = $state<AlignSeg[]>([]);
	let dialects = $state<Dialect[]>([]);
	let loading = $state(true);
	const hasDescendants = $derived(!loading && !!ea?.reflexes.length);
	const origin = $derived(ancestryChain[0]?.[0]);
	let selected = $state<number | null>(null);
	let expanded = $state<Set<string>>(new Set());
	let view = $state<'align' | 'concept' | 'normal'>('normal');
	const entryReferences = $derived.by(() =>
		referenceSummary(
			[
				...(entry.references ?? []),
				...(entry.text_blocks ?? []).map(blockReference).filter((r): r is Reference => r != null),
				...variants.flatMap((variant) => variant.references ?? []),
				...comparisons.map((comparison) => comparison.reference)
			]
		)
	);
	const reflexReferences = $derived.by(() =>
		referenceSummary(
			(ea?.reflexes ?? []).flatMap(({ lemma }) => [
				...(lemma.references ?? []),
				...(lemma.variants ?? []).flatMap((variant) => variant.references ?? [])
			])
		)
	);

	onMount(() => reload(entry.id));
	let curId = '';
	$effect(() => {
		if (entry.id !== curId) reload(entry.id);
	});
	function reload(id: string) {
		curId = id;
		loading = true;
		ea = null;
		selected = null;
		expanded = new Set();
		variants = [];
		ancestryChain = [];
		alternates = [];
		comparisons = [];
		derivedTree = [];
		ownSegs = [];
		getEntryVariants(id).then((v) => (variants = v));
		getAncestryChain(id).then((c) => (ancestryChain = c));
		getAlternates(id).then((a) => (alternates = a));
		getCrossFamilyComparisons(id).then((c) => (comparisons = c));
		getDerivedTree(id).then((t) => (derivedTree = t));
		getAllDialects().then((d) => (dialects = d));
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

	const formSearch = $derived(browser ? page.url.searchParams.get('word')?.trim() ?? '' : '');
	const relaxedSearch = $derived(browser && page.url.searchParams.get('relaxed') === '1');
	const filteredReflexes = $derived((ea?.reflexes ?? []).filter((reflex) => {
		if (!formSearch) return true;
		const lemma = reflex.lemma;
		const fields = [lemma.id, lemma.word, lemma.native, lemma.phonemic, lemma.gloss,
			lemma.notes, lemma.tags, lemma.cognateset, lemma.language_id,
			lemma.language?.name, lemma.language?.clade,
			...(lemma.variants ?? []).flatMap((variant) => [variant.word, variant.gloss]),
			...(lemma.references ?? []).flatMap((reference) => [reference.id, reference.short, reference.source, reference.locator]),
			...reflex.concepts.map((concept) => concept.name)];
		return fields.some((field) => unicodeSearchIncludes(striptags(field ?? ''), formSearch, relaxedSearch));
	}));
	const rows = $derived.by<Row[]>(() => {
		if (!ea) return [];
		const n = ea.etymon.length;
		const sorted = [...filteredReflexes].sort((a, b) => {
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
	const totalCols = $derived(
		view === 'align' ? (ea?.etymon.length ?? 0) + 4 : view === 'concept' ? 6 : 5
	);

	// ---- correspondence for the selected column (etymon segment) -------------
	interface Corr { seg: string; change: string; count: number; langs: string[] }
	const correspondence = $derived.by<Corr[]>(() => {
		if (!ea || selected == null) return [];
		const m = new Map<string, Corr>();
		for (const r of filteredReflexes) {
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
	/** The column the map is answering to — only alignment view asks it anything. */
	const activeCol = $derived(view === 'align' ? selected : null);

	function toggleSel(i: number) {
		selected = selected === i ? null : i;
	}
	// which outcomes of the selected column are drawn: pinned by clicking a chip, previewed by
	// hovering one. Hovering a table row previews that reflex's own places instead.
	let pinnedOut = $state<string[]>([]);
	let hoverOut = $state<string | null>(null);
	let hoverRow = $state<string | null>(null);
	// the map repaints every point when the emphasis changes, so let the pointer settle first
	let hoverTimer: ReturnType<typeof setTimeout>;
	function previewRow(id: string | null) {
		clearTimeout(hoverTimer);
		hoverTimer = setTimeout(() => (hoverRow = id), id ? 70 : 0);
	}
	const activeOut = $derived(
		hoverOut && !pinnedOut.includes(hoverOut) ? [...pinnedOut, hoverOut] : pinnedOut
	);
	// outcomes only single anything out while their column is the one being asked about
	const litOutcomes = $derived(activeCol == null ? [] : activeOut);
	function toggleOut(seg: string) {
		pinnedOut = pinnedOut.includes(seg) ? pinnedOut.filter((o) => o !== seg) : [...pinnedOut, seg];
	}
	// a column change is a different question entirely — none of the old answers carry over
	$effect(() => {
		selected;
		pinnedOut = [];
		hoverOut = null;
	});

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
	interface ConceptSummary { id: number; name: string; category: string; count: number }
	const conceptSummary = $derived.by<ConceptSummary[]>(() => {
		const counts = new Map<number, ConceptSummary>();
		for (const reflex of filteredReflexes) {
			for (const concept of reflex.concepts) {
				const current = counts.get(concept.id);
				if (current) current.count++;
				else counts.set(concept.id, { ...concept, count: 1 });
			}
		}
		return [...counts.values()].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
	});
	const conceptColors = $derived.by<Map<number, string>>(() =>
		new Map(conceptSummary.map((concept, index) => [concept.id, PALETTE[index % PALETTE.length]]))
	);
	const unmappedConceptCount = $derived(
		filteredReflexes.filter((reflex) => reflex.concepts.length === 0).length
	);
	let pinnedConcepts = $state<number[]>([]);
	let hoverConcept = $state<number | null>(null);
	const activeConcepts = $derived(
		hoverConcept != null && !pinnedConcepts.includes(hoverConcept)
			? [...pinnedConcepts, hoverConcept]
			: pinnedConcepts
	);
	function toggleConcept(id: number) {
		pinnedConcepts = pinnedConcepts.includes(id)
			? pinnedConcepts.filter((concept) => concept !== id)
			: [...pinnedConcepts, id];
	}
	$effect(() => {
		view;
		pinnedConcepts = [];
		hoverConcept = null;
	});
	// outcome segment (at the selected column) → colour, ordered by frequency; loss → grey
	const outcomeColors = $derived.by<Map<string, string>>(() => {
		const m = new Map<string, string>();
		if (activeCol == null) return m;
		const bySeg = new Map<string, number>();
		for (const c of correspondence) {
			const k = c.seg || '∅';
			bySeg.set(k, (bySeg.get(k) ?? 0) + c.count);
		}
		let pi = 0;
		for (const [seg] of [...bySeg.entries()].sort((a, b) => b[1] - a[1]))
			m.set(seg, seg === '∅' ? '#4f555e' : PALETTE[pi++ % PALETTE.length]);
		return m;
	});

	const markers = $derived.by<MapMarker[]>(() => {
		if (!ea) return [];
		interface Location {
			lang: Language;
			name: string;
			lat: number;
			long: number;
			reflexes: AlignedReflex[];
		}
		const dialectByToken = new Map(dialects.map((d) => [d.token, d]));
		const byLocation = new Map<string, Location>();
		for (const r of filteredReflexes) {
			const l = r.lemma.language;
			if (!l) continue;
			const tagged = (r.lemma.tags ?? '')
				.split(/\s+/)
				.map((t) => dialectByToken.get(t))
				.filter((d): d is Dialect => !!d && d.lat != null && d.long != null);
			const locations = tagged.length
				? tagged.map((d) => ({ key: d.token, name: `${l.name}: ${d.name}`, lat: d.lat!, long: d.long! }))
				: l.lat != null && l.long != null
					? [{ key: `language:${l.id}`, name: l.name, lat: l.lat, long: l.long }]
					: [];
			for (const location of locations) {
				if (!byLocation.has(location.key))
					byLocation.set(location.key, { ...location, lang: l, reflexes: [] });
				byLocation.get(location.key)!.reflexes.push(r);
			}
		}
		return [...byLocation.values()].map(({ lang, name, lat, long, reflexes }) => {
			let color = cladeColor(lang.clade);
			let extra = '';
			// what this place shows for the selected column, if anything
			const seg =
				activeCol == null
					? null
					: reflexes.map((r) => r.segs.find((s) => s.etymonIdx === activeCol)).find(Boolean);
			const out = seg ? seg.reflexSeg || '∅' : null;
			if (out != null) {
				color = outcomeColors.get(out) ?? '#8b8b8b';
				extra = ` · *${selSeg} → ${out}`;
			}
			const conceptCounts = new Map<number, number>();
			for (const reflex of reflexes)
				for (const concept of reflex.concepts)
					conceptCounts.set(concept.id, (conceptCounts.get(concept.id) ?? 0) + 1);
			const conceptSlices = [...conceptCounts.entries()]
				.map(([id, n]) => ({ id, n, color: conceptColors.get(id) ?? '#8b8b8b' }))
				.sort((a, b) => b.n - a.n);
			const locationConceptIds = conceptSlices.map((slice) => slice.id);
			if (view === 'concept' && conceptSlices.length === 1)
				color = conceptSlices[0].color;
			else if (view === 'concept' && conceptSlices.length === 0)
				color = '#8b8b8b';
			const words = reflexes.map((r) => striptags(r.lemma.word));
			const ids = reflexes.map((r) => r.lemma.id);
			const ocr = reflexes.map((r) => r.lemma.references?.some((reference) => Boolean(reference.ocr)));
			// Emphasis follows the atlases: everything is drawn until you name something. A hovered
			// table row wins over a picked outcome, because it is the more specific question.
			const lit = hoverRow
				? ids.includes(hoverRow)
				: view === 'concept' && activeConcepts.length
					? locationConceptIds.some((id) => activeConcepts.includes(id))
				: litOutcomes.length
					? out != null && litOutcomes.includes(out)
					: activeCol == null || out != null;
			const conceptNames = conceptSlices
				.map((slice) => conceptSummary.find((concept) => concept.id === slice.id)?.name)
				.filter(Boolean);
			const conceptMarker = view === 'concept' && conceptSlices.length > 1;
			const pointStyle = conceptMarker
				? {
						svg: pieMarker(conceptSlices),
						size: hoverRow && ids.includes(hoverRow) ? 20 : 16,
						dim: !lit,
						foreground: lit && (!!hoverRow || activeConcepts.length > 0)
					}
				: { svg: lang.map_marker, ...(lit ? activePoint(color) : mutedPoint()) };
			return {
				lat,
				long,
				...pointStyle,
				tooltip: `${name}${extra ? ` · <span class="phon">${extra.slice(3)}</span>` : ''}${view === 'concept' ? ` · ${conceptNames.join(', ') || 'No parsed concept'}` : ''}`,
				popupHtml: `<h3>${striptags(name)}</h3><ul>${words
					.map(
						(w, i) =>
							`<li><a class="lemma-word" href="${base}/reflexes/${ids[i]}">${w}</a>${ocr[i] ? ' <span class="map-ocr" title="Parsed with optical character recognition; check the original source when accuracy matters">OCR</span>' : ''}${view === 'concept' && reflexes[i].concepts.length ? `<span class="map-concepts">${reflexes[i].concepts.map((concept) => `<a href="${base}/concepts/${concept.id}">${concept.name}</a>`).join(', ')}</span>` : ''}</li>`
					)
					.join('')}</ul>`
			};
		});
	});

	const plainGloss = $derived(striptags(entry.gloss) || shortGloss(entry.etymology ?? ''));
	const langCount = $derived(new Set(filteredReflexes.map((r) => r.lemma.language_id)).size);
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
<div class="entry-intro">
	<div class="entry-summary">
		<div class="entry-head">
			<div class="entry-title">
		<div class="entry-eyebrow">
			{#if entry.language}<a href="{base}/languages/{entry.language.id}">{entry.language.name}</a>{/if}
			<span class="entry-id" title="Entry identifier">{entry.id}</span>
		</div>
		<h1 class="headword">
			<span class="lemma-word"><FormWord word={entry.word} ocr={entry.ocr} /></span>
		</h1>
		{#if entry.phonemic}<p class="entry-pronunciation phon">/{entry.phonemic}/</p>{/if}
		{#if entry.gloss}<div class="gloss serif">{@html safe(entry.gloss)}</div>{/if}
		{#if entry.tags}<div class="entry-tags"><Tags tags={entry.tags} /></div>{/if}
			</div>
	</div>
{#if ancestryChain.length}
	<div class="entry-ancestry">
	<Ancestry label={relLabel} chain={ancestryChain} startLang={entry.language?.name} compact />
	{#if alternates.length}
		<p class="alternates">
			<span class="alt-label">also proposed</span>
			{#each alternates as a, i (a.id + i)}{#if i > 0}, {/if}from
				<a class="phon" href="{base}/{a.isEntry ? 'entries' : 'reflexes'}/{a.id}">{a.word || a.id}</a
				>{#if a.lang}&nbsp;<span class="muted">({a.lang})</span>{/if}{#if a.note?.startsWith('review:')}
				<span class="alt-review" title="auto-classified during the edge-model migration — pending curation">?</span>{/if}{/each}
		</p>
	{/if}
	</div>
{/if}
{#if variants.length}
	<div class="variants">
		<span class="v-label">Variant{variants.length === 1 ? '' : 's'}</span>
		{#each variants as v (v.id)}<span class="v-one"
				><a class="v-item phon" href="{base}/reflexes/{v.id}"><FormWord word={v.word} references={v.references} /></a
				>{#if v.gloss}<span class="v-gloss muted">&nbsp;‘{striptags(v.gloss)}’</span>{/if}</span
			>{/each}
	</div>
{/if}
{#if comparisons.length || entry.text_blocks?.length || entry.etymology || entry.notes}
	<details class="entry-evidence">
		<summary>Evidence and notes</summary>
{#if comparisons.length}
	<section class="cross-family" aria-labelledby="cross-family-title">
		<h2 id="cross-family-title">Cross-family comparisons</h2>
		<div class="comparison-list">
			{#each comparisons as comparison (comparison.id)}
				{@const comparisonRelation = comparisonLabel(comparison, entry.id)}
				<details class="comparison-row">
					<summary class="comparison-head">
						<span class="comparison-main">
							{#if comparisonRelation}<span class="comparison-relation">{comparisonRelation}</span>{/if}
							<a class="comparison-word phon" href="{base}/entries/{comparison.other_id}"
								><FormWord word={comparison.other_word || comparison.other_id} /></a
							>
							<span class="id-tag">[{comparison.other_id}]</span>
							{#if comparison.other_language_id}
								<a class="comparison-language" href="{base}/languages/{comparison.other_language_id}"
									>{comparison.other_language}</a
								>
							{/if}
							{#if comparison.other_gloss}
								<span class="comparison-gloss">‘{striptags(comparison.other_gloss)}’</span>
							{/if}
						</span>
						<span class="comparison-tail">
							<span
								class="confidence {comparison.confidence}"
								title="Confidence in the source's printed comparison, not a new editorial borrowing claim"
								>{comparison.confidence}</span
							>
							<span class="chev comparison-caret" aria-hidden="true"></span>
						</span>
					</summary>
					<div class="comparison-evidence etymology serif">
						<p>{comparison.evidence}</p>
						<span class="block-source"><ReferenceLink reference={comparison.reference} /></span>
					</div>
				</details>
			{/each}
		</div>
	</section>
{/if}
{#if entry.text_blocks?.length}
	{#each entry.text_blocks as block (block.position)}
		{@const reference = blockReference(block)}
		<section class="etymology serif" data-kind={block.kind}>
			{#if isKewaBlock(block) && block.format === 'html'}
				<CollapsibleSourceScan content={block.content} scanId={`kewa-scan-${entry.id}-${block.position}`} />
			{:else if block.format === 'markdown'}
				<div class="markdown">{@html md(block.content)}</div>
			{:else if block.format === 'text'}
				<p>{block.content}</p>
			{:else}
				{@html safe(block.content)}
			{/if}
			{#if reference}
				<span class="block-source"><ReferenceLink {reference} /></span>
			{/if}
		</section>
	{/each}
{:else if entry.etymology}
	<!-- Compatibility for databases built before structured text blocks were introduced. -->
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
	</details>
{/if}
	</div>
	{#if entryReferences.length || hasDescendants}
	<aside class="entry-context" aria-label="Sources and coverage">
		<div class="source-scopes" aria-label="Sources by information supplied">
			{#if entryReferences.length}
			<div class="source-scope" title="Sources for this headword, gloss, tags, and article text">
				<h2 class="source-scope-label">Entry sources</h2>
				<RefList references={entryReferences} />
			</div>
			{/if}
			{#if hasDescendants && reflexReferences.length}
			<div class="source-scope" title="Sources for the descendant and borrowed forms shown below">
				<h2 class="source-scope-label">Descendant sources</h2>
				<RefList references={reflexReferences} />
			</div>
			{/if}
		</div>
		{#if hasDescendants}
		<div class="entry-coverage">
			<h2 class="source-scope-label">Descendant coverage</h2>
			<p><strong>{filteredReflexes.length.toLocaleString()}</strong> reflexes <span aria-hidden="true">·</span> <strong>{langCount}</strong> {langCount === 1 ? 'language' : 'languages'}</p>
			<CladeBars clades={formSearch ? filteredReflexes.map((reflex) => reflex.lemma.language?.clade ?? '').join(',') : entry.clades} />
		</div>
		{/if}
	</aside>
	{/if}
</div>

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
			<a class="d-word phon" href="{base}/entries/{d.id}"><FormWord word={d.word} ocr={d.ocr} /></a>
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
{#if hasDescendants}
	<div class="toggle" role="tablist" aria-label="View">
		<button role="tab" aria-selected={view === 'normal'} class:on={view === 'normal'} onclick={() => (view = 'normal')}>Forms</button>
		<button role="tab" aria-selected={view === 'align'} class:on={view === 'align'} onclick={() => (view = 'align')}>Sound alignment</button>
		<button role="tab" aria-selected={view === 'concept'} class:on={view === 'concept'} onclick={() => (view = 'concept')}>Concepts</button>
	</div>
{/if}

<!-- alignment matrix -->
{#if loading}
	<div class="loader-line" style="margin:1.5rem 0"></div>
{:else if ea}
	{#if !hasDescendants}
	<section class="empty-descendants" aria-labelledby="empty-descendants-title">
		<h2 id="empty-descendants-title">No descendants recorded</h2>
		<p>Jambu has no descendant or borrowed forms recorded for this term.</p>
		<nav aria-label="Explore related entries">
			{#if origin}
				<a href="{base}/entries/{origin.id}">Explore origin <span class="phon"><FormWord word={origin.word || origin.id} ocr={origin.ocr} /></span> <span aria-hidden="true">→</span></a>
			{/if}
			{#if entry.language}
				<a href="{base}/languages/{entry.language.id}">Browse {entry.language.name} <span aria-hidden="true">→</span></a>
			{/if}
		</nav>
	</section>
	{:else}
	<p class="count muted" aria-live="polite">{filteredReflexes.length.toLocaleString()}{formSearch ? ` of ${ea.reflexes.length.toLocaleString()}` : ''} reflexes · {langCount} languages</p>
	{#if formSearch && !filteredReflexes.length}<p class="muted">No forms match “{formSearch}”. Clear the search to show all forms.</p>{/if}
	<div class="entry-body">
		<div class="matrix-col">
			<PageFormsSearch />
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
					{#if view === 'concept'}<th class="c-concepts">Concepts</th>{/if}
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
						onmouseenter={() => previewRow(row.r.lemma.id)}
						onmouseleave={() => previewRow(null)}
					>
						<td class="c-clade clade-cell">{row.firstClade ? row.clade : ''}</td>
						<td class="c-lang">
							{#if row.firstLang}<LangName lang={row.r.lemma.language} />{/if}
						</td>
						{#if view !== 'align'}
							<td class="c-form formcell">
								<span class="lemma-word"><FormWord word={row.r.lemma.word} references={row.r.lemma.references} /></span>{#if row.r.lemma.phonemic}
									<span class="phon">/{row.r.lemma.phonemic}/</span>{/if}{#if row.r.lemma.reflex_sub_count}&nbsp;<a class="refcount" href="{base}/entries/{row.r.lemma.id}" title="{row.r.lemma.reflex_sub_count} reflex(es) of this word">→&#8288;{row.r.lemma.reflex_sub_count}</a>{/if}{#if row.r.lemma.sub_count}&nbsp;<a class="subcount" href="{base}/entries/{row.r.lemma.id}" title="{row.r.lemma.sub_count} form(s) borrowed from this word">→&#8288;{row.r.lemma.sub_count}</a>{/if}
								{#each row.r.lemma.variants ?? [] as v (v.id)}<span class="rvar-line"
										><span class="rvar-arrow">→</span>&nbsp;<span class="rvar"
											><FormWord word={v.word} references={v.references} /></span
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
								><FormWord word={row.r.lemma.word} references={row.r.lemma.references} /></td
							>
						{/if}
						<td class="c-gloss gloss-cell"
							>{@html safe(row.r.lemma.gloss)}{#if row.r.lemma.tags}
								<Tags tags={row.r.lemma.tags} />{/if}{#if row.r.lemma.secondary}<span
									class="derived-badge"
									title="alternate etymology — this form's accepted etymon is another entry">alternate</span
								>{/if}</td
						>
						{#if view === 'concept'}
							<td class="c-concepts concept-cell">
								{#if row.r.concepts.length}
									{#each row.r.concepts as concept (concept.id)}
										<a
											class="concept-pill"
											style={`--concept-color:${conceptColors.get(concept.id) ?? '#8b8b8b'}`}
											title={concept.category}
											href={`${base}/concepts/${concept.id}`}>{concept.name}</a
										>
									{/each}
								{:else}<span class="faint">—</span>{/if}
							</td>
						{/if}
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

		{#if markers.length}
			<aside class="map-col" aria-label="Where these reflexes are attested">
				<div class="map-head">
					<h2>Distribution</h2>
					<p class="muted">
						{markers.length} location{markers.length === 1 ? '' : 's'} · {langCount}
						language{langCount === 1 ? '' : 's'}
					</p>
				</div>
				<MapView {markers} height="clamp(16rem, 44vh, 32rem)" />

				{#if view === 'concept'}
					<div class="concept-key">
						<div class="outcomes-head">
							<span class="corr-head">Concepts</span>
							{#if pinnedConcepts.length}
								<button class="clear" onclick={() => (pinnedConcepts = [])}>clear {pinnedConcepts.length}</button>
							{/if}
						</div>
						{#if conceptSummary.length}
							<div class="concept-options">
								{#each conceptSummary as concept (concept.id)}
									<button
										class="concept-option"
										class:on={pinnedConcepts.includes(concept.id)}
										class:off={activeConcepts.length > 0 && !activeConcepts.includes(concept.id)}
										style={`--concept-color:${conceptColors.get(concept.id)}`}
										aria-pressed={pinnedConcepts.includes(concept.id)}
										title={concept.category}
										onmouseenter={() => (hoverConcept = concept.id)}
										onmouseleave={() => (hoverConcept = null)}
										onfocus={() => (hoverConcept = concept.id)}
										onblur={() => (hoverConcept = null)}
										onclick={() => toggleConcept(concept.id)}
									>
										<span class="sw"></span>
										<span>{concept.name}</span>
										<span class="x">×{concept.count}</span>
									</button>
								{/each}
								{#if unmappedConceptCount}
									<span class="concept-unmapped"><span class="sw"></span>Unmapped <span class="x">×{unmappedConceptCount}</span></span>
								{/if}
							</div>
						{:else}
							<p class="map-cap muted">No concept assignments for these reflexes.</p>
						{/if}
					</div>
				{/if}

				<!-- with a column selected the correspondence becomes a picker: the swatches are the
				     map's own colours, so clicking one isolates where that outcome happens -->
				{#if view === 'align' && selected != null && correspondence.length}
					<div class="outcomes">
						<div class="outcomes-head">
							<span class="corr-head">*{selSeg} →</span>
							{#if pinnedOut.length}
								<button class="clear" onclick={() => (pinnedOut = [])}>clear {pinnedOut.length}</button>
							{/if}
						</div>
						{#each correspondence as c (c.seg + c.change)}
							{@const info = changeInfo(c.change)}
							{@const seg = c.seg || '∅'}
							<button
								class="outcome {info.cls}"
								class:on={pinnedOut.includes(seg)}
								class:off={activeOut.length > 0 && !activeOut.includes(seg)}
								style="--c:{outcomeColors.get(seg)}"
								aria-pressed={pinnedOut.includes(seg)}
								title={c.langs.join(', ')}
								onmouseenter={() => (hoverOut = seg)}
								onmouseleave={() => (hoverOut = null)}
								onfocus={() => (hoverOut = seg)}
								onblur={() => (hoverOut = null)}
								onclick={() => toggleOut(seg)}
							>
								<span class="sw"></span>
								<b>{seg}</b>
								<span class="corr-name">{info.name}</span>
								<span class="x">×{c.count}</span>
							</button>
						{/each}
					</div>
				{:else if view === 'align'}
					<p class="map-cap muted">Select a column in the table to map its outcomes.</p>
				{/if}
			</aside>
		{/if}
	</div>
	{/if}
{/if}

<style>
	.empty-descendants {
		margin: 1.5rem 0;
		padding: 1.1rem 1.25rem;
		border: 1px solid var(--border);
		border-radius: 9px;
		background: var(--surface);
	}
	.empty-descendants h2 {
		margin: 0;
		font-size: 1rem;
	}
	.empty-descendants p {
		margin: 0.4rem 0 0;
		color: var(--muted);
		font-size: 0.9rem;
	}
	.empty-descendants nav {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem 1.5rem;
		margin-top: 0.85rem;
		font-size: 0.85rem;
	}
	.cross-family {
		margin: 0.8rem 0 1rem;
		border: 1px solid color-mix(in srgb, var(--berry) 28%, var(--border));
		border-radius: 9px;
		background: color-mix(in srgb, var(--plum-2) 4%, var(--surface));
		overflow: hidden;
	}
	.cross-family h2 {
		margin: 0;
		padding: 0.42rem 0.7rem;
		border-bottom: 1px solid var(--border);
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.72rem;
		font-variant: small-caps;
		letter-spacing: 0.07em;
	}
	.comparison-list { display: grid; }
	.comparison-row {
		padding: 0.55rem 0.7rem 0.65rem;
	}
	.comparison-row + .comparison-row { border-top: 1px solid var(--border); }
	.comparison-head, .comparison-main {
		display: flex;
		align-items: baseline;
		gap: 0.42rem;
		min-width: 0;
	}
	.comparison-head {
		justify-content: space-between;
		cursor: pointer;
		list-style: none;
	}
	.comparison-head::-webkit-details-marker { display: none; }
	.comparison-main { flex-wrap: wrap; }
	.comparison-tail {
		display: inline-flex;
		flex: 0 0 auto;
		align-items: center;
		gap: 0.38rem;
	}
	.comparison-caret {
		color: var(--faint);
		transform: rotate(-45deg); /* points right while closed */
	}
	.comparison-row[open] .comparison-caret { transform: rotate(45deg); }
	.comparison-relation, .comparison-language, .comparison-gloss {
		color: var(--muted);
		font-size: 0.82rem;
	}
	.comparison-word { font-size: 1.02rem; font-weight: 600; }
	.confidence {
		padding: 0.08rem 0.35rem;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		color: var(--muted);
		font-size: 0.65rem;
		white-space: nowrap;
	}
	.confidence.high {
		color: #23704a;
		border-color: color-mix(in srgb, #23704a 45%, var(--border));
		background: color-mix(in srgb, #23704a 9%, var(--surface));
	}
	.confidence.medium {
		color: color-mix(in srgb, #a76b0d 90%, var(--ink));
		border-color: color-mix(in srgb, #b97812 50%, var(--border));
		background: color-mix(in srgb, #e8a62a 11%, var(--surface));
	}
	.confidence.low {
		color: color-mix(in srgb, #a64955 88%, var(--ink));
		border-color: color-mix(in srgb, #a64955 42%, var(--border));
		background: color-mix(in srgb, #a64955 8%, var(--surface));
	}
	.cross-family .comparison-evidence {
		margin: 0.42rem 0 0.05rem 0.85rem;
		padding: 0.55rem 0.75rem;
		font-size: 0.86rem;
		line-height: 1.45;
	}
	.comparison-evidence p { margin: 0; }
	@media (max-width: 760px) {
		.comparison-head { align-items: flex-start; }
		.cross-family .comparison-evidence { margin-left: 0.35rem; }
	}
	:global(.map-ocr) {
		display: inline-block;
		margin-left: 0.25rem;
		padding: 0.02rem 0.28rem;
		border: 1px solid color-mix(in srgb, #b97812 55%, transparent);
		border-radius: 999px;
		background: color-mix(in srgb, #e8a62a 16%, var(--surface));
		color: color-mix(in srgb, #8b5708 88%, var(--ink));
		font-family: var(--font-sans);
		font-size: 0.56rem;
		font-weight: 700;
		letter-spacing: 0.05em;
		vertical-align: middle;
	}
	:global(.map-concepts) {
		display: block;
		margin-top: 0.15rem;
		color: var(--muted);
		font-size: 0.72rem;
	}
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
	.entry-intro {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(250px, 310px);
		align-items: start;
		gap: 2.5rem;
		margin: 1.5rem 0;
		padding-bottom: 1.5rem;
		border-bottom: 1px solid var(--border);
	}
	.entry-summary,
	.entry-context {
		min-width: 0;
	}
	.entry-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		margin-top: 0;
	}
	.entry-context :global(.clades) {
		justify-content: flex-start;
		flex-wrap: wrap;
		margin: 0.65rem 0 0;
	}
	.entry-context {
		border-left: 1px solid var(--border);
		padding-left: 1.25rem;
	}
	.entry-eyebrow {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.4rem 0.9rem;
		font-size: 0.85rem;
	}
	.entry-eyebrow a { font-weight: 600; }
	.entry-id {
		color: var(--muted);
		font-size: 0.7rem;
		overflow-wrap: anywhere;
	}
	.headword {
		margin: 0.45rem 0 0.35rem;
		font-size: clamp(2.2rem, 4vw, 3rem);
		line-height: 1.15;
		overflow-wrap: anywhere;
	}
	.entry-pronunciation {
		margin: 0.3rem 0;
		color: var(--muted);
		font-size: 1rem;
	}
	.entry-tags { margin: 0.55rem 0; }
	.entry-ancestry {
		margin: 1.1rem 0 0.8rem;
		padding-left: 0.85rem;
		border-left: 2px solid var(--border-strong);
	}
	.entry-coverage {
		margin-top: 1.15rem;
	}
	.entry-coverage p {
		margin: 0.4rem 0 0;
		font-size: 0.82rem;
		color: var(--muted);
	}
	.entry-coverage strong { color: var(--ink); }
	.entry-coverage p span { margin: 0 0.25rem; }
	.entry-title {
		min-width: 0;
	}
	.source-scopes {
		display: grid;
		align-items: start;
		gap: 1rem;
		font-family: var(--font-sans);
	}
	.source-scope {
		display: grid;
		align-content: start;
		gap: 0.45rem;
	}
	.source-scope-label {
		margin: 0;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.68rem;
		text-transform: uppercase;
		font-weight: 600;
		letter-spacing: 0.08em;
	}
	.gloss {
		font-size: 1.2rem;
		line-height: 1.5;
		margin: 0.4rem 0 0.5rem;
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
	.block-source {
		display: block;
		margin-top: 0.45rem;
		font-family: var(--font-sans);
		font-size: 0.72rem;
		color: var(--muted);
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
	.entry-evidence {
		margin: 0.7rem 0;
		border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
	}
	.entry-evidence > summary {
		padding: 0.65rem 0;
		color: var(--plum-2);
		font-size: 0.88rem;
		font-weight: 600;
		cursor: pointer;
	}
	.entry-evidence[open] { padding-bottom: 0.8rem; }
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
	/* "derived" marker on a secondary reflex (reached via an alternate-etymology derivation edge) */
	.derived-badge {
		display: inline-block;
		margin-left: 0.35rem;
		padding: 0 0.4em;
		border-radius: 999px;
		font-size: 0.66rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		background: transparent;
		border: 1px solid color-mix(in srgb, var(--berry) 50%, transparent);
		color: var(--berry);
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
	.c-concepts {
		min-width: 10rem;
	}
	.concept-cell {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem;
	}
	.concept-pill {
		display: inline-flex;
		align-items: center;
		padding: 0.12rem 0.42rem;
		border: 1px solid color-mix(in srgb, var(--concept-color) 58%, var(--border));
		border-radius: 999px;
		background: color-mix(in srgb, var(--concept-color) 13%, var(--surface));
		color: color-mix(in srgb, var(--concept-color) 72%, var(--ink));
		font-size: 0.72rem;
		font-weight: 600;
		line-height: 1.25;
		text-decoration: none;
		white-space: nowrap;
	}
	.concept-pill:hover {
		background: color-mix(in srgb, var(--concept-color) 22%, var(--surface));
	}

	/* ---- the outcomes of the selected column, as a picker beneath the map ----
	   Same grammar as the atlas lists: a swatch that is literally the map's colour, the thing
	   itself, what it is called, how many. Clicking isolates it; hovering previews. */
	.outcomes {
		display: grid;
		gap: 2px;
		margin-top: 0.5rem;
		max-height: 30vh;
		overflow-y: auto;
		scrollbar-width: thin;
		scrollbar-color: var(--border-strong) transparent;
	}
	.outcomes-head {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		padding: 0 0.15rem 0.2rem;
	}
	.corr-head {
		font-family: var(--font-phon);
		font-size: 1.05rem;
		font-weight: 600;
	}
	.outcome {
		display: grid;
		grid-template-columns: auto auto minmax(0, 1fr) auto;
		align-items: baseline;
		gap: 0.45rem;
		padding: 0.25rem 0.45rem;
		border: 1.5px solid transparent;
		border-radius: 8px;
		background: none;
		color: var(--ink);
		font: inherit;
		font-size: 0.8rem;
		text-align: left;
		cursor: pointer;
		transition: background 120ms ease, border-color 120ms ease, opacity 120ms ease;
	}
	.outcome:hover {
		border-color: var(--c);
		background: color-mix(in srgb, var(--c) 12%, transparent);
	}
	.outcome.on {
		border-color: var(--c);
		background: color-mix(in srgb, var(--c) 22%, transparent);
	}
	/* not in the current selection: still listed, but stood down like its points on the map */
	.outcome.off {
		opacity: 0.4;
	}
	.outcome:focus-visible {
		outline: 2px solid var(--c);
		outline-offset: -2px;
	}
	.outcome b {
		font-family: var(--font-phon);
		font-size: 0.98rem;
	}
	.outcome .sw {
		align-self: center;
		width: 10px;
		height: 10px;
		border-radius: 50%;
		border: 1px solid rgba(0, 0, 0, 0.25);
		background: var(--c);
		flex-shrink: 0;
	}
	.outcome .x {
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.corr-name {
		font-size: 0.68rem;
		color: var(--muted);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
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
	.concept-key {
		display: grid;
		gap: 0.2rem;
		margin-top: 0.55rem;
		max-height: 30vh;
		overflow-y: auto;
		scrollbar-width: thin;
	}
	.concept-options {
		display: grid;
		gap: 2px;
	}
	.concept-option,
	.concept-unmapped {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.45rem;
		padding: 0.28rem 0.45rem;
		border: 1.5px solid transparent;
		border-radius: 8px;
		background: none;
		color: var(--ink);
		font: inherit;
		font-size: 0.8rem;
		text-align: left;
	}
	.concept-option {
		cursor: pointer;
		transition: background 120ms ease, border-color 120ms ease, opacity 120ms ease;
	}
	.concept-option:hover,
	.concept-option.on {
		border-color: var(--concept-color);
		background: color-mix(in srgb, var(--concept-color) 16%, transparent);
	}
	.concept-option.off { opacity: 0.4; }
	.concept-option:focus-visible {
		outline: 2px solid var(--concept-color);
		outline-offset: -2px;
	}
	.concept-option .sw,
	.concept-unmapped .sw {
		width: 10px;
		height: 10px;
		border: 1px solid rgba(0, 0, 0, 0.25);
		border-radius: 50%;
		background: var(--concept-color, #8b8b8b);
	}
	.concept-option .x,
	.concept-unmapped .x {
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.concept-unmapped { color: var(--muted); }

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
		padding: 0.3rem 0.55rem; /* inline padding matches table.aln td */
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
	/* `table.aln th` sets text-align, so the centred columns need to out-specify it or their
	   headers drift left of the cells they label */
	table.aln th.c-seg,
	table.aln th.c-cog {
		text-align: center;
	}
	/* tighter gutters on the segment columns, header and cells in step */
	table.aln th.c-seg,
	table.aln td.c-seg {
		padding-inline: 0.3rem;
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
	.map-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.75rem;
		margin-bottom: 0.4rem;
	}
	.map-head h2 {
		margin: 0;
		font-size: 1.05rem;
	}
	.map-head p {
		margin: 0;
		font-size: 0.78rem;
		text-align: right;
	}
	.map-cap {
		font-size: 0.78rem;
		text-align: center;
		margin-top: 0.45rem;
	}
	@media (max-width: 900px) {
		.entry-intro {
			grid-template-columns: 1fr;
			gap: 1.25rem;
		}
		.entry-context {
			border-left: 0;
			padding: 1rem 0 0;
			border-top: 1px solid var(--border);
		}
		.source-scopes {
			grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		}
		.entry-context :global(.clades) {
			justify-content: flex-start;
			margin-top: 0;
		}
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
		.map-head {
			display: block;
		}
		.map-head p {
			margin-top: 0.15rem;
			text-align: left;
		}
		.entry-context :global(.clades) {
			width: 100%;
			flex-wrap: wrap;
		}
	}
	/* "also proposed" alternate-etymology line under the ancestry chain */
	.alternates {
		margin: 0.15rem 0 0;
		font-size: 0.9rem;
		color: var(--ink-muted);
	}
	.alt-label {
		font-variant: small-caps;
		letter-spacing: 0.04em;
		margin-right: 0.4rem;
	}
	.alt-review {
		display: inline-block;
		border: 1px solid var(--ink-faint);
		border-radius: 50%;
		width: 1em;
		height: 1em;
		line-height: 1em;
		text-align: center;
		font-size: 0.75em;
		vertical-align: super;
	}
</style>
