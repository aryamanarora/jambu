"""Independently reproduce the distributed evidence archive in a fresh directory."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('JAMBU_DATA', HERE.parents[2] / 'data')).resolve()
ARCHIVE = HERE / 'evidence/shinaic-accent-evidence.zip'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return list(csv.DictReader(io.StringIO(path.read_text()), delimiter='\t'))


def main():
    with tempfile.TemporaryDirectory(prefix='shinaic-evidence-check-') as directory:
        root = Path(directory)
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(root)
        manifest = json.loads((root / 'manifest.json').read_text())
        for name, expected in manifest['input_sha256'].items():
            assert sha(DATA / name) == expected, f'Input changed: {name}'
        for name, expected in manifest['appendix_sha256'].items():
            assert sha(root / name) == expected, f'Archive file changed: {name}'
        scripts = ['inventory.py', 'audit_palula.py', 'compare_shina.py',
                   'annotate_families.py', 'annotate_palula_nominals.py',
                   'survey_comparison.py']
        for name in scripts:
            assert sha(root / 'reproduce' / name) == manifest['script_sha256'][name]
            subprocess.run([sys.executable, str(root / 'reproduce' / name)],
                           env={**os.environ, 'JAMBU_DATA': str(DATA)},
                           check=True, capture_output=True, text=True)
        comparisons = {}
        for public, generated in [
            ('palula-nominal-screen.tsv', 'palula-nominal-screen.tsv'),
            ('palula-closed-aa-candidates.tsv', 'palula-closed-aa-nominals.tsv'),
            ('palula-aa-imperatives.tsv', 'palula-aa-imperatives.tsv'),
            ('shina-survey-selected.tsv', 'shina-survey-selected.tsv'),
            ('shina-survey-matrix.tsv', 'shina-survey-matrix.tsv'),
            ('shina-family-screen.tsv', 'shina-family-screen.tsv'),
            ('palula-short-a-test.tsv', 'palula-closed-aa-nominals.tsv'),
        ]:
            expected = rows(root / public)
            actual = rows(root / 'reproduce' / generated)
            if public == 'shina-family-screen.tsv':
                actual = [{k: v for k, v in row.items() if k != 'proto_entry'}
                          for row in actual]
            if public == 'palula-short-a-test.tsv':
                actual = [row for row in actual
                          if row['literal_modern_short_a_alternation'] == 'True']
            assert actual == expected, f'Table did not reproduce: {public}'
            comparisons[public] = len(actual)
        result = {'status': 'passed',
                  'input_hashes_checked': len(manifest['input_sha256']),
                  'scripts_rerun': len(scripts),
                  'public_files_hash_checked': len(manifest['appendix_sha256']),
                  'exact_table_comparisons': comparisons,
                  'zip_sha256': sha(ARCHIVE)}
        (HERE / 'reproduction-check.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
