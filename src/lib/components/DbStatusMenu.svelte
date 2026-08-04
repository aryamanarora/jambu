<script lang="ts">
	import { dbUI, deleteDatabase, loadDatabase } from '$lib/db.svelte';
	import { DB_APPROX_BYTES, DB_VERSION } from '$lib/dbMeta';

	let menu: HTMLDetailsElement;
	let confirmDelete = $state(false);
	let deleting = $state(false);
	let actionError = $state<string | null>(null);

	const approximateMb = Math.round(DB_APPROX_BYTES / 1e6);
	const statusLabel = $derived(
		dbUI.status === 'ready'
			? 'Loaded'
			: dbUI.status === 'downloading'
				? `${Math.round(dbUI.progress * 100)}%`
				: dbUI.status === 'checking'
					? 'Checking'
					: dbUI.status === 'error'
						? 'Error'
						: 'Not loaded'
	);

	async function removeDatabase() {
		deleting = true;
		actionError = null;
		try {
			await deleteDatabase();
			confirmDelete = false;
		} catch (error) {
			actionError = error instanceof Error ? error.message : String(error);
		} finally {
			deleting = false;
		}
	}
</script>

<details
	class="db-menu"
	bind:this={menu}
	ontoggle={() => {
		if (!menu.open) {
			confirmDelete = false;
			actionError = null;
		}
	}}
