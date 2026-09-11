#!/usr/bin/env python3
"""Explicit process-specific denominators, never pooled with apical root counts."""
from collections import defaultdict,Counter
from quantify_families import read,write,joined
def main():
 rows=read('stop-cluster-annotations.tsv');out=[];members=[]
 for lang in ['Kui','Kuwi','Pengo','Manda']:
  fs=defaultdict(list)
  for r in rows:
   if r['Language_ID']==lang and r['Input_Class']=='verbal-velar+labial-formative':fs[r['Family_ID']].append(r)
  c=Counter()
  for f,rs in fs.items():
   flags={r['Observed_Outcome'] for r in rs}
   state='D' if flags=={'D'} else 'possible-R' if flags=={'R?'} else 'mixed-or-uncertain'
   c[state]+=1;members.append(dict(Language_ID=lang,Family_ID=f,Observed_State=state,Record_IDs=joined(r['Record_ID'] for r in rs)))
  out.append(dict(Language_ID=lang,N_Input_Supported_Families=len(fs),N_D=c['D'],N_Possible_R=c['possible-R'],
   N_Mixed_or_Uncertain=c['mixed-or-uncertain'],D_Over_All_Input_Supported=f"{c['D']}/{len(fs)}",
   Proportion=round(c['D']/len(fs),6) if fs else '',
   Caveat='Selected literal cluster screen. Possible R remains uncertain; absence of exceptions in printed derived forms does not prove language-wide exceptionlessness.'))
 write('stop-rule-counts.tsv',out);write('stop-rule-count-membership.tsv',members)
 rs=read('kondh-source-paradigms.tsv');groups=defaultdict(list);out=[];members=[]
 for r in rs:groups[(r['Source'],r['Language_ID'],r['Input_Class'])].append(r)
 for (source,lang,cl),rr in groups.items():
  counts=Counter(r['Observed_Order'] for r in rr)
  for outcome,n in sorted(counts.items()):
   ids=[r['Observation_ID'] for r in rr if r['Observed_Order']==outcome]
   out.append(dict(Source=source,Language_ID=lang,Input_Class=cl,Observed_Order=outcome,N_Paradigms=n,
    Denominator_Class=len(rr),Fraction=f'{n}/{len(rr)}',Proportion=round(n/len(rr),6),Observation_IDs=joined(ids),
    Caveat='Published paradigms; overlapping sources must not be summed as independent etyma.'))
 write('source-paradigm-counts.tsv',out)
 print('Stop input families and selected source-paradigm counts exported.')
if __name__=='__main__':main()
