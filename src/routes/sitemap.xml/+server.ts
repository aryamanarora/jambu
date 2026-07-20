import { allEntryIds, allLanguageIds, allReferenceIds } from '$lib/server/db';
import { base } from '$app/paths';

// Prerendered sitemap covering the citable canonical pages (entries, languages, references)
// plus the top-level list pages. Set SITE_URL in CI to your deployed origin.
export const prerender = true;

const SITE_URL = (process.env.SITE_URL ?? '').replace(/\/$/, '');

export function GET() {
	const urls: string[] = [
		'/',
		'/entries',
		'/reflexes',
		'/languages',
		'/references',
		...allEntryIds().map((e) => `/entries/${e.entry}`),
		...allLanguageIds().map((l) => `/languages/${l.lang1}`),
		...allReferenceIds().map((r) => `/references/${r.ref}`)
	];

	const body =
		`<?xml version="1.0" encoding="UTF-8"?>\n` +
		`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
		urls
			.map((u) => `  <loc>${SITE_URL}${base}${u}</loc>`)
			.map((loc) => `  <url>\n  ${loc}\n  </url>`)
			.join('\n') +
		`\n</urlset>\n`;

	return new Response(body, {
		headers: { 'Content-Type': 'application/xml' }
	});
}
