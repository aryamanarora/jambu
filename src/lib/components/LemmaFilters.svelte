<script lang="ts">
	import type { ListParams } from '$lib/types';
	import type { SelectOption } from '$lib/languageOptions';
	import { ENTRY_TYPES, type FilterMode } from '$lib/listFilters';
	import FilterField from './FilterField.svelte';
	import SelectFilter from './SelectFilter.svelte';
	import SearchMatchToggle from './SearchMatchToggle.svelte';
	import TagFilter from './TagFilter.svelte';
	import SourceFilter from './SourceFilter.svelte';

	let {
		params, mode, showLanguage = true, languages = [], originLanguages = [], debounceMs = 250, onFilter
	}: {
		params: ListParams;
		mode: FilterMode;
		showLanguage?: boolean;
		languages?: SelectOption[];
		originLanguages?: SelectOption[];
		debounceMs?: number;
		onFilter: (key: string, value: string) => void;
	} = $props();
</script>

<SearchMatchToggle relaxed={params.relaxed} onToggle={(value) => onFilter('relaxed', value ? '1' : '')} />
<FilterField label="Form" placeholder="Filter forms…" palette {debounceMs} value={params.form} onValue={(value) => onFilter('form', value)} />
{#if showLanguage}
	<label class="filter-control">
		<span>Language</span>
		<SelectFilter placeholder="Any language" options={languages} value={params.origin_lang} onSelect={(value) => onFilter('origin_lang', value)} />
	</label>
{/if}
{#if mode === 'forms'}
	<label class="filter-control">
		<span>Origin language</span>
		<SelectFilter placeholder="Any origin language" options={originLanguages} value={params.etymon_lang} onSelect={(value) => onFilter('etymon_lang', value)} />
	</label>
	<FilterField label="Origin form" palette {debounceMs} value={params.origin} onValue={(value) => onFilter('origin', value)} />
{/if}
<FilterField label="Meaning" placeholder="Filter meanings…" palette {debounceMs} value={params.gloss} onValue={(value) => onFilter('gloss', value)} />
{#if mode === 'entries'}
	<FilterField label="Etymology" placeholder="Filter etymologies…" palette {debounceMs} value={params.etymology} onValue={(value) => onFilter('etymology', value)} />
{:else}
	<FilterField label="Notes" palette {debounceMs} value={params.notes} onValue={(value) => onFilter('notes', value)} />
{/if}
<TagFilter standalone value={params.tags} {onFilter} />
<SourceFilter standalone value={params.source} {onFilter} onSort={() => {}} />
{#if mode === 'entries'}
	<div class="filter-control entry-types">
		<span>Entry type</span>
		<div class="toggle-group">
			{#each ENTRY_TYPES as type (type.key)}
				<button type="button" class:on={params[type.state]} aria-pressed={!!params[type.state]} title={type.title}
					onclick={() => onFilter(type.key, params[type.state] ? '' : '1')}>{type.label}</button>
			{/each}
		</div>
	</div>
{/if}

<style>
	.entry-types { grid-column: 1 / -1; }
	.toggle-group { display: flex; flex-wrap: wrap; gap: 0.4rem; }
	.toggle-group button {
		font-family: var(--font-sans); font-size: 0.82rem; font-weight: 500;
		padding: 3px 14px; border: 1px solid var(--border-strong); border-radius: 999px;
		background: var(--surface); color: var(--muted); cursor: pointer; white-space: nowrap;
		transition: background 0.12s, color 0.12s, border-color 0.12s;
	}
	.toggle-group button:hover { color: var(--ink); }
	.toggle-group button.on { background: var(--plum); border-color: var(--plum); color: #fbeefb; }
	@media (max-width: 640px) {
		.toggle-group { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
		.toggle-group button { min-height: 40px; padding-inline: 12px; white-space: normal; }
	}
</style>
