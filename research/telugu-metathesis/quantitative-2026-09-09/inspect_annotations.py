"""Audit input classifications without consulting observed outcomes."""
import csv
from collections import Counter
from pathlib import Path
from annotations import CASES
P=Path(__file__).resolve().parent
fields=['entry_id','family_id','concept','reconstruction','c1','v1','v1_quantity','c2','c2_structure','v2','structure','eligibility','input_confidence']
with (P/'input-class-audit.tsv').open('w') as f:
    w=csv.DictWriter(f,fields,delimiter='\t',extrasaction='ignore');w.writeheader()
    w.writerows(sorted(CASES,key=lambda c:int(c['entry_id'][1:])))
for field in ['c1','v1_quantity','c2','c2_structure','v2']:
    print('\nFIELD',field)
    for value,n in Counter(c[field] for c in CASES).most_common():print(n,repr(value))
print('Nonidentity families',[(c['entry_id'],c['family_id']) for c in CASES if c['entry_id']!=c['family_id']])
