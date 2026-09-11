import { base } from '$app/paths';
import { getDb, getEntryMeta, getLanguageRow, getReferenceRow } from './db';
import { md, referenceLabel, striptags } from '$lib/render';
import { publishedPosts } from '$lib/blog';
import { renderPost, type BlogRecord, type RecordKind } from '$lib/blog/render';
import shinaicCharts from '$lib/blog/data/shinaic-accent-charts.json';
import teluguCharts from '$lib/blog/data/telugu-metathesis-charts.json';

const content = import.meta.glob('/src/lib/blog/posts/*.md', { query: '?raw', import: 'default', eager: true }) as Record<string, string>;
const href = (route: string, id: string) => `${base}/${route}/${encodeURIComponent(id)}`;

// Reference descriptions are Markdown in the database but plain text in previews.
const referenceEntities: Record<string, string> = {
	amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", '#39': "'", nbsp: ' ',
	ndash: '–', mdash: '—', lsquo: '‘', rsquo: '’', ldquo: '“', rdquo: '”', hellip: '…'
};
const plainReference = (source: string) => striptags(md(source))
	.replace(/&([a-z]+|#39);/g, (match, entity: string) => referenceEntities[entity] ?? match)
	.replace(/\s+/g, ' ').trim();

export function resolveBlogRecord(kind: RecordKind, id: string): BlogRecord {
	if (kind === 'entry' || kind === 'form') {
		const row = getEntryMeta(id);
		if (row) return {
			kind, id: row.id, href: href('entries', row.id), label: striptags(row.word),
			description: [row.language?.name, striptags(row.gloss), row.native, row.phonemic && `/${row.phonemic}/`].filter(Boolean).join(' · '),
			context: [
				...(row.language ? [{ label: row.language.name, href: href('languages', row.language.id) }] : []),
				...(row.origin_lemma_id ? [{ label: `${row.relation || 'Origin'} → ${striptags(getEntryMeta(row.origin_lemma_id)?.word || row.origin_lemma_id)}`, href: href('entries', row.origin_lemma_id) }] : []),
				...(row.references ?? []).map((ref) => ({ label: `${referenceLabel(ref)}${ref.locator ? `, ${ref.locator}` : ''}`, href: href('references', ref.id) }))
			]
		};
	} else if (kind === 'concept') {
		const row = getDb().prepare('SELECT id, name, form_count, lang_count FROM concepts WHERE id = ?').get(id) as { id: number; name: string; form_count: number; lang_count: number } | undefined;
		if (row) return { kind, id: String(row.id), href: href('concepts', String(row.id)), label: row.name.toLowerCase(), description: `${row.form_count.toLocaleString('en')} forms · ${row.lang_count} languages` };
	} else if (kind === 'language') {
		const row = getLanguageRow(id);
		if (row) return { kind, id: row.id, href: href('languages', row.id), label: row.name, description: [row.clade, row.glottocode].filter(Boolean).join(' · ') };
	} else {
		const row = getReferenceRow(id);
		if (row) return { kind, id: row.id, href: href('references', row.id), label: referenceLabel(row), description: plainReference(row.source ?? '') };
	}
	throw new Error(`Unknown blog record ${kind}:${id}`);
}

export function getBlogPost(slug: string) {
	const post = publishedPosts().find((post) => post.slug === slug);
	if (!post) return null;
	const markdown = content[`/src/lib/blog/posts/${slug}.md`];
	if (!markdown) throw new Error(`Missing Markdown for blog post ${slug}`);
	const charts = slug === 'shinaic-accent' ? shinaicCharts : slug === 'telugu-metathesis' ? teluguCharts : {};
	return { post, ...renderPost(markdown, resolveBlogRecord, { basePath: base, charts }) };
}
