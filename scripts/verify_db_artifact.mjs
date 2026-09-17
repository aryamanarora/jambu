import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import { decompress } from '../src/lib/vendor/fzstd.js';
const manifest = JSON.parse(readFileSync(new URL('./db-release.json', import.meta.url), 'utf8'));
const meta = readFileSync('src/lib/dbMeta.ts', 'utf8');
assert.equal(meta.match(/DB_VERSION = '([^']+)'/)[1], manifest.version);
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
for (const [path, expected] of Object.entries(manifest.assets)) {
  const bytes = readFileSync(path);
  assert.equal(bytes.length, expected.bytes, `${path} size`);
  assert.equal(hash(bytes), expected.sha256, `${path} digest`);
}
const packed = readFileSync('static/db/jambu.db.zst');
assert.ok(packed.length < 60_000_000, 'packed database exceeds deployment cap');
assert.equal(hash(decompress(packed)), manifest.assets['.dbwork/jambu.db'].sha256, 'browser decoder roundtrip');
for (const [name, path] of [['DB_DOWNLOAD_BYTES', 'static/db/jambu.db.zst'], ['DB_LOCAL_BYTES', '.dbwork/jambu.db']]) {
  assert.equal(Number(meta.match(new RegExp(name + ' = ([0-9_]+)'))[1].replaceAll('_', '')), manifest.assets[path].bytes);
}
console.log(`Verified database v${manifest.version}: asset sizes, SHA-256, and browser decoding.`);
