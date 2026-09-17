<script lang="ts">
	import { base } from '$app/paths';
	let { label, items, open = $bindable(false), isActive, onclick }: {
		label: string; items: { href: string; label: string }[]; open?: boolean;
		isActive: (href: string) => boolean; onclick: () => void;
	} = $props();
</script>

<details class="nav-dropdown" bind:open>
	<summary class:active={items.some((item) => isActive(item.href))} {onclick}>{label}</summary>
	<div class="nav-dropdown-panel">
		{#each items as item (item.href)}
			<a href="{base}{item.href}" class:active={isActive(item.href)}>{item.label}</a>
		{/each}
	</div>
</details>
