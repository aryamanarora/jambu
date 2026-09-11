#!/usr/bin/env python3
"""Regenerate final presentation and independent checks after run_analysis.py.

Requires optional Markdown and matplotlib packages; no database/site writes.
"""
import subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
for name in ['source-index.py','render_appendices.py','validate_final.py','write_report.py',
             'check_report.py','plot_results.py','render_report_html.py','build_manifest.py']:
    result=subprocess.run([sys.executable,str(P/name)],cwd=P)
    if result.returncode:raise SystemExit(result.returncode)
