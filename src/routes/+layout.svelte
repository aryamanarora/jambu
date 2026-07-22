<script lang="ts">
	import '../app.css';
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import Favorites from '$lib/components/Favorites.svelte';
	import DbBanner from '$lib/components/DbBanner.svelte';
	import EntryPeek from '$lib/components/EntryPeek.svelte';
	import { loadFavorites } from '$lib/prefs.svelte';
	import { preloadDb } from '$lib/db.svelte';

	let { children } = $props();

	type Theme = '' | 'light' | 'dark';
	let theme = $state<Theme>('');

	onMount(() => {
		theme = (localStorage.getItem('jambu-theme') as Theme) || '';
		loadFavorites();
		preloadDb(); // init worker + check OPFS cache (auto-ready if already downloaded)
	});

	function toggleTheme() {
		// Resolve what is currently showing, then flip to the opposite explicit value.
		const showingDark =
			theme === 'dark' ||
			(theme === '' && window.matchMedia('(prefers-color-scheme: dark)').matches);
		theme = showingDark ? 'light' : 'dark';
		document.documentElement.setAttribute('data-theme', theme);
		try {
			localStorage.setItem('jambu-theme', theme);
		} catch (e) {
			/* ignore */
		}
	}

	const nav = [
		{ href: '/entries', label: 'Entries' },
		{ href: '/reflexes', label: 'Reflexes' },
		{ href: '/languages', label: 'Languages' },
		{ href: '/correspondences', label: 'Sounds' },
		{ href: '/references', label: 'References' }
	];

	function isActive(href: string): boolean {
		const p = page.url.pathname;
		return p === base + href || p.startsWith(base + href + '/');
	}
</script>

<header class="nav">
	<nav class="nav-inner">
		<a class="brand" href="{base}/">
			<img src="{base}/favicon.svg" alt="" width="24" height="24" />
			Jambu
		</a>
		<Favorites />
		{#each nav as item (item.href)}
			<a href="{base}{item.href}" class:active={isActive(item.href)}>{item.label}</a>
		{/each}
		<span class="spacer"></span>
		<button class="theme-toggle" onclick={toggleTheme} aria-label="Toggle light/dark theme">
			{theme === 'dark' ? '☾' : theme === 'light' ? '☀' : '◐'}
		</button>
	</nav>
</header>

<DbBanner />

<main class="content">
	{@render children()}
</main>

<EntryPeek />
