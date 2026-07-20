/**
 * sqlite.worker.ts — runs SQLite (WASM) in a Web Worker, backed by the OPFS SAHPool VFS.
 *
 * The whole DB is downloaded once and imported into OPFS (the browser's Origin Private File
 * System), then queried from "disk" — so we never hold the full ~300 MB in RAM, and the copy
 * persists across sessions (the cache). The SAHPool VFS needs no COOP/COEP headers, which is why
 * this works on GitHub Pages. Sync access handles are only available in a Worker, hence this file.
 */
import sqlite3InitModule, { type Sqlite3Static } from '@sqlite.org/sqlite-wasm';
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

let sqlite3: Sqlite3Static | null = null;
let pool: Pool | null = null;
let db: DbHandle | null = null;

async function ensurePool(): Promise<Pool> {
	if (pool) return pool;
	sqlite3 = await sqlite3InitModule();
	// stable pool name; the cached DB file itself is versioned (OPFS_DB_PATH), and stale versions
	// are unlinked on load, so bumping DB_VERSION reuses the pool and re-downloads cleanly.
	pool = (await (
		sqlite3 as unknown as {
			installOpfsSAHPoolVfs: (o: { name: string; initialCapacity: number }) => Promise<Pool>;
		}
	).installOpfsSAHPoolVfs({ name: 'jambu-opfs', initialCapacity: 4 })) as Pool;
	return pool;
}

type InMsg =
	| { type: 'init'; id: number }
	| { type: 'load'; id: number; url: string }
	| { type: 'query'; id: number; sql: string; params: unknown[] };

function post(msg: Record<string, unknown>) {
	(self as unknown as Worker).postMessage(msg);
}

self.onmessage = async (e: MessageEvent<InMsg>) => {
	const msg = e.data;
	try {
		if (msg.type === 'init') {
			const p = await ensurePool();
			const cached = p.getFileNames().includes(OPFS_DB_PATH);
			if (cached) db = new p.OpfsSAHPoolDb(OPFS_DB_PATH);
			post({ type: 'done', id: msg.id, cached });
		} else if (msg.type === 'load') {
			const p = await ensurePool();
			const resp = await fetch(msg.url);
			if (!resp.ok || !resp.body) throw new Error(`download failed: HTTP ${resp.status}`);
			const reader = resp.body.getReader();
			const chunks: Uint8Array[] = [];
			let received = 0;
			for (;;) {
				const { done, value } = await reader.read();
				if (done) break;
				chunks.push(value);
				received += value.length;
				post({ type: 'progress', received });
			}
			const bytes = new Uint8Array(received);
			let off = 0;
			for (const c of chunks) {
				bytes.set(c, off);
				off += c.length;
			}
			// drop any stale cached DBs, then import fresh and open
			for (const name of p.getFileNames()) if (name !== OPFS_DB_PATH) p.unlink(name);
			p.importDb(OPFS_DB_PATH, bytes);
			db = new p.OpfsSAHPoolDb(OPFS_DB_PATH);
			post({ type: 'done', id: msg.id });
		} else if (msg.type === 'query') {
			if (!db) throw new Error('database not loaded');
			const rows = db.exec({
				sql: msg.sql,
				bind: msg.params,
				rowMode: 'object',
				returnValue: 'resultRows'
			});
			post({ type: 'result', id: msg.id, rows });
		}
	} catch (err) {
		post({ type: 'error', id: msg.id, error: err instanceof Error ? err.message : String(err) });
	}
};
