import assert from 'node:assert/strict';
import test from 'node:test';
import { alignmentGrid } from '../src/lib/alignmentGrid.ts';
import { countListFilters, resultRange } from '../src/lib/listFilters.ts';
import { referenceProgress, unetymologisedPercent } from '../src/lib/referenceStatus.ts';

test('alignment preserves sparse ancestor columns and insertion order without changing input', () => {
	const segments = [-1, 2, -1, 9, 8, -1].map((etymonIdx, i) => Object.freeze({ etymonIdx, reflexSeg: String(i) }));
	Object.freeze(segments);
	const { cells, lead } = alignmentGrid(segments, [2, 5, 8]);
	assert.deepEqual(lead, [segments[0]]);
	assert.deepEqual(cells, [
		{ main: segments[1], post: [segments[2], segments[3]] },
		{ main: null, post: [] },
		{ main: segments[4], post: [segments[5]] }
	]);
});

test('alignment supports dense entry columns, losses and empty ancestors', () => {
	const loss = { etymonIdx: 0, reflexSeg: '', change: 'loss' };
	assert.deepEqual(alignmentGrid([loss], [0]), { cells: [{ main: loss, post: [] }], lead: [] });
	assert.deepEqual(alignmentGrid([loss], []), { cells: [], lead: [loss] });
});

test('filter counts follow the controls available in each list mode', () => {
	const params = { form: 'a', source: 'CDIAL', origin_lang: 'hin', rootsOnly: true, dialect: 'x', notes: 'note' };
	assert.equal(countListFilters(params, 'entries'), 4);
	assert.equal(countListFilters(params, 'entries', false), 3);
	assert.equal(countListFilters(params, 'forms'), 5);
	assert.equal(countListFilters({}, 'forms'), 0);
});

test('result labels handle empty results and partial final pages', () => {
	assert.equal(resultRange(0, 1, 0, 50, 'forms'), '0–0 of 0 forms');
	assert.equal(resultRange(53, 2, 3, 50, 'entries'), '51–53 of 53 entries');
});

test('source progress and percentages share unknown and empty states', () => {
	assert.deepEqual(['Yes', 'Partial', 'No', null].map(referenceProgress), ['ok', 'warn', 'bad', 'bad']);
	assert.equal(unetymologisedPercent(0, 0), '—');
	assert.equal(unetymologisedPercent(3, 1), '33.3%');
});
