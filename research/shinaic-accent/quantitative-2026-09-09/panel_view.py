from analysis_data import *
from quantify import lect
import sys
rows=load_analysis_tokens();fs={r['family_id']:r for r in tsv('families.tsv')}
for fid in sys.argv[1].split(','):
    print('\nFAMILY',fid,fs.get(fid,{}).get('headword',''),fs.get(fid,{}).get('gloss',''))
    for lang in ['Sh','Phal','Sv','Kalk','Kund','bro','Ush']:
        rs=[r for r in rows if r['research_family_id']==fid and r['language_id']==lang]
        primary=[r for r in rs if r['notation'] not in ['historical-dictionary','historical-list','accent-not-investigated','survey-phonetic']]
        rs=primary or rs
        print(lang,' | '.join(dict.fromkeys(r['reading_form']+' ['+lect(r)+';'+r['source_keys']+'] '+r['research_gloss'][:35] for r in rs)))
