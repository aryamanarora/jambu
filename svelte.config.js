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
			// SPA fallback for routes we don't prerender (reflex details, language-vs-language
			// compare, /correspondences/set, filtered views). It MUST be 404.html: GitHub Pages
			// ignores a 200.html fallback and serves its own 404 for unknown paths, so 404.html is
			// the only shell it will return for deep links — the client router then renders them.
			fallback: '404.html',
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
