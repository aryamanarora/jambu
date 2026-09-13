import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
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

test('charts interrupt prose without splitting tables or losing linked records', () => {
	const chart = { id: 'accent', title: 'Accent', sources: ['counts.tsv'], views: [{ label: 'All', unit: 'families', note: 'Unknown included', categories: ['E', 'L'], rows: [{ label: 'Nouns', values: [7, 10] }] }] };
	const result = renderPost('[](entry:1)\n\n```chart\naccent\n```\n\n| Word | Outcome |\n| --- | --- |\n| [](entry:2) | E |', resolve, { charts: { accent: chart } });
	assert.deepEqual(result.blocks.map((b) => b.kind), ['html', 'chart', 'html']);
	assert.equal(result.blocks[1].chart, chart);
	assert.match(result.blocks[2].html, /<table>/);
	assert.equal(result.records.length, 2);
	assert.throws(() => renderPost('```chart\nmissing\n```', resolve), /Unknown blog chart/);
	assert.throws(() => renderPost('```chart\naccent\n```', resolve, { charts: { accent: { ...chart, views: [{ ...chart.views[0], rows: [{ label: 'Bad', values: [7] }] }] } } }), /Invalid counts/);
});

test('research downloads respect deployment base paths while external and fragment links remain intact', () => {
	const { html } = renderPost('[Data](/research/file.tsv) [Section](#one) [External](https://example.org)', resolve, { basePath: '/jambu' });
	assert.match(html, /href="\/jambu\/research\/file.tsv"/);
	assert.match(html, /href="#one"/);
	assert.match(html, /href="https:\/\/example.org"/);
});

test('research figures respect project deployment base paths', () => {
	const { html } = renderPost('![Chart](/research/dardic-plains/coverage.svg)', resolve, { basePath: '/jambu' });
	assert.match(html, /src="\/jambu\/research\/dardic-plains\/coverage.svg"/);
});

test('weighted votes require explicit opt-in and reject nonfinite or negative values', () => {
	const make = (fractionalVotes, values) => ({ id: 'votes', title: 'Votes', sources: [], views: [{ label: 'Scope', unit: 'votes', note: '', categories: ['A', 'B'], rows: [{ label: 'Group', values }], fractionalVotes }] });
	const render = (chart) => renderPost('```chart\nvotes\n```', resolve, { charts: { votes: chart } });
	assert.equal(render(make(true, [1.5, 2.5])).blocks[1].kind, 'chart');
	assert.throws(() => render(make(false, [1.5, 2.5])), /Invalid counts/);
	assert.throws(() => render(make(true, [NaN, 2])), /Invalid counts/);
	assert.throws(() => render(make(true, [Infinity, 2])), /Invalid counts/);
	assert.throws(() => render(make(true, [-1, 2])), /Invalid counts/);
});

test('geographic charts validate points and reconcile the other-family breakdown', () => {
	const charts = JSON.parse(readFileSync(new URL('../src/lib/blog/data/dardic-plains-charts.json', import.meta.url), 'utf8'));
	for (const [id] of Object.entries(charts)) {
		assert.equal(renderPost('```chart\n' + id + '\n```', resolve, { charts }).blocks[1].kind, 'chart');
	}
	const id = 'dardic-family-shares';
	const badLocation = structuredClone(charts);
	badLocation[id].views[0].map.points[0].latitude = 91;
	assert.throws(() => renderPost('```chart\n' + id + '\n```', resolve, { charts: badLocation }), /Invalid map point/);
	const badBreakdown = structuredClone(charts);
	badBreakdown[id].views[0].otherFamilies[0].values[0] += 1;
	assert.throws(() => renderPost('```chart\n' + id + '\n```', resolve, { charts: badBreakdown }), /Invalid other-family breakdown/);
});
