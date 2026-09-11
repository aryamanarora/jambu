#!/usr/bin/env python3
"""Input-only classes and root-deduplicated descriptive denominators.

Run after analyse.py. No observed outcome is inspected by classify_input().
The broad eligibility hypothesis is intentionally falsifiable: retained forms
inside it are not reassigned to new input classes because they failed to change.
Counts describe the explicitly reviewed frame, not all Dravidian etyma.
"""
import csv,json,re
from collections import defaultdict,Counter
from pathlib import Path
from annotations import CASES

HERE=Path(__file__).resolve().parent
ALIASES={'OTelugu':'Telugu','OMal':'Malayalam','pampa':'Kannada'}

# Possible common roots, supported by comparative/semantic arguments in the
# annotation notes. These are sensitivity merges, not accepted new etymologies.
SENSITIVITY=[
 (['d63','d80'],'Compressed/hidden and piled/close semantic extensions with overlapping full forms.'),
 (['d75','d76'],'Pot may be a cooking implement derivative of cook *aṭ; new weak semantic/shape hypothesis, not demonstrated suffix identity.'),
 (['d207','d259','d260'],'Interlace/weave and bowstring: overlapping allu and plausible ar-V-l > all; notes explicitly compare d207 with d260.'),
 (['d236','d240'],'Suffer/tire and move/shake: DEDR explicitly discusses semantic convergence, while retaining separate roots.'),
 (['d247','d248'],'Blossom/expand and beauty/shine: DEDR tentative connection, overlapping alar forms.'),
 (['d304','d306'],'Prick/be angry and fear: overlapping Kannada aḷaku/aḷuku and Telugu aluku with affective semantic bridge.'),
 (['d296','d307'],'Mix/seize and enclose/cover: overlapping Telugu alamu; different extensions remain uncertain.'),
 (['d233','d315'],'Fall rālu is compared by K61 p.56 with Tamil aṟal from sever/cut, making independent counting questionable.'),
 (['d276','d281'],'Burn/grieve and affection/desire: DEDR tentative cross-reference, with shared aẓ and differing extensions.'),
 (['d434','d448','d446','d449'],'Place/room/broadness cluster, explicitly uncertain formation relationships.'),
 (['d435','d437'],'Affliction/obstacle and stumble/hinder: possible common obstruction root, explicitly noted.'),
 (['d439','d455'],'Flour cake and steamed cake: plausible culinary/pounding derivatives, independent root status uncertain.'),
 (['d651','d665'],'Mortar ural may be an instrument derivative of ur rub/grind; explicit annotation sensitivity.'),
 (['d656','d661'],'Burn/heat and melt/steel: plausible parent root ur with velar melt formation.'),
 (['d587','d593'],'Wear uṭu and property/owner uṭai: possible older possession/clothing relationship, not proved by homophony.'),
 (['d533','d536'],'Fly/bee and winged termite: DEDR cross-reference; insect-root relationship uncertain.'),
 (['d697','d698'],'Existence and inside: possible common uḷ, with different existential and locative morphology.'),
 (['d590','d713'],'Squirrel and jump/run/squirrel: possible strengthened root variant and animal derivative.'),
 (['d711','d719'],'Increase/abundance and force/speed/throw: possible common uṟ with related labial extensions.'),
 (['d710','d715'],'Happen/be fit and suffer/be afflicted: potentially related uṟ root, with different derivatives.'),
 (['d3949','d4536'],'Spread and sell: K80/DEDR split partly motivated by vowel outcomes; test merger sensitivity.'),
 (['d817','d820'],'Red/dark colour/dog and black soil: split from old DED700; common colour-root hypothesis.'),
 (['d829','d832'],'Shine and joy/enliven: possible el semantic family with different suffixes.'),
 (['d914','d915'],'Glean/separate and winnow ēṟ formations.'),
 (['d946','d949'],'Break and sling: sling may be an instrument derivative, unproved.'),
 (['d958','d959','d962','d965'],'Join/place/bind-related strong oṭṭ family; oath/bank extensions uncertain.'),
 (['d4876','d4885'],'Shine/star and fish may share a shiny root; retained only as sensitivity hypothesis.'),
 (['d1767','d1826'],'Bend/sink kruŋgu and submerge kruŋ share cluster forms and a plausible semantic bridge; full comparanda are available in1767, but the linkage remains uncertain.'),
 (['d1123','d1594'],'Same disputed Telugu cluster assigned to competing roots; preserve alternative cognacy as a merged sensitivity family.'),
 (['d1778','d1851'],'Competing assignments of the same Telugu cluster forms; not two independent positive observations.'),
 (['d3305','d3339'],'Telugu cut/break cluster forms are explicitly alternatively assigned to nasal tuṇ and rhotic tur roots.'),
 (['d3821','d4057'],'Same prā̃ci moss/stale form has competing etymological assignments.'),
 (['d4973','d4989'],'Same Telugu roar cluster series explicitly alternatively assigned to mur and muẓ roots.'),
 (['d5017','d5046'],'Same Telugu ripen mruggu/muggu forms explicitly alternatively assigned to strong muṟṟ and long mūẓ.'),
 (['d5368','d5369'],'Perch and incline may be polysemy of long vāl, with the same extra-r Telugu variant; semantic bridge plausible, not proven.'),
]

