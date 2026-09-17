import assert from 'node:assert/strict';
import test from 'node:test';
import { build } from 'esbuild';
import { analyzeProsody, segmentKey, segmentFeatures, segmentChanges, alignmentEvents, matchesSound, isDetachedNotation } from '../src/lib/phonology.ts';

const bundle = await build({ entryPoints: [new URL('../src/lib/soundExplorer.ts', import.meta.url).pathname], bundle: true, write: false, platform: 'node', format: 'esm' });
const { DEFAULT_SOUND_FILTERS: D, readSoundFilters, soundSearch, matchesObservation, summarizeSounds, clusterAt } = await import('data:text/javascript;base64,' + Buffer.from(bundle.outputFiles[0].text).toString('base64'));
const studyBundle = await build({ entryPoints: [new URL('../src/lib/soundStudy.ts', import.meta.url).pathname], bundle: true, write: false, platform: 'node', format: 'esm' });
const { DEFAULT_STUDY: S, INPUT_FACETS, inputCategory, readStudy, studySearch, queryKey, loadKey, groupStudy, inputColumns, buildMatrix, languageOutcomeCounts, matchesLanguageCounts, languageCountError } = await import('data:text/javascript;base64,' + Buffer.from(studyBundle.outputFiles[0].text).toString('base64'));
const patternBundle = await build({ entryPoints: [new URL('../src/lib/soundPattern.ts', import.meta.url).pathname], bundle: true, write: false, platform: 'node', format: 'esm' });
const { parseSoundPattern, matchPattern, formatSoundPattern, insertPatternClass, targetSelectedText } = await import('data:text/javascript;base64,' + Buffer.from(patternBundle.outputFiles[0].text).toString('base64'));
const old = tokens => analyzeProsody(tokens, { old: true });

test('accent position, syllable count, quantity and weight remain separate', () => {
	const a = old(['á', 'ṅ', 'g', 'ā', 'r', 'a']);
	assert.equal(a.count, 3); assert.equal(a.accentClass, 'barytone');
	assert.equal(a.accentFromRight, 3); assert.equal(a.quantityPattern, 'SLS');
	assert.equal(a.weightPattern, 'HHL'); assert.deepEqual(a.segmentSyllables, [0, 0, 1, 1, 2, 2]);
	assert.equal(old(['b', 'ā', 'l', 'á']).accentClass, 'oxytone');
	assert.equal(old(['b', 'ā', 'l', 'a']).accentClass, 'unknown');
	assert.equal(old(['a', 'ś', 'a']).accentClass, 'unknown'); // ś decomposes to s + acute
	assert.equal(old(['á', 'ṁ', 'ś', 'a']).count, 2);
	assert.equal(old(['á', 'ṁ', 'ś', 'a']).syllables[0].weight, 'heavy');
	assert.equal(analyzeProsody(['aː', 't', 'a']).syllables[0].closed, false);
	assert.equal(analyzeProsody(['a', 'tː', 'a']).syllables[0].closed, true);
});

test('syllabic liquids, diphthongs, and legacy detached marks keep their positions', () => {
	assert.equal(old(['v', 'r', '̩́', 'k', 'a']).count, 2);
	assert.equal(old(['v', 'r', '̩́', 'k', 'a']).accentPosition, 1);
	assert.equal(old(['ai']).count, 1); assert.equal(old(['au']).quantityPattern, 'L');
	assert.equal(segmentFeatures('r̩').kind, 'V');
	assert.equal(segmentFeatures('a̯').kind, '?');
	assert.equal(segmentKey('ś'), 'ś'); assert.equal(segmentKey('ā̃́'), 'ā̃');
	assert.deepEqual(segmentChanges('á', 'a'), ['kept']);
	assert.deepEqual(segmentChanges('dʰ', 't'), ['devoicing', 'deaspiration']);
	assert.equal(isDetachedNotation('̩́'), true); assert.equal(isDetachedNotation('ŕ̩'), false);
});

