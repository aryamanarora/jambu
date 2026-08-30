import assert from 'node:assert/strict';
import test from 'node:test';

import {
	ETYMOLOGY_GUESS_THRESHOLD,
	bestEtymologyGuess,
	soundSimilarity
} from '../src/lib/etymologyGuess.ts';

test('sound similarity uses the Etymology Lab normalization', () => {
	assert.equal(soundSimilarity('*kā́r-', 'kar'), 1);
	assert.equal(soundSimilarity('', 'kar'), 0);
});

test('best guess prefers a same-language reflex and returns its evidence', () => {
	const guess = bestEtymologyGuess(
		{ word: 'kala', language_id: 'A' },
		[
			{
				value: 'cross-language',
				headword: 'zzzz',
				reflexes: [{ word: 'kala', language_id: 'B' }]
			},
			{
				value: 'same-language',
				headword: 'zzzz',
				reflexes: [{ word: 'kala', language_id: 'A' }]
			}
		]
	);

	assert.equal(guess?.value, 'same-language');
	assert.equal(guess?.matchedWord, 'kala');
	assert.equal(guess?.similarity, 1);
});

test('best guess rejects candidates below the shared support threshold', () => {
	const guess = bestEtymologyGuess(
		{ word: 'abc', language_id: 'A' },
		[{ value: 'unrelated', headword: 'xyz', reflexes: [] }],
		ETYMOLOGY_GUESS_THRESHOLD
	);

	assert.equal(guess, null);
});
