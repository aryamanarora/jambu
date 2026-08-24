import { allLanguages, getDb } from '$lib/server/db';
import type { DialectIndexRow } from '$lib/types';
import type { PageServerLoad } from './$types';

export const prerender = true;

export const load: PageServerLoad = () => {
	const dialects = getDb()
		.prepare(
			`SELECT token, id, name, language_id, location, quality, lemma_count, lat, long, color
			 FROM dialects WHERE lemma_count > 0 ORDER BY name, id`
		)
		.all() as DialectIndexRow[];
	return { languages: allLanguages(), dialects };
};