test('uncertainty is never converted into a negative accent observation', () => {
	assert.equal(old(['m', 'a', 'n', 'u', 'ṣ', 'y', 'à']).accentClass, 'svarita');
	assert.equal(old(['á', 'k', 'á']).accentClass, 'multiple');
	const sequence = analyzeProsody(['a', 'i']);
	assert.equal(sequence.count, null); assert.ok(sequence.issues.includes('vowel-sequence-needs-reading'));
	assert.equal(analyzeProsody(['á', 't', 'a'], { word: 'áta / ata', old: true }).count, null);
	assert.equal(analyzeProsody(['k', 'ʲ', 'ī']).accentClass, 'unknown');
});

test('mora readings follow normalized source conventions', () => {
	assert.equal(analyzeProsody(['ā', '̂'], { sources: ['liljegren'] }).accentType, 'mora-1');
	assert.equal(analyzeProsody(['ā̌'], { sources: ['liljegren'] }).accentType, 'mora-2');
	assert.equal(analyzeProsody(['ā̀'], { sources: ['degener-shina2008'] }).accentType, 'mora-1');
	assert.equal(analyzeProsody(['ā́'], { sources: ['degener-shina2008'] }).accentType, 'mora-2');
	assert.equal(analyzeProsody(['ā́'], { sources: ['CDIAL'] }).accentType, 'acute');
	assert.equal(analyzeProsody(['ā́'], { sources: ['CDIAL', 'degener-shina2008'] }).accentType, 'acute');
});

function obs(id, outcome, family = 'root', lang = 'H', pos = 0) {
	return { pos, index: 0, sound: 'a', outcome, prev: '#', next: 'k', changes: ['vowel'], syllable: 0, cluster: 'vowel', form: {
		id, familyId: family, language: lang, languageName: lang, clade: 'Central', parentId: 'old', parentWord: 'áka', word: 'ak', gloss: 'test', relation: 'inherited', tags: [], parentTags: [], sources: [],
		ancestor: old(['á', 'k', 'a']), modern: analyzeProsody(['a', 'k'])
	} };
}
test('independent counting splits conflicting units without double-counting citations or positions', () => {
	const rows = [obs('f1', 'a'), obs('f1', 'a', 'root', 'H', 2), obs('f2', 'e'), obs('f3', 'a', 'root', 'P')];
	assert.equal(summarizeSounds(rows, 'occurrences').total, 4);
	assert.equal(summarizeSounds(rows, 'forms').total, 3);
	const s = summarizeSounds(rows, 'families');
	assert.equal(s.total, 2); assert.equal(s.families, 1);
	assert.equal(s.outcomes.find(o => o.sound === 'a').percent, 75);
	assert.equal(s.outcomes.reduce((n, o) => n + o.percent, 0), 100);
});

test('composed filters, unknown counts, natural classes and URL round-trip', () => {
	const o = obs('f1', 'a');
	const f = { ...D, accent: 'barytone', syllables: '2', relative: '0', position: '1', quantity: 'short', weight: 'light', closed: 'open', nx: ':C', delta: 'loss', source: '' };
	assert.equal(matchesObservation(o, f), true);
	assert.equal(matchesObservation(o, { ...f, accent: 'oxytone' }), false);
	assert.equal(matchesObservation(o, { ...f, syllables: 'unknown' }), false);
	assert.equal(matchesObservation(o, { ...D, modernAccent: 'unknown' }), true);
	assert.equal(matchesSound('ā́', ':long'), true); assert.equal(matchesSound('a', ':long'), false);
	assert.equal(matchesSound('ś', 's'), false);
	const query = { ...f, s: 'ā', view: 'evidence', l: 'Phal', r: '∅', source: 'liljegren', unit: 'families' };
	assert.deepEqual(readSoundFilters(new URLSearchParams(soundSearch(query))), query);
	assert.equal(readSoundFilters(new URLSearchParams('view=invalid&unit=invalid')).view, 'distribution');
});

