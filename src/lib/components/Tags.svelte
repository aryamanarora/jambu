<script lang="ts">
	// Renders the structured `tags` string (space-separated gender + grammatical tokens, extracted
	// from notes in ../data) as small pills. Gender tags get a slightly stronger accent.
	let { tags }: { tags?: string | null } = $props();
	const GENDER = new Set(['m', 'f', 'n', 'mn', 'fn', 'mf']);
	const list = $derived((tags ?? '').split(/\s+/).filter(Boolean));
</script>

{#if list.length}
	<span class="tags">
		{#each list as t (t)}
			<span class="tag" class:gender={GENDER.has(t)}>{t}</span>
		{/each}
	</span>
{/if}

<style>
	.tags {
		display: inline-flex;
		flex-wrap: wrap;
		gap: 3px;
		vertical-align: middle;
	}
	.tag {
		font-size: 0.68rem;
		line-height: 1.4;
		padding: 0 6px;
		border-radius: 999px;
		border: 1px solid var(--border-strong);
		color: var(--muted);
		background: var(--surface);
		white-space: nowrap;
		font-variant: small-caps;
	}
	.tag.gender {
		color: var(--berry);
		border-color: color-mix(in srgb, var(--berry) 45%, var(--border-strong));
	}
</style>
