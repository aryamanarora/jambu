"""Exploratory input-defined screens with explicit caveats and full outcomes."""
import re,json,unicodedata as ud
from collections import defaultdict,Counter
from analysis_data import load_analysis_tokens,load_annotations,load_ancestors,tsv,write_tsv
from quantify import input_for,lect,outcome
from phonology import old_features

PROPERTY_FAMILIES={'722','1962','2613','3153','3451','3523','3533','3602','3832','3895','3941','4424','4850','4889','5145','5679','5839','5938','6119','6368','6926','6983','7563','7621','7638','8047','8156','8283','8330','9268','9568','10299','10896','11168','11225','12196','12487','12548','12717','12774','13519','13548','13924','13990'}
PROPERTY_WORDS={'little','few','heavy','bad','dirty','black','soft','tender','crooked','strong','mighty','left','short','lame','dwarf','big','sour','small','old','hot','warm','sharp','bitter','right','long','tall','naked','new','blue','green','ripe','woolen','white','beautiful','pretty','smooth','whole','all','deaf','good','sweet','light','fast','red','open','cold','dry','blind','golden','straight','yellow'}

def main():
    rows=load_analysis_tokens();anns=load_annotations();fams={x['family_id']:x for x in tsv('families.tsv')};anc=load_ancestors()
    clusters=[];props=[]
    for r in rows:
        fid=r['research_family_id']
        if not fid:continue
        word,kind,aid=input_for(r,anc,fams);p=old_features(word)
        cluster=re.sub(r'([kgcjṭḍtdpb])h',r'\1',p['old_intervocalic_cluster'])
        if p['old_nuclei']==2 and p['old_first_quantity']=='short' and len(cluster)>=2 and r['language_id']=='Sh' and r['notation'] in ['gilgit-mora','shina-mora'] and r['modern_outcome'] in ['E','L'] and r['modern_accent_position']==1 and not r['strict_exclusion']:
            clusters.append(dict(family_id=fid,input=word,input_basis=kind,input_vowel=p['old_first_vowel'],cluster=p['old_intervocalic_cluster'],form=r['reading_form'],source=r['source_keys'],dialect=lect(r),observed=r['modern_outcome'],record_id=r['id'],analysis=anns[fid]['analysis'],unresolved=anns[fid].get('unresolved',''),scope='Modern first-nucleus long E/L forms with a two-nucleus short-root cluster input. Consonant-count and first-vowel alignment are retrieval approximations; input variants and derivations still require the dossier.'))
        if fid not in PROPERTY_FAMILIES:continue
        words=set(re.findall('[a-z]+',r['research_gloss'].lower()))
        if not words&PROPERTY_WORDS:continue
        # Avoid known homonymous nominal material within property families.
        if words&{'blood','mud','wool','fever','gold','egg'} and not words&{'woolen','golden'}:continue
        if not r['modern_final_vowel'] or not r['modern_quantity_pattern'].endswith('S') or r['modern_nuclei']<2:continue
        reason=[]
        if r['strict_exclusion']:reason.append(r['strict_exclusion'])
        if not r['modern_single_word']:reason.append('multiple-words-or-alternatives')
        if r['modern_vowel_sequence']:reason.append('vowel-sequence-unresolved')
        if r['notation']=='accent-not-investigated':reason.append('source-did-not-investigate-accent')
        pos=r['stress_from_right'] if r['notation'] in ['brokskat-stress','dras-stress-vowel-sequence','survey-phonetic'] else r['modern_accent_from_right']
        if pos=='':reason.append('no-single-location-mark')
        props.append(dict(family_id=fid,input_family=fams[fid]['headword'],language=r['language_id'],dialect=lect(r),source=r['source_keys'],form=r['reading_form'],gloss=r['research_gloss'],notation=r['notation'],position_from_right=pos,outcome=outcome(r),status='unscorable' if reason else 'penultimate' if pos==2 else 'other-position',exclusion=';'.join(reason),record_id=r['id'],analysis=anns[fid]['analysis']))
    write_tsv('short-root-cluster-screen.tsv',clusters)
    summaries=[]
    for vowel in sorted({r['input_vowel'] for r in clusters}):
        for dialect in sorted({r['dialect'] for r in clusters}):
            rr=[r for r in clusters if r['input_vowel']==vowel and r['dialect']==dialect];groups=defaultdict(set)
            for r in rr:groups[r['family_id']].add(r['observed'])
            summaries.append(dict(old_first_vowel=vowel,dialect=dialect,families=len(groups),outcome_sets=dict(Counter('/'.join(sorted(v)) for v in groups.values()))))
    write_tsv('short-root-cluster-summary.tsv',summaries)
    write_tsv('property-location-screen.tsv',props)
    psummary=[]
    for lang in ['Sh','Phal','Sv','Kalk','Kund','bro','Ush']:
        rr=[r for r in props if r['language']==lang];groups=defaultdict(list)
        for r in rr:groups[r['family_id']].append(r)
        counts=Counter();outs=defaultdict(set)
        for fid,rs in groups.items():
            valid=[r for r in rs if r['status']!='unscorable'];pp={r['position_from_right'] for r in valid}
            status='unscorable' if not pp else 'only-penultimate' if pp=={2} else 'mixed-with-penultimate' if 2 in pp else 'only-other-position'
            counts[status]+=1
            for p in pp:outs[p].add(fid)
        psummary.append(dict(language=lang,families=len(groups),family_statuses=dict(counts),position_family_counts={k:len(v) for k,v in outs.items()},scope='Predeclared core property families and property senses with a retained final short vowel; all sources shown separately in detailed rows. Savi historical accent marks indicate location, not mora contrast. This is a comparative location screen, not a fitted sound law.'))
    write_tsv('property-location-summary.tsv',psummary)
    print('cluster tokens',len(clusters),'property tokens',len(props));print(json.dumps(psummary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
