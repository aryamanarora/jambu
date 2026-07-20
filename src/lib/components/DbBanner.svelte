<script lang="ts">
	// A slim banner that gates the in-browser database. The dictionary data lives in a ~90 MB
	// download; rather than pull it automatically, we ask the user once. After loading it's cached
	// on their device (OPFS), so this only appears on the first visit (or after a data update).
	import { dbUI, loadDatabase } from '$lib/db.svelte';
	import { DB_APPROX_BYTES } from '$lib/dbMeta';

	const mb = (b: number) => (b / 1e6).toFixed(0);
	const approxMb = mb(DB_APPROX_BYTES);
</script>

{#if dbUI.status !== 'ready' && dbUI.status !== 'checking'}
	<div class="db-banner" class:busy={dbUI.status === 'downloading'} role="region" aria-label="Database">
		{#if dbUI.status === 'downloading'}
			<div class="bar" style="--p:{dbUI.progress * 100}%"></div>
			<span class="msg">
				Loading dictionary… <b>{mb(dbUI.receivedBytes)}</b> / ~{approxMb} MB
			</span>
		{:else}
			<span class="msg">
				{#if dbUI.status === 'error'}
					<span class="err">Couldn’t load the database{dbUI.error ? `: ${dbUI.error}` : ''}.</span>
				{:else}
					This dictionary runs entirely in your browser. Load the database
					<span class="muted">(~{approxMb} MB, one-time — then cached on this device)</span>.
				{/if}
			</span>
			<button class="load" onclick={() => loadDatabase()}>
				{dbUI.status === 'error' ? 'Retry' : 'Load database'}
			</button>
		{/if}
	</div>
{/if}

<style>
	.db-banner {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 12px;
		flex-wrap: wrap;
		padding: 8px 16px;
		background: var(--surface);
		border-bottom: 1px solid var(--border-strong);
		font-size: 0.88rem;
		overflow: hidden;
	}
	.bar {
		position: absolute;
		inset: 0 auto 0 0;
		width: var(--p, 0%);
		background: color-mix(in srgb, var(--berry) 16%, transparent);
		transition: width 0.2s ease;
		z-index: 0;
	}
	.msg {
		position: relative;
		z-index: 1;
	}
	.muted {
		color: var(--muted);
	}
	.err {
		color: var(--bad);
	}
	.load {
		position: relative;
		z-index: 1;
		border: 1px solid var(--plum);
		background: var(--plum);
		color: #fbeefb;
		border-radius: 999px;
		padding: 4px 14px;
		font-size: 0.85rem;
		cursor: pointer;
		white-space: nowrap;
	}
	.load:hover {
		background: var(--berry);
		border-color: var(--berry);
	}
</style>
