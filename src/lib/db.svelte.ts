/**
 * db.svelte.ts — browser-side SQLite access via an OPFS-backed worker (see sqliteCore.ts).
 *
 * The DB is downloaded once (a full, one-shot download — GitHub Pages may gzip it, which is fine
 * for a whole-file fetch), stored in OPFS, and queried from there via a dedicated worker. OPFS's
 * synchronous access handles are exclusive to one tab, so we can't just open the pool in every tab.
 * Instead we elect a single **leader** tab (via the Web Locks API) that owns the one worker; other
 * tabs are **followers** that proxy their queries to the leader over a BroadcastChannel. If the
 * leader tab closes, the lock frees and a follower is promoted (it re-opens the already-cached DB).
 *
 * `dbUI` exposes reactive status for the load gate; `query`/`queryOne` are the same API the rest of
 * the app uses and wait until the DB is ready.
 */
import { browser } from '$app/environment';
import { base } from '$app/paths';
import { DB_APPROX_BYTES } from './dbMeta';

// dev loads the local DB automatically (no manual gate); prod waits for the user to opt in.
const DEV = import.meta.env.DEV;

export type DbStatus = 'idle' | 'checking' | 'downloading' | 'ready' | 'error';

let status = $state<DbStatus>('idle');
let receivedBytes = $state(0);
let errorMsg = $state<string | null>(null);

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

// ---- shared state & channels ----------------------------------------------

const LOCK = 'jambu-db-leader';
const CHANNEL = 'jambu-db';
const DB_URL = () => `${base}/db/jambu.db`;

let started = false;
let role: 'follower' | 'leader' = 'follower';
let worker: Worker | null = null; // leader only
let channel: BroadcastChannel | null = null;
const tabId = browser ? crypto.randomUUID() : '';

let readyResolve: (() => void) | null = null;
let readyPromise: Promise<void> | null = null;
function ensureReadyPromise() {
	if (!readyPromise) readyPromise = new Promise((r) => (readyResolve = r));
}
function setReady() {
	status = 'ready';
	ensureReadyPromise();
	readyResolve?.();
}

// worker RPC (leader ↔ its dedicated worker)
let nextWid = 1;
const wpending = new Map<number, { resolve: (v: WMsg) => void; reject: (e: Error) => void }>();
type WMsg = { type: string; id?: number; rows?: unknown[]; cached?: boolean; received?: number };

function workerCall(msg: Record<string, unknown>): Promise<WMsg> {
	if (!worker) return Promise.reject(new Error('no worker'));
	const id = nextWid++;
	return new Promise<WMsg>((resolve, reject) => {
		wpending.set(id, { resolve, reject });
		worker!.postMessage({ ...msg, id });
	});
}
function onWorkerMessage(m: WMsg) {
	if (m.type === 'progress') {
		receivedBytes = m.received ?? 0;
		broadcastStatus();
		return;
	}
	if (m.id == null) return;
	const p = wpending.get(m.id);
	if (!p) return;
	wpending.delete(m.id);
	if (m.type === 'error') p.reject(new Error((m as unknown as { error: string }).error));
	else p.resolve(m);
}

// ---- broadcast protocol (followers ⇄ leader) ------------------------------

type Chan =
	| { k: 'hello' }
	| { k: 'status'; status: DbStatus; received: number; error: string | null }
	| { k: 'loadRequest' }
	| { k: 'req'; rid: string; msg: Record<string, unknown> }
	| { k: 'res'; rid: string; ok: boolean; data?: WMsg; error?: string };

function post(m: Chan) {
	channel?.postMessage(m);
}
function broadcastStatus() {
	if (role === 'leader') post({ k: 'status', status, received: receivedBytes, error: errorMsg });
}

const cpending = new Map<string, { resolve: (v: WMsg) => void; reject: (e: Error) => void }>();

function onChannelMessage(m: Chan) {
	switch (m.k) {
		case 'hello':
			if (role === 'leader') broadcastStatus();
			break;
		case 'status':
			if (role !== 'leader') applyRemoteStatus(m.status, m.received, m.error);
			break;
		case 'loadRequest':
			if (role === 'leader') void doLoad();
			break;
		case 'req':
			if (role === 'leader') void serveRequest(m.rid, m.msg);
			break;
		case 'res': {
			const p = cpending.get(m.rid);
			if (!p) return;
			cpending.delete(m.rid);
			if (m.ok) p.resolve(m.data as WMsg);
			else p.reject(new Error(m.error ?? 'request failed'));
			break;
		}
	}
}

function applyRemoteStatus(s: DbStatus, received: number, error: string | null) {
	receivedBytes = received;
	errorMsg = error;
	if (s === 'ready') setReady();
	else status = s; // idle / downloading / error / checking
}

