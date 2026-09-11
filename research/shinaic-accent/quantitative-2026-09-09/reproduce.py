"""Reproduce the quantitative views from the frozen corpus and adjudications.

Does not re-extract the live database, access the network, or change any source.
Manual research JSONL and reviewed paradigm TSV files are analytical inputs.
Run from any directory: python3 /absolute/path/to/reproduce.py
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent
PROGRAMS=[
 'phonology_fixtures.py','analysis_data.py','quantify.py',
 'palula_pairs.py','adjective_test.py','adjective_extension.py',
 'structural_screens.py','kalkoti_pairs.py','kalkoti_adjudication.py',
 'old_long_nominals.py','dras_suffix_accent.py',
 'vowel_raising_pairs.py','vowel_raising_adjudication.py',
 'umlaut_nouns.py','idecl_extension.py','numeral_series.py','kundal_paradigms.py',
 # Refresh record exports after the reviewed structural annotations above.
 'analysis_data.py','quantify.py','old_long_nominals.py','class_counterparts.py','residual_ledger.py',
]
def main():
    log=[]
    for name in PROGRAMS:
        start=time.monotonic()
        r=subprocess.run([sys.executable,str(HERE/name)],capture_output=True,text=True,cwd=HERE)
        (HERE/(name.removesuffix('.py')+'-reproduce.log')).write_text(r.stdout+r.stderr)
        log.append(dict(program=name,exit_code=r.returncode,seconds=round(time.monotonic()-start,3)))
        print(name,r.returncode,flush=True)
        if r.returncode:
            print(r.stdout,r.stderr);raise SystemExit(r.returncode)
    (HERE/'reproduction-audit.json').write_text(json.dumps(log,indent=2)+'\n')
if __name__=='__main__':main()
