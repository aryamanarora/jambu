<script lang="ts">
	import QualityBadge from '$lib/components/QualityBadge.svelte';
	// The languages of Jambu as a full-screen atlas, in the same idiom as the concept atlas: an
	// edge-to-edge map with two floating panels over it. Left holds the scope — which family you
	// are looking at, and what it contains. Right is the list of languages in that scope, working
	// as a picker: clicking a language draws it on the map, opening one reads out its dialects.
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import GeoMap from '$lib/components/Map.svelte';
	import AtlasShell from '$lib/components/AtlasShell.svelte';
	import PanelToggle from '$lib/components/PanelToggle.svelte';
	import { activePoint, highlightPoint, livePoint, mutedPoint } from '$lib/atlas';
	import { CLADE_ORDER, cladeColor } from '$lib/clades';
	import { SUPER_ORDER, SUPER_GROUPS, cladeGroup, superBranch } from '$lib/cladeTree';
	import { floatingPanel } from '$lib/floatingPanel';
	import type { DialectIndexRow, Language, MapMarker } from '$lib/types';

	let { languages, dialects }: { languages: Language[]; dialects: DialectIndexRow[] } = $props();

	interface Taxon {
		clade: string;
		branch: string;
		super: string;
	}
	interface Row {
		language: Language;
		taxon: Taxon;
		dialects: DialectIndexRow[];
	}

	// ---- indexes ------------------------------------------------------------------------------
	const cladeRank = (clade: string) => {
		const i = CLADE_ORDER.indexOf(clade);
		return i < 0 ? 999 : i;
	};

	const rowsById = $derived.by(() => {
		const byLanguage = new Map<string, DialectIndexRow[]>();
		for (const dialect of dialects) {
			const list = byLanguage.get(dialect.language_id);
			if (list) list.push(dialect);
			else byLanguage.set(dialect.language_id, [dialect]);
		}
		return new Map<string, Row>(
			languages.map((language) => {
				const clade = language.clade || 'Other';
				const branch = cladeGroup(clade);
				return [
					language.id,
					{
						language,
						taxon: { clade, branch, super: superBranch(branch) },
						dialects: byLanguage.get(language.id) ?? []
					}
				];
			})
		);
	});
	const allRows = $derived([...rowsById.values()]);
	const maxForms = $derived(Math.max(1, ...languages.map((language) => language.lemma_count)));
	const totalForms = $derived(languages.reduce((sum, language) => sum + language.lemma_count, 0));

	/** Corpus totals per clade — the backbone of both the band and the family tree. */
	const cladeTotals = $derived.by(() => {
		const totals = new Map<string, { languages: number; dialects: number; forms: number }>();
		for (const row of allRows) {
			const cell = totals.get(row.taxon.clade) ?? { languages: 0, dialects: 0, forms: 0 };
			cell.languages += 1;
			cell.dialects += row.dialects.length;
			cell.forms += row.language.lemma_count;
			totals.set(row.taxon.clade, cell);
		}
		return totals;
	});

	// super-branch → branch → clade, pruned to what the corpus actually holds. A level carrying a
	// single child is folded away rather than printed as its own row.
	const tree = $derived.by(() =>
		SUPER_ORDER.map((superName) => {
			const branches = (SUPER_GROUPS[superName] ?? [])
				.map((branch) => {
					const clades = [...cladeTotals.keys()]
						.filter((clade) => cladeGroup(clade) === branch)
						.sort((a, b) => cladeRank(a) - cladeRank(b));
					return {
						branch,
						clades,
						forms: clades.reduce((sum, c) => sum + cladeTotals.get(c)!.forms, 0),
						languages: clades.reduce((sum, c) => sum + cladeTotals.get(c)!.languages, 0)
					};
				})
				.filter((branch) => branch.languages > 0);
			return {
				super: superName,
				branches,
				forms: branches.reduce((sum, b) => sum + b.forms, 0),
				languages: branches.reduce((sum, b) => sum + b.languages, 0),
				lone: branches.length === 1 && branches[0].clades.length === 1 ? branches[0].clades[0] : null
			};
		}).filter((node) => node.languages > 0)
	);

	// ---- state --------------------------------------------------------------------------------
	type Level = 'all' | 'super' | 'branch' | 'clade';
	let scope = $state<{ level: Level; key: string }>({ level: 'all', key: '' });
	let search = $state('');
	let searchInput = $state(''); // what is typed; `search` follows it once the typing settles
	let searchTimer: ReturnType<typeof setTimeout>;
	function typeSearch(value: string) {
		searchInput = value;
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => (search = value), 140);
	}
	let sort = $state<'family' | 'forms' | 'name'>('family');
	let pinned = $state<string[]>([]);
	let hovered = $state<string | null>(null);
	// Every hover repaints all ~343 points (~20ms), so let the pointer settle first: sweeping the
	// list must not queue a redraw per row. A deliberate hover still lights within a frame or two.
	let hoverTimer: ReturnType<typeof setTimeout>;
	function preview(id: string | null) {
		clearTimeout(hoverTimer);
		hoverTimer = setTimeout(() => (hovered = id), id ? 70 : 0);
	}
	let expanded = $state<string[]>([]);
	let scopeOpen = $state(true);
	let listOpen = $state(true);
	let pickerOpen = $state(false);
	let treeFilter = $state('');
	let triggerEl = $state<HTMLButtonElement | null>(null);
	let searchEl = $state<HTMLInputElement | null>(null);

	const query = $derived(search.trim().toLowerCase());
	const active = $derived(pinned);

	/** What stays lit: your picks if you have any, else your search, else everything. */
	const emphasised = $derived.by(() => {
		if (pinned.length) return new Set(pinned);
		if (query) return hitIds;
		return null; // nothing singled out — the whole scope is live
	});

	function inScope(taxon: Taxon): boolean {
		if (scope.level === 'all') return true;
		if (scope.level === 'super') return taxon.super === scope.key;
		if (scope.level === 'branch') return taxon.branch === scope.key;
		return taxon.clade === scope.key;
	}
	function setScope(level: Level, key: string) {
		scope = scope.level === level && scope.key === key ? { level: 'all', key: '' } : { level, key };
		pickerOpen = false;
		treeFilter = '';
		expanded = [];
		// a pin outside the new scope is not drawn, so it would sit in the count saying nothing
		pinned = pinned.filter((id) => {
			const row = rowsById.get(id);
			return row ? inScope(row.taxon) : false;
		});
	}
	// Picking a language is one gesture: draw it, unfold its dialects, and let the frame close in.
	function clearPins() {
		expanded = expanded.filter((id) => !pinned.includes(id));
		pinned = [];
	}
	// A point on the map answers a click the way its row does: the first one picks the language,
	// and a second one — now that it is picked and you can see which it is — goes to it.
	function pickOrOpen(id: string) {
		if (pinned.includes(id)) goto(`${base}/languages/${id}`);
		else togglePin(id);
	}
	function togglePin(id: string) {
		if (pinned.includes(id)) {
			pinned = pinned.filter((p) => p !== id);
			expanded = expanded.filter((e) => e !== id);
		} else {
			pinned = [...pinned, id];
			if (!expanded.includes(id)) expanded = [...expanded, id];
		}
	}
	function toggleOpen(id: string) {
		expanded = expanded.includes(id) ? expanded.filter((e) => e !== id) : [...expanded, id];
	}

	/** The one muted line under a language's name: only what the panels above have not said. */
	function metaOf(r: Row): string {
		const parts: string[] = [];
		if (scope.level !== 'clade') parts.push(r.taxon.clade);
		if (r.dialects.length)
			parts.push(`${r.dialects.length} dialect${r.dialects.length === 1 ? '' : 's'}`);
		return parts.join(' · ');
	}

	/** `Sanskrit [Sk]` earns its tag; `Tamil [Tamil]` does not. */
	const slug = (v: string) => v.toLowerCase().replace(/[^a-z0-9]/g, '');
	const idWorthShowing = (language: Language) => slug(language.id) !== slug(language.name);

	function has(parts: Array<string | null | undefined>, needle: string): boolean {
		return parts.some((part) => part?.toLowerCase().includes(needle));
	}
	function matchedDialects(row: Row): DialectIndexRow[] {
		if (!query) return [];
		return row.dialects.filter((dialect) => has([dialect.name, dialect.id, dialect.location], query));
	}
	function isHit(row: Row): boolean {
		if (!query) return true;
		const { language, taxon } = row;
		return (
			has([language.name, language.language, language.dialect, language.id, language.glottocode, taxon.clade, taxon.branch], query) ||
			matchedDialects(row).length > 0
		);
	}

	// everything the map draws (the scope), and the subset the list shows (the scope, searched)
	const scopeRows = $derived(allRows.filter((row) => inScope(row.taxon)));
	const listRows = $derived.by(() => {
		const kept = scopeRows.filter(isHit);
		if (sort === 'name') return [...kept].sort((a, b) => a.language.name.localeCompare(b.language.name));
		if (sort === 'forms') return [...kept].sort((a, b) => b.language.lemma_count - a.language.lemma_count);
		return [...kept].sort(
			(a, b) =>
				cladeRank(a.taxon.clade) - cladeRank(b.taxon.clade) ||
				b.language.lemma_count - a.language.lemma_count
		);
	});
	const hitIds = $derived(new Set(listRows.map((row) => row.language.id)));

	const stats = $derived({
		languages: scopeRows.length,
		dialects: scopeRows.reduce((sum, row) => sum + row.dialects.length, 0),
		forms: scopeRows.reduce((sum, row) => sum + row.language.lemma_count, 0)
	});
	const scopeLabel = $derived(scope.level === 'all' ? 'All languages' : scope.key);
	const scopeCrumb = $derived.by(() => {
		if (scope.level === 'all') return 'Every family in Jambu';
		if (scope.level === 'super') return 'Branch of Jambu';
		const node = allRows.find((row) =>
			scope.level === 'branch' ? row.taxon.branch === scope.key : row.taxon.clade === scope.key
		);
		if (!node) return '';
		return scope.level === 'branch'
			? node.taxon.super
			: node.taxon.branch === node.taxon.clade
				? node.taxon.super
				: `${node.taxon.super} › ${node.taxon.branch}`;
	});

	// a power scale: a log bar flattens the whole top decade into one length, a linear bar hides
	// every small corpus. n^0.4 keeps both ends legible.
	const scale = (n: number) => Math.pow(n / maxForms, 0.4);
	const barWidth = (n: number) => `${Math.max(n > 0 ? 3 : 0, scale(n) * 100)}%`;

	// ---- the map ------------------------------------------------------------------------------
	// Every point wears the concept atlas's active treatment — filled in its family's colour, ringed
	// and raised — and keeps the shape its attestation earns it: a rhombus for the reconstructed and
	// historical languages, a circle for the living ones. The whole scope is active by default.
	// Picking or searching deactivates the complement to small grey; merely pointing at a row only
	// swells that one point and names it, leaving the map whole. The frame never moves either way.
	const markers = $derived.by((): MapMarker[] => {
		const points: MapMarker[] = [];
		for (const row of scopeRows) {
			const { language, taxon } = row;
			if (language.lat == null || language.long == null) continue;
			const lit = !emphasised || emphasised.has(language.id);
			const pointedAt = hovered === language.id;
			const isPinned = pinned.includes(language.id);
			points.push({
				lat: language.lat,
				long: language.long,
				svg: language.map_marker,
				// only the few points that must sit above the rest pay for being raised
				...(pointedAt
					? highlightPoint(cladeColor(taxon.clade))
					: isPinned
						? activePoint(cladeColor(taxon.clade))
						: lit
							? livePoint(cladeColor(taxon.clade))
							: mutedPoint()),
				focus: isPinned,
				tooltipOpen: pointedAt,
				tooltip: `<strong>${language.name}</strong><br>${taxon.clade} · ${language.lemma_count.toLocaleString()} forms${row.dialects.length ? ` · ${row.dialects.length} dialects` : ''}`,
				onClick: () => pickOrOpen(language.id)
			});
		}
		// an opened language puts its located dialects on the map — the geographic reading of the
		// list it just unfolded
		for (const id of expanded) {
			const row = rowsById.get(id);
			if (!row || !inScope(row.taxon)) continue;
			for (const dialect of row.dialects) {
				if (dialect.lat == null || dialect.long == null) continue;
				points.push({
					lat: dialect.lat,
					long: dialect.long,
					svg: '',
					...activePoint(cladeColor(row.taxon.clade)),
					radius: 3.2, // a dialect is a place inside a language, so it sits below its point
					focus: pinned.includes(id),
					tooltip: `<strong>${dialect.name}</strong><br>${row.language.name} · ${dialect.location || 'location not recorded'} · ${dialect.lemma_count.toLocaleString()} forms`,
					onClick: () =>
						goto(`${base}/languages/${id}?dialect=${encodeURIComponent(dialect.token)}#lexicon`)
				});
			}
		}
		return points;
	});

	// The map refits only when the set of points changes — a new scope, or a language opened to
	// show its dialects. Pinning, hovering and searching recolour what is already drawn, so the
	// frame stays put while you work through a list.
	const unmapped = $derived(scopeRows.filter((row) => row.language.lat == null).length);

	// ---- the family picker's dropdown -----------------------------------------------------------
	const treeQuery = $derived(treeFilter.trim().toLowerCase());
	const treeShown = $derived.by(() =>
		tree
			.map((node) => ({
				...node,
				branches: node.branches
					.map((branch) => ({
						...branch,
						clades: branch.clades.filter(
							(clade) => !treeQuery || clade.toLowerCase().includes(treeQuery) || branch.branch.toLowerCase().includes(treeQuery) || node.super.toLowerCase().includes(treeQuery)
						)
					}))
					.filter((branch) => branch.clades.length > 0)
			}))
			.filter((node) => node.branches.length > 0)
	);

	$effect(() => {
		if (!pickerOpen) return;
		searchEl?.focus();
		const onDown = (event: MouseEvent) => {
			const root = document.getElementById('family-picker');
			if (root && !root.contains(event.target as Node)) pickerOpen = false;
		};
		const onKey = (event: KeyboardEvent) => event.key === 'Escape' && (pickerOpen = false);
		window.addEventListener('mousedown', onDown);
		window.addEventListener('keydown', onKey);
		return () => {
			window.removeEventListener('mousedown', onDown);
			window.removeEventListener('keydown', onKey);
		};
	});