test('clusters and spans preserve the full observable change', () => {
	assert.equal(clusterAt(['a','k','k','a'], 1), 'geminate');
	assert.equal(clusterAt(['a','k','t','a'], 1), 'cluster');
	assert.equal(clusterAt(['a','k','a'], 1), 'singleton');
	const events = alignmentEvents([{ pos: 0, etymonSeg: 'a', reflexSeg: 'ā' }, { pos: 1, etymonSeg: 'k', reflexSeg: '' }, { pos: 2, etymonSeg: 't', reflexSeg: 't' }]);
	assert.equal(events.length, 1); assert.equal(events[0].from, 'ak'); assert.equal(events[0].to, 'ā');
	assert.deepEqual(events[0].labels, ['lengthening', 'loss']);
});

const columns = pairs => pairs.map(([etymonSeg,reflexSeg],pos)=>({pos,etymonSeg,reflexSeg}));
test('sequence patterns compose literals, classes, boundaries and attached marks', () => {
  for (const text of ['kt', 'k t']) assert.deepEqual(parseSoundPattern(text).tokens, ['k','t']);
  assert.deepEqual(parseSoundPattern('VCV').tokens, [':V',':C',':V']);
  assert.deepEqual(parseSoundPattern('#[retroflex+stop]V#').tokens, ['#',':retroflex+stop',':V','#']);
  assert.deepEqual(parseSoundPattern('dʰ ai ŕ̩').tokens, ['dʰ','ai','ŕ̩'.normalize('NFC')]);
  assert.deepEqual(parseSoundPattern('ai',false).tokens, ['a','i']);
  for (const text of ['[retroflex', 'retroflex]', '[wrong]', '#', 'a#k', '*k', '́a']) assert.ok(parseSoundPattern(text).error, text);
  const cs=columns([['ṭ','t'],['a','a'],['ṣ','s'],['i','i']]);
  assert.equal(matchPattern(cs,parseSoundPattern('[retroflex+stop]V')).length,1);
  assert.equal(matchPattern(cs,parseSoundPattern('[retroflex]V')).length,2);
  assert.equal(matchPattern(cs,parseSoundPattern('#[retroflex]V')).length,1);
  assert.equal(matchPattern(cs,parseSoundPattern('[retroflex]V#'))[0].sound,'ṣi');
  assert.equal(matchPattern(cs,parseSoundPattern('#[retroflex]V#')).length,0);
});

test('matched spans include internal insertions, whole forms include edge insertions, and overlaps survive', () => {
  const cs=columns([['','a'],['k','k'],['','i'],['t','t'],['a',''],['','h']]);
  const [span]=matchPattern(cs,parseSoundPattern('kt'));
  assert.deepEqual([span.start,span.end,span.sound,span.outcome],[1,3,'kt','kit']);
  assert.deepEqual(span.positions,[1,3]);
  assert.equal(matchPattern(cs,parseSoundPattern('*'))[0].outcome,'akith');
  assert.equal(matchPattern(cs,parseSoundPattern('a'))[0].outcome,'∅');
  assert.equal(matchPattern(columns([['k','̩'],['t','t']]),parseSoundPattern('kt'))[0].outcome,'?');
  assert.deepEqual(matchPattern(columns([['k','k'],['k','k'],['k','k']]),parseSoundPattern('CC')).map(s=>s.start),[0,1]);
});

test('input facets and descendant grouping produce independent per-language denominators', () => {
  const a=obs('a','t'), b=obs('b','d'), c=obs('c','t','root','P');
  a.sound='ṭ'; b.sound='ṭ'; c.sound='ḍ';
  const grouped=groupStudy([a,b,c],{...S,facet:'sound',groupBy:'syllables'});
  assert.deepEqual(inputColumns(grouped),['ḍ','ṭ']);
  assert.ok(grouped.every(o=>o.outcome==='1 syllable'));
  assert.equal(grouped[0].alignedOutcome,'t');
  const matrix=buildMatrix(grouped,'forms');
  assert.equal(matrix.get('H').get('ṭ').total,2);
  assert.equal(matrix.get('P').get('ḍ').total,1);
  assert.equal(matrix.get('H').has('ḍ'),false);
  assert.equal(matrix.get('H').get('ṭ').outcomes[0].percent,100);
  assert.equal(a.outcome,'t','grouping does not mutate aligned evidence');
  assert.equal(groupStudy([a],{...S,groupBy:'tone'})[0].outcome,'unknown','unmarked accent is not toneless');
});

