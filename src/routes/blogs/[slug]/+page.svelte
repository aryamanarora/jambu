<script lang="ts">
	import { base } from '$app/paths';
	import { postDate } from '$lib/blog';
	import BlogDisclaimer from '$lib/components/BlogDisclaimer.svelte';
	import BlogChart from '$lib/components/BlogChart.svelte';
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
</script>

<svelte:head>
	<title>{data.post.title} — Jambu Blogs</title>
	<meta name="description" content={data.post.description} />
	<meta name="author" content={data.post.authors.map((author) => author.name).join(', ')} />
	<meta property="og:type" content="article" />
	<meta property="og:title" content={data.post.title} />
	<meta property="og:description" content={data.post.description} />
	<meta property="article:published_time" content={`${data.post.date}T00:00:00Z`} />
</svelte:head>

<article class="essay" class:research-essay={data.post.slug === 'telugu-metathesis'}>
	<a class="back" href="{base}/blogs">← Blogs</a>
	<header>
		<h1>{data.post.title}</h1>
		<p class="deck">{data.post.description}</p>
		<div class="byline">{#each data.post.authors as author}<span>{author.name} <span class="author-kind">{author.kind === 'agent' ? 'AI-written' : 'Human-written'}</span></span>{/each}<time datetime={data.post.date}>{postDate(data.post.date)}</time></div>
		{#if data.post.reviewedBy}<p class="review">Reviewed by {data.post.reviewedBy}</p>{/if}
	</header>
	{#if data.post.authors.some((author) => author.kind === 'agent')}<BlogDisclaimer />{/if}
	<div class="prose">{#each data.blocks as block}{#if block.kind === 'html'}{@html block.html}{:else}{#key block.chart.id}<BlogChart chart={block.chart} />{/key}{/if}{/each}</div>
	{#if data.records.length}
		<aside aria-labelledby="linked-records">
			<h2 id="linked-records">Records in this essay</h2>
			<p class="records-intro">Explore the dictionary evidence and its sources.</p>
			<details class="record-details"><summary>Show all {data.records.length} linked records</summary>
			<dl>
				{#each data.records as record (`${record.kind}:${record.id}`)}
					<div class="record">
						<dt><span class="record-kind">{record.kind === 'ref' ? 'Source' : record.kind}</span><a href={record.href} class:word={record.kind === 'entry' || record.kind === 'form'}>{record.label}</a></dt>
						<dd>{record.description}
							{#if record.context?.length}<ul aria-label={`Context for ${record.label}`}>{#each record.context as link}<li><a href={link.href}>{link.label}</a></li>{/each}</ul>{/if}
						</dd>
					</div>
				{/each}
			</dl>
			</details>
		</aside>
	{/if}
</article>

<style>
	.essay { max-width: 740px; margin: 1.5rem auto 5rem; overflow-wrap: anywhere; }
	.research-essay { max-width: 960px; }
	.research-essay header { max-width: 740px; }
	.research-essay .prose :global(p), .research-essay .prose :global(h2) { max-width: 740px; }
	.research-essay .prose :global(table) { line-height: 1.55; font-size: .95rem; margin-bottom: 1.75rem; }
	.research-essay .prose :global(table th:nth-child(1)), .research-essay .prose :global(table td:nth-child(1)) { min-width: 115px; }
	.research-essay .prose :global(table td:nth-child(2)) { min-width: 125px; }
	.research-essay .prose :global(table td:nth-child(3)) { min-width: 160px; }
	.research-essay .prose :global(table td:nth-child(4)) { min-width: 240px; }
	.research-essay .prose :global(.research-methods) { font-family: var(--font-sans); font-size: .9rem; line-height: 1.7; border-top: 1px solid var(--border); padding-top: 1rem; }
	.research-essay .prose :global(.research-methods summary) { cursor: pointer; margin-bottom: 1rem; }
	.back { font-size: .9rem; }
	header { padding: 2rem 0; border-bottom: 1px solid var(--border-strong); margin-bottom: 2rem; }
	h1 { font-family: var(--font-serif); font-weight: 400; font-size: clamp(2.2rem, 6vw, 3.5rem); line-height: 1.15; margin: 0 0 1rem; letter-spacing: -.025em; }
	.deck { font-family: var(--font-serif); color: var(--muted); font-size: 1.2rem; line-height: 1.6; }
	.byline { display: flex; flex-wrap: wrap; align-items: center; gap: .8rem 1.5rem; font-size: .875rem; }
	time, .review { color: var(--muted); font-size: .875rem; }
	.author-kind { margin-left: .4rem; padding: .15rem .4rem; background: var(--surface-2); border-radius: 4px; font-size: .75rem; }
	.prose { font-family: var(--font-serif); font-size: 1.125rem; line-height: 1.85; }
	.prose :global(p) { margin: 0 0 1.4em; }
	.prose :global(h2) { margin: 2em 0 .65em; font-weight: 400; font-size: 1.6rem; line-height: 1.3; }
	.prose :global(h3) { font-size: 1.25rem; margin-top: 1.8em; }
	.prose :global(a) { text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: .18em; }
	.prose :global(.blog-link-entry), .prose :global(.blog-link-form) { font-style: italic; }
	.prose :global(.blog-link-concept) { font-variant: small-caps; letter-spacing: .035em; }
	.prose :global(.blog-link-ref) { font-size: .95em; }
	.prose :global(blockquote) { border-left: 3px solid var(--border-strong); margin: 1.5rem 0; padding: .25rem 1.25rem; color: var(--muted); }
	.prose :global(img) { max-width: 100%; height: auto; }
	.prose :global(pre) { overflow-x: auto; background: var(--surface-2); padding: 1rem; font-size: .875rem; }
	.prose :global(table) { display: block; overflow-x: auto; border-collapse: collapse; font-size: 1rem; }
	.prose :global(.blog-table) { max-width: 100%; overflow-x: auto; margin: 1rem 0 1.75rem; }
	.prose :global(.blog-table table) { display: table; width: 100%; min-width: 640px; overflow-wrap: normal; }
	.prose :global(.blog-table th:first-child), .prose :global(.blog-table td:first-child) { min-width: 7rem; }
	.prose :global(.blog-table th:last-child), .prose :global(.blog-table td:last-child) { min-width: 16rem; }
	.prose :global(.table-hint) { display: none; }
	.prose :global(.blog-table:focus-visible) { outline: 2px solid var(--border-strong); outline-offset: 3px; }
	.prose :global(.claim-nav) { font-family: var(--font-sans); font-size: .85rem; line-height: 1.8; border-block: 1px solid var(--border); padding: 1rem 0; }
	.prose :global(.claim-nav p) { margin: 0; }
	.prose :global(h2[id]) { scroll-margin-top: 6rem; }
	.prose :global(th), .prose :global(td) { border-bottom: 1px solid var(--border); padding: .5rem .75rem; text-align: left; }
	aside { border-top: 1px solid var(--border-strong); margin-top: 3rem; padding-top: 1.5rem; }
	aside h2 { font-family: var(--font-serif); font-size: 1.5rem; font-weight: 400; margin-bottom: .5rem; }
	.records-intro { color: var(--muted); font-size: .9rem; }
	.record-details summary { cursor: pointer; font-size: .9rem; }
	dl { margin: 1.5rem 0; }
	.record { padding: 1rem 0; border-top: 1px solid var(--border); }
	dt { display: flex; align-items: baseline; gap: .75rem; }
	.record-kind { min-width: 5rem; font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
	.word { font-family: var(--font-serif); font-style: italic; font-size: 1.15rem; }
	dd { margin: .4rem 0 0 5.75rem; font-size: .9rem; line-height: 1.7; color: var(--muted); }
	dd ul { display: flex; flex-wrap: wrap; list-style: none; gap: .25rem 1rem; padding: 0; margin: .5rem 0 0; }
	@media (max-width: 660px) {
		.prose :global(.table-hint) { display: block; font-family: var(--font-sans); font-size: .75rem; color: var(--muted); margin: 1rem 0 -.5rem; }
	}
	@media (max-width: 500px) { dd { margin-left: 0; } }
</style>