>
	<summary aria-label="Database status: {statusLabel}" title="Database status">
		<span class="status-dot" class:ready={dbUI.ready} class:error={dbUI.status === 'error'}></span>
		<span class="summary-label">DB {statusLabel}</span>
		<span class="chevron" aria-hidden="true">▾</span>
	</summary>

	<div class="panel">
		<div class="heading">
			<div>
				<strong>Dictionary database</strong>
				<span>Stored privately in this browser</span>
			</div>
			<span class="version">db-v{DB_VERSION}</span>
		</div>

		<div class="status-row">
			<span class="status-dot" class:ready={dbUI.ready} class:error={dbUI.status === 'error'}></span>
			<div>
				<b>{statusLabel}</b>
				{#if dbUI.status === 'ready'}
					<span>Ready for searches · ~{approximateMb} MB</span>
				{:else if dbUI.status === 'downloading'}
					<span>{Math.round(dbUI.receivedBytes / 1e6)} of ~{approximateMb} MB downloaded</span>
				{:else if dbUI.status === 'checking'}
					<span>Looking for a saved copy</span>
				{:else if dbUI.status === 'error'}
					<span>{dbUI.error ?? 'The database could not be opened'}</span>
				{:else}
					<span>Load this version to search Jambu</span>
				{/if}
			</div>
		</div>

		{#if dbUI.status === 'downloading'}
			<div class="progress"><span style="width: {dbUI.progress * 100}%"></span></div>
		{:else if dbUI.status !== 'ready' && dbUI.status !== 'checking'}
			<button class="primary" onclick={() => loadDatabase()}>
				{dbUI.status === 'error' ? 'Retry download' : 'Load database'}
			</button>
		{/if}

		{#if dbUI.status === 'ready'}
			<div class="danger-zone">
				{#if confirmDelete}
					<p>Delete db-v{DB_VERSION} from this browser? You can download it again later.</p>
					<div class="actions">
						<button class="cancel" onclick={() => (confirmDelete = false)} disabled={deleting}>Cancel</button>
						<button class="danger" onclick={removeDatabase} disabled={deleting}>
							{deleting ? 'Deleting…' : 'Delete database'}
						</button>
					</div>
				{:else}
					<button class="delete-link" onclick={() => (confirmDelete = true)}>Delete local database…</button>
				{/if}
			</div>
		{/if}

		{#if actionError}<p class="action-error">Couldn’t delete the database: {actionError}</p>{/if}
	</div>
</details>

<style>
	.db-menu {
		position: relative;
	}
	summary {
		display: inline-flex;
		align-items: center;
		gap: 0.42rem;
		min-height: 34px;
		padding: 0.25rem 0.62rem;
		border: 1px solid rgba(255, 255, 255, 0.25);
		border-radius: 999px;
		color: var(--nav-fg);
		font-size: 0.78rem;
		font-weight: 650;
		line-height: 1;
		cursor: pointer;
		list-style: none;
		white-space: nowrap;
	}
	summary::-webkit-details-marker {
		display: none;
	}
	summary:hover,
	.db-menu[open] summary {
		background: rgba(255, 255, 255, 0.12);
	}
	summary:focus-visible {
		outline: 2px solid var(--nav-fg);
		outline-offset: 2px;
	}
	.status-dot {
		width: 0.55rem;
		height: 0.55rem;
		border-radius: 50%;
		background: var(--warn);
		box-shadow: 0 0 0 2px color-mix(in srgb, var(--warn) 20%, transparent);
		flex: 0 0 auto;
	}
	.status-dot.ready {
		background: var(--ok);
		box-shadow: 0 0 0 2px color-mix(in srgb, var(--ok) 20%, transparent);
	}
	.status-dot.error {
		background: var(--bad);
		box-shadow: 0 0 0 2px color-mix(in srgb, var(--bad) 20%, transparent);
	}
	.chevron {
		color: var(--nav-fg-dim);
		transition: transform 0.15s ease;
	}
	.db-menu[open] .chevron {
		transform: rotate(180deg);
	}
	.panel {
		position: absolute;
		top: calc(100% + 0.55rem);
		right: 0;
		width: min(22rem, calc(100vw - 1.5rem));
		padding: 1rem;
		background: var(--surface);
		color: var(--ink);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius);
		box-shadow: var(--shadow-md);
		z-index: 1100;
	}
	.heading,
	.status-row,
	.actions {
		display: flex;
		align-items: center;
	}
	.heading {
		justify-content: space-between;
		gap: 1rem;
		padding-bottom: 0.8rem;
		border-bottom: 1px solid var(--border);
	}
	.heading div,
	.status-row div {
		display: grid;
	}
	.heading strong {
		font-size: 0.92rem;
	}
	.heading span,
	.status-row span {
		color: var(--muted);
		font-size: 0.76rem;
	}
	.version {
		padding: 0.2rem 0.48rem;
		background: var(--surface-2);
		border: 1px solid var(--border);
		border-radius: 999px;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
	.status-row {
		gap: 0.7rem;
		padding: 0.85rem 0;
	}
	.status-row b {
		font-size: 0.88rem;
	}
	.progress {
		height: 0.42rem;
		background: var(--surface-2);
		border-radius: 999px;
		overflow: hidden;
	}
	.progress span {
		display: block;
		height: 100%;
		background: var(--berry);
		transition: width 0.2s ease;
	}
	button {
		font: inherit;
		cursor: pointer;
	}
	.primary,
	.danger,
	.cancel {
		border-radius: var(--radius-sm);
		padding: 0.42rem 0.7rem;
		font-size: 0.8rem;
		font-weight: 650;
	}
	.primary {
		width: 100%;
		border: 1px solid var(--plum);
		background: var(--plum);
		color: var(--surface);
	}
	.danger-zone {
		padding-top: 0.75rem;
		border-top: 1px solid var(--border);
	}
	.delete-link {
		padding: 0;
		border: 0;
		background: transparent;
		color: var(--bad);
		font-size: 0.78rem;
	}
	.danger-zone p,
	.action-error {
		margin: 0 0 0.65rem;
		font-size: 0.78rem;
		line-height: 1.4;
	}
	.actions {
		justify-content: flex-end;
		gap: 0.5rem;
	}
	.cancel {
		border: 1px solid var(--border-strong);
		background: var(--surface);
		color: var(--ink);
	}
	.danger {
		border: 1px solid var(--bad);
		background: var(--bad);
		color: white;
	}
	button:disabled {
		opacity: 0.55;
		cursor: wait;
	}
	.action-error {
		margin-top: 0.65rem;
		color: var(--bad);
	}

	@media (max-width: 640px) {
		.summary-label {
			display: none;
		}
		summary {
			width: 34px;
			justify-content: center;
			padding: 0;
		}
		.chevron {
			display: none;
		}
	}
</style>
