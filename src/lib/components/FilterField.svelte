<script lang="ts">
	import CharPalette from './CharPalette.svelte';

	let {
		label,
		value = '',
		placeholder = '',
		palette = false,
		onValue
	}: {
		label: string;
		value?: string;
		placeholder?: string;
		palette?: boolean;
		onValue: (value: string) => void;
	} = $props();

	let local = $state('');
	let inputEl = $state<HTMLInputElement | null>(null);
	let showPalette = $state(false);
	let debounce: ReturnType<typeof setTimeout>;

	$effect(() => {
		local = value;
	});

	function update(next: string) {
		local = next;
		clearTimeout(debounce);
		debounce = setTimeout(() => onValue(next), 250);
	}

	function insert(character: string) {
		local += character;
		onValue(local);
		inputEl?.focus();
	}
</script>

<label class="filter-field">
	<span>{label}</span>
	<div class="input-wrap">
		<input
			bind:this={inputEl}
			class="search-box"
			placeholder={placeholder || label}
			value={local}
			oninput={(event) => update(event.currentTarget.value)}
			onfocus={() => (showPalette = palette)}
			onblur={() => setTimeout(() => (showPalette = false), 200)}
		/>
		{#if showPalette}<CharPalette oninsert={insert} anchor={inputEl} />{/if}
	</div>
</label>

<style>
	.filter-field {
		display: grid;
		gap: 0.3rem;
		min-width: 0;
		color: var(--muted);
		font-size: 0.76rem;
		font-weight: 600;
	}
	.input-wrap { position: relative; }
	.search-box { font-family: var(--font-sans); }
</style>
