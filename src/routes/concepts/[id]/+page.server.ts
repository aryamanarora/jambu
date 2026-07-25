import { error } from '@sveltejs/kit';
import { allConceptIds, getConceptDetail } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

export function entries() {
	return allConceptIds();
}

export const load: PageServerLoad = ({ params }) => {
	const detail = getConceptDetail(params.id);
	if (!detail) throw error(404, 'Concept not found');
	return detail;
};
