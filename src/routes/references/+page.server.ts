import { allReferences, allReferenceCladeDistributions } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const prerender = true;

export const load: PageServerLoad = () => {
	return { references: allReferences(), cladeDistributions: allReferenceCladeDistributions() };
};