test('shared entry filters and all three choices round-trip independently of display and evidence', () => {
  const state={...S,s:'[retroflex]',entry:'word=seed&form=bija&relaxed=1&tags=Early-Vedic',langs:'H|Phal',facet:'sound',groupBy:'tone',view:'map',mapGroup:'ṭ',detail:'H',cellInput:'ṭ',r:'unknown',text:'word'};
  assert.deepEqual(readStudy(new URLSearchParams(studySearch(state))),state);
  assert.equal(queryKey(state),queryKey({...state,view:'table',detail:'',mapGroup:'ḍ',r:'',text:'',unit:'families'}));
  assert.equal(loadKey(state),loadKey({...state,facet:'accent',groupBy:'delta'}));
  assert.notEqual(loadKey(state),loadKey({...state,entry:'gloss=fire'}));
  assert.equal(loadKey(state),loadKey({...state,langs:'P'}));
  const legacy=readStudy(new URLSearchParams('view=evidence&l=H&r=∅&s=k'));
  assert.equal(legacy.langs,'H'); assert.equal(legacy.detail,'H'); assert.equal(legacy.r,'∅');
  assert.equal(readStudy(new URLSearchParams('view=compare')).facet,'accent');
});


test('one ancestor sound can be faceted by whole-form accent and syllable count', () => {
  const first=obs('first','kʰ'), second=obs('second','kʰ'), third=obs('third','cʰ');
  first.sound=second.sound=third.sound='kṣ';
  first.form.ancestor=old(['k','ṣ','á','m','a']);
  second.form.ancestor=old(['k','ṣ','a','m','á']);
  third.form.ancestor=old(['k','ṣ','a','m','a','t','a']);
  const rows=[first,second,third];
  const sound=groupStudy(rows,{...S,facet:'sound'});
  const accent=groupStudy(rows,{...S,facet:'accent'});
  const count=groupStudy(rows,{...S,facet:'syllables'});
  assert.deepEqual(inputColumns(sound),['kṣ']);
  assert.deepEqual(inputColumns(accent),['barytone','oxytone','unknown']);
  assert.deepEqual(inputColumns(count),['2 syllables','3 syllables']);
  for(const grouped of [sound,accent,count]) {
    assert.deepEqual(grouped.map(o=>o.outcome),['kʰ','kʰ','cʰ']);
    assert.equal([...buildMatrix(grouped,'forms').get('H').values()].reduce((n,c)=>n+c.total,0),3);
  }
});

test('sound-property facets use only the matched ancestor sequence and retain its order', () => {
  const o=obs('sequence','h');
  o.pos=1; o.endPos=4;
  o.form.columns=columns([['a','a'],['k','k'],['','i'],['ṣ','s'],['a','a'],['m','m']]);
  assert.equal(inputCategory(o,'shape'),'CCV');
  assert.equal(inputCategory(o,'place'),'velar → retroflex → vowel');
  assert.equal(inputCategory(o,'manner'),'stop → fricative → vowel');
  assert.equal(inputCategory(o,'voicing'),'voiceless → voiceless → voiced');
  assert.equal(inputCategory(o,'aspiration'),'unaspirated → unaspirated → vowel');
  o.pos=0; o.endPos=1;
  o.form.columns=columns([['dʰ','d'],['?','a']]);
  assert.equal(inputCategory(o,'aspiration'),'aspirated → unknown');
  assert.equal(inputCategory(o,'voicing'),'voiced → unknown');
});

