<script lang="ts">
	import ReflexesView from '$lib/components/ReflexesView.svelte';
</script>

<svelte:head>
	<title>Reflexes — Jambu</title>
	<meta name="description" content="Search the full lexicon of the Jambu etymological dictionary — every reflex across all South Asian languages." />
</svelte:head>

<h1>Reflexes</h1>
<p class="muted">The entire lexicon — every attested form across all languages. Type at least three characters to search a column.</p>

<ReflexesView mode="reflexes" />
