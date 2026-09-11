"""Inspect candidate reduction pairs; no outcome inferred from matching alone."""
import csv,json,re,unicodedata
from pathlib import Path
from collections import defaultdict
P=Path(__file__).resolve().parent;S=P.parent/'quantitative-2026-09-09'
def read(n):
 with (S/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
A={r['entry_id']:r for r in read('etymon-annotations.tsv')}
L={(r['Family_ID'],r['Language_ID']):r for r in read('family-language-outcomes.tsv') if r['Partition']=='primary'}
E=defaultdict(list)
for r in read('cited-evidence.tsv'):
 if r['Language_ID']=='Telugu':E[r['Family_ID']].append(r)
out=[]
for fam,rs in E.items():
 if L[(fam,'Telugu')]['Has_D']!='1':continue
 words=defaultdict(list)
 for r in rs:words[unicodedata.normalize('NFC',r['Evidence_Form'])].append(r)
 for w in words:
  if not re.match(r'^[kgctdṯṭḍpbmsv][rṟṛlḷẓ][aeiouāēīōū]',w):continue
  for mode,short in [('lose-apical',w[0]+w[2:]),('lose-first',w[1:])]:
   if short in words:
    eid=words[w][0]['Entry_ID'];a=A[eid]
    out.append(dict(family=fam,entry=eid,concept=a['concept'],cluster=w,reduced=short,operation=mode,
                    cluster_flags=sorted({r['Observed_Outcome'] for r in words[w]}),reduced_flags=sorted({r['Observed_Outcome'] for r in words[short]}),
                    cluster_ids=[r['Form_ID'] for r in words[w]],reduced_ids=[r['Form_ID'] for r in words[short]],
                    derivation=a['derivation'],exception=a['exception_notes']))
(P/'reduction-screen.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('SCREEN',len(out),'pairs',len({r['family'] for r in out}),'families')
for r in out:
 print(r['entry'],r['concept'],r['cluster'],'→',r['reduced'],r['operation'],r['cluster_flags'],r['reduced_flags'])
print('\nREFERENCES')
for r in read('references.tsv'):
 if any(s in r['ID'].lower() for s in ['krish','winfield','sastri','subrah','hume','dedr']):print(r['ID'],r['Short'])
