#!/usr/bin/env python3
"""Complete lexical screen for Kui/Pengo velar-labial cluster spellings.

Screening observes either order; outcomes and morphological inputs are adjudicated
later. This inventory is not a denominator of reconstructed eligible stems.
"""
import csv,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
rx=re.compile(r'(?:[kg][\s-]*[pb]|[pb][\s-]*[kg])')
rows=[]
with (P/'corpus.tsv').open() as f:
    for r in csv.DictReader(f,delimiter='\t'):
        if r['Language_ID'] not in ['Kui','Kuwi','Pengo','Manda']:continue
        if rx.search(r['Form']+' '+r['Gloss']):rows.append(r)
with (P/'stop-cluster-screen.tsv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
for r in sorted(rows,key=lambda r:(r['Language_ID'],r['Research_Group'],r['Form'])):
    print(r['Research_Group'],r['Language_ID'],r['ID'],r['Form'],repr(r['Gloss']),r['Source'])
print('RECORDS',len(rows),'GROUPS',len(set(r['Research_Group'] for r in rows)))
