"""Auditable research views. Never changes any database input.

Raw family membership is preserved beside corrected research membership.
First-pass family review is explicitly not represented as individual source QA.
"""
from pathlib import Path
import csv
import json
import re
from collections import Counter, defaultdict
from functools import lru_cache
from phonology import modern_features, old_features, segment_key

HERE=Path(__file__).resolve().parent

def numbered(path):
    m=re.search(r'_(\d+)\.',path.name)
    return int(m[1]) if m else 0

def jsonlines(pattern):
    for path in sorted(HERE.glob(pattern),key=numbered):
        for n,line in enumerate(path.read_text().splitlines(),1):
            if line.strip():
                row=json.loads(line)
                yield row, f'{path.name}:{n}'

def tsv(name):
    with (HERE/name).open() as f:return list(csv.DictReader(f,delimiter='\t'))

def load_ancestors():
    rows=tsv('ancestral-records.tsv')
    if (HERE/'supplementary-ancestors.tsv').exists():rows+=tsv('supplementary-ancestors.tsv')
    assert len({r['ID'] for r in rows})==len(rows)
    return {r['ID']:r for r in rows}

def write_tsv(name,rows):
    rows=list(rows)
    if not rows:return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (HERE/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='raise')
        w.writeheader()
        for row in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})

@lru_cache(maxsize=1)
def formation_rules():return tuple(jsonlines('formation_decisions*.jsonl'))

def apply_formation_decisions(r):
    """Last-stage explicit formation corrections, including split tokens.

    A family constraint prevents a homonym split from receiving the other
    branch's input. These source-based rules never inspect accent outcomes.
    """
    r['formation_decisions']=[]
    for d,loc in formation_rules():
        if r['research_family_id']!=d['family_id']:continue
        if d.get('language') and r['language_id']!=d['language']:continue
        if d.get('gloss_regex') and not re.search(d['gloss_regex'],r['research_gloss'],re.I):continue
        for k in ['research_ancestor_id','strict_exclusion']:
            if k in d:r[k]=d[k]
        r['formation_decisions'].append({**d,'decision_locator':loc})
    return r

def load_annotations():
    annotations={}
    for row,loc in jsonlines('family_annotations*.jsonl'):
        fid=row['family_id']
        assert fid not in annotations,('duplicate first pass',fid,loc)
        annotations[fid]={**row,'annotation_history':[loc]}
    for row,loc in jsonlines('annotation_revisions*.jsonl'):
        fid=row['family_id'];assert fid in annotations,(fid,loc)
        annotations[fid].update(row)
        annotations[fid]['annotation_history'].append(loc)
    expected={r['family_id'] for r in tsv('families.tsv')}
    assert set(annotations)==expected,('family coverage',expected-set(annotations),set(annotations)-expected)
    return annotations

