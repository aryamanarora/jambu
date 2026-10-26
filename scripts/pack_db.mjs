#!/usr/bin/env node
/** Pack and verify the exact artifact that the browser's decoder will restore. */
import { mkdirSync, readFileSync, renameSync, rmSync, statSync } from 'node:fs';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { decompress } from '../src/lib/vendor/fzstd.js';

const input = process.argv[2] ?? '.dbwork/jambu.db';
const output = process.argv[3] ?? 'static/db/jambu.db.zst';
const temporary = `${output}.tmp`;
// Local release preparation can use a smaller compression window; CI can retain
// the strongest settings when they are needed to meet the download budget.
const level = Number(process.env.ZSTD_LEVEL ?? 22);
const windowLog = Number(process.env.ZSTD_WINDOW_LOG ?? 27);
const threads = Number(process.env.ZSTD_THREADS ?? 1);
if (!Number.isInteger(level) || level < 1 || level > 22 ||
	!Number.isInteger(windowLog) || windowLog < 10 || windowLog > 27 ||
	!Number.isInteger(threads) || threads < 1) {
	throw new Error('Invalid Zstandard level, window log, or thread count');
}
// Download budget for browser users, not a platform limit (Pages serves files to 100 MB).
// Raised to 65 MB for db-v39 (60.77 MB at level 22) and to 70 MB for db-v40, which adds the
// Iranian family and the whole-book source expansions (181 MB expanded).
const limit = 70_000_000;
mkdirSync(dirname(output), { recursive: true });

try {
	// Use the corrected wide-offset decoder; stronger compression keeps the corpus
	// under the artifact limit. A round trip catches unsupported sequences early.
	const result = spawnSync('zstd', [
		'--ultra', `-${level}`, `--long=${windowLog}`, `--threads=${threads}`, '--force', input, '-o', temporary
	], { stdio: 'inherit' });
	if (result.error?.code === 'ENOENT') {
		throw new Error('zstd is required to stage the database (install it with Homebrew or apt)');
	}
	if (result.error) throw result.error;
	if (result.status !== 0) throw new Error(`zstd exited with status ${result.status}`);
	const sourceBytes = statSync(input).size;
	const packedBytes = statSync(temporary).size;
	if (packedBytes >= limit) {
		throw new Error(`packed database is ${(packedBytes / 1e6).toFixed(2)} MB; target is below ${limit / 1e6} MB`);
	}
	const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
	const restored = decompress(new Uint8Array(readFileSync(temporary)));
	if (restored.length !== sourceBytes || sha256(restored) !== sha256(readFileSync(input))) {
		throw new Error('browser Zstandard decoder did not restore the identical SQLite image');
	}
	renameSync(temporary, output);
	// Retire the pre-v30 path only after the replacement artifact has passed checks.
	if (output === 'static/db/jambu.db.zst') rmSync('static/db/jambu.db', { force: true });
	console.log(`Packed ${input} (${(sourceBytes / 1e6).toFixed(2)} MB) -> ${output} (${(packedBytes / 1e6).toFixed(2)} MB); browser round trip verified`);
} finally {
	rmSync(temporary, { force: true });
}
