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
	const gaMeasurementId = (env.PUBLIC_GA_MEASUREMENT_ID ?? '').trim();
	const hasGoogleAnalytics = /^G-[A-Z0-9]+$/i.test(gaMeasurementId);
	let trackPageView: (() => void) | undefined;

	afterNavigate(() => {
		mobileNavOpen = false;
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

	const nav = [
		{ href: '/entries', label: 'Entries' },
		{ href: '/reflexes', label: 'Reflexes' },
		{ href: '/languages', label: 'Languages' },
		{ href: '/correspondences', label: 'Sounds' },
		{ href: '/isoglosses', label: 'Isoglosses' },
		{ href: '/concepts', label: 'Concepts' },
		{ href: '/references', label: 'References' }
	];
	if (dev) {
		nav.push({ href: '/dev/etymologies', label: 'Etymology lab' });
		nav.push({ href: '/dev/ocr', label: 'OCR lab' });
	}

	function isActive(href: string): boolean {
		const p = page.url.pathname;
		return p === base + href || p.startsWith(base + href + '/');
	}
</script>

<a class="skip-link" href="#main-content">Skip to content</a>
<header class="nav">
	<nav class="nav-inner" aria-label="Primary navigation">
		<a class="brand" href="{base}/" onclick={() => (mobileNavOpen = false)}>
			<img src="{base}/favicon.svg" alt="" width="24" height="24" />
			Jambu
		</a>
		<div class="nav-favorites"><Favorites /></div>
		<div class="nav-links" class:open={mobileNavOpen} id="primary-nav-links">
			{#each nav as item (item.href)}
				<a
					href="{base}{item.href}"
					class:active={isActive(item.href)}
					onclick={() => (mobileNavOpen = false)}>{item.label}</a
				>
			{/each}
		</div>
		<span class="spacer"></span>
		<DbStatusMenu />
		<button class="theme-toggle" onclick={toggleTheme} aria-label="Toggle light/dark theme">
			{theme === 'dark' ? '☾' : theme === 'light' ? '☀' : '◐'}
		</button>
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
