<script lang="ts">
	import { postDate, type BlogPost } from '$lib/blog';
	let { authors, date, dateFirst = false }: { authors: BlogPost['authors']; date: string; dateFirst?: boolean } = $props();
</script>

{#snippet published()}<time datetime={date}>{postDate(date)}</time>{/snippet}
<div class="byline">
	{#if dateFirst}{@render published()}<span aria-hidden="true">·</span>{/if}
	{#each authors as author}
		<span>{author.name} <span class="author-kind">{author.kind === 'agent' ? 'AI-written' : 'Human-written'}</span></span>
	{/each}
	{#if !dateFirst}{@render published()}{/if}
</div>

<style>
	.byline { display: flex; flex-wrap: wrap; align-items: center; gap: 0.6rem; font-size: 0.875rem; color: var(--muted); }
	.author-kind { border: 1px solid var(--border-strong); border-radius: 4px; padding: 0.1rem 0.35rem; font-size: 0.75rem; margin-left: 0.25rem; }
</style>
