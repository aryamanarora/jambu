import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import Database from 'better-sqlite3';

const querySource = readFileSync(new URL('../src/lib/query.ts', import.meta.url), 'utf8');
const entrySource = readFileSync(new URL('../src/routes/entries/[entry]/+page.svelte', import.meta.url), 'utf8');

// Execute the production query body against a small database, without importing the browser
// worker or reading a compiled release. Projection/hydration is covered by compact parity.
function derivativeQuery() {
	const block = querySource.split('const derivativeRows = await query<')[1];
	assert.ok(block, 'production derivative query must exist');
	const sql = block.match(/`([\s\S]*?)`/)[1];
	return sql.replaceAll('${LEM_COLS}', 'l.rowid AS rid, l.word')
		.replaceAll('${LEM_JOINS}', '')
		.replaceAll('${KIND_COMPONENT}', '5').replaceAll('${KIND_DERIVED}', '6');
}

test('a repeated component displays one child while all graph positions survive', () => {
	const db = new Database(':memory:');
	try {
		db.exec(`CREATE TABLE lem(word TEXT, lang_rid INTEGER, origin_rid INTEGER, ord INTEGER);
			CREATE TABLE edges(child_rid INTEGER, parent_rid INTEGER, kind INTEGER, rank INTEGER, pos INTEGER);
			INSERT INTO lem VALUES ('parent',1,NULL,1), ('repeated compound',2,NULL,2),
			 ('same-language',1,NULL,3), ('accepted reflex',2,1,4), ('other parent',1,NULL,5),
			 ('different derivative',3,NULL,6);
			INSERT INTO edges VALUES (2,1,5,1,1), (2,1,5,1,2), (2,1,6,1,NULL),
			 (3,1,6,1,NULL), (4,1,5,1,1), (6,5,6,1,NULL), (6,1,6,2,NULL);`);
		assert.deepEqual(db.prepare(derivativeQuery()).all(1), [
			{ rid: 2, word: 'repeated compound', derivation: 5 }
		]);
		assert.deepEqual(db.prepare('SELECT kind,pos FROM edges WHERE child_rid=2 ORDER BY rowid').all(), [
			{ kind: 5, pos: 1 }, { kind: 5, pos: 2 }, { kind: 6, pos: null }
		]);
	} finally {
		db.close();
	}
});

test('the displayed language count includes derivative-only search results', () => {
	const expression = entrySource.match(/const langCount = \$derived\(([^\n]+)\);/);
	assert.ok(expression, 'production language count must exist');
	// Evaluate that exact pure reactive expression with its two input lists. This catches
	// accidentally reverting to filteredReflexes while avoiding a synthetic Svelte harness.
	const count = new Function('shownForms', 'filteredReflexes', `return (${expression[1]});`);
	const form = (language_id) => ({ lemma: { language_id } });
	assert.equal(count([form('Pothwari'), form('Pothwari')], []), 1);
	assert.equal(count([form('Hindi'), form('Pothwari'), form('Punjabi')], [form('Hindi')]), 3);
	assert.equal(count([], []), 0);
});


test('same-language repeated components have one neighbour and one count on both paths', () => {
 const serverSource = readFileSync(new URL('../src/lib/server/db.ts', import.meta.url), 'utf8');
 const db = new Database(':memory:');
 try {
  db.exec(`CREATE TABLE lem(word TEXT, gloss TEXT, counts INTEGER, lang_rid INTEGER, origin_rid INTEGER, ord INTEGER);
   CREATE TABLE edges(child_rid INTEGER, parent_rid INTEGER, kind INTEGER, rank INTEGER, pos INTEGER);
   INSERT INTO lem VALUES ('parent','root',NULL,1,NULL,1), ('same','child',NULL,1,NULL,2), ('foreign','child',NULL,2,NULL,3);
   INSERT INTO edges VALUES (2,1,5,1,1), (2,1,5,1,2), (2,1,6,1,NULL), (3,1,5,1,1);`);
  const expand = (sql) => sql.replaceAll('${KIND_COMPONENT}', '5').replaceAll('${KIND_DERIVED}', '6');
  for (const source of [querySource, serverSource]) {
   const query = source.match(/`(SELECT DISTINCT l\.rowid AS rid, l\.word, l\.gloss, l\.counts[\s\S]*?ORDER BY l\.ord)`/);
   assert.ok(query, 'production same-language neighbour query must exist');
   assert.deepEqual(db.prepare(expand(query[1])).all(1), [{rid:2,word:'same',gloss:'child',counts:null}]);
  }
  const countQuery = querySource.match(/`(SELECT d\.parent_rid AS p, COUNT\(DISTINCT d\.child_rid\) AS c FROM edges d[\s\S]*?GROUP BY d\.parent_rid)`/);
  assert.ok(countQuery, 'production distinct-child count must exist');
  assert.deepEqual(db.prepare(expand(countQuery[1]).replaceAll('${IN_JSON}', '(SELECT value FROM json_each(?))')).all('[1]'), [{p:1,c:1}]);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM edges').get().n, 4);
 } finally { db.close(); }
});
