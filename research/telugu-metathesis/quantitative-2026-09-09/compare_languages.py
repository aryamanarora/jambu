#!/usr/bin/env python3
"""Compare outcomes only on common independently input-classified reviewed families."""
from collections import defaultdict,Counter
from itertools import combinations
from quantify_families import read,write,joined

def main():
 inputs=read('family-input-classes.tsv');out=read('family-language-outcomes.tsv')
 lookup={(r['Partition'],r['Family_ID'],r['Language_ID']):r for r in out}
 langs=sorted({r['Language_ID'] for r in out});counts=[];members=[]
 for part in ['primary','sensitivity']:
  fs=[r for r in inputs if r['Partition']==part]
  domains=['all-reviewed-inputs']+sorted({r['Domain'] for r in fs})
  for domain in domains:
   sub=fs if domain=='all-reviewed-inputs' else [r for r in fs if r['Domain']==domain]
   for a,b in combinations(langs,2):
    c=Counter()
    for f in sub:
     x=lookup[(part,f['Family_ID'],a)];y=lookup[(part,f['Family_ID'],b)]
     def state(r):
      if r['Reviewed']!='1':return 'missing-or-unreviewed'
      d=r['Has_D']=='1';ret=r['Has_R']=='1'
      return 'mixed' if d and ret else 'D' if d else 'R' if ret else 'other-or-uncertain'
     u,v=state(x),state(y)
     category=u+' / '+v;c[category]+=1
     if u in {'D','R','mixed'} and v in {'D','R','mixed'}:
      members.append({'Partition':part,'Input_Domain':domain,'Language_A':a,'Language_B':b,'Family_ID':f['Family_ID'],
       'Entry_IDs':f['Entry_IDs'],'Outcome_A':u,'Outcome_B':v,'Evidence_A':x['Evidence_IDs'],'Evidence_B':y['Evidence_IDs']})
    decisive=sum(c[u+' / '+v] for u in ['D','R','mixed'] for v in ['D','R','mixed'])
    if not decisive:continue
    dd=sum(c[u+' / '+v] for u in ['D','mixed'] for v in ['D','mixed'])
    adbr=sum(c[u+' / R'] for u in ['D','mixed']);ardb=sum(c['R / '+v] for v in ['D','mixed'])
    rr=c['R / R'];mixed=sum(n for k,n in c.items() if 'mixed' in k and 'missing-or-unreviewed' not in k and 'other-or-uncertain' not in k)
    counts.append({'Partition':part,'Input_Domain':domain,'Language_A':a,'Language_B':b,
     'N_Input_Families':len(sub),'N_Common_DR_Informative':decisive,'N_Both_D_Bearing':dd,
     'N_A_D_B_R':adbr,'N_A_R_B_D':ardb,'N_Both_R_No_D':rr,'N_Common_With_Mixed_Cell':mixed,
     'Both_D_Over_Common':f'{dd}/{decisive}','Both_D_Proportion':round(dd/decisive,6),
     'N_Excluded_Not_Common_Informative':len(sub)-decisive,
     'Caution':'Mixed cells remain identifiable; D includes supported displacement-family histories. Shared outcome does not establish one inherited event.'})
 write('pairwise-language-counts.tsv',counts);write('pairwise-language-membership.tsv',members)
 print('Pairwise rows',len(counts),'memberships',len(members))
if __name__=='__main__':main()
