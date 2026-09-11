"""Read-only comparison of Schmidt & Kaul's six Shina varieties with Palula.

This script inventories existing source rows. It neither ingests a source nor
accepts new etymologies. Turner identifiers are the database's proposed links;
they are not independently proved here. Brokskat accent marks indicate stress,
not the pitch-accent contrast used for the other five varieties.
"""
import csv
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from inventory import nfc, palula_accent, vowels

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('JAMBU_DATA', HERE.parents[2] / 'data')).resolve()
SOURCE = DATA / 'data/other/forms/20230621-shina.csv'
PARAMS = DATA / 'data/cdial/params.csv'
DIALECTS = ('gil', 'koh', 'gur', 'Astor', 'dr', 'bro')


def main():
    rows = list(csv.reader(SOURCE.open()))
    params = {r[0]: r for r in csv.reader(PARAMS.open())}
    palula = defaultdict(list)
    for r in csv.DictReader((HERE / 'inventory.tsv').open(), delimiter='\t'):
        if r['turner']:
            palula[r['turner']].append(r)
    grouped = defaultdict(lambda: defaultdict(list))
    for i, r in enumerate(rows, 1):
        if r[1]:
            grouped[r[1]][r[0]].append((i, r))
    out = []
    for root, groups in sorted(grouped.items(), key=lambda p: (not p[0].isdigit(), int(p[0]) if p[0].isdigit() else p[0])):
        p = params.get(root, [root, '', '', ''])
        old = p[1]
        ov = vowels(old, sanskrit=True)
        accents = [i+1 for i,v in enumerate(ov) if v['accent']]
        r = {'turner': root, 'proto_headword': old,
             'proto_accent_nucleus': ','.join(map(str, accents)),
             'proto_nuclei': len(ov),
             'source_glosses': '; '.join(dict.fromkeys(x[1][3] for g in groups.values() for x in g)),
             'palula': '; '.join(f"{x['headword']} [{x['gloss']}]" for x in palula[root])}
        for d in DIALECTS:
            r[d] = '; '.join(dict.fromkeys(nfc(x[1][2]) for x in groups.get(d, [])))
        r['source_rows'] = '; '.join(f'{d}:{i}' for d, g in groups.items() for i, _ in g)
        r['proto_entry'] = re.sub('<[^>]+>', '', p[3])
        out.append(r)
    for name, subset in [('shina-comparison.tsv', out), ('shina-accented-comparison.tsv', [r for r in out if r['proto_accent_nucleus']])]:
        with (HERE / name).open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=out[0], delimiter='\t')
            w.writeheader(); w.writerows(subset)
    manifest = {
        'source': str(SOURCE.relative_to(DATA.parent)),
        'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'rows': len(rows),
        'varieties': dict(Counter(r[0] for r in rows)),
        'linked_rows': sum(bool(r[1]) for r in rows),
        'non_turner_linked_rows': sum(bool(r[1]) and not r[1].isdigit() for r in rows),
        'linked_families': len(out),
        'families_with_accent_in_turner_headword': sum(bool(r['proto_accent_nucleus']) for r in out),
        'families_with_palula_comparanda': sum(bool(r['palula']) for r in out),
        'cautions': ['Brokskat marks stress, not mora accent.',
                     'Unlinked items are excluded from cognate grouping, not from the source inventory.',
                     'Each Turner family is counted once; multiple dictionary formations may share an ID.',
                     'Rows and proposed source etymologies need manual verification before sound-law counts.'],
    }
    (HERE / 'shina-comparison-summary.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
