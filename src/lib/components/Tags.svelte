<script lang="ts">
	// Renders the structured `tags` string (gender + grammatical + attestation source, extracted
	// in ../data) as small pills, coloured by category.
	import { tagCategory, TAG_NAMES } from '$lib/tags';
	let { tags }: { tags?: string | null } = $props();
	const list = $derived((tags ?? '').split(/\s+/).filter(Boolean));
</script>

{#if list.length}
	<span class="tags">
		{#each list as t (t)}
			<span class="tag {tagCategory(t)}" title={TAG_NAMES[t] ?? t}>{t}</span>
		{/each}
	</span>
{/if}

<style>
	.tags {
		display: inline-flex;
		flex-wrap: wrap;
		gap: 3px;
		vertical-align: middle;
		margin-left: 0.35em;
	}
	.tag {
		font-size: 0.68rem;
		line-height: 1.4;
		padding: 0 6px;
		border-radius: 999px;
		border: 1px solid currentColor;
		background: var(--surface);
		white-space: nowrap;
		font-variant: small-caps;
	}
	.tag.gender {
		color: var(--berry);
	}
	.tag.grammatical {
		color: var(--tag-gram);
	}
	.tag.source {
		color: var(--tag-source);
	}
</style>
