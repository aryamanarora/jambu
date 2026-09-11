#!/usr/bin/env python3
"""Hash the complete research deliverables, excluding caches and editing logs."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
P=Path(__file__).resolve().parent
files=[]
for p in sorted(P.iterdir()):
    if not p.is_file() or p.name=='deliverable-manifest.json':continue
    if p.suffix not in {'.py','.cjs','.md','.tsv','.json','.jsonl','.html','.png','.svg','.txt'}:continue
    digest=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    files.append({'path':p.name,'bytes':p.stat().st_size,'sha256':digest.hexdigest()})
validation={}
for name in ['validation.json','report-validation.json','browser-qa.json','input-verification.json']:
    if (P/name).exists():validation[name]=json.loads((P/name).read_text())
out={'generated_at_utc':datetime.now(timezone.utc).isoformat(),
     'scope':'Bounded eight-hour research investigation, not exhaustive database review.',
     'analysis_freeze':json.loads((P/'analysis-freeze.json').read_text()),
     'input_manifest':json.loads((P/'input-manifest.json').read_text()),
     'validation':validation,'files':files,
     'exclusions':'This self-referential manifest, working .log files and __pycache__. One-off editing scripts are preserved as history, not regeneration commands.'}
(P/'deliverable-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Hashed',len(files),'research files')
