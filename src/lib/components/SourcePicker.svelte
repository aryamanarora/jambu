<script lang="ts">
	import { getFilterReferences } from '$lib/query';
	import { floatingPanel } from '$lib/floatingPanel';
	import { referenceLabel, striptags } from '$lib/render';
	import type { Reference } from '$lib/types';

	let {
		placeholder = 'Source',
		emptyLabel = 'All sources',
		value = '',
		options = [],
		onSelect
	}: {
		placeholder?: string;
		emptyLabel?: string;
		value?: string;
		options?: Reference[];
		onSelect: (value: string) => void;
	} = $props();

	let open = $state(false);
	let search = $state('');
	let references = $state<Reference[]>([]);
	let loaded = $state(false);
	let root: HTMLElement;
	let triggerEl = $state<HTMLButtonElement | null>(null);

	$effect(() => {
		if (options.length) {
			references = options;
			loaded = true;
		}
	});

	$effect(() => {
		if (open && !loaded) {
			loaded = true;
			getFilterReferences().then((rows) => (references = rows));
		}
	});

	const selected = $derived(references.find((reference) => reference.id === value || reference.short === value) ?? null);
	const filtered = $derived.by(() => {
		const needle = search.trim().toLocaleLowerCase();
		return needle
			? references.filter((reference) =>
					[reference.id, reference.short, reference.source, reference.editor].some((field) =>
						(field ?? '').toLocaleLowerCase().includes(needle)
					)
				)
			: references;
	});

	function citation(reference: Reference): string {
		return striptags(reference.source)
			.replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
			.replace(/\\([\\`*{}\[\]()#+\-.!_>])/g, '$1')
			.replace(/[*_`#]/g, '')
			.replace(/\s+/g, ' ')
			.trim();
	}
	function pick(next: string) {
		onSelect(next);
		open = false;
		search = '';
	}

	$effect(() => {
		if (!open) return;
		const onDown = (event: MouseEvent) => {
			if (root && !root.contains(event.target as Node)) open = false;
		};
		const onKey = (event: KeyboardEvent) => event.key === 'Escape' && (open = false);
		window.addEventListener('mousedown', onDown);
		window.addEventListener('keydown', onKey);
		return () => {
			window.removeEventListener('mousedown', onDown);
			window.removeEventListener('keydown', onKey);
		};
	});
</script>

<div class="picker" bind:this={root}>
	<button
		type="button"
		class="trigger"
		class:active={open || !!value}
		bind:this={triggerEl}
		aria-expanded={open}
		aria-label={value ? `Source: ${selected ? referenceLabel(selected) : value}` : 'Filter by source'}
		onclick={() => (open = !open)}
	>
		<span class:placeholder={!value}>{selected ? referenceLabel(selected) : value || placeholder}</span>
		<span class="chev" class:open aria-hidden="true"></span>
	</button>
	{#if open}
		<div class="panel" use:floatingPanel={triggerEl}>
			<div class="search-row">
				<!-- svelte-ignore a11y_autofocus -->
				<input
					class="source-search"
					placeholder="Search abbreviation, citation, or editor…"
					bind:value={search}
					autocomplete="off"
					autofocus
				/>
				{#if value}<button type="button" class="clear" onclick={() => pick('')}>clear</button>{/if}
			</div>
			<div class="list">
				<button type="button" class="option any" class:on={!value} onclick={() => pick('')}>{emptyLabel}</button>
				{#if !loaded}<div class="hint">loading references…</div>{/if}
				{#each filtered as reference (reference.id)}
					<button type="button" class="option" class:on={value === reference.id || value === reference.short} onclick={() => pick(reference.id)}>
						<span class="reference-row">
							<span class="abbr">{referenceLabel(reference)}</span>
							<span class="count">{reference.lemma_count.toLocaleString()} forms</span>
						</span>
						{#if citation(reference)}<span class="citation">{citation(reference)}</span>{/if}
					</button>
				{/each}
				{#if loaded && !filtered.length}<div class="hint">No matching references</div>{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.picker { position: relative; display: inline-flex; width: 100%; min-width: 0; }
	.trigger {
		display: inline-flex;
		align-items: center;
		justify-content: space-between;
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
	}
	.trigger.active { border-color: var(--plum-2); box-shadow: 0 0 0 3px rgba(160, 46, 125, 0.15); }
	.trigger > span:first-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.placeholder { color: var(--muted); }
	.trigger :global(.chev) { margin-left: auto; }
	.panel {
		width: min(32rem, calc(100vw - 1rem));
		background: var(--surface);
		border: 1.5px solid var(--border-strong);
		border-radius: 10px;
		box-shadow: 0 12px 34px rgba(0, 0, 0, 0.22);
		z-index: 70;
		overflow: hidden;
	}
	.search-row { display: flex; gap: 0.4rem; padding: 0.55rem; border-bottom: 1px solid var(--border); }
	.source-search { flex: 1; min-width: 0; padding: 0.45rem 0.55rem; border: 1px solid var(--border-strong); border-radius: var(--radius-sm); background: var(--bg); color: var(--ink); font-size: 0.86rem; }
	.source-search:focus { outline: none; border-color: var(--plum-2); }
	.clear { padding-inline: 0.65rem; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); color: var(--muted); cursor: pointer; }
	.list { max-height: 24rem; overflow-y: auto; padding: 0.35rem; }
	.option { display: flex; flex-direction: column; gap: 0.12rem; width: 100%; padding: 0.45rem 0.55rem; border: 0; border-radius: 7px; background: transparent; color: var(--ink); text-align: left; cursor: pointer; }
	.option:hover { background: var(--surface-2); }
	.option.on { background: color-mix(in srgb, var(--plum-2) 13%, var(--surface)); }
	.option.any { color: var(--muted); font-family: var(--font-sans); }
	.reference-row { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; width: 100%; }
	.abbr { color: var(--ink); font-family: var(--font-serif); font-weight: 500; }
	.count { color: var(--faint); font-family: var(--font-sans); font-size: 0.7rem; white-space: nowrap; }
	.citation { width: 100%; overflow: hidden; color: var(--muted); font-family: var(--font-sans); font-size: 0.76rem; line-height: 1.25; text-overflow: ellipsis; white-space: nowrap; }
	.hint { padding: 0.75rem; color: var(--muted); font-family: var(--font-sans); font-size: 0.8rem; text-align: center; }
	@media (max-width: 640px) { .trigger, .option { min-height: 42px; } .panel { width: calc(100vw - 1rem); } }
</style>
