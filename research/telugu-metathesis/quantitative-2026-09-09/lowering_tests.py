#!/usr/bin/env python3
"""Audit all 25 numbered K80 examples, without reconstructing V2 from their outcomes.

These are a selected scholarly example set, not a population sample. The source's
reported incidence is distinguished from a fresh determination of vowel history.
"""
import json
from collections import Counter
from annotations import CASES
from quantify_families import read,write,joined,HERE

# Independent support tiers concern the low vowel in the relevant formation.
# 'root-low-only' does NOT prove the suffix of the eastern derivative.
ITEMS=[
 (1,'d1959','unknown','displacement','Kui','Konda ker supports order but supplies no -a.'),
 (2,'d513','root-low-only','displacement','Kui;Kuwi;Manda','Low young formations independent; eastern human cognacy partly reassigned using the rule.'),
 (3,'d495','root-low-only','displacement','Kuwi','Southern -av versus eastern -ak; Kui is missing, not a retained counterexample.'),
 (4,'d2674','full-low-formation','contraction','Kui;Kuwi;Manda','Full cow-ar/ov-ar has independent southern and Gondi support; no apical promotion.'),
 (5,'d516','alternative-cognacy','displacement','Kui;Kuwi','Eastern jāpa also belongs to cāy incline d2456; not two independent observations.'),
 (6,'d1574','root-low-only','displacement','Kui','Southern cilai/kele supports low root derivative; labial eastern formation differs.'),
 (7,'d1818','different-formations','displacement','Kui;Kuwi','Independent low-a tube versus high-i pit; lowered pit and mid-vowel tube must not be interchanged.'),
 (8,'d1859','root-low-only','displacement','Kui','Low-ay cut independent, precise eastern labial derivative is reconstructed.'),
 (9,'d2018','root-low-only','displacement','Kui','Short kiḷai independent beside long kēḷ; Kui -mbu not attested in that comparandum.'),
 (10,'d3259','root-low-only','displacement','Kui','Southern low open formation independent; labial ending and initial cluster loss separate.'),
 (11,'d3754','root-low-only','displacement','Kui','Low moon base independent; eastern -nj versus southern -v requires morphology.'),
 (12,'d4536','unknown','displacement','Kui;Kuwi','Konda por has no independent -a; separation from spread partly uses vowel outcome.'),
 (13,'d3982','unknown','displacement','Kui','Rice has high-u and plural velar comparanda; proposed -a not independently matched.'),
 (14,'d4410','full-low-formation','contraction','Kui','Southern pec-ar/pey-ar supports contraction; eastern dōr has a distinct unresolved history.'),
 (15,'d4968','root-low-only','secondary-apical-displacement','Kui;Kuwi','Southern muc/y-al supplies low-a but not a primary apical input; regional morol needed.'),
 (16,'d4976','full-low-formation','displacement','Kui;Kuwi','Tamil muraṟci/Tulu murajɛ/Gondi moras support low-a cord formation; Kuvi marcu source quantity differs.'),
 (17,'d5082','unknown','displacement','Kui','Independent meẓ-uk is high-u; low-a nasal/labial formation must not be inferred from ē/ā.'),
 (18,'d5153','compound-underdetermined','compound','Kui;Kuwi','Completed+year analysis and exact first member unresolved; bare long year is not eligible.'),
 (19,'d3559','full-low-formation','contraction-control','','Full togal/tukal supports low formation, but Kui/Kuvi retain ō; earlier contraction is a chronology hypothesis.'),
 (20,'d2929','high-vowel-formation','high-vowel-control','','Southern neruppu independent high-u; Kui drē is long, so do not universalize Telugu short-output rule.'),
 (21,'d5159','independent-long-root','long-vowel-control','','Long yĀṯ is independently supported; no lowering or apical displacement.'),
 (22,'d811','different-formations','long-causative-control','','Short eri and long causative/nominal grades must remain separate; not uniformly long input.'),
 (23,'d2237','independent-long-root','long-vowel-control','','Independent long kōl; no lowering.'),
 (24,'d2628','unknown','proposed-exception','','Chironji exact historical vowel/formation needs evidence; mid output cannot establish or disprove an -a input.'),
 (25,'d4418','independent-nonlow-formation','proposed-exception','','Konda peṛen/Gondi peṛe- support e, not -a; ē is not a decisive exception to a low-a rule.'),
]

