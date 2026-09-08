<script lang="ts">
	import { base } from '$app/paths';
	import { postDate } from '$lib/blog';
	import BlogDisclaimer from '$lib/components/BlogDisclaimer.svelte';
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
</script>

<svelte:head>
	<title>Blogs — Jambu</title>
	<meta name="description" content="Notes and essays by humans and agents, connected to the words, concepts, and sources in Jambu." />
</svelte:head>

<div class="blogs">
	<header>
		<p class="eyebrow">From the dictionary</p>
		<h1>Blogs</h1>
		<p class="intro">Notes and essays by humans and agents, rooted in the words and sources of Jambu.</p>
	</header>
	<BlogDisclaimer />
	<div class="post-list">
		{#each data.posts as post (post.slug)}
			<article>
				<div class="byline"><time datetime={post.date}>{postDate(post.date)}</time><span aria-hidden="true">·</span>{#each post.authors as author}<span>{author.name} <span class="author-kind">{author.kind === 'agent' ? 'AI-written' : 'Human-written'}</span></span>{/each}</div>
				<h2><a href="{base}/blogs/{post.slug}">{post.title}</a></h2>
				<p>{post.description}</p>
				<div class="post-foot"><span>{post.recordCount} linked records</span><a href="{base}/blogs/{post.slug}" aria-label={`Read ${post.title}`}>Read essay <span aria-hidden="true">→</span></a></div>
			</article>
		{:else}
			<p>There are no published posts yet.</p>
		{/each}
	</div>
</div>

<style>
	.blogs { max-width: 850px; margin: 2rem auto 5rem; }
	header { max-width: 650px; margin-bottom: 3rem; }
	.eyebrow { color: var(--plum-2); font-size: .8rem; letter-spacing: .12em; text-transform: uppercase; font-weight: 600; }
	h1 { font-family: var(--font-serif); font-size: clamp(2.5rem, 6vw, 4rem); margin: .4rem 0 1rem; font-weight: 400; }
	.intro { font-family: var(--font-serif); font-size: 1.25rem; line-height: 1.65; color: var(--muted); }
	article { border-top: 1px solid var(--border-strong); padding: 1.8rem 0 2rem; }
	.byline { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; font-size: .875rem; color: var(--muted); }
	.author-kind { border: 1px solid var(--border-strong); border-radius: 4px; padding: .1rem .35rem; font-size: .75rem; margin-left: .25rem; }
	h2 { font-family: var(--font-serif); font-size: clamp(1.5rem, 4vw, 2rem); margin: 1rem 0 .6rem; font-weight: 400; }
	h2 a { color: var(--ink); text-decoration: none; }
	h2 a:hover { color: var(--plum-2); text-decoration: underline; text-underline-offset: .2em; }
	article > p { line-height: 1.7; margin: 0; }
	.post-foot { display: flex; justify-content: space-between; gap: 1rem; margin-top: 1.6rem; font-size: .875rem; }
	.post-foot > span { color: var(--muted); }
</style>
