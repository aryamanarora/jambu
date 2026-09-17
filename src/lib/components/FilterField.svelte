<script lang="ts">
	import SearchInput from './SearchInput.svelte';
	let {
		label, value = '', placeholder = '', palette = false, debounceMs = 250, onValue
	}: {
		label: string;
		value?: string;
		placeholder?: string;
		palette?: boolean;
		debounceMs?: number;
		onValue: (value: string) => void;
	} = $props();
</script>

<label class="filter-control">
	<span>{label}</span>
	<SearchInput {label} {value} placeholder={placeholder || label} {palette} {debounceMs} {onValue} sans />
</label>
