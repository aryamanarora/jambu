#!/usr/bin/env node
/** Run the actual browser query and feature code against a read-only compact database.
 * node scripts/check_sound_explorer.mjs [DB] [sound] [--study]
 * A single sound is deliberately the unit of this check; no full data rebuild is required.
 */
import assert from 'node:assert/strict';
import { build } from 'esbuild';
import { mkdtempSync, rmSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import Database from 'better-sqlite3';
import { readVarints } from '../src/lib/dbShared.ts';
import { unicodeSearchFold } from '../src/lib/unicodeSearch.ts';

const db = new Database(process.argv[2] ?? '.dbwork/jambu.db', { readonly: true });
db.function('unicode_fold', value => unicodeSearchFold(String(value ?? '')));
let sets = new Map();
db.function('vin_in', (blob, id) => readVarints(blob).some(v => sets.get(Number(id))?.has(v)) ? 1 : 0);
globalThis.__soundQuery = async (sql, params = [], supplied = []) => {
	sets = new Map(supplied.map(([id, members]) => [id, new Set(members)]));
	return db.prepare(sql).all(...params);
};
const dir = mkdtempSync(path.resolve('.dbwork/sound-check-'));
try {
	await build({ entryPoints: ['src/lib/query.ts'], outfile: path.join(dir, 'query.mjs'), bundle: true, platform: 'node', format: 'esm', plugins: [{ name: 'test-db', setup(b) {
		b.onResolve({ filter: /db\.svelte$/ }, () => ({ path: 'db', namespace: 'stub' }));
		b.onResolve({ filter: /^\$app\/paths$/ }, () => ({ path: 'paths', namespace: 'stub' }));
		b.onLoad({ filter: /.*/, namespace: 'stub' }, args => ({ contents: args.path === 'db'
			? 'export const query = (...args) => globalThis.__soundQuery(...args); export const queryOne = async (...args) => (await query(...args))[0] ?? null;'
			: 'export const base = "";', loader: 'js' }));
	} }] });
	const { getSoundObservations, getSoundSegments, getSoundAncestorIds, fetchLemmaList, getSoundLanguages } = await import(pathToFileURL(path.join(dir, 'query.mjs')));
	for (const language of (await getSoundLanguages('Indo-Aryan')).filter(l => ['H','P','Phal'].includes(l.id))) {
		const actual = db.prepare('SELECT count(*) AS n FROM lem WHERE lang_rid = (SELECT rowid FROM languages WHERE id = ?)').get(language.id).n;
		assert.equal(language.lemma_count, actual, `${language.name} total forms use the language lexicon count`);
	}
	const sound = process.argv[3] ?? 'k';
	const t = performance.now();
	const rows = await getSoundObservations('Indo-Aryan', sound);
	assert.ok(rows.length > 0);
	assert.equal(await getSoundObservations('Indo-Aryan', sound), rows, 'filter navigation reuses the selected cohort');
	assert.equal(new Set(rows.map(o => `${o.form.id}:${o.pos}`)).size, rows.length);
	const expected = (await getSoundSegments('Indo-Aryan')).find(s => s.seg === sound)?.total;
	if (expected != null) assert.equal(rows.length, expected, 'all occurrences reconcile with existing summaries');
	assert.ok(rows.some(o => o.form.ancestor.accentClass === 'barytone'));
	assert.ok(rows.some(o => o.form.ancestor.accentClass === 'oxytone'));
	assert.ok(rows.every(o => o.form.parentId && o.form.familyId));
	const notes = { sound, occurrences: rows.length, forms: new Set(rows.map(o => o.form.id)).size,
		families: new Set(rows.map(o => o.form.familyId)).size, seconds: Math.round((performance.now() - t) / 10) / 100,
		rssMB: Math.round(process.memoryUsage().rss / 1048576),
		sample: rows.filter(o => o.form.ancestor.count === 2 && o.form.ancestor.accentClass === 'barytone').slice(0, 3).map(o => ({ ancestor: o.form.parentWord, form: o.form.word, id: o.form.id })) };
	console.log(JSON.stringify(notes, null, 2));
  if (process.argv.includes('--study')) {
    const probes = [
      { word:'seed' }, { form:'amsa',relaxed:true }, { form:'áṁśa' },
      { gloss:'seed',source:'CDIAL' }, { gloss:'seed',tags:'Early-Vedic' },
      { form:'bhar',rootsOnly:true,relaxed:true }, { form:'agni',sectionsOnly:true,relaxed:true },
      { word:'fire',loanSourcesOnly:true }, { word:'fire',crossFamilyOnly:true },
      { etymology:'fire' }
    ];
    const checks=[];
    for (const params of probes) {
      const ancestorIds=await getSoundAncestorIds('Indo-Aryan',params);
      const listed=[];
      let count=0;
      for(let page=1;;page++) {
        const result=await fetchLemmaList({mode:'entries',params:{...params,origin_lang:'Indo-Aryan',page}});
        count=result.count; listed.push(...result.rows.map(r=>r.id));
        if(listed.length>=count) break;
        assert.ok(result.rows.length,'Entries pagination must advance');
        assert.ok(page<20,'Keep parity checks bounded');
      }
      assert.deepEqual(new Set(ancestorIds),new Set(listed),JSON.stringify(params));
      checks.push({params,count});
    }
    const options={languages:['H','P','Phal']};
    const sequence=await getSoundObservations('Indo-Aryan','kt',options);
    assert.ok(sequence.length);
    assert.ok(sequence.every(o=>o.sound==='kt' && o.positions.length===2 && options.languages.includes(o.form.language)));
    const target=await getSoundObservations('Indo-Aryan','V (k) V',options);
    const contextual=await getSoundObservations('Indo-Aryan','V k V',options);
    assert.ok(target.length);
    assert.equal(target.length,contextual.length,'target selection preserves the full-pattern cohort');
    assert.ok(target.every(o=>o.sound==='k' && o.positions.length===1 && o.contextStart<o.pos && o.contextEnd>o.endPos));
    assert.deepEqual(new Set(target.map(o=>o.form.id)),new Set(contextual.map(o=>o.form.id)));
    const byContext=new Map(contextual.map(o=>[`${o.form.id}:${o.pos}`,o]));
    assert.ok(target.some(o=>o.outcome!==byContext.get(`${o.form.id}:${o.contextStart}`).outcome),'outcomes exclude context sounds');
    const retroflex=await getSoundObservations('Indo-Aryan','[retroflex+stop]',options);
    assert.ok(retroflex.length);
    assert.ok(new Set(retroflex.map(o=>o.sound)).size>1);
    const search={word:'seed'};
    const ids=new Set(await getSoundAncestorIds('Indo-Aryan',search));
    const whole=await getSoundObservations('Indo-Aryan','*',{...options,entrySearch:search,filters:{syllables:'2'}});
    assert.ok(whole.length);
    assert.ok(whole.every(o=>ids.has(o.form.parentId) && o.form.ancestor.count===2));
    assert.equal(whole.length,new Set(whole.map(o=>o.form.id)).size,'whole-form selection counts once');
    assert.ok(whole.every(o=>o.pos===o.form.columns[0].pos && o.endPos===o.form.columns.at(-1).pos));
    assert.deepEqual(await getSoundObservations('Indo-Aryan','*',{...options,entrySearch:{word:'zzzz-no-such-entry'}}),[]);
    console.log(JSON.stringify({entriesParity:checks,sequenceForms:sequence.length,contextualTargetForms:target.length,retroflexForms:retroflex.length,seedWholeForms:whole.length},null,2));
  }
	if (process.env.SOUND_SAMPLE) console.log(JSON.stringify(rows.filter(o => [o.form.id, o.form.word, o.form.parentWord, o.form.language].some(s => s.normalize("NFC") === process.env.SOUND_SAMPLE.normalize("NFC"))).slice(0, 3), null, 2));
} finally { db.close(); rmSync(dir, { recursive: true, force: true }); delete globalThis.__soundQuery; }
