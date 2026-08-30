<script lang="ts">
	import CharPalette from './CharPalette.svelte';
	import SelectFilter, { type SelectOption } from './SelectFilter.svelte';
	import SortToggle from './SortToggle.svelte';
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
		accent = false,
		pickerKey = null,
		pickerOptions = [],
		pickerValue = '',
		pickerPlaceholder = '',
		onFilter,
		onSort
	}: {
		label: string;
		filterKey?: string | null;
		sortKey?: string | null;
		type?: 'text' | 'select';
		options?: SelectOption[];
		value?: string;
		activeSort?: string; // current params.sort, e.g. "asc-word"
		palette?: boolean;
		numeric?: boolean; // right-align (for count columns)
		accent?: boolean; // this column's cells carry a coloured left rail — match it in the header
		pickerKey?: string | null; // optional second control: a select picker beside the text filter
		pickerOptions?: SelectOption[];
		pickerValue?: string;
		pickerPlaceholder?: string;
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

</script>

<th class:numeric class:accent>
	<div class="field" class:split={!!pickerKey} class:boxed={!!filterKey || !!pickerKey}>
		{#if pickerKey}
			<div class="picker-box">
				<SelectFilter
					placeholder={pickerPlaceholder}
					options={pickerOptions}
					value={pickerValue}
					onSelect={(v) => pickerKey && onFilter(pickerKey, v)}
				/>
			</div>
		{/if}
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
					<CharPalette oninsert={insert} anchor={inputEl} />
				{/if}
			</div>
		{:else if filterKey && type === 'select'}
			<SelectFilter
				placeholder={label}
				{options}
				value={local}
				onSelect={(v) => filterKey && onFilter(filterKey, v)}
			/>
		{:else}
			<span>{label}</span>
		{/if}

		{#if sortKey}
			<SortToggle {label} {sortKey} {activeSort} {onSort} />
		{/if}
	</div>
</th>

<style>
	/* two controls (text filter + picker) sharing the column equally, side by side */
	th :global(.field.split) {
		gap: 0.4rem;
	}
	th :global(.field.split .filter-box),
	th :global(.field.split .picker-box) {
		flex: 1 1 0;
		min-width: 0;
	}
	th :global(.field.split .search-box) {
		width: 100%;
	}
	/* The header's inline padding matches the body cells' so plain labels sit on the column's
	   text edge. A filter control is a box, not text, so pull it back out into that padding —
	   it keeps the boxes tight against the column rules and evenly gapped from each other. */
	th :global(.field.boxed) {
		margin-inline: -0.3rem;
	}
	/* Label last so it ends on the column's right edge, flush with the figures below;
	   the sort control sits to its left rather than pushing it out of alignment. */
	th.numeric :global(.field) {
		flex-direction: row-reverse;
		justify-content: flex-start;
	}
</style>
