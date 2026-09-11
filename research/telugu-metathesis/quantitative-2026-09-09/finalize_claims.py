"""Freeze statuses of explicitly tested literature claims; no new outcomes inferred."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
claims=json.loads((P/'literature-claims.json').read_text())
updates={
 'K03-rule20':('Tested against182 manually annotated formations covering every117 Telugu D-bearing family; strict surface quantity results25/33 long,8/8 differing-high short,21/21 consonantal short. Conditional/mixed inputs excluded.','formation-tests.tsv; formation-count-membership.tsv'),
 'K03-rule21':('Tested across409 comparative entries: visible cluster/reduced doublets support concealment, but direct medial assimilation remains an alternative for r-less forms without cluster witnesses. Telugu vrāyu>rāyu is a first-member-loss exception to a uniform Telugu R-loss formula.','casebook.md; cited-evidence.tsv'),
 'H04-kp':('All152 literal-screen records adjudicated. Supported-family counts Kui61/61,Kuvi2/3 with one possible retained source variant,Pengo4/4,Manda2/2; additional55 source paradigm observations preserve nonvelar and vowel-stem controls.','stop-cluster-annotations.tsv; stop-rule-counts.tsv; kondh-source-paradigms.tsv'),
 'S69-destroy':('Fourteen historical observations exported with separate source dating, written reading and inferred sound history. Earlier first-quarter seventh-century claim is source-attributed, not an absolute onset date.','historical-evidence.tsv'),
 'GB09-analogy':('Source paradigms and labial/vowel-base controls establish nonexchange routes to pk. They make the analogical account viable but do not uniquely establish its reconstructed historical sequence.','kondh-source-paradigms.tsv; source-paradigm-counts.tsv'),
 'BB63-source-quality':('Introductory p.231 read; attempted local full-PDF extraction failed because the saved file was an HTML access page. Full article not consulted. Source/dialect caveat retained without deleting contrary evidence.','SOURCE_ACCESS.md')}
for c in claims:
 if c['id'] in updates:c['status'],c['analysis_artifacts']=updates[c['id']]
claims.append({'id':'K80-lowering-recount','source':'Krishnamurti1980 pp.495–506, especially499,501','claim':'Lowering distribution and relative chronology distinguish vowels produced by different contractions.','status':'All25 numbered positive/control/exception items audited; printed-list Kui17/18 selected or17/17 explicitly nonmissing, Kuvi9/18, Manda2/18. Exact inherited low-a formation is independently supported in only a subset.','test':'No population estimate from the selected list; preserved open-mid quality is a historical hypothesis, not a look-back rule.','analysis_artifacts':'lowering-source-audit.tsv; lowering-language-panels.tsv; lowering-results.json'})
(P/'literature-claims.json').write_text(json.dumps(claims,ensure_ascii=False,indent=2)+'\n')
