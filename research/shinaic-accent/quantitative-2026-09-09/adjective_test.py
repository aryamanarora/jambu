"""Independent grammatical domain: Palula u~i gender inflection.

Includes some participial forms. Ending selection uses the accent-stripped
final segment: selecting literal u would wrongly omit final-accented ú.
"""
import re,json,unicodedata as ud
from collections import defaultdict,Counter
from analysis_data import load_analysis_tokens,load_annotations,HERE,write_tsv
def main():
    rows=load_analysis_tokens();anns=load_annotations();out=[]
    for r in rows:
        if r['language_id']!='Phal' or r['source_keys']!='liljegren':continue
        category=re.search(r'Inflection: (Reg|Uml) \(Fem\):',r['description'])
        if not category:continue
        if r['modern_final_segment']!='u' or r['modern_nuclei']<2 or not r['modern_quantity_pattern'].endswith('S'):continue
        reason=[]
        if not r['modern_single_word']:reason.append('multiple-words')
        if r['modern_vowel_sequence']:reason.append('vowel-sequence-unresolved')
        if r['modern_accent_count']!=1:reason.append('not-one-acute')
        # An independently supplied feminine-i form is a real grammatical
        # control. It is not selected by the accent of either citation.
        fem=re.search(r'Inflection: (?:Reg|Uml) \(Fem\):\s*([^;,]+)',ud.normalize('NFC',r['description']))[1]
        status='unscorable' if reason else 'consistent' if r['modern_accent_from_right']==2 else 'exception'
        fid=r['research_family_id']
        out.append(dict(record_id=r['id'],family_id=fid,masculine=r['reading_form'],feminine=fem,gloss=r['research_gloss'],source_tags=r['tags'],
          input=category[1]+'-u-masculine-with-feminine-i',prediction='penultimate-nucleus',observed_from_right=r['modern_accent_from_right'],
          observed_mora=r['modern_outcome'],status=status,exclusion=';'.join(reason),description=r['description'],
          family_analysis=anns[fid]['analysis'] if fid else r.get('etymological_assessment','No established ancestral link; grammatical test remains possible.')))
    # Duplicate graph placements never become independent confirmations.
    dedup={}
    for x in out:
        k=(x['masculine'],x['feminine'],x['gloss']);dedup.setdefault(k,x)
    write_tsv('palula-u-adjectives.tsv',out)
    c=Counter(x['status'] for x in dedup.values());summary={'raw_records':len(out),'unique_citation_types':len(dedup),**c,
     'by_inflection_class':{cl:dict(Counter(x['status'] for x in dedup.values() if x['input']==cl)) for cl in sorted({x['input'] for x in dedup.values()})},
     'domain':'Regular or umlaut gender-inflecting citation ending in short u, including accented ú, with recorded feminine-i inflection class; includes participial forms. Unequal vowel sequences and multiple words not scored. Variant entries can inherit the main lemma feminine metadata, so not every cited feminine is a verified dialect-specific counterpart. No filter on observed accent.',
     'audit_correction':'An earlier literal-final-u selection omitted eight final-accented ú citations. This version selects the accent-stripped final segment and supersedes the earlier exceptionless count.'}
    (HERE/'palula-u-adjectives-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(summary)
    for x in dedup.values():
        if x['status']=='exception':print(x['record_id'],x['masculine'],x['gloss'],x['family_id'],x['feminine'])
if __name__=='__main__':main()
