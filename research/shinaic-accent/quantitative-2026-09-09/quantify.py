"""Descriptive family-level tables; no fitted rule is called deterministic.

Historical input features come from the nearest named formation. All source
and dialect outcomes are retained as sets. Modern monosyllabicity is an
explicit observation-domain restriction, not a reconstructed input feature.
"""
from collections import defaultdict,Counter
import json,re,unicodedata as ud
from analysis_data import load_analysis_tokens,load_annotations,load_ancestors,tsv,HERE,write_tsv
from phonology import old_features
LANGS=['Sh','Phal','Sv','Kalk','Kund','bro','Ush']
MORA={'gilgit-mora','shina-mora','palula-mora','strand-phonatory-accent'}
def lect(r):
    tags=r['dialect_tags'].split(';')
    values=[t.split(':')[2] for t in tags if t.startswith('dialect:') and len(t.split(':'))>2]
    return '|'.join(values) or r['language_id']
def input_for(r,anc,fams):
    aid=r['research_ancestor_id']
    if aid in anc:
        a=anc[aid];return a.get('Original') or a['Form'],'nearest-formation',aid
    fid=r['research_family_id']
    if fid in fams:return fams[fid]['headword'],'family-head-proxy',fid
    return '','no-reconstruction',''
def screen_class(word):
    p=old_features(word)
    if p['old_nuclei']==2 and p['old_accent_count']==1:
        if p['old_first_quantity']=='long':return 'old-long-barytone' if p['old_accent_position']==1 else 'old-long-oxytone'
        return 'old-short-barytone' if p['old_accent_position']==1 else 'old-short-oxytone'
    if p['old_accent_count']==1:return 'other-accented-formation'
    return 'input-accent-undetermined'
def outcome(r):
    o=r['modern_outcome'];p=r['modern_accent_from_right']
    if r['notation']=='brokskat-stress' or r['notation']=='dras-stress-vowel-sequence':p=r['stress_from_right']
    elif r['notation']=='survey-phonetic' and r['stress_from_right']!='':p=r['stress_from_right']
    elif r['notation']=='kundal-mixed-legacy':p=r['contour_from_right']
    if p!='' and r['modern_vowel_sequence']:return o+'@position-unresolved'
    return o+('@-'+str(p) if p!='' else '')
