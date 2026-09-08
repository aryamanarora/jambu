"""Read-only inventory of the existing Palula dictionary ingestion.

Run from any directory with Python 3. Outputs research files beside this script;
does not install or change lexical data. Classification is descriptive, not an
automatic proof of cognacy or a reconstruction of sound changes.
"""
from pathlib import Path
import csv
import hashlib
import json
import os
import re
import unicodedata as ud
from collections import Counter

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('JAMBU_DATA', HERE.parents[2] / 'data')).resolve()
SOURCE = DATA / 'data/other/forms/20220913-palula.csv'


def nfc(s):
    return ud.normalize('NFC', s)


def clusters(s):
    result = []
    for c in ud.normalize('NFD', s):
        if ud.combining(c) and result:
            result[-1] += c
        else:
            result.append(c)
    return result


def vowels(s, sanskrit=False):
    """Vowel tokens with acute preserved, not a full syllabification algorithm.

    Sanskrit ai/au are single nuclei, regardless of which letter bears the
    transcription's acute. Modern Palula sequences remain separate mora tokens.
    """
    out = []
    cs = clusters(s)
    i = 0
    while i < len(cs):
        c = cs[i]
        if sanskrit and c[0] == 'a' and '\u0304' not in c and i + 1 < len(cs) and cs[i + 1][0] in 'iu':
            pair = c + cs[i + 1]
            out.append({'position': i, 'text': nfc(pair), 'vowel': c[0] + cs[i + 1][0],
                        'accent': '\u0301' in pair, 'length': 2})
            i += 2
            continue
        if c[0] in 'aeiou' or (sanskrit and c[0] in 'rl' and any(mark in c for mark in ('\u0325', '\u0323'))):
            long = '\u0304' in c or (sanskrit and c[0] in 'eo')
            out.append({'position': i, 'text': nfc(c), 'vowel': c[0],
                        'accent': '\u0301' in c, 'length': 2 if long else 1})
        i += 1
    return out


def palula_accent(s):
    cs = clusters(s)
    vs = vowels(s)
    accented = [v for v in vs if v['accent']]
    if not accented:
        return 'implicit-short' if len(vs) == 1 else 'unmarked'
    if len(accented) != 1:
        return 'multiple'
    v = accented[0]
    i = v['position']
    if i and cs[i-1][0] == v['vowel']:
        return 'second-mora'
    if i+1 < len(cs) and cs[i+1][0] == v['vowel']:
        return 'first-mora'
    return 'short-or-diphthong'


def main():
    with SOURCE.open(newline='') as f:
        rows = list(csv.reader(f))
    aliases = {r['Legacy_ID']: r['Form_ID'] for r in csv.DictReader(
        (DATA / 'cldf/form-id-aliases.csv').open())}
    source_ids = {r['Source_Key']: aliases.get(r['Legacy_ID'], '')
                  for r in csv.DictReader((DATA / 'cldf/form-source-keys.csv').open())}
    compiled = [r for r in csv.DictReader((DATA / 'cldf/forms.csv').open())
                if r['Language_ID'] == 'Phal' and 'liljegren' in r['Source'].split(';')]
    by_original = {}
    for r in compiled:
        by_original.setdefault(nfc(r['Original']), []).append(r)
    main_rows = [r for r in rows if not r[11] and '-turner-' not in r[10]]
    inventory = []
    for row in main_rows:
        lang, turner, form, gloss, native, phonemic, notes, source, _, etym, key, *_ = row
        # Retain the complete unmodified source claim too: this first-token field
        # is just a search aid, and may not be the immediate historical ancestor.
        first = re.split(r"\s|[;]", etym, maxsplit=1)[0]
        old_vowels = vowels(first, sanskrit=True)
        old_accent = [i for i,v in enumerate(old_vowels) if v['accent']]
        jambu_id = source_ids.get(key, '')
        id_basis = 'source-key alias' if jambu_id else ''
        if not jambu_id:
            # Earlier cross-source merges sometimes remove the newer source key.
            # Accept only an unambiguous original spelling + full etymology match
            # among rows explicitly carrying the same bibliographic citation.
            candidates = [r for r in by_original.get(nfc(form), [])
                          if nfc(r['Etymology']) == nfc(etym)]
            if len(candidates) == 1:
                jambu_id = candidates[0]['ID']
                id_basis = 'unique cited original and full etymology'
        inventory.append({
            'source_key': key, 'jambu_id': jambu_id, 'id_basis': id_basis,
            'headword': nfc(form), 'gloss': gloss, 'tags': row[14],
            'accent_type': palula_accent(form),
            'turner': turner, 'first_proto_form': nfc(first),
            'proto_accent_nucleus': ','.join(str(i+1) for i in old_accent),
            'proto_nuclei': len(old_vowels),
            'etymology': nfc(etym), 'inflection': nfc(notes),
        })
    for filename, data in [
        ('inventory.tsv', inventory),
        ('accented-etymologies.tsv', [r for r in inventory if r['turner'] and r['proto_accent_nucleus']]),
        ('accented-nominals.tsv', [r for r in inventory if r['turner'] and r['proto_accent_nucleus']
                                  and set(r['tags'].split()) & {'noun', 'adj', 'num'}]),
    ]:
        with (HERE / filename).open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=inventory[0].keys(), delimiter='\t')
            w.writeheader()
            w.writerows(data)
    manifest = {
        'source': str(SOURCE.relative_to(DATA.parent)),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'raw_rows': len(rows), 'main_entries': len(inventory),
        'main_entries_with_turner': sum(bool(r['turner']) for r in inventory),
        'main_entries_with_etymology_or_origin': sum(bool(r['etymology']) for r in inventory),
        'main_entries_with_first_proto_accent_and_turner': sum(bool(r['turner'] and r['proto_accent_nucleus']) for r in inventory),
        'accent_types': dict(Counter(r['accent_type'] for r in inventory)),
        'missing_jambu_ids': [r['source_key'] for r in inventory if not r['jambu_id']],
        'limitations': [
            'Entry counts are not independent etymological-family counts.',
            'Acute marks are inventoried, not repaired or inferred in Sanskrit.',
            'First proto-form may be a remote ancestor or derivative base.',
            'Sanskrit ai/au are grouped; unusual source spellings and morphological boundaries still require manual review.',
            'Closed syllables and source-specific phonetics require manual analysis.',
        ],
    }
    (HERE / 'inventory-summary.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
