<script lang="ts">
	import { base } from '$app/paths';
	import type { MapMarker } from '$lib/types';
	import Map from '$lib/components/Map.svelte';
	import ReflexesView from '$lib/components/ReflexesView.svelte';
	import Donut from '$lib/components/Donut.svelte';
	import Tags from '$lib/components/Tags.svelte';
	import {
		getLanguageDialects,
		getLanguageTags,
		getOriginLangDistribution,
		getReferenceDistribution,
		type OriginSlice
	} from '$lib/query';
	import { tagCategory, type TagCategory } from '$lib/tags';
	import { hashColor } from '$lib/clades';
	import type { Dialect } from '$lib/types';

	let { data } = $props();
	const lang = $derived(data.language);

	// distribution of this language's reflexes by the language they descend from (client-side)
	let origins = $state<OriginSlice[]>([]);
	let references = $state<OriginSlice[]>([]);
	let languageTags = $state<string[]>([]);
	let dialects = $state<Dialect[]>([]);
	let curLang = '';
	$effect(() => {
		if (lang.id !== curLang) {
			curLang = lang.id;
			origins = [];
			references = [];
			languageTags = [];
			dialects = [];
			getOriginLangDistribution(lang.id).then((o) => (origins = o));
			getReferenceDistribution(lang.id).then((r) => (references = r));
			getLanguageTags(lang.id).then((t) => (languageTags = t));
			getLanguageDialects(lang.id).then((d) => (dialects = d));
		}
	});
	const tagGroups: Array<{ category: TagCategory; label: string }> = [
		{ category: 'dialect', label: 'Dialects' },
		{ category: 'gender', label: 'Gender' },
		{ category: 'grammatical', label: 'Grammatical' },
		{ category: 'source', label: 'Sources' },
		{ category: 'era', label: 'Eras' }
	];
	function tagsFor(category: TagCategory): string[] {
		return languageTags.filter((tag) => tagCategory(tag) === category);
	}

	const markers = $derived<MapMarker[]>(
		[
			...(lang.lat != null
				? [{ lat: lang.lat, long: lang.long, svg: lang.map_marker, tooltip: lang.name }]
				: []),
			...dialects
				.filter((d) => d.lat != null && d.long != null)
				.map((d) => ({
					lat: d.lat!,
					long: d.long!,
					svg: lang.map_marker,
					tooltip: `${lang.name}: ${d.name}`
				}))
		]
	);
</script>

<svelte:head>
	<title>{lang.name} — Jambu</title>
	<meta name="description" content="The lexicon of {lang.name} ({lang.clade}) in the Jambu etymological dictionary — {lang.lemma_count} reflexes." />
</svelte:head>

<h1 class="headword">{lang.name} <span class="id-tag">[{lang.id}]</span></h1>

<div class="lang-header">
	<dl class="props card">
		<div class="prop"><dt>Family</dt><dd>{lang.clade}</dd></div>
		{#if lang.glottocode}
			<div class="prop">
				<dt>Glottolog</dt>
				<dd>
					<a href="https://glottolog.org/resource/languoid/id/{lang.glottocode}" rel="noreferrer"
						>{lang.glottocode}</a
					>
				</dd>
			</div>
		{/if}
		{#if lang.lat != null}
			<div class="prop">
				<dt>Coordinates</dt>
				<dd class="muted">{lang.lat?.toFixed(3)}, {lang.long?.toFixed(3)}</dd>
			</div>
		{/if}
		<div class="prop"><dt>Reflexes</dt><dd>{lang.lemma_count.toLocaleString()}</dd></div>
	</dl>
	{#if markers.length}
		<div class="lang-map"><Map {markers} zoom={5} height="260px" /></div>
	{/if}
</div>

{#if languageTags.length}
	<section class="tag-summary">
		<h2>Tags</h2>
		<div class="tag-groups card">
			{#each tagGroups as group}
				{@const found = tagsFor(group.category)}
				{#if found.length}
					<div class="tag-group">
						<h3>{group.label}</h3>
						<Tags tags={found.join(' ')} />
					</div>
				{/if}
			{/each}
		</div>
	</section>
{/if}

{#if dialects.length}
	<section class="dialect-metadata">
		<h2>Dialect metadata</h2>
		<div class="table-wrap">
			<table class="data accent-col">
				<thead>
					<tr>
						<th>Dialect</th>
						<th>Clade</th>
						<th>Glottocode</th>
						<th>Location</th>
						<th>Survey quality</th>
						<th>Coordinates</th>
						<th class="numeric">Reflexes</th>
					</tr>
				</thead>
				<tbody>
					{#each dialects as dialect (dialect.token)}
						<tr>
							<td class="lang-cell" style="border-left-color: {hashColor(dialect.color)}"
								>{dialect.name}</td
							>
							<td>{dialect.clade ?? ''}</td>
							<td>
								{#if dialect.glottocode}
									<a
										href="https://glottolog.org/resource/languoid/id/{dialect.glottocode}"
										rel="noreferrer">{dialect.glottocode}</a
									>
								{/if}
							</td>
							<td>{dialect.location ?? ''}</td>
							<td class="muted">{dialect.quality ?? ''}</td>
							<td class="muted"
								>{dialect.lat != null && dialect.long != null
									? `${dialect.lat.toFixed(3)}, ${dialect.long.toFixed(3)}`
									: ''}</td
							>
							<td class="numeric">{dialect.lemma_count.toLocaleString()}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</section>
{/if}

{#if origins.length || references.length}
	<div class="donut-row">
		{#if origins.length}
			<section class="origins">
				<h2>Origins</h2>
				<Donut slices={origins} />
			</section>
		{/if}
		{#if references.length}
			<section class="origins">
				<h2>References</h2>
				<Donut slices={references} unit="citations" label="Distribution of references" />
			</section>
		{/if}
	</div>
{/if}

<h2>Lexicon</h2>
<ReflexesView mode="lexicon" languageId={lang.id} />

<style>
	.donut-row {
		display: flex;
		gap: 2.5rem;
		flex-wrap: wrap;
		align-items: flex-start;
	}
	.origins {
		margin: 1.6rem 0;
	}
	.tag-summary,
	.dialect-metadata {
		margin: 1.6rem 0;
	}
	.tag-groups {
		display: grid;
		gap: 0.8rem;
		padding: 1rem 1.15rem;
	}
	.tag-group {
		display: grid;
		grid-template-columns: 8rem minmax(0, 1fr);
		align-items: start;
		gap: 0.75rem;
	}
	.tag-group h3 {
		margin: 0;
		font-size: 0.85rem;
		color: var(--muted);
	}
	.lang-header {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 1.2rem;
		align-items: start;
		margin-top: 1rem;
	}
	.lang-header .props {
		margin: 0;
		padding: 0.4rem 1.15rem;
		align-self: start;
	}
	.prop {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1.5rem;
		padding: 0.55rem 0;
		border-bottom: 1px solid var(--border);
	}
	.prop:last-child {
		border-bottom: none;
	}
	.prop dt {
		color: var(--muted);
		font-size: 0.85rem;
		font-weight: 600;
	}
	.prop dd {
		margin: 0;
		font-weight: 500;
		text-align: right;
		font-variant-numeric: tabular-nums;
	}
	@media (max-width: 720px) {
		.lang-header {
			grid-template-columns: 1fr;
		}
		.tag-group {
			grid-template-columns: 1fr;
		}
	}
</style>
