"""Integrity, denominator and evidence-level audits for the research package."""
from pathlib import Path
import hashlib,json,py_compile
from collections import Counter,defaultdict
from analysis_data import HERE,tsv,load_records,load_analysis_tokens,load_annotations,load_ancestors,jsonlines

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    records=load_records();tokens=load_analysis_tokens(records);anns=load_annotations();raw=tsv('corpus.tsv')
    original={r['id']:r for r in raw};byid={r['id']:r for r in records}
    assert len(raw)==len(original)==len(records)==25505
    assert len(tokens)==25593 and len({r['analysis_token_id'] for r in tokens})==len(tokens)
    assert {r['id'] for r in tokens}==set(original)
    assert len(anns)==1686 and all(a.get('analysis') and a.get('input') and a.get('formation') for a in anns.values())
    for rid,r in original.items():
        assert all(byid[rid][k]==v for k,v in r.items()),('raw field changed',rid)
    assert all(not r['research_family_id'] or r['research_family_id'] in anns for r in tokens)
    ancestors=set(load_ancestors())
    missing_ancestor=sorted({r['research_ancestor_id'] for r in tokens if r['research_ancestor_id'] and r['research_ancestor_id'] not in ancestors})
    assert not missing_ancestor,missing_ancestor
    for name in ['annotated-records.tsv','analysis-tokens.tsv','annotated-families.tsv']:
        rr=tsv(name);assert len(rr)=={'annotated-records.tsv':25505,'analysis-tokens.tsv':25593,'annotated-families.tsv':1686}[name]
    for r in tsv('annotated-records.tsv'):
        assert r['individual_review']==byid[r['id']]['individual_review'],('stale review status',r['id'])
        assert json.loads(r['additional_record_annotations'])==byid[r['id']]['additional_record_annotations'],('stale annotations',r['id'])
    hist=tsv('historical-observations.tsv');assert len(hist)==sum(bool(r['research_family_id']) for r in tokens)
    assert len({r['analysis_token_id'] for r in hist})==len(hist)
    proposals=list(jsonlines('etymology_proposals.jsonl'));assert len(proposals)==5
    assert all(rid in original for r,_ in proposals for rid in r['record_ids'])
    assert len(list(jsonlines('brokskat_primary*.jsonl')))==269
    # Independent expected inventories established in the manual review.
    assert len(tsv('vowel-raising-reviewed.tsv'))==78
    assert len(tsv('palula-umlaut-i-nouns.tsv'))==74
    assert len(tsv('palula-i-decl-extension.tsv'))==43
    assert len(tsv('dras-paradigm-review.tsv'))==287
    assert len(tsv('kundal-primary-paradigms.tsv'))==21
    assert len(tsv('numeral-series-tests.tsv'))==20
    assert all(r['consistent']=='1' for r in tsv('numeral-series-tests.tsv'))
    frozen=json.loads((HERE/'input-manifest.json').read_text());cldf=Path(frozen['input_directory'])
    live={name:sha(cldf/name) for name in frozen['input_sha256']}
    drift=[name for name,h in live.items() if h!=frozen['input_sha256'][name]]
    for p in HERE.glob('*.py'):py_compile.compile(str(p),doraise=True)
    coverage=[]
    for lang in ['Sh','Phal','Sv','Kalk','Kund','bro','Ush']:
        rr=[r for r in records if r['language_id']==lang];tt=[r for r in tokens if r['language_id']==lang]
        coverage.append(dict(language=lang,raw_records=len(rr),analysis_tokens=len(tt),raw_linked=sum(bool(r['family_id']) for r in rr),
          research_linked=sum(bool(r['research_family_id']) for r in rr),research_families=len({r['research_family_id'] for r in tt if r['research_family_id']}),
          unlinked=sum(not bool(r['research_family_id']) for r in rr),review_levels=dict(Counter(r['individual_review'] for r in rr)),
          notation_counts=dict(Counter(r['notation'] for r in rr))))
    audit=dict(status='passed',raw_records=len(records),analysis_tokens=len(tokens),families=len(anns),historical_observations=len(hist),
      research_linked_records=sum(bool(r['research_family_id']) for r in records),unlinked_records=sum(not bool(r['research_family_id']) for r in records),
      missing_family_annotations=0,duplicate_family_annotations=0,missing_raw_records=0,altered_raw_fields=0,
      unresolved_research_ancestor_ids=missing_ancestor,live_database_drift_since_freeze=drift,live_database_sha256=live,
      review_levels=dict(Counter(r['individual_review'] for r in records)),coverage=coverage,
      evidence_limit='Complete family first pass and complete record inventory do not imply individual printed-source QA for every citation. Review status and access level are explicit.')
    (HERE/'integrity-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    metrics={name:json.loads((HERE/name).read_text()) for name in ['annotation-audit.json','palula-u-adjectives-summary.json','palula-tagged-u-summary.json','gilgit-o-adjectives-summary.json','palula-umlaut-i-summary.json','palula-i-decl-extension-summary.json']}
    metrics['coverage']=coverage
    for name in ['old-long-screen.tsv','old-long-nominal-sensitivity.tsv','palula-short-a-sensitivity.tsv','property-location-summary.tsv','kalkoti-palula-combined-summary.tsv','dras-suffix-accent-summary.tsv','vowel-raising-summary.tsv']:
        metrics[name]=tsv(name)
    (HERE/'report-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
    # Manifest hashes all analytical inputs and deliverables, excluding mutable
    # progress logs, this manifest itself and Python cache files.
    files={str(p.relative_to(HERE)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['artifact-manifest.json','WORK_STATE.md'] and p.suffix not in ['.log','.pyc']}
    (HERE/'artifact-manifest.json').write_text(json.dumps(dict(files=files,original_input_manifest='input-manifest.json',scope='Research artifacts only; no database or website mutation.'),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:audit[k] for k in ['status','raw_records','analysis_tokens','families','historical_observations','research_linked_records','unlinked_records','live_database_drift_since_freeze']},indent=2))
if __name__=='__main__':main()
