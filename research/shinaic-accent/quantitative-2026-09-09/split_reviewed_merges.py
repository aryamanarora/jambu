"""Unpack the manually inspected two-source pairs, preserving source notation."""
import json
from analysis_data import load_records,HERE
rows=load_records();out=[]
for r in rows:
    if not r['research_family_id'] or ';' not in r['original']:continue
    ss=r['source_keys'].split(';')
    if not set(ss)&{'liljegren','strand','degener-shina2008','buddruss-shina1996','schmidt'}:continue
    forms=r['original'].split(';');assert len(forms)==2,(r['id'],forms)
    first='CDIAL' if 'CDIAL' in ss else 'backstrom1992' if 'backstrom1992' in ss else 'liljegren'
    second='strand' if 'strand' in ss else 'schmidt' if 'schmidt' in ss else 'liljegren'
    assert first in ss and second in ss and first!=second,(r['id'],ss)
    out.append({'record_id':r['id'],
      'basis':'Two merged source strings manually inspected in the 2026-09-09 review packet. Each spelling uses its own source notation: first '+first+', second '+second+'. This is source-field disaggregation, not a new primary-page check; no accent is copied between sources.',
      'branches':[{'surface':f.strip(),'gloss':r['research_gloss'],'family_id':r['research_family_id'],
       'ancestor_id':r['research_ancestor_id'],'source_keys':src,'relation':r['research_relation'],
       'confidence':r['research_link_confidence'],'strict_exclusion':r['strict_exclusion'],
       'analysis':'Same reviewed lexical family; retain source-specific accent/quantity and the complete family dossier caveats.'} for f,src in zip(forms,[first,second])]})
assert len(out)==74,len(out)
with (HERE/'lexical_splits_02.jsonl').open('w') as f:
    for x in out:f.write(json.dumps(x,ensure_ascii=False)+'\n')
print('disaggregated',len(out),'merged records into',2*len(out),'source tokens')
