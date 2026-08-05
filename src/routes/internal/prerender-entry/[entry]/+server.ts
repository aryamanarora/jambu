import { error, json } from '@sveltejs/kit';
import { getEntryGraph, getEntryMeta, resolveEntryId } from '$lib/server/db';
import type { RequestHandler } from './$types';

/** Build-time data source for prerendered entry pages; absent from the static deployment. */
export const GET: RequestHandler = ({ params }) => {
	const id = resolveEntryId(params.entry);
	const entry = getEntryMeta(id);
	if (!entry) throw error(404, 'Entry not found');
	return json({ entry, graph: getEntryGraph(id) });
};
