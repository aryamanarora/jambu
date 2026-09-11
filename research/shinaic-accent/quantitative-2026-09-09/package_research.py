"""Bundle the audited report, complete appendices and reproducible analysis."""
from pathlib import Path
import hashlib,json,zipfile

HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'artifact-manifest.json').read_text())
assert json.loads((HERE/'integrity-audit.json').read_text())['status']=='passed'
assert json.loads((HERE/'presentation-audit.json').read_text())['status']=='passed'
names=sorted(set(manifest['files'])|{'artifact-manifest.json'})
output=HERE.parent/(HERE.name+'.zip')
if output.exists():raise SystemExit('Archive already exists; preserve it or remove it deliberately before rebuilding: '+str(output))
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in names:
        p=HERE/name
        if name in manifest['files']:
            assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest['files'][name]['sha256'],('manifest drift',name)
        z.write(p,str(Path(HERE.name)/name))
with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(names)
digest=hashlib.sha256(output.read_bytes()).hexdigest()
audit=dict(archive=str(output),files=len(names),bytes=output.stat().st_size,sha256=digest,crc_check='passed',
           scope='All files in the final artifact manifest, plus the manifest itself. Mutable working checkpoints, runtime logs and Python caches are excluded.')
(output.with_suffix('.zip.audit.json')).write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit,indent=2))