async function serveRequest(rid: string, msg: Record<string, unknown>) {
	try {
		const data = await workerCall(msg);
		post({ k: 'res', rid, ok: true, data });
	} catch (err) {
		post({ k: 'res', rid, ok: false, error: err instanceof Error ? err.message : String(err) });
	}
}

/** One follower→leader round trip, with a timeout so a leader hand-off doesn't wedge us. */
function channelCall(msg: Record<string, unknown>, timeout = 6000): Promise<WMsg> {
	const rid = `${tabId}-${nextWid++}`;
	return new Promise<WMsg>((resolve, reject) => {
		const t = setTimeout(() => {
			cpending.delete(rid);
			reject(new Error('timeout'));
		}, timeout);
		cpending.set(rid, {
			resolve: (v) => {
				clearTimeout(t);
				resolve(v);
			},
			reject: (e) => {
				clearTimeout(t);
				reject(e);
			}
		});
		post({ k: 'req', rid, msg });
	});
}

// ---- leader election ------------------------------------------------------

async function becomeLeader() {
	role = 'leader';
	worker = new Worker(new URL('./sqlite.worker.ts', import.meta.url), { type: 'module' });
	worker.onmessage = (e: MessageEvent) => onWorkerMessage(e.data);
	try {
		const res = await workerCall({ type: 'init' });
		if (res.cached) setReady();
		else if (DEV) void loadDatabase(); // dev: auto-load the current local DB, no manual gate
		else if (status === 'checking') status = 'idle';
	} catch (err) {
		status = 'error';
		errorMsg = err instanceof Error ? err.message : String(err);
	}
	broadcastStatus();
}

function startEngine() {
	if (started || !browser) return;
	started = true;
	channel = new BroadcastChannel(CHANNEL);
	channel.onmessage = (e: MessageEvent<Chan>) => onChannelMessage(e.data);
	const locks = (navigator as unknown as { locks?: LockManager }).locks;
	// In dev the DB is a per-tab in-memory copy (no OPFS exclusivity), so every tab is its own
	// leader — this avoids proxying to a stale leader tab and lets each reload auto-load fresh.
	if (locks && !DEV) {
		// hold the lock (→ leadership) until this tab unloads; then a follower is promoted
		void locks.request(LOCK, { mode: 'exclusive' }, () => {
			void becomeLeader();
			return new Promise<void>(() => {});
		});
	} else {
		void becomeLeader(); // dev, or no Web Locks → single-tab leader
	}
}

// ---- public API -----------------------------------------------------------

export async function initDatabase(): Promise<void> {
	if (!browser || started) return;
	status = 'checking';
	ensureReadyPromise();
	startEngine();
	// if we didn't immediately become the leader, ask the current leader for its status
	if (role !== 'leader') post({ k: 'hello' });
}

export async function loadDatabase(): Promise<void> {
	if (!browser || status === 'downloading' || status === 'ready') return;
	status = 'downloading';
	receivedBytes = 0;
	errorMsg = null;
	ensureReadyPromise();
	if (role === 'leader') void doLoad();
	else post({ k: 'loadRequest' });
}

async function doLoad() {
	if (status === 'ready') return;
	try {
		await workerCall({ type: 'load', url: DB_URL() });
		setReady();
		broadcastStatus();
	} catch (err) {
		status = 'error';
		errorMsg = err instanceof Error ? err.message : String(err);
		broadcastStatus();
	}
}

async function whenReady(): Promise<void> {
	if (status === 'ready') return;
	ensureReadyPromise();
	await readyPromise;
}

/** Run a query, routing to the local worker (leader) or the leader tab (follower). */
async function run(msg: Record<string, unknown>): Promise<WMsg> {
	for (let attempt = 0; ; attempt++) {
		if (role === 'leader') return workerCall(msg);
		try {
			return await channelCall(msg);
		} catch (err) {
			// leader may have gone away (hand-off in progress); retry a few times, and if we were
			// promoted meanwhile the next loop uses the local worker
			if (attempt >= 3) throw err;
			await new Promise((r) => setTimeout(r, 250));
		}
	}
}

export async function query<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = []
): Promise<T[]> {
	if (!browser) throw new Error('db may only be used in the browser');
	await whenReady();
	const res = await run({ type: 'query', sql, params });
	return (res.rows ?? []) as T[];
}

export async function queryOne<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = []
): Promise<T | null> {
	const rows = await query<T>(sql, params);
	return rows.length ? rows[0] : null;
}

/** Kick off engine init + OPFS check (call once on app mount). */
export function preloadDb(): void {
	if (browser) void initDatabase();
}
