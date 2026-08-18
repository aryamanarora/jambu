import { dev } from '$app/environment';
import { error, json } from '@sveltejs/kit';
import { listSources, queryRows, saveCorrection } from '$lib/server/ocrWorkbench';
import type { RequestHandler } from './$types';

export const prerender = false;

function localOnly(request: Request) {
	if (!dev) error(404, 'Not found');
	const host = new URL(request.url).hostname;
	if (!['localhost', '127.0.0.1', '::1'].includes(host)) error(403, 'Development interface is local-only');
}

export const GET: RequestHandler = async ({ request, url }) => {
	localOnly(request);
	try {
		const source = url.searchParams.get('source');
		if (!source) return json({ sources: await listSources() });
		const query = url.searchParams.get('q') ?? '';
		const status = url.searchParams.get('status') ?? 'pending';
		const page = Math.max(1, Number(url.searchParams.get('page') ?? 1) || 1);
		return json(await queryRows(source, query, status, page));
	} catch (cause) {
		error(500, cause instanceof Error ? cause.message : String(cause));
	}
};

export const POST: RequestHandler = async ({ request }) => {
	localOnly(request);
	try {
		const body = await request.json() as Record<string, string> & { source?: string; remove?: boolean };
		if (!body.source) error(400, 'Choose an OCR source');
		const status = await saveCorrection(body.source, body);
		return json({ ok: true, status });
	} catch (cause) {
		if (cause && typeof cause === 'object' && 'status' in cause) throw cause;
		error(400, cause instanceof Error ? cause.message : String(cause));
	}
};
