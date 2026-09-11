"""Formation/source sensitivity of the broad long-root screening result.

The manually defined set includes nominal a-stems with attested nominal OIA
meanings and corresponding modern noun senses. It deliberately retains the
unexplained smell and village cases and the foam/steam source/sense conflict.
This is a restricted follow-up to the exhaustive broad screen, not a claim
that the screened set exhausts every historically possible a-stem.
"""
from collections import defaultdict,Counter
import json
from analysis_data import tsv,write_tsv,load_annotations
from quantify import LANGS,MORA

# Selection was made from historical formation and lexical meaning, before
# calculating this restricted model's outcome counts.
NOMINALS={
'2563':'lip, old a-stem body-part noun',
'2993':'crow, old a-stem animal noun',
'3023':'arrow, old a-stem nominal; both old accents explicitly attested',
'3084':'year/time, old a-stem time noun; Iranian saal excluded separately',
'3696':'milk, old neuter a-stem mass noun',
'3735':'field, old neuter a-stem land noun',
'4336':'house, old a-stem dwelling noun',
'4368':'village, old a-stem settlement noun',
'4531':'smell, old neuter a-stem action/result noun; retained as a possible counterexample',
'4931':'thief, old a-stem agent noun',
'5206':'lover/friend, old a-stem person noun',
'5958':'oil, old neuter a-stem substance noun',
'6547':'village/region, old a-stem place noun; retained as a possible counterexample',
'6849':'smoke, old a-stem substance noun',
'9072':'ploughshare, old a-stem implement noun',
'9108':'foam/steam, old a-stem substance noun; related senses kept distinct in the dossier',
'9216':'child, independently attested nominal use of the old a-stem adjective',
'9250':'seed, old neuter a-stem noun',
'9459':'load/burden, old a-stem noun; short bhara alternative separately documented',
'9982':'flesh, old neuter a-stem mass noun; old consonant-stem maas is a separate alternative',
'10042':'nest, old a-stem dwelling noun with semantic specialization',
'10104':'month, old a-stem time noun',
'10234':'urine, old neuter a-stem mass noun',
'11572':'hair, old a-stem body-material noun',
'11591':'lodging, old a-stem residence noun',
'12497':'head, old neuter a-stem body-part noun',
'12575':'labor pain, old a-stem pain noun with narrowed sense',
'12619':'ashes, old a-stem heat noun with semantic specialization',
'13561':'thread, old neuter a-stem implement/material noun',
}
# Conservative sensitivity over documented competing accents or formations.
AMBIGUOUS={'3023','6628','6546','9459','9982','12619','13355','14068','10826'}

def main():
    rows=tsv('historical-observations.tsv');anns=load_annotations()
    selected=[r for r in rows if r['family_id'] in NOMINALS and r['input_class'] in ['old-long-barytone','old-long-oxytone']]
    write_tsv('old-long-nominal-formation-audit.tsv',({'family_id':f,'formation_basis':note,'documented_input_alternative':int(f in AMBIGUOUS),'analysis':anns[f]['analysis'],'unresolved':anns[f].get('unresolved','')} for f,note in NOMINALS.items()))
    panels=[]
    for f in NOMINALS:
        for lang in LANGS:
            rr=[r for r in selected if r['family_id']==f and r['language']==lang]
            panels.append(dict(family_id=f,language=lang,all_forms=sorted({r['form'] for r in rr}),
              outcomes=sorted({r['outcome'] for r in rr if not r['screening_exclusions']}),
              excluded_outcomes=sorted({r['outcome'] for r in rr if r['screening_exclusions']}),
              sources=sorted({r['source'] for r in rr}),formation_basis=NOMINALS[f]))
    write_tsv('old-long-nominal-language-panel.tsv',panels)
    scopes={
      'all-sources-all-lects':lambda r:True,
      'nearest-formation-only':lambda r:r['input_basis']=='nearest-formation',
      'exclude-documented-input-alternatives':lambda r:r['family_id'] not in AMBIGUOUS,
      'Gilgit-Degener-only':lambda r:r['language']=='Sh' and r['source']=='degener-shina2008',
      'Gilgit-Buddruss-only':lambda r:r['language']=='Sh' and r['source']=='buddruss-shina1996',
      'Palula-Liljegren-only':lambda r:r['language']=='Phal' and r['source']=='liljegren',
      'Palula-Strand-only':lambda r:r['language']=='Phal' and r['source']=='strand',
    }
    for dialect in ['gil','koh','gur','Astor','dr']:
        scopes['Shina-Schmidt-'+dialect]=lambda r,d=dialect:r['language']=='Sh' and r['source']=='schmidt' and r['dialect']==d
    out=[];residuals=[]
    for scope,predicate in scopes.items():
        for cl,pred in [('old-long-barytone','E'),('old-long-oxytone','L')]:
            for lang in LANGS:
                vv=[r for r in selected if r['language']==lang and r['input_class']==cl and predicate(r) and not r['screening_exclusions'] and r['notation'] in MORA and r['modern_nuclei']=='1' and r['raw_outcome'] in ['E','L']]
                groups=defaultdict(list)
                for r in vv:groups[r['family_id']].append(r)
                counts=Counter()
                for f,rr in groups.items():
                    os={r['raw_outcome'] for r in rr};status='consistent' if os=={pred} else 'conflicting' if pred in os else 'opposite';counts[status]+=1
                    if scope=='all-sources-all-lects' and status!='consistent':
                        residuals.append(dict(family_id=f,language=lang,input_class=cl,expected=pred,observed=sorted(os),forms=sorted({r['form']+' ['+r['source']+';'+r['dialect']+']' for r in rr}),analysis=anns[f]['analysis'],unresolved=anns[f].get('unresolved','')))
                out.append(dict(scope=scope,input_class=cl,language=lang,scorable_families=len(groups),**counts))
    write_tsv('old-long-nominal-sensitivity.tsv',out);write_tsv('old-long-nominal-residuals.tsv',residuals)
    for r in out:
        if r['scorable_families'] and r['scope'] in ['all-sources-all-lects','Gilgit-Degener-only','exclude-documented-input-alternatives']:print(r)
if __name__=='__main__':main()
