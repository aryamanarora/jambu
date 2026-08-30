<script lang="ts">
	import ConceptAtlas from '$lib/components/ConceptAtlas.svelte';
	import type { ConceptDetail } from '$lib/types';

	let { data } = $props();
	const detail = $derived(data as ConceptDetail);
	const concept = $derived(detail.concept);
</script>

<svelte:head>
	<title>Concepts — Jambu</title>
	<meta
		name="description"
		content="Map the etyma expressing a concept across the languages of South Asia, starting from {concept.name}."
	/>
</svelte:head>

<ConceptAtlas {detail} />
