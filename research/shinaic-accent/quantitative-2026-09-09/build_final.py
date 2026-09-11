"""Build the presentation around the frozen analysis; no new corpus extraction."""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
NODE='/Users/aryamanarora/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
for script in ['source_register.py','build_appendices.py','build_reference_appendices.py','render_report.mjs','audit_presentation.py']:
    run=subprocess.run([NODE if script.endswith('.mjs') else sys.executable,str(HERE/script)],cwd=HERE,capture_output=True,text=True)
    (HERE/(script.rsplit('.',1)[0]+'-final.log')).write_text(run.stdout+run.stderr)
    print(script,run.returncode,flush=True)
    if run.returncode:
        print(run.stdout,run.stderr);raise SystemExit(run.returncode)