def load_records():
    rows=tsv('corpus.tsv');byid={r['id']:r for r in rows}
    assert len(byid)==len(rows)
    decisions=defaultdict(list)
    for d,loc in jsonlines('record_decisions*.jsonl'):
        for rid in d.get('record_ids',[d.get('record_id')]):
            assert rid in byid,(loc,d)
            decisions[rid].append({**d,'record_id':rid,'decision_locator':loc})
    links={}
    for d,loc in jsonlines('research_links*.jsonl'):
        for rid in d.get('record_ids',[d.get('record_id')]):
            assert rid in byid,(loc,rid)
            assert rid not in links,('duplicate research link',rid,loc)
            links[rid]={**d,'link_locator':loc}
    for d,loc in jsonlines('research_link_revisions*.jsonl'):
        for rid in d.get('record_ids',[d.get('record_id')]):
            assert rid in byid,(loc,rid)
            links[rid]={**links.get(rid,{}),**d,'link_locator':loc}
    for d,loc in jsonlines('identity_links*.jsonl'):
        for rid in d['record_ids']:
            assert rid in byid and rid not in links,(rid,loc)
            links[rid]={**d,'link_locator':loc}
    observations=defaultdict(list)
    for d,loc in jsonlines('source_observations*.jsonl'):
        for rid in d.get('record_ids',[d.get('record_id')]):
            assert rid in byid,(loc,rid)
            observations[rid].append({**d,'observation_locator':loc})
    additional=defaultdict(list)
    for pattern in ['adjective_residuals*.jsonl','property_residuals*.jsonl','paradigm_annotations*.jsonl','lexical_annotations*.jsonl','etymology_proposals*.jsonl']:
        for d,loc in jsonlines(pattern):
            for rid in d.get('record_ids',[d.get('record_id')]):
                assert rid in byid,(loc,rid)
                additional[rid].append({**d,'annotation_locator':loc})
    reviews={}
    for d,loc in jsonlines('unlinked_reviews*.jsonl'):
        for rid in d['record_ids']:
            assert rid in byid,(loc,rid)
            reviews[rid]={**d,'review_locator':loc}
    # Compact, manually adjudicated source/gloss sets. Exact frozen spellings
    # can restrict a selection; this is not a similarity-based cognacy rule.
    for d,loc in jsonlines('review_sets*.jsonl'):
        matches=[r for r in rows if r['language_id']==d['language']
                 and d['source'] in r['source_keys'].split(';') and not r['family_id']
                 and r['gloss'].lower().strip() in d['glosses']
                 and ('forms' not in d or r['original'] in d['forms'])]
        assert matches,('empty reviewed set',loc,d)
        for r in matches:
            rid=r['id'];assert rid not in reviews and rid not in links,('overlapping reviewed set',rid,loc)
            reviews[rid]={'analysis':d['basis'],'status':d.get('status','assessed'), 'review_locator':loc}
            if d.get('family_id'):
                links[rid]={**d,'confidence':d.get('confidence','high'),
                            'relation':d.get('relation','research-cognate'),'link_locator':loc}
    consolidations={d['from_family']:d for d,_ in jsonlines('family_consolidations*.jsonl')}
    bro_primary={}
    for d,loc in jsonlines('brokskat_primary*.jsonl'):
        key=str(d['item']);assert key not in bro_primary,('duplicate Brokskat primary item',key)
        bro_primary[key]={**d,'reading_locator':loc,'source':'Schmidt and Kaul 2008, Table 2'}
    bro_alignments={}
    for d,loc in jsonlines('brokskat_alignments*.jsonl'):
        for rid in d['record_ids']:
            assert rid in byid,(loc,rid)
            bro_alignments[rid]={**d,'alignment_locator':loc}
    for r in rows:
        r.update(research_family_id=r['family_id'],research_ancestor_id=r['ancestor_id'],
                 research_gloss=r['gloss'],research_relation='database-link' if r['family_id'] else 'unlinked',
                 strict_exclusion='',individual_review='family-context-first-pass' if r['family_id'] else 'unlinked-inventory',
                 research_link_evidence='',research_link_confidence='database-unverified' if r['family_id'] else '')
        r['record_decisions']=decisions.get(r['id'],[])
        r['additional_record_annotations']=additional.get(r['id'],[])
        if r['additional_record_annotations']:r['individual_review']='explicit-structural-or-paradigm-review'
        for d in r['record_decisions']:
            target=d.get('research_family_id',d.get('research_family'))
            if target:
                r['research_family_id']=target
                r['research_ancestor_id']=d.get('research_ancestor_id',d.get('research_ancestor',''))
                r['research_relation']=d.get('research_relation','corrected-reference')
            if 'research_gloss' in d:r['research_gloss']=d['research_gloss']
            if 'research_original' in d:r['research_original']=d['research_original']
            if d['decision'].startswith('exclude'):r['strict_exclusion']=d['decision']
            r['individual_review']='explicit-record-decision'
        if r['id'] in reviews:
            d=reviews[r['id']]
            r.update(etymological_assessment=d['analysis'],unlinked_review_locator=d['review_locator'],
                     unlinked_review_status=d['status'],individual_review='manual-unlinked-assessment')
        if r['id'] in links:
            d=links[r['id']]
            r.update(research_family_id=d['family_id'],research_ancestor_id=d.get('ancestor_id',''),
                     research_relation=d.get('relation','research-cognate'),research_link_evidence=d['basis'],
                     research_link_confidence=d['confidence'],research_link_locator=d['link_locator'],
                     individual_review='manual-research-link')
            if d.get('strict_exclusion'):r['strict_exclusion']=d['strict_exclusion']
        if r['research_family_id'] in consolidations:
            d=consolidations[r['research_family_id']]
            r['research_family_id']=d['to_family'];r['family_consolidation']=d['basis']
        r['primary_table_readings']=[]
        if r['language_id']=='bro' and 'schmidt' in r['source_keys'].split(';'):
            items=re.findall(r'Table 2 item (\d+[a-z]?)',r['description'])
            r['primary_table_readings']=[bro_primary[x] for x in items if x in bro_primary]
            forms=list(dict.fromkeys(w for d in r['primary_table_readings'] for w in d['forms']))
            alignment=bro_alignments.get(r['id'])
            if alignment:
                forms=alignment['forms'];r['primary_alignment']=alignment
            r['primary_reading_forms']=forms
            if len(forms)==1:
                r['research_original']=forms[0]
                r['individual_review']='primary-table-reading'
            elif r['primary_table_readings']:
                r['primary_reading_unresolved']='multiple-source-alternatives-or-merged-items' if forms else 'no-source-attestation'
                if not r['strict_exclusion']:r['strict_exclusion']=r['primary_reading_unresolved']
        r.update(modern_features({**r,'original':r.get('research_original',r['original'])}))
        r['source_observations']=observations.get(r['id'],[])
        for d in r['source_observations']:
            # Explicit field patch is required. Merely citing a source changes nothing.
            r.update(d.get('reading_override',{}))
            r['individual_review']='primary-source-reading'
        if r['comparison_only'] and not r['strict_exclusion']:
            r['strict_exclusion']='starred-modern-comparison-not-attestation'
        if r.get('primary_reading_unresolved'):
            r.update(modern_outcome='unresolved-source-reading',modern_accent_position='',
                     modern_accent_from_right='',stress_position='',stress_from_right='')
        # This is an evidence identity, not a claim that all same-shaped forms
        # share an etymology. Etymon-level tables use sets, never token majorities.
        r['lexical_comparison_key']='|'.join([r['language_id'],r['dialect_tags'],segment_key(r['original']),r['research_gloss'].lower()])
    return [apply_formation_decisions(r) for r in rows]

