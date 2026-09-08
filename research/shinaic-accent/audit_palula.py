"""Audit two restricted Palula patterns in the existing dictionary inventory.

These are descriptive checks, not a cognate classifier or a reconstruction.
Run inventory.py first. This script never changes Jambu's lexical data.
"""
import csv
import json
import re
import unicodedata as ud
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOWELS = 'aeiouáéíóú'


def unaccent(s):
    return ud.normalize('NFC', ud.normalize('NFD', s).replace('\u0301', ''))


def write(name, rows):
    with (HERE / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter='\t')
        w.writeheader()
        w.writerows(rows)


def main():
    rows = list(csv.DictReader((HERE / 'inventory.tsv').open(), delimiter='\t'))
    imperatives, nominals = [], []
    for r in rows:
        for m in re.finditer(r'\(Imp\):\s*([^;\n]+)', r['inflection']):
            imp = m.group(1)
            if re.search(r'áa|aá', imp):
                imperatives.append({
                    'jambu_id': r['jambu_id'], 'headword': r['headword'],
                    'imperative': imp, 'aa_accent': 'late' if 'aá' in imp else 'early',
                    'turner': r['turner'], 'etymology': r['etymology'],
                    'inflection': r['inflection'],
                })
        head = r['headword']
        if ' ' in head or not set(r['tags'].split()) & {'noun', 'adj'}:
            continue
        m = re.search(r'(áa|aá)([^' + VOWELS + r']+)$', head)
        if not m:
            continue
        stem_match = re.search(r'Morphemic form:\s*([^;]+)', r['inflection'])
        stem = stem_match.group(1).strip() if stem_match else ''
        preceding = head[:m.start()]
        pretonic = any(c in VOWELS for c in preceding)
        aspirated_onset = 'h' in re.split('[' + VOWELS + ']', preceding)[-1]
        prediction = 'late' if pretonic or aspirated_onset else 'early'
        actual = 'late' if m.group(1) == 'aá' else 'early'
        # This tests a conservative literal stem alternation, not old vowel length.
        shortened = unaccent(head[:m.start()] + 'a' + m.group(2))
        short_stem = unaccent(stem.strip('-')) == shortened
        nominals.append({
            'jambu_id': r['jambu_id'], 'headword': head, 'gloss': r['gloss'],
            'turner': r['turner'], 'morphemic_form': stem,
            'literal_modern_short_a_alternation': short_stem,
            'aspirated_onset': aspirated_onset, 'pretonic_syllable': pretonic,
            'prediction_if_late_lengthening': prediction, 'observed': actual,
            'matches_prediction': prediction == actual,
            'source_marks_loan': r['etymology'].startswith('Origin:'),
            'etymology': r['etymology'], 'inflection': r['inflection'],
        })
    write('palula-aa-imperatives.tsv', imperatives)
    write('palula-closed-aa-nominals.tsv', nominals)
    summary = {
        'explicit_aa_imperatives': len(imperatives),
        'early_aa_imperatives': sum(r['aa_accent'] == 'early' for r in imperatives),
        'all_closed_aa_nominals': len(nominals),
        'literal_modern_short_a_alternation': sum(r['literal_modern_short_a_alternation'] for r in nominals),
        'limitations': [
            'The imperative count covers explicitly supplied forms only.',
            'Modern alternation does not by itself establish historical short a.',
            'Loans, historical long vowels and contractions are not eligible tests of late short-a lengthening.',
            'No rule success percentage is computed before manual historical annotation.',
        ],
    }
    (HERE / 'palula-audit-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