def main():
 cases={c['entry_id']:c for c in CASES}; ev=read('cited-evidence.tsv')
 rows=[];panels=[]
 for n,e,tier,process,langs,note in ITEMS:
  c=cases[e];source_role='positive' if n<=18 else 'control' if n<=23 else 'proposed-exception'
  rows.append({'K80_Item':n,'Entry_ID':e,'Concept':c['concept'],'Source_Role':source_role,
   'Input_Support_Tier':tier,'Process':process,'K80_Lowering_Languages':langs,
   'Reconstruction_Audit':c['reconstruction'],'Independent_Input_Evidence':c['input_support'],
   'Assessment':note,'Full_Exception_Notes':c['exception_notes'],
   'Reference':'Krishnamurti1980 pp.496–504; DOI10.3765/bls.v6i0.2099'})
  for lang in ['Telugu','Gondi','Konda','Kui','Kuwi','Pengo','Manda']:
   evidence=[r for r in ev if r['Entry_ID']==e and r['Language_ID'] in ({'Telugu','OTelugu'} if lang=='Telugu' else {lang})]
   if e=='d516' and lang in {'Kui','Manda'}:
    evidence += [r for r in ev if r['Entry_ID']=='d2456' and r['Language_ID']==lang]
   panels.append({'K80_Item':n,'Entry_ID':e,'Language_ID':lang,'Input_Support_Tier':tier,
    'K80_Reports_Lowering':int(lang in langs.split(';')) if n<=18 else 'not-positive-example',
    'Reviewed_Evidence_Available':int(bool(evidence)),
    'Evidence_Forms':joined(r['Evidence_Form'] for r in evidence),'Evidence_IDs':joined(r['Form_ID'] for r in evidence),
    'Sources':joined(r['Source'] for r in evidence),'Interpretation':note,
    'Scope':'Source-reported vowel-lowering incidence is not automatically accepted from these unclassified surface vowels; consult etymon and formation notes.'})
 counts=[]
 for lang in ['Kui','Kuwi','Manda']:
  items=[n for n,e,t,p,ls,note in ITEMS[:18] if lang in ls.split(';')]
  missing=[3] if lang=='Kui' else []
  denom=18-len(missing)
  counts.append({'Language_ID':lang,'N_K80_Listed_Lowered':len(items),'N_Selected_Positive_Examples':18,
    'Listed_Lowered_Over_Selected':f'{len(items)}/18','Proportion_Selected':round(len(items)/18,6),
    'Explicitly_Missing_Items':joined(map(str,missing)),'Known_Attestation_Adjusted_Denominator':denom if lang=='Kui' else '',
    'Lowered_Over_Explicitly_Nonmissing':f'{len(items)}/{denom}' if lang=='Kui' else '',
    'K80_Item_Membership':joined(map(str,items)),
    'Caution':'Recount of the printed positive-example list, not an independently sampled frequency or replication of historical conditioning.'})
 write('lowering-source-audit.tsv',rows);write('lowering-language-panels.tsv',panels);write('lowering-source-counts.tsv',counts)
 stats={'source_items':len(rows),'positive_items':18,'control_items':5,'proposed_exceptions':2,
  'input_tiers':dict(Counter(r['Input_Support_Tier'] for r in rows)),
  'printed_list_recount':counts,
  'arithmetic_correction':'K80 p.499 lists 9 Kui-only, 1 Kuvi-only, 6 Kui+Kuvi and 2 Kui+Kuvi+Manda: Kui17/18 selected, or17/17 explicitly nonmissing; not18/18. Kuvi9/18; sharedKuiKuvi8/18. Kui-only9/18, not10/18.'}
 (HERE/'lowering-results.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
