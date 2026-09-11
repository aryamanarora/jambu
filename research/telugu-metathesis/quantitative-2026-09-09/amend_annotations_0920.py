"""Idempotent maintenance: restore exact parsed paradigm citation strings."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'cases_control_nouns.py'
s=p.read_text()
fixes={
"'Kuwi':('R','kāl','Long root with plural suffix.')":"'Kuwi':('R','kāl ( -ka)','Long root with plural suffix.')",
"'Parji':('R','kēl','Long root, local vowel change.')":"'Parji':('R','kēl ( kēlul)','Long root, local vowel change.')",
"'Gadaba':('R','kāl','Long root.')":"'Gadaba':('R','kāl ( kālgil)','Long root.')",
"'Gadaba':('R','panḍu|panḍ','Cluster retained.')":"'Gadaba':('R','panḍu ( panḍkīl)|panḍ','Cluster retained.')",
}
for old,new in fixes.items():
    assert s.count(old)+s.count(new)==1,(old,s.count(old),s.count(new))
    s=s.replace(old,new)
if '    # Preserve parsed paradigm strings' in s:
    start=s.index('    # Preserve parsed paradigm strings')
    end=s.index("    add('d1906'",start)
    s=s[:start]+s[end:]
p.write_text(s)
p=HERE/'cases_c_controls.py'
s=p.read_text().replace('Retroflexion in ḍakku remains locally unexplained, but uncertainty about that one consonant is not positive metathesis evidence.', 'K61 p.53 §1.126 proposes hyperstandard ḍ for d in ḍakku; this is an alternative to metathesis, not a demonstrated ancient sound law. The same discussion finds no evidence for an assumed lost nasal source. Uncertainty about this consonant is not positive metathesis evidence.')
s=s.replace("references='DEDR 3014'", "references='DEDR 3014; K61 p.53 §1.126 (prior verified reading)'")
s=s.replace("references='DEDR 2988; compare DEDR 2698'", "references='DEDR 2988; compare DEDR2698 and K61 p.54 §1.127 alternative derivations (prior verified reading)'")
p.write_text(s)
print('Annotation citation strings amended.')
p=HERE/'cases_e_processes.py'
if p.exists():
    s=p.read_text().replace('iṟata|iṟake|iṟaku','iṟata|iṟaku')
    p.write_text(s)
p=HERE/'cases_lowering_controls.py'
s=p.read_text().replace("references='K80 p.498 item4; DEDR2674; K03 reconstruction records'", "references='K80 p.498 item4; DEDR2674; K03 p.97 example10 (ogaru perhaps a Kannada loan; Gondi sawwor vowel metathesis)'")
s=s.replace("R='uppu|uppani|uppana|uppaḷamu|ogaru',A='vagaru'", "R='uppu|uppani|uppana|uppaḷamu',A='ogaru|vagaru'")
p.write_text(s)
