from quantify_families import read
from annotations import CASES
classes={r['Entry_ID']:r for r in read('input-class-membership.tsv')}
for r in read('family-language-outcomes.tsv'):
 if r['Partition']=='primary' and r['Language_ID']=='Telugu' and r['Has_D']=='1':
  if any(classes[e]['Domain'] in {'nonapical-or-uncertain-input','long-apical-input','short-strong-or-mixed-structure'} for e in r['Entry_IDs'].split(';')):print('RESIDUAL',r['Entry_IDs'],r['Evidence_Forms'])
for r in read('formation-count-membership.tsv'):
 if r['Language_ID']=='Telugu' and r['Category']=='counterexample':print('QUANTITY_EXCEPTION',r['Family_ID'],r['Formation_IDs'])
for r in read('family-class-counts.tsv'):
 if r['Partition']=='primary' and r['Axis']=='Domain_Apical_Group' and r['Language_ID']=='Telugu' and r['Class'].startswith('short-vowel-initial'):print('VC_CLASS',r['Class'],r['D_Over_DR'],r['N_Mixed_DR'],r['D_Over_Attested_Reviewed'])