test('whole-form patterns, matched syllable properties and unknown readings stay distinct', () => {
  const o=obs('prosody','a');
  o.form.ancestor=old(['ā','k','á']); o.syllable=1;
  assert.equal(inputCategory(o,'weightPattern'),'HL');
  assert.equal(inputCategory(o,'quantityPattern'),'LS');
  assert.equal(inputCategory(o,'weight'),'light');
  assert.equal(inputCategory(o,'quantity'),'Short');
  assert.equal(inputCategory(o,'closed'),'Open');
  o.form.parentWord='*āka';
  assert.equal(inputCategory(o,'reconstruction'),'Starred');
  o.form.ancestor={...o.form.ancestor,count:null};
  for(const facet of ['syllables','weightPattern','quantityPattern','weight','quantity','closed']) {
    assert.equal(inputCategory(o,facet),'unknown',facet);
  }
  for(const [facet] of INPUT_FACETS) {
    const state={...S,s:'kṣ',facet,groupBy:'tone',entry:'gloss=seed',langs:'H|Phal'};
    assert.deepEqual(readStudy(new URLSearchParams(studySearch(state))),state,facet);
    assert.equal(loadKey(state),loadKey({...state,facet:'none'}),'faceting reuses the cohort');
  }
});


test('a captured target requires its full context but returns only aligned target outcomes', () => {
  const cs=columns([['a','o'],['k','g'],['','u'],['t','d'],['a','e']]);
  const pattern=parseSoundPattern('V (kt) V');
  assert.deepEqual(pattern.tokens,[':V','k','t',':V']);
  assert.deepEqual(pattern.target,{start:1,end:3});
  const [span]=matchPattern(cs,pattern);
  assert.deepEqual([span.start,span.end,span.contextStart,span.contextEnd],[1,3,0,4]);
  assert.deepEqual([span.index,span.lastIndex,span.sound,span.outcome],[1,2,'kt','gud']);
  const [single]=matchPattern(cs,parseSoundPattern('V (k) t V'));
  assert.equal(single.outcome,'g','insertion outside the target is excluded');
  const observation={...obs('context','g'),pos:span.start,endPos:span.end,contextStart:span.contextStart,contextEnd:span.contextEnd,sound:span.sound};
  observation.form.columns=cs;
  assert.equal(inputCategory(observation,'sound'),'kt');
  assert.equal(inputCategory(observation,'context'),'akta');
  assert.equal(matchPattern(cs,parseSoundPattern('C (kt) V')).length,0,'context must match');
  assert.equal(matchPattern(cs,parseSoundPattern('#V (kt) V#')).length,1);
  const edge=matchPattern(columns([['k','g'],['a','o']]),parseSoundPattern('#(k)V#'))[0];
  assert.deepEqual([edge.index,edge.lastIndex,edge.sound,edge.outcome],[0,0,'k','g']);
  assert.equal(matchPattern(columns([['a','?'],['k',''],['a','o']]),parseSoundPattern('V(k)V'))[0].outcome,'∅');
});

test('target notation is validated and survives canonical text and shared URLs', () => {
  for(const value of ['V (k V','V k) V','V () V','(k)(t)','((k))','(#k)V','V(k#)']) {
    assert.ok(parseSoundPattern(value).error,value);
  }
  for(const value of ['V(k)V','#([retroflex+stop]V)#','(dʰ)ai','(kṣ)']) {
    const parsed=parseSoundPattern(value);
    assert.equal(parsed.error,'',value);
    assert.deepEqual(parseSoundPattern(formatSoundPattern(parsed)),parsed);
    const state={...S,s:value,facet:'sound'};
    assert.deepEqual(readStudy(new URLSearchParams(studySearch(state))),state);
  }
  const all=parseSoundPattern('V (k) V');
  assert.equal(formatSoundPattern(all,null),'V k V');
  assert.equal(formatSoundPattern(all,{start:0,end:2}),'(V k) V');
});

test('class insertion preserves caret context, combines descriptors, and supports selection targets', () => {
  let result=insertPatternClass('V k V',2,3,'retroflex');
  assert.equal(result.text,'V [retroflex] V');
  result=insertPatternClass('[retroflex]',10,10,'stop');
  assert.equal(result.text,'[retroflex+stop]');
  assert.equal(parseSoundPattern(result.text).error,'');
  assert.equal(insertPatternClass(result.text,result.caret,result.caret,'stop').text,result.text);
  assert.equal(insertPatternClass('V(k)V',2,3,'C').text,'V(C)V');
  assert.equal(insertPatternClass('[retroflex]',1,10,'stop').text,'[stop]');
  assert.equal(insertPatternClass('kt',1,1,'V').text,'k V t');
  assert.equal(targetSelectedText('V k V',2,3).text,'V (k) V');
  assert.equal(targetSelectedText('V (k) V',6,7).text,'V k (V)');
  assert.equal(targetSelectedText('V (k) V',0,0).text,'V (k) V');
});


