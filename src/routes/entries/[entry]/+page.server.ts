import { error } from '@sveltejs/kit';
import { allEntryIds, getEntryMeta, getEntryGraph } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

// Enumerate every headword so each entry gets a static, citable, SEO-friendly page.
export function entries() {
	return allEntryIds();
}

export const load: PageServerLoad = ({ params }) => {
	const entry = getEntryMeta(params.entry);
	if (!entry) throw error(404, 'Entry not found');
	return { entry, graph: getEntryGraph(params.entry) };
};
