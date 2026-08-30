/**
 * One in-memory SQLite connection shared by every development tab on this origin.
 *
 * Each connecting tab sends `init` with the current DB URL. sqliteCore.load() performs a cheap
 * validator request and only replaces the connection when the served database has changed.
 * Production continues to use the Web-Locks/OPFS path in db.svelte.ts.
 */
import { deleteCached, load, runQuery } from './sqliteCore';

type InMsg =
	| { type: 'init'; id: number; url: string }
	| { type: 'load'; id: number; url: string }
	| { type: 'delete'; id: number }
	| { type: 'query'; id: number; sql: string; params: unknown[]; sets?: Array<[number, number[]]> };

function respond(port: MessagePort, msg: Record<string, unknown>) {
	port.postMessage(msg);
}

async function handle(port: MessagePort, msg: InMsg) {
	try {
		if (msg.type === 'init' || msg.type === 'load') {
			await load(msg.url, (received) => respond(port, { type: 'progress', received }));
			respond(port, { type: 'done', id: msg.id, cached: true });
		} else if (msg.type === 'delete') {
			await deleteCached();
			respond(port, { type: 'done', id: msg.id });
		} else if (msg.type === 'query') {
			respond(port, { type: 'result', id: msg.id, rows: runQuery(msg.sql, msg.params, msg.sets) });
		}
	} catch (err) {
		respond(port, {
			type: 'error',
			id: msg.id,
			error: err instanceof Error ? err.message : String(err)
		});
	}
}

const scope = self as unknown as {
	onconnect: ((event: MessageEvent) => void) | null;
};

scope.onconnect = (event: MessageEvent) => {
	const port = event.ports[0];
	port.onmessage = (message: MessageEvent<InMsg>) => void handle(port, message.data);
	port.start();
};
