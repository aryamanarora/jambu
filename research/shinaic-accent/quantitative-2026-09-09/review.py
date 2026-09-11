"""Print bounded review packets from the frozen research corpus."""
from collections import defaultdict
import csv
from pathlib import Path
import re
import sys
import unicodedata as ud
from phonology import old_features, modern_features

HERE=Path(__file__).resolve().parent
FAMILIES=list(csv.DictReader((HERE/'families.tsv').open(),delimiter='\t'))
ROWS=list(csv.DictReader((HERE/'corpus.tsv').open(),delimiter='\t'))
GROUPS=defaultdict(list)
for r in ROWS:GROUPS[r['family_id']].append(r)
STRONG={'palula-mora','gilgit-mora','shina-mora','strand-phonatory-accent'}


def eligible(f,section):
    old=old_features(f['headword'])['old_accent_count']==1
    strong=any(modern_features(r)['notation'] in STRONG for r in GROUPS[f['family_id']])
    return section=='all' or section=='core' and old and strong or section=='unaccented' and not old and strong or section=='legacy' and not strong


def short(r):
    ss=r['source_keys'].split(';')
    source=next((s for s in ['liljegren','degener-shina2008','buddruss-shina1996','schmidt','strand','kund','kalkoti','CDIAL'] if s in ss),ss[0])
    lect=re.search(r'dialect:[^:]+:([^:]+):',r['tags'])
    lect=lect[1] if lect else r['language_id']
    return f"{lect}:{ud.normalize('NFC',r['original'])} ‘{r['gloss']}’ ({source})"


def packet(section,start,count):
    fs=[f for f in FAMILIES if eligible(f,section)]
    print(f'{section}: {len(fs)} families; packet {start}–{min(start+count,len(fs))}')
    for n,f in enumerate(fs[start:start+count],start):
        print(f"\n{n}\t{f['family_id']}\t{f['headword']}\t{f['gloss']}\t{f['tags']}")
        print('  Inputs:',f['ancestral_forms'])
        rows=GROUPS[f['family_id']]
        for lang in ['Phal','Sh','Kalk','Kund','Sv','bro','Ush']:
            subset=[r for r in rows if r['language_id']==lang and 'backstrom1992' not in r['source_keys']]
            if not subset:
                subset=[r for r in rows if r['language_id']==lang]
            # Show primary modern sources first, then historically older sources.
            subset.sort(key=lambda r:(modern_features(r)['notation'] not in STRONG,'CDIAL' in r['source_keys']))
            values=list(dict.fromkeys(short(r) for r in subset))
            if values:print('  '+' | '.join(values[:8])+(' | … '+str(len(values))+' total' if len(values)>8 else ''))
        etym=re.sub('<[^>]+>','',f['etymology'])
        print('  OIA:',etym[:450])


def family(fid):
    for f in FAMILIES:
        if f['family_id']==fid:
            print(f['headword'],f['gloss'],f['tags']);print(f['etymology'])
    for r in GROUPS[fid]:
        print('\n',r['id'],short(r),'INPUT',r['ancestor_id'],r['ancestor_form'])
        print(' tags:',r['tags'],'; notation:',modern_features(r))
        print(' notes:',r['description'],'; etymology:',r['etymology'])


if __name__=='__main__':
    if sys.argv[1]=='family':family(sys.argv[2])
    else:packet(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
