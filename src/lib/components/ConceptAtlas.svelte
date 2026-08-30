<script lang="ts">
	import { base } from '$app/paths';
	import GeoMap from '$lib/components/Map.svelte';
	import AtlasShell from '$lib/components/AtlasShell.svelte';
	import PanelToggle from '$lib/components/PanelToggle.svelte';
	import { activePoint, mutedPoint, pieMarker, plainPoint, HISTORICAL_MARKER } from '$lib/atlas';
	import { cladeColor } from '$lib/clades';
	import { etymonSlotColor, ETYMON_PALETTE } from '$lib/etyma';
	import { ETYMOLOGY_GUESS_THRESHOLD } from '$lib/etymologyGuess';
	import { safe, striptags } from '$lib/render';
	import type { MapMarker } from '$lib/types';
	import type { ConceptDetail, ConceptAttestation } from '$lib/types';
	import FormWord from '$lib/components/FormWord.svelte';
	import ConceptPicker from '$lib/components/ConceptPicker.svelte';
	import Tooltip from '$lib/components/Tooltip.svelte';

	let { detail }: { detail: ConceptDetail } = $props();
	const concept = $derived(detail.concept);
	const etyma = $derived(detail.etyma);
	const unetym = $derived(detail.unetym);
	let useBestGuesses = $state(false);
	const guessedCount = $derived(unetym.filter((form) => !!form.best_guess).length);
	const shownEtyma = $derived.by(() =>
		etyma.map((etymon) => ({
			...etymon,
			forms: useBestGuesses
				? [
						...etymon.forms,
						...unetym.filter((form) => form.best_guess?.etymon === etymon.etymon)
					]
				: etymon.forms
		}))
	);
	const shownUnetym = $derived(
		useBestGuesses ? unetym.filter((form) => !form.best_guess) : unetym
	);

	// Unetymologised forms are selectable like an etymon, but they are not one: they get a slate
	// that sits outside ETYMON_PALETTE so a grey point never reads as somebody's reconstruction.
	const UNETYM = '__unetym__';
	const UNETYM_COLOR = '#6b7280';
	// the shape the languages atlas and the isogloss map already use for historical and
	// reconstructed languages; Map.svelte recolours the polygon fill to the point's colour
	const languageCount = (forms: ConceptAttestation[]) =>
		new Set(
			forms
				.map((form) => form.language_id ?? form.language)
				.filter((language): language is string => !!language)
		).size;

	// selector entries in db order (most attesting languages first), each with its slot colour
	// and that language count
	const legend = $derived(
		shownEtyma.map((e, i) => ({
			etymon: e.etymon,
			word: e.word,
			gloss: e.gloss,
			source: e.source,
			language: e.language,
			clade: e.clade,
			ocr: e.ocr,
			color: etymonSlotColor(i),
			langs: languageCount(e.forms),
			forms: e.forms,
			isUnetym: false
		}))
	);
	const unetymEntry = $derived(
		shownUnetym.length
			? {
					etymon: UNETYM,
					word: 'Unetymologised',
					gloss: 'attested with this meaning, not yet linked to an etymon',
					source: '',
					language: null,
					clade: null,
					ocr: false as boolean | number | undefined,
					color: UNETYM_COLOR,
					langs: languageCount(shownUnetym),
					forms: shownUnetym,
					isUnetym: true
				}
			: null
	);
	const entries = $derived(unetymEntry ? [...legend, unetymEntry] : legend);
	const wordOf = $derived(new Map(entries.map((l) => [l.etymon, l.word])));

	// etyma highlighted on the map: pinned (clicked) plus a transient hover/focus preview
	const DEFAULT_PINS = 4; // the leading etyma, pinned on load so the map opens on a real contrast
	let pinned = $state<string[]>([]);
	let pinnedFor = $state<number | null>(null);
	let hovered = $state<string | null>(null);
	let search = $state('');
	let listOpen = $state(true);
	let conceptOpen = $state(true);
	// reflexes are folded away until asked for: the list is a picker first, and a concept can
	// carry dozens of etyma. Pinning (what the map draws) is deliberately separate from opening.
	let expanded = $state<string[]>([]);

	// Reset to the default selection whenever the concept changes — this component is reused
	// across concept navigations, so carrying pinned ids over would dim the whole next map.
	$effect(() => {
		if (pinnedFor !== concept.id) {
			pinnedFor = concept.id;
			pinned = legend.slice(0, DEFAULT_PINS).map((l) => l.etymon);
			expanded = [];
			search = '';
			useBestGuesses = false;
		}
	});
	const active = $derived(hovered && !pinned.includes(hovered) ? [...pinned, hovered] : pinned);
	function toggle(etymon: string) {
		pinned = pinned.includes(etymon) ? pinned.filter((e) => e !== etymon) : [...pinned, etymon];
	}
	function toggleOpen(etymon: string) {
		expanded = expanded.includes(etymon)
			? expanded.filter((e) => e !== etymon)
			: [...expanded, etymon];
	}
	function setBestGuesses(enabled: boolean) {
		useBestGuesses = enabled;
		if (enabled && unetym.every((form) => !!form.best_guess)) {
			pinned = pinned.filter((etymon) => etymon !== UNETYM);
			expanded = expanded.filter((etymon) => etymon !== UNETYM);
		}
	}

	// The concept's whole corpus as one stacked bar, in the same rank order as the list. It is a
	// second reading of the same selection: a highlighted etymon shows in its map colour, the
	// rest fall back to the empty-track grey, so the bar answers "how much of this concept does
	// what I've picked account for?" at a glance.
	const barTotal = $derived(entries.reduce((n, l) => n + l.forms.length, 0));
	const barSegs = $derived(
		entries
			.filter((l) => l.forms.length)
			.map((l) => ({
				etymon: l.etymon,
				word: l.word,
				isUnetym: l.isUnetym,
				n: l.forms.length,
				pct: barTotal ? (100 * l.forms.length) / barTotal : 0,
				on: active.includes(l.etymon),
				color: activeColor.get(l.etymon) ?? l.color
			}))
	);
	// A segment can be two pixels wide, so the native title tooltip — slow to appear and
	// impossible to aim at — is not enough. Follow the same hover popover the correspondence
	// bars use, with a short close delay so crossing between segments does not flicker.
	type BarSeg = (typeof barSegs)[number];
	let pop = $state<{ el: HTMLElement; seg: BarSeg } | null>(null);
	let popTimer: ReturnType<typeof setTimeout>;
	function enterSeg(e: Event, seg: BarSeg) {
		clearTimeout(popTimer);
		pop = { el: e.currentTarget as HTMLElement, seg };
		hovered = seg.etymon;
	}
	function leaveSeg() {
		popTimer = setTimeout(() => (pop = null), 120);
		hovered = null;
	}

	const pinnedShare = $derived(
		barTotal
			? Math.round(
					(100 * barSegs.filter((b) => pinned.includes(b.etymon)).reduce((n, b) => n + b.n, 0)) /
						barTotal
				)
			: 0
	);

	const filtered = $derived.by(() => {
		const needle = search.trim().toLocaleLowerCase();
		if (!needle) return legend;
		return legend.filter((l) =>
			[l.word, l.etymon, striptags(l.gloss ?? ''), l.source].some((field) =>
				(field ?? '').toLocaleLowerCase().includes(needle)
			)
		);
	});

	// Rank colours cycle every 8 slots, so two highlighted etyma far apart in rank can collide.
	// Give each active etymon its rank colour when free, else the next unused slot — chips read
	// from this too, so the selector and the map never disagree about what a colour means.
	const activeColor = $derived.by(() => {
		const used = new Set<string>();
		const out = new Map<string, string>();
		for (const e of active) {
			const entry = entries.find((l) => l.etymon === e);
			if (!entry) continue;
			if (entry.isUnetym) {
				out.set(e, UNETYM_COLOR);
				continue;
			}
			let c = entry.color;
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


	// one uniform-size marker per attesting place — a dialect point where the form is tagged with a
	// located dialect, else the language's own point. With nothing highlighted the map shows plain
	// coverage; highlighting an entry recolours its places (ring) and dims the rest.
	const markers = $derived.by((): MapMarker[] => {
		const byPlace = new Map<
			string,
			{
				name: string;
				lat: number;
				long: number;
				historical: boolean;
				counts: Map<string, number>;
				forms: Map<string, ConceptAttestation[]>;
			}
		>();
		const bump = (f: ConceptAttestation, etymon: string) => {
			for (const p of f.places) {
				let m = byPlace.get(p.key);
				if (!m)
					byPlace.set(
						p.key,
						(m = {
							name: p.name,
							lat: p.lat,
							long: p.long,
							historical: !!f.historical,
							counts: new Map(),
							forms: new Map()
						})
					);
				m.counts.set(etymon, (m.counts.get(etymon) ?? 0) + 1);
				const forms = m.forms.get(etymon) ?? [];
				forms.push(f);
				m.forms.set(etymon, forms);
			}
		};
		for (const e of shownEtyma) for (const f of e.forms) bump(f, e.etymon);
		for (const f of shownUnetym) bump(f, UNETYM);
		return [...byPlace.values()].map((m) => {
			const entries = [...m.counts.entries()].sort(
				(a, b) => Number(active.includes(b[0])) - Number(active.includes(a[0])) || b[1] - a[1]
			);
			const total = entries.reduce((sum, [, n]) => sum + n, 0);
			const details = entries.slice(0, 6).map(([e, n]) => {
				const words = [...new Set((m.forms.get(e) ?? []).map((f) => tooltipText(f.word || f.form_id)))];
				const examples = words.slice(0, 3).join(', ');
				const rest = words.length > 3 ? `, +${words.length - 3} more` : '';
				return `<br><strong>${tooltipText(wordOf.get(e) ?? e)}</strong> (${n}): ${examples}${rest}`;
			});
			if (entries.length > 6) details.push(`<br>+${entries.length - 6} more etyma`);
			const base = {
				lat: m.lat,
				long: m.long,
				svg: '',
				tooltip: `<strong>${tooltipText(m.name)}</strong><br>${total} ${total === 1 ? 'attestation' : 'attestations'} · ${entries.length} ${entries.length === 1 ? 'etymon' : 'etyma'}${details.join('')}`
			};
			const matches = active.filter((e) => m.counts.has(e)).map((e) => activeColor.get(e)!);
			// a historical or reconstructed language is drawn as a rhombus, a living one as a
			// circle — except where a place attests several highlighted etyma and the split pie
			// has to carry the colours instead
			const shape = m.historical ? HISTORICAL_MARKER : '';
			if (!active.length) return { ...base, svg: shape, ...plainPoint() };
			if (!matches.length) return { ...base, svg: shape, ...mutedPoint() };
			if (matches.length === 1) return { ...base, svg: shape, ...activePoint(matches[0]) };
			return { ...base, svg: pieMarker(matches.map((color) => ({ color, n: 1 }))), foreground: true };
		});
	});

	// reflexes read better grouped by language than as one long undifferentiated list
	function byLanguage(forms: ConceptAttestation[]) {
		const groups = new Map<
			string,
			{
				language: string;
				id: string | null;
				clade: string | null;
				historical: boolean;
				forms: ConceptAttestation[];
			}
		>();
		for (const f of forms) {
			const key = f.language_id ?? f.language ?? '—';
			let g = groups.get(key);
			if (!g)
				groups.set(
					key,
					(g = {
						language: f.language ?? '—',
						id: f.language_id,
						clade: f.clade,
						historical: !!f.historical,
						forms: []
					})
				);
			g.forms.push(f);
		}
		// historical stages first: a reflex list reads as a descent, oldest attestation down
		return [...groups.values()].sort(
			(a, b) => Number(b.historical) - Number(a.historical)
		);
	}
</script>

{#snippet row(l: (typeof entries)[number])}
	{@const isOpen = expanded.includes(l.etymon)}
	{@const isPinned = pinned.includes(l.etymon)}
	<div class="row" class:pinned={isPinned} class:open={isOpen} style="--c: {chipColor(l.etymon, l.color)}">
		<!-- picking is what the map draws; opening is what you read. Two jobs, two controls. -->
		<button
			class="pick"
			class:unetym={l.isUnetym}
			aria-pressed={isPinned}
			title={isPinned ? 'Remove from the map' : 'Show on the map'}
			onmouseenter={() => (hovered = l.etymon)}
			onmouseleave={() => (hovered = null)}
			onfocus={() => (hovered = l.etymon)}
			onblur={() => (hovered = null)}
			onclick={() => toggle(l.etymon)}
		>
			<span class="dot"></span>
			<span class="word">
				{#if l.isUnetym}Unetymologised{:else}<FormWord word={l.word} ocr={l.ocr} />{/if}
			</span>
			<span class="count">{l.langs}</span>
			{#if l.gloss || l.language}
				<span class="gloss">
					{#if l.language}<span class="elang" style="--lc: {cladeColor(l.clade)}">{l.language}</span
						>{/if}{#if l.gloss}{@html safe(l.gloss)}{/if}
				</span>
			{/if}
		</button>
		<button
			class="disclose"
			aria-expanded={isOpen}
			title={isOpen ? 'Hide reflexes' : `Show ${l.forms.length} reflexes`}
			onclick={() => toggleOpen(l.etymon)}
		>
			<span class="chev" class:right={!isOpen} aria-hidden="true"></span>
		</button>
	</div>

	{#if isOpen}
		{@const groups = byLanguage(l.forms)}
		<div class="detail" style="--c: {chipColor(l.etymon, l.color)}">
			<div class="detail-head">
				{#if !l.isUnetym}
					<a class="detail-link" href="{base}/entries/{l.etymon}">{l.etymon}</a>
				{/if}
				<span class="detail-meta">{groups.length} lang · {l.forms.length} forms</span>
			</div>
			<ul class="reflexes">
				{#each groups as g (g.id ?? g.language)}
					<li class:historical={g.historical} style="--clade: {cladeColor(g.clade)}">
						<span class="rlang">
							{#if g.historical}<span
									class="hist"
									title="historical or reconstructed language"
									aria-label="historical or reconstructed">◆</span
								>{/if}{#if g.id}<a href="{base}/languages/{g.id}">{g.language}</a>{:else}{g.language}{/if}
						</span>
						<span class="rforms">
							{#each g.forms as f (f.form_id)}
								<span class="rform">
									<a href="{base}/reflexes/{f.form_id}"><FormWord word={f.word} ocr={f.ocr} /></a>
									{#if useBestGuesses && f.best_guess}
										<span
											class="guess-badge"
											title={`Best guess: ${Math.round(f.best_guess.similarity * 100)}% sound similarity to ${f.best_guess.matched_word}`}
											>best guess {Math.round(f.best_guess.similarity * 100)}%</span
										>
									{/if}
									{#if f.gloss}<span class="rgloss">{@html safe(f.gloss)}</span>{/if}
								</span>
							{/each}
						</span>
					</li>
				{/each}
			</ul>
		</div>
	{/if}
{/snippet}

{#snippet map()}
	<!-- the concept panel owns the top-left corner, so the zoom sits opposite the attribution -->
	<GeoMap {markers} zoom={4} height="100%" fitOnce mutedTiles flush zoomPosition="bottomleft" scrollZoom />
{/snippet}

<!-- left: which concept you are looking at, and the way to change it -->
{#snippet left()}
		<div class="crumb-head">
			<nav class="crumbs"><a href="{base}/concepts/browse">All concepts</a></nav>
			<PanelToggle open={conceptOpen} side="left" label="the concept panel" onclick={() => (conceptOpen = !conceptOpen)} />
		</div>
		<h1><ConceptPicker current={concept} large /></h1>
		{#if conceptOpen}
			<dl class="stats">
				<!-- counted from the grouped etyma rather than the precomputed column, which still
				     counts an alternate form's target as an etymon of its own -->
				<div><dt>Etyma</dt><dd>{legend.length.toLocaleString()}</dd></div>
				<div><dt>Langs</dt><dd>{concept.lang_count.toLocaleString()}</dd></div>
				<div><dt>Forms</dt><dd>{concept.form_count.toLocaleString()}</dd></div>
			</dl>

			<div class="dist">
				<div class="cbar" role="group" aria-label="Distribution of forms across etyma">
					{#each barSegs as b (b.etymon)}
						<button
							class="cseg"
							class:on={b.on}
							class:unetym={b.isUnetym}
							style="width: {b.pct}%; --c: {b.color}"
							aria-pressed={pinned.includes(b.etymon)}
							aria-label="{b.isUnetym ? 'Unetymologised' : b.word} — {b.n} {b.n === 1
								? 'form'
								: 'forms'}"
							onmouseenter={(e) => enterSeg(e, b)}
							onmouseleave={leaveSeg}
							onfocus={(e) => enterSeg(e, b)}
							onblur={leaveSeg}
							onclick={() => toggle(b.etymon)}
						></button>
					{/each}
				</div>
				<p class="dist-key">
					{#if pinned.length}
						<b>{pinnedShare}%</b> of forms in {pinned.length}
						{pinned.length === 1 ? 'selection' : 'selections'}
					{:else}
						Distribution of {barTotal.toLocaleString()} forms
					{/if}
				</p>
			</div>
		{/if}
{/snippet}

<!-- right: the etyma, as a picker that opens out into reflexes -->
{#snippet right()}
		<div class="panel-head">
			<PanelToggle open={listOpen} side="right" label="the etymon panel" onclick={() => (listOpen = !listOpen)} />
			<h2>{legend.length.toLocaleString()} etyma</h2>
			{#if pinned.length}
				<button class="clear" onclick={() => (pinned = [])} title="Clear the map selection"
					>clear {pinned.length}</button
				>
			{/if}
		</div>

		{#if listOpen}
			<div class="controls">
				<input class="search" placeholder="Filter etyma…" bind:value={search} />
				{#if guessedCount}
					<button
						class="guess-toggle"
						class:on={useBestGuesses}
						aria-pressed={useBestGuesses}
						title={`Group ${guessedCount} unetymologised ${guessedCount === 1 ? 'form' : 'forms'} with the closest etyma already attested here when sound similarity is at least ${Math.round(ETYMOLOGY_GUESS_THRESHOLD * 100)}%`}
						onclick={() => setBestGuesses(!useBestGuesses)}
					>
						Best guess <span>{guessedCount}</span>
					</button>
				{/if}
			</div>
			<p class="hint">
				{#if useBestGuesses}
					Suggested forms are grouped only with etyma already attested for this concept at ≥{Math.round(ETYMOLOGY_GUESS_THRESHOLD * 100)}% sound similarity.
				{:else}
					Click an etymon to map it — pin several to compare. Open one to read its reflexes.
				{/if}
				<span class="key">◆ historical or reconstructed · ● living</span>
			</p>

			<div class="list" role="group" aria-label="Etyma expressing this concept">
				{#each filtered as l (l.etymon)}
					{@render row(l)}
				{:else}
					<p class="empty">No etymon matches “{search}”.</p>
				{/each}
			</div>

			{#if unetymEntry}
				<div class="foot">{@render row(unetymEntry)}</div>
			{/if}
		{/if}
{/snippet}

<AtlasShell {map} {left} {right} leftOpen={conceptOpen} rightOpen={listOpen} />

{#if pop}
	{@const seg = pop.seg}
	{@const entry = entries.find((l) => l.etymon === seg.etymon)}
	<!-- below the bar: the panel header sits directly above it, and covering the concept you are
	     looking at to describe one of its etyma reads badly -->
	<Tooltip
		anchor={pop.el}
		prefer="below"
		onenter={() => clearTimeout(popTimer)}
		onleave={leaveSeg}
	>
		<div class="pop-head">
			<span class="sw" class:hatched={seg.isUnetym} style="background:{seg.color}"></span>
			<b>
				{#if seg.isUnetym}Unetymologised{:else}<FormWord word={seg.word} ocr={entry?.ocr} />{/if}
			</b>
			<span class="pop-n">{seg.n.toLocaleString()}</span>
		</div>
		<div class="pop-sub">
			{#if entry?.language}<span class="pop-lang" style="--lc: {cladeColor(entry.clade)}"
					>{entry.language}</span
				>{/if}{seg.pct.toFixed(1)}% of forms · {entry?.langs ?? 0}
			{(entry?.langs ?? 0) === 1 ? 'language' : 'languages'}
		</div>
		{#if entry?.gloss}<div class="pop-gloss">{@html safe(entry.gloss)}</div>{/if}
		<div class="pop-hint">{pinned.includes(seg.etymon) ? 'click to unpin' : 'click to map'}</div>
	</Tooltip>
{/if}

<style>

	/* ---- the floating panels --------------------------------------------- */
	/* Both sit over the map rather than beside it, so the map keeps the whole viewport and each
	   can be folded away when you want the geography bare.
	   No backdrop-filter on either: it would make them containing blocks for position:fixed,
	   stranding the concept picker's dropdown off-screen. */

	/* the concept itself: the largest thing on the screen after the map */




	/* ---- the concept's distribution bar ---------------------------------- */
	.dist {
		padding: 0 0.95rem 0.75rem;
	}
	.cbar {
		display: flex;
		height: 16px;
		border-radius: 3px;
		overflow: hidden;
		background: var(--border);
	}
	.cseg {
		display: block;
		height: 100%;
		min-width: 2px;
		padding: 0;
		border: 0;
		/* unhighlighted segments sit back as an empty track so the picked ones carry the colour */
		background: var(--clade-empty);
		cursor: pointer;
		transition: background 120ms ease, filter 120ms ease;
	}
	.cseg.unetym {
		background: repeating-linear-gradient(
			45deg,
			var(--clade-empty),
			var(--clade-empty) 3px,
			transparent 3px,
			transparent 6px
		);
	}
	.cseg.on {
		background: var(--c);
	}
	.cseg:hover {
		filter: brightness(1.15) saturate(1.25);
	}
	.cseg:focus-visible {
		outline: 2px solid var(--plum-2);
		outline-offset: 1px;
	}
	.dist-key {
		margin: 0.35rem 0 0;
		color: var(--muted);
		font-size: 0.7rem;
		line-height: 1.35;
	}
	.dist-key b {
		color: var(--ink);
		font-variant-numeric: tabular-nums;
	}

	.pop-head {
		display: flex;
		align-items: baseline;
		gap: 0.4rem;
	}
	.pop-head b {
		font-family: var(--font-phon);
		font-size: 1.02rem;
	}
	.sw {
		flex: none;
		align-self: center;
		width: 11px;
		height: 11px;
		border-radius: 50%;
		border: 1px solid rgba(0, 0, 0, 0.25);
	}
	.sw.hatched {
		background: repeating-linear-gradient(
			45deg,
			var(--clade-empty),
			var(--clade-empty) 2px,
			transparent 2px,
			transparent 4px
		) !important;
	}
	.pop-n {
		margin-left: auto;
		color: var(--muted);
		font-size: 0.85rem;
		font-variant-numeric: tabular-nums;
	}
	.pop-sub {
		margin-top: 0.15rem;
		color: var(--muted);
		font-size: 0.74rem;
	}
	.pop-lang {
		margin-right: 0.4em;
		padding: 0.02em 0.36em;
		border-radius: 3px;
		background: color-mix(in srgb, var(--lc) 26%, transparent);
		box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--lc) 55%, transparent);
		color: var(--ink);
		font-family: var(--font-sans);
	}
	.pop-gloss {
		margin-top: 0.3rem;
		color: var(--ink);
		font-family: var(--font-serif);
		font-size: 0.82rem;
		line-height: 1.35;
	}
	.pop-hint {
		margin-top: 0.35rem;
		color: var(--faint);
		font-size: 0.66rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.hint .key {
		display: block;
		margin-top: 0.15rem;
	}
	.guess-toggle {
		flex: none;
		padding: 0.35rem 0.55rem;
		border: 1.5px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--muted);
		font: inherit;
		font-size: 0.72rem;
		font-weight: 600;
		white-space: nowrap;
		cursor: pointer;
	}
	.guess-toggle span {
		display: inline-block;
		min-width: 1.25rem;
		margin-left: 0.2rem;
		padding: 0.03rem 0.25rem;
		border-radius: 999px;
		background: var(--surface-2);
		font-variant-numeric: tabular-nums;
	}
	.guess-toggle:hover,
	.guess-toggle.on {
		border-color: var(--plum);
		color: var(--ink);
	}
	.guess-toggle.on {
		background: color-mix(in srgb, var(--plum) 18%, var(--surface));
	}
	.guess-toggle:focus-visible {
		outline: 2px solid var(--plum-2);
		outline-offset: 2px;
	}

	/* ---- the etymon list ------------------------------------------------- */
	.foot {
		padding: 0.4rem 0.6rem 0.6rem;
		border-top: 1px solid var(--border);
	}
	/* first line is the shared 'dot word count'; under it the gloss runs the full width */
	.pick {
		grid-template-areas:
			'dot word count'
			'. gloss gloss';
	}
	.pick:focus-visible,
	.disclose:focus-visible {
		outline: 2px solid var(--c);
		outline-offset: -2px;
		border-radius: 6px;
	}
	.dot {
		grid-area: dot;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		background: var(--c);
		flex: none;
		box-shadow: 0 0 0 2px var(--surface);
	}
	.pick.unetym .dot {
		background: transparent;
		border: 2px dashed var(--c);
		box-shadow: none;
	}
	.word {
		grid-area: word;
		font-family: var(--font-phon);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.pick.unetym .word {
		font-family: var(--font-sans);
		font-size: 0.82rem;
		font-style: italic;
		color: var(--muted);
	}
	/* the language an etymon is reconstructed in, tagged in its clade colour before the gloss —
	   *taṭṭ- and gāḍʰa mean nothing alike until you know one is Dravidian and the other OIA */
	.elang {
		margin-right: 0.4em;
		padding: 0.02em 0.36em;
		border-radius: 3px;
		background: color-mix(in srgb, var(--lc) 26%, transparent);
		box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--lc) 55%, transparent);
		color: var(--ink);
		font-family: var(--font-sans);
		font-size: 0.88em;
		white-space: nowrap;
	}
	/* the gloss is what distinguishes two reconstructions at a glance, so it stays on the row
	   even closed — clamped to two lines so the list keeps its rhythm */
	.gloss {
		grid-area: gloss;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		line-clamp: 2;
		overflow: hidden;
		color: var(--muted);
		font-family: var(--font-serif);
		font-size: 0.76rem;
		line-height: 1.35;
	}

	/* ---- an opened etymon ------------------------------------------------ */
	.detail-link {
		font-family: var(--font-phon);
		font-size: 0.76rem;
		color: var(--muted);
	}
	.detail-gloss {
		margin: 0;
		padding: 0 0.6rem 0.35rem;
		color: var(--muted);
		font-size: 0.82rem;
		line-height: 1.4;
	}
	.reflexes {
		list-style: none;
		margin: 0;
		padding: 0;
		border-top: 1px solid var(--border);
	}
	.reflexes li {
		display: grid;
		grid-template-columns: minmax(5rem, 7.5rem) minmax(0, 1fr);
		gap: 0.6rem;
		padding: 0.28rem 0.6rem;
		border-left: 3px solid var(--clade);
		border-bottom: 1px solid var(--border);
	}
	.reflexes li:last-child {
		border-bottom: 0;
	}
	.rlang {
		font-size: 0.76rem;
		font-weight: 500;
		overflow-wrap: anywhere;
	}
	/* historical and reconstructed languages carry the same rhombus the map draws for them */
	.hist {
		margin-right: 0.25em;
		color: var(--faint);
		font-size: 0.62em;
		vertical-align: 0.15em;
	}
	.reflexes li.historical {
		background: color-mix(in srgb, var(--surface-2) 55%, transparent);
	}
	.reflexes li.historical .rlang {
		font-variant: small-caps;
		letter-spacing: 0.02em;
	}
	.rforms {
		display: grid;
		gap: 0.12rem;
		min-width: 0;
	}
	.rform {
		font-family: var(--font-phon);
		font-size: 0.9rem;
		overflow-wrap: anywhere;
	}
	.guess-badge {
		display: inline-block;
		margin-left: 0.35rem;
		padding: 0.04rem 0.28rem;
		border: 1px dashed color-mix(in srgb, var(--c) 70%, var(--border));
		border-radius: 999px;
		color: var(--muted);
		font-family: var(--font-sans);
		font-size: 0.58rem;
		line-height: 1.25;
		vertical-align: 0.12em;
		white-space: nowrap;
	}
	.rgloss {
		color: var(--muted);
		font-family: var(--font-serif);
		font-size: 0.76rem;
	}
	.rgloss::before {
		content: '\2018';
	}
	.rgloss::after {
		content: '\2019';
	}

	/* ---- narrow screens: the panel stops floating and the page scrolls again -- */
</style>
