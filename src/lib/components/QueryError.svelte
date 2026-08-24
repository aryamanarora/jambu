<script lang="ts">
	import { deleteDatabase, loadDatabase } from '$lib/db.svelte';

	let { error }: { error: unknown } = $props();
	let recovering = $state(false);
	let recoveryError = $state('');
	const details = $derived(error instanceof Error ? error.message : String(error ?? 'Unknown error'));

	async function recover() {
		recovering = true;
		recoveryError = '';
		try {
			await deleteDatabase();
			await loadDatabase();
			location.reload();
		} catch (reason) {
			recoveryError = reason instanceof Error ? reason.message : String(reason);
			recovering = false;
		}
	}
</script>

<div class="query-error" role="alert">
	<div>
		<strong>Dictionary data needs attention</strong>
		<p>Refresh the saved dictionary data, then try the search again.</p>
	</div>
	<button type="button" onclick={recover} disabled={recovering}>
		{recovering ? 'Refreshing…' : 'Refresh dictionary data'}
	</button>
	<details>
		<summary>Technical details</summary>
		<code>{recoveryError || details}</code>
	</details>
</div>

<style>
	.query-error {
		display: grid;
		grid-template-columns: 1fr auto;
		gap: 0.65rem 1rem;
		align-items: center;
		margin: 0.8rem 0;
		padding: 0.8rem 0.9rem;
		border: 1px solid color-mix(in srgb, var(--bad) 35%, var(--border));
		border-radius: var(--radius);
		background: color-mix(in srgb, var(--bad) 5%, var(--surface));
	}
	.query-error p {
		margin: 0.12rem 0 0;
		color: var(--muted);
		font-size: 0.86rem;
	}
	.query-error button {
		min-height: 38px;
		padding: 0.45rem 0.75rem;
		border: 1px solid var(--bad);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--bad);
		font: inherit;
		font-size: 0.82rem;
		font-weight: 600;
		cursor: pointer;
	}
	.query-error button:disabled { opacity: 0.6; }
	.query-error details {
		grid-column: 1 / -1;
		color: var(--muted);
		font-size: 0.76rem;
	}
	.query-error code {
		display: block;
		margin-top: 0.35rem;
		white-space: pre-wrap;
		word-break: break-word;
	}
	@media (max-width: 640px) {
		.query-error { grid-template-columns: 1fr; }
		.query-error button { width: 100%; }
	}
</style>
