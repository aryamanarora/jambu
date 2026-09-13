#!/usr/bin/env node
/** Restore a packed release artifact for better-sqlite3 during prerendering. */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';
import { decompress } from '../src/lib/vendor/fzstd.js';

const input = process.argv[2] ?? 'static/db/jambu.db.zst';
const output = process.argv[3] ?? '.dbwork/jambu.db';
const packed = readFileSync(input);
const sqlite = decompress(packed);
const header = new TextDecoder().decode(sqlite.subarray(0, 16));
if (header !== 'SQLite format 3\0') throw new Error(`${input} did not unpack to a SQLite database`);
mkdirSync(dirname(output), { recursive: true });
writeFileSync(output, sqlite);
console.log(
	`Unpacked ${input} (${(packed.length / 1e6).toFixed(2)} MB) -> ${output} (${(sqlite.length / 1e6).toFixed(2)} MB)`
);
