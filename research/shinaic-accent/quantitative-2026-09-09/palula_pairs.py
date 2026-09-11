"""Quantity/aspiration input test on independently matched Biori/Ashret lexemes."""
import re,json,unicodedata as ud
from collections import defaultdict,Counter
from analysis_data import load_analysis_tokens,load_annotations,HERE,write_tsv
from phonology import segment_key,modern_features
def plain(s):return ''.join(c for c in ud.normalize('NFD',s) if c not in '\u0301\u0300\u0304').strip()
def infl(r):
    d=ud.normalize('NFC',r['description'])
    m=re.search(r'Inflection: ([^;]+)',d)
    if not m:return 'not-recorded',''
    s=m[1];mm=re.search(r'\):\s*([^,;(]+)',s)
    if not mm:return 'not-parsed',s
    f=mm[1].strip()
    if 'á' in f or 'í' in f:
        return ('suffix-accented' if f.startswith('-') or f.endswith(('á','í')) else 'root-accented'),s
    return ('root-retaining' if f.startswith('-') else 'unmarked-or-irregular'),s
def main():
    rr=[r for r in load_analysis_tokens() if r['language_id']=='Phal' and r['source_keys']=='liljegren']
    groups=defaultdict(list);anns=load_annotations()
    for r in rr:groups[(r['research_family_id'],r['research_gloss'])].append(r)
    out={}
    for (fid,g),rs in groups.items():
        b=[r for r in rs if 'Biori' in r['description'] or ':biori:' in r['dialect_tags']]
        a=[r for r in rs if r not in b]
        for br in b:
            if br['modern_quantity_pattern']!='S' or br['modern_vowel_bases']!='a' or not br['modern_single_word'] or re.search('[-=;,]',br['reading_form']):continue
            # Same consonantal skeleton, differing only in quantity/accents.
            aa=[r for r in a if segment_key(r['reading_form'])==segment_key(br['reading_form']) and r['modern_quantity_pattern']=='L' and r['modern_single_word']]
            if not aa:continue
            has_h='h' in plain(br['reading_form']);pred='L' if has_h else 'E'
            key=(plain(br['reading_form']),g)
            if key not in out:out[key]=dict(biori=br['reading_form'],gloss=g,family_ids=[],input_class='short-a-with-h' if has_h else 'short-a-without-h',expected=pred,ashret_forms=[],observed=[],record_ids=[],inflections=[],explanations=[])
            x=out[key]
            if fid and fid not in x['family_ids']:x['family_ids'].append(fid);x['explanations'].append(anns[fid]['analysis'])
            for ar in aa:
                x['ashret_forms'].append(ar['reading_form']);x['observed'].append(ar['modern_outcome']);x['record_ids'] += [br['id'],ar['id']]
                x['inflections'].append(infl(ar))
    for x in out.values():
        for k in ['ashret_forms','observed','record_ids']:x[k]=sorted(set(x[k]))
        x['inflections']=sorted(set(x['inflections']))
        x['status']='consistent' if set(x['observed'])=={x['expected']} else 'opposite' if x['expected'] not in x['observed'] else 'conflicting'
    write_tsv('palula-short-a-pairs.tsv',out.values())
    summary=[]
    for cl in ['short-a-without-h','short-a-with-h']:
        xs=[x for x in out.values() if x['input_class']==cl];c=Counter(x['status'] for x in xs)
        summary.append(dict(input_class=cl,lexemes=len(xs),**c,outcomes=dict(Counter('/'.join(x['observed']) for x in xs))))
    write_tsv('palula-short-a-summary.tsv',summary)
    # Input-domain and unit sensitivity, specified without selecting outcomes.
    # The open numeral a is not a closed syllable. Numeral ak and article ak
    # are one historically related form, despite two dictionary gloss groups.
    sensitivity=[]
    domains={'all-form-gloss-pairs':list(out.values()),
             'closed-form-gloss-pairs':[x for x in out.values() if plain(x['biori'])!='a']}
    dedup={}
    for x in domains['closed-form-gloss-pairs']:
        key=plain(x['biori']) if plain(x['biori'])=='ak' else (plain(x['biori']),x['gloss'])
        if key not in dedup:dedup[key]={**x,'observed':set(x['observed'])}
        else:dedup[key]['observed'].update(x['observed'])
    domains['closed-lexemes-article-numeral-one-collapsed']=list(dedup.values())
    for domain,xx in domains.items():
        for cl in ['short-a-without-h','short-a-with-h']:
            xs=[x for x in xx if x['input_class']==cl];pred='L' if cl.endswith('with-h') else 'E'
            counts=Counter('consistent' if set(x['observed'])=={pred} else 'conflicting' if pred in x['observed'] else 'opposite' for x in xs)
            sensitivity.append(dict(domain=domain,input_class=cl,units=len(xs),expected=pred,**counts,
              outcome_sets=dict(Counter('/'.join(sorted(x['observed'])) for x in xs))))
    write_tsv('palula-short-a-sensitivity.tsv',sensitivity)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
