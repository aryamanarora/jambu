import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// Base path: for a project page served at https://<user>.github.io/<repo>/ set BASE_PATH=/<repo>.
// For a custom domain or a user/org page (root), leave it empty.
const base = process.env.BASE_PATH ?? '';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			// SPA fallback: routes we don't prerender (reflex details, language-vs-language compare,
			// filtered/sorted views) are served this shell and rendered client-side from SQLite.
			fallback: '200.html',
			precompress: false,
			strict: false
		}),
		paths: { base },
		// Prerendering is opted into per-route (see canonical routes' `prerender = true`).
		// Errors during prerender crawl of dynamic links shouldn't fail the whole build.
		prerender: {
			handleHttpError: 'warn',
			handleMissingId: 'warn'
		}
	}
};

export default config;
