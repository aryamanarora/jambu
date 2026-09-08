"""Publish a compact, attributed research appendix; never modify lexical sources.

Run the six analysis scripts first. The resulting static files are derived
research aids, not a new Jambu source ingestion or accepted etymology layer.
"""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[1]
DATA = Path(os.environ.get('JAMBU_DATA', HERE.parents[2] / 'data')).resolve()
PUBLIC = SITE / 'static/research/shinaic-accent'
SCRIPTS = ['inventory.py', 'audit_palula.py', 'compare_shina.py',
           'annotate_families.py', 'annotate_palula_nominals.py',
           'survey_comparison.py']
INPUTS = ['data/other/forms/20220913-palula.csv',
          'data/other/forms/20230621-shina.csv', 'data/cdial/params.csv',
          'data/other/forms/raw_data/northern',
          'data/other/forms/raw_data/northern_param',
          'cldf/forms.csv', 'cldf/form-source-keys.csv', 'cldf/form-id-aliases.csv']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return list(csv.DictReader((HERE / name).open(), delimiter='\t'))


def write(name, rows):
    with (PUBLIC / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0], delimiter='\t')
        w.writeheader()
        w.writerows(rows)


def main():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    write('palula-nominal-screen.tsv', read('palula-nominal-screen.tsv'))
    # Full Turner paragraphs are unnecessary for this comparison. Preserve
    # the family ID, headword, lexical forms, manual assessment and row locators.
    write('shina-family-screen.tsv', [
        {k: v for k, v in r.items() if k != 'proto_entry'}
        for r in read('shina-family-screen.tsv')])
    aa = read('palula-closed-aa-nominals.tsv')
    write('palula-closed-aa-candidates.tsv', aa)
    write('palula-short-a-test.tsv', [
        r for r in aa if r['literal_modern_short_a_alternation'] == 'True'])
    for name in ['palula-aa-imperatives.tsv', 'shina-survey-selected.tsv',
                 'shina-survey-matrix.tsv', 'source-readings.tsv',
                 'evidence-ledger.tsv', 'rule-ledger.tsv', 'nasal-backing-screen.tsv']:
        shutil.copyfile(HERE / name, PUBLIC / name)
    shutil.copyfile(HERE / 'APPENDIX.md', PUBLIC / 'README.md')
    summaries = {name: json.loads((HERE / name).read_text()) for name in [
        'inventory-summary.json', 'palula-audit-summary.json',
        'palula-nominal-screen-summary.json', 'shina-comparison-summary.json',
        'shina-survey-summary.json']}
    manifest = {
        'date': '2026-09-08', 'author': 'Codex (AI agent)',
        'purpose': 'Research appendix to How the Shinaic languages got their accents',
        'data_repository': 'https://github.com/moli-mandala/data',
        'data_commit': subprocess.check_output(
            ['git', '-C', str(DATA), 'rev-parse', 'HEAD'], text=True).strip(),
        'input_sha256': {name: sha(DATA / name) for name in INPUTS},
        'script_sha256': {name: sha(HERE / name) for name in SCRIPTS},
        'summaries': summaries,
        'limitations': [
            'Counts measure selected records and notation, not sound-law accuracy.',
            'Manual screens are provisional; only central examples have independent page checks.',
            'Source readings are preserved; corrections are recorded separately.',
            'Shared family IDs do not prove that every form continues the same formation.',
            'The article does not change accepted etymologies or lexical source files.',
        ],
        'appendix_sha256': {p.name: sha(p) for p in sorted(PUBLIC.iterdir())
                           if p.is_file() and p.suffix in {'.tsv', '.md'}},
    }
    (PUBLIC / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    archive = PUBLIC / 'shinaic-accent-evidence.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(PUBLIC.iterdir()):
            if p.is_file() and p != archive:
                z.write(p, p.name)
        for name in SCRIPTS:
            z.write(HERE / name, f'reproduce/{name}')
    print(json.dumps({'files': len(manifest['appendix_sha256']),
                      'archive_bytes': archive.stat().st_size,
                      'archive_sha256': sha(archive)}, indent=2))


if __name__ == '__main__':
    main()
