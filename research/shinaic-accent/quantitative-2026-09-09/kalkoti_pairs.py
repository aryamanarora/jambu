"""Candidate comparative apocope test, paired without consulting either tone.

Pairing uses reviewed family identity plus overlapping lexical meanings.
Formation mismatches remain for explicit manual adjudication. The Palula
final vowel is a comparative structural predictor, not a reconstruction by fiat.
"""
import re,json,unicodedata as ud
from collections import defaultdict
from analysis_data import load_analysis_tokens,write_tsv

def senses(g):
    return {re.sub(r'^to ','',s.strip().lower()) for s in re.split(r'[;,]',g)}
def main():
    rows=load_analysis_tokens();pp=defaultdict(list)
    for r in rows:
        if r['language_id']=='Phal' and r['source_keys']=='liljegren' and r['research_family_id'] and r['modern_single_word'] and not r['strict_exclusion'] and ':biori:' not in r['dialect_tags']:
            pp[r['research_family_id']].append(r)
    pairs=[]
    for k in rows:
        if k['language_id']!='Kalk' or k['source_keys'] not in ['kalkoti','hultman2023kalkoti'] or not k['research_family_id'] or not k['modern_single_word'] or k['strict_exclusion']:continue
        if k['modern_nuclei']!=1:continue
        ps=[p for p in pp.get(k['research_family_id'],[]) if senses(p['research_gloss'])&senses(k['research_gloss'])]
        for p in ps:
            final='short-final-vowel' if p['modern_final_vowel'] and p['modern_quantity_pattern'].endswith('S') else 'long-final-vowel' if p['modern_final_vowel'] else 'consonant-final'
            pairs.append(dict(family_id=k['research_family_id'],gloss=k['research_gloss'],palula=p['reading_form'],palula_gloss=p['research_gloss'],palula_nuclei=p['modern_nuclei'],palula_final=final,palula_outcome=p['modern_outcome'],palula_accent_from_right=p['modern_accent_from_right'],kalkoti=k['reading_form'],kalkoti_source=k['source_keys'],kalkoti_outcome=k['modern_outcome'],kalkoti_low_status=k.get('low_status',''),kalkoti_record_id=k['id'],palula_record_id=p['id']))
    write_tsv('kalkoti-palula-candidates.tsv',pairs)
    groups=defaultdict(list)
    for p in pairs:groups[(p['family_id'],p['gloss'])].append(p)
    print('pairs',len(pairs),'lexical groups',len(groups))
    for i,((fid,g),ps) in enumerate(groups.items()):
        print(i,fid,g,'PAL',list(dict.fromkeys(p['palula']+' '+p['palula_final']+' '+p['palula_outcome'] for p in ps)),'KALK',list(dict.fromkeys(p['kalkoti']+' '+p['kalkoti_outcome']+' '+p['kalkoti_source'] for p in ps)))
if __name__=='__main__':main()
