<script lang="ts">
	// The fold-away control on an atlas panel. Which way the chevron points depends on which edge
	// the panel is docked to, so the caller says `side` rather than spelling the classes out.
	let {
		open,
		side,
		label,
		onclick
	}: {
		open: boolean;
		side: 'left' | 'right';
		label: string; // what is being folded, e.g. "the etymon panel"
		onclick: () => void;
	} = $props();

	const pointsRight = $derived(side === 'left' ? open : !open);
</script>

<button
	class="panel-toggle"
	aria-label={open ? `Collapse ${label}` : `Expand ${label}`}
	aria-expanded={open}
	{onclick}
>
	<span class="chev" class:right={pointsRight} class:open={!pointsRight} aria-hidden="true"></span>
</button>
