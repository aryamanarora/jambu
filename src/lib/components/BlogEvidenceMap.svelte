<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import Map from './Map.svelte';
	import type { BlogMap, BlogMapPoint } from '$lib/blog/charts';
	let { data, colors, label }: { data: BlogMap; colors: string[]; label: string } = $props();
	let host: HTMLDivElement;
	let visible = $state(false);
	let group = $state('All');
	let selectedId = $state('');
	let points = $derived(data.points.filter((p) => group === 'All' || p.group === group));
	let selected = $derived(points.find((p) => p.id === selectedId));
	$effect(() => { if (selectedId && !points.some((p) => p.id === selectedId)) selectedId = ''; });
	let missing = $derived(points.filter((p) => p.latitude === null || p.longitude === null));
	const escape = (s: string) => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
	const color = (i: number) => /no included|no resolved/i.test(data.categories[i]) ? '#85858c' : colors[i % colors.length];
	function icon(p: BlogMapPoint) {
		const sum = p.values.reduce((a, b) => a + b, 0);
		let angle = -Math.PI / 2;
		let paths = '';
		for (let i = 0; i < p.values.length; i++) {
			if (!p.values[i]) continue;
			const end = angle + 2 * Math.PI * p.values[i] / sum;
			paths += p.values[i] === sum ? `<rect width="24" height="24" fill="${color(i)}"/>` : `<path d="M12 12 L${12 + 18 * Math.cos(angle)} ${12 + 18 * Math.sin(angle)} A18 18 0 ${end - angle > Math.PI ? 1 : 0} 1 ${12 + 18 * Math.cos(end)} ${12 + 18 * Math.sin(end)} Z" fill="${color(i)}"/>`;
			angle = end;
		}
		const shape = p.group === 'Dardic' ? '<circle cx="12" cy="12" r="10"/>' : '<rect x="2" y="2" width="20" height="20" rx="2"/>';
		return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><defs><clipPath id="point"><circle cx="12" cy="12" r="10"/></clipPath></defs><g fill="#fff">${shape}</g><g clip-path="url(#point)">${paths}</g><g fill="none" stroke="${p.id === selectedId ? '#b34f85' : '#25232c'}" stroke-width="${p.id === selectedId ? 3 : 1.5}">${shape}</g></svg>`;
	}
	let markers = $derived(points.filter((p) => p.latitude !== null && p.longitude !== null).map((p) => ({
		lat: p.latitude!, long: p.longitude!, svg: icon(p), size: p.id === selectedId ? 16 : 10,
		foreground: p.id === selectedId,
		tooltip: `${escape(p.label)} · ${p.group}<br>${p.values.map((v, i) => v ? `${escape(data.categories[i])}: ${Math.round(v * 100)}%` : '').filter(Boolean).join(' · ')}`,
		onClick: () => { selectedId = p.id; }
	})));
	onMount(() => {
		const observer = new IntersectionObserver(([entry]) => {
			if (entry.isIntersecting) { visible = true; observer.disconnect(); }
		}, { rootMargin: '250px' });
		observer.observe(host);
		return () => observer.disconnect();
	});
</script>

<div class="evidence-map" bind:this={host}>
	<div class="map-heading"><strong>{label} on the map</strong><span>○ Dardic · □ Plains</span></div>
	<div class="map-controls">
		<label>Map group<select aria-label="Map group" bind:value={group}><option>All</option><option>Dardic</option><option>Plains</option></select></label>
		<label>Inspect language<select aria-label="Inspect language" bind:value={selectedId}><option value="">Choose a language or click a point</option>{#each points as p}<option value={p.id}>{p.label}{p.latitude === null || p.longitude === null ? ' (no coordinates)' : ''}</option>{/each}</select></label>
	</div>
	{#if visible}
		{#key group}<Map {markers} height="320px" bounds={group === 'Dardic' ? [[32, 69], [37, 77]] : [[7, 58], [38, 96]]} fitOnce mutedTiles animateZoom={false} />{/key}
	{:else}
		<div class="placeholder">The interactive map loads when it comes into view.</div>
	{/if}
	<ul class="map-legend">{#each data.categories as category, i}<li><span style:background={color(i)}></span>{category}</li>{/each}</ul>
	<p class="map-note">{markers.length} located / {points.length} attested units{missing.length ? `; ${missing.length} without coordinates remain in the bars and language selector` : ''}. {data.note} The map-group filter affects only the map.</p>
	<div class="point-detail" aria-live="polite">
		{#if selected}
			<strong>{selected.label} · {selected.group}</strong>
			<p>{selected.locationLabel}</p>
			<p>Resolved families: {#each selected.families as family, i}{#if i}, {/if}<a href={`${base}/entries/${encodeURIComponent(family.id)}`}>{family.label}</a>{:else}none included{/each}.</p>
			<p>{selected.unresolved} unresolved records · {selected.loans} excluded loan records.</p>
			<ul>{#each selected.examples as e}<li>{e.language} <a href={`${base}/entries/${encodeURIComponent(e.id)}`}>{e.form}</a> “{e.gloss}” <span class="status">{e.status}</span></li>{/each}</ul>
			<p>Representative records shown; the evidence download retains all records and source locators.</p>
		{:else}
			<p>Click a point or choose a language to inspect its families, forms and unresolved evidence. Split markers show fractional votes across the displayed categories.</p>
		{/if}
	</div>
	<noscript>Use the language memberships and evidence downloads below for the complete geographic evidence.</noscript>
</div>

<style>
	.evidence-map { margin: 1.25rem 0; padding-top: 1rem; border-top: 1px solid var(--border); }
	.map-heading { display: flex; justify-content: space-between; flex-wrap: wrap; gap: .5rem; }
	.map-heading span { color: var(--muted); font-size: .75rem; }
	.map-controls { display: flex; flex-wrap: wrap; gap: .75rem; margin: .8rem 0; }
	label { display: grid; gap: .25rem; font-size: .75rem; min-width: 0; }
	label:last-child { flex: 1; }
	select { font: inherit; color: inherit; background: var(--surface); border: 1px solid var(--border-strong); border-radius: 5px; padding: .4rem; width: 100%; min-width: 0; }
	.map-legend { display: flex; flex-wrap: wrap; list-style: none; gap: .35rem .8rem; padding: 0; margin: .75rem 0; font-size: .7rem; }
	.map-legend li { display: flex; align-items: center; gap: .3rem; }
	.map-legend span { width: .65rem; height: .65rem; border-radius: 2px; }
	.map-note, .point-detail { font-size: .75rem; line-height: 1.6; color: var(--muted); }
	.point-detail { background: var(--surface-2); padding: .75rem; border-radius: 6px; }
	.point-detail strong { color: var(--text); }
	.point-detail p { margin: .35rem 0 !important; }
	.point-detail ul { padding-left: 1.2rem; }
	.status { font-size: .65rem; }
	.placeholder { display: grid; place-content: center; height: 320px; background: var(--surface-2); color: var(--muted); font-size: .75rem; }
	@media (max-width: 500px) { .map-controls { display: grid; grid-template-columns: 1fr; } }
</style>
