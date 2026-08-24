<script lang="ts">
	import '../app.css';
	import { base } from '$app/paths';
	import { afterNavigate } from '$app/navigation';
	import { page } from '$app/state';
	import { env } from '$env/dynamic/public';
	import { onMount } from 'svelte';
	import { dev } from '$app/environment';
	import Favorites from '$lib/components/Favorites.svelte';
	import DbBanner from '$lib/components/DbBanner.svelte';
	import DbStatusMenu from '$lib/components/DbStatusMenu.svelte';
	import EntryPeek from '$lib/components/EntryPeek.svelte';
	import { loadFavorites } from '$lib/prefs.svelte';
	import { preloadDb } from '$lib/db.svelte';

	let { children } = $props();

	type Theme = '' | 'light' | 'dark';
	let theme = $state<Theme>('');
	let mobileNavOpen = $state(false);
	let dictionaryOpen = $state(false);
	let researchOpen = $state(false);
	let utilityOpen = $state(false);
	const gaMeasurementId = (env.PUBLIC_GA_MEASUREMENT_ID ?? '').trim();
	const hasGoogleAnalytics = /^G-[A-Z0-9]+$/i.test(gaMeasurementId);
	let trackPageView: (() => void) | undefined;

	afterNavigate(() => {
		mobileNavOpen = false;
		dictionaryOpen = false;
		researchOpen = false;
		utilityOpen = false;
		trackPageView?.();
	});

	onMount(() => {
		theme = (localStorage.getItem('jambu-theme') as Theme) || '';
		loadFavorites();
		preloadDb(); // init worker + check OPFS cache (auto-ready if already downloaded)

		if (!hasGoogleAnalytics) return;

		const analyticsWindow = window as Window & { dataLayer?: unknown[][] };
		const dataLayer = (analyticsWindow.dataLayer ??= []);
		const gtag = (...args: unknown[]) => dataLayer.push(args);
		gtag('js', new Date());
		gtag('config', gaMeasurementId, { send_page_view: false });

		trackPageView = () => {
			const pathname = window.location.pathname;
			const routePath =
				base && (pathname === base || pathname.startsWith(`${base}/`))
					? pathname.slice(base.length)
					: pathname;
			const analyticsPath = `/jambu${routePath.startsWith('/') ? routePath : `/${routePath}`}`;
			const analyticsLocation = new URL(window.location.href);
			analyticsLocation.pathname = analyticsPath;

			gtag('event', 'page_view', {
				page_location: analyticsLocation.href,
				page_path: analyticsPath,
				page_title: document.title
			});
		};
		trackPageView();

		const script = document.createElement('script');
		script.async = true;
		script.src = `https://www.googletagmanager.com/gtag/js?id=${gaMeasurementId}`;
		document.head.append(script);
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

	const dictionaryNav = [
		{ href: '/entries', label: 'Headwords' },
		{ href: '/reflexes', label: 'All forms' }
	];
	const nav = [
		{ href: '/languages', label: 'Languages' },
		{ href: '/concepts', label: 'Concepts' },
		{ href: '/references', label: 'Sources' }
	];
	const researchNav = [
		{ href: '/correspondences', label: 'Sound correspondences' },
		{ href: '/isoglosses', label: 'Isoglosses' }
	];

	function isActive(href: string): boolean {
		const p = page.url.pathname;
		return p === base + href || p.startsWith(base + href + '/');
	}
	function anyActive(items: { href: string }[]): boolean {
		return items.some((item) => isActive(item.href));
	}
</script>

<a class="skip-link" href="#main-content">Skip to content</a>
<header class="nav">
	<nav class="nav-inner" aria-label="Primary navigation">
		<a class="brand" href="{base}/" onclick={() => (mobileNavOpen = false)}>
			<img src="{base}/favicon.svg" alt="" width="24" height="24" />
			Jambu
		</a>
		<div class="nav-links" class:open={mobileNavOpen} id="primary-nav-links">
			<details class="nav-dropdown" bind:open={dictionaryOpen}>
				<summary class:active={anyActive(dictionaryNav)} onclick={() => { researchOpen = false; utilityOpen = false; }}>Dictionary</summary>
				<div class="nav-dropdown-panel">
					{#each dictionaryNav as item (item.href)}
						<a href="{base}{item.href}" class:active={isActive(item.href)}>{item.label}</a>
					{/each}
				</div>
			</details>
			{#each nav as item (item.href)}
				<a
					href="{base}{item.href}"
					class:active={isActive(item.href)}
					onclick={() => (mobileNavOpen = false)}>{item.label}</a
				>
			{/each}
			<details class="nav-dropdown" bind:open={researchOpen}>
				<summary class:active={anyActive(researchNav)} onclick={() => { dictionaryOpen = false; utilityOpen = false; }}>Research</summary>
				<div class="nav-dropdown-panel">
					{#each researchNav as item (item.href)}
						<a href="{base}{item.href}" class:active={isActive(item.href)}>{item.label}</a>
					{/each}
				</div>
			</details>
		</div>
		<span class="spacer"></span>
		<details class="utility-menu" bind:open={utilityOpen}>
			<summary aria-label="Open settings and favorites" title="Settings and favorites" onclick={() => { dictionaryOpen = false; researchOpen = false; }}>•••</summary>
			<div class="utility-panel">
				<Favorites variant="menu" />
				<DbStatusMenu variant="menu" />
				<button class="utility-row" onclick={toggleTheme}>
					<span aria-hidden="true">{theme === 'dark' ? '☾' : theme === 'light' ? '☀' : '◐'}</span>
					<span>Appearance</span>
					<small>{theme || 'System'}</small>
				</button>
				{#if dev}
					<div class="utility-divider">Development</div>
					<a class="utility-row" href="{base}/dev/etymologies">Etymology lab</a>
					<a class="utility-row" href="{base}/dev/ocr">OCR lab</a>
				{/if}
			</div>
		</details>
		<button
			class="nav-menu-toggle"
			class:open={mobileNavOpen}
			type="button"
			aria-label={mobileNavOpen ? 'Close navigation menu' : 'Open navigation menu'}
			aria-expanded={mobileNavOpen}
			aria-controls="primary-nav-links"
			onclick={() => (mobileNavOpen = !mobileNavOpen)}
		>
			<span aria-hidden="true"></span>
			<span aria-hidden="true"></span>
			<span aria-hidden="true"></span>
		</button>
	</nav>
</header>

<DbBanner />

<main class="content" id="main-content">
	{@render children()}
</main>

<EntryPeek />
