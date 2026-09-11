"""Independent i-declension test: final long aa in citation, ee in oblique.

Accent is excluded from selection. Full printed inflected forms are required;
suffix-only shorthand is not expanded using the citation accent.
"""
import re,json,unicodedata as ud
from collections import Counter
from analysis_data import load_analysis_tokens,HERE,write_tsv
from phonology import modern_features

def main():
    out={}
    for r in load_analysis_tokens():
        if r['language_id']!='Phal' or r['source_keys']!='liljegren' or not r['modern_single_word'] or r['modern_vowel_sequence']:continue
        if not r['modern_quantity_pattern'].endswith('L') or r['modern_final_vowel'] or not r['modern_vowel_bases'].endswith('a'):continue
        m=re.search(r'Inflection: i-decl \(([^)]+)\): ([^;]+)',r['description'])
        if not m:continue
        inf=ud.normalize('NFC',m[2].strip())
        if re.search(r'[- ,/()\u0325]',inf):continue
        f=modern_features({**r,'original':inf})
        if f['modern_nuclei']!=r['modern_nuclei']+1 or not f['modern_quantity_pattern'].endswith('LS') or not f['modern_vowel_bases'].endswith('ei'):continue
        key=(r['reading_form'],r['research_gloss'],inf)
        if key in out:continue
        out[key]=dict(record_id=r['id'],family_id=r['research_family_id'],citation=r['reading_form'],gloss=r['research_gloss'],
          inflected=inf,inflection_cells=m[1],dialect=r['dialect_tags'],citation_outcome=r['modern_outcome'],
          citation_accent_from_right=r['modern_accent_from_right'],inflected_outcome=f['modern_outcome'],inflected_accent_from_right=f['modern_accent_from_right'],
          prediction='citation-final-root-L; inflected-final-short-i-accent',
          status='consistent' if r['modern_outcome']=='L' and r['modern_accent_from_right']==1 and f['modern_accent_from_right']==1 else 'residual',
          description=r['description'])
    # All74 retrieved pairs were read. The one nonmatching lexical pair is
    # niildhráal/izreeṇí: a Biori synonym inherited another headword's printed
    # inflection metadata. It is not evidence for that synonym's own plural.
    for r in out.values():
        r['adjudication']='comparable-lexical-stem'
        r['analysis']='The same lexical stem has citation aa and inflected ee before i; the accents were not used to retrieve this pair. This supports a productive i-declension accent class, not an old-accent inheritance claim.'
        if r['record_id']=='f_idnbwdlalthls':
            r['adjudication']='unmatched-synonym-and-inflection';r['status']='excluded-unmatched-paradigm'
            r['analysis']='Biori niildhráal rainbow and izreeṇí are segmentally different stems. The dictionary attaches the izraáṇ inflection to its lexical variant; the actual inflection of niildhráal is not supplied. Its early accent remains a fact, but this row cannot test the aa/ee paradigm rule. A blue nīl- compound is only a lead until the remaining component is independently identified.'
    write_tsv('palula-umlaut-i-nouns.tsv',out.values())
    valid=[r for r in out.values() if r['adjudication']=='comparable-lexical-stem']
    lexemes={}
    for r in valid:lexemes.setdefault((r['gloss'],r['inflected']),[]).append(r)
    annotations=[dict(record_ids=[r['record_id'] for r in rs],analysis=' / '.join(r['citation'] for r in rs)+' → '+rs[0]['inflected']+' ('+rs[0]['gloss']+'). '+rs[0]['analysis'],source='Liljegren2019 dictionary; independently described in Liljegren2016Tables5.18–19pp117–118') for rs in lexemes.values()]
    for r in out.values():
        if r['adjudication']!='comparable-lexical-stem':annotations.append(dict(record_ids=[r['record_id']],analysis=r['analysis'],source='Liljegren2019 dictionary variant metadata'))
    (HERE/'lexical_annotations_03.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in annotations))
    summary=dict(form_gloss_cells=len(out),comparable_form_cells=len(valid),comparable_lexemes=len(lexemes),status_counts=dict(Counter(r['status'] for r in out.values())),
       domain='Source i-decl nouns with a full printed inflection: consonant-final citation whose last vowel is long aa, paired with one-more-nucleus inflection ending long ee plus short i. Selection ignores all accents. No suffix-only expansions. Same-source modern morphological prediction, not proof of a unique OIA ancestor.')
    (HERE/'palula-umlaut-i-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    for i,r in enumerate(out.values()):print(i,r['citation'],r['inflected'],r['gloss'],r['status'],r['family_id'])
    print(summary)
if __name__=='__main__':main()
