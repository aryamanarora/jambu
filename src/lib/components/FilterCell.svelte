<script lang="ts">
	import CharPalette from './CharPalette.svelte';

	interface Option {
		value: string;
		label: string;
		disabled?: boolean;
	}
	let {
		label,
		filterKey = null,
		sortKey = null,
		type = 'text',
		options = [],
		value = '',
		activeSort = '',
		palette = false,
		numeric = false,
		onFilter,
		onSort
	}: {
		label: string;
		filterKey?: string | null;
		sortKey?: string | null;
		type?: 'text' | 'select';
		options?: Option[];
		value?: string;
		activeSort?: string; // current params.sort, e.g. "asc-word"
		palette?: boolean;
		numeric?: boolean; // right-align (for count columns)
		onFilter: (key: string, value: string) => void;
		onSort: (sortValue: string) => void;
	} = $props();

	let showPalette = $state(false);
	let inputEl = $state<HTMLInputElement | null>(null);
	let local = $state(value);
	$effect(() => {
		local = value;
	});

	let debounce: ReturnType<typeof setTimeout>;
	function onInput(v: string) {
		local = v;
		clearTimeout(debounce);
		debounce = setTimeout(() => filterKey && onFilter(filterKey, v), 300);
	}
	function insert(c: string) {
		local += c;
		if (filterKey) onFilter(filterKey, local);
		inputEl?.focus();
	}

	const ascActive = $derived(sortKey ? activeSort === `asc-${sortKey}` : false);
	const descActive = $derived(sortKey ? activeSort === `desc-${sortKey}` : false);
	function clickSort(dir: 'asc' | 'desc') {
		if (!sortKey) return;
		const val = `${dir}-${sortKey}`;
		onSort(activeSort === val ? '' : val);
	}
</script>

<th class:numeric>
	<div class="field">
		{#if filterKey && type === 'text'}
			<div class="filter-box">
				<input
					bind:this={inputEl}
					class="search-box"
					placeholder={label}
					value={local}
					oninput={(e) => onInput(e.currentTarget.value)}
					onfocus={() => (showPalette = palette)}
					onblur={() => setTimeout(() => (showPalette = false), 200)}
				/>
				{#if showPalette}
					<CharPalette oninsert={insert} />
				{/if}
			</div>
		{:else if filterKey && type === 'select'}
			<select
				class="search-box"
				value={local}
				onchange={(e) => filterKey && onFilter(filterKey, e.currentTarget.value)}
			>
				{#each options as opt (opt.value + opt.label)}
					<option value={opt.value} disabled={opt.disabled}>{opt.label}</option>
				{/each}
			</select>
		{:else}
			<span>{label}</span>
		{/if}

		{#if sortKey}
			<span class="sort">
				<button
					class="up"
					class:active={ascActive}
					aria-label="Sort {label} ascending"
					onclick={() => clickSort('asc')}
				></button>
				<button
					class="down"
					class:active={descActive}
					aria-label="Sort {label} descending"
					onclick={() => clickSort('desc')}
				></button>
			</span>
		{/if}
	</div>
</th>

<style>
	th.numeric :global(.field) {
		justify-content: flex-end;
	}
	th.numeric {
		text-align: right;
		vertical-align: middle; /* line up with the input-bearing headers */
	}
</style>
