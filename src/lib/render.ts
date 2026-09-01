/**
 * render.ts — text/HTML helpers matching neojambu's Jinja filters.
 *
 * NOTE on trust: the Jambu dataset intentionally embeds hand-authored HTML in fields like
 * `word`, `gloss`, and `notes` (see neojambu commit 4319443), and the original templates render
 * them with `| safe`. We reproduce that: these fields are trusted, curated content, rendered raw.
 */
import { marked } from 'marked';
import { unicodeSearchFold } from './unicodeSearch';
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
	// Pybtex's Markdown backend writes a literal LaTeX command for `~` in URLs. Normalise it
	// before parsing so author-homepage links remain valid even in an already-built database.
	const normalized = text.replace(/\\+textasciitilde\s*/g, '~');
	return linkEntries(marked.parse(normalized.replace(/\\n/g, '\n\n'), { async: false }) as string);
}

/** Pass-through for fields that already contain trusted HTML (the old `| safe`). */
export function safe(text: string | null | undefined): string {
	return linkEntries(text ?? '');
}

const escapeRegex = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const escapeText = (value: string) =>
	value
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#39;');

export type HighlightQuery = string | Array<string | null | undefined> | null | undefined;

function highlightValues(query: HighlightQuery): string[] {
	const values = (Array.isArray(query) ? query : [query])
		.map((value) => value?.trim() ?? '')
		.filter(Boolean);
	return [...new Map(values.map((value) => [value.toLocaleLowerCase(), value])).values()]
		.sort((a, b) => b.length - a.length);
}

function highlightPattern(query: HighlightQuery): RegExp | null {
	const unique = highlightValues(query);
	return unique.length ? new RegExp(`(${unique.map(escapeRegex).join('|')})`, 'giu') : null;
}

/** Highlight relaxed matches while preserving the original spelling. Each folded character keeps
 * the UTF-16 span it came from, so `amsa` can wrap the original `áṁśa` rather than replacing it. */
function highlightRelaxedText(text: string, query: HighlightQuery): string {
	let folded = '';
	const starts: number[] = [];
	const ends: number[] = [];
	let offset = 0;
	for (const character of text) {
		const start = offset;
		offset += character.length;
		const part = unicodeSearchFold(character);
		if (!part) {
			// A decomposed combining mark belongs visually to the preceding base character.
			if (ends.length) ends[ends.length - 1] = offset;
			continue;
		}
		for (const foldedCharacter of part) {
			folded += foldedCharacter;
			starts.push(start);
			ends.push(offset);
		}
	}

	const ranges: Array<[number, number]> = [];
	for (const rawNeedle of highlightValues(query)) {
		const needle = unicodeSearchFold(rawNeedle);
		if (!needle) continue;
		let from = 0;
		for (;;) {
			const index = folded.indexOf(needle, from);
			if (index < 0) break;
			ranges.push([starts[index], ends[index + needle.length - 1]]);
			from = index + Math.max(1, needle.length);
		}
	}
	if (!ranges.length) return escapeText(text);
	ranges.sort((a, b) => a[0] - b[0] || b[1] - a[1]);
	const merged: Array<[number, number]> = [];
	for (const range of ranges) {
		const previous = merged.at(-1);
		if (previous && range[0] <= previous[1]) previous[1] = Math.max(previous[1], range[1]);
		else merged.push([...range]);
	}
	let output = '';
	let cursor = 0;
	for (const [start, end] of merged) {
		output += escapeText(text.slice(cursor, start));
		output += `<mark class="search-match">${escapeText(text.slice(start, end))}</mark>`;
		cursor = end;
	}
	return output + escapeText(text.slice(cursor));
}

/** Highlight a case-insensitive substring in visible HTML text without touching tags, attributes,
 * or entities. The query is escaped and only the original matched text is emitted, so a URL-driven
 * search term cannot inject markup. */
export function highlightHtml(html: string | null | undefined, query: HighlightQuery, relaxed = false): string {
	const content = html ?? '';
	if (relaxed)
		return content
			.split(/(<[^>]*>|&(?:#\d+|#x[\da-f]+|[a-z][\w]+);)/giu)
			.map((part) =>
				part.startsWith('<') || part.startsWith('&') ? part : highlightRelaxedText(part, query)
			)
			.join('');
	const match = highlightPattern(query);
	if (!match) return content;
	return content
		.split(/(<[^>]*>|&(?:#\d+|#x[\da-f]+|[a-z][\w]+);)/giu)
		.map((part) =>
			part.startsWith('<') || part.startsWith('&')
				? part
				: part.replace(match, (found) => `<mark class="search-match">${found}</mark>`)
		)
		.join('');
}

/** Escape plain text and highlight its visible matches. */
export function highlightText(text: string | null | undefined, query: HighlightQuery, relaxed = false): string {
	const content = text ?? '';
	if (relaxed) return highlightRelaxedText(content, query);
	const match = highlightPattern(query);
	if (!match) return escapeText(content);
	return content
		.split(match)
		.map((part, index) =>
			index % 2 ? `<mark class="search-match">${escapeText(part)}</mark>` : escapeText(part)
		)
		.join('');
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
