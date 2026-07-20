import { allLanguages } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

export const load: PageServerLoad = () => {
	return { languages: allLanguages() };
};
