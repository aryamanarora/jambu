#!/usr/bin/env python3
"""Prioritize independent input-shaped comparisons; Telugu outcomes never select cases.

This is a deliberately inclusive review queue, not a reconstruction or denominator.
It preserves candidate evidence and the exact reason each group entered the screen.
"""
import csv
import json
import re
from pathlib import Path
from annotations import CASES
from build_corpus import norm

HERE=Path(__file__).resolve().parent
seen={c['entry_id'] for c in CASES}
with (HERE/'languages.tsv').open() as f:languages={r['ID']:r for r in csv.DictReader(f,delimiter='\t')}
proto={k for k,r in languages.items() if r['Name'].startswith('Proto-')}|{'Drav'}
patterns={
 'vowel-initial-short-nonnasal-apical':r'^[aeiou][rṟlḷẓḍṭṯṛ]',
 'consonant-initial-short-nonnasal-apical':r'^[kgcjśsṣtdṭḍpbmvywhnñṇ][aeiou][rṟlḷẓḍṭṯṛ]',
 'long-vowel-apical-control':r'^(?:[kgcjśsṣtdṭḍpbmvywhnñṇ])?[āēīōū][rṟlḷẓḍṭṯṛ]',
 'vowel-initial-nasal-control':r'^[aeiou][nṇ]',
}
rows=[]
with (HERE/'groups.jsonl').open() as f:
 for line in f:
    g=json.loads(line)
    if not re.fullmatch(r'd\d+[a-z]?',g['id']):continue
    rs=g['records']
    eligible=[r for r in rs if r['Language_ID'] in languages and r['Language_ID'] not in {'Telugu','OTelugu'} and str(r['Borrowed_In_Path'])=='0' and (r['Language_ID'] not in proto or '*' in r['Form'])]
    for name,pat in patterns.items():
        evidence=[r for r in eligible if re.match(pat,norm(r['Form']).lower().lstrip('*').replace('-',''))]
        if not evidence:continue
        rows.append({'Entry_ID':g['id'],'Screen':name,'Has_Telugu':int(any(r['Language_ID'] in {'Telugu','OTelugu'} for r in rs)),
          'Review_Status':'reviewed' if g['id'] in seen else 'pending','Displayed_Input':g['head']['Form'],
          'Evidence_IDs':';'.join(r['ID'] for r in evidence),
          'Independent_Screen_Forms':' | '.join(dict.fromkeys(r['Language_ID']+': '+r['Form'] for r in evidence))})
rows.sort(key=lambda r:(r['Screen'],int(re.search(r'\d+',r['Entry_ID'])[0])))
assert rows, 'Empty input screen: check source field types before interpreting absence'
with (HERE/'independent-input-queue.tsv').open('w') as f:
 w=csv.DictWriter(f,list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
for name in patterns:
 selected=[r for r in rows if r['Screen']==name]
 print(name,'groups',len(selected),'Telugu-bearing',sum(r['Has_Telugu'] for r in selected),'reviewed',sum(r['Review_Status']=='reviewed' for r in selected))
 if name.startswith('vowel-initial-short'):
    for r in selected:
        if r['Has_Telugu'] and r['Review_Status']=='pending':print(r['Entry_ID'],r['Displayed_Input'],r['Independent_Screen_Forms'][:150])
