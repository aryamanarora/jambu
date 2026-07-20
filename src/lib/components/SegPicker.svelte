<script lang="ts">
	// Environment picker for the correspondence explorer: a single dropdown listing every
	// neighbouring segment (the list is long — dozens of segments can precede/follow a given one),
	// with a search box. The trigger shows the current selection.
	interface Opt {
		seg: string;
		n: number;
	}
	let {
		label,
		options,
		value,
		onSelect,
		align = 'start'
	}: {
		label: string;
		options: Opt[];
		value: string | null;
		onSelect: (v: string | null) => void;
		align?: 'start' | 'end';
	} = $props();

	let open = $state(false);
	let filter = $state('');
	let root: HTMLDivElement;

	const valueOpt = $derived(options.find((o) => o.seg === value) ?? null);
	const segLabel = (s: string) => (s === '#' ? '#' : s);
	const filtered = $derived(filter ? options.filter((o) => o.seg.includes(filter)) : options);

	function pick(v: string | null) {
		onSelect(v);
		open = false;
		filter = '';
	}

	$effect(() => {
		if (!open) return;
		const onDown = (e: MouseEvent) => {
			if (root && !root.contains(e.target as Node)) open = false;
		};
		const onKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape') open = false;
		};
		window.addEventListener('mousedown', onDown);
		window.addEventListener('keydown', onKey);
		return () => {
			window.removeEventListener('mousedown', onDown);
			window.removeEventListener('keydown', onKey);
		};
	});
</script>

<div class="ctx" class:end={align === 'end'} bind:this={root}>
	<span class="lbl">{label}</span>
	<div class="dd">
		<button
			class="trigger"
			class:active={open}
			class:set={value !== null}
			aria-expanded={open}
			onclick={() => {
				open = !open;
				filter = '';
			}}
		>
			<span class="cur phon">{value === null ? 'any' : segLabel(value)}</span>
			{#if valueOpt}<span class="curn">{valueOpt.n.toLocaleString()}</span>{/if}
			<span class="caret">▾</span>
		</button>
		{#if open}
			<div class="panel" class:right={align === 'end'}>
				<input class="search phon" placeholder="filter…" bind:value={filter} autocomplete="off" />
				<div class="list">
					<button class="opt" class:on={value === null} onclick={() => pick(null)}>
						<span>any</span>
					</button>
					{#each filtered as o (o.seg)}
						<button class="opt" class:on={value === o.seg} onclick={() => pick(o.seg)}>
							<span class="phon">{o.seg === '#' ? '# word edge' : o.seg}</span>
							<span class="en">{o.n.toLocaleString()}</span>
						</button>
					{/each}
					{#if filtered.length === 0}<div class="empty">no match</div>{/if}
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.ctx {
		display: flex;
		align-items: center;
		gap: 6px;
	}
	.ctx.end {
		justify-content: flex-end;
	}
	.lbl {
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
	}
	.dd {
		position: relative;
		display: inline-flex;
	}
	.trigger {
		display: inline-flex;
		align-items: baseline;
		gap: 5px;
		font-size: 0.92rem;
		padding: 3px 9px;
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		background: var(--surface);
		color: var(--ink);
		cursor: pointer;
	}
	.trigger:hover,
	.trigger.active {
		border-color: var(--berry);
	}
	.trigger.set {
		background: var(--plum);
		color: #fbeefb;
		border-color: var(--plum);
	}
	.trigger .cur {
		font-family: var(--font-phon);
	}
	.trigger .curn {
		font-family: var(--font-sans);
		font-size: 0.6rem;
		opacity: 0.65;
	}
	.trigger .caret {
		font-size: 0.62rem;
		transition: transform 0.12s ease;
	}
	.trigger.active .caret {
		transform: rotate(180deg);
	}
	.panel {
		position: absolute;
		top: calc(100% + 5px);
		left: 0;
		z-index: 40;
		width: 190px;
		background: var(--surface);
		border: 1px solid var(--border-strong);
		border-radius: 10px;
		box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
		padding: 6px;
		display: flex;
		flex-direction: column;
		gap: 5px;
	}
	.panel.right {
		left: auto;
		right: 0;
	}
	.search {
		width: 100%;
		box-sizing: border-box;
		font-size: 0.9rem;
		padding: 4px 8px;
		border: 1px solid var(--border);
		border-radius: 7px;
		background: var(--bg);
		color: var(--ink);
	}
	.search:focus {
		outline: none;
		border-color: var(--berry);
	}
	.list {
		display: flex;
		flex-direction: column;
		max-height: 240px;
		overflow-y: auto;
	}
	.opt {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 10px;
		padding: 4px 8px;
		border: none;
		border-radius: 6px;
		background: none;
		color: var(--ink);
		cursor: pointer;
		font-family: var(--font-phon);
		font-size: 0.95rem;
		text-align: left;
	}
	.opt:hover {
		background: var(--surface-2, rgba(128, 128, 128, 0.1));
	}
	.opt.on {
		background: var(--plum);
		color: #fbeefb;
	}
	.opt .en {
		font-family: var(--font-sans);
		font-size: 0.65rem;
		opacity: 0.6;
	}
	.empty {
		padding: 8px;
		text-align: center;
		font-size: 0.8rem;
		color: var(--muted);
	}
</style>
