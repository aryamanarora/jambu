#!/usr/bin/env python3
"""Assemble the final narrative after the recorded analysis freeze.

Only table formatting occurs here; all outcomes and counts are read from audited TSVs.
"""
import csv,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
assert (P/'analysis-freeze.json').exists()
assert json.loads((P/'validation.json').read_text())['status']=='PASS'
def read(n):
 with (P/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def table(rs,fields):
 def m(x):return str(x).replace('|','\\|').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(fields)+' |','| '+' | '.join('---' for _ in fields)+' |',*['| '+' | '.join(m(r[f]) for f in fields)+' |' for r in rs]])
counts=read('family-class-counts.tsv');rr=[]
labels={'long-apical-input':'Long apical','mixed-across-related-entries':'Mixed across merged entries','mixed-or-uncertain-quantity':'Mixed/uncertain quantity','nasal-or-nasal-cluster-input':'Lexical nasal/mixed nasal inputs','nasal-quotative-morphology':'Say/quotative morphology','nonapical-or-uncertain-input':'Nonapical/uncertain input','pronominal-morphology':'Pronominal morphology','short-C-initial-other-apical':'Short CVC: other apicals','short-C-initial-r-rhotics-retroflex-approximant':'Short CVr/CVẓ','short-strong-or-mixed-structure':'Short strong/mixed structure','short-vowel-initial-singleton-apical':'Short V–singleton apical','uncertain-initial-order':'Uncertain initial order'}
for r in counts:
 if r['Partition']=='primary' and r['Axis']=='Domain' and r['Language_ID']=='Telugu':
  rr.append({'Input domain':labels[r['Class']],'Frame':r['N_Reviewed_Frame_Families'],'Reviewed':r['N_Attested_Reviewed'],'Missing':r['N_Missing'],'D only':r['N_D_No_R'],'R only':r['N_R_No_D'],'D+R':r['N_Mixed_DR'],'Other/A/B':sum(int(r[k]) for k in ['N_Other_No_DR','N_Uncertain_No_DR','N_Other_And_Uncertain_No_DR','N_Borrowed_Only']),'D / informative':r['D_Over_DR'],'D / reviewed':r['D_Over_Attested_Reviewed']})
domain=table(rr,list(rr[0]))
ls=[]
for lang in ['Telugu','Gondi','Konda','Kui','Kuwi','Pengo','Manda','Brahui']:
 r=next(r for r in counts if r['Partition']=='primary' and r['Axis']=='ALL' and r['Language_ID']==lang)
 ls.append({'Language':lang.replace('Kuwi','Kuvi'),'Reviewed':r['N_Attested_Reviewed'],'Unreviewed attested':r['N_Attested_Unreviewed'],'Missing':r['N_Missing'],'D only':r['N_D_No_R'],'R only':r['N_R_No_D'],'D+R':r['N_Mixed_DR'],'D / informative':r['D_Over_DR'],'D / reviewed':r['D_Over_Attested_Reviewed']})
language=table(ls,list(ls[0]))
qs=[];fr=read('formation-class-counts.tsv')
for tier,pred,label in [('full','long-if-displaced','Full input; low V₂ or equal vowels → long'),('full','short-if-displaced','Full input; different high V₂ → short'),('cluster','short-from-consonantal-input','Independent consonantal input → short')]:
 r=next(r for r in fr if r['Language_ID']=='Telugu' and r['Input_Tier']==tier and r['Prediction']==pred)
 qs.append({'Conditional prediction':label,'All audited families':r['N_Families'],'Matching / tested D families':r['Match_Only_Over_Tested'],'Proportion':f"{float(r['Match_Only_Proportion']):.1%}",'Surface exceptions':r['N_Quantity_Counterexample_Only'],'Retained evidence, including controls':r['N_R_Bearing']})
quantity=table(qs,list(qs[0]))
ss=[]
for r in read('stop-rule-counts.tsv'):ss.append({'Language':r['Language_ID'].replace('Kuwi','Kuvi'),'Supported input families':r['N_Input_Supported_Families'],'Reversed':r['N_D'],'Possible retained':r['N_Possible_R'],'Reversed / supported':r['D_Over_All_Input_Supported']})
stop=table(ss,list(ss[0]))
text=(P/'report-template.md').read_text()
for key,value in [('DOMAIN_TABLE',domain),('LANGUAGE_TABLE',language),('QUANTITY_TABLE',quantity),('STOP_TABLE',stop)]:text=text.replace('{{'+key+'}}',value)
assert '{{' not in text
for author in ['Krishnamurti','Subrahmanyam','Sastri','Hume','Steever','Monier-Williams']:
 text=re.sub(r'\b'+re.escape(author)+r'(?=\d{4})',author+' ',text)
text=re.sub(r'\b(DEDR|family|etymology|inscription|line|dated)(?=\d)',r'\1 ',text)
text=re.sub(r'\b(notes?|pp?\.)(?=\d)',r'\1 ',text)
text=text.replace('Blevins2009','Blevins 2009').replace('Dash2025','Dash 2025')
(P/'report.md').write_text(text)
print('Report words',len(text.split()),'bytes',len(text.encode()))
