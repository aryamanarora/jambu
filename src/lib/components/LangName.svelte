<script lang="ts">
	import { base } from '$app/paths';
	import type { Language } from '$lib/types';

	// Many Jambu "languages" are really dialects (name = "Language: Dialect"). Render the base
	// language prominently and the dialect as a faint qualifier so dialect clusters read at a glance.
	let {
		lang,
		link = true,
		stacked = false
	}: { lang: Language | undefined; link?: boolean; stacked?: boolean } = $props();
</script>

{#if lang}
	{#if link}
		<a href="{base}/languages/{lang.id}" class="langname" class:stacked>
			<span class="base">{lang.language || lang.name}</span>{#if lang.dialect}<span class="dia"
					>{lang.dialect}</span
				>{/if}
		</a>
	{:else}
		<span class="langname" class:stacked>
			<span class="base">{lang.language || lang.name}</span>{#if lang.dialect}<span class="dia"
					>{lang.dialect}</span
				>{/if}
		</span>
	{/if}
{/if}

<style>
	.dia {
		font-size: 0.82em;
		color: var(--faint);
		margin-left: 0.35em;
	}
	.stacked {
		display: inline-flex;
		flex-direction: column;
		line-height: 1.15;
	}
	.stacked .dia {
		margin-left: 0;
	}
</style>
