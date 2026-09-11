import { Marked, Renderer } from 'marked';
import type { BlogChart } from './charts';

function validateChart(chart: BlogChart) {
	if (!/^[a-z0-9-]+$/.test(chart.id) || !chart.views.length) throw new Error('Invalid blog chart');
	for (const view of chart.views) {
		if (!view.categories.length || !view.rows.length) throw new Error(`Empty chart ${chart.id}`);
		for (const row of view.rows) {
			if (row.values.length !== view.categories.length || row.values.some((n) => !Number.isSafeInteger(n) || n < 0)) {
				throw new Error(`Invalid counts in chart ${chart.id}`);
			}
		}
	}
}

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
export function renderPost(markdown: string, resolve: (kind: RecordKind, id: string) => BlogRecord, options: { basePath?: string; charts?: Record<string, BlogChart> } = {}) {
	const records = new Map<string, BlogRecord>();
	const chartSlots: BlogChart[] = [];
	const parser = new Marked({
		renderer: {
			table(token) {
				return `<p class="table-hint">Scroll sideways to read the full table.</p><div class="blog-table" role="region" aria-label="Scrollable evidence table" tabindex="0">${Renderer.prototype.table.call(this, token)}</div>`;
			},
			code(token) {
				if (token.lang !== 'chart') return false;
				const id = token.text.trim();
				const chart = options.charts?.[id];
				if (!chart) throw new Error(`Unknown blog chart ${id}`);
				validateChart(chart);
				chartSlots.push(chart);
				return `<!--blog-chart-slot:${chartSlots.length - 1}-->`;
			},
			link(token) {
				const match = /^(entry|form|concept|language|ref):(.+)$/.exec(token.href);
				if (!match) {
					if (/^(?:javascript|data|vbscript):/i.test(token.href)) throw new Error('Unsafe blog link');
					if (/^\/(?!\/)/.test(token.href)) token.href = (options.basePath || '') + token.href;
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
	const blocks: ({ kind: 'html'; html: string } | { kind: 'chart'; chart: BlogChart })[] = [];
	let start = 0;
	for (const match of html.matchAll(/<!--blog-chart-slot:(\d+)-->/g)) {
		blocks.push({ kind: 'html', html: html.slice(start, match.index) });
		const chart = chartSlots[Number(match[1])];
		if (!chart) throw new Error('Invalid blog chart slot');
		blocks.push({ kind: 'chart', chart });
		start = match.index + match[0].length;
	}
	blocks.push({ kind: 'html', html: html.slice(start) });
	return { html, blocks, records: [...records.values()] };
}
