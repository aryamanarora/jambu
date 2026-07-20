<script lang="ts">
	import EntriesView from '$lib/components/EntriesView.svelte';
</script>

<svelte:head>
	<title>Entries — Jambu</title>
	<meta name="description" content="Browse the headword entries of the Jambu etymological dictionary of South Asian languages." />
</svelte:head>

<h1>Entries</h1>
<p class="muted">Headwords across the South Asian languages. Click an entry for its map, cognates, and descendants.</p>

<EntriesView />
