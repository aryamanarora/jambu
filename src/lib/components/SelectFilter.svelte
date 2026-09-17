<script module lang="ts">
	export type { SelectOption } from '$lib/languageOptions';
</script>

<script lang="ts">
	import { tick, type Snippet } from 'svelte';
	import type { SelectOption } from '$lib/languageOptions';
	import SearchableOptions from './SearchableOptions.svelte';
	let {
		placeholder, options, value = '', onSelect, multiple = false, values = [], onChange,
		header, summary, emptyLabel = 'No matching languages'
	}: {
		placeholder: string; options: SelectOption[]; value?: string; onSelect?: (value: string) => void;
		multiple?: boolean; values?: string[]; onChange?: (values: string[]) => void;
		header?: Snippet; summary?: string; emptyLabel?: string;
	} = $props();
	let open = $state(false), query = $state('');
	let root: HTMLDivElement, triggerEl: HTMLButtonElement;
	let menuStyle = $state('');
	const valueOpt = $derived(options.find(o => o.value === value));
	const selected = $derived(multiple ? values : [value]);
	const label = $derived(summary ?? (multiple ? values.length ? `${values.length} selected` : placeholder : valueOpt?.label ?? placeholder));
	const choices = $derived(multiple ? options : [{ value: '', label: 'All languages' }, ...options]);
	function place() {
		if (!triggerEl) return;
		const r = triggerEl.getBoundingClientRect();
		const width = Math.min(Math.max(r.width, multiple ? 320 : 250), window.innerWidth - 16);
		const left = Math.min(Math.max(8, r.left), window.innerWidth - width - 8);
		const below = window.innerHeight - r.bottom - 13;
		const above = r.top - 13;
		const up = below < 260 && above > below;
		menuStyle = `${up ? `bottom:${window.innerHeight - r.top + 5}` : `top:${r.bottom + 5}`}px;left:${left}px;width:${width}px;max-height:${Math.max(120, up ? above : below)}px;`;
	}
	function close(focus = false) { open = false; if (focus) triggerEl?.focus(); }
	function pick(id: string) {
		if (multiple) onChange?.(values.includes(id) ? values.filter(v => v !== id) : [...values, id]);
		else { onSelect?.(id); close(true); }
	}
	$effect(() => {
		if (!open) return;
		place();
		const onDown = (event: MouseEvent) => { if (!root.contains(event.target as Node)) close(); };
		const onFocus = (event: FocusEvent) => { if (!root.contains(event.target as Node)) close(); };
		const onKey = (event: KeyboardEvent) => {
			if (event.key === 'Escape' && root.contains(event.target as Node)) { event.preventDefault(); event.stopPropagation(); close(true); }
		};
		window.addEventListener('mousedown', onDown);
		window.addEventListener('focusin', onFocus);
		window.addEventListener('keydown', onKey, true);
		window.addEventListener('scroll', place, true);
		window.addEventListener('resize', place);
		return () => {
			window.removeEventListener('mousedown', onDown);
			window.removeEventListener('focusin', onFocus);
			window.removeEventListener('keydown', onKey, true);
			window.removeEventListener('scroll', place, true);
			window.removeEventListener('resize', place);
		};
	});
	async function show() { query = ''; open = !open; await tick(); place(); }
</script>

<div class="dd" bind:this={root}>
	<button type="button" class="trigger" class:active={open} bind:this={triggerEl} aria-label={multiple ? `Descendant languages: ${label}` : `${placeholder}: ${valueOpt?.label ?? 'All languages'}`} aria-expanded={open} onclick={show}>
		<span class="cur" class:placeholder={!multiple && !valueOpt}>{label}</span><span aria-hidden="true">⌄</span>
	</button>
	{#if open}
		<div class="panel" style={menuStyle}>
			{#if header}{@render header()}{/if}
			<SearchableOptions options={choices} bind:query {selected} {multiple} {emptyLabel} focusOnMount onSelect={pick}>
				{#snippet toolbar(matches)}
					{#if multiple}<div class="actions"><button type="button" onclick={() => onChange?.([])}>Use all languages</button><button type="button" disabled={!matches.length} onclick={() => onChange?.([...new Set([...values, ...matches.map(o => o.value)])])}>Select {query.trim() ? 'matches' : 'listed'}</button></div>{/if}
				{/snippet}
			</SearchableOptions>
			{#if multiple}<div class="footer"><span>{values.length ? `${values.length} selected` : 'All languages'}</span><button type="button" onclick={() => close(true)}>Done</button></div>{/if}
		</div>
	{/if}
</div>

<style>
	.dd {
		position: relative;
		display: inline-flex;
		width: 100%;
	}
	.trigger {
		display: inline-flex;
		align-items: center;
		justify-content: space-between;
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
	}
	.trigger.active {
		outline: none;
		border-color: var(--plum-2);
		box-shadow: 0 0 0 3px rgba(160, 46, 125, 0.15);
	}
	.cur {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.cur.placeholder {
		color: var(--muted);
	}

	.panel{position:fixed;z-index:65;box-sizing:border-box;overflow-y:auto;overscroll-behavior:contain;background:var(--surface);color:var(--ink);border:1px solid var(--border-strong);border-radius:12px;box-shadow:0 14px 38px #0004;padding:10px;text-align:left;font-weight:400}
	.actions,.footer{display:flex;align-items:center;justify-content:space-between;gap:.5rem;padding-top:.5rem;font-size:.72rem;color:var(--muted)}
	.actions button,.footer button{font:inherit;background:var(--surface);color:var(--ink);border:1px solid var(--border);border-radius:5px;padding:.35rem .45rem;cursor:pointer}
	.actions button:disabled{opacity:.4;cursor:default}.footer{border-top:1px solid var(--border);margin-top:.5rem}.panel button:focus-visible{outline:2px solid var(--plum-2);outline-offset:1px}
	@media(max-width:640px){.trigger{min-height:42px}}
</style>
