<script lang="ts">
	// The concept the atlas is showing, and the way to change it. The list is queried from the
	// in-browser database when the panel first opens rather than shipped with every prerendered
	// concept page — there are thousands of concepts and only one of them is ever on screen.
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { getConceptList, type ConceptPick } from '$lib/query';
	import { floatingPanel } from '$lib/floatingPanel';

	let {
		current,
		large = false
	}: {
		current: { id: number; name: string; category: string };
		large?: boolean; // the headline treatment, for the atlas's concept panel
	} = $props();

	let open = $state(false);
	let filter = $state('');
	let concepts = $state<ConceptPick[]>([]);
	let loading = $state(false);
	let root: HTMLDivElement;
	let triggerEl = $state<HTMLButtonElement | null>(null);
	let searchEl = $state<HTMLInputElement | null>(null);

	$effect(() => {
		if (!open || concepts.length || loading) return;
		loading = true;
		getConceptList()
			.then((rows) => (concepts = rows))
			.finally(() => (loading = false));
	});

	const filtered = $derived.by(() => {
		const needle = filter.trim().toLocaleLowerCase();
		const rows = needle
			? concepts.filter((c) =>
					`${c.name} ${c.category}`.toLocaleLowerCase().includes(needle)
				)
			: concepts;
		return rows.slice(0, 300); // the list is long; the search box is the way through it
	});

	function pick(id: number) {
		open = false;
		filter = '';
		if (id !== current.id) goto(`${base}/concepts/${id}`);
	}

	$effect(() => {
		if (!open) return;
		searchEl?.focus();
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

<div class="picker" bind:this={root}>
	<button
		class="trigger"
		class:large
		class:active={open}
		bind:this={triggerEl}
		aria-expanded={open}
		aria-label="Change concept; showing {current.name}"
		onclick={() => (open = !open)}
	>
		<span class="name">{current.name}</span>
		<span class="cat">{current.category}</span>
		<span class="chev" class:open aria-hidden="true"></span>
		{#if large}<span class="swap">change</span>{/if}
	</button>

	{#if open}
		<div class="panel" use:floatingPanel={triggerEl}>
			<input
				class="search"
				placeholder="Search concepts…"
				bind:value={filter}
				bind:this={searchEl}
				autocomplete="off"
			/>
			<ul class="list">
				{#each filtered as c (c.id)}
					<li>
						<button class="opt" class:on={c.id === current.id} onclick={() => pick(c.id)}>
							<span class="opt-name">{c.name}</span>
							<span class="opt-cat">{c.category}</span>
							<span class="opt-n">{c.form_count.toLocaleString()}</span>
						</button>
					</li>
				{:else}
					<li class="none">{loading ? 'loading concepts…' : `no concept matches “${filter}”`}</li>
				{/each}
			</ul>
			{#if !filter && concepts.length > filtered.length}
				<p class="more">{(concepts.length - filtered.length).toLocaleString()} more — search to narrow</p>
			{/if}
		</div>
	{/if}
</div>

<style>
	.picker {
		position: relative;
		min-width: 0;
	}
	.trigger.large {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		grid-template-areas:
			'name chev'
			'cat swap';
		align-items: center;
		row-gap: 0.3rem;
	}
	.trigger.large .name {
		grid-area: name;
		font-size: clamp(1.6rem, 2.6vw, 2.3rem);
		line-height: 1.05;
		white-space: normal;
		overflow-wrap: anywhere;
	}
	.trigger.large .cat {
		grid-area: cat;
		justify-self: start;
	}
	.trigger.large :global(.chev) {
		grid-area: chev;
		margin-left: 0.5rem;
		align-self: start;
		margin-top: 0.6rem;
	}
	.trigger.large .swap {
		grid-area: swap;
		justify-self: end;
		font-size: 0.68rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.trigger.large:hover .swap,
	.trigger.large.active .swap {
		color: var(--plum-2);
	}
	.trigger {
		display: flex;
		align-items: baseline;
		gap: 0.45rem;
		width: 100%;
		min-width: 0;
		padding: 0.1rem 0.3rem 0.1rem 0;
		border: 0;
		border-radius: 6px;
		background: transparent;
		color: inherit;
		font: inherit;
		text-align: left;
		cursor: pointer;
	}
	.trigger:hover .name,
	.trigger.active .name {
		color: var(--plum-2);
	}
	.name {
		font-family: var(--font-serif);
		font-size: 1.25rem;
		font-weight: 700;
		line-height: 1.15;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.cat {
		flex: none;
		font-size: 0.7rem;
		color: var(--muted);
		border: 1px solid var(--border);
		border-radius: 999px;
		padding: 0.08rem 0.5rem;
		white-space: nowrap;
	}
	.trigger :global(.chev) {
		flex: none;
		margin-left: auto;
		color: var(--muted);
		align-self: center;
	}

	.panel {
		position: fixed;
		z-index: 1200;
		width: min(24rem, calc(100vw - 1.5rem));
		padding: 0.55rem;
		border: 1.5px solid var(--border-strong);
		border-radius: 12px;
		background: var(--surface);
		box-shadow: 0 14px 38px rgba(0, 0, 0, 0.32);
	}
	.search {
		width: 100%;
		box-sizing: border-box;
		padding: 0.45rem 0.6rem;
		border: 1px solid var(--border-strong);
		border-radius: 8px;
		background: var(--bg);
		color: var(--ink);
		font: inherit;
		font-size: 0.9rem;
	}
	.search:focus {
		outline: none;
		border-color: var(--berry);
	}
	.list {
		list-style: none;
		margin: 0.5rem 0 0;
		padding: 0;
		max-height: 22rem;
		overflow-y: auto;
		scrollbar-width: thin;
		scrollbar-color: var(--border-strong) transparent;
	}
	.opt {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto auto;
		align-items: baseline;
		gap: 0.6rem;
		width: 100%;
		padding: 0.35rem 0.45rem;
		border: 0;
		border-radius: 7px;
		background: none;
		color: var(--ink);
		font: inherit;
		text-align: left;
		cursor: pointer;
	}
	.opt:hover {
		background: var(--surface-2);
	}
	.opt.on {
		background: var(--plum);
		color: #fbeefb;
	}
	.opt-name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 600;
	}
	.opt-cat {
		font-size: 0.72rem;
		color: var(--muted);
		white-space: nowrap;
	}
	.opt-n {
		font-size: 0.72rem;
		color: var(--faint);
		font-variant-numeric: tabular-nums;
	}
	.opt.on .opt-cat,
	.opt.on .opt-n {
		color: #fbeefb;
		opacity: 0.75;
	}
	.none,
	.more {
		margin: 0.4rem 0 0;
		padding: 0.5rem;
		color: var(--muted);
		font-size: 0.78rem;
		text-align: center;
	}

	@media (max-width: 560px) {
		.panel {
			width: calc(100vw - 1rem);
			max-height: calc(100dvh - 1rem);
		}
		.list {
			max-height: calc(100dvh - 8rem);
		}
		.opt {
			min-height: 2.75rem;
		}
	}
</style>
