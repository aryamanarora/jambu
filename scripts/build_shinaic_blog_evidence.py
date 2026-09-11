"""Export a blog view of the sealed 2026-09-09 research; never rewrite the study.

Run from any directory with Python 3. No database edits or new etymological edges.
The hand-selected examples below are illustrations, not the chart denominators.
"""
import csv
import hashlib
import html
import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / 'research/shinaic-accent/quantitative-2026-09-09'
DEST = ROOT / 'static/research/shinaic-accent'
DATA = ROOT / 'src/lib/blog/data'
TEMPLATE = ROOT / 'research/shinaic-accent/blog-post-2026-09-09.md'

def rows(file):
    with (Q / file).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def plain(s):
    return html.unescape(re.sub('<[^>]+>', '', s)).replace('|', '\\|')

def norm(s):
    return unicodedata.normalize('NFC', plain(s)).strip()

families = {r['family_id']: r for r in rows('families.tsv')}
tokens = rows('analysis-tokens.tsv')
byid = {}
for r in tokens:
    byid.setdefault(r['id'], []).append(r)

def entry(f, label=None):
    return f'[{plain(label or families[f]["headword"])}](entry:{f})'

def form(label, record):
    assert record in byid, record
    return f'[{plain(label)}](form:{record})'

def paired_form(label, ids):
    matched = [i for i in ids if any(norm(label) in {norm(t['form']), norm(t['reading_form'])} for t in byid[i])]
    assert matched, (label, ids)
    return form(label, matched[0])

examples = {}
tables = {}

def table(key, headers, records):
    assert len(records) == 10, (key, len(records))
    assert len({r['family_id'] for r in records}) == 10, key
    examples[key] = records
    tables[key] = '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] + ['| ' + ' | '.join(r['cells']) + ' |' for r in records])

historical = rows('historical-observations.tsv')
old_choices = {
    '2993': 'The old accented ā stays early despite loss of the second k; nasalization is transcribed as ~.',
    '3735': 'Early here and in Palula; Buddruss’s late Gilgit reading is a source disagreement, retained below.',
    '4368': 'Early despite simplification of gr. Kalkoti’s final High is a separate correspondence problem.',
    '9072': 'Inherited long ā remains early despite aspiration; contrast newly lengthened “hand” in §3.',
    '10104': 'Early “month” contrasts with late “meat” in several lects. Keep Gilgit máaz distinct from móos elsewhere.',
    '3084': 'Late after the old accented ending disappears. Iranian saal is a different word, excluded from this comparison.',
    '4336': 'Independent Gilgit sources agree on late accent; early Kohistani/Guresi forms require a separate explanation.',
    '4931': 'The simple noun is late. Extended čurúṭo belongs to a different formation and is not counted as its variant.',
    '6849': 'Old ū stays long and becomes late. Palula dhuumíi has another ending and is not the same comparison cell.',
    '9216': 'The ā was already long in bālá; modern late accent does not require compensatory lengthening.'
}
rr = []
for f, note in old_choices.items():
    r = next(r for r in historical if r['family_id'] == f and r['source'] == 'degener-shina2008' and r['modern_nuclei'] == '1' and not r['screening_exclusions'])
    rr.append(dict(family_id=f, source_table='historical-observations.tsv', evidence=[r], annotation=note, cells=[entry(f, r['historical_input']) + ' — ' + plain(r['gloss']), form(r['form'], r['record_id']), r['raw_outcome'], note]))
table('old-long', ['Etymon · meaning', 'Gilgit (Degener)', 'Accent', 'Annotation'], rr)

