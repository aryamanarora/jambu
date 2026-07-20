import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	// @sqlite.org/sqlite-wasm ships its own wasm (loaded via import.meta.url); don't pre-bundle it,
	// so Vite emits the wasm asset correctly for the worker.
	optimizeDeps: {
		exclude: ['@sqlite.org/sqlite-wasm']
	},
	worker: {
		format: 'es'
	},
	// The OPFS SAHPool VFS needs no COOP/COEP headers (no SharedArrayBuffer), so nothing special is
	// required here — which is why the in-browser DB works on GitHub Pages.
	server: {
		fs: { allow: ['..'] }
	}
});
