<script lang="ts">
	import { onDestroy, tick, untrack } from 'svelte';
	import CharPalette from './CharPalette.svelte';

	let {
		value = '', placeholder = '', label, palette = false, debounceMs = 250,
		type = 'text', inputClass = 'search-box', sans = false, onValue, onSubmit
	}: {
		value?: string;
		placeholder?: string;
		label: string;
		palette?: boolean;
		debounceMs?: number;
		type?: 'text' | 'search';
		inputClass?: string;
		sans?: boolean;
		onValue: (value: string) => void;
		onSubmit?: () => void;
	} = $props();

	let local = $state(untrack(() => value));
	let input = $state<HTMLInputElement>();
	let showPalette = $state(false);
	let pending: ReturnType<typeof setTimeout> | undefined;
	let blurTimer: ReturnType<typeof setTimeout> | undefined;

	$effect(() => {
		local = value;
		clearTimeout(pending);
		pending = undefined;
	});
	onDestroy(() => { clearTimeout(pending); clearTimeout(blurTimer); });

	function commit() {
		clearTimeout(pending);
		pending = undefined;
		onValue(local);
	}
	function update(next: string) {
		local = next;
		clearTimeout(pending);
		if (debounceMs === 0) commit();
		else pending = setTimeout(commit, debounceMs);
	}
	async function insert(character: string) {
		if (!input) return;
		const start = input.selectionStart ?? local.length;
		const end = input.selectionEnd ?? start;
		local = local.slice(0, start) + character + local.slice(end);
		commit();
		await tick();
		input.focus();
		input.setSelectionRange(start + character.length, start + character.length);
	}
</script>

<span class="search-input">
	<input
		bind:this={input} class={inputClass} class:sans {type} {placeholder} aria-label={label}
		value={local} oninput={(event) => update(event.currentTarget.value)}
		onfocus={() => { clearTimeout(blurTimer); showPalette = palette; }}
		onblur={() => { blurTimer = setTimeout(() => (showPalette = false), 200); }}
		onkeydown={(event) => {
			if (event.key === 'Enter' && !event.isComposing && onSubmit) {
				event.preventDefault();
				if (pending !== undefined) commit();
				onSubmit();
			}
		}}
	/>
	{#if showPalette}<CharPalette oninsert={insert} anchor={input ?? null} />{/if}
</span>

<style>
	.search-input { display: block; position: relative; min-width: 0; }
	.sans { font-family: var(--font-sans); }
</style>
