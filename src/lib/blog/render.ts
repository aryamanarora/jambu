import { Marked } from 'marked';

export type RecordKind = 'entry' | 'form' | 'concept' | 'language' | 'ref';
export type BlogRecord = {
	kind: RecordKind;
	id: string;
	href: string;
	label: string;
	description: string;
	context?: { label: string; href: string }[];
};

export const escapeHtml = (value: string) => value.replaceAll('&', '&amp;')
	.replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');

/** Curated Markdown only; raw HTML is allowed, just as in dictionary editorial prose. */
export function renderPost(markdown: string, resolve: (kind: RecordKind, id: string) => BlogRecord) {
	const records = new Map<string, BlogRecord>();
	const parser = new Marked({
		renderer: {
			link(token) {
				const match = /^(entry|form|concept|language|ref):(.+)$/.exec(token.href);
				if (!match) {
					if (/^(?:javascript|data|vbscript):/i.test(token.href)) throw new Error('Unsafe blog link');
					return false;
				}
				const kind = match[1] as RecordKind;
				const record = resolve(kind, decodeURIComponent(match[2]));
				records.set(`${record.kind}:${record.id}`, record);
				const entry = kind === 'entry' || kind === 'form';
				const label = token.tokens.length ? this.parser.parseInline(token.tokens) : escapeHtml(record.label);
				return `<a class="blog-record-link blog-link-${kind}${entry ? ' eref' : ''}" href="${escapeHtml(record.href)}" title="${escapeHtml(record.description || record.label)}"${entry ? ` data-eref="${escapeHtml(record.id)}"` : ''}>${label}</a>`;
			}
		}
	});
	const html = parser.parse(markdown, { async: false });
	return { html, records: [...records.values()] };
}
