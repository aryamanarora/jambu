<script lang="ts">
	// Header cell for the Reflexes table: a dropdown that filters by structured tags. Multi-select
	// with AND semantics (a row must carry every picked tag). Renders a <th> so it drops into the
	// header row alongside the FilterCell columns. Chips are coloured by category.
	import { GENDER_TAGS, GRAMMATICAL_TAGS, COMMON_SOURCES, ERA_TAGS, TAG_NAMES } from '$lib/tags';
	import { floatingPanel } from '$lib/floatingPanel';
	let {
		value = '',
		onFilter
	}: { value?: string; onFilter: (key: string, value: string) => void } = $props();

	const GROUPS = [
		{ label: 'gender', cat: 'gender', tags: GENDER_TAGS },
		{ label: 'grammatical', cat: 'grammatical', tags: GRAMMATICAL_TAGS },
		{ label: 'source', cat: 'source', tags: COMMON_SOURCES },
		{ label: 'era', cat: 'era', tags: ERA_TAGS }
	] as const;

	const selected = $derived(new Set(value.split(/\s+/).filter(Boolean)));
	let open = $state(false);
	let root: HTMLElement;
	let triggerEl = $state<HTMLButtonElement | null>(null);

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
			{#each GROUPS as g (g.label)}
				<div class="grp">
					<div class="grp-lbl">
						{g.label}
						{#if g.label === 'gender' && selected.size}
							<button class="clear" onclick={() => onFilter('tags', '')}>clear all</button>
						{/if}
					</div>
					<div class="chips {g.cat}">
						{#each g.tags as t (t)}
							<button
								class="chip"
								class:on={selected.has(t)}
								title={TAG_NAMES[t] ?? t}
								onclick={() => toggle(t)}>{t}</button
							>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</th>

<style>
	th {
		position: relative;
	}
	/* match the sibling text-filter inputs (.search-box) so the header row reads uniformly */
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
	.caret {
		margin-left: auto;
	}
	.count {
		font-size: 0.62rem;
		font-weight: 700;
		background: color-mix(in srgb, currentColor 22%, transparent);
		border-radius: 999px;
		padding: 0 5px;
	}
	.caret {
		font-size: 0.6rem;
		transition: transform 0.12s ease;
	}
	.caret.up {
		transform: rotate(180deg);
	}
	.panel {
		position: absolute;
		z-index: 40;
		top: calc(100% + 4px);
		left: 0;
		width: 250px;
		background: var(--surface);
		color: var(--ink);
		border: 1px solid var(--border-strong);
		border-radius: 10px;
		box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
		padding: 9px 11px 11px;
		text-align: left;
		font-weight: 400;
	}
	.grp + .grp {
		margin-top: 9px;
	}
	.grp-lbl {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		font-size: 0.65rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
		margin-bottom: 5px;
	}
	.clear {
		border: none;
		background: none;
		color: var(--berry);
		cursor: pointer;
		font-size: 0.68rem;
		text-transform: none;
		letter-spacing: 0;
		padding: 0;
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}
	/* per-category accent colour (used on hover + selected) */
	.chips.gender {
		--cat: var(--berry);
	}
	.chips.grammatical {
		--cat: var(--tag-gram);
	}
	.chips.source {
		--cat: var(--tag-source);
	}
	.chips.era {
		--cat: var(--tag-era);
	}
	.chip {
		font-size: 0.72rem;
		padding: 1px 8px;
		border-radius: 999px;
		border: 1px solid var(--border-strong);
		background: var(--surface);
		color: var(--ink);
		cursor: pointer;
		font-variant: small-caps;
	}
	.chip:hover {
		border-color: var(--cat);
		color: var(--cat);
	}
	.chip.on {
		background: var(--cat);
		border-color: var(--cat);
		color: #fff;
	}
</style>
