import test from 'node:test';
import assert from 'node:assert/strict';
import { readOffsetBits } from '../src/lib/zstdBits.js';

test('wide Zstandard offsets retain the bit beyond a 32-bit read', () => {
	assert.equal(readOffsetBits(Uint8Array.of(0, 0, 0, 0, 1), 0, 7, 26), 2 ** 25);
	assert.equal(readOffsetBits(Uint8Array.of(255, 255, 255, 255, 255), 0, 7, 26), 2 ** 26 - 1);
});

test('offset fields agree with an exact integer oracle at every bit alignment', () => {
	const bytes = Uint8Array.of(93, 228, 17, 239, 165);
	const integer = bytes.reduce((n, b, i) => n | BigInt(b) << BigInt(i * 8), 0n);
	for (let shift = 0; shift < 8; shift++) {
		for (let width = 1; width <= 30; width++) {
			const expected = Number((integer >> BigInt(shift)) & ((1n << BigInt(width)) - 1n));
			assert.equal(readOffsetBits(bytes, 0, shift, width), expected);
		}
	}
});