def load_analysis_tokens(rows=None):
    """Split only explicitly reviewed alternatives/homonyms, with raw IDs retained."""
    rows=load_records() if rows is None else rows
    byid={r['id']:r for r in rows};splits={}
    for d,loc in jsonlines('lexical_splits*.jsonl'):
        rid=d['record_id'];assert rid in byid and rid not in splits,(rid,loc)
        splits[rid]={**d,'split_locator':loc}
    tokens=[]
    for r in rows:
        if r['id'] not in splits:
            tokens.append({**r,'analysis_token_id':r['id']});continue
        d=splits[r['id']]
        for n,b in enumerate(d['branches'],1):
            t={**r,'analysis_token_id':r['id']+'#'+str(n),
               'research_original':b['surface'],'research_gloss':b['gloss'],
               'research_family_id':b['family_id'],'research_ancestor_id':b.get('ancestor_id',''),
               'research_relation':b.get('relation','research-cognate'),
               'research_link_confidence':b.get('confidence','manual-split'),
               'strict_exclusion':b.get('strict_exclusion',''),
               'primary_reading_unresolved':'','individual_review':'manual-lexical-split',
               'split_evidence':d['basis'],'branch_analysis':b['analysis'],
               'split_locator':d['split_locator']}
            for key in ['source_keys','dialect_tags','description']:
                if key in b:t[key]=b[key]
            t.update(modern_features({**t,'original':b['surface']}))
            tokens.append(t)
    return [apply_formation_decisions(t) for t in tokens]

def build():
    annotations=load_annotations();rows=load_records();tokens=load_analysis_tokens(rows)
    write_tsv('annotated-records.tsv',rows)
    write_tsv('annotated-families.tsv',annotations.values())
    write_tsv('analysis-tokens.tsv',tokens)
    bylang=defaultdict(Counter)
    for r in rows:
        c=bylang[r['language_id']];c['records']+=1
        c['raw_linked']+=bool(r['family_id']);c['research_linked']+=bool(r['research_family_id'])
        c['strict_excluded']+=bool(r['strict_exclusion'])
        c['manual_link_records']+=bool(r['research_link_evidence'])
        c['primary_reading_records']+=bool(r['source_observations'] or r['primary_table_readings'])
    audit={'raw_records':len(rows),'analysis_tokens':len(tokens),'family_first_pass':len(annotations),'languages':dict(bylang),
           'record_decision_count':sum(len(r['record_decisions']) for r in rows),
           'research_link_records':sum(bool(r['research_link_evidence']) for r in rows),
           'source_reading_records':sum(bool(r['source_observations'] or r['primary_table_readings']) for r in rows),
           'brokskat_primary_items':len({str(d['item']) for d,_ in jsonlines('brokskat_primary*.jsonl')})}
    (HERE/'annotation-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(audit,ensure_ascii=False,indent=2))

if __name__=='__main__':build()
