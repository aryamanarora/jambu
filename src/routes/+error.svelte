<script lang="ts">
	import { base } from '$app/paths';
	import { page } from '$app/state';
</script>

<svelte:head>
	<title>{page.status} — Jambu</title>
</svelte:head>

<h1>{page.status}</h1>
<p class="lead">{page.error?.message ?? 'Something went wrong.'}</p>
<p class="muted">
	Try the <a href="{base}/entries">entries</a>, <a href="{base}/reflexes">reflexes</a>, or
	<a href="{base}/languages">languages</a>, or head back <a href="{base}/">home</a>.
</p>
