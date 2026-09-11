#!/usr/bin/env python3
"""Read-only compact corpus inspection; output is never an annotation decision."""
import argparse
import csv
import json
import re
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
def rows(name):
    with (HERE/name).open(encoding='utf-8',newline='') as f:
        yield from csv.DictReader(f,delimiter='\t')

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='mode',required=True)
    sub.add_parser('summary')
    f=sub.add_parser('families')
    f.add_argument('--flag',default='short-vowel-apical')
    f.add_argument('--basis',choices=['reconstructed','comparative','either'],default='reconstructed')
    f.add_argument('--telugu',action='store_true')
    f.add_argument('--offset',type=int,default=0)
    f.add_argument('--limit',type=int,default=40)
    panel=sub.add_parser('panel')
    panel.add_argument('ids',nargs='+')
    panel.add_argument('--max',type=int,default=15)
    panel.add_argument('--form-ids',action='store_true')
    panel.add_argument('--lang',default='')
    s=sub.add_parser('search')
    s.add_argument('pattern')
    s.add_argument('--lang',default='')
    s.add_argument('--field',default='Form')
    s.add_argument('--limit',type=int,default=60)
    a=p.parse_args()
    if a.mode=='summary':
        fs=list(rows('families.tsv'))
        dedr=[r for r in fs if re.fullmatch(r'd\d+[a-z]?',r['Group_ID'])]
        print('Inventory groups',len(fs),'DEDR',len(dedr))
        for subset,name in [(dedr,'DEDR'),([r for r in dedr if int(r['N_Telugu_Records'])],'Telugu DEDR')]:
            print(name, len(subset),'head strategies',dict(Counter(r['Head_Strategy'] for r in subset)))
            for key in ['Reconstructed_Input_Flags','Comparative_Input_Flags']:
                print(key,dict(Counter(f for r in subset for f in set(r[key].split(';')) if f)))
        print('Language record totals',dict(Counter(r['Language_ID'] for r in rows('corpus.tsv'))))
        return
    if a.mode=='families':
        data=[]
        for r in rows('families.tsv'):
            if not re.fullmatch(r'd\d+[a-z]?',r['Group_ID']):continue
            if a.telugu and not int(r['N_Telugu_Records']):continue
            keys={'reconstructed':['Reconstructed_Input_Flags'],'comparative':['Comparative_Input_Flags'],
                  'either':['Reconstructed_Input_Flags','Comparative_Input_Flags']}[a.basis]
            if a.flag and not any(a.flag in r[k].split(';') for k in keys):continue
            data.append(r)
        data.sort(key=lambda r:int(re.search(r'\d+',r['Group_ID'])[0]))
        print('MATCHES',len(data),'RANGE',a.offset,a.offset+a.limit)
        for n,r in enumerate(data[a.offset:a.offset+a.limit],a.offset):
            print(n,r['Group_ID'],r['Reconstructions'] or '['+r['Display_Form']+']',
                  '|',r['Display_Gloss'][:100],'| TE',r['Telugu_Forms'],'|',r['Languages'])
        return
    if a.mode=='search':
        pat=re.compile(a.pattern,re.I)
        matches=0
        for r in rows('corpus.tsv'):
            if a.lang and r['Language_ID'] not in a.lang.split(','):continue
            if not pat.search(r[a.field]):continue
            matches+=1
            if matches<=a.limit:
                print(r['Research_Group'],r['ID'],r['Language_ID'],r['Form'],repr(r['Gloss']),
                      '['+r['Source']+']',r['Tags'],'PATH-LOAN',r['Borrowed_In_Path'])
        print('TOTAL',matches)
        return
    wanted=set(a.ids)
    notes=defaultdict(list)
    for r in rows('entry-texts.tsv'):
        if r['Form_ID'] in wanted:notes[r['Form_ID']].append(r)
    with (HERE/'groups.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            g=json.loads(line)
            if g['id'] not in wanted:continue
            print('\n###',g['id'],g['head']['Form'],g['head']['Gloss'],'HEAD',g['audit'].get('Strategy',''))
            print('ETYMOLOGY',g['head']['Etymology'])
            for r in notes[g['id']]:
                print('SOURCE NOTE',r['Content'],'SOURCE',r['Source'])
            langs=defaultdict(list)
            for r in g['records']:
                if a.lang and r['Language_ID'] not in a.lang.split(','):continue
                langs[r['Language_ID']].append(r)
            order=['PDr','PSTDr','PSD1','PSD2','PCDr','Tamil','Malayalam','Kota','Toda','Kannada','Kodagu','Tulu',
                   'Telugu','OTelugu','Gondi','Konda','Kui','Kuwi','Pengo','Manda','Kolami','Naikri','Naiki','Parji',
                   'Ollari','Gadaba','Kurux','Malto','Brahui']
            for lang in sorted(langs,key=lambda l:(order.index(l) if l in order else 100,l)):
                unique={}
                for r in langs[lang]:
                    key=(r['Form'],r['Gloss'],r['Tags'],r['Description'])
                    unique.setdefault(key,[]).append(r)
                print(lang+':')
                for k,rs in list(unique.items())[:a.max]:
                    word,gloss,tags,desc=k
                    details=''
                    if a.form_ids:details=' IDs='+','.join(r['ID'] for r in rs)+' SRC='+';'.join(dict.fromkeys(r['Source'] for r in rs))
                    print(' ',word,'‘'+gloss+'’',tags,desc,details)
                if len(unique)>a.max:print(' ...',len(unique)-a.max,'additional unique records')

if __name__=='__main__':main()
