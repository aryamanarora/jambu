#!/usr/bin/env python3
"""Freeze a read-only Dravidian research corpus; no historical outcomes inferred.

Standard library only. Run from any directory. Outputs stay beside this script.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[3] / 'data'
VOWELS = 'aeiouāēīōūăĕĭŏŭɛɔəɨɯ'
APICALS = 'rṟlḷẓḻḍṭṯṛnṇ'

def read(path):
    with path.open(encoding='utf-8', newline='') as f:
        yield from csv.DictReader(f)

def write(name, rows, fields=None):
    rows = list(rows)
    fields = fields or (list(rows[0]) if rows else [])
    with (HERE / name).open('w', encoding='utf-8', newline='') as f:
        out = csv.DictWriter(f, fields, delimiter='\t', extrasaction='ignore')
        out.writeheader()
        out.writerows(rows)

def norm(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if c not in {'\u0301','\u0300'})
    return unicodedata.normalize('NFC', s).replace('ṛ̆', 'ẓ').replace('r̤', 'ẓ').replace('ḻ', 'ẓ').strip()

def input_flags(s):
    s = norm(s).lstrip('*').lower()
    s = re.sub(r'<[^>]*>', '', s)
    # No rule application: an inclusive screen for comparative reading.
    s = s.replace('-', '')
    found = []
    c = '[^' + VOWELS + r'\W\d_]'
    if re.match(f'^(?:{c})?[aeiou][{APICALS}]', s):
        found.append('short-vowel-apical')
    if re.match(f'^(?:{c})?[āēīōū][{APICALS}]', s):
        found.append('long-vowel-apical-control')
    if re.match(f'^(?:{c})?[aeiou]([{APICALS}])\\1', s):
        found.append('geminate-apical-control')
    if re.match(f'^(?:{c})?[aeiou][{APICALS}]{c}', s):
        found.append('postapical-cluster')
    if re.match(f'^(?:{c})?[aeiou][kgcjśsṣtdpbmvywh]', s):
        found.append('nonapical-control')
    return found

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cldf', type=Path, default=DATA / 'cldf')
    parser.add_argument('--verify-only', action='store_true', help='Compare current input hashes with the frozen manifest; write nothing')
    parser.add_argument('--allow-new-inputs', action='store_true', help='Explicitly replace this extraction with changed inputs; use a separate copy for a new investigation')
    args = parser.parse_args()
    cldf = args.cldf
    names = ['forms','edges','languages','dialects','references','comparisons',
             'entry-texts','pdr-headword-audit','form-id-aliases','form-source-keys']
    paths = [cldf / (n + '.csv') for n in names]
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    existing=HERE/'input-manifest.json'
    old=json.loads(existing.read_text())['input_sha256'] if existing.exists() else None
    changed=[name for name,value in hashes.items() if old is not None and old.get(name)!=value]
    if args.verify_only:
        print(json.dumps({'match':old is not None and not changed,'changed_files':changed,'manifest_exists':old is not None},indent=2))
        raise SystemExit(0 if old is not None and not changed else 1)
    if changed and not args.allow_new_inputs:
        raise SystemExit('Refusing to overwrite the frozen extraction: changed inputs '+', '.join(changed)+'. Use the saved corpus for recounting, or explicitly --allow-new-inputs in a separate investigation copy.')
    languages = {r['ID']:r for r in read(cldf/'languages.csv')}
    drav = {k for k,r in languages.items() if 'Dravidian' in r['Clade'] or 'Dravidian' in r['Name'] or r['Clade']=='Brahui'}
    proto = {k for k,r in languages.items() if r['Name'].startswith('Proto-')} | {'Drav'}
    forms = {r['ID']:r for r in read(cldf/'forms.csv')}
    edges = list(read(cldf/'edges.csv'))
    parent = {}
    for e in edges:
        if e['Kind'] in {'reflex','variant','borrowed'} and e['Rank']=='1':
            assert e['Child_ID'] not in parent, e['Child_ID']
            parent[e['Child_ID']] = e
    memo = {}
    def ancestry(fid):
        if fid in memo:
            return memo[fid]
        trail = []
        seen = set()
        node = fid
        while node in parent:
            assert node not in seen, ('cycle', fid, node)
            seen.add(node)
            e = parent[node]
            trail.append(e)
            node = e['Parent_ID']
        memo[fid] = (node, trail)
        return memo[fid]
    selected = {fid for fid,r in forms.items() if r['Language_ID'] in drav}
    selected |= {fid for fid in forms if re.fullmatch(r'd\d+[a-z]?',fid)}
    for fid in list(selected):
        root, trail = ancestry(fid)
        selected.add(root)
        selected.update(e['Parent_ID'] for e in trail)
    # Include non-Dravidian loans/reflexes on the same DEDR trees for contact evidence.
    dedr = {fid for fid in selected if re.fullmatch(r'd\d+[a-z]?',fid)}
    for fid in forms:
        if fid in selected:
            continue
        root, trail = ancestry(fid)
        if root in dedr or any(e['Parent_ID'] in dedr for e in trail):
            selected.add(fid)
    audit = {r['Parameter_ID']:r for r in read(cldf/'pdr-headword-audit.csv')}
    groups = defaultdict(list)
    records = []
    for fid in sorted(selected):
        r = forms[fid]
        root, trail = ancestry(fid)
        did = next((n for n in [fid]+[e['Parent_ID'] for e in trail] if n in dedr), '')
        group = did or root
        record = r | {
            'Research_Group':group, 'DEDR_ID':did, 'Accepted_Root_ID':root,
            'Immediate_Parent_ID':parent.get(fid,{}).get('Parent_ID',''),
            'Immediate_Kind':parent.get(fid,{}).get('Kind',''),
            'Borrowed_In_Path':int(any(e['Kind']=='borrowed' for e in trail)),
            'Clade':languages.get(r['Language_ID'],{}).get('Clade',''),
            'Is_Dravidian':int(r['Language_ID'] in drav),
            'Candidate_Flags':';'.join(input_flags(r['Form'])),
        }
        records.append(record)
        groups[group].append(record)
    write('corpus.tsv', records)
    write('languages.tsv',[languages[k] for k in sorted(drav)])
    write('dialects.tsv',[r for r in read(cldf/'dialects.csv') if r['Language_ID'] in drav])
    write('record-edges.tsv',[e for e in edges if e['Child_ID'] in selected or e['Parent_ID'] in selected])
    write('comparisons.tsv',[r for r in read(cldf/'comparisons.csv') if r['Entry_ID'] in selected or r['Compared_Entry_ID'] in selected])
    write('entry-texts.tsv',[r for r in read(cldf/'entry-texts.csv') if r['Form_ID'] in selected])
    write('headword-audit.tsv',[r for k,r in audit.items() if k in selected])
    write('references.tsv',read(cldf/'references.csv'))
    family_rows=[]
    for gid, rows in sorted(groups.items()):
        recon=[r for r in rows if r['Language_ID'] in proto & drav and '*' in r['Form'] and 'not-reconstructed' not in r['Tags']]
        att=[r for r in rows if r['Language_ID'] in drav and r['Language_ID'] not in proto]
        tel=[r for r in att if r['Language_ID']=='Telugu']
        flags=Counter(f for r in recon for f in input_flags(r['Form']))
        comparative_flags=Counter(f for r in att if r['Language_ID']!='Telugu' for f in input_flags(r['Form']))
        family_rows.append({
            'Group_ID':gid,'Display_Form':forms[gid]['Form'],'Display_Gloss':forms[gid]['Gloss'],
            'Head_Strategy':audit.get(gid,{}).get('Strategy',''),
            'N_Records':len(rows),'N_Attested':len(att),'N_Telugu_Records':len(tel),
            'Languages':';'.join(sorted({r['Language_ID'] for r in att})),
            'Reconstructions':' | '.join(dict.fromkeys(r['Form'] for r in recon)),
            'Reconstruction_IDs':';'.join(r['ID'] for r in recon),
            'Reconstructed_Input_Flags':';'.join(sorted(flags)),
            'Comparative_Input_Flags':';'.join(sorted(comparative_flags)),
            'Telugu_Forms':' | '.join(dict.fromkeys(r['Form'] for r in tel)),
            'Status':forms[gid]['Status'],
        })
    write('families.tsv',family_rows)
    with (HERE/'groups.jsonl').open('w',encoding='utf-8') as f:
        for gid,rows in sorted(groups.items()):
            f.write(json.dumps({'id':gid,'head':forms[gid],'audit':audit.get(gid,{}),'records':rows},ensure_ascii=False)+'\n')
    counts=Counter((r['Language_ID'],r['Status'],r['Immediate_Kind']) for r in records if r['Is_Dravidian'])
    write('coverage.tsv',[{'Language_ID':k[0],'Status':k[1],'Immediate_Kind':k[2],'N_Records':v} for k,v in sorted(counts.items())])
    manifest={
        'input_sha256':hashes,
        'total_forms':len(forms),'total_edges':len(edges),'selected_records':len(records),
        'dravidian_language_ids':sorted(drav),'research_groups':len(groups),
        'reconstructed_or_generic_language_ids':sorted(proto & drav),
        'dedr_groups':len(dedr),
        'telugu_bearing_groups':sum(bool(r['N_Telugu_Records']) for r in family_rows),
        'telugu_bearing_dedr_groups':sum(bool(r['N_Telugu_Records']) and r['Group_ID'] in dedr for r in family_rows),
        'warning':'Inventory and input screens only. No record is automatically classified as metathesis or reconstructed cognacy.'
    }
    (HERE/'input-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