</script>

{#snippet row(r: Row)}
	{@const language = r.language}
	{@const isOpen = expanded.includes(language.id)}
	{@const isPinned = pinned.includes(language.id)}
	{@const hits = matchedDialects(r)}
	{@const meta = metaOf(r)}
	<div class="row" class:pinned={isPinned} class:open={isOpen} style="--c: {cladeColor(r.taxon.clade)}">
		<!-- picking is what the map draws; opening is what you read. Two jobs, two controls. -->
		<button
			class="pick"
			aria-pressed={isPinned}
			title={isPinned ? 'Remove from the map' : 'Draw on the map'}
			onmouseenter={() => preview(language.id)}
			onmouseleave={() => preview(null)}
			onfocus={() => preview(language.id)}
			onblur={() => preview(null)}
			onclick={() => togglePin(language.id)}
		>
			<span class="dot" class:proto={language.map_marker?.includes('polygon')}></span>
			<span class="word"
				>{language.name}{#if idWorthShowing(language)}<small>[{language.id}]</small>{/if}</span
			>
			<span class="count">{language.lemma_count.toLocaleString()}</span>
			<span class="meta"
				>{meta}{#if language.lat == null}<span class="nogeo">{meta ? ' · ' : ''}not located</span
					>{/if}</span
			>
			<span class="bar" aria-hidden="true"><i style={`width:${barWidth(language.lemma_count)}`}></i></span>
		</button>
		<button
			class="disclose"
			aria-expanded={isOpen}
			title={isOpen ? 'Close' : r.dialects.length ? `Show ${r.dialects.length} dialects` : 'Open'}
			onclick={() => toggleOpen(language.id)}
		>
			<span class="chev" class:right={!isOpen} aria-hidden="true"></span>
		</button>
	</div>

	{#if isOpen}
		<div class="detail" style="--c: {cladeColor(r.taxon.clade)}">
			<div class="detail-head">
				<a class="detail-link" href="{base}/languages/{language.id}">{language.name} [{language.id}] →</a>
				<span class="detail-meta">
					{#if r.dialects.length}{r.dialects.length} dialects · {r.dialects.filter((d) => d.lat != null).length} located{:else}no dialects recorded{/if}
				</span>
			</div>
			<p class="detail-path">
				{r.taxon.super}{#if r.taxon.branch !== r.taxon.super}<span class="sep" aria-hidden="true">›</span>{r.taxon.branch}{/if}{#if r.taxon.clade !== r.taxon.branch}<span class="sep" aria-hidden="true">›</span>{r.taxon.clade}{/if}
			</p>
			<ul class="dialects">
				{#each [...r.dialects].sort((a, b) => b.lemma_count - a.lemma_count) as dialect (dialect.token)}
					<li class:hit={hits.includes(dialect)}>
						<a class="dname" href="{base}/languages/{language.id}?dialect={encodeURIComponent(dialect.token)}#lexicon">
							{dialect.name}
						</a>
						<span class="dwhere" title={dialect.location || 'location not recorded'}>{dialect.location || 'location not recorded'}</span>
						{#if dialect.quality}
							<QualityBadge quality={dialect.quality} />
						{/if}
						<span class="dn">{dialect.lemma_count.toLocaleString()}</span>
					</li>
				{/each}
			</ul>
		</div>
	{/if}
{/snippet}

{#snippet map()}
	<GeoMap {markers} zoom={4} height="100%" mutedTiles flush zoomPosition="bottomleft" scrollZoom />
{/snippet}

<!-- left: which family you are looking at, and the way to change it -->
{#snippet left()}
		<div class="crumb-head">
			<nav class="crumbs">
				{#if scope.level === 'all'}
					{scopeCrumb}
				{:else}
					<button class="crumb-reset" onclick={() => setScope('all', '')}>All families</button>
					<span class="sep" aria-hidden="true">›</span>{scopeCrumb}
				{/if}
			</nav>
			<PanelToggle open={scopeOpen} side="left" label="the family panel" onclick={() => (scopeOpen = !scopeOpen)} />
		</div>

		<h1 id="family-picker">
			<button
				class="trigger"
				bind:this={triggerEl}
				class:active={pickerOpen}
				aria-expanded={pickerOpen}
				aria-label="Change family; showing {scopeLabel}"
				onclick={() => (pickerOpen = !pickerOpen)}
			>
				<span class="name">{scopeLabel}</span>
				<span class="chev" class:open={pickerOpen} aria-hidden="true"></span>
				<span class="swap">change</span>
			</button>

			{#if pickerOpen}
				<div class="picker-panel" use:floatingPanel={triggerEl}>
					<input
						class="picker-search"
						placeholder="Search families…"
						bind:value={treeFilter}
						bind:this={searchEl}
						autocomplete="off"
					/>
					<div class="tree">
						<button class="tree-node all" class:on={scope.level === 'all'} onclick={() => setScope('all', '')}>
							<span>All languages</span><small>{languages.length}</small>
						</button>
						{#each treeShown as node (node.super)}
							{#if node.lone}
								<button
									class="tree-node level-1 solo"
									class:on={scope.level === 'clade' && scope.key === node.lone}
									onclick={() => setScope('clade', node.lone!)}
								>
									<span><i style={`background:${cladeColor(node.lone)}`}></i>{node.super}</span>
									<small>{node.languages}</small>
								</button>
							{:else}
								<button
									class="tree-node level-1"
									class:on={scope.level === 'super' && scope.key === node.super}
									onclick={() => setScope('super', node.super)}
								>
									<span>{node.super}</span><small>{node.languages}</small>
								</button>
								{#each node.branches as branch (branch.branch)}
									{#if branch.clades.length === 1}
										<button
											class="tree-node level-2"
											class:on={scope.level === 'clade' && scope.key === branch.clades[0]}
											onclick={() => setScope('clade', branch.clades[0])}
										>
											<span><i style={`background:${cladeColor(branch.clades[0])}`}></i>{branch.clades[0]}</span>
											<small>{branch.languages}</small>
										</button>
									{:else}
										<button
											class="tree-node level-2"
											class:on={scope.level === 'branch' && scope.key === branch.branch}
											onclick={() => setScope('branch', branch.branch)}
										>
											<span>{branch.branch}</span><small>{branch.languages}</small>
										</button>
										{#each branch.clades as clade (clade)}
											<button
												class="tree-node level-3"
												class:on={scope.level === 'clade' && scope.key === clade}
												onclick={() => setScope('clade', clade)}
											>
												<span><i style={`background:${cladeColor(clade)}`}></i>{clade}</span>
												<small>{cladeTotals.get(clade)!.languages}</small>
											</button>
										{/each}
									{/if}
								{/each}
							{/if}
						{:else}
							<p class="none">no family matches “{treeFilter}”</p>
						{/each}
					</div>
				</div>
			{/if}
		</h1>

		{#if scopeOpen}
			<dl class="stats">
				<div><dt>Langs</dt><dd>{stats.languages.toLocaleString()}</dd></div>
				<div><dt>Dialects</dt><dd>{stats.dialects.toLocaleString()}</dd></div>
				<div><dt>Forms</dt><dd>{stats.forms.toLocaleString()}</dd></div>
			</dl>
			<!-- the whole corpus as one strip: every clade sized by its share of the lexicon, and a
			     way into it — the current scope stays lit while the rest fades -->
			<div class="band" role="group" aria-label="Share of the lexicon by family">
				{#each tree as node (node.super)}
					<div class="band-super" style={`flex-grow:${node.forms}`}>
						<div class="band-bar">
							{#each node.branches as branch (branch.branch)}
								{#each branch.clades as clade (clade)}
									{@const cell = cladeTotals.get(clade)!}
									<button
										class="band-seg"
										class:off={scope.level !== 'all' && !inScope({ clade, branch: branch.branch, super: node.super })}
										style={`flex-grow:${cell.forms};background:${cladeColor(clade)}`}
										title={`${clade} — ${cell.languages} languages · ${cell.forms.toLocaleString()} forms (${((cell.forms / totalForms) * 100).toFixed(1)}%)`}
										aria-label={`Show ${clade}`}
										onclick={() => setScope('clade', clade)}
									></button>
								{/each}
							{/each}
						</div>
						<span class="band-label" class:narrow={node.forms / totalForms < 0.09}>{node.super}</span>
					</div>
				{/each}
			</div>
		{/if}
{/snippet}

<!-- right: the languages of this scope, as a picker that opens out into dialects -->
{#snippet right()}
		<div class="panel-head">
			<PanelToggle open={listOpen} side="right" label="the language panel" onclick={() => (listOpen = !listOpen)} />
			<h2>{listRows.length.toLocaleString()} {listRows.length === 1 ? 'language' : 'languages'}</h2>
			{#if pinned.length}
				<button class="clear" onclick={clearPins} title="Clear the map selection">clear {pinned.length}</button>
			{/if}
		</div>

		{#if listOpen}
			<div class="controls">
				<input
					class="search"
					placeholder="Filter languages, dialects, places…"
					value={searchInput}
					oninput={(event) => typeSearch(event.currentTarget.value)}
				/>
				<div class="sorts" role="group" aria-label="Sort languages">
					{#each [['family', 'Family'], ['forms', 'Forms'], ['name', 'A–Z']] as [key, label] (key)}
						<button class:on={sort === key} onclick={() => (sort = key as typeof sort)}>{label}</button>
					{/each}
				</div>
			</div>
			<p class="hint">
				Click a language — here or on the map — to pin it and read its dialects. Pin several to
				compare; click a pinned point again to open it{unmapped ? `; ${unmapped} in this scope have no coordinates` : ''}.
			</p>

			<div class="list" role="group" aria-label="Languages in this scope">
				{#each listRows as r (r.language.id)}
					{@render row(r)}
				{:else}
					<p class="empty">No language or dialect matches “{search}”.</p>
				{/each}
			</div>
		{/if}
{/snippet}

<AtlasShell {map} {left} {right} leftOpen={scopeOpen} rightOpen={listOpen} />

<style>

	/* ---- the floating panels --------------------------------------------- */
	.sep { margin: 0 0.3rem; }
	.crumb-reset {
		border: 0;
		background: none;
		padding: 0;
		color: var(--plum-2);
		font: inherit;
		font-size: 0.72rem;
		cursor: pointer;
	}

	/* ---- the family picker ------------------------------------------------ */
	.trigger {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		grid-template-areas: 'name chev' 'swap swap';
		align-items: center;
		row-gap: 0.3rem;
		width: 100%;
		padding: 0.1rem 0.3rem 0.1rem 0;
		border: 0;
		border-radius: 6px;
		background: transparent;
		color: inherit;
		font: inherit;
		text-align: left;
		cursor: pointer;
	}
	.trigger .name {
		grid-area: name;
		font-family: var(--font-serif);
		font-size: clamp(1.5rem, 2.4vw, 2.1rem);
		font-weight: 700;
		line-height: 1.05;
		overflow-wrap: anywhere;
	}
	.trigger:hover .name,
	.trigger.active .name { color: var(--plum-2); }
	.trigger :global(.chev) {
		grid-area: chev;
		align-self: start;
		margin: 0.6rem 0 0 0.5rem;
		color: var(--muted);
	}
	.trigger .swap {
		grid-area: swap;
		justify-self: end;
		color: var(--muted);
		font-size: 0.68rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}
	.trigger:hover .swap,
	.trigger.active .swap { color: var(--plum-2); }

	.picker-panel {
		position: fixed;
		z-index: 1200;
		width: min(22rem, calc(100vw - 1.5rem));
		padding: 0.55rem;
		border: 1.5px solid var(--border-strong);
		border-radius: 12px;
		background: var(--surface);
		box-shadow: 0 14px 38px rgba(0, 0, 0, 0.32);
	}
	.picker-search {
		width: 100%;
		box-sizing: border-box;
		padding: 0.45rem 0.6rem;
		border: 1px solid var(--border-strong);
		border-radius: 8px;
		background: var(--surface);
		color: var(--ink);
		font: inherit;
		font-size: 0.9rem;
	}
	.picker-search:focus { outline: none; border-color: var(--berry); }
	.tree {
		display: grid;
		gap: 0.05rem;
		max-height: 24rem;
		margin-top: 0.5rem;
		overflow-y: auto;
		scrollbar-width: thin;
		scrollbar-color: var(--border-strong) transparent;
	}
	.tree-node {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.6rem;
		width: 100%;
		padding: 0.3rem 0.45rem;
		border: 0;
		border-radius: 7px;
		background: none;
		color: var(--ink);
		font: inherit;
		font-size: 0.84rem;
		text-align: left;
		cursor: pointer;
	}
	.tree-node span { display: inline-flex; align-items: center; min-width: 0; overflow: hidden; text-overflow: ellipsis; }
	.tree-node small { flex: none; color: var(--faint); font-size: 0.72rem; font-variant-numeric: tabular-nums; }
	.tree-node:hover { background: var(--surface-2); }
	.tree-node.on { background: var(--plum); color: #fbeefb; }
	.tree-node.on small { color: #fbeefb; opacity: 0.75; }
	.tree-node.all { font-weight: 600; }
	.tree-node.level-1 {
		font-family: var(--font-sans);
		font-size: 0.67rem;
		font-weight: 700;
		letter-spacing: 0.07em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.tree-node.level-1.solo { color: var(--ink); font-size: 0.72rem; }
	.tree-node.level-1.on { color: #fbeefb; }
	.tree-node.level-2 { padding-left: 0.9rem; }
	.tree-node.level-3 { padding-left: 1.9rem; }
	.tree-node i {
		display: inline-block;
		flex: none;
		width: 0.5rem;
		height: 0.5rem;
		margin-right: 0.45rem;
		border: 1px solid color-mix(in srgb, var(--ink) 18%, transparent);
		border-radius: 50%;
	}
	.none { margin: 0.4rem 0 0; padding: 0.5rem; color: var(--muted); font-size: 0.78rem; text-align: center; }

	/* ---- scope stats + corpus band ---------------------------------------- */
	.band { display: flex; gap: 0.3rem; padding: 0 0.95rem 0.75rem; }
	.band-super { display: grid; gap: 0.22rem; min-width: 0; flex-basis: 0; }
	.band-bar { display: flex; gap: 1px; height: 0.6rem; border-radius: 3px; overflow: hidden; }
	.band-seg { flex-basis: 0; min-width: 1px; padding: 0; border: 0; cursor: pointer; transition: opacity 0.12s ease; }
	.band-seg:hover { opacity: 0.7; }
	.band-seg.off { opacity: 0.2; }
	.band-label {
		overflow: hidden;
		color: var(--faint);
		font-size: 0.6rem;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		white-space: nowrap;
		text-overflow: ellipsis;
	}
	.band-label.narrow { visibility: hidden; }

	/* ---- the language panel ----------------------------------------------- */
	.sorts { display: flex; flex: none; gap: 0.15rem; }
	.sorts button {
		padding: 0.2rem 0.45rem;
		border: 1px solid var(--border);
		border-radius: 999px;
		background: none;
		color: var(--muted);
		font: inherit;
		font-size: 0.72rem;
		cursor: pointer;
	}
	.sorts button:hover { border-color: var(--border-strong); color: var(--ink); }
	.sorts button.on { border-color: var(--plum-2); background: color-mix(in srgb, var(--plum-2) 14%, transparent); color: var(--plum-2); }

	/* ---- the language list ------------------------------------------------ */
	/* first line is the shared 'dot word count'; under it we put the taxonomy and the size bar */
	.pick {
		grid-template-areas:
			'dot word count'
			'. meta bar';
	}
	.pick:focus-visible,
	.disclose:focus-visible { outline: 2px solid var(--c); outline-offset: -2px; border-radius: 6px; }
	.dot {
		grid-area: dot;
		box-sizing: border-box;
		width: 0.72rem;
		height: 0.72rem;
		border: 1px solid color-mix(in srgb, var(--ink) 30%, transparent);
		border-radius: 50%;
		background: var(--c);
		flex: none;
	}
	/* reconstructed and historical languages are marked out from the living ones */
	.dot.proto { border-radius: 2px; transform: rotate(45deg) scale(0.86); }
	.word {
		grid-area: word;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-size: 0.94rem;
	}
	.word small { margin-left: 0.3rem; color: var(--faint); font-size: 0.7rem; }
	.meta {
		grid-area: meta;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--muted);
		font-size: 0.72rem;
		line-height: 1.3;
	}
	.nogeo { font-style: italic; }
	.bar {
		grid-area: bar;
		align-self: center;
		width: 3.2rem;
		height: 3px;
		border-radius: 2px;
		background: color-mix(in srgb, var(--ink) 9%, transparent);
	}
	.bar i { display: block; height: 100%; border-radius: 2px; background: var(--c); }

	/* ---- an opened language ------------------------------------------------ */
	.detail-link { font-size: 0.76rem; font-weight: 600; color: var(--plum-2); }
	.detail-path {
		margin: 0;
		padding: 0 0.6rem 0.3rem;
		color: var(--faint);
		font-size: 0.7rem;
	}
	/* how good the record behind a dialect is — A best, C weakest */
	/* Outlined rather than filled: a solid tint deep enough to read in one theme goes muddy in the
	   other, so the letter keeps the accent colour and only the fill deepens with the grade. */

	.dialects { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--border); }
	.dialects li {
		display: grid;
		grid-template-columns: minmax(4.5rem, 7rem) minmax(0, 1fr) auto auto;
		gap: 0.5rem;
		padding: 0.26rem 0.6rem;
		border-bottom: 1px solid var(--border);
	}
	.dialects li:last-child { border-bottom: 0; }
	.dialects li.hit { background: color-mix(in srgb, var(--berry) 12%, transparent); }
	.dname { font-size: 0.78rem; font-weight: 500; overflow-wrap: anywhere; }
	.dwhere { color: var(--muted); font-size: 0.72rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.dn { color: var(--faint); font-size: 0.72rem; font-variant-numeric: tabular-nums; }

	@media (max-width: 560px) {
		.picker-panel {
			width: calc(100vw - 1rem);
			max-height: calc(100dvh - 1rem);
		}
		.tree {
			max-height: calc(100dvh - 8rem);
		}
		.tree-node {
			min-height: 2.75rem;
		}
		.sorts {
			width: 100%;
		}
		.sorts button {
			flex: 1 1 0;
			min-height: 2.75rem;
		}
		.dialects li {
			grid-template-columns: minmax(0, 1fr) auto auto;
			gap: 0.25rem 0.5rem;
			padding-block: 0.45rem;
		}
		.dwhere {
			grid-column: 1 / -1;
			grid-row: 2;
		}
	}
</style>
