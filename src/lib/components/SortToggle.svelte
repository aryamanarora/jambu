<script lang="ts">
	// The sort control for a column header: click to cycle ascending → descending → unsorted.
	// Both FilterCell and SourceFilter render one, so the icon, the cycle order and the
	// screen-reader wording live here rather than being written out twice.
	let {
		label,
		sortKey,
		activeSort = '',
		onSort
	}: {
		label: string;
		sortKey: string;
		activeSort?: string;
		onSort: (sortValue: string) => void;
	} = $props();

	const asc = $derived(activeSort === `asc-${sortKey}`);
	const desc = $derived(activeSort === `desc-${sortKey}`);
	const state = $derived(asc ? 'ascending' : desc ? 'descending' : 'unsorted');
</script>

<button
	class="sort-cycle"
	class:asc
	class:desc
	aria-label="Sort {label}; currently {state}"
	title="Sort {label}"
	onclick={() => onSort(asc ? `desc-${sortKey}` : desc ? '' : `asc-${sortKey}`)}
>
	<svg viewBox="0 0 10 14" aria-hidden="true" focusable="false">
		<path class="up" d="M5 1.8 8.3 6.05H1.7z" />
		<path class="down" d="M5 12.2 1.7 7.95h6.6z" />
	</svg>
</button>
