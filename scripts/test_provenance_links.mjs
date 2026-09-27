import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { provenanceUrl } from '../src/lib/provenance.ts';

const prefix = 'https://github.com/moli-mandala/data/blob/main/';
test('historical filename annotations stay labels, not repository paths', () => {
	for (const file of ['20260925-cfel-koda-adornments.csv', '20260925-cfel-koda-print-pilot.csv', '20260925-roy-birhor-p567-p568.csv']) {
		const path = `data/other/forms/${file}`;
		assert.equal(provenanceUrl(`${path} (historical filename retained)`), prefix + path);
	}
	const page = readFileSync(new URL('../src/routes/references/[ref]/+page.svelte', import.meta.url), 'utf8');
	assert.match(page, /href=\{url\}[^>]*>\{file\}<\/a>/); // Original full label retained.
});
test('ordinary paths work; URLs and prose remain ordinary provenance text', () => {
	assert.equal(provenanceUrl('data/other/forms/raw_data/ho_mla_2004/audit.jsonl'), prefix + 'data/other/forms/raw_data/ho_mla_2004/audit.jsonl');
	assert.equal(provenanceUrl('https://example.org/source.pdf'), null);
	assert.equal(provenanceUrl('Printed original retained locally'), null);
	assert.equal(provenanceUrl('data/../private.txt'), null);
});
