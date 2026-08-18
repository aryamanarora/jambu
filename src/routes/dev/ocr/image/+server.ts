import { dev } from '$app/environment';
import { error } from '@sveltejs/kit';
import { renderDocumentImage } from '$lib/server/ocrWorkbench';
import type { RequestHandler } from './$types';

export const prerender = false;

function localOnly(request: Request) {
	if (!dev) error(404, 'Not found');
	const host = new URL(request.url).hostname;
	if (!['localhost', '127.0.0.1', '::1'].includes(host)) error(403, 'Development interface is local-only');
}

export const GET: RequestHandler = async ({ request, url }) => {
	localOnly(request);
	const source = url.searchParams.get('source') ?? '';
	const document = url.searchParams.get('document') ?? '';
	const entry = url.searchParams.get('entry') ?? '';
	const view = url.searchParams.get('view') === 'page' ? 'page' : 'crop';
	if (!source || !document || !entry) error(400, 'Source, document, and entry are required');
	try {
		const image = await renderDocumentImage(source, document, entry, view);
		const body = image.buffer.slice(image.byteOffset, image.byteOffset + image.byteLength) as ArrayBuffer;
		return new Response(body, {
			headers: {
				'content-type': 'image/png',
				'cache-control': 'private, max-age=3600'
			}
		});
	} catch (cause) {
		error(404, cause instanceof Error ? cause.message : String(cause));
	}
};
