"""Preserve an existing DB subentry needed by a verified reference correction.

The raw ancestry walk did not visit10310-2 because Strand's ram reference was
misnumbered10301.2. The data file must still match the original frozen hash.
"""
import csv,json,hashlib
from pathlib import Path
from analysis_data import HERE,write_tsv
def main():
    m=json.loads((HERE/'input-manifest.json').read_text());p=Path(m['input_directory'])/'forms.csv'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==m['input_sha256']['forms.csv']
    rows=[r for r in csv.DictReader(p.open()) if r['ID']=='10310-2'];assert len(rows)==1
    write_tsv('supplementary-ancestors.tsv',rows)
    (HERE/'supplementary-ancestor-provenance.json').write_text(json.dumps(dict(record_id='10310-2',source_file=str(p),source_sha256=m['input_sha256']['forms.csv'],reason='Existing subentry required by source-verified ram reference correction, record_decisions_02.jsonl:1; original ancestry extract remains unchanged.'),indent=2)+'\n')
if __name__=='__main__':main()