test('language thresholds use distinct forms across all groups, with inclusive bounds and zero', () => {
	const rows = [obs('f1','a'), obs('f1','k','root','H',2), obs('f2','e'), obs('f3','a','root','P')];
	const counts = languageOutcomeCounts(rows);
	assert.deepEqual([...counts], [['H',2], ['P',1]]);
	assert.deepEqual(languageOutcomeCounts(groupStudy(rows,{...S,facet:'sound',groupBy:'accent'})),counts);
	const language = {lemma_count:100};
	assert.equal(matchesLanguageCounts(language,2,{...S,totalMin:'100',totalMax:'100',outcomeMin:'2',outcomeMax:'2'}),true);
	assert.equal(matchesLanguageCounts(language,2,{...S,totalMin:'101'}),false);
	assert.equal(matchesLanguageCounts(language,2,{...S,outcomeMin:'3'}),false);
	assert.equal(matchesLanguageCounts(language,2,{...S,outcomeMax:'0'}),false);
	assert.equal(matchesLanguageCounts(language,0,{...S,outcomeMax:'0'}),true);
	assert.equal(matchesLanguageCounts(language,undefined,{...S,outcomeMin:'3'}),true,'pending outcomes are not misreported as zero');
	assert.match(languageCountError({...S,outcomeMin:'10',outcomeMax:'2'}),/minimum/);
	assert.match(languageCountError({...S,totalMin:'-1'}),/whole number/);
	assert.equal(languageCountError({...S,outcomeMax:'0'}),'');
});

test('language choices and count limits round-trip but reuse the same observation cohort', () => {
	const state = {...S,s:'V ([stop]) V',langs:'H|P',totalMin:'1000',totalMax:'20000',outcomeMin:'10',outcomeMax:'50'};
	assert.deepEqual(readStudy(new URLSearchParams(studySearch(state))),state);
	assert.notEqual(queryKey(state),queryKey({...state,outcomeMin:'20'}));
	assert.equal(loadKey(state),loadKey({...state,langs:'Phal',totalMin:'2000',outcomeMin:'20',view:'map',unit:'families',facet:'syllables',groupBy:'tone'}));
	assert.equal(readStudy(new URLSearchParams('outcomeMax=0')).outcomeMax,'0');
	assert.equal(readStudy(new URLSearchParams('totalMin=-1&outcomeMin=3.5')).totalMin,'');
	assert.equal(readStudy(new URLSearchParams('totalMin=-1&outcomeMin=3.5')).outcomeMin,'');
});


test('shared language options search by name, ID, branch and dialect parent', async () => {
	const bundle = await build({entryPoints:['src/lib/languageOptions.ts'],bundle:true,write:false,platform:'node',format:'esm'});
	const {languageOptions,filterOptions} = await import('data:text/javascript;base64,'+Buffer.from(bundle.outputFiles[0].text).toString('base64'));
	const options = languageOptions([{id:'Sh',name:'Shina',clade:'Shinaic'},{id:'Phal',name:'Palula',clade:'Shinaic'},{id:'H',name:'Hindi-Urdu',clade:'W. Hindi'}],[{token:'dialect-sh-gilgit',name:'Gilgit',language_id:'Sh'}]);
	assert.deepEqual(filterOptions(options,'Phal').map(o=>o.value),['Phal']);
	assert.deepEqual(filterOptions(options,'shinaic').map(o=>o.value),['Sh','Phal','dialect-sh-gilgit']);
	assert.deepEqual(filterOptions(options,'Shina Gilgit').map(o=>o.value),['dialect-sh-gilgit']);
	assert.equal(options.at(-1).label,'Shina: Gilgit');
	assert.deepEqual(filterOptions(options,'nonexistent'),[]);
});
