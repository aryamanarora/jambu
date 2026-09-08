import assert from 'node:assert/strict';
import test from 'node:test';
import { renderPost } from '../src/lib/blog/render.ts';

const resolve = (kind, id) => ({ kind, id, href: `/jambu/entries/${encodeURIComponent(id)}`, label: 'pānī <water>', description: 'Hindi "water"' });

test('semantic links resolve labels, escape metadata, support custom text and deduplicate records', () => {
	const result = renderPost('[](form:f_1) and [**the form**](form:f_1)', resolve);
	assert.equal(result.records.length, 1);
	assert.match(result.html, /pānī &lt;water&gt;/);
	assert.match(result.html, /<strong>the form<\/strong>/);
	assert.match(result.html, /data-eref="f_1"/);
	assert.match(result.html, /href="\/jambu\/entries\/f_1"/);
	assert.match(result.html, /Hindi &quot;water&quot;/);
});

test('code examples remain literal and ordinary Markdown links are preserved', () => {
	const result = renderPost('`[](entry:missing)`\n\n[Website](https://example.org)', () => { throw new Error('Must not resolve code'); });
	assert.equal(result.records.length, 0);
	assert.match(result.html, /<code>\[\]\(entry:missing\)<\/code>/);
	assert.match(result.html, /href="https:\/\/example.org"/);
});

test('missing records fail rather than publishing broken evidence links', () => {
	assert.throws(() => renderPost('[](ref:missing)', () => { throw new Error('Unknown blog record ref:missing'); }), /Unknown blog record/);
});

test('all record types resolve and non-entry links omit entry preview attributes', () => {
	for (const kind of ['entry', 'form', 'concept', 'language', 'ref']) {
		const { html, records } = renderPost(`[](${kind}:a%20b)`, resolve);
		assert.equal(records[0].id, 'a b');
		assert.match(html, new RegExp(`blog-link-${kind}`));
		assert.equal(html.includes('data-eref'), kind === 'entry' || kind === 'form');
	}
});
