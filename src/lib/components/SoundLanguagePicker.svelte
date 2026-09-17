<script lang="ts">
	import SelectFilter from './SelectFilter.svelte';
	import { languageOptions } from '$lib/languageOptions';
	import { favorites } from '$lib/prefs.svelte';
	import { matchesLanguageCounts, languageCountError, LANGUAGE_COUNT_FIELDS, type LanguageCountFilters } from '$lib/soundStudy';
	import type { Language } from '$lib/types';
	let { languages, counts, values, filters, onChange, onCounts }: {
		languages: Language[]; counts?: Map<string, number>; values: string[];
		filters: LanguageCountFilters; onChange: (values: string[]) => void;
		onCounts: (patch: Partial<LanguageCountFilters>) => void;
	} = $props();
	const error = $derived(languageCountError(filters));
	const limited = $derived(LANGUAGE_COUNT_FIELDS.some(key => filters[key]));
	const eligible = $derived(languages.filter(l => matchesLanguageCounts(l, counts ? counts.get(l.id) ?? 0 : undefined, filters)));
	const options = $derived(languageOptions(eligible).map((option, index) => ({
		...option, note: `${eligible[index].lemma_count.toLocaleString()} total · ${counts ? (counts.get(option.value) ?? 0).toLocaleString() : '…'} outcomes`
	})));
	const favoriteIds = $derived(eligible.filter(l => favorites.has('lang', l.id) || favorites.has('clade', l.clade)).map(l => l.id));
	const ranges = [
		{ label: 'Total forms', min: 'totalMin', max: 'totalMax' },
		{ label: 'Outcome forms', min: 'outcomeMin', max: 'outcomeMax' }
	] as const;
	const rangeLabel = (min: string, max: string) => min && max ? `${Number(min).toLocaleString()}–${Number(max).toLocaleString()}` : min ? `≥ ${Number(min).toLocaleString()}` : `≤ ${Number(max).toLocaleString()}`;
</script>

<SelectFilter placeholder="All languages" {options} multiple {values} {onChange} summary={`${values.length ? `${values.length} selected` : 'All languages'}${limited ? ' · form counts' : ''}`} emptyLabel="No languages match these filters">
	{#snippet header()}
		<details class="counts" open={limited}>
			<summary>Filter by form counts</summary>
			<div class="ranges">
				{#each ranges as range}
					<fieldset><legend>{range.label}</legend>
						<label><span>Min</span><input type="number" min="0" step="1" placeholder="0" aria-label={`${range.label} minimum`} value={filters[range.min]} oninput={event => onCounts({ [range.min]: event.currentTarget.value })} /></label>
						<label><span>Max</span><input type="number" min="0" step="1" placeholder="Any" aria-label={`${range.label} maximum`} value={filters[range.max]} oninput={event => onCounts({ [range.max]: event.currentTarget.value })} /></label>
					</fieldset>
				{/each}
			</div>
			<p>Total = all forms in Jambu. Outcomes = distinct forms matching this comparison, across all input groups.</p>
			{#if limited}<button type="button" class="clear" onclick={() => onCounts({ totalMin: '', totalMax: '', outcomeMin: '', outcomeMax: '' })}>Clear count filters</button>{/if}
		</details>
		{#if !counts}<p class="pending">Run the comparison to refresh outcome counts.</p>{/if}
		{#if error}<p class="error" role="alert">{error}</p>{/if}
		<div class="available"><span>{eligible.length} languages{limited ? ' within limits' : ''}</span>{#if favoriteIds.length}<button type="button" onclick={() => onChange(favoriteIds)}>Use favorites</button>{/if}</div>
	{/snippet}
</SelectFilter>
{#if limited}
	<div class="chips" aria-label="Language count filters">
		{#each ranges as range}{#if filters[range.min] || filters[range.max]}<button type="button" aria-label={`Remove ${range.label.toLowerCase()} limits`} onclick={() => onCounts({ [range.min]: '', [range.max]: '' })}>{range.label} {rangeLabel(filters[range.min], filters[range.max])} ×</button>{/if}{/each}
	</div>
{/if}

<style>
	.counts{border-bottom:1px solid var(--border);padding:0 0 .65rem;margin-bottom:.6rem}.counts summary{cursor:pointer;font-size:.78rem;color:var(--ink);padding:.2rem 0}
	.ranges{display:grid;gap:.6rem;margin-top:.6rem}fieldset{border:0;padding:0;margin:0;display:flex;gap:.5rem;min-width:0}legend{font-size:.72rem;color:var(--ink);margin-bottom:.25rem;padding:0}label{display:flex;align-items:center;gap:.3rem;flex:1;min-width:0;font-size:.68rem;color:var(--muted)}input{min-width:0;width:100%;font:inherit;font-size:.78rem;color:var(--ink);background:var(--bg);border:1px solid var(--border-strong);border-radius:4px;padding:.3rem .4rem}
	p{font-size:.68rem;line-height:1.5;color:var(--muted);margin:.5rem 0 0}.error{color:var(--bad)}.pending{margin:0 0 .5rem}.available{display:flex;align-items:center;justify-content:space-between;gap:.5rem;font-size:.68rem;color:var(--muted);margin-bottom:.6rem}
	button{font:inherit;cursor:pointer;color:var(--ink);border:1px solid var(--border);border-radius:5px;background:var(--surface);padding:.3rem .4rem}.clear{font-size:.68rem;margin-top:.4rem}
	.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.6rem}.chips button{font-size:.7rem;padding:.3rem .5rem;border-radius:1rem}
	input:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid var(--plum-2);outline-offset:2px}
</style>
