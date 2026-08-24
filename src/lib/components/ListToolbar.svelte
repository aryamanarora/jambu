<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		value = '',
		placeholder = 'Search…',
		searchLabel = 'Search',
		resultLabel = '',
		filterCount = 0,
		onSearch,
		filters,
		actions
	}: {
		value?: string;
		placeholder?: string;
		searchLabel?: string;
		resultLabel?: string;
		filterCount?: number;
		onSearch: (value: string) => void;
		filters?: Snippet;
		actions?: Snippet;
	} = $props();

	let local = $state('');
	let filterMenu = $state<HTMLDetailsElement | null>(null);
	let debounce: ReturnType<typeof setTimeout>;

	$effect(() => {
		local = value;
	});

	function update(next: string) {
		local = next;
		clearTimeout(debounce);
		debounce = setTimeout(() => onSearch(next), 250);
	}
</script>

<div class="list-toolbar">
	<label class="search-field">
		<span class="visually-hidden">{searchLabel}</span>
		<span class="search-icon" aria-hidden="true">⌕</span>
		<input
			type="search"
			{placeholder}
			value={local}
			oninput={(event) => update(event.currentTarget.value)}
		/>
	</label>

	{#if filters}
		<details class="filter-menu" bind:this={filterMenu}>
			<summary class:active={filterCount > 0}>
				Filters{#if filterCount}<span class="filter-count">{filterCount}</span>{/if}
			</summary>
			<div class="filter-panel">
				<div class="filter-panel-head">
					<strong>Refine results</strong>
					<button type="button" onclick={() => filterMenu?.removeAttribute('open')}>Done</button>
				</div>
				<div class="filter-grid">{@render filters()}</div>
			</div>
		</details>
	{/if}

	{#if actions}<div class="toolbar-actions">{@render actions()}</div>{/if}
	{#if resultLabel}<span class="result-label">{resultLabel}</span>{/if}
</div>

<style>
	.list-toolbar {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.55rem;
		margin: 0.85rem 0 0.7rem;
	}
	.search-field {
		position: relative;
		flex: 1 1 22rem;
		max-width: 36rem;
	}
	.search-field input {
		width: 100%;
		min-height: 42px;
		padding: 0.58rem 0.8rem 0.58rem 2.15rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--ink);
		font: inherit;
	}
	.search-field input:focus {
		outline: none;
		border-color: var(--plum-2);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--berry) 16%, transparent);
	}
	.search-icon {
		position: absolute;
		left: 0.75rem;
		top: 50%;
		z-index: 1;
		transform: translateY(-52%);
		color: var(--muted);
		font-size: 1.15rem;
		pointer-events: none;
	}
	.filter-menu {
		position: relative;
		flex: 0 0 auto;
	}
	.filter-menu > summary {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		min-height: 42px;
		padding: 0.5rem 0.85rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--ink);
		font-size: 0.88rem;
		font-weight: 600;
		cursor: pointer;
		list-style: none;
	}
	.filter-menu > summary::-webkit-details-marker { display: none; }
	.filter-menu > summary::after {
		content: '⌄';
		color: var(--muted);
	}
	.filter-menu > summary:hover,
	.filter-menu > summary.active,
	.filter-menu[open] > summary {
		border-color: var(--plum-2);
		color: var(--plum-2);
	}
	.filter-count {
		display: inline-grid;
		place-items: center;
		min-width: 1.25rem;
		height: 1.25rem;
		padding: 0 0.3rem;
		border-radius: 999px;
		background: var(--plum);
		color: #fff;
		font-size: 0.7rem;
	}
	.filter-panel {
		position: absolute;
		top: calc(100% + 0.45rem);
		right: 0;
		z-index: 50;
		width: min(42rem, calc(100vw - 2rem));
		padding: 0.9rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius);
		background: var(--surface);
		box-shadow: var(--shadow-md);
	}
	.filter-panel-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 0.75rem;
	}
	.filter-panel-head button {
		border: 0;
		background: none;
		color: var(--plum-2);
		font: inherit;
		font-size: 0.82rem;
		font-weight: 600;
		cursor: pointer;
	}
	.filter-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.75rem;
	}
	.toolbar-actions {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
	}
	.result-label {
		margin-left: auto;
		color: var(--muted);
		font-size: 0.84rem;
		white-space: nowrap;
	}
	@media (max-width: 640px) {
		.list-toolbar { flex-wrap: wrap; }
		.search-field { flex-basis: calc(100% - 6.5rem); }
		.filter-panel {
			position: fixed;
			inset: 4.25rem 0.65rem auto;
			width: auto;
			max-height: calc(100dvh - 5rem);
			overflow-y: auto;
		}
		.filter-grid { grid-template-columns: 1fr; }
		.result-label {
			order: 5;
			width: 100%;
			margin-left: 0;
		}
	}
</style>
