#!/usr/bin/env python3
"""Compare a selected CLDF reference registry with the last deployed data ref.

Read-only. --base must be resolved from release provenance, not guessed as HEAD.
Primary candidates use installed-form provenance and still require editorial review.
"""
import argparse
import csv
import io
import json
import re
import subprocess
from pathlib import Path


def registry(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    if rows and 'ID' not in rows[0]:
        raise ValueError('Reference registry is missing its ID column')
    result = {row['ID']: row for row in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate reference IDs')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_repo', type=Path)
    parser.add_argument('--base', required=True, help='Data commit/ref used by the previous successful deployment')
    parser.add_argument('--current', type=Path, help='Selected references.csv; defaults to working CLDF registry')
    args = parser.parse_args()
    baseline = subprocess.check_output(
        ['git', '-C', str(args.data_repo), 'show', f'{args.base}:cldf/references.csv'], text=True)
    old = registry(baseline)
    new = registry((args.current or args.data_repo / 'cldf/references.csv').read_text())
    added = [new[k] for k in sorted(new.keys() - old.keys())]
    changed = [{'id': k, 'fields': [f for f in sorted(set(old[k]) | set(new[k])) if old[k].get(f) != new[k].get(f)]}
               for k in sorted(old.keys() & new.keys()) if old[k] != new[k]]
    primary = [r['ID'] for r in added if re.search(r'data/(?:other/)?forms/\d{8}-[^;\s]+\.csv', r.get('Provenance', ''))]
    print(json.dumps({
        'baseline_ref': args.base, 'baseline_references': len(old), 'current_references': len(new),
        'added_count': len(added), 'primary_candidates': primary,
        'other_added_references': [r['ID'] for r in added if r['ID'] not in primary],
        'added': added, 'changed': changed, 'removed': sorted(old.keys() - new.keys()),
        'review_required': 'Inspect expanded existing ingests and distinguish supporting citations from primary ingestions; provenance-based suggestions are not an ingestion count.'
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
