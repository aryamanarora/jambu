<script lang="ts">
	import { base } from '$app/paths';
	import { postDate } from '$lib/blog';
	import BlogDisclaimer from '$lib/components/BlogDisclaimer.svelte';
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

<article class="essay">
	<a class="back" href="{base}/blogs">← Blogs</a>
	<header>
		<h1>{data.post.title}</h1>
		<p class="deck">{data.post.description}</p>
		<div class="byline">{#each data.post.authors as author}<span>{author.name} <span class="author-kind">{author.kind === 'agent' ? 'AI-written' : 'Human-written'}</span></span>{/each}<time datetime={data.post.date}>{postDate(data.post.date)}</time></div>
		{#if data.post.reviewedBy}<p class="review">Reviewed by {data.post.reviewedBy}</p>{/if}
	</header>
	{#if data.post.authors.some((author) => author.kind === 'agent')}<BlogDisclaimer />{/if}
	<div class="prose">{@html data.html}</div>
	{#if data.records.length}
		<aside aria-labelledby="linked-records">
			<h2 id="linked-records">Records in this essay</h2>
			<p class="records-intro">Explore the dictionary evidence and its sources.</p>
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
		</aside>
	{/if}
</article>

<style>
	.essay { max-width: 740px; margin: 1.5rem auto 5rem; overflow-wrap: anywhere; }
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
	.prose :global(th), .prose :global(td) { border-bottom: 1px solid var(--border); padding: .5rem .75rem; text-align: left; }
	aside { border-top: 1px solid var(--border-strong); margin-top: 3rem; padding-top: 1.5rem; }
	aside h2 { font-family: var(--font-serif); font-size: 1.5rem; font-weight: 400; margin-bottom: .5rem; }
	.records-intro { color: var(--muted); font-size: .9rem; }
	dl { margin: 1.5rem 0; }
	.record { padding: 1rem 0; border-top: 1px solid var(--border); }
	dt { display: flex; align-items: baseline; gap: .75rem; }
	.record-kind { min-width: 5rem; font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
	.word { font-family: var(--font-serif); font-style: italic; font-size: 1.15rem; }
	dd { margin: .4rem 0 0 5.75rem; font-size: .9rem; line-height: 1.7; color: var(--muted); }
	dd ul { display: flex; flex-wrap: wrap; list-style: none; gap: .25rem 1rem; padding: 0; margin: .5rem 0 0; }
	@media (max-width: 500px) { dd { margin-left: 0; } }
</style>
