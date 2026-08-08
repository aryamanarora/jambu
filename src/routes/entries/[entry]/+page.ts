import { base } from '$app/paths';
import { error, redirect } from '@sveltejs/kit';
import { getEntryGraph, getLemma } from '$lib/query';
import type { PageLoad } from './$types';

// Emit the enumerated canonical pages while retaining this route in the SPA for reflex IDs.
export const prerender = 'auto';

// Kept in this universal module (rather than +page.server.ts) so the production SPA route has no
// server-data dependency. The browser build removes this branch and never bundles better-sqlite3.
export async function entries() {
	if (!import.meta.env.SSR) return [];
	const { default: Database } = await import('better-sqlite3');
	const { IdIndex } = await import('$lib/dbShared');
	const database = new Database(process.env.JAMBU_DB ?? '.dbwork/jambu.db', {
		readonly: true,
		fileMustExist: true
	});
	const data = (database.prepare('SELECT data FROM ids').get() as { data: Buffer }).data;
	const misc = (database.prepare('SELECT id FROM ids_misc ORDER BY rank').all() as {
		id: string;
	}[]).map((r) => r.id);
	const idx = new IdIndex(new Uint8Array(data), misc);
	const rows = database
		.prepare('SELECT rowid AS rid FROM lem WHERE origin_rid IS NULL ORDER BY ord')
		.all() as { rid: number }[];
	database.close();
	const limit = process.env.PRERENDER_LIMIT ? parseInt(process.env.PRERENDER_LIMIT, 10) : rows.length;
	return rows.slice(0, limit).map((row) => ({ entry: idx.idOf(row.rid) }));
}

/** Native SQLite during prerender; browser SQLite for reflex IDs served by the SPA fallback. */
export const load: PageLoad = async ({ params }) => {
	if (import.meta.env.SSR) {
		const {
			getEntryGraph: getServerEntryGraph,
			getEntryMeta,
			resolveEntryId
		} = await import('$lib/server/db');
		const id = resolveEntryId(params.entry);
		const entry = getEntryMeta(id);
		if (!entry) throw error(404, 'Entry not found');
		if (entry.id !== params.entry) throw redirect(308, `${base}/entries/${entry.id}`);
		return { entry, graph: getServerEntryGraph(id) };
	}

	const entry = await getLemma(params.entry);
	if (!entry) throw error(404, 'Entry not found');
	if (entry.id !== params.entry) throw redirect(308, `${base}/entries/${entry.id}`);

	return { entry, graph: await getEntryGraph(entry.id) };
};
