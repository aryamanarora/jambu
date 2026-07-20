/**
 * db.ts — browser-side SQLite access via sql.js-httpvfs.
 *
 * The transformed, chunked DB lives at `${base}/db/` (config.json + jambu.sqlite3.NNN).
 * sql.js-httpvfs runs SQLite in a Web Worker and fetches only the byte ranges each query
 * touches (HTTP Range), so the ~122 MB DB is never fully downloaded. No COOP/COEP headers are
 * needed (it uses plain fetch, not SharedArrayBuffer) — which is why it works on GitHub Pages.
 *
 * Everything here is client-only; the sql.js-httpvfs package (CommonJS, browser-only) is
 * dynamically imported inside the browser guard so SSR/prerender never touches it.
 */
import { browser } from '$app/environment';
import { base } from '$app/paths';
// `?url` imports resolve through node resolution and emit the asset; safe on the server (a string).
import workerUrl from 'sql.js-httpvfs/dist/sqlite.worker.js?url';
import wasmUrl from 'sql.js-httpvfs/dist/sql-wasm.wasm?url';

type QueryFn = (sql: string, params?: unknown[]) => Promise<Record<string, unknown>[]>;

let workerPromise: Promise<{ query: QueryFn }> | null = null;

async function initWorker(): Promise<{ query: QueryFn }> {
	if (!browser) throw new Error('db.ts may only be used in the browser');
	// dynamic import keeps the browser-only CJS package out of the SSR/prerender graph
	const mod = (await import('sql.js-httpvfs')) as unknown as {
		createDbWorker?: CreateDbWorker;
		default?: { createDbWorker?: CreateDbWorker };
	};
	const createDbWorker = mod.createDbWorker ?? mod.default?.createDbWorker;
	if (!createDbWorker) throw new Error('sql.js-httpvfs: createDbWorker not found');

	// Single-file "full" mode: SQLite reads byte ranges directly from one jambu.db via HTTP Range.
	// (Chunked/split mode is unsafe here — its read-ahead can straddle a server-chunk boundary and
	// fail on large scans, and maxReadSpeed isn't configurable through the public API.)
	const w = await createDbWorker(
		[
			{
				from: 'inline',
				config: {
					serverMode: 'full',
					url: `${base}/db/jambu.db`,
					requestChunkSize: 8192 // == the DB page_size
				}
			}
		],
		workerUrl,
		wasmUrl
	);
	return {
		query: (sql: string, params: unknown[] = []) =>
			w.db.query(sql, params) as Promise<Record<string, unknown>[]>
	};
}

type CreateDbWorker = (
	config: unknown[],
	workerUrl: string,
	wasmUrl: string
) => Promise<{ db: { query: (sql: string, params?: unknown[]) => Promise<unknown> } }>;

function getWorker(): Promise<{ query: QueryFn }> {
	if (!workerPromise) workerPromise = initWorker();
	return workerPromise;
}

/** Run a parameterised query and get back typed rows. */
export async function query<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = []
): Promise<T[]> {
	const w = await getWorker();
	return (await w.query(sql, params)) as T[];
}

/** Convenience: first row or null. */
export async function queryOne<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = []
): Promise<T | null> {
	const rows = await query<T>(sql, params);
	return rows.length ? rows[0] : null;
}

/** Warm up the worker (e.g. on route entry) so the first real query is faster. */
export function preloadDb(): void {
	if (browser) void getWorker();
}
