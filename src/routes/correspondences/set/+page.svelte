<script lang="ts">
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import { browser } from '$app/environment';
	import { getCorrespondenceReflexes, type CorrReflex, type CorrQuery } from '$lib/query';
	import { changeInfo } from '$lib/soundChange';
	import { hashColor } from '$lib/clades';
	import { langFavRank } from '$lib/prefs.svelte';
	import { safe } from '$lib/render';

	// ---- read the correspondence from the URL ------------------------------
	const q = $derived<CorrQuery | null>(browser ? readQuery(page.url.searchParams) : null);
	function readQuery(sp: URLSearchParams): CorrQuery | null {
		const proto = sp.get('p');
		const seg = sp.get('s');
		const reflexSeg = sp.get('r');
		if (proto == null || seg == null || reflexSeg == null) return null;
		return {
			proto,
			seg,
			reflexSeg,
			clade: sp.get('c'),
			lang: sp.get('l'),
			prev: sp.get('pv'),
			next: sp.get('nx')
		};
	}

	let rows = $state<CorrReflex[]>([]);
	let total = $state(0);
	let truncated = $state(false);
	let loading = $state(true);

	$effect(() => {
		const query = q;
		if (!query) {
			rows = [];
			total = 0;
			truncated = false;
			loading = false;
			return;
		}
		loading = true;
		getCorrespondenceReflexes(query).then((res) => {
			rows = res.rows;
			total = res.total;
			truncated = res.truncated;
			loading = false;
		});
	});

	// one row per reflex (a reflex can show the correspondence at two positions); pinned languages
	// float to the top (stable within the DB's language order otherwise)
	const reflexes = $derived.by<CorrReflex[]>(() => {
		const seen = new Set<string>();
		const out: CorrReflex[] = [];
		for (const r of rows) {
			if (seen.has(r.id)) continue;
			seen.add(r.id);
			out.push(r);
		}
		return out
			.map((r, i) => ({ r, i }))
			.sort((a, b) => {
				const fa = langFavRank(a.r.lang);
				const fb = langFavRank(b.r.lang);
				if (fa !== fb) return fa - fb;
				return a.i - b.i;
			})
			.map((x) => x.r);
	});

	function envLabel(query: CorrQuery): string {
		if (!query.prev && !query.next) return '';
		return ` / ${query.prev ?? ''}_${query.next ?? ''}`;
	}
</script>

<svelte:head>
	<title>
		{q ? `*${q.seg} → ${q.reflexSeg || '∅'} — Correspondences — Jambu` : 'Correspondences — Jambu'}
	</title>
</svelte:head>

<div class="crumb"><a href="{base}/correspondences">← Sound correspondences</a></div>

{#if !q}
	<h1>No correspondence selected</h1>
	<p class="muted">
		Pick a segment and outcome from the
		<a href="{base}/correspondences">correspondence explorer</a>.
	</p>
{:else}
	<h1 class="corr-head">
		<span class="phon proto">*{q.seg}</span>
		<span class="arrow">→</span>
		<span class="phon out">{q.reflexSeg || '∅'}</span>
		{#if envLabel(q)}<span class="phon env">{envLabel(q)}</span>{/if}
	</h1>
	<p class="sub muted">
		{q.proto}{#if q.clade} · {q.clade}{/if}{#if q.lang} · {q.lang}{/if}
	</p>

	<div class="showing-line">
		<div class="loader-slot">{#if loading}<div class="loader-line"></div>{/if}</div>
		{#if !loading}
			<p class="muted">
				{#if truncated}Showing first {reflexes.length.toLocaleString()} of {total.toLocaleString()}
				{:else}Showing {reflexes.length.toLocaleString()}{/if}
				reflex{total === 1 ? '' : 'es'}.
			</p>
		{/if}
	</div>

	{#if !loading && reflexes.length === 0}
		<p class="muted">No reflexes found for this correspondence.</p>
	{:else if reflexes.length}
		<div class="table-wrap">
			<table class="data">
				<thead>
					<tr>
						<th>Language</th>
						<th>Word</th>
						<th>Gloss</th>
						<th>Change</th>
						<th>Etymon</th>
					</tr>
				</thead>
				<tbody>
					{#each reflexes as r (r.id)}
						{@const info = changeInfo(r.change)}
						<tr>
							<td class="lang-cell" style="border-left-color: {hashColor(r.color)}">
								<a href="{base}/languages/{r.lang}"
									>{r.language || r.langName}{#if r.dialect}: <span class="font-thin"
											>{r.dialect}</span
										>{/if}</a
								>
							</td>
							<td class="lemma-word">
								<a href="{base}/reflexes/{r.id}">{@html safe(r.word)}</a>{#if r.phonemic}
									<span class="phonemic">/&#8288;{r.phonemic}&#8288;/</span>{/if}
							</td>
							<td class="muted">{@html safe(r.gloss) || '—'}</td>
							<td><span class="chg {info.cls}">{info.name}</span></td>
							<td>
								{#if r.entryId}
									<a class="ety" href="{base}/entries/{r.entryId}"
										><span class="id-tag">[{r.entryId}]</span></a
									>
								{:else}<span class="faint">—</span>{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
{/if}

<style>
	.crumb {
		margin: 0.5rem 0 0.75rem;
		font-size: 0.85rem;
	}
	.crumb a {
		color: var(--muted);
	}
	.corr-head {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		font-size: 2rem;
		margin: 0.2rem 0;
	}
	.corr-head .phon {
		font-family: var(--font-phon);
	}
	.corr-head .proto {
		color: var(--accent);
	}
	.corr-head .arrow {
		color: var(--muted);
		font-size: 1.4rem;
	}
	.corr-head .env {
		color: var(--muted);
		font-size: 1.3rem;
	}
	.sub {
		margin: 0 0 0.5rem;
		font-size: 0.9rem;
	}
	.showing-line {
		margin-top: 0.5rem;
	}
	.loader-slot {
		height: 3px;
		margin-bottom: 0.4rem;
	}
	.chg {
		font-size: 0.78rem;
		white-space: nowrap;
	}
	.chg.kept {
		color: var(--faint);
	}
	.chg.change {
		color: #a85713;
	}
	.chg.loss {
		color: var(--bad);
	}
	.chg.add {
		color: #2563a8;
	}
	:global(:root[data-theme='dark']) .chg.change,
	:global(:root:not([data-theme='light'])) .chg.change {
		color: #e0a35a;
	}
	.ety {
		font-family: var(--font-phon);
	}
</style>
