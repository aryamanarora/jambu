<script module lang="ts">
	export interface SelectOption {
		value: string;
		label: string;
		sub?: string; // muted secondary text (e.g. the clade)
		swatch?: string; // colour chip on the left (e.g. the clade colour)
	}
</script>

<script lang="ts">
	// A styled, searchable single-select used in filter-header cells (e.g. the Language column).
	// The trigger matches the sibling text-filter inputs; the open panel — search box + swatch/
	// label/sub rows — mirrors the favourites list so the two pieces of UI feel of a kind.
	let {
		placeholder,
		options,
		value,
		onSelect
	}: {
		placeholder: string;
		options: SelectOption[];
		value: string;
		onSelect: (v: string) => void;
	} = $props();

	let open = $state(false);
	let filter = $state('');
	let root: HTMLDivElement;
	let triggerEl = $state<HTMLButtonElement | null>(null);
	let searchEl = $state<HTMLInputElement | null>(null);
	// The panel is position:fixed (so it escapes the table wrapper's overflow clipping); we place it
	// against the trigger and keep it there on scroll/resize.
	let menuStyle = $state('');
	function place() {
		if (!triggerEl) return;
		const r = triggerEl.getBoundingClientRect();
		menuStyle = `top:${r.bottom + 5}px; left:${r.left}px; width:${Math.max(r.width, 230)}px;`;
	}

	const valueOpt = $derived(options.find((o) => o.value === value) ?? null);
	const filtered = $derived(
		filter
			? options.filter((o) => `${o.label} ${o.sub ?? ''}`.toLowerCase().includes(filter.toLowerCase()))
			: options
	);

	function pick(v: string) {
		onSelect(v);
		open = false;
		filter = '';
	}

	$effect(() => {
		if (!open) return;
		place();
		searchEl?.focus();
		const onDown = (e: MouseEvent) => {
			if (root && !root.contains(e.target as Node)) open = false;
		};
		const onKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape') open = false;
		};
		window.addEventListener('mousedown', onDown);
		window.addEventListener('keydown', onKey);
		// keep the fixed panel glued to the trigger as things move (scroll catches the table wrapper too)
		window.addEventListener('scroll', place, true);
		window.addEventListener('resize', place);
		return () => {
			window.removeEventListener('mousedown', onDown);
			window.removeEventListener('keydown', onKey);
			window.removeEventListener('scroll', place, true);
			window.removeEventListener('resize', place);
		};
	});
</script>

<div class="dd" bind:this={root}>
	<button
		class="trigger"
		class:active={open}
		bind:this={triggerEl}
		aria-expanded={open}
		onclick={() => {
			open = !open;
			filter = '';
		}}
	>
		<span class="cur" class:placeholder={!valueOpt}>{valueOpt ? valueOpt.label : placeholder}</span>
		<span class="caret">▾</span>
	</button>
	{#if open}
		<div class="panel" style={menuStyle}>
			<input
				class="search"
				placeholder="filter…"
				bind:value={filter}
				bind:this={searchEl}
				autocomplete="off"
			/>
			<ul class="list">
				<li>
					<button class="opt" class:on={value === ''} onclick={() => pick('')}>
						<span class="sw none"></span>
						<span class="lbl muted">All languages</span>
					</button>
				</li>
				{#each filtered as o (o.value)}
					<li>
						<button class="opt" class:on={value === o.value} onclick={() => pick(o.value)}>
							<span class="sw" style="background:{o.swatch ?? 'transparent'}"></span>
							<span class="lbl">{o.label}</span>
							{#if o.sub}<span class="sub">{o.sub}</span>{/if}
						</button>
					</li>
				{/each}
				{#if filtered.length === 0}<li class="none">no match</li>{/if}
			</ul>
		</div>
	{/if}
</div>

<style>
	.dd {
		position: relative;
		display: inline-flex;
		width: 100%;
	}
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
	.trigger.active {
		outline: none;
		border-color: var(--plum-2);
		box-shadow: 0 0 0 3px rgba(160, 46, 125, 0.15);
	}
	.cur {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.cur.placeholder {
		color: var(--muted);
	}
	.caret {
		font-size: 0.62rem;
		transition: transform 0.12s ease;
	}
	.trigger.active .caret {
		transform: rotate(180deg);
	}

	/* open panel — matches the favourites list styling */
	.panel {
		position: fixed;
		z-index: 60;
		background: var(--surface);
		color: var(--ink);
		border: 1px solid var(--border-strong);
		border-radius: 12px;
		box-shadow: 0 14px 38px rgba(0, 0, 0, 0.28);
		padding: 10px;
	}
	.search {
		width: 100%;
		box-sizing: border-box;
		font-size: 0.9rem;
		padding: 7px 10px;
		border: 1px solid var(--border-strong);
		border-radius: 8px;
		background: var(--bg);
		color: var(--ink);
	}
	.search:focus {
		outline: none;
		border-color: var(--berry);
	}
	.list {
		list-style: none;
		margin: 8px 0 0;
		padding: 0;
		max-height: 280px;
		overflow-y: auto;
	}
	.opt {
		display: flex;
		align-items: center;
		gap: 7px;
		width: 100%;
		background: none;
		border: none;
		padding: 5px 6px;
		border-radius: 6px;
		cursor: pointer;
		color: var(--ink);
		text-align: left;
	}
	.opt:hover {
		background: var(--surface-2, rgba(128, 128, 128, 0.1));
	}
	.opt.on {
		background: var(--plum);
		color: #fbeefb;
	}
	.sw {
		width: 11px;
		height: 11px;
		border-radius: 3px;
		flex: none;
		border: 1px solid rgba(0, 0, 0, 0.2);
	}
	.sw.none {
		background: transparent;
		border-style: dashed;
	}
	.lbl {
		flex: 1;
		font-size: 0.9rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.sub {
		font-size: 0.72rem;
		color: var(--muted);
		white-space: nowrap;
	}
	.opt.on .sub {
		color: #fbeefb;
		opacity: 0.75;
	}
	.none {
		padding: 8px;
		text-align: center;
		font-size: 0.8rem;
		color: var(--muted);
	}
</style>
