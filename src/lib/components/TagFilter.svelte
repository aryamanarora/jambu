<script lang="ts">
	// Header cell: a searchable, multi-select tag filter. The tag list is built automatically from
	// the DB (getAllTags) — no hand-maintained list — grouped by category and searchable, since the
	// tag set is now large. Multi-select with AND semantics (a row must carry every picked tag).
	import { getAllTags } from '$lib/query';
	import { tagCategory, tagLabel, type TagCategory } from '$lib/tags';
	import { floatingPanel } from '$lib/floatingPanel';

	let {
		value = '',
		onFilter
	}: { value?: string; onFilter: (key: string, value: string) => void } = $props();

	const selected = $derived(new Set(value.split(/\s+/).filter(Boolean)));
	let open = $state(false);
	let search = $state('');
	let root: HTMLElement;
	let triggerEl = $state<HTMLButtonElement | null>(null);

	// fetched once, lazily on first open
	let allTags = $state<{ tag: string; count: number }[]>([]);
	let loaded = false;
	$effect(() => {
		if (open && !loaded) {
			loaded = true;
			getAllTags().then((t) => (allTags = t));
		}
	});

	const CAT_ORDER: TagCategory[] = ['grammatical', 'gender', 'source', 'era', 'dialect'];
	const groups = $derived.by(() => {
		const q = search.trim().toLowerCase();
		const byCat = new Map<TagCategory, { tag: string; count: number }[]>();
		for (const t of allTags) {
			if (q && !t.tag.toLowerCase().includes(q) && !tagLabel(t.tag).toLowerCase().includes(q))
				continue;
			const cat = tagCategory(t.tag);
			const arr = byCat.get(cat);
			if (arr) arr.push(t);
			else byCat.set(cat, [t]);
		}
		return [...byCat.keys()]
			.sort((a, b) => ((CAT_ORDER.indexOf(a) + 1 || 99) - (CAT_ORDER.indexOf(b) + 1 || 99)))
			.map((cat) => ({ cat, tags: byCat.get(cat)! }));
	});

	function toggle(t: string) {
		const next = new Set(selected);
		if (next.has(t)) next.delete(t);
		else next.add(t);
		onFilter('tags', [...next].join(' '));
	}

	$effect(() => {
		if (!open) return;
		const onDown = (e: MouseEvent) => {
			if (root && !root.contains(e.target as Node)) open = false;
		};
		const onKey = (e: KeyboardEvent) => e.key === 'Escape' && (open = false);
		window.addEventListener('mousedown', onDown);
		window.addEventListener('keydown', onKey);
		return () => {
			window.removeEventListener('mousedown', onDown);
			window.removeEventListener('keydown', onKey);
		};
	});
</script>

<th bind:this={root}>
	<div class="field">
		<button
			class="trigger"
			class:active={selected.size > 0}
			bind:this={triggerEl}
			aria-expanded={open}
			onclick={() => (open = !open)}
		>
			Tags{#if selected.size}<span class="count">{selected.size}</span>{/if}
			<span class="caret" class:up={open}>▾</span>
		</button>
	</div>
	{#if open}
		<div class="panel" use:floatingPanel={triggerEl}>
			<div class="search-row">
				<!-- svelte-ignore a11y_autofocus -->
				<input class="tag-search" placeholder="Search tags…" bind:value={search} autofocus />
				{#if selected.size}
					<button class="clear" onclick={() => onFilter('tags', '')}>clear</button>
				{/if}
			</div>
			<div class="scroll">
				{#if !allTags.length}
					<div class="hint">loading…</div>
				{:else if !groups.length}
					<div class="hint">no matching tags</div>
				{/if}
				{#each groups as g (g.cat)}
					<div class="grp">
						<div class="grp-lbl">{g.cat}</div>
						<div class="chips {g.cat}">
							{#each g.tags as t (t.tag)}
								<button
									class="chip"
									class:on={selected.has(t.tag)}
									title="{tagLabel(t.tag)} · {t.count.toLocaleString()}"
									onclick={() => toggle(t.tag)}
								>
									{tagLabel(t.tag)}<span class="cnt">{t.count.toLocaleString()}</span>
								</button>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</th>

<style>
	th {
		position: relative;
	}
	.trigger {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		width: 100%;
		min-width: 90px;
		padding: 0.38rem 0.5rem;
		font-family: var(--font-serif);
		font-size: 0.9rem;
		color: var(--ink);
		background: var(--surface);
		border: 1.5px solid var(--border-strong);
		border-radius: var(--radius-sm);
		cursor: pointer;
		white-space: nowrap;
	}
	.trigger:hover,
	.trigger.active {
		border-color: var(--plum-2);
	}
	.count {
		background: var(--plum-2);
		color: #fff;
		border-radius: 999px;
		padding: 0 0.4em;
		font-size: 0.75em;
	}
	.caret {
		margin-left: auto;
		font-size: 0.7em;
		transition: transform 0.12s;
	}
	.caret.up {
		transform: rotate(180deg);
	}
	.panel {
		background: var(--surface);
		border: 1.5px solid var(--border-strong);
		border-radius: var(--radius-sm);
		box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
		width: 20rem;
		max-width: 90vw;
		z-index: 50;
		display: flex;
		flex-direction: column;
	}
	.search-row {
		display: flex;
		gap: 0.4rem;
		padding: 0.5rem;
		border-bottom: 1px solid var(--border);
	}
	.tag-search {
		flex: 1;
		padding: 0.35rem 0.5rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--bg, var(--surface));
		color: inherit;
		font-size: 0.85rem;
	}
	.clear {
		font-size: 0.75rem;
		background: none;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 0 0.5rem;
		cursor: pointer;
		color: var(--muted);
	}
	.scroll {
		max-height: 22rem;
		overflow-y: auto;
		padding: 0.4rem 0.5rem 0.6rem;
	}
	.hint {
		color: var(--muted);
		font-size: 0.8rem;
		padding: 0.6rem;
	}
	.grp {
		margin-bottom: 0.5rem;
	}
	.grp-lbl {
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		color: var(--muted);
		margin: 0.3rem 0;
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}
	.chip {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		font-size: 0.78rem;
		padding: 0.15rem 0.45rem;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		background: var(--surface);
		color: var(--ink);
		cursor: pointer;
		white-space: nowrap;
	}
	.chip:hover {
		border-color: var(--plum-2);
	}
	.chip.on {
		background: var(--plum-2);
		color: #fff;
		border-color: var(--plum-2);
	}
	.chip .cnt {
		font-size: 0.72em;
		opacity: 0.6;
		font-variant-numeric: tabular-nums;
	}
	.chip.on .cnt {
		opacity: 0.85;
	}
</style>
