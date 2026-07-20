/**
 * render.ts — text/HTML helpers matching neojambu's Jinja filters.
 *
 * NOTE on trust: the Jambu dataset intentionally embeds hand-authored HTML in fields like
 * `word`, `gloss`, and `notes` (see neojambu commit 4319443), and the original templates render
 * them with `| safe`. We reproduce that: these fields are trusted, curated content, rendered raw.
 */
import { marked } from 'marked';
import { base } from '$app/paths';

marked.setOptions({ breaks: false, gfm: true });

// The data prep step (../data/link_refs.py) marks cross-references to other entries as
// `<a data-entry="ID">…</a>` (route-agnostic). Turn those into real, base-prefixed links here.
function linkEntries(h: string): string {
	return h.includes('data-entry')
		? h.replace(/<a data-entry="([^"]*)"/g, `<a class="eref" href="${base}/entries/$1"`)
		: h;
}

/** Markdown → HTML, replicating the app's `\n` → paragraph-break preprocessing. */
export function md(text: string | null | undefined): string {
	if (!text) return '';
	return linkEntries(marked.parse(text.replace(/\\n/g, '\n\n'), { async: false }) as string);
}

/** Pass-through for fields that already contain trusted HTML (the old `| safe`). */
export function safe(text: string | null | undefined): string {
	return linkEntries(text ?? '');
}

/** Strip tags for contexts that used Jinja `| striptags` (e.g. map popups, plain titles). */
export function striptags(text: string | null | undefined): string {
	if (!text) return '';
	return text.replace(/<[^>]*>/g, '');
}

/** Parse a cognateset key "CODE:label" into display parts (mirrors the template logic). */
export function cognatesetParts(key: string | null | undefined): { code: string | null; label: string } {
	if (!key) return { code: null, label: '' };
	const i = key.indexOf(':');
	if (i === -1) return { code: null, label: key };
	return { code: key.slice(0, i), label: key.slice(i + 1) };
}
