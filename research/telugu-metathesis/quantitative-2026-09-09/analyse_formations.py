#!/usr/bin/env python3
"""Validate manual formation rows and test conditional quantity/application rules."""
import csv,json
from collections import defaultdict,Counter
from pathlib import Path
from annotations import CASES
from formation_tests import FORMATIONS
from quantify_families import read,write,joined
HERE=Path(__file__).resolve().parent

def prediction(r):
    if r['Target']!='apical' or r['Root_Quantity']!='short':return 'outside-short-singleton-rule'
    a,b=r['V1'],r['V2']
    if b=='zero':return 'short-from-consonantal-input'
    if b=='a' or (a==b and a in {'a','i','u','e','o'}):return 'long-if-displaced'
    if b in {'i','u'} and a in {'a','i','u','e','o'} and a!=b:return 'short-if-displaced'
    return 'input-underdetermined'

def main():
    cases={c['entry_id']:c for c in CASES};ev=read('cited-evidence.tsv')
    bykey=defaultdict(list);byentry=defaultdict(list)
    for r in ev:bykey[(r['Entry_ID'],r['Language_ID'],r['Evidence_Form'])].append(r);byentry[r['Entry_ID']].append(r)
    rows=[];errors=[]
    for r in FORMATIONS:
        hits=[]
        for word in r['Evidence_Forms'].split('|'):
            found=bykey[(r['Entry_ID'],r['Language_ID'],word)]
            if not found:errors.append(f"{r['Formation_ID']} {r['Language_ID']}: {word!r}")
            hits.extend(found)
        c=cases[r['Entry_ID']];flags={h['Observed_Outcome'] for h in hits}
        p=prediction(r)
        if 'D' not in flags:result='not-a-displaced-quantity-observation'
        elif r['Input_Tier'] in {'conditional','mixed'}:result='conditional-or-mixed-input-excluded-from-strict-test'
        elif p in {'outside-short-singleton-rule','input-underdetermined'}:result=p
        else:
            expected='long' if p=='long-if-displaced' else 'short'
            result='surface-match' if r['Observed_Quantity']==expected else 'surface-counterexample-needs-additional-history'
        inputs=[h for h in byentry[r['Entry_ID']] if h['Language_ID']!=r['Language_ID'] and h['Observed_Outcome']=='R']
        rows.append(r|{'Family_ID':c['family_id'],'Prediction':p,'Observed_Flags':joined(flags),
            'Quantity_Test_Result':result,'Outcome_Evidence_IDs':joined(h['Form_ID'] for h in hits),
            'Outcome_Sources':joined(h['Source'] for h in hits),
            'Comparative_Panel_IDs':joined(h['Form_ID'] for h in inputs),
            'Comparative_Panel_Scope':'Cited retained-order comparanda; exact formation match is assessed in Input_Tier and explanation, not asserted for every panel form.',
            'Full_Derivation':c['derivation'],'Exception_Notes':c['exception_notes'],'References':c['references']})
    (HERE/'formation-errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2)+'\n')
    if errors:
        print('\n'.join(errors));raise SystemExit(1)
    assert len({(r['Formation_ID'],r['Language_ID']) for r in rows})==len(rows)
    write('formation-tests.tsv',rows)
    counts=[];members=[]
    for lang in sorted({r['Language_ID'] for r in rows}):
        for tier in sorted({r['Input_Tier'] for r in rows}):
            for pred in sorted({r['Prediction'] for r in rows}):
                subset=[r for r in rows if r['Language_ID']==lang and r['Input_Tier']==tier and r['Prediction']==pred]
                if not subset:continue
                fs=defaultdict(list)
                for r in subset:fs[r['Family_ID']].append(r)
                cc=Counter()
                for f,rr in fs.items():
                    flags=set(';'.join(r['Observed_Flags'] for r in rr).split(';'))
                    results={r['Quantity_Test_Result'] for r in rr}
                    d='D' in flags;ret='R' in flags
                    category=('mixed-match-and-counterexample' if {'surface-match','surface-counterexample-needs-additional-history'}<=results else
                              'counterexample' if 'surface-counterexample-needs-additional-history' in results else
                              'match' if 'surface-match' in results else 'not-strictly-testable')
                    cc[category]+=1;cc['D-bearing']+=d;cc['R-bearing']+=ret
                    members.append({'Language_ID':lang,'Input_Tier':tier,'Prediction':pred,'Family_ID':f,
                        'Formation_IDs':joined(r['Formation_ID'] for r in rr),'Category':category,
                        'Has_D':int(d),'Has_R':int(ret),'Outcome_Evidence_IDs':joined(r['Outcome_Evidence_IDs'] for r in rr)})
                tested=cc['match']+cc['counterexample']+cc['mixed-match-and-counterexample']
                counts.append({'Language_ID':lang,'Input_Tier':tier,'Prediction':pred,
                    'N_Formation_Rows':len(subset),'N_Families':len(fs),'N_D_Bearing':cc['D-bearing'],'N_R_Bearing':cc['R-bearing'],
                    'N_Quantity_Match_Only':cc['match'],'N_Quantity_Counterexample_Only':cc['counterexample'],
                    'N_Mixed_Match_Counterexample':cc['mixed-match-and-counterexample'],
                    'N_Not_Strictly_Testable':cc['not-strictly-testable'],'N_Strict_Quantity_Denominator':tested,
                    'Match_Only_Over_Tested':f"{cc['match']}/{tested}",
                    'Match_Only_Proportion':round(cc['match']/tested,6) if tested else ''})
    write('formation-class-counts.tsv',counts);write('formation-count-membership.tsv',members)
    covered={r['Family_ID'] for r in rows if r['Language_ID']=='Telugu' and 'D' in r['Observed_Flags']}
    all_d={r['Family_ID'] for r in ev if r['Language_ID']=='Telugu' and r['Observed_Outcome']=='D'}
    summary={'formation_rows':len(rows),'entry_ids':len({r['Entry_ID'] for r in rows}),
        'telugu_D_families_covered':len(covered),'telugu_D_families_not_in_formation_tests':sorted(all_d-covered),
        'quantity_counts':counts,'note':'Selected formation audit, not independent etymon frequencies. A family may enter different independently defined formation classes; do not sum across those classes.'}
    (HERE/'formation-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print('Rows',len(rows),'Telugu D families covered',len(covered),'not covered',sorted(all_d-covered))
    for r in counts:print(r)
if __name__=='__main__':main()
