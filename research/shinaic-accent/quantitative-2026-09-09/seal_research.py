"""Final presentation build, preservation audit, then verified archive."""
from pathlib import Path
import json,subprocess,sys
HERE=Path(__file__).resolve().parent
reproduction=json.loads((HERE/'reproduction-audit.json').read_text())
assert len(reproduction)==22 and all(r['exit_code']==0 for r in reproduction)
for script in ['build_final.py','audit_analysis.py','package_research.py']:
    result=subprocess.run([sys.executable,str(HERE/script)],cwd=HERE,capture_output=True,text=True)
    (HERE/(script.removesuffix('.py')+'-seal.log')).write_text(result.stdout+result.stderr)
    print(script,result.returncode,flush=True)
    if result.returncode:
        print(result.stdout,result.stderr);raise SystemExit(result.returncode)
