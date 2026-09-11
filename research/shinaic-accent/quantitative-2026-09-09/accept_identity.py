"""Freeze the 313 explicitly inspected lexical-identity candidates.

Acceptance concerns same-language lexeme identity, not proof of the inherited
etymology. No accent is copied. Historical etymology caveats still apply.
"""
import json
from identity_candidates import candidates
from analysis_data import HERE
snapshot=HERE/'identity-candidate-snapshot.json'
cs=json.loads(snapshot.read_text()) if snapshot.exists() else candidates()
assert len(cs)==313,len(cs)
rejected={93:'Empty target gloss; identity insufficiently constrained.',
          193:'Maize family markaka bird is a disputed semantic/contact comparison, not a secure inherited anchor.',
          272:'Year saal is likely Iranian; do not propagate the unsupported kaala assignment.'}
(HERE/'identity-candidate-snapshot.json').write_text(json.dumps(cs,ensure_ascii=False,indent=2)+'\n')
with (HERE/'identity_links.jsonl').open('w') as f:
    for c in cs:
        if c['candidate'] in rejected:continue
        d={'record_ids':c['record_ids'],'family_id':c['family_id'],'confidence':'lexeme-identity-etymology-inherited',
           'relation':'same-language-reviewed-lexeme','anchor_record_ids':c['anchor_ids'],
           'basis':'Manually inspected same-language form and meaning match: '+', '.join(c['target_forms'])+' = '+', '.join(c['anchor_forms'])+'. Quantity and accent remain source-specific; inherited root-family assignment retains the anchor etymology caveats.',
           'candidate_index':c['candidate']}
        f.write(json.dumps(d,ensure_ascii=False)+'\n')
(HERE/'identity-review-audit.json').write_text(json.dumps({'candidates':len(cs),'accepted_groups':len(cs)-len(rejected),'rejected':rejected},ensure_ascii=False,indent=2)+'\n')
print('accepted',len(cs)-len(rejected),'groups',sum(len(c['record_ids']) for c in cs if c['candidate'] not in rejected),'records')