gil = rows('gilgit-o-adjectives.tsv')
pal = rows('palula-u-adjectives.tsv')
adj_choices = {
    '644': 'The masculine/feminine aa : ee alternation leaves the final gender vowel unaccented; old árdha is also attested.',
    '1236': 'A long, early root with an independently recorded āmaka formation. Modern -u alone would not establish that history.',
    '3523': 'The last root syllable carries accent even though an earlier syllable also has a long vowel.',
    '5244': 'Palula E and Gilgit L occupy the same penultimate syllable. Contraction and old jī́vant/jīvantá alternatives matter.',
    '5679': 'Palula E versus Gilgit L: syllable location agrees while mora alignment differs. Astori tátto supplies a geminate comparison.',
    '6926': 'Both languages accent the stem. Independently attested nágnaka supports an extended historical formation.',
    '6983': 'Palula E versus Gilgit L again. The surviving w makes a simple “lost w caused lengthening” account insufficient.',
    '8047': 'Accent falls on the final root syllable; old pāṇḍurá competes with the initially accented headword.',
    '8283': 'A multisyllabic adjective with early accent before the gender ending; rounded vowels record a separate quantity history.',
    '12487': 'Both accent the final root syllable. The related contracted noun “fever” must be analyzed separately.'
}
rr=[]
for f,note in adj_choices.items():
    p=next(r for r in pal if r['family_id']==f and r['input'].startswith('Uml') and 'dialect:' not in r['source_tags'] and r['status']=='consistent')
    g=next((r for r in gil if r['family_id']==f and r['source']=='degener-shina2008' and r['status']=='consistent'),None)
    rr.append(dict(family_id=f,source_table='palula-u-adjectives.tsv;gilgit-o-adjectives.tsv',evidence=[p]+([g] if g else []),annotation=note,cells=[entry(f)+' — '+plain(p['gloss'].split(';')[0]),form(g['form'],g['record_id']) if g else '—',form(p['masculine'],p['record_id'])+' / *'+plain(p['feminine'])+'*',note]))
table('gender',['Etymon · meaning','Gilgit','Palula masculine / feminine','Annotation'],rr)

short_choices = {
    '941':'The older numeral lost an accented ending, but Biori has a short stem. Ashret E fits subsequent lengthening, not simple retention.',
    '2830':'Biori kaṇ supplies the short-root comparison; Ashret lengthens with early accent after earlier consonant changes.',
    '2892':'The kr cluster survives in both dialects; early lengthening cannot be attributed to its loss.',
    '10539':'The blood noun has a short Biori root and early Ashret aa; it is distinct from extended “red” adjective forms.',
    '13254':'The early citation becomes suffix-accented sarí in inflection (§5); E is not an invariant paradigm property.',
    '3818':'The aspirated onset accompanies late new aa. The Biori short comparator supplies the relevant quantity contrast.',
    '5334':'The hair/fur noun has late aa with aspiration; the goat-hair sense is retained rather than merged with generic hair.',
    '13952':'Late citation haáḍ contrasts with early inflected háaḍa; morphology changes the mora alignment.',
    '14000':'Initial h belongs to the conditioning group alongside aspirated stops; haál has the predicted late alignment.',
    '14024':'Late haát, but early inflected háata. This is a newly lengthened root, unlike old-long early pháal (§1).'
}
rr=[]
for f,note in short_choices.items():
    r=next(r for r in rows('palula-short-a-pairs.tsv') if json.loads(r['family_ids'])==[f] and r['status']=='consistent')
    ids=json.loads(r['record_ids']); a=json.loads(r['ashret_forms'])[0]
    rr.append(dict(family_id=f,source_table='palula-short-a-pairs.tsv',evidence=[r],annotation=note,cells=[entry(f)+' — '+plain(r['gloss'].split(';')[0]),paired_form(r['biori'],ids)+' → '+paired_form(a,ids),('No h → E' if r['expected']=='E' else 'h / aspiration → L'),note]))
table('lengthening',['Etymon · meaning','Biori → Ashret','Condition → outcome','Annotation'],rr)

