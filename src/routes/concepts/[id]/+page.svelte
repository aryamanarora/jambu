<script lang="ts">
	import ConceptAtlas from '$lib/components/ConceptAtlas.svelte';
	import type { ConceptDetail } from '$lib/types';

	let { data } = $props();
	const detail = $derived(data as ConceptDetail);
	const concept = $derived(detail.concept);
</script>

<svelte:head>
	<title>{concept.name} — Concepts — Jambu</title>
	<meta
		name="description"
		content="Etyma across {concept.lang_count} languages expressing the concept {concept.name} in Jambu."
	/>
</svelte:head>


<ConceptAtlas {detail} />
