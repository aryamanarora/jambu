#!/usr/bin/env python3
"""Compact manual reading aid; never labels an outcome. Full records remain in corpus."""
import sys,json,csv
from collections import defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent
wanted=set(sys.argv[1:]);langs={'Tamil','Malayalam','Kannada','Kota','Toda','Kodagu','Tulu','Telugu','OTelugu','Gondi','Konda','Kui','Kuwi','Pengo','Manda','Kolami','Naikri','Naiki','Parji','Gadaba','Kurux','Malto','Brahui','Badaga','Irula','Koraga','markodi'}
notes=defaultdict(list)
with (P/'entry-texts.tsv').open() as f:
 for r in csv.DictReader(f,delimiter='\t'):
  if r['Form_ID'] in wanted:notes[r['Form_ID']].append(r['Content'])
with (P/'groups.jsonl').open() as f:
 for line in f:
  g=json.loads(line)
  if g['id'] not in wanted:continue
  print('\n###',g['id'],g['head']['Form'],g['head']['Gloss']);print('NOTES', ' / '.join(notes[g['id']]))
  by=defaultdict(list)
  for r in g['records']:
   if r['Language_ID'] in langs:by[r['Language_ID']].append(r)
  for lang,rr in by.items():
   forms={}
   for r in rr:forms.setdefault(r['Form'],r)
   limit=50 if lang in {'Telugu','OTelugu'} else 25
   bits=[]
   for form,r in list(forms.items())[:limit]:
    gloss=' '.join(r['Gloss'].split())
    if len(gloss)>95:gloss=gloss[:95]+'…'
    bits.append(form+' ['+gloss+']'+(' {loan}' if r['Borrowed_In_Path']=='1' else ''))
   print(lang+': '+' | '.join(bits))
   if len(forms)>limit:print('TRUNCATED',lang,len(forms)-limit,'additional forms; consult full panel')