raise_choices={
    '125':'The final closed syllable raises aa to oo. The earlier syllable does not disqualify the word: this is a syllable-domain test.',
    '2993':'Old-long early “crow” also fits the inheritance comparison (§1); raising changes quality while E survives.',
    '3735':'Early ee raises to ii. The Gilgit source disagreement does not erase this local dialect correspondence.',
    '4368':'Early aa raises despite aspiration: distinguish inherited long roots from the short-a lengthening layer.',
    '6547':'Early ee → ii implies early accent before raising, if dēśá is the ancestor; a very recent retraction is insufficient.',
    '6914':'The preserved consonantal frame and fingernail meaning support the paired vowel comparison.',
    '9072':'The aspirated old-long root raises normally. Its behavior contrasts with newly lengthened late haát “hand”.',
    '9828':'Early méeš → míiš is secure in this comparison. Kalkoti meéš is an independent accentual residual.',
    '12323':'The bed sense continues a lying-down formation; the early ee → ii correspondence is directly visible.',
    '12753':'An aa → uu outcome. Internal ša(w)úra independently supports earlier au; this evidence is stronger than for stream or lap.'
}
rr=[]
for f,note in raise_choices.items():
    r=next(r for r in rows('vowel-raising-reviewed.tsv') if r['biori_family']==f and r['tested_syllable_domain']=='word-final-closed')
    ids=json.loads(r['record_ids'])
    rr.append(dict(family_id=f,source_table='vowel-raising-reviewed.tsv',evidence=[r],annotation=note,cells=[entry(f)+' — '+plain(r['gloss'].split(';')[0]),paired_form(r['biori'],ids),paired_form(r['ashret'],ids),note]))
table('raising',['Etymon · meaning','Biori','Ashret','Annotation'],rr)

idecl_choices={
    '10702':'Counted night/day-period: raát/reetí. Ordinary róot/róota is another noun and declension; merging their senses creates a false contradiction.',
    '11564':'The word/speech noun joins the aa/ee subclass: late root in citation, final -í in inflection.',
    '1577':'This is the valid izraáṇ paradigm. The same izreeṇí was attached to the different Biori synonym niildhráal, an excluded mismatch.',
    '8906':'Wound belongs to the same aa/ee subclass; final -í is observed in the supplied full form, not inferred from suffix shorthand.',
    '9560':'Earthquake follows the aa/ee pattern. Records carrying a copied wheat gloss require a separate editorial correction.',
    '4762':'An early citation also takes final -í. Biori short čar prevents treating its modern aa as inherited old ā.',
    '13254':'Early sáar → sarí: the general i-declension rule predicts suffix accent, not late accent in every citation.',
    '7031':'Early náas → nastí also changes the stem shape; do not manufacture the inflection by merely appending -i.',
    '13468':'The regional trousers noun has late suthaán; Biori suthán is short. Both take the recorded suthaní.',
    '13878':'The trouser-cord noun joins the non-aa/ee extension sample, with final -í but no ee umlaut in this pair.'
}
ir=rows('palula-umlaut-i-nouns.tsv')+rows('palula-i-decl-extension.tsv')
rr=[]
for f,note in idecl_choices.items():
    r=next(r for r in ir if r['family_id']==f and r['status']=='consistent')
    rr.append(dict(family_id=f,source_table='palula-umlaut-i-nouns.tsv' if 'inflection_cells' in r else 'palula-i-decl-extension.tsv',evidence=[r],annotation=note,cells=[entry(f)+' — '+plain(r['gloss'].split(';')[0]),form(r['citation'],r['record_id'])+' / *'+plain(r['inflected'])+'*',r['citation_outcome']+' → final -í',note]))
table('inflection',['Etymon · meaning','Citation / inflected form','Accent','Annotation'],rr)

dras_choices={
    'f_6yyktgwn5xkfi':'Roof: the plural has final-only accent; the candidate singular has root accent. The shelter/roof semantic link is straightforward.',
    'f_mecchxwbk4v6s':'Tube: final yéh follows an i-derived stem. Compare nāḍī́, rather than assigning the accent of an unextended bamboo noun.',
    'f_7du73gc342cha':'Barber is a regional title/occupation word. Its final-accented plural illustrates local inflection, not direct Sanskrit accent retention.',
    'f_bekmf4gzkvfts':'Hammer has TWO acute marks in print. Final accent is present, but replacing this with a final-only transcription would falsify the source.',
    'f_eqecsfyzwv674':'Nail also retains two acutes; print separates kí:l yéh. A clitic-like expression or inconsistent typography remains possible.',
    'f_tc55mtuopm7me':'Head: plain -e is unaccented. Consonant alternation in the candidate singular/plural is separate from stress location.',
    'f_pw3jtn2xowmns':'Liver: root stress survives before plain -e; vowel length does not force accent onto the ending.',
    'f_vt7kf2ylx7th2':'Rope: a candidate -u singular alternates with plural -e, with accent remaining on the root.',
    'f_766uzyhomkxfs':'Skin: the consonant-final stem is followed by unaccented -e; the inherited family link does not itself predict this modern suffix behavior.',
    'f_4674l576w3lu2':'Leaf: the gender/number vowel changes while the root accent stays. Keep the two-mora root separate from the final vowel.'
}
rr=[]
for rid,note in dras_choices.items():
    r=next(r for r in rows('dras-suffix-accent-review.tsv') if r['plural_id']==rid)
    f=next(t['research_family_id'] for t in byid[rid] if t['research_family_id'])
    rr.append(dict(family_id=f,source_table='dras-suffix-accent-review.tsv',evidence=[r],annotation=note,cells=[entry(f)+' — '+r['gloss'],form(r['plural'],rid),{'final-accent-only':'Final only','final-plus-other-accent':'Final + stem','stem-accent-only':'Stem only'}[r['suffix_accent_status']],note]))
