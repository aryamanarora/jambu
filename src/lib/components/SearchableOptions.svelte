<script lang="ts">
	import type { Snippet } from 'svelte';
	import { filterOptions, type SelectOption } from '$lib/languageOptions';
	let {
		options, query = $bindable(''), selected = [], multiple = false, action = '',
		placeholder = 'Find a language or branch…', searchLabel = 'Find languages or a branch',
		requireQuery = false, limit, focusOnMount = false, emptyLabel = 'No matching languages',
		onSelect, toolbar
	}: {
		options: SelectOption[]; query?: string; selected?: string[]; multiple?: boolean; action?: string;
		placeholder?: string; searchLabel?: string; requireQuery?: boolean; limit?: number;
		focusOnMount?: boolean; emptyLabel?: string; onSelect: (value: string) => void;
		toolbar?: Snippet<[SelectOption[]]>;
	} = $props();
	let searchEl: HTMLInputElement;
	let listEl = $state<HTMLUListElement>();
	const matches = $derived(filterOptions(options, query));
	const visible = $derived(limit == null ? matches : matches.slice(0, limit));
	$effect(() => { if (focusOnMount) searchEl?.focus(); });
	function move(event: KeyboardEvent, index: number) {
		const buttons = [...(listEl?.querySelectorAll<HTMLButtonElement>('button') ?? [])];
		if (!buttons.length) return;
		let next: number;
		if (event.key === 'ArrowDown') next = Math.min(index + 1, buttons.length - 1);
		else if (event.key === 'ArrowUp') next = index - 1;
		else if (index >= 0 && event.key === 'Home') next = 0;
		else if (index >= 0 && event.key === 'End') next = buttons.length - 1;
		else return;
		event.preventDefault();
		if (next < 0) searchEl.focus();
		else buttons[next]?.focus();
	}
</script>

<input class="search" type="search" {placeholder} aria-label={searchLabel} bind:value={query} bind:this={searchEl} autocomplete="off" onkeydown={event => move(event, -1)} />
{#if toolbar}{@render toolbar(matches)}{/if}
{#if !requireQuery || query.trim()}
	<ul class="options" bind:this={listEl} aria-label="Languages">
		{#each visible as option, index (option.value)}
			<li><button type="button" class:selected={selected.includes(option.value)} aria-pressed={multiple ? selected.includes(option.value) : undefined} aria-current={!multiple && selected.includes(option.value) ? 'true' : undefined} onclick={() => onSelect(option.value)} onkeydown={event => move(event, index)}>
				{#if multiple}<span class="check" aria-hidden="true">{selected.includes(option.value) ? '✓' : ''}</span>{/if}
				<span class="swatch" style:background={option.swatch ?? 'transparent'} aria-hidden="true"></span>
				<span class="text"><span class="label">{option.label}</span>{#if option.sub}<span class="sub">{option.sub}</span>{/if}{#if option.note}<span class="note">{option.note}</span>{/if}</span>
				{#if action}<span class="action" aria-hidden="true">{action}</span>{/if}
			</button></li>
		{/each}
		{#if !matches.length}<li class="empty" role="status">{emptyLabel}</li>{/if}
	</ul>
	{#if visible.length < matches.length}<p class="more">Showing {visible.length} of {matches.length}. Refine your search.</p>{/if}
{/if}

<style>
	.search{width:100%;box-sizing:border-box;font:inherit;font-size:.85rem;padding:7px 10px;border:1px solid var(--border-strong);border-radius:8px;background:var(--bg);color:var(--ink)}
	.search:focus{outline:2px solid var(--plum-2);outline-offset:1px}
	.options{list-style:none;margin:8px 0 0;padding:0;max-height:280px;overflow-y:auto;overscroll-behavior:contain;min-height:0}
	.options button{display:flex;align-items:center;gap:8px;width:100%;background:none;border:0;padding:7px 6px;border-radius:6px;cursor:pointer;color:var(--ink);text-align:left;font:inherit}
	.options button:hover{background:var(--surface-2)}.options button:focus-visible{outline:2px solid var(--plum-2);outline-offset:-2px}
	.options button.selected{background:color-mix(in srgb,var(--plum-2) 12%,var(--surface))}
	.swatch{width:11px;height:11px;border-radius:3px;flex:none;border:1px solid #0003}
	.text{display:flex;align-items:baseline;flex-wrap:wrap;gap:2px 8px;flex:1;min-width:0}.label{flex:1;font-size:.85rem;overflow-wrap:anywhere}.sub{color:var(--muted);font-size:.7rem}.note{flex-basis:100%;font-size:.68rem;color:var(--muted);font-variant-numeric:tabular-nums}
	.check{display:grid;place-items:center;width:15px;height:15px;border:1px solid var(--border-strong);border-radius:3px;flex:none;font-size:.7rem}.selected .check{background:var(--plum-2);color:var(--surface);border-color:var(--plum-2)}
	.action{color:var(--plum-2)}.empty,.more{padding:8px;font-size:.78rem;color:var(--muted);text-align:center}.more{margin:0}
	@media(max-width:640px){.options button{min-height:42px}}
</style>