def read(name):
    with (HERE/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))
def write(name,rows,fields=None):
    rows=list(rows)
    assert rows or fields,name
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fields or list(rows[0]),delimiter='\t',extrasaction='ignore')
        w.writeheader();w.writerows(rows)
def joined(values):return ';'.join(sorted(set(values)))

def classify_input(c):
    """Only comparative reconstruction fields, never outcomes/observed forms."""
    c1,c2,q=c['c1'],c['c2'],c['v1_quantity']
    onset=('vowel-initial' if c1 in {'Ø','zero'} else
           'mixed/uncertain-onset' if 'zero' in c1 or 'Ø' in c1 else 'consonant-initial')
    quantity='short' if q in {'short','short initial vowel'} else 'long' if q in {'long','long independently established'} else 'mixed/uncertain-quantity'
    apical_map={
        'r':'rhotic','ṟ':'alveolar','ṯ':'alveolar','ẓ':'retroflex-approximant',
        'ḷ':'lateral','l':'lateral','ṭ':'retroflex-stop','ḍ':'retroflex-stop','ṛ':'retroflex-rhotic',
        'ṭ/ḍ':'retroflex-stop','l/ḷ':'lateral','ḷ/l':'lateral','ḷ / alternative r':'mixed-apical',
        'r/ṟ':'rhotic-or-alveolar','ṟ/r':'rhotic-or-alveolar','ṟ/ṯ':'alveolar','ṯ/ṟ':'alveolar',
        'r/ẓ':'mixed-apical','ẓ/r':'mixed-apical','ẓ/ṛ':'mixed-apical','r/l':'mixed-apical','ḷ/ṭ':'mixed-apical',
        'r/ṟ/l':'mixed-apical','ṟ/l':'mixed-apical','ll':'lateral','ḷḷ':'lateral',
        'll/ḷḷ':'lateral','ll/l':'lateral','n':'nasal','ṇ':'nasal',
        'n/l':'mixed-nasal-apical','ṇ/ṛ':'mixed-nasal-apical','ḷ/ṇ':'mixed-nasal-apical','ṇṭ/ṛ':'mixed-nasal-apical',
        'ṇṇ':'nasal','nṯ':'nasal-stop','ṇṭ':'nasal-stop','ṇṭ/ṭ':'nasal-stop','nt':'nasal-stop',
        'ṟṟ':'alveolar-strong',
        'ṯṯ/ṇṯṯ':'alveolar-strong','ll/yy':'mixed-lateral-glide',
        'n/y':'nasal-or-glide','t/w/b':'morphological-dental-labial',
    }
    apical=apical_map.get(c2,'nonapical-or-uncertain')
    structure='singleton' if c['c2_structure']=='singleton' else 'geminate' if c['c2_structure'] in {'geminate','geminate independently supported'} else 'mixed/cluster/other'
    vowel=c['v1'] if c['v1'] in {'a','i','u','e','o'} else 'mixed/uncertain-vowel'
    v2=c['v2']
    following='low-a' if v2=='a' else 'high-i' if v2=='i' else 'high-u' if v2=='u' else 'consonantal/no-vowel' if v2 in {'zero','none','Ø'} else 'mixed/unknown-formative'
    primary_apical=apical in {'rhotic','retroflex-rhotic','alveolar','retroflex-approximant','lateral','retroflex-stop','mixed-apical','rhotic-or-alveolar','alveolar-strong'}
    if c['entry_id'] in {'d1','d410'}:domain='pronominal-morphology'
    elif c['grammatical_category']=='verb/quotative':domain='nasal-quotative-morphology'
    elif apical in {'nasal','nasal-or-glide','mixed-nasal-apical','nasal-stop'}:domain='nasal-or-nasal-cluster-input'
    elif not primary_apical:domain='nonapical-or-uncertain-input'
    elif quantity=='long':domain='long-apical-input'
    elif quantity!='short':domain='mixed-or-uncertain-quantity'
    elif structure!='singleton':domain='short-strong-or-mixed-structure'
    elif onset=='vowel-initial':domain='short-vowel-initial-singleton-apical'
    elif onset=='mixed/uncertain-onset':domain='uncertain-initial-order'
    elif c2 in {'r','ṟ','ẓ','r/ṟ','ṟ/r','r/ẓ'}:domain='short-C-initial-r-rhotics-retroflex-approximant'
    else:domain='short-C-initial-other-apical'
    prediction=('eligible; obligatory application predicts D' if domain in {
        'short-vowel-initial-singleton-apical','short-C-initial-r-rhotics-retroflex-approximant'}
        else 'outside narrow classical Telugu domain; no D prediction from that rule')
    return dict(Domain=domain,Onset=onset,C1_Identity=c1,Quantity=quantity,Apical_Group=apical,
                Apical_Structure=structure,V1_Quality=vowel,Following_Vowel=following,
                Grammatical_Category=c['grammatical_category'],
                Domain_Following_Vowel=domain+' / '+following,
                Domain_Apical_Group=domain+' / '+apical,
                Domain_V1_Quality=domain+' / '+vowel,
                Telugu_Broad_Obligatory_Hypothesis=prediction)

