/**
 * db.svelte.ts — browser-side SQLite access via an OPFS-backed worker (see sqlite.worker.ts).
 *
 * The DB is downloaded once (a full, one-shot download — GitHub Pages may gzip it, which is fine
 * for a whole-file fetch), stored in OPFS, and queried from there. `dbUI` exposes reactive status
 * for the load gate; `query`/`queryOne` are the same API the rest of the app already uses and
 * transparently wait until the DB is ready.
 */
import { browser } from '$app/environment';
import { base } from '$app/paths';
import { OPFS_DB_PATH, DB_APPROX_BYTES } from './dbMeta';

export type DbStatus = 'idle' | 'checking' | 'downloading' | 'ready' | 'error';

let status = $state<DbStatus>('idle');
let receivedBytes = $state(0);
let errorMsg = $state<string | null>(null);

/** Reactive view of the load state, for the download-gate UI. */
export const dbUI = {
	get status() {
		return status;
	},
	get ready() {
		return status === 'ready';
	},
	get receivedBytes() {
		return receivedBytes;
	},
	/** 0..1 download progress (approximate — the transfer is gzipped, so we compare against a
	 *  known uncompressed size). */
	get progress() {
		return Math.min(1, receivedBytes / DB_APPROX_BYTES);
	},
	get error() {
		return errorMsg;
	}
};

// ---- worker RPC ------------------------------------------------------------

let worker: Worker | null = null;
let nextId = 1;
const pending = new Map<number, { resolve: (v: unknown) => void; reject: (e: Error) => void }>();
let readyResolve: (() => void) | null = null;
// resolves once the DB is queryable (cached-open or freshly loaded); queries await this.
let readyPromise: Promise<void> | null = null;

function ensureWorker(): Worker {
	if (worker) return worker;
	worker = new Worker(new URL('./sqlite.worker.ts', import.meta.url), { type: 'module' });
	worker.onmessage = (e: MessageEvent) => {
		const m = e.data;
		if (m.type === 'progress') {
			receivedBytes = m.received;
			return;
		}
		const p = pending.get(m.id);
		if (!p) return;
		pending.delete(m.id);
		if (m.type === 'error') p.reject(new Error(m.error));
		else p.resolve(m);
	};
	return worker;
}

function call<T = unknown>(msg: Record<string, unknown>): Promise<T> {
	const w = ensureWorker();
	const id = nextId++;
	return new Promise<T>((resolve, reject) => {
		pending.set(id, { resolve: resolve as (v: unknown) => void, reject });
		w.postMessage({ ...msg, id });
	});
}

/**
 * Initialise the worker and check OPFS. If a cached copy exists it becomes ready immediately;
 * otherwise status stays 'idle' until the user triggers {@link loadDatabase}. Safe to call repeatedly.
 */
export async function initDatabase(): Promise<void> {
	if (!browser || status !== 'idle') return;
	status = 'checking';
	if (!readyPromise) readyPromise = new Promise((r) => (readyResolve = r));
	try {
		const res = await call<{ cached: boolean }>({ type: 'init' });
		if (res.cached) {
			status = 'ready';
			readyResolve?.();
		} else {
			status = 'idle'; // waiting for the user to opt into the download
		}
	} catch (err) {
		status = 'error';
		errorMsg = err instanceof Error ? err.message : String(err);
	}
}

/** Download the DB, store it in OPFS, and become ready. Triggered by the load button. */
export async function loadDatabase(): Promise<void> {
	if (!browser || status === 'downloading' || status === 'ready') return;
	status = 'downloading';
	receivedBytes = 0;
	errorMsg = null;
	if (!readyPromise) readyPromise = new Promise((r) => (readyResolve = r));
	try {
		await call({ type: 'load', url: `${base}/db/jambu.db` });
		status = 'ready';
		readyResolve?.();
	} catch (err) {
		status = 'error';
		errorMsg = err instanceof Error ? err.message : String(err);
	}
}

async function whenReady(): Promise<void> {
	if (status === 'ready') return;
	if (!readyPromise) readyPromise = new Promise((r) => (readyResolve = r));
	await readyPromise;
}

// ---- query API (unchanged signatures) --------------------------------------

export async function query<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = []
): Promise<T[]> {
	if (!browser) throw new Error('db may only be used in the browser');
	await whenReady();
	const res = await call<{ rows: T[] }>({ type: 'query', sql, params });
	return res.rows;
}

export async function queryOne<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = []
): Promise<T | null> {
	const rows = await query<T>(sql, params);
	return rows.length ? rows[0] : null;
}

/** Kick off worker init + OPFS check (call once on app mount). */
export function preloadDb(): void {
	if (browser) void initDatabase();
}
