/**
 * sqlite.worker.ts — dedicated-worker fallback for browsers without SharedWorker (single-tab).
 * The SharedWorker (sqlite.shared.worker.ts) is preferred so multiple tabs can share the DB.
 */
import { openCached, load, runQuery } from './sqliteCore';

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
			const cached = await openCached();
			post({ type: 'done', id: msg.id, cached });
		} else if (msg.type === 'load') {
			await load(msg.url, (received) => post({ type: 'progress', received }));
			post({ type: 'done', id: msg.id });
		} else if (msg.type === 'query') {
			post({ type: 'result', id: msg.id, rows: runQuery(msg.sql, msg.params) });
		}
	} catch (err) {
		post({ type: 'error', id: msg.id, error: err instanceof Error ? err.message : String(err) });
	}
};
