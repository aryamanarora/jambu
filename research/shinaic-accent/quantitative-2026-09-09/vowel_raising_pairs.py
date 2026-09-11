"""Retrieve quantity-controlled Biori/Ashret long-vowel correspondences.

The consonantal frame, gloss and vowel-nucleus count select pairs before
either dialect's accent or the Ashret vowel quality is inspected.
"""
from collections import defaultdict
import re,json,unicodedata as ud
from analysis_data import load_analysis_tokens,write_tsv
from phonology import clusters,VOWELS

def frame(word):
    cs=clusters(word);out=[];previous=False
    for c in cs:
        if c[0] in VOWELS:
            if not previous:out.append('V')
            previous=True
        else:
            if c[0] not in "ː:'ʹˈˊ":out.append(c)
            previous=False
    return ud.normalize('NFC',''.join(out))

def main():
    rr=[r for r in load_analysis_tokens() if r['language_id']=='Phal' and r['source_keys']=='liljegren'
        and r['modern_single_word'] and not r['modern_vowel_sequence'] and not re.search('[-=;,]',r['reading_form'])]
    groups=defaultdict(list)
    for r in rr:groups[r['research_gloss']].append(r)
    out={}
    for g,rs in groups.items():
        b=[r for r in rs if 'Biori' in r['description'] or ':biori:' in r['dialect_tags']]
        a=[r for r in rs if r not in b]
        for br in b:
            if not br['modern_accent_position']:continue
            bi=br['modern_accent_position']-1
            if br['modern_quantity_pattern'][bi]!='L' or br['modern_vowel_bases'][bi] not in 'ae':continue
            for ar in a:
                if frame(br['reading_form'])!=frame(ar['reading_form']) or br['modern_nuclei']!=ar['modern_nuclei']:continue
                key=(br['reading_form'],ar['reading_form'],g)
                if key in out:continue
                out[key]=dict(biori=br['reading_form'],ashret=ar['reading_form'],gloss=g,
                  biori_family=br['research_family_id'],ashret_family=ar['research_family_id'],
                  biori_quality=br['modern_vowel_bases'],ashret_quality=ar['modern_vowel_bases'],
                  biori_quantity=br['modern_quantity_pattern'],ashret_quantity=ar['modern_quantity_pattern'],
                  biori_accent=br['modern_outcome'],biori_accent_position=br['modern_accent_position'],
                  ashret_accent=ar['modern_outcome'],ashret_accent_position=ar['modern_accent_position'],
                  record_ids=[br['id'],ar['id']],biori_description=br['description'],ashret_description=ar['description'],
                  tested_nucleus=bi+1,biori_test_vowel=br['modern_vowel_bases'][bi],
                  ashret_test_vowel=ar['modern_vowel_bases'][bi],
                  tested_syllable_domain='word-final-closed' if bi==br['modern_nuclei']-1 and not br['modern_final_vowel'] else 'other',
                  expected_raised_quality='o' if br['modern_vowel_bases'][bi]=='a' else 'i')
    write_tsv('vowel-raising-candidates.tsv',out.values())
    for i,x in enumerate(out.values()):print(i,x['biori'],'>',x['ashret'],x['gloss'],x['biori_accent'],x['biori_accent_position'],'>',x['ashret_accent'],x['ashret_accent_position'],x['biori_family'],x['ashret_family'])
    print('pairs',len(out))
if __name__=='__main__':main()
