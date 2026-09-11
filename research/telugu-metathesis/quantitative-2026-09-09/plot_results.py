#!/usr/bin/env python3
"""Standalone scientific figure; all bar values copied from family count outputs."""
import csv,os
from pathlib import Path
P=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/telugu-metathesis-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
with (P/'family-class-counts.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
domains=[('short-vowel-initial-singleton-apical','Short V–apical'),('short-C-initial-r-rhotics-retroflex-approximant','Short CVr / CVẓ'),('short-C-initial-other-apical','Short CVC: other apicals'),('short-strong-or-mixed-structure','Short: strong / mixed structure'),('long-apical-input','Long apical input'),('mixed-or-uncertain-quantity','Mixed / uncertain input quantity')]
rr=[next(r for r in rows if r['Partition']=='primary' and r['Axis']=='Domain' and r['Language_ID']=='Telugu' and r['Class']==d) for d,_ in domains]
series=[('D only','N_D_No_R','#27725b'),('D + retained','N_Mixed_DR','#9b67a2'),('Retained, no D','N_R_No_D','#a8b4bc'),('Other','N_Other_No_DR','#d9b666'),('Unresolved','N_Uncertain_No_DR','#e1c9a3'),('Other + unresolved','N_Other_And_Uncertain_No_DR','#b58a58'),('Loan only','N_Borrowed_Only','#6088b3')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,(ax,aq)=plt.subplots(2,1,figsize=(12,9),gridspec_kw={'height_ratios':[2.1,1]});fig.patch.set_facecolor('#faf9f5')
left=[0.0]*len(rr)
for title,key,color in series:
 vals=[100*int(r[key])/int(r['N_Attested_Reviewed']) for r in rr]
 ax.barh(range(len(rr)),vals,left=left,label=title,color=color,height=.7)
 left=[a+b for a,b in zip(left,vals)]
ax.set_yticks(range(len(rr)),[lab+'  (n='+r['N_Attested_Reviewed']+')' for (_,lab),r in zip(domains,rr)]);ax.invert_yaxis();ax.set_xlim(0,103);ax.set_xlabel('Percent of attested, reviewed families in each input class')
ax.set_title('Telugu: input classes contain both displaced and retained families',loc='left',pad=15,fontweight='bold')
ax.legend(ncol=4,loc='lower left',bbox_to_anchor=(0,-.37),frameon=False,fontsize=9)
with (P/'formation-class-counts.tsv').open() as f:fr=list(csv.DictReader(f,delimiter='\t'))
spec=[('full','long-if-displaced','Full input: low V₂ or equal vowels'),('full','short-if-displaced','Full input: different high V₂'),('cluster','short-from-consonantal-input','Independent consonantal input')]
for i,(tier,pred,label) in enumerate(spec):
 r=next(r for r in fr if r['Language_ID']=='Telugu' and r['Input_Tier']==tier and r['Prediction']==pred)
 n=int(r['N_Strict_Quantity_Denominator']);m=int(r['N_Quantity_Match_Only']);aq.barh(i,100*m/n,color='#27725b',height=.65);aq.barh(i,100*(n-m)/n,left=100*m/n,color='#bd7560',height=.65);aq.text(102,i,f'{m}/{n}',va='center',fontweight='bold')
aq.set_yticks(range(3),[x[2] for x in spec]);aq.invert_yaxis();aq.set_xlim(0,113);aq.set_xlabel('Percent matching the predicted surface vowel quantity');aq.set_title('Quantity prediction, conditional on displacement',loc='left',pad=12,fontweight='bold')
fig.text(.03,.018,'Targeted review, not a population sample. Green = match; rust = additional history required.\nFormation classes can share a root; do not sum their denominators. Source: family-class-counts.tsv and formation-class-counts.tsv.',fontsize=9,color='#4c5960')
fig.subplots_adjust(left=.34,right=.94,top=.94,bottom=.12,hspace=.95)
fig.savefig(P/'conditioning.png',dpi=180,facecolor=fig.get_facecolor());fig.savefig(P/'conditioning.svg',facecolor=fig.get_facecolor())
print('Wrote conditioning.png and conditioning.svg')
