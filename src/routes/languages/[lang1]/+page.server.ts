import { error, redirect } from '@sveltejs/kit';
import { base } from '$app/paths';
import { allDialectIds, allLanguageIds, getDialectLanguageId, getLanguageRow } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

export function entries() {
	return [...allLanguageIds(), ...allDialectIds()];
}

export const load: PageServerLoad = ({ params }) => {
	const language = getLanguageRow(params.lang1);
	if (!language) {
		const parent = getDialectLanguageId(params.lang1);
		if (parent) throw redirect(308, `${base}/languages/${parent}`);
		throw error(404, 'Language not found');
	}
	return { language };
};
