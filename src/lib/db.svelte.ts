/**
 * db.svelte.ts — browser-side SQLite access via an OPFS-backed worker (see sqliteCore.ts).
 *
 * The DB is downloaded once (a full, one-shot download — GitHub Pages may gzip it, which is fine
 * for a whole-file fetch), stored in OPFS, and queried from there via a dedicated worker. OPFS's
 * synchronous access handles are exclusive to one tab, so we can't just open the pool in every tab.
 * Instead we elect a single **leader** tab (via the Web Locks API) that owns the one worker; other
 * tabs are **followers** that proxy their queries to it over a BroadcastChannel. Leadership moves
 * to the visible tab so a suspended background tab cannot leave active-page queries hanging.
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
// A route load can query the database before the root layout mounts (notably on a direct
// /entries/:id or /reflexes/:id visit). Remember that demand so initialization can load an
// uncached database instead of leaving SvelteKit hydration waiting for onMount forever.
let loadDemanded = false;
let role: 'follower' | 'leader' = 'follower';
let worker: Worker | MessagePort | null = null; // dedicated worker, or the shared dev worker's port
let stopWorker: (() => void) | null = null;
let channel: BroadcastChannel | null = null;
let lockManager: LockManager | null = null;
let lockRequestActive = false;
let releaseLeadership: (() => void) | null = null;
let leadershipYieldRequested = false;
const tabId = browser ? crypto.randomUUID() : '';

let readyResolve: (() => void) | null = null;
let readyPromise: Promise<void> | null = null;
function ensureReadyPromise() {
	if (!readyPromise) readyPromise = new Promise((r) => (readyResolve = r));
}
function setReady() {
	status = 'ready';
	loadDemanded = false;
	ensureReadyPromise();
	readyResolve?.();
}

function setNotReady() {
	status = 'idle';
	receivedBytes = 0;
	errorMsg = null;
	readyPromise = null;
	readyResolve = null;
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
	| { k: 'hello'; visible: boolean }
	| { k: 'leaderReleased' }
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
			if (role === 'leader' && m.visible && document.hidden) yieldLeadership();
			else if (role === 'leader') broadcastStatus();
			break;
		case 'leaderReleased':
			if (role !== 'leader') {
				for (const pending of cpending.values()) pending.reject(new Error('database leader changed'));
				cpending.clear();
			}
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
	else if (s === 'idle' && loadDemanded) {
		// Keep the promise currently awaited by the route load, then ask the leader to satisfy it.
		status = 'idle';
		void loadDatabase();
	} else if (s === 'idle') setNotReady();
	else status = s; // idle / downloading / error / checking
}

async function serveRequest(rid: string, msg: Record<string, unknown>) {
	try {
		const data = await workerCall(msg);
		if (msg.type === 'delete') {
			setNotReady();
			broadcastStatus();
		}
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
	const sharedDevWorker = DEV && typeof SharedWorker !== 'undefined';
	if (sharedDevWorker) {
		const shared = new SharedWorker(new URL('./sqlite.shared.worker.ts', import.meta.url), {
			type: 'module',
			name: 'jambu-dev-db'
		});
		worker = shared.port;
		shared.port.start();
		stopWorker = () => shared.port.close();
	} else {
		const dedicated = new Worker(new URL('./sqlite.worker.ts', import.meta.url), { type: 'module' });
		worker = dedicated;
		stopWorker = () => dedicated.terminate();
	}
	worker.onmessage = (e: MessageEvent) => onWorkerMessage(e.data);
	try {
		// A named SharedWorker is one process for every dev tab on this origin. Its init performs a
		// cheap HEAD freshness check and downloads only when .dbwork/jambu.db has changed.
		if (sharedDevWorker) {
			status = 'downloading';
			await workerCall({ type: 'init', url: DB_URL() });
			setReady();
		} else {
			const res = await workerCall({ type: 'init' });
			if (res.cached) setReady();
			else if (DEV || loadDemanded) void loadDatabase(); // query-driven direct load, or dev fallback
			else if (status === 'checking') status = 'idle';
		}
	} catch (err) {
		status = 'error';
		errorMsg = err instanceof Error ? err.message : String(err);
	}
	broadcastStatus();
}

function yieldLeadership() {
	if (role !== 'leader') return;
	leadershipYieldRequested = true;
	post({ k: 'leaderReleased' });
	stopWorker?.();
	worker = null;
	stopWorker = null;
	for (const pending of wpending.values()) pending.reject(new Error('database leadership released'));
	wpending.clear();
	role = 'follower';
	releaseLeadership?.();
	releaseLeadership = null;
}

function requestLeadership() {
	if (!lockManager || lockRequestActive || document.hidden || role === 'leader') return;
	lockRequestActive = true;
	void lockManager
		.request(LOCK, { mode: 'exclusive' }, async () => {
			if (document.hidden) return;
			leadershipYieldRequested = false;
			await becomeLeader();
			if (document.hidden || leadershipYieldRequested || role !== 'leader') {
				if (role === 'leader') yieldLeadership();
				return;
			}
			await new Promise<void>((resolve) => (releaseLeadership = resolve));
		})
		.finally(() => {
			lockRequestActive = false;
			releaseLeadership = null;
			if (!document.hidden && role !== 'leader') requestLeadership();
		});
}

function startEngine() {
	if (started || !browser) return;
	started = true;
	channel = new BroadcastChannel(CHANNEL);
	channel.onmessage = (e: MessageEvent<Chan>) => onChannelMessage(e.data);
	lockManager = (navigator as unknown as { locks?: LockManager }).locks ?? null;
	// In dev every tab talks directly to one named SharedWorker (or gets an independent dedicated
	// worker on browsers without SharedWorker). Production retains the Web-Locks leader/follower
	// protocol because its persistent OPFS database has exclusive connection semantics.
	if (lockManager && !DEV) {
		requestLeadership();
		document.addEventListener('visibilitychange', () => {
			if (!document.hidden) {
				requestLeadership();
				post({ k: 'hello', visible: true });
			}
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
	if (role !== 'leader') post({ k: 'hello', visible: !document.hidden });
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

/** Close the active connection and remove the versioned database from this browser. */
export async function deleteDatabase(): Promise<void> {
	if (!browser || status !== 'ready') return;
	await run({ type: 'delete' });
	setNotReady();
	if (role === 'leader') broadcastStatus();
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
	loadDemanded = true;
	ensureReadyPromise();
	// Usually the root layout preloads the engine. During a direct route visit, however, the
	// universal page load runs before layout onMount; starting here breaks that hydration cycle.
	if (!started) await initDatabase();
	else if (status === 'idle') await loadDatabase();
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

/** Candidate sets for `vin_in`, shipped with the query that uses them: [setId, members][]. */
export type QuerySets = Array<[number, number[]]>;

export async function query<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = [],
	sets?: QuerySets
): Promise<T[]> {
	if (!browser) throw new Error('db may only be used in the browser');
	await whenReady();
	const res = await run({ type: 'query', sql, params, sets });
	return (res.rows ?? []) as T[];
}

export async function queryOne<T = Record<string, unknown>>(
	sql: string,
	params: unknown[] = [],
	sets?: QuerySets
): Promise<T | null> {
	const rows = await query<T>(sql, params, sets);
	return rows.length ? rows[0] : null;
}

/** Kick off engine init + OPFS check (call once on app mount). */
export function preloadDb(): void {
	if (browser) void initDatabase();
}
