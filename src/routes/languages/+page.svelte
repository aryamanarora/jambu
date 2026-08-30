<script lang="ts">
	import LanguageAtlas from '$lib/components/LanguageAtlas.svelte';
	import type { DialectIndexRow, Language } from '$lib/types';

	let { data } = $props();
	const languages = $derived(data.languages as Language[]);
	const dialects = $derived(data.dialects as DialectIndexRow[]);
</script>

<svelte:head>
	<title>Languages — Jambu</title>
	<meta
		name="description"
		content="An atlas of the {languages.length} languages and {dialects.length} dialects represented in Jambu, by family, lexicon size, and place."
	/>
</svelte:head>

<LanguageAtlas {languages} {dialects} />
