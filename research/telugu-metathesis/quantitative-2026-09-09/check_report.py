#!/usr/bin/env python3
"""Check local links/anchors and trace every headline statistic to frozen outputs."""
import csv,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n):
 with (P/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
text=(P/'report.md').read_text();errors=[];checked=[]
for document in ['report.md','README.md','SOURCE_ACCESS.md']:
 for target in re.findall(r'\]\(([^)]+)\)',(P/document).read_text()):
  if target.startswith(('https:','http:')):continue
  path,_,anchor=target.partition('#');p=P/path
  if not p.exists():errors.append(document+': missing target '+target);continue
  if anchor and 'id="'+anchor+'"' not in p.read_text():errors.append(document+': missing anchor '+target)
  checked.append(document+' -> '+target)
rs=read('family-class-counts.tsv');te=next(r for r in rs if r['Partition']=='primary' and r['Axis']=='ALL' and r['Language_ID']=='Telugu');sen=next(r for r in rs if r['Partition']=='sensitivity' and r['Axis']=='ALL' and r['Language_ID']=='Telugu')
stats=[]
def stat(label,val,source,locator):stats.append({'Statistic':label,'Value':str(val),'Source_File':source,'Selection':locator})
for label,key in [('Telugu D-bearing families','N_D_Bearing'),('Telugu D/R denominator','N_DR_Informative'),('Telugu reviewed-attested denominator','N_Attested_Reviewed'),('Telugu mixed families','N_Mixed_DR')]:stat(label,te[key],'family-class-counts.tsv','primary / ALL / Telugu / '+key)
for label,key in [('Telugu sensitivity D','N_D_Bearing'),('Telugu sensitivity DR','N_DR_Informative'),('Telugu sensitivity reviewed','N_Attested_Reviewed')]:stat(label,sen[key],'family-class-counts.tsv','sensitivity / ALL / Telugu / '+key)
for file in ['quantitative-results.json','analysis-progress.json','coverage-results.json','auxiliary-results.json']:
 for key,value in json.loads((P/file).read_text()).items():
  if isinstance(value,int):stat(key,value,file,key)
for key,value in json.loads((P/'quantitative-results.json').read_text())['broad_obligatory_test'].items():stat(key,value,'quantitative-results.json','broad_obligatory_test / '+key)
for key,value in json.loads((P/'input-manifest.json').read_text()).items():
 if isinstance(value,int):stat(key,value,'input-manifest.json',key)
for r in read('formation-class-counts.tsv'):
 if r['Language_ID']=='Telugu' and r['Input_Tier'] in {'full','cluster'} and int(r['N_Strict_Quantity_Denominator']):stat('Telugu quantity: '+r['Prediction'],r['Match_Only_Over_Tested'],'formation-class-counts.tsv','Telugu / '+r['Input_Tier']+' / '+r['Prediction'])
for r in rs:
 if r['Partition']=='primary' and r['Language_ID']=='Telugu' and r['Axis']=='Domain_Following_Vowel':stat(r['Class'],r['D_Over_DR'],'family-class-counts.tsv','primary / Domain_Following_Vowel / Telugu / '+r['Class'])
for r in rs:
 if r['Partition']=='primary' and r['Axis']=='ALL':
  for key in ['N_D_Bearing','N_DR_Informative','N_Attested_Reviewed','N_Mixed_DR']:
   stat(r['Language_ID']+' '+key,r[key],'family-class-counts.tsv','primary / ALL / '+r['Language_ID']+' / '+key)
for r in read('pairwise-language-counts.tsv'):
 if r['Partition']=='primary' and r['Input_Domain']=='all-reviewed-inputs' and 'Telugu' in {r['Language_A'],r['Language_B']}:
  for key,value in r.items():
   if key.startswith('N_'):stat(r['Language_A']+' / '+r['Language_B']+' / '+key,value,'pairwise-language-counts.tsv','primary / all-reviewed-inputs / '+r['Language_A']+' / '+r['Language_B']+' / '+key)
for r in read('lowering-source-counts.tsv'):
 for key in ['N_K80_Listed_Lowered','N_Selected_Positive_Examples','Listed_Lowered_Over_Selected','Known_Attestation_Adjusted_Denominator','Lowered_Over_Explicitly_Nonmissing']:
  if r[key]:stat('K80 '+r['Language_ID']+' '+key,r[key],'lowering-source-counts.tsv',r['Language_ID']+' / '+key)
for r in read('stop-cluster-counts.tsv'):
 for key in ['N_Records','N_Families']:stat(r['Language_ID']+' / '+r['Disposition']+' / '+key,r[key],'stop-cluster-counts.tsv',r['Language_ID']+' / '+r['Disposition']+' / '+key)
stop=read('stop-cluster-annotations.tsv')
stat('Complete stop screen records',len(stop),'stop-cluster-annotations.tsv','all rows')
stat('Complete stop screen groups',len({r['Entry_ID'] for r in stop}),'stop-cluster-annotations.tsv','distinct Entry_ID')
parts=read('family-partitions.tsv')
stat('Primary family mergers',len({r['Primary_Family_ID'] for r in parts if r['Entry_ID']!=r['Primary_Family_ID']}),'family-partitions.tsv','distinct nonidentity Primary_Family_ID')
stat('Sensitivity merger proposals',len(read('family-merge-sensitivity-proposals.tsv')),'family-merge-sensitivity-proposals.tsv','all rows')
for r in read('stop-rule-counts.tsv'):
 for key in ['N_Input_Supported_Families','N_D','N_Possible_R','D_Over_All_Input_Supported']:
  stat(r['Language_ID']+' / '+key,r[key],'stop-rule-counts.tsv',r['Language_ID']+' / '+key)
with (P/'report-statistics.tsv').open('w') as f:
 w=csv.DictWriter(f,list(stats[0]),delimiter='\t');w.writeheader();w.writerows(stats)
for phrase in [te['N_D_Bearing']+' of '+te['N_DR_Informative'],te['N_D_Bearing']+' of '+te['N_Attested_Reviewed'],
               f"{100*int(te['N_D_Bearing'])/int(te['N_DR_Informative']):.1f}%",f"{100*int(te['N_D_Bearing'])/int(te['N_Attested_Reviewed']):.1f}%",
               sen['D_Over_DR'],sen['D_Over_Attested_Reviewed'],f"{100*int(sen['N_D_Bearing'])/int(sen['N_DR_Informative']):.1f}%",f"{100*int(sen['N_D_Bearing'])/int(sen['N_Attested_Reviewed']):.1f}%"]:
 if phrase not in text:errors.append('Missing headline statistic '+phrase)
for file in ['report.md','report-template.md']:
 if 'TODO' in (P/file).read_text():errors.append(file+' unfinished marker')
out={'status':'PASS' if not errors else 'FAIL','documents_checked':['report.md','README.md','SOURCE_ACCESS.md'],'local_links_checked':len(checked),'statistics_index_rows':len(stats),'errors':errors,'scope':'Local artifact linkage and recorded statistical provenance; citations and linguistic interpretation require scholarly reading.'}
(P/'report-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if errors:raise SystemExit(1)
