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

// In dev we skip the versioned OPFS cache and load the current local DB straight into an in-memory
// SQLite, so a rebuilt db.db is picked up on reload with no DB_VERSION bump / re-download dance.
// Production keeps the OPFS SAHPool (one-time download, cached across visits).
const DEV = import.meta.env.DEV;

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
/* eslint-disable @typescript-eslint/no-explicit-any */
type Sqlite3 = any;

let sqlite3: Sqlite3 = null;
let pool: Pool | null = null;
let db: DbHandle | null = null;
let loadingPromise: Promise<void> | null = null;

export function isReady(): boolean {
	return !!db;
}

async function ensureSqlite(): Promise<Sqlite3> {
	if (!sqlite3) sqlite3 = await sqlite3InitModule();
	return sqlite3;
}

async function ensurePool(): Promise<Pool> {
	if (pool) return pool;
	const s = await ensureSqlite();
	pool = (await s.installOpfsSAHPoolVfs({ name: 'jambu-opfs', initialCapacity: 4 })) as Pool;
	return pool;
}

/** Open the cached DB if it's already in OPFS (prod only). Returns whether the DB is now ready. */
export async function openCached(): Promise<boolean> {
	if (DEV) return !!db; // dev: nothing cached; ready only after an in-memory load
	const p = await ensurePool();
	if (!db && p.getFileNames().includes(OPFS_DB_PATH)) db = new p.OpfsSAHPoolDb(OPFS_DB_PATH);
	return !!db;
}

/** Fetch the whole DB file into one Uint8Array, reporting bytes received. */
async function fetchBytes(url: string, onProgress: (received: number) => void): Promise<Uint8Array> {
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
	return bytes;
}

/**
 * Load the DB and open it. In dev this deserialises the bytes into an in-memory DB (always the
 * current local file); in prod it imports into OPFS and opens from there. Concurrent calls share
 * one load (important for the SharedWorker: many tabs may ask at once).
 */
export function load(url: string, onProgress: (received: number) => void): Promise<void> {
	if (db) return Promise.resolve();
	if (loadingPromise) return loadingPromise;
	loadingPromise = (async () => {
		const bytes = await fetchBytes(url, onProgress);
		if (DEV) {
			const s = await ensureSqlite();
			const h = new s.oo1.DB();
			const ptr = s.wasm.allocFromTypedArray(bytes);
			h.checkRc(
				s.capi.sqlite3_deserialize(
					h.pointer,
					'main',
					ptr,
					bytes.length,
					bytes.length,
					s.capi.SQLITE_DESERIALIZE_FREEONCLOSE | s.capi.SQLITE_DESERIALIZE_RESIZEABLE
				)
			);
			db = h as DbHandle;
		} else {
			const p = await ensurePool();
			for (const name of p.getFileNames()) if (name !== OPFS_DB_PATH) p.unlink(name);
			p.importDb(OPFS_DB_PATH, bytes);
			db = new p.OpfsSAHPoolDb(OPFS_DB_PATH);
		}
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
