import csv, json
from pathlib import Path
P=Path(__file__).resolve().parent; S=P.parent/'quantitative-2026-09-09'
def read(n):
 with (S/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
A={r['entry_id']:r for r in read('etymon-annotations.tsv')}
L={(r['Family_ID'],r['Language_ID']):r for r in read('family-language-outcomes.tsv') if r['Partition']=='primary'}
F=read('formation-tests.tsv'); E=read('cited-evidence.tsv'); T=read('stop-cluster-annotations.tsv')
groups={'controls':[229,472,490,240,61,84,89,247,249,203], 'quantity':[63,79,228,295,651,277,4866,4728,5372,4005], 'compare':[63,474,1787,4711,240,282,305,480,3259,4760], 'kui':[228,1080,1628,2654,5200,4760,520,1851,3439,3514], 'lookalikes':[3364,1898,3411,5368,5250,5555,2090,4194,5087,4608]}
for group,ns in groups.items():
 with (P/f'inspect-{group}.txt').open('w') as out:
  for n in ns:
   e='d'+str(n);a=A.get(e,{'family_id':e});fam=a['family_id'];print('\n',e,json.dumps(a,ensure_ascii=False),file=out)
   if group=='kui':
    for r in T:
     if r['Entry_ID']==e and r['Language_ID']=='Kui':print(json.dumps(r,ensure_ascii=False),file=out)
   elif group=='quantity':
    for r in F:
     if r['Entry_ID']==e and r['Language_ID']=='Telugu':print(json.dumps({k:r[k] for k in ['Formation_ID','Reconstructed_Input','Input_Tier','Prediction','Evidence_Forms','Formation_Explanation']},ensure_ascii=False),file=out)
   else:
    for lang in ['Telugu','Tamil','Kannada','Kui','Kuwi','Gondi']:
     r=L.get((fam,lang))
     if r:print(lang,r['Outcome_State'],r['Evidence_Forms'],file=out)
   for r in E:
    if r['Entry_ID']==e and r['Language_ID']=='Telugu':print(r['Evidence_Form'],r['Form_ID'],r['Observed_Outcome'],file=out)
print('Wrote five inspection files')
