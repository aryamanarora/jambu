#!/usr/bin/env python3
"""Independent arithmetic and completeness checks on research outputs."""
import csv,json,hashlib,re
from pathlib import Path
from collections import defaultdict,Counter
P=Path(__file__).resolve().parent
def rows(n):
 with (P/n).open() as f:yield from csv.DictReader(f,delimiter='\t')
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
counts={tuple(r[x] for x in ['Partition','Axis','Class','Language_ID']):r for r in rows('family-class-counts.tsv')}
summed=defaultdict(Counter);seen=set()
for r in rows('family-count-membership.tsv'):
 key=tuple(r[x] for x in ['Partition','Axis','Class','Language_ID']);uniq=key+(r['Family_ID'],)
 check(uniq not in seen,'Repeated membership '+str(uniq));seen.add(uniq)
 cc=summed[key];cc['frame']+=1;cc['D']+=int(r['In_D_Numerator']);cc['DR']+=int(r['In_DR_Denominator']);cc['reviewed']+=int(r['In_Attested_Reviewed_Denominator']);cc[r['Outcome_State']]+=1
for k,r in counts.items():
 s=summed[k]
 for a,b in [('frame','N_Reviewed_Frame_Families'),('D','N_D_Bearing'),('DR','N_DR_Informative'),('reviewed','N_Attested_Reviewed'),('missing','N_Missing'),('not-reviewed','N_Attested_Unreviewed'),('mixed','N_Mixed_DR'),('D-bearing-no-R','N_D_No_R'),('R-bearing-no-D','N_R_No_D'),('other-no-DR','N_Other_No_DR'),('uncertain-no-DR','N_Uncertain_No_DR'),('other-and-uncertain','N_Other_And_Uncertain_No_DR'),('borrowed-only','N_Borrowed_Only')]:check(s[a]==int(r[b]),str(k)+' '+b)
 check(r['D_Over_DR']==f"{s['D']}/{s['DR']}",str(k)+' ratio DR')
 check(r['D_Over_Attested_Reviewed']==f"{s['D']}/{s['reviewed']}",str(k)+' ratio attested')
 check(s['frame']==s['reviewed']+s['missing']+s['not-reviewed'],str(k)+' exhaustiveness')
fcounts={tuple(r[x] for x in ['Language_ID','Input_Tier','Prediction']):r for r in rows('formation-class-counts.tsv')};fs=defaultdict(Counter)
for r in rows('formation-count-membership.tsv'):
 cc=fs[tuple(r[x] for x in ['Language_ID','Input_Tier','Prediction'])];cc['N']+=1;cc[r['Category']]+=1;cc['D']+=int(r['Has_D']);cc['R']+=int(r['Has_R'])
for k,r in fcounts.items():
 s=fs[k]
 for a,b in [('N','N_Families'),('D','N_D_Bearing'),('R','N_R_Bearing'),('match','N_Quantity_Match_Only'),('counterexample','N_Quantity_Counterexample_Only')]:check(s[a]==int(r[b]),str(k)+' '+b)
pair=defaultdict(list)
for r in rows('pairwise-language-membership.tsv'):pair[tuple(r[x] for x in ['Partition','Input_Domain','Language_A','Language_B'])].append(r)
for r in rows('pairwise-language-counts.tsv'):
 k=tuple(r[x] for x in ['Partition','Input_Domain','Language_A','Language_B']);rr=pair[k]
 check(len(rr)==int(r['N_Common_DR_Informative']),str(k)+' pair denominator')
 check(len({x['Family_ID'] for x in rr})==len(rr),str(k)+' pair duplicated family')
ev=list(rows('cited-evidence.tsv'));annotations=list(rows('etymon-annotations.tsv'));entryids={r['entry_id'] for r in annotations}
required=['family_id','concept','reconstruction','c1','v1','v1_quantity','c2','c2_structure','v2','structure','grammatical_category','input_support','input_confidence','direction_argument','derivation','exception_notes','confidence','references','eligibility']
for r in annotations:
 for field in required:check(bool(r[field].strip()),r['entry_id']+' missing '+field)
stop=list(rows('stop-cluster-annotations.tsv'))
for r in stop:
 if r['Disposition']=='source-supported-verbal-input':
  check(bool(re.search(r'[kg]-?[pb]',r['Proposed_Immediate_Input'].replace(' ',''))),r['Record_ID']+' malformed explicitly supported stop input')
check(len(entryids)==409,'409 reviewed entries')
check(all(r['Entry_ID'] in entryids for r in ev),'Evidence entry membership')
check(len({(r['Entry_ID'],r['Language_ID'],r['Evidence_Form'],r['Form_ID']) for r in ev})==len(ev),'Duplicate evidence links')
progress=json.loads((P/'analysis-progress.json').read_text());check(len(ev)==progress['evidence_record_links'],'Evidence total')
for file in ['annotation-errors.json','formation-errors.json','auxiliary-errors.json']:check(json.loads((P/file).read_text())==[],file)
check(json.loads((P/'formation-results.json').read_text())['telugu_D_families_not_in_formation_tests']==[],'All Telugu D families covered by formation audit')
coverage=json.loads((P/'coverage-results.json').read_text());check(coverage['prior_cluster_not_currently_fully_reviewed']==0,'All prior cluster candidates reviewed')
check(coverage['current_reviewed_entries']+coverage['remaining_dedr_groups']==coverage['all_dedr_groups'],'Full DEDR coverage arithmetic')
for file in ['casebook.md','casebook.html']:
 content=(P/file).read_text();check(all(('id="'+e+'"') in content for e in entryids),file+' entry anchors')
check(not errors,'All checks')
result={'status':'PASS' if not errors else 'FAIL','family_count_rows_checked':len(counts),'family_memberships_checked':len(seen),'formation_count_rows_checked':len(fcounts),'pairwise_comparison_groups_checked':len(pair),'reviewed_entries':len(entryids),'required_annotation_fields_per_entry':len(required),'stop_screen_records_checked':len(stop),'evidence_links':len(ev),'errors':errors,'scope':'Arithmetic, linkage and appendix completeness checks. These do not mechanically validate linguistic judgments.'}
(P/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,indent=2))
if errors:raise SystemExit(1)
