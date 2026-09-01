<script lang="ts">
	let {
		relaxed = false,
		onToggle
	}: {
		relaxed?: boolean;
		onToggle: (relaxed: boolean) => void;
	} = $props();
</script>

<label class="match-toggle">
	<input
		type="checkbox"
		checked={relaxed}
		onchange={(event) => onToggle(event.currentTarget.checked)}
	/>
	<span>
		<strong>Relax Unicode matching</strong>
		<small>Ignore diacritics and compatibility variants, e.g. h matches ʰ.</small>
	</span>
</label>

<style>
	.match-toggle {
		display: flex;
		align-items: flex-start;
		gap: 0.55rem;
		min-width: 0;
		padding: 0.45rem 0.55rem;
		border: 1px solid var(--border);
		border-radius: 6px;
		background: var(--bg);
		cursor: pointer;
	}
	.match-toggle input {
		flex: 0 0 auto;
		margin: 0.16rem 0 0;
		accent-color: var(--plum);
	}
	.match-toggle span {
		display: grid;
		gap: 0.12rem;
		min-width: 0;
	}
	.match-toggle strong {
		color: var(--ink);
		font-size: 0.8rem;
		font-weight: 600;
	}
	.match-toggle small {
		color: var(--muted);
		font-size: 0.7rem;
		font-weight: 400;
		line-height: 1.3;
	}
</style>
