<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import type { BlogChart } from '$lib/blog/charts';
	import BlogEvidenceMap from './BlogEvidenceMap.svelte';
	let { chart }: { chart: BlogChart } = $props();
	let viewIndex = $state(0);
	let mode = $state<'share' | 'count'>('share');
	let interactive = $state(false);
	let showOther = $state(false);
	let familyMode = $state<'head' | 'entry'>('entry');
	let hasModes = $derived(chart.views.some((v) => v.familyMode));
	let availableViews = $derived(chart.views.map((view, index) => ({ view, index })).filter(({ view }) => !view.familyMode || view.familyMode === familyMode));
	$effect(() => {
		if (hasModes && chart.views[viewIndex]?.familyMode !== familyMode) {
			const label = chart.views[viewIndex]?.label;
			viewIndex = availableViews.find(({ view }) => view.label === label)?.index ?? availableViews[0]?.index ?? 0;
		}
	});
	onMount(() => { interactive = true; });
	let view = $derived(chart.views[viewIndex]);
	const total = (values: number[]) => values.reduce((a, b) => a + b, 0);
	let maximum = $derived(Math.max(1, ...view.rows.map((row) => total(row.values))));
	const colors = ['#346e69', '#a8542c', '#756296', '#51687f', '#7d681e', '#88546a', '#627565', '#706f74'];
	const categoryColor = (category: string, i: number) => /no included|no resolved/i.test(category) ? '#85858c' : colors[i % colors.length];
	const percentage = (n: number, denominator: number) => denominator ? (100 * n / denominator).toFixed(1) : '0.0';
	const display = (n: number) => Number(n.toFixed(2)).toLocaleString('en', { maximumFractionDigits: 2 });
</script>