table('dras',['Etymological family · meaning','Dras plural','Accent marked','Annotation'],rr)

nums=rows('numeral-series-records.tsv')
numeral_notes={11:'The compound retains an initial syllable, yet patterns with monosyllabic twelve and thirteen.',12:'A residual of simple E → zero-High becomes a regular member of the ten-compound series.',13:'Early Palula tríiš is explicit; rewriting it as late would remove the very correspondence to explain.',14:'The ten element carries the compared accent; the initial constituent does not attract it.',15:'The same E → H2 correspondence continues with another independently recognizable first constituent.',16:'Segmental reshaping of “six” does not change the series-level accent correspondence.',17:'Palula oo and Kalkoti aa differ in quality while preserving this E → H2 pairing.',18:'The eighth ten-compound completes the observed series; shared morphology makes the examples dependent.',19:'The twenty-based formation follows twenty’s L → H1 correspondence, not the preceding eight numerals.',20:'The base for the preceding twenty-element formation supplies an independent morphological control.'}
rr=[]
for n,note in numeral_notes.items():
    p=next(r for r in nums if r['numeral']==str(n) and r['language']=='Phal' and r['source']=='liljegren' and not r['dialect'])
    k=next(r for r in nums if r['numeral']==str(n) and r['language']=='Kalk' and r['source']=='hultman2023kalkoti')
    f=p['family_id']
    rr.append(dict(family_id=f,source_table='numeral-series-records.tsv',evidence=[p,k],annotation=note,cells=[str(n)+' · '+entry(f),form(p['form'],p['record_id']),form(k['form'],k['record_id']),('E → H2. ' if n<19 else 'L → H1. ')+note]))
table('numerals',['Number · etymon','Palula Ashret','Kalkoti (2023)','Correspondence and annotation'],rr)

charts={}
def view(label,unit,note,cats,data):
    return dict(label=label,unit=unit,note=note,categories=cats,rows=[dict(label=k,values=v) for k,v in data])
def chart(key,title,sources,views):
    charts[key]=dict(id=key,title=title,sources=sources,views=views)

cats=['Predicted outcome only','Conflicting outcomes','Opposite outcome only']
v=[]
for scope,label in [('Gilgit-Degener-only','Restricted nouns · Degener Gilgit'),('all-sources-all-lects','Restricted nouns · all Shina / Palula sources')]:
    data=[]
    for r in rows('old-long-nominal-sensitivity.tsv'):
        if r['scope']==scope and r['language'] in ['Sh','Phal'] and int(r['scorable_families']):
            data.append((('Shina' if r['language']=='Sh' else 'Palula')+' · '+('root-accented → E' if r['input_class'].endswith('barytone') else 'ending-accented → L'),[int(r.get(c) or 0) for c in ['consistent','conflicting','opposite']]))
    v.append(view(label,'Scorable etymological families','The restricted set is a selected follow-up of 29 nominal families, not an exhaustive a-stem census. Source pooling reintroduces disagreement. Documented alternative old inputs remain visible in the audit.',cats,data))
