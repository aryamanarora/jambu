#!/usr/bin/env python3
"""Verify saved research-file hashes without modifying any deliverable."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
manifest=json.loads((P/'deliverable-manifest.json').read_text())
errors=[]
for row in manifest['files']:
    path=P/row['path']
    if not path.is_file():
        errors.append(row['path']+': missing');continue
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    if h.hexdigest()!=row['sha256'] or path.stat().st_size!=row['bytes']:
        errors.append(row['path']+': changed')
print(json.dumps({'status':'PASS' if not errors else 'FAIL',
                  'files_checked':len(manifest['files']),'errors':errors},indent=2))
if errors:raise SystemExit(1)
