"""Independent arithmetic and publication-shape checks on generated outputs."""
import csv,json,re
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PUB=ROOT/'static/research/telugu-metathesis'
def read(n):
 with (PUB/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
C=json.loads((PUB/'charts.json').read_text());M=read('chart-membership.tsv');E=read('annotated-examples.tsv')
keys=[(r['Chart'],r['View'],r['Row'],r['Family_ID']) for r in M];assert len(keys)==len(set(keys))
counts=Counter((r['Chart'],r['View'],r['Row'],r['Category']) for r in M)
for c in C.values():
 for v in c['views']:
  for row in v['rows']:assert row['values']==[counts[c['id'],v['label'],row['label'],cat] for cat in v['categories']]
assert Counter(r['Section'] for r in E)==dict.fromkeys(C,10)
assert len({(r['Section'],r['Family_ID']) for r in E})==60
telugu=C['languages']['views'][1]['rows'][0]['values'];assert telugu==[66,51,196,17,39,1,33,0]
assert C['languages']['views'][0]['rows'][2]['values']==[38,6,18,29]
assert [r['values'] for r in C['quantity']['views'][0]['rows']]==[[25,8,11],[8,0,4],[21,0,0]]
assert C['inputs']['views'][1]['rows'][0]['values']==[8,10,30,0,6,0,2,0]
assert C['clusters']['views'][0]['rows'][0]['values']==[48,26,22,0,20,0,0,0]
assert C['reduction']['views'][0]['rows'][0]['values']==[41,76]
post=(ROOT/'src/lib/blog/posts/telugu-metathesis.md').read_text();assert len(re.findall(r'^## \d\.',post,re.M))==6
assert len(re.findall(r'^```chart$',post,re.M))==6
result=dict(charts=len(C),chart_memberships=len(M),examples=len(E),unique_section_families=60,arithmetic='passed',approved_claims=6)
(P/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