v.append(view('Broad screen · all formations','Scorable etymological families','This exploratory screen also includes other grammatical formations. A family with both E and L is counted once as conflicting, not twice as confirming evidence.',cats,[(('Shina' if r['language']=='Sh' else 'Palula')+' · '+('root-accented → E' if r['test'].endswith('barytone') else 'ending-accented → L'),[int(r[c]) for c in ['consistent','conflicting','opposite']]) for r in rows('old-long-screen.tsv') if r['language'] in ['Sh','Phal']]))
chart('old-long','Inherited accent: a clean local result, a messier wider comparison',['old-long-nominal-sensitivity.tsv','old-long-screen.tsv'],v)
chart('gender','Short gender endings leave the preceding syllable prominent',['gilgit-o-adjectives.tsv','palula-tagged-u-adjectives.tsv','palula-u-adjectives.tsv','property-location-summary.tsv'],[
    view('Source-tagged grammatical classes','Unique form/gloss or citation types','The broader Palula adjective class has nine final-accented types. The regular/umlaut pool includes participles; these overlapping samples must not be added together.', ['Penultimate','Final','Unscorable'], [('Gilgit · short -o adjectives',[110,0,11]),('Palula · short -u adjectives',[111,9,6]),('Palula · regular/umlaut u:i types',[115,8,6]),('Palula · umlaut subclass',[37,0,2])]),
    view('Core property families · seven languages','Families in a separate retained-ending screen','This is syllable location, not a pan-Shinaic tone comparison. Kalkoti has no candidates in this retained-ending domain. Unknown readings stay in the denominator.', ['Penultimate only','Mixed with penultimate','Other position only','Unscorable'], [('Shina',[35,4,0,0]),('Palula',[25,2,1,0]),('Sauji',[1,0,3,10]),('Kalkoti',[0,0,0,0]),('Kundal Shahi',[0,0,0,1]),('Brokskat',[10,0,0,1]),('Ushojo',[14,0,1,4])])])
chart('lengthening','Aspiration separates most early and late new long vowels',['palula-short-a-pairs.tsv','palula-short-a-sensitivity.tsv'],[
    view('Closed monosyllables · lexemes','35 lexemes','Biori short a and Ashret long aa define the comparison before Ashret accent is scored. Article and numeral “one” count as one lexeme. Today, mountain and grape are retained residuals.', ['Early (E)','Late (L)'], [('Without h / aspiration',[25,1]),('With h / aspiration',[2,7])])])
chart('raising','Early long vowels raise in the final closed syllable',['vowel-raising-reviewed.tsv'],[
    view('Final closed syllables','Form pairs','The six aa → uu cases are raised, but are residuals of a narrower aa → oo rule. The two late-aa controls are two pronoun forms with one accusative ending, not two independent lexical controls. Thirty other-domain pairs are outside this test.', ['oo','uu','ii','aa retained'], [('Biori early aa',[29,6,0,0]),('Biori early ee',[0,0,11,0]),('Biori late aa',[0,0,0,2])])])
chart('inflection','Different citation accents converge on inflected -í',['palula-umlaut-i-nouns.tsv','palula-i-decl-extension.tsv'],[
    view('Inflected outcomes by morphological sample','Retrieved paradigm cells','115 comparable cells represent 95 operational lexemes; the two samples overlap in one lexeme. Exclusions are mismatched synonym/variant paradigms, not observed exceptions.', ['Final -í','Other accent','Excluded pairing'], [('aa / ee+i subclass',[73,0,1]),('Further i-declension paradigms',[42,0,1])]),
    view('Citation accents before final-accented inflection','Comparable paradigm cells','Every citation group shown here has final -í in the corresponding full inflected form. E/L distinguish the two morae of a long vowel; short citations cannot exhibit that contrast.', ['Late (L)','Early (E)','Short accented','Short monosyllable, unmarked'], [('aa / ee+i subclass',[73,0,0,0]),('Further i-declension paradigms',[24,6,5,7])])])
chart('dras','Dras plural endings differ sharply in accent marking',['dras-suffix-accent-review.tsv'],[
    view('All plural ending groups','287 raw plural citations','“Final present” includes final-only and double-accented citations: 57/60 for -eh, 24/176 for -e. These are not independent etyma or automatically verified singular–plural paradigms.', ['Final only','Final + another acute','Stem only','Unmarked'], [('-eh / -eɦ',[53,4,3,0]),('-e',[22,2,130,22]),('-i',[1,0,11,3]),('Other formations',[27,1,4,4])])])
