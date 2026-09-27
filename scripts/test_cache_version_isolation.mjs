import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
const coordination = readFileSync(new URL('../src/lib/db.svelte.ts', import.meta.url), 'utf8');
const storage = readFileSync(new URL('../src/lib/sqliteCore.ts', import.meta.url), 'utf8');
const meta = readFileSync(new URL('../src/lib/dbMeta.ts', import.meta.url), 'utf8');
function identities(version) {
	return Object.fromEntries([
		['LOCK', coordination], ['CHANNEL', coordination],
		['POOL_NAME', storage], ['POOL_DIRECTORY', storage], ['OPFS_DB_PATH', meta]
	].map(([name, source]) => {
		const expression = source.match(new RegExp(`(?:export )?const ${name} = (\\x60[^\\x60]+\\x60);`));
		assert.ok(expression, `${name} has an explicit version-based identity`);
		return [name, new Function('DB_VERSION', `return ${expression[1]}`)(version)];
	}));
}
test('same releases coordinate, distinct releases isolate messaging and storage', () => {
	const old = identities('38'), current = identities('39');
	assert.deepEqual(current, identities('39'));
	for (const name of Object.keys(current)) assert.notEqual(current[name], old[name], name);
	assert.match(coordination, /new BroadcastChannel\(CHANNEL\)/);
	assert.match(coordination, /\.request\(LOCK,/);
	assert.match(storage, /installOpfsSAHPoolVfs\(\{ name: POOL_NAME, directory: POOL_DIRECTORY,/);
	assert.doesNotMatch(storage, /removeEntry|removeVfs/); // Do not delete another version's pool.
});
