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
	// strip the stray <html>/<body> wrapper some source entries carry (a BeautifulSoup artifact)
	if (h.includes('<html') || h.includes('<body')) h = h.replace(/<\/?(?:html|body)>/g, '');
	// keep the entry id in data-eref so the hover popover can lazy-load the target
	return h.includes('data-entry')
		? h.replace(/<a data-entry="([^"]*)"/g, `<a class="eref" data-eref="$1" href="${base}/entries/$1"`)
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

/** Turn an internal bibliography abbreviation such as `T1962—1966` into the compact
 * author–date form readers expect in running text (`Turner 1962–1966`). */
export function referenceLabel(reference: {
	id: string;
	short: string | null;
	source: string | null;
}): string {
	const source = (reference.source ?? '')
		.replace(/\\([\\`*{}\[\]()#+\-.!_>])/g, '$1')
		.replace(/<[^>]*>/g, '')
		.trim();
	const sourceLines = source.split(/\n|\\n/);
	const authorLine = /^Reference abbreviation\b/i.test(source)
		? ''
		: ((sourceLines.length > 1 ? sourceLines[0] : source.split(',')[0])
			?.replace(/[.*_`]+$/g, '')
			.trim() ?? '');
	const people = authorLine
		.replace(/,?\s+and\s+/gi, '|')
		.split(/\s*\|\s*|,\s*/)
		.map((name) => name.trim())
		.filter(Boolean);
	const surname = (name: string) => {
		const parts = name.replace(/[.,]+$/g, '').split(/\s+/).filter(Boolean);
		while (parts.length > 1 && /^[A-Z]$/.test(parts.at(-1)!)) parts.pop();
		return parts.at(-1) ?? '';
	};
	let authors = '';
	if (people.length === 1) authors = surname(people[0]);
	else if (people.length === 2) authors = `${surname(people[0])} & ${surname(people[1])}`;
	else if (people.length > 2) authors = `${surname(people[0])} et al.`;

	const shortYear = reference.short?.match(/(?:^|\D)((?:1[5-9]|20)\d{2})/)?.[1];
	const citationLead = source.split(/\n(?:URL|ISBN|DOI):?/i)[0] ?? source;
	const sourceYears = [...citationLead.matchAll(/\b(?:1[5-9]|20)\d{2}(?:[–—-](?:\d{2}|\d{4}))?\b/g)];
	const year = shortYear || sourceYears.at(-1)?.[0]?.slice(0, 4) || '';
	return [authors, year].filter(Boolean).join(' ') || reference.short || reference.id;
}

/** Parse a cognateset key "CODE:label" into display parts (mirrors the template logic). */
export function cognatesetParts(key: string | null | undefined): { code: string | null; label: string } {
	if (!key) return { code: null, label: '' };
	const i = key.indexOf(':');
	if (i === -1) return { code: null, label: key };
	return { code: key.slice(0, i), label: key.slice(i + 1) };
}


/** Ancestry-line label for a node, keyed on its accepted (rank-1) edge kind. */
export function relationLabel(l: {
	relation?: string | null;
	origin_lemma_id?: string | null;
}): string {
	switch (l.relation) {
		case 'borrowed':
			return 'Borrowed from';
		case 'variant':
			return 'Variant of';
		case 'reflex':
			return 'Reflex of';
		default:
			return l.origin_lemma_id ? 'Reflex of' : 'Derived from';
	}
}
