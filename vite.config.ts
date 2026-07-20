import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	// sql.js-httpvfs is a CommonJS package; force esbuild to pre-bundle it (adds the CJS→ESM
	// interop shim) even though we import it dynamically. Its worker + wasm come in via `?url`.
	optimizeDeps: {
		include: ['sql.js-httpvfs']
	},
	worker: {
		format: 'es'
	},
	// COOP/COEP are not required for sql.js-httpvfs (it uses plain fetch Range, not SharedArrayBuffer),
	// so no special headers are needed — which is exactly why it works on GitHub Pages.
	server: {
		fs: { allow: ['..'] }
	}
});