def main():
    rows=load_analysis_tokens();anns=load_annotations();fams={x['family_id']:x for x in tsv('families.tsv')};anc=load_ancestors()
    observations=[];coverage=defaultdict(Counter);cells=defaultdict(list)
    for r in rows:
        c=coverage[(r['language_id'],r['source_keys'])];c['tokens']+=1;c['linked']+=bool(r['research_family_id']);c['unknown_ancestry']+=not bool(r['research_family_id']);c['explicit_review']+=r['individual_review'] not in ['unlinked-inventory','family-context-first-pass']
        if not r['research_family_id']:continue
        word,kind,aid=input_for(r,anc,fams);p=old_features(word);cl=screen_class(word)
        reasons=[]
        if r['strict_exclusion']:reasons.append(r['strict_exclusion'])
        if not r['modern_single_word']:reasons.append('multiple-words-or-alternatives')
        if r['comparison_only']:reasons.append('comparison-only')
        if r['modern_vowel_sequence']:reasons.append('vowel-sequence-syllabicity-unresolved')
        # Hyphens, fragment markers and grammatical clitics are retained in
        # appendices, but not interpreted as whole nominal citation words.
        if re.search(r'[-=°…]',r['reading_form']):reasons.append('fragment-or-morphological-boundary')
        if r['research_link_confidence']=='provisional':reasons.append('provisional-etymology')
        v=dict(analysis_token_id=r['analysis_token_id'],record_id=r['id'],family_id=r['research_family_id'],
          language=r['language_id'],dialect=lect(r),source=r['source_keys'],form=r['reading_form'],gloss=r['research_gloss'],
          historical_input=word,input_basis=kind,input_id=aid,input_class=cl,**p,notation=r['notation'],
          outcome=outcome(r),raw_outcome=r['modern_outcome'],modern_nuclei=r['modern_nuclei'],
          accent_from_right=r['modern_accent_from_right'],stress_from_right=r['stress_from_right'],
          screening_exclusions=';'.join(dict.fromkeys(reasons)),family_analysis=anns[r['research_family_id']]['analysis'],
          family_unresolved=anns[r['research_family_id']].get('unresolved',''),individual_review=r['individual_review'])
        observations.append(v)
        cells[(cl,r['language_id'],r['research_family_id'])].append(v)
    write_tsv('historical-observations.tsv',observations)
    write_tsv('coverage-research-by-source.tsv',({'language':k[0],'source':k[1],**c} for k,c in sorted(coverage.items())))
    summary=[];famcells=[]
    for (cl,lang,fid),vv in sorted(cells.items()):
        eligible=[v for v in vv if not v['screening_exclusions']]
        os=sorted({v['outcome'] for v in eligible});es=sorted({v['outcome'] for v in vv if v['screening_exclusions']})
        famcells.append(dict(input_class=cl,language=lang,family_id=fid,headword=fams[fid]['headword'],
          eligible_outcomes=os,excluded_outcomes=es,eligible_tokens=len(eligible),all_tokens=len(vv),
          sources=sorted({v['source'] for v in vv}),forms=sorted({v['form'] for v in vv})))
    write_tsv('input-class-family-outcomes.tsv',famcells)
    for cl in sorted({v['input_class'] for v in observations}):
        for lang in LANGS:
            vv=[v for v in observations if v['input_class']==cl and v['language']==lang]
            fids={v['family_id'] for v in vv};good=[v for v in vv if not v['screening_exclusions']]
            byout=defaultdict(set)
            for v in good:byout[v['outcome']].add(v['family_id'])
            summary.append(dict(input_class=cl,language=lang,all_families=len(fids),eligible_families=len({v['family_id'] for v in good}),
                 outcome_family_counts={o:len(ff) for o,ff in sorted(byout.items())},
                 note='Outcome counts overlap when one family has multiple dialect/source/cell outcomes; not independent token votes.'))
    write_tsv('input-class-summary.tsv',summary)
    # Deliberately broad falsification of the simplest old-long-accent claim.
    tests=[];residuals=[]
    for cl,pred in [('old-long-barytone','E'),('old-long-oxytone','L')]:
        for lang in LANGS:
            vv=[v for v in observations if v['input_class']==cl and v['language']==lang and not v['screening_exclusions'] and v['notation'] in MORA and v['modern_nuclei']==1 and v['raw_outcome'] in ['E','L']]
            groups=defaultdict(list)
            for v in vv:groups[v['family_id']].append(v)
            counts=Counter()
            for fid,rr in groups.items():
                os={v['raw_outcome'] for v in rr};status='consistent' if os=={pred} else 'conflicting' if pred in os else 'opposite'
                counts[status]+=1
                if status!='consistent':residuals.append(dict(test=cl,language=lang,family_id=fid,expected=pred,observed=sorted(os),status=status,
                    forms=sorted({v['form']+' ['+v['dialect']+';'+v['source']+']' for v in rr}),
                    explanation=anns[fid]['analysis'],unresolved=anns[fid].get('unresolved','')))
            tests.append(dict(test=cl,language=lang,prediction=pred,scorable_families=len(groups),**counts,
               scope='Modern monosyllabic E/L forms, all nearest two-syllable old-long inputs, no manual nominal/formation restriction; exploratory falsification screen, not an established law.'))
    write_tsv('old-long-screen.tsv',tests);write_tsv('old-long-screen-residuals.tsv',residuals)
    print('observations',len(observations),'family cells',len(famcells),'residual cells',len(residuals))
if __name__=='__main__':main()
