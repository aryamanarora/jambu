"""Independent Gilgit adjective test and complete cognate-family panel.

The Gilgit domain uses the source's adjective tag and final short o, not the
observed accent. Palula membership uses its supplied inflectional class.
Other-language cells are descriptive cognate sets, not assumed equivalents
of the same grammatical citation formation.
"""
import re,json,unicodedata as ud
from collections import Counter,defaultdict
from analysis_data import load_analysis_tokens,load_annotations,write_tsv,HERE
from quantify import lect,outcome

def main():
    rows=load_analysis_tokens();out=[];pal=[];families=set()
    for r in rows:
        if r['language_id']=='Phal' and r['source_keys']=='liljegren' and re.search(r'Inflection: (Reg|Uml) \(Fem\):',r['description']) and r['modern_final_segment']=='u' and r['modern_nuclei']>=2:
            if r['research_family_id']:families.add(r['research_family_id'])
        if r['language_id']=='Phal' and r['source_keys']=='liljegren' and re.search(r'\badj\b',r['tags']) and r['modern_final_segment']=='u' and r['modern_quantity_pattern'].endswith('S') and r['modern_nuclei']>=2:
            reasons=[]
            if not r['modern_single_word']:reasons.append('multiword-or-alternatives')
            if r['modern_vowel_sequence']:reasons.append('vowel-sequence-unresolved')
            if r['modern_accent_count']!=1:reasons.append('not-one-acute')
            status='unscorable' if reasons else 'consistent' if r['modern_accent_from_right']==2 else 'exception'
            pal.append(dict(record_id=r['id'],family_id=r['research_family_id'],form=r['reading_form'],gloss=r['research_gloss'],source=r['source_keys'],input='source-tagged-adjective-with-final-short-u-including-ú',prediction='penultimate-nucleus',observed_from_right=r['modern_accent_from_right'],observed_mora=r['modern_outcome'],status=status,exclusion=';'.join(reasons),description=r['description']))
        if r['language_id']!='Sh' or r['source_keys'] not in ['degener-shina2008','buddruss-shina1996']:continue
        if not re.search(r'\badj\b',r['tags']):continue
        if r['modern_final_segment']!='o' or r['modern_nuclei']<2 or not r['modern_quantity_pattern'].endswith('S'):continue
        reasons=[]
        if not r['modern_single_word']:reasons.append('multiword-or-alternatives')
        if r['modern_vowel_sequence']:reasons.append('vowel-sequence-unresolved')
        if r['modern_accent_count']!=1:reasons.append('not-one-acute')
        if re.search('[-=]',r['reading_form']):reasons.append('explicit-compound-boundary')
        status='unscorable' if reasons else 'consistent' if r['modern_accent_from_right']==2 else 'exception'
        out.append(dict(record_id=r['id'],family_id=r['research_family_id'],form=r['reading_form'],gloss=r['research_gloss'],source=r['source_keys'],input='source-tagged-adjective-with-final-short-o',prediction='penultimate-nucleus',observed_from_right=r['modern_accent_from_right'],observed_mora=r['modern_outcome'],status=status,exclusion=';'.join(reasons)))
        if r['research_family_id']:families.add(r['research_family_id'])
    write_tsv('gilgit-o-adjectives.tsv',out)
    write_tsv('palula-tagged-u-adjectives.tsv',pal)
    pg={}
    for r in pal:pg.setdefault((r['form'],r['gloss']),r)
    psum={'raw_records':len(pal),'unique_form_gloss_types':len(pg),'counts':dict(Counter(r['status'] for r in pg.values())),
      'domain':'Explicit source adjective tag, final short u including accented ú; no inflection-class filter. This corrects an earlier accent-sensitive literal-suffix selection.'}
    (HERE/'palula-tagged-u-summary.json').write_text(json.dumps(psum,ensure_ascii=False,indent=2)+'\n')
    groups=defaultdict(list)
    for x in out:groups[(x['form'],x['gloss'])].append(x)
    summary={'raw_records':len(out),'unique_form_gloss_types':len(groups),'counts':dict(Counter(xs[0]['status'] for xs in groups.values())),
       'source_counts':{s:dict(Counter(x['status'] for x in out if x['source']==s)) for s in sorted({x['source'] for x in out})},
       'domain':'Source adjective tag, at least two nuclei, final short o. Unequal sequences, compound boundaries and absent/multiple marks not scored. Independent source transcriptions are preserved; form/gloss types are not independent historical etyma.'}
    (HERE/'gilgit-o-adjectives-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    anns=load_annotations();panel=[]
    for fid in sorted(families,key=lambda s:float(s) if re.fullmatch(r'\d+(\.\d+)?',s) else 99999):
        for lang in ['Sh','Phal','Sv','Kalk','Kund','bro','Ush']:
            rr=[r for r in rows if r['research_family_id']==fid and r['language_id']==lang]
            panel.append(dict(family_id=fid,language=lang,forms=[{'form':r['reading_form'],'outcome':outcome(r),'source':r['source_keys'],'dialect':lect(r),'gloss':r['research_gloss'],'record_id':r['id'],'excluded':r['strict_exclusion']} for r in rr],analysis=anns[fid]['analysis'],unresolved=anns[fid].get('unresolved',''),scope='Full family context; includes other parts of speech and derivations. Only grammatically matched forms can test the adjective rule.'))
    write_tsv('adjective-cognate-panel.tsv',panel)
    print(json.dumps(summary,ensure_ascii=False,indent=2),'panel families',len(families))
    print('PALULA',json.dumps(psum,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