chart('numerals','Ten-compounds and twenty-based forms diverge together',['numeral-series-tests.tsv','numeral-series-records.tsv'],[
    view('Kalkoti outcomes by numeral formation','Numeral families','All eight 11–18 forms have E in both recorded Palula dialect comparisons and H2 in Kalkoti. Nineteen and twenty have Palula L and Kalkoti H1. Shared compound structure means the ten rows are not ten independent innovations.', ['H2 · second-mora High','H1 · first-mora High'], [('11–18 · ten compounds (Palula E)',[8,0]),('19–20 · twenty-based (Palula L)',[0,2])])])

apocope=rows('kalkoti-palula-combined.tsv')
ap=[r for r in apocope if r['input_class']=='Palula-prefinal-accent-plus-short-final-vowel' and r['status']=='consistent']
assert len(ap)==10 and len({r['family_id'] for r in ap})==9
tables['apocope']='\n'.join(['| Family · meaning | Palula | Recorded Kalkoti comparisons | Annotation |','| --- | --- | --- | --- |']+['| '+entry(r['family_id'])+' — '+', '.join(json.loads(r['glosses']))+' | *'+r['palula']+'* | '+', '.join('*'+f+'*' for f in json.loads(r['kalkoti_forms']))+' | '+('Same broad family as the other grandparent term; these are two cells, not two independent etyma.' if r['family_id']=='6261' else 'Short-vowel final High: no extra vowel length is reconstructed.' if r['family_id']=='6368' else 'High and Low coexist; Low is a separate dimension.' if r['family_id']=='4516' else 'Matches the final-High comparison; unmarked source variants add no tonal vote.')+' |' for r in ap])
kp=[r for r in rows('kundal-primary-paradigms.tsv') if r['input_formation']=='post-accenting-noun-origin-unexplained']
tables['kundal']='\n'.join(['| Meaning | Nominative singular | Oblique singular | Oblique plural | Annotation |','| --- | --- | --- | --- | --- |']+['| '+r['gloss']+' | *'+r['nom_singular']+'* | *'+r['obl_singular']+'* | *'+r['obl_plural']+'* | '+('Long root: contradicts a general short-root explanation.' if 'LONG' in r['observed_pattern'] else 'Suffix accent is attested; its historical source is unresolved.')+' |' for r in kp])

files=sorted(set(s for c in charts.values() for s in c['sources']) | {r['source_table'] for records in examples.values() for r in records if ';' not in r['source_table']} | {'old-long-nominal-formation-audit.tsv','old-long-screen-residuals.tsv','old-long-nominal-residuals.tsv','kalkoti-palula-combined.tsv','kundal-primary-paradigms.tsv','property-location-screen.tsv','short-root-cluster-summary.tsv','source-register.tsv','etymology_proposals.jsonl','editorial-and-source-decisions.tsv','exception-ledger.tsv','dras-paradigm-review.tsv','coverage-by-source.tsv'})
# Source names are explicit; a missing source is an error, never a silently omitted download.
for file in files: assert (Q/file).exists(), file
for p in [DEST/'tables',DATA]:p.mkdir(parents=True,exist_ok=True)
manifest=[]
for file in files:
    target=DEST/'tables'/file
    shutil.copyfile(Q/file,target)
    manifest.append(dict(path='tables/'+file,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size))
archive=Q.with_suffix('.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='cff67a3590fcffebc2f5177a4bc34f3abd99d71cdc6f53eef4825cb0208595e6'
shutil.copyfile(archive,DEST/archive.name)
manifest.append(dict(path=archive.name,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size))
for path,data in [(DATA/'shinaic-accent-charts.json',charts),(DEST/'examples.json',examples),(DEST/'manifest.json',manifest)]:
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
text=TEMPLATE.read_text()
for key,value in tables.items():
    marker='{{TABLE:'+key+'}}'
    assert text.count(marker)==1,(key,'missing/duplicate marker')
    text=text.replace(marker,value)
assert '{{TABLE:' not in text
(ROOT/'src/lib/blog/posts/shinaic-accent.md').write_text(text)
print(f'Built {len(charts)} charts; {sum(map(len,examples.values()))} annotated examples; {len(manifest)} source assets.')