<figure class="evidence-chart" aria-labelledby={`chart-${chart.id}`}>
	<figcaption id={`chart-${chart.id}`}><span class="eyebrow">The evidence</span><strong>{chart.title}</strong></figcaption>
	{#if interactive}
		<div class="controls">
			{#if hasModes}<label>Counting <select aria-label="Counting" bind:value={familyMode}><option value="entry">Entry families (collapse subheads)</option><option value="head">Separate headwords</option></select></label>{/if}
			{#if availableViews.length > 1}
				<label>Comparison <select aria-label="Comparison" bind:value={viewIndex}>{#each availableViews as option}<option value={option.index}>{option.view.label}</option>{/each}</select></label>
			{/if}
			<div class="switch" aria-label="Chart scale">
				<button type="button" aria-pressed={mode === 'share'} onclick={() => mode = 'share'}>Proportion</button>
				<button type="button" aria-pressed={mode === 'count'} onclick={() => mode = 'count'}>{view.fractionalVotes ? 'Votes' : 'Count'}</button>
			</div>
		</div>
	{/if}
	<p class="unit">{view.unit} · {mode === 'share' ? 'Each bar totals 100%' : view.fractionalVotes ? 'Bars share a vote scale' : 'Bars share a count scale'}</p>
	<ul class="legend" aria-label="Outcomes">{#each view.categories as category, i}<li><span style:background={categoryColor(category, i)}></span>{#if category === 'Other resolved families' && view.otherFamilies}<button class="legend-detail" aria-expanded={showOther} onclick={() => { showOther = !showOther; }}>Other resolved families ({view.otherFamilies.length})</button>{:else}{category}{/if}</li>{/each}</ul>
	<div class="plot">
		{#each view.rows as row}
			<div class="chart-row">
				<div class="row-label"><span>{row.label}</span><span class="n">n = {display(total(row.values))}</span></div>
				<div class="track" role="img" aria-label={`${row.label}: ${row.values.map((n, i) => `${view.categories[i]} ${display(n)}`).join(', ')}`}>
					{#if total(row.values) === 0}<span class="no-data">No candidates in this domain</span>{/if}
					{#each row.values as n, i}{#if n > 0}
						<span class="segment" style:background={categoryColor(view.categories[i], i)} style:width={`${100 * n / (mode === 'share' ? total(row.values) : maximum)}%`} title={`${view.categories[i]}: ${display(n)}/${display(total(row.values))} (${percentage(n, total(row.values))}%)`}>
							{#if view.categories[i] === 'Other resolved families' && view.otherFamilies}<button class="segment-detail" aria-label={`Show other resolved families for ${row.label}`} onclick={() => { showOther = true; }}>{#if n / (mode === 'share' ? total(row.values) : maximum) >= .08}{mode === 'share' ? `${Math.round(100 * n / total(row.values))}%` : display(n)}{:else}<span class="detail-dot">⋯</span>{/if}</button>{:else if n / (mode === 'share' ? total(row.values) : maximum) >= .08}<span>{mode === 'share' ? `${Math.round(100 * n / total(row.values))}%` : display(n)}</span>{/if}
						</span>
					{/if}{/each}
				</div>
			</div>
		{/each}
	</div>
	{#if view.otherFamilies}
		<details class="other-families" bind:open={showOther}>
			<summary>Other resolved families: {view.otherFamilies.length} etyma</summary>
			<p class="note">Every etymon inside “Other resolved families” for {view.label}. Values are fractional language votes, followed by their share of the displayed group bar.</p>
			<!-- svelte-ignore a11y_no_noninteractive_tabindex (Keyboard users need access to horizontal table scrolling.) -->
			<div class="counts-scroll" role="region" aria-label="Other resolved family contributions" tabindex="0">
				<table><thead><tr><th>Family</th>{#each view.rows as row}<th>{row.label}</th>{/each}</tr></thead><tbody>
					{#each view.otherFamilies as family}<tr><th><a href={`${base}/entries/${encodeURIComponent(family.id)}`}>{family.label}</a></th>{#each view.rows as row, i}<td>{display(family.values[i])} ({percentage(family.values[i], total(row.values))}%)<small>{family.languages[i] || 'No linked attestations'}</small></td>{/each}</tr>{/each}
				</tbody></table>
			</div>
		</details>
	{/if}
	<p class="note" aria-live="polite">{view.note}</p>
	{#if view.map}
		<BlogEvidenceMap data={view.map} colors={colors} label={view.label} />
	{/if}
	<details>
		<summary>{chart.views.some((v) => v.fractionalVotes) ? 'Values and all comparison scopes (votes rounded to 2 decimals)' : 'Exact counts and all comparison scopes'}</summary>
		{#each chart.views as tableView}
			<!-- svelte-ignore a11y_no_noninteractive_tabindex (Horizontal table scrolling must be available to keyboard users.) -->
			<div class="counts-scroll" tabindex="0" role="region" aria-label={`${tableView.label} counts`}>
					<table><caption>{tableView.label}{tableView.familyMode ? ` · ${tableView.familyMode === 'entry' ? 'Entry families' : 'Separate headwords'}` : ''} · {tableView.unit}</caption><thead><tr><th scope="col">Input / group</th>{#each tableView.categories as c}<th scope="col">{c}</th>{/each}<th scope="col">Total</th></tr></thead>
					<tbody>{#each tableView.rows as row}<tr><th scope="row">{row.label}</th>{#each row.values as n}<td title={String(n)}>{display(n)}</td>{/each}<td>{display(total(row.values))}</td></tr>{/each}</tbody>
				</table>
			</div>
			<p class="note">{tableView.note}</p>
		{/each}
	</details>
	<p class="downloads">Audited data: {#each chart.sources as source, i}{#if i > 0} · {/if}<a href={`${base}${chart.sourceBase ?? '/research/shinaic-accent/tables'}/${source}`} download>{source}</a>{/each}</p>
</figure>

<style>
	.evidence-chart { font-family: var(--font-sans); font-size: .875rem; line-height: 1.5; margin: 1.75rem 0 2rem; padding: 1.25rem; border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface); overflow: hidden; }
	figcaption { display: grid; gap: .35rem; margin-bottom: 1rem; }
	.eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .65rem; color: var(--muted); }
	figcaption strong { font-size: 1rem; font-weight: 600; }
	.controls { display: flex; align-items: end; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-bottom: 1rem; }
	label { display: grid; gap: .3rem; font-size: .75rem; min-width: 0; max-width: 100%; }
	select, button { font: inherit; color: inherit; background: var(--surface); border: 1px solid var(--border-strong); border-radius: 5px; padding: .45rem .65rem; }
	select { width: 100%; min-width: 0; max-width: 100%; box-sizing: border-box; }
	.switch { display: flex; gap: .25rem; }
	button { cursor: pointer; }
	button[aria-pressed='true'] { background: var(--surface-2); font-weight: 600; box-shadow: inset 0 -2px #346e69; }
	button:focus-visible, select:focus-visible, summary:focus-visible { outline: 2px solid #8070a8; outline-offset: 3px; }
	.unit { color: var(--muted); font-size: .75rem; margin: 0 0 .65rem !important; }
	.legend { display: flex; flex-wrap: wrap; gap: .4rem 1rem; padding: 0; margin: 0 0 1.2rem; list-style: none; font-size: .75rem; }
	.legend li { display: flex; align-items: center; gap: .35rem; }
	.legend li span { width: .65rem; height: .65rem; border-radius: 2px; }
	.legend-detail { border: 0; background: none; padding: 0; text-decoration: underline; text-underline-offset: .2em; font-size: inherit; }
	.segment-detail { border: 0; border-radius: 0; background: none; color: inherit; width: 100%; height: 100%; padding: 0; font: inherit; }
	.segment-detail:hover { background: #ffffff22; }
	.other-families { margin-top: 1rem; }
	.other-families table { display: table; min-width: 540px; width: 100%; overflow-wrap: normal; }
	.other-families th:first-child { min-width: 110px; }
	.other-families td { min-width: 160px; }
	.other-families small { display: block; margin-top: .3rem; color: var(--muted); font-size: .7rem; min-width: 8rem; }
	.plot { display: grid; gap: .9rem; }
	.row-label { display: flex; align-items: baseline; justify-content: space-between; gap: .5rem; font-size: .8rem; margin-bottom: .3rem; }
	.n { white-space: nowrap; color: var(--muted); font-variant-numeric: tabular-nums; }
	.track { display: flex; height: 1.65rem; background: var(--surface-2); border-radius: 3px; overflow: hidden; }
	.segment { display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: .7rem; min-width: 1px; }
	.no-data { color: var(--muted); font-size: .75rem; padding: .2rem .5rem; }
	.note { font-size: .8rem; color: var(--muted); margin: 1rem 0 !important; }
	details { border-top: 1px solid var(--border); padding-top: .8rem; }
	summary { cursor: pointer; font-size: .8rem; }
	.counts-scroll { overflow-x: auto; margin: 1rem 0; }
	table { font-size: .75rem !important; font-variant-numeric: tabular-nums; }
	caption { text-align: left; font-weight: 600; margin-bottom: .5rem; }
	th, td { padding: .4rem .5rem !important; }
	.downloads { font-size: .7rem; color: var(--muted); margin: .8rem 0 0 !important; overflow-wrap: anywhere; }
	@media (max-width: 500px) { .evidence-chart { padding: .85rem; } .controls { align-items: start; flex-direction: column; } }
	@media print { .controls { display: none; } .evidence-chart { break-inside: avoid; } }
</style>
