import { globalStats } from '$lib/server/db';
import type { PageServerLoad } from './$types';

// Prerendered (see +page.ts): the corpus totals are baked in at build time, so the homepage
// still ships as plain static HTML with no client-side DB fetch.
export const load: PageServerLoad = () => {
	return { stats: globalStats() };
};
