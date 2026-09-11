"""Check the blog's aggregates, citations and exports against frozen research rows."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'research/shinaic-accent/quantitative-2026-09-09'
PUBLIC=ROOT/'static/research/shinaic-accent'
charts=json.loads((ROOT/'src/lib/blog/data/shinaic-accent-charts.json').read_text())
examples=json.loads((PUBLIC/'examples.json').read_text())
post=(ROOT/'src/lib/blog/posts/shinaic-accent.md').read_text()
checks=0
def check(condition,reason):
    global checks
    assert condition,reason
    checks+=1
def rows(name):
    with (Q/name).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def vector(key,view=0):return [r['values'] for r in charts[key]['views'][view]['rows']]
def counts(items,statuses):
    c=Counter(r['status'] for r in items)
    return [c[s] for s in statuses]
def unique(items,columns):
    d={}
    for r in items:d.setdefault(tuple(r[c] for c in columns),r)
    return list(d.values())

check(len(charts)==7 and len(examples)==7,'seven main sections')
for key,rr in examples.items():
    check(len(rr)==10 and len({r['family_id'] for r in rr})==10,key+' ten distinct families')
    for r in rr:
        check(r['annotation'] and r['evidence'] and all(c in post for c in r['cells']),key+' rendered evidence row')
        for source_row in r['evidence']:
            check(any(source_row in rows(file) for file in r['source_table'].split(';')),key+' exact frozen evidence')
check(re.findall(r'```chart\n([a-z-]+)\n```',post)==list(charts),'chart order and registration')
for letter in 'abcdef':check(f'id="appendix-{letter}"' in post,'appendix '+letter)

# Recompute each displayed scope from the audited rows; no modal category is silently dropped.
for n,scope in enumerate(['Gilgit-Degener-only','all-sources-all-lects']):
    expected=[[int(r.get(c) or 0) for c in ['consistent','conflicting','opposite']] for r in rows('old-long-nominal-sensitivity.tsv') if r['scope']==scope and r['language'] in ['Sh','Phal'] and int(r['scorable_families'])]
    check(vector('old-long',n)==expected,'old-long '+scope)
check(vector('old-long',2)==[[int(r[c]) for c in ['consistent','conflicting','opposite']] for r in rows('old-long-screen.tsv') if r['language'] in ['Sh','Phal']],'old-long broad')
gg=unique(rows('gilgit-o-adjectives.tsv'),['form','gloss'])
pa=unique(rows('palula-tagged-u-adjectives.tsv'),['form','gloss'])
ui=unique(rows('palula-u-adjectives.tsv'),['masculine','feminine','gloss'])
check(vector('gender')==[counts(gg,['consistent','exception','unscorable']),counts(pa,['consistent','exception','unscorable']),counts(ui,['consistent','exception','unscorable']),counts([r for r in ui if r['input'].startswith('Uml')],['consistent','exception','unscorable'])],'gender typed classes')
expected=[]
for language in ['Sh','Phal','Sv','Kalk','Kund','bro','Ush']:
    r=next(r for r in rows('property-location-summary.tsv') if r['language']==language)
    c=json.loads(r['family_statuses'])
    expected.append([c.get(k,0) for k in ['only-penultimate','mixed-with-penultimate','only-other-position','unscorable']])
check(vector('gender',1)==expected,'seven-language property comparison')
ss=[r for r in rows('palula-short-a-sensitivity.tsv') if r['domain']=='closed-lexemes-article-numeral-one-collapsed']
check(vector('lengthening')==[[json.loads(r['outcome_sets']).get(c,0) for c in ['E','L']] for r in ss],'short-a lexeme scope')
vr=[r for r in rows('vowel-raising-reviewed.tsv') if r['tested_syllable_domain']=='word-final-closed']
expected=[]
for accent,vowel in [('E','a'),('E','e'),('L','a')]:
    c=Counter(r['ashret_test_vowel'] for r in vr if r['biori_accent']==accent and r['biori_test_vowel']==vowel)
    expected.append([c[k] for k in ['o','u','i','a']])
check(vector('raising')==expected,'vowel raising all outcomes')
ir=[rows(f) for f in ['palula-umlaut-i-nouns.tsv','palula-i-decl-extension.tsv']]
expected=[]
for group in ir:
    comparable=[r for r in group if r['status']=='consistent']
    check(all(r['inflected_outcome']=='S' and r.get('inflected_position',r.get('inflected_accent_from_right'))=='1' for r in comparable),'inflections explicitly final short accent')
    expected.append([len(comparable),0,len(group)-len(comparable)])
check(vector('inflection')==expected,'inflection pairing exclusions')
check(vector('inflection',1)==[[Counter(r['citation_outcome'] for r in group if r['status']=='consistent')[s] for s in ['L','E','S','short-monosyllable']] for group in ir],'citation accent scope')
dr=rows('dras-suffix-accent-review.tsv')
expected=[]
for suffix in ['-eh/-eɦ','-e','-i','other']:
    selected=[r for r in dr if (r['suffix']==suffix if suffix!='other' else r['suffix'] not in ['-eh/-eɦ','-e','-i'])]
    c=Counter(r['suffix_accent_status'] for r in selected)
    expected.append([c[k] for k in ['final-accent-only','final-plus-other-accent','stem-accent-only','unmarked']])
check(vector('dras')==expected,'all Dras endings including dual marks')
nr=rows('numeral-series-tests.tsv')
for number in range(11,21):
    for language,outcome in [('Phal','E' if number<19 else 'L'),('Kalk','H2' if number<19 else 'H1')]:
        r=next(r for r in nr if r['numeral']==str(number) and r['language']==language)
        check(json.loads(r['observed'])==[outcome] and r['consistent']=='1','numeral '+str(number)+' '+language)
check(vector('numerals')==[[8,0],[0,2]],'numeral aggregation')

for asset in json.loads((PUBLIC/'manifest.json').read_text()):
    p=PUBLIC/asset['path']
    check(p.stat().st_size==asset['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256'],'asset '+asset['path'])
    source=Q/p.name if p.suffix!='.zip' else Q.with_suffix('.zip')
    check(p.read_bytes()==source.read_bytes(),'unchanged source '+p.name)
for path in re.findall(r'\]\((/research/[^)#]+)',post):
    check((ROOT/'static'/path.lstrip('/')).is_file(),'download '+path)
print(f'{checks} evidence checks passed: seven charts, seventy family examples, six appendices, exact frozen exports.')
