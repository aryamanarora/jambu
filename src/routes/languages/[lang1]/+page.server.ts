import { error } from '@sveltejs/kit';
import { allLanguageIds, getLanguageRow } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

export function entries() {
	return allLanguageIds();
}

export const load: PageServerLoad = ({ params }) => {
	const language = getLanguageRow(params.lang1);
	if (!language) throw error(404, 'Language not found');
	return { language };
};
