import { error } from '@sveltejs/kit';
import { defaultConceptId, getConceptDetail } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

// /concepts is the atlas. With no concept named it opens on the most widely attested one; the
// picker in its header changes concepts from there, and /concepts/browse still lists them all.
export const load: PageServerLoad = () => {
	const id = defaultConceptId();
	const detail = id ? getConceptDetail(id) : null;
	if (!detail) throw error(404, 'No concepts available');
	return detail;
};
