"""Freeze a read-only research view of every existing Shinaic CLDF record.

No source ingestion, lexical correction, or database mutation is performed.
The nearest non-Shinaic attestation ancestor is kept separately from the broader
numbered Turner family. This avoids silently replacing a derivative by a headword.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import unicodedata as ud

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('JAMBU_DATA', HERE.parents[3] / 'data')).resolve()
CLDF = DATA / 'cldf'
INPUTS = ['languages.csv', 'dialects.csv', 'forms.csv', 'edges.csv',
          'references.csv', 'form_concepts.csv', 'concepts.csv',
          'form-source-keys.csv', 'form-id-aliases.csv']


def read(name):
    with (CLDF / name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def write(name, rows, fields=None):
    rows = list(rows)
    with (HERE / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]),
                                delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def plain(s):
    return re.sub('<[^>]+>', '', s)


def source_keys(s):
    return list(dict.fromkeys(re.sub(r'\[.*', '', x) for x in s.split(';') if x))


def order(s):
    m = re.match(r'^(\d+)(.*)', s)
    return (0, int(m[1]), m[2]) if m else (1, 0, s)


def main():
    languages = {r['ID']: r for r in read('languages.csv') if r['Clade'] == 'Shinaic'}
    all_forms = {r['ID']: r for r in read('forms.csv')}
    forms = {k: r for k, r in all_forms.items() if r['Language_ID'] in languages}
    all_edges = read('edges.csv')
    accepted = {r['Child_ID']: r for r in all_edges if r['Rank'] == '1'
                and r['Kind'] in {'reflex', 'borrowed', 'variant'}}
    relevant_edges = [r for r in all_edges if r['Child_ID'] in forms]
    anchors = {}
    ancestors = set()
    corpus = []
    for fid, r in forms.items():
        current, visited, path = fid, set(), []
        anchor = ''
        while current in accepted and current not in visited:
            visited.add(current)
            edge = accepted[current]
            path.append(edge)
            current = edge['Parent_ID']
            assert current in all_forms, current
            ancestors.add(current)
            if all_forms[current]['Language_ID'] not in languages:
                anchor = current
                break
        # Broad family is an identifier, not a reconstructed immediate input.
        family = anchor
        if anchor and re.match(r'^\d+(?:-|$)', anchor):
            family = anchor.split('-')[0]
        elif anchor and all_forms[anchor]['Language_ID'] == 'Indo-Aryan':
            cur, seen = anchor, set()
            while cur in accepted and cur not in seen:
                seen.add(cur)
                cur = accepted[cur]['Parent_ID']
                ancestors.add(cur)
                if re.match(r'^\d+(?:-|$)', cur):
                    family = cur.split('-')[0]
                    break
                if all_forms[cur]['Language_ID'] != 'Indo-Aryan':
                    break
        if family:
            ancestors.add(family)
        anchors[fid] = (anchor, family)
        lects = re.findall(r'dialect:[^\s;]+', r['Tags'])
        copied = {k.lower(): v for k, v in r.items()}
        copied.update(language_name=languages[r['Language_ID']]['Name'],
                      dialect_tags=';'.join(lects),
                      source_keys=';'.join(source_keys(r['Source'])),
                      ancestor_id=anchor, family_id=family,
                      ancestor_form=(all_forms[anchor]['Original'] or all_forms[anchor]['Form']) if anchor else '',
                      ancestor_original=all_forms[anchor]['Original'] if anchor else '',
                      ancestor_form_field=('Original' if all_forms[anchor]['Original'] else 'Form') if anchor else '',
                      ancestor_gloss=all_forms[anchor]['Gloss'] if anchor else '',
                      ancestor_language=all_forms[anchor]['Language_ID'] if anchor else '',
                      family_form=(all_forms[family]['Original'] or all_forms[family]['Form']) if family else '',
                      ancestry_path=json.dumps(path, ensure_ascii=False),
                      link_status=('borrowed' if any(e['Kind']=='borrowed' for e in path)
                                   else 'linked' if anchor else 'unanchored'))
        corpus.append(copied)
    write('corpus.tsv', corpus)
    write('ancestral-records.tsv', [all_forms[k] for k in sorted(ancestors, key=order)])
    write('record-edges.tsv', relevant_edges)
    write('languages.tsv', languages.values())
    references = read('references.csv')
    cited = {s for r in corpus for s in r['source_keys'].split(';')}
    write('references.tsv', [r for r in references if r['ID'] in cited])
    family_forms = defaultdict(list)
    ancestor_forms = defaultdict(list)
    for r in corpus:
        if r['family_id']:
            family_forms[r['family_id']].append(r)
            ancestor_forms[r['ancestor_id']].append(r)
    families = []
    for fid, rows in sorted(family_forms.items(), key=lambda x: order(x[0])):
        p = all_forms[fid]
        family = dict(family_id=fid, headword=p['Original'] or p['Form'], headword_original=p['Original'],
                      headword_field='Original' if p['Original'] else 'Form', gloss=p['Gloss'],
                      tags=p['Tags'], source=p['Source'], etymology=p['Etymology'],
                      records=len(rows),
                      formations=';'.join(sorted({r['ancestor_id'] for r in rows}, key=order)),
                      ancestral_forms='; '.join(dict.fromkeys(r['ancestor_form'] for r in rows)),
                      languages=';'.join(sorted({r['language_id'] for r in rows})))
        for lang in languages:
            # Compact evidence summary only; no information lost from corpus.tsv.
            subset = [r for r in rows if r['language_id']==lang]
            family[lang] = ' | '.join(dict.fromkeys(
                f"{ud.normalize('NFC', r['original'])} [{r['gloss']}; {r['source_keys']}; {r['dialect_tags']}]"
                for r in subset))
        families.append(family)
    write('families.tsv', families)
    coverage = []
    for lang in languages:
        ss = sorted({s for r in corpus if r['language_id']==lang for s in r['source_keys'].split(';')})
        for source in ss:
            rows = [r for r in corpus if r['language_id']==lang and source in r['source_keys'].split(';')]
            coverage.append(dict(language=lang, source=source, records=len(rows),
                                 linked_records=sum(bool(r['family_id']) for r in rows),
                                 families=len({r['family_id'] for r in rows if r['family_id']}),
                                 original_with_acute=sum('\u0301' in ud.normalize('NFD',r['original']) for r in rows),
                                 original_with_grave=sum('\u0300' in ud.normalize('NFD',r['original']) for r in rows),
                                 original_with_stress_mark=sum(any(c in r['original'] for c in ["'",'ˈ','ʹ']) for r in rows)))
    write('coverage-by-source.tsv', coverage)
    manifests = {name: hashlib.sha256((CLDF / name).read_bytes()).hexdigest() for name in INPUTS}
    manifest = dict(input_directory=str(CLDF), input_sha256=manifests,
                    repository_revision=subprocess.check_output(['git','-C',str(DATA),'rev-parse','HEAD'],text=True).strip(),
                    counts=dict(records=len(corpus), nearest_ancestors=len(ancestor_forms),
                                families=len(families),
                                linked_records=sum(bool(r['family_id']) for r in corpus),
                                unanchored_records=sum(not r['family_id'] for r in corpus),
                                records_by_language=dict(Counter(r['language_id'] for r in corpus)),
                                families_by_language={l:sum(l in r['languages'].split(';') for r in families) for l in languages}),
                    notes=['Source counts overlap for merged citations.',
                           'No accent normalization or cognacy proposal is made by this extractor.',
                           'Each family retains its nearest input formation separately.',
                           'Unanchored means no accepted path out of Shinaic; an etymology note may still exist.'])
    (HERE/'input-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest['counts'],indent=2))


if __name__ == '__main__':
    main()
