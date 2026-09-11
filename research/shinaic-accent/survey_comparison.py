"""Compare selected concepts in the existing Backstrom/Radloff Shina data.

The original survey's phonetic field notation is retained. An unmarked form is
not classified as toneless. Concept grouping does not assert cognacy.
"""
import csv
import hashlib
import json
import os
import unicodedata as ud
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('JAMBU_DATA', HERE.parents[2] / 'data')).resolve()
RAW = DATA / 'data/other/forms/raw_data'
CONCEPTS = {
    'eye', 'ear', 'tooth', 'tongue', 'house', 'firewood', 'broom', 'star',
    'stone', 'fire', 'meat', 'name', 'mother', 'brother', 'day', 'night',
    'month', 'year', 'new', 'hot', 'light', 'red', 'head', 'hand',
}


def main():
    source = RAW / 'northern'
    params = {r['ID']: r for r in csv.DictReader((RAW / 'northern_param').open())}
    selected = []
    grouped = defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader(source.open()):
        if not r['Parameter_ID'].startswith('Backstrom-1992-210f-'):
            continue
        concept = params[r['Parameter_ID']]['Name']
        if concept not in CONCEPTS:
            continue
        form = ud.normalize('NFC', r['Form'])
        selected.append({
            'source_id': r['ID'], 'locality': r['Language_ID'],
            'concept': concept, 'form': form, 'source_value': r['Value'],
            'source_comment': r['Comment'],
            'has_explicit_pitch_diacritic': any(c in ud.normalize('NFD', form) for c in ['\u0300', '\u0301', '\u030c', '\u0302']),
            'caution': 'Field transcription, not a uniform phonemic analysis; unmarked pitch is not proven absence of lexical tone',
        })
        grouped[concept][r['Language_ID']].append(form)
    with (HERE / 'shina-survey-selected.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=selected[0].keys(), delimiter='\t')
        w.writeheader(); w.writerows(selected)
    localities = sorted({r['locality'] for r in selected})
    with (HERE / 'shina-survey-matrix.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['concept', *localities], delimiter='\t')
        w.writeheader()
        for c, forms in sorted(grouped.items()):
            w.writerow({'concept': c, **{l: '; '.join(dict.fromkeys(v)) for l,v in forms.items()}})
    summary = {
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'selected_rows': len(selected), 'concepts': len(grouped),
        'localities': localities,
        'pitch_marked_rows': sum(r['has_explicit_pitch_diacritic'] for r in selected),
        'primary_source': 'Backstrom & Radloff 1992, Languages of Northern Areas; transcription pp147–148, 209; lists pp302–369',
        'warning': 'Counts measure coverage and explicit notation, not sound-law fit or historical absence of accent.',
    }
    (HERE / 'shina-survey-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
