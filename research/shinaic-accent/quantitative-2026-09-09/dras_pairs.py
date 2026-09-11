"""Retrieve Dras noun paradigms by explicit number and identical source gloss.

Suffix groups are segmentally defined before reading their accent. Candidate
pairing is broad and exported for manual review, not a cognacy assertion.
"""
import re,json,unicodedata as ud
from collections import defaultdict,Counter
from analysis_data import load_records,write_tsv

def plain(s):
    return ''.join(c for c in ud.normalize('NFD',s) if c not in '\u0301\u0300')

def number(r):
    s=r['tags']+';'+r['description'] if 'tags' in r else r.get('form_tags','')+';'+r['description']
    if re.search(r'\bno\s+pl\b',s,re.I):return ''
    if re.search(r'\bPL\b|\bpl\b',s):return 'pl'
    if re.search(r'\bSG\b|\bsg\b',s):return 'sg'
    return ''

def main():
    rows=[r for r in load_records() if r['source_keys']=='rajapurohit2012']
    groups=defaultdict(list)
    for r in rows:groups[r['research_gloss'].lower().strip()].append(r)
    pairs=[]
    for g,rs in groups.items():
        sg=[r for r in rs if number(r)=='sg'];pl=[r for r in rs if number(r)=='pl']
        for p in pl:
            f=plain(p['reading_form'])
            suffix='-eh/-eɦ' if f.endswith(('eh','eɦ')) else '-e' if f.endswith('e') else '-i' if f.endswith('i') else 'other'
            pairs.append(dict(gloss=g,plural=p['reading_form'],suffix=suffix,plural_stress_from_right=p['stress_from_right'],plural_outcome=p['modern_outcome'],singulars=[s['reading_form'] for s in sg],singular_stress=[s['stress_from_right'] for s in sg],singular_ids=[s['id'] for s in sg],plural_id=p['id'],family_ids=sorted({r['research_family_id'] for r in [p]+sg if r['research_family_id']}),plural_description=p['description']))
    write_tsv('dras-plural-candidates.tsv',pairs)
    print('records',len(rows),'number',dict(Counter(number(r) for r in rows)),'plural candidates',len(pairs),'paired',sum(bool(p['singulars']) for p in pairs))
    for i,p in enumerate(pairs):print(i,json.dumps(p,ensure_ascii=False))
if __name__=='__main__':main()
