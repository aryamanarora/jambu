#!/usr/bin/env python3
"""Exact reviewed, screened-only and remaining scope, with membership exports."""
import csv,json,re
from collections import Counter
from pathlib import Path
from annotations import CASES
from quantify_families import read,write,joined,HERE
def main():
 seen={r['entry_id'] for r in CASES};fs=read('families.tsv');queue=read('independent-input-queue.tsv')
 with (HERE.parent/'cluster-triage.tsv').open() as f:prior=list(csv.DictReader(f,delimiter='\t'))
 screen={r['Entry_ID'] for r in queue};prior_ids={r['Entry_ID'] for r in prior}
 dedr=[r for r in fs if re.fullmatch(r'd\d+[a-z]?',r['Group_ID'])]
 pending=[]
 for r in dedr:
  if r['Group_ID'] in seen:continue
  pending.append(r|{'Scope':'not-in-current-full-casebook','In_Independent_Input_Screen':int(r['Group_ID'] in screen),
   'In_Prior_Cluster_Triage':int(r['Group_ID'] in prior_ids),
   'In_Local_Stop_Process_Audit':int(r['Group_ID'] in {x['Entry_ID'] for x in read('stop-cluster-annotations.tsv')})})
 write('remaining-dedr-groups.tsv',pending)
 write('prior-cluster-review-coverage.tsv',[r|{'Current_Full_Case_Review':int(r['Entry_ID'] in seen),
  'Scope':'Prior 2026-09-08 triage preserved; only current-full flag identifies this investigation’s complete casebook review.'} for r in prior])
 write('pending-input-screen.tsv',[r for r in queue if r['Entry_ID'] not in seen])
 totals={'all_dedr_groups':len(dedr),'current_reviewed_entries':len(seen),'remaining_dedr_groups':len(pending),
  'telugu_bearing_dedr_groups':sum(int(r['N_Telugu_Records'])>0 for r in dedr),
  'reviewed_telugu_bearing_dedr_groups':sum(int(r['N_Telugu_Records'])>0 and r['Group_ID'] in seen for r in dedr),
  'remaining_telugu_bearing_dedr_groups':sum(int(r['N_Telugu_Records'])>0 for r in pending),
  'independent_input_screen_groups':len(screen),'input_screen_reviewed_groups':len(screen&seen),
  'input_screen_pending_groups':len(screen-seen),'prior_cluster_groups':len(prior),
  'prior_cluster_now_fully_reviewed':len(prior_ids&seen),'prior_cluster_not_currently_fully_reviewed':len(prior_ids-seen),
  'prior_cluster_pending_ids':sorted(prior_ids-seen),
  'input_screen_classes':{s:{'groups':len({r['Entry_ID'] for r in queue if r['Screen']==s}),
    'reviewed':len({r['Entry_ID'] for r in queue if r['Screen']==s and r['Entry_ID'] in seen})} for s in sorted({r['Screen'] for r in queue})},
  'scope_warning':'Screen matches are modern-form candidates, not verified reconstructed-input eligibility. Unreviewed groups cannot be assigned negative outcomes.'}
 (HERE/'coverage-results.json').write_text(json.dumps(totals,ensure_ascii=False,indent=2)+'\n');print(json.dumps(totals,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
