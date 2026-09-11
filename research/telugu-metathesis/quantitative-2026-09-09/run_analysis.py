#!/usr/bin/env python3
"""Rebuild research annotations/counts from the frozen corpus; no database writes.

Run build_corpus.py separately to extract a new input snapshot, after checking the
input manifest. Amend_* files are one-off editing history, not regeneration steps.
"""
import subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
for name in ['analyse.py','quantify_families.py','analyse_formations.py','review_queue.py',
             'scan_stop_clusters.py','annotate_stop_clusters.py','export_auxiliary.py',
             'quantify_auxiliary.py','lowering_tests.py','compare_languages.py','inspect_annotations.py','coverage_audit.py']:
 with (P/(name.removesuffix('.py')+'.rebuild.log')).open('w') as log:
  result=subprocess.run([sys.executable,str(P/name)],stdout=log,stderr=subprocess.STDOUT,cwd=P)
 print(name, 'OK' if result.returncode==0 else 'FAILED',flush=True)
 if result.returncode:raise SystemExit(result.returncode)
