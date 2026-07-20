<script lang="ts">
	import { base } from '$app/paths';
	import { md } from '$lib/render';

	let { data } = $props();

	// progress → badge class + border colour (mirrors the old references.html)
	function badge(progress: string): 'ok' | 'warn' | 'bad' {
		if (progress === 'Yes') return 'ok';
		if (progress === 'Partial') return 'warn';
		return 'bad';
	}
	const borderColor = { ok: 'var(--ok)', warn: 'var(--warn)', bad: 'var(--bad)' };
</script>

<svelte:head>
	<title>References — Jambu</title>
	<meta name="description" content="The bibliography of sources digitised in the Jambu etymological dictionary of South Asian languages." />
</svelte:head>

<h1>References</h1>
<p class="muted">Sources digitised for Jambu. The coloured bar shows digitisation progress.</p>

<div class="table-wrap">
	<table class="data">
		<tbody>
			{#each data.references as r (r.id)}
				{@const b = badge(r.progress)}
				<tr>
					<td class="lang-cell ref-cell" style="border-left-color: {borderColor[b]}">
						<a href="{base}/references/{r.id}">{r.short}</a>
						<span class="id-tag">[{r.id}]</span>
					</td>
					<td class="markdown">{@html md(r.source)}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.ref-cell {
		white-space: nowrap;
		width: 1%;
	}
</style>
