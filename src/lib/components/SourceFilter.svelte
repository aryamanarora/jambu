<script lang="ts">
	import SourcePicker from './SourcePicker.svelte';
	import SortToggle from './SortToggle.svelte';

	let {
		value = '', activeSort = '', standalone = false, onFilter, onSort
	}: {
		value?: string;
		activeSort?: string;
		standalone?: boolean;
		onFilter: (key: string, value: string) => void;
		onSort: (value: string) => void;
	} = $props();
</script>

<svelte:element this={standalone ? 'div' : 'th'} class:standalone>
	<div class="field">
		<SourcePicker {value} emptyLabel="Any source" onSelect={(next) => onFilter('source', next)} />
		{#if !standalone}<SortToggle label="Source" sortKey="source" {activeSort} {onSort} />{/if}
	</div>
</svelte:element>

<style>
	.standalone { display: grid; align-content: end; min-width: 0; }
</style>
