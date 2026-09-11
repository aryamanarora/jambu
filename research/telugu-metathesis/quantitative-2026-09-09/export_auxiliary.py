#!/usr/bin/env python3
"""Export and validate source, chronology and candidate annotations."""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
from historical_evidence import HISTORY
from kunha_comparisons import KUNHA
from kondh_paradigms import PARADIGMS
from unlinked_candidates import CANDIDATES
P=Path(__file__).resolve().parent
def read(n):
 with (P/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rs):
 with (P/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t');w.writeheader();w.writerows(rs)
def main():
 corpus={r['ID']:r for r in read('corpus.tsv')};cited=read('cited-evidence.tsv');byentry=defaultdict(list)
 for r in cited:byentry[r['Entry_ID']].append(r)
 errors=[];cands=[];hist=[]
 for r in CANDIDATES:
  if r['Form_ID'] not in corpus:errors.append('Missing candidate '+r['Form_ID']);continue
  raw=corpus[r['Form_ID']]
  cands.append(r|{'Language_ID':raw['Language_ID'],'Source_Form':raw['Form'],'Source_Gloss':raw['Gloss'],
    'Source':raw['Source'],'Dialect_and_Tags':raw['Tags'],'Current_Research_Group':raw['Research_Group'],
    'Already_In_Reviewed_Evidence':int(r['Form_ID'] in {x['Form_ID'] for x in cited})})
 for r in HISTORY:
  hist.append(r|{'Comparative_Case_Evidence_IDs':';'.join(sorted({x['Form_ID'] for x in byentry[r['Entry_ID']]})),
    'Link_Scope':'IDs are the comparative etymon panel, not a claim that the historical token itself is already a database record.'})
 for r in PARADIGMS:
  for fid in r['Linked_Database_IDs'].split(';'):
   if fid and fid not in corpus:errors.append('Missing paradigm link '+fid)
 if errors:
  (P/'auxiliary-errors.json').write_text(json.dumps(errors,indent=2));raise SystemExit(errors)
 write('unlinked-candidate-annotations.tsv',cands);write('historical-evidence.tsv',hist)
 write('kunha-published-pair-audit.tsv',KUNHA);write('kondh-source-paradigms.tsv',PARADIGMS)
 # Counts refer to published examples, not a random language-wide denominator.
 kunha_counts=[{'Source':'Kujur and Dash2025 pp.118–119','Category':c,'N_Published_Pairs':n,
   'Denominator_All_Published_Pairs':len(KUNHA),'Proportion':round(n/len(KUNHA),6)} for c,n in sorted(Counter(r['Analysis_Category'] for r in KUNHA).items())]
 write('kunha-published-pair-counts.tsv',kunha_counts)
 stats={'historical_observations':len(hist),'unlinked_records_assessed':len(cands),'kunha_published_pairs':len(KUNHA),
  'source_paradigms':len(PARADIGMS),'errors':errors,
  'scope':'Auxiliary data are not pooled with primary root frequencies. Source paradigms overlap one another and database etyma; never sum them as independent roots.'}
 (P/'auxiliary-results.json').write_text(json.dumps(stats,indent=2)+'\n');(P/'auxiliary-errors.json').write_text('[]\n')
 print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
