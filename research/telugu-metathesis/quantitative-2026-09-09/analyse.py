#!/usr/bin/env python3
"""Validate manual annotation, link evidence IDs, and generate traceable counts.

Never assigns a historical outcome by regex. Missing observations remain missing;
unreviewed attested language cells remain unreviewed, never unchanged.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from annotations import CASES, TOKEN_OUTCOMES
from source_corrections import CORRECTIONS, SOURCE_ISSUES, research_record
from other_processes import PROCESSES
from supplemental_evidence import EXTRA

HERE=Path(__file__).resolve().parent
def read(name):
    with (HERE/name).open(encoding='utf-8',newline='') as f:
        yield from csv.DictReader(f,delimiter='\t')
def write(name,data,fields=None):
    data=list(data)
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fields or list(data[0]),delimiter='\t',extrasaction='ignore')
        w.writeheader();w.writerows(data)
def main():
    assert len(CASES)==len({c['entry_id'] for c in CASES}), 'duplicate annotation'
    languages={r['ID']:r for r in read('languages.tsv')}
    attested_languages={k for k,r in languages.items() if not r['Name'].startswith('Proto-') and k!='Drav'}
    groups=defaultdict(list)
    database_ids=set()
    for r in read('corpus.tsv'):
        database_ids.add(r['ID'])
        groups[r['Research_Group']].append(research_record(r)|{'Record_Origin':'database','Linked_Database_IDs':r['ID']})
    for r in EXTRA:
        assert all(fid in database_ids for fid in r['Linked_Database_IDs'].split(';')),r
        groups[r['Research_Group']].append(r)
    errors=[];evidence=[];cells=[];case_rows=[];appendix=[]
    for c in CASES:
        assert set(c['outcomes'])<=attested_languages, (c['entry_id'],set(c['outcomes'])-attested_languages)
        eid=c['entry_id']
        if eid not in groups:
            errors.append('No group '+eid);continue
        base={k:v for k,v in c.items() if k!='outcomes'}
        case_rows.append(base)
        bylang=defaultdict(list)
        for r in groups[eid]:bylang[r['Language_ID']].append(r)
        used_ids=set(); token_statuses={}
        for lang in sorted(attested_languages):
            actual=bylang[lang]
            if lang in c['outcomes']:
                status,words,note=c['outcomes'][lang]
                assert status in {'D','R','M','A','O','B'}, (eid,lang,status)
                ids=[]
                for word in words.split('|'):
                    token_status=TOKEN_OUTCOMES.get((eid,lang,word),status)
                    if token_status=='M':
                        errors.append(f'{eid} {lang}: mixed cell needs per-token outcome for {word!r}')
                    assert token_status in {'D','R','A','O','B','M'}, (eid,lang,word,token_status)
                    matches=[r for r in actual if r['Form']==word]
                    if not matches:
                        errors.append(f'{eid} {lang}: unmatched form {word!r}')
                    for r in matches:
                        ids.append(r['ID']);used_ids.add(r['ID'])
                        token_statuses[r['ID']]=token_status
                        evidence.append({'Entry_ID':eid,'Family_ID':c['family_id'],'Language_ID':lang,
                            'Language_Outcome':status,'Observed_Outcome':token_status,
                            'Evidence_Form':word,'Form_ID':r['ID'],
                            'Record_Origin':r['Record_Origin'],'Linked_Database_IDs':r['Linked_Database_IDs'],
                            'Database_Language_ID':r['Database_Language_ID'],
                            'Research_Correction':r['Research_Correction'],
                            'Original':r['Original'],'Gloss':r['Gloss'],'Source':r['Source'],
                            'Tags':r['Tags'],'Description':r['Description'],
                            'Borrowed_In_Path':r['Borrowed_In_Path'],'Outcome_Note':note})
            else:
                status='not-reviewed' if actual else 'missing'
                words='';note='';ids=[]
            cells.append({'Entry_ID':eid,'Family_ID':c['family_id'],'Concept':c['concept'],
                'Language_ID':lang,'Clade':languages[lang]['Clade'],
                'Eligibility':c['eligibility'],'C1':c['c1'],'V1':c['v1'],
                'V1_Quantity':c['v1_quantity'],'C2':c['c2'],'C2_Structure':c['c2_structure'],
                'V2':c['v2'],'Structure':c['structure'],'Grammatical_Category':c['grammatical_category'],
                'Input_Confidence':c['input_confidence'],'Confidence':c['confidence'],
                'Outcome':status,'Evidence_Forms':words,'Evidence_IDs':';'.join(dict.fromkeys(ids)),
                'N_Database_Records':sum(r['Record_Origin']=='database' for r in actual),
                'N_Supplemental_Observations':sum(r['Record_Origin']=='source-supplement' for r in actual),'Notes':note})
        for r in groups[eid]:
            appendix.append(r|{'Annotation_Entry_ID':eid,'Annotation_Family_ID':c['family_id'],
                              'Individually_Cited_Evidence':int(r['ID'] in used_ids),
                              'Observed_Token_Outcome':token_statuses.get(r['ID'],'not-individually-adjudicated'),
                              'Language_Review_Status':c['outcomes'].get(r['Language_ID'],('not-reviewed',))[0]})
    process_rows=[]
    for p in PROCESSES:
        matches=[r for r in groups[p['Entry_ID']]
                 if r['Language_ID']==p['Language_ID'] and r['Form']==p['Observed_Form']]
        if not matches:errors.append(f"Process unmatched: {p['Entry_ID']} {p['Language_ID']} {p['Observed_Form']!r}")
        for r in matches:
            process_rows.append(p|{'Form_ID':r['ID'],'Database_Language_ID':r['Database_Language_ID'],
                                   'Source':r['Source'],'Tags':r['Tags'],'Gloss':r['Gloss']})
    (HERE/'annotation-errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2)+'\n')
    if errors:
        print('\n'.join(errors));raise SystemExit(f'{len(errors)} annotation linkage errors')
    write('etymon-annotations.tsv',case_rows)
    write('language-outcomes.tsv',cells)
    write('cited-evidence.tsv',evidence)
    write('complete-reviewed-records.tsv',appendix)
    write('source-corrections.tsv',[{'Form_ID':fid}|r for fid,r in CORRECTIONS.items()])
    write('source-issues.tsv',SOURCE_ISSUES)
    write('supplemental-source-forms.tsv',EXTRA)
    write('other-process-observations.tsv',process_rows)
    # Explicit full categorical distributions; no conflation of missing with retained.
    summary=[];members=[]
    dimensions=['C1','C2','V1','V1_Quantity','C2_Structure','V2','Eligibility','Grammatical_Category']
    for dim in ['all']+dimensions:
        bins=defaultdict(list)
        for r in cells:
            bins[(r['Language_ID'],'all' if dim=='all' else r[dim])].append(r)
        for (lang,value),rs in sorted(bins.items()):
            cnt=Counter(r['Outcome'] for r in rs)
            decisive=cnt['D']+cnt['R']+cnt['M']+cnt['O']
            reviewed=decisive+cnt['A']+cnt['B']
            attested=reviewed+cnt['not-reviewed']
            summary.append({'Dimension':dim,'Value':value,'Language_ID':lang,
                'N_Annotated_Entries':len(rs),'N_Attested':attested,'N_Reviewed':reviewed,
                'N_Decisive_Nonloan':decisive,'N_Displacement_Only':cnt['D'],
                'N_Retained_Only':cnt['R'],'N_Mixed':cnt['M'],'N_Other':cnt['O'],
                'N_Ambiguous':cnt['A'],'N_Loan':cnt['B'],'N_Missing':cnt['missing'],
                'N_Unreviewed_Attested':cnt['not-reviewed'],
                'Any_Displacement_Among_Decisive':(cnt['D']+cnt['M'])/decisive if decisive else '',
                'Any_Displacement_Numerator':cnt['D']+cnt['M'],
                'Any_Displacement_Denominator':decisive,
                'Unit':'DEDR group; root-family merging sensitivity still separate'})
            for r in rs:
                members.append({'Dimension':dim,'Value':value,'Language_ID':lang,
                                'Entry_ID':r['Entry_ID'],'Family_ID':r['Family_ID'],
                                'Outcome':r['Outcome']})
    write('counts-by-input-class.tsv',summary)
    write('count-membership.tsv',members)
    coverage=[]
    reviewed={c['entry_id'] for c in CASES}
    for r in read('families.tsv'):
        coverage.append(r|{'Review_Status':'reviewed' if r['Group_ID'] in reviewed else 'inventory-only'})
    write('review-coverage.tsv',coverage)
    stats={'reviewed_entries':len(CASES),'reviewed_language_cells':sum(r['Outcome'] not in {'missing','not-reviewed'} for r in cells),
        'evidence_record_links':len(evidence),'unique_cited_form_ids':len({r['Form_ID'] for r in evidence if r['Record_Origin']=='database'}),
        'cited_supplemental_observations':sum(r['Record_Origin']=='source-supplement' for r in evidence),
        'all_records_in_reviewed_groups':sum(r['Record_Origin']=='database' for r in appendix),'linkage_errors':len(errors),
        'annotation_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted([HERE/'annotations.py',HERE/'source_corrections.py',HERE/'other_processes.py',HERE/'supplemental_evidence.py',*HERE.glob('cases_*.py')])},
        'status':'annotation export complete; consult validation.json for the independent audit'}
    (HERE/'analysis-progress.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2))

if __name__=='__main__':main()