def union_partition(primary):
    parent={v:v for v in primary.values()}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    audit=[]
    for members,reason in SENSITIVITY:
        present=[e for e in members if e in primary]
        if len(present)<2:continue
        roots=sorted({find(primary[e]) for e in present})
        for r in roots[1:]:parent[r]=roots[0]
        audit.append(dict(Entry_IDs=joined(present),Proposal=reason,Status='uncertain; sensitivity only'))
    clusters=defaultdict(list)
    for e,p in primary.items():clusters[find(p)].append(e)
    result={e:'sensitivity:'+joined(es) for es in clusters.values() for e in es}
    write('family-merge-sensitivity-proposals.tsv',audit)
    return result

def state(flags,attested):
    if not flags:return 'not-reviewed' if attested else 'missing'
    if 'D' in flags and 'R' in flags:return 'mixed'
    if 'D' in flags:return 'D-bearing-no-R'
    if 'R' in flags:return 'R-bearing-no-D'
    if 'O' in flags and 'A' in flags:return 'other-and-uncertain'
    if 'O' in flags:return 'other-no-DR'
    if 'A' in flags:return 'uncertain-no-DR'
    assert flags=={'B'},flags
    return 'borrowed-only'

def main():
    assert json.loads((HERE/'annotation-errors.json').read_text())==[], 'Run and fix analyse.py first'
    cases={c['entry_id']:c for c in CASES}
    primary={e:c['family_id'] for e,c in cases.items()}
    sensitivity=union_partition(primary)
    partitions={'primary':primary,'sensitivity':sensitivity}
    classes={e:classify_input(c) for e,c in cases.items()}
    write('input-class-membership.tsv',[{'Entry_ID':e,'Primary_Family_ID':primary[e],**v,
        'Raw_C1':cases[e]['c1'],'Raw_C2':cases[e]['c2'],'Raw_Quantity':cases[e]['v1_quantity'],
        'Raw_V2':cases[e]['v2'],'Raw_Structure':cases[e]['c2_structure'],
        'Input_Confidence':cases[e]['input_confidence']} for e,v in classes.items()])
    write('family-partitions.tsv',[{'Entry_ID':e,'Primary_Family_ID':primary[e],
          'Sensitivity_Family_ID':sensitivity[e]} for e in sorted(cases)])
    entry_cells=read('language-outcomes.tsv');evidence=read('cited-evidence.tsv')
    langs=sorted({ALIASES.get(r['Language_ID'],r['Language_ID']) for r in entry_cells})
    ev=defaultdict(list)
    for r in evidence:ev[(r['Entry_ID'],ALIASES.get(r['Language_ID'],r['Language_ID']))].append(r)
    cells=defaultdict(list)
    for r in entry_cells:cells[(r['Entry_ID'],ALIASES.get(r['Language_ID'],r['Language_ID']))].append(r)
    family_rows=[];class_rows=[];count_rows=[];member_rows=[]
    axes=['Domain','Onset','C1_Identity','Quantity','Apical_Group','Apical_Structure','V1_Quality','Following_Vowel','Grammatical_Category',
          'Domain_Following_Vowel','Domain_Apical_Group','Domain_V1_Quality']
    for partition,mapping in partitions.items():
        fams=defaultdict(list)
        for e,f in mapping.items():fams[f].append(e)
        fclasses={}
        for f,es in fams.items():
            fclasses[f]={a:next(iter(v)) if len(v:={classes[e][a] for e in es})==1 else 'mixed-across-related-entries' for a in axes}
            class_rows.append({'Partition':partition,'Family_ID':f,'Entry_IDs':joined(es),**fclasses[f]})
        per_family={}
        for f,es in fams.items():
            for lang in langs:
                observations=[r for e in es for r in ev[(e,lang)]]
                source_cells=[r for e in es for r in cells[(e,lang)]]
                flags={r['Observed_Outcome'] for r in observations}
                assert flags<={'D','R','O','A','B'},flags
                attested=any(int(r['N_Database_Records'])+int(r['N_Supplemental_Observations'])>0 for r in source_cells)
                partial=any(r['Outcome']=='not-reviewed' for r in source_cells)
                row={'Partition':partition,'Family_ID':f,'Entry_IDs':joined(es),'Language_ID':lang,
                    'Raw_Language_IDs':joined(r['Language_ID'] for r in source_cells if int(r['N_Database_Records'])+int(r['N_Supplemental_Observations'])>0),
                    'Outcome_State':state(flags,attested),'Has_D':int('D' in flags),'Has_R':int('R' in flags),
                    'Has_O':int('O' in flags),'Has_A':int('A' in flags),'Has_B':int('B' in flags),
                    'Attested':int(attested),'Reviewed':int(bool(flags)),
                    'Has_Unreviewed_Attested_Member':int(partial),
                    'N_Database_Records':sum(int(r['N_Database_Records']) for r in source_cells),
                    'N_Unique_Cited_Form_IDs':len({r['Form_ID'] for r in observations}),
                    'Evidence_IDs':joined(r['Form_ID'] for r in observations),
                    'Evidence_Forms':joined(r['Evidence_Form'] for r in observations)}
                per_family[(f,lang)]=row;family_rows.append(row)
        for axis in ['ALL',*axes]:
            groups=defaultdict(list)
            for f in fams:groups['all-reviewed-families' if axis=='ALL' else fclasses[f][axis]].append(f)
            for value,fs in sorted(groups.items()):
                for lang in langs:
                    rs=[per_family[(f,lang)] for f in fs]
                    states=Counter(r['Outcome_State'] for r in rs)
                    d=sum(r['Has_D'] for r in rs);r=sum(x['Has_R'] for x in rs)
                    dr=sum(bool(x['Has_D'] or x['Has_R']) for x in rs)
                    reviewed=sum(x['Reviewed'] for x in rs)
                    row={'Partition':partition,'Axis':axis,'Class':value,'Language_ID':lang,
                        'N_Reviewed_Frame_Families':len(fs),'N_Attested_Reviewed':reviewed,
                        'N_Attested_Unreviewed':states['not-reviewed'],'N_Missing':states['missing'],
                        'N_D_No_R':states['D-bearing-no-R'],'N_R_No_D':states['R-bearing-no-D'],
                        'N_Mixed_DR':states['mixed'],'N_Other_No_DR':states['other-no-DR'],
                        'N_Uncertain_No_DR':states['uncertain-no-DR'],'N_Other_And_Uncertain_No_DR':states['other-and-uncertain'],
                        'N_Borrowed_Only':states['borrowed-only'],'N_D_Bearing':d,'N_R_Bearing':r,
                        'N_DR_Informative':dr,'N_Any_Uncertain':sum(x['Has_A'] for x in rs),
                        'N_Any_Other':sum(x['Has_O'] for x in rs),'N_Any_Borrowed':sum(x['Has_B'] for x in rs),
                        'N_Partially_Reviewed_Families':sum(x['Has_Unreviewed_Attested_Member'] for x in rs),
                        'D_Over_DR':f'{d}/{dr}','D_Over_Attested_Reviewed':f'{d}/{reviewed}',
                        'D_Proportion_DR':round(d/dr,6) if dr else '',
                        'D_Proportion_Attested_Reviewed':round(d/reviewed,6) if reviewed else ''}
                    assert reviewed+states['not-reviewed']+states['missing']==len(fs),row
                    assert sum(states.values())==len(fs)
                    count_rows.append(row)
                    for f in fs:
                        rr=per_family[(f,lang)]
                        member_rows.append({'Partition':partition,'Axis':axis,'Class':value,'Language_ID':lang,
                            'Family_ID':f,'Entry_IDs':joined(fams[f]),'Outcome_State':rr['Outcome_State'],
                            'In_D_Numerator':rr['Has_D'],'In_DR_Denominator':int(rr['Has_D'] or rr['Has_R']),
                            'In_Attested_Reviewed_Denominator':rr['Reviewed']})
    write('family-input-classes.tsv',class_rows)
    write('family-language-outcomes.tsv',family_rows)
    write('family-class-counts.tsv',count_rows)
    write('family-count-membership.tsv',member_rows)
    # Explicit test of the strong/obligatory version; not a claim it is true.
    tests=[]
    core_domains={'short-vowel-initial-singleton-apical','short-C-initial-r-rhotics-retroflex-approximant'}
    for rr in family_rows:
        if rr['Partition']!='primary' or rr['Language_ID']!='Telugu':continue
        f=rr['Family_ID'];es=[e for e in cases if primary[e]==f]
        if not all(classes[e]['Domain'] in core_domains for e in es):continue
        result='counterexample-to-obligatory-application' if rr['Has_R'] else 'consistent-D' if rr['Has_D'] else 'not-decisive'
        tests.append({'Hypothesis':'All reviewed short singleton apicals in the narrow classical Telugu domain undergo displacement',
            'Family_ID':f,'Entry_IDs':joined(es),'Input_Classes':joined(classes[e]['Domain'] for e in es),
            'Prediction':'D in every cognate formation','Observed_State':rr['Outcome_State'],
            'Result':result,'Has_D':rr['Has_D'],'Has_R':rr['Has_R'],'Has_A':rr['Has_A'],'Has_O':rr['Has_O'],
            'Evidence_IDs':rr['Evidence_IDs'],'Limit':'Entry-wide formation aggregation; refined formation tests are separate.'})
    write('telugu-obligatory-domain-test.tsv',tests)
    totals={
        'reviewed_entries':len(CASES),'primary_families':len(set(primary.values())),
        'sensitivity_families':len(set(sensitivity.values())),
        'raw_language_ids':len({r['Language_ID'] for r in entry_cells}),
        'time_aggregated_language_groups':len(langs),'aliases':ALIASES,
        'family_class_count_rows':len(count_rows),'membership_rows':len(member_rows),
        'broad_obligatory_test':dict(Counter(r['Result'] for r in tests)),
        'warning':'Targeted reviewed frame; no population frequency or random-sample inference.'}
    (HERE/'quantitative-results.json').write_text(json.dumps(totals,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(totals,ensure_ascii=False,indent=2))
    for row in count_rows:
        if row['Partition']=='primary' and row['Axis']=='ALL':
            print(row['Language_ID'],row['D_Over_DR'],row['D_Over_Attested_Reviewed'],
                  'mixed',row['N_Mixed_DR'],'uncertain',row['N_Uncertain_No_DR'],
                  'other',row['N_Other_No_DR'],'not-reviewed',row['N_Attested_Unreviewed'])

if __name__=='__main__':main()
