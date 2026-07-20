import { error } from '@sveltejs/kit';
import { allReferenceIds, getReferenceRow } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

export function entries() {
	return allReferenceIds();
}

export const load: PageServerLoad = ({ params }) => {
	const reference = getReferenceRow(params.ref);
	if (!reference) throw error(404, 'Source not found');
	return { reference };
};
