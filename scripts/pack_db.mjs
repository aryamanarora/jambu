#!/usr/bin/env node
/** Pack the browser SQLite image as a Zstandard release/deploy artifact. */
import { mkdirSync, rmSync, statSync } from 'node:fs';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';

const input = process.argv[2] ?? '.dbwork/jambu.db';
const output = process.argv[3] ?? 'static/db/jambu.db.zst';
const limit = 50_000_000;

mkdirSync(dirname(output), { recursive: true });
// Retire the pre-v30 staged path so a local build cannot silently deploy both copies.
if (output === 'static/db/jambu.db.zst') rmSync('static/db/jambu.db', { force: true });
const result = spawnSync('zstd', ['-19', '--threads=0', '--force', input, '-o', output], {
	stdio: 'inherit'
});
if (result.error?.code === 'ENOENT') {
	throw new Error('zstd is required to stage the database (install it with Homebrew or apt)');
}
if (result.status !== 0) process.exit(result.status ?? 1);

const sourceBytes = statSync(input).size;
const packedBytes = statSync(output).size;
if (packedBytes >= limit) {
	throw new Error(
		`packed database is ${(packedBytes / 1e6).toFixed(2)} MB; target is below ${limit / 1e6} MB`
	);
}
console.log(
	`Packed ${input} (${(sourceBytes / 1e6).toFixed(2)} MB) -> ${output} (${(packedBytes / 1e6).toFixed(2)} MB)`
);
