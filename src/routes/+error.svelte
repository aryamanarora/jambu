<script lang="ts">
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import QueryError from '$lib/components/QueryError.svelte';

	const isDatabaseError = $derived(
		/sqlite|database|no such table|malformed/i.test(page.error?.message ?? '')
	);
</script>

<svelte:head>
	<title>{page.status} — Jambu</title>
</svelte:head>

{#if isDatabaseError}
	<h1>Dictionary data needs updating</h1>
	<p class="lead">The saved dictionary and this version of Jambu do not match.</p>
	<QueryError error={page.error} />
{:else}
	<h1>{page.status === 404 ? 'Page not found' : 'Something went wrong'}</h1>
	<p class="lead">
		{page.status === 404
			? 'That page may have moved, or its link may be incomplete.'
			: 'Jambu could not open this page.'}
	</p>
	<p class="muted">
		Try the <a href="{base}/entries">dictionary</a>, <a href="{base}/languages">languages</a>, or
		head back <a href="{base}/">home</a>.
	</p>
	{#if page.error?.message}
		<details class="technical"><summary>Technical details</summary><code>{page.error.message}</code></details>
	{/if}
{/if}

<style>
	.technical { margin-top: 1rem; color: var(--muted); font-size: 0.8rem; }
	.technical code { display: block; margin-top: 0.4rem; white-space: pre-wrap; }
</style>
