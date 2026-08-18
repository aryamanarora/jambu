import { dev } from '$app/environment';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ url }) => {
	if (!dev) error(404, 'Not found');
	if (!['localhost', '127.0.0.1', '::1'].includes(url.hostname))
		error(403, 'Development interface is local-only');
	return {};
};
