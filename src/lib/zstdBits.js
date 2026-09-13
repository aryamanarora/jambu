/**
 * Read an unaligned Zstandard offset field. A 26-bit field starting at bit 7
 * crosses five bytes; JavaScript's 32-bit shifts would discard its top bit.
 * @param {Uint8Array} data
 * @param {number} byte
 * @param {number} shift
 * @param {number} width
 */
export function readOffsetBits(data, byte, shift, width) {
	const value = (data[byte] || 0) + (data[byte + 1] || 0) * 256
		+ (data[byte + 2] || 0) * 65536 + (data[byte + 3] || 0) * 16777216
		+ (data[byte + 4] || 0) * 4294967296;
	return Math.floor(value / 2 ** shift) & (2 ** width - 1);
}
