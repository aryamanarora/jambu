/**
 * sqliteCore.ts — the SQLite/OPFS logic shared by both worker entry points.
 *
 * A SharedWorker (sqlite.shared.worker.ts) is used when available so every tab on the origin
 * shares ONE OPFS SAHPool — the SAHPool VFS takes an exclusive lock on its files, so only one
 * connection may hold it. A plain dedicated Worker (sqlite.worker.ts) is the single-tab fallback
 * for browsers without SharedWorker.
 */
import sqlite3InitModule from '@sqlite.org/sqlite-wasm';
import { OPFS_DB_PATH } from './dbMeta';

type Pool = {
	getFileNames(): string[];
	importDb(path: string, bytes: Uint8Array): void;
	unlink(path: string): boolean;
	OpfsSAHPoolDb: new (path: string) => DbHandle;
};
type DbHandle = {
	exec(opts: {
		sql: string;
		bind?: unknown[];
		rowMode?: string;
		returnValue?: string;
	}): Record<string, unknown>[];
};

let pool: Pool | null = null;
let db: DbHandle | null = null;
let loadingPromise: Promise<void> | null = null;

export function isReady(): boolean {
	return !!db;
}

async function ensurePool(): Promise<Pool> {
	if (pool) return pool;
	const sqlite3 = await sqlite3InitModule();
	pool = (await (
		sqlite3 as unknown as {
			installOpfsSAHPoolVfs: (o: { name: string; initialCapacity: number }) => Promise<Pool>;
		}
	).installOpfsSAHPoolVfs({ name: 'jambu-opfs', initialCapacity: 4 })) as Pool;
	return pool;
}

/** Open the cached DB if it's already in OPFS. Returns whether the DB is now ready. */
export async function openCached(): Promise<boolean> {
	const p = await ensurePool();
	if (!db && p.getFileNames().includes(OPFS_DB_PATH)) db = new p.OpfsSAHPoolDb(OPFS_DB_PATH);
	return !!db;
}

/**
 * Download the DB, import it into OPFS, and open it. Concurrent calls share one download
 * (important for the SharedWorker: many tabs may ask at once). `onProgress` reports bytes received.
 */
export function load(url: string, onProgress: (received: number) => void): Promise<void> {
	if (db) return Promise.resolve();
	if (loadingPromise) return loadingPromise;
	loadingPromise = (async () => {
		const p = await ensurePool();
		const resp = await fetch(url);
		if (!resp.ok || !resp.body) throw new Error(`download failed: HTTP ${resp.status}`);
		const reader = resp.body.getReader();
		const chunks: Uint8Array[] = [];
		let received = 0;
		for (;;) {
			const { done, value } = await reader.read();
			if (done) break;
			chunks.push(value);
			received += value.length;
			onProgress(received);
		}
		const bytes = new Uint8Array(received);
		let off = 0;
		for (const c of chunks) {
			bytes.set(c, off);
			off += c.length;
		}
		for (const name of p.getFileNames()) if (name !== OPFS_DB_PATH) p.unlink(name);
		p.importDb(OPFS_DB_PATH, bytes);
		db = new p.OpfsSAHPoolDb(OPFS_DB_PATH);
	})();
	try {
		return loadingPromise;
	} finally {
		// allow a retry if it rejected
		loadingPromise.catch(() => (loadingPromise = null));
	}
}

export function runQuery(sql: string, params: unknown[]): Record<string, unknown>[] {
	if (!db) throw new Error('database not loaded');
	return db.exec({ sql, bind: params, rowMode: 'object', returnValue: 'resultRows' });
}
