"""Manually reviewed nominal Palula–Kalkoti comparative domains.

The statistical sample includes unmarked/unscorable cells in its denominator
inventory. It does not turn the selected examples in published tone tables
into an unbiased sample of known tone categories.
"""
import json,re
from collections import defaultdict,Counter
from analysis_data import tsv,load_records,load_annotations,write_tsv,HERE

VERBS={'4236','6141','6518','13756','10452','12225','3865','5046','4008','8012','9837','8209','841','10278','13085'}
NOTES={
'1351':'Mother yéei has an unequal-vowel sequence; Hultman explicitly treats final-vowel loss as relevant, but the conservative automated nucleus test excludes it. Include separately as primary-author analysis.',
'2462':'The full numeral áak and reduced article áa have different coda shapes; do not count them as independent etyma or infer zero tone from unmarked äk/ä.',
'4147':'Cow ghaáu has a vowel sequence and cannot be classified as a transparent unaccented short-u ending. Its apparent counterexample to apocope is excluded for this independent structural reason.',
'4368':'Village ghróom/draám is a genuine counterexample to the simple Palula E→Kalkoti no-High mapping. Hultman Table6p12 explicitly prints draám beside ghróom. A former extra ending, analogical reaccentuation or contact could explain it, but none is independently demonstrated. Palula ghr also fails to predict Low here; do not hide that second issue.',
'6261':'Grandfather and grandmother are two lexemes in one expressive kin family. Both independently retain a short gender vowel in Palula and lose it in Kalkoti. Count lexical cells and broad families separately.',
'6368':'Long is short-vowel dhrígu/dríg. Its Kalkoti outcome is Hshort, which belongs to the final-High result of apocope rather than an invented long rising vowel.',
'6658':'Twelve bóoš/baáš differs in High location. It is an independently identifiable teen compound, and the Kalkoti teen series is reaccented toward the -eéš/-aáš element; report it as compound-series remodeling, not an exceptionless simplex rule.',
'7047':'Root neer corresponds to Palula neeṛíi with an accented long final vowel, a different derivation from the canal/bamboo simplex. It falls outside the unaccented short-final-vowel apocope class.',
'9828':'Man míiš/meéš is Hultman’s explicit counterexample. Palula míiš is EARLY (also Strand mʹîš), not miíš. Its competing manuṣya/martya ancestry and remodeled plurals do not independently establish the missing Kalkoti ending. Keep the High source unresolved.',
'6001':'Thirteen tríiš/treéš joins the independently recognizable Kalkoti teen series with final High. This is compound-series reaccentuation; the old first-accented tráyōdaśa is not a transparent unextended monosyllabic input.',
'9982':'Meat maas is explicitly said to lack Low despite Palula mhaás. Its unmarked High status remains conservative/unscored; absence of Low alone does not prove a zero-High category.',
'10978':'Salt lhoóṇ/lùun is a Palula L versus Kalkoti Low correspondence. It is compatible with Low obscuring an otherwise expected early High, but that tonal interaction is a hypothesis rather than a recovered stage.',
'5589':'Belly ḍheér/ḍä̀är has the same Palula L versus Kalkoti Low pattern as salt and wheat. Old root-quantity variants prevent identifying its older mora history from the headword alone.',
'4287':'Wheat ghoóm/goom has a documented low-level contour in 2013, alongside secondary aspiration/metathesis in Palula. It is not an unmarked no-tone observation.',
'48':'Walnut ac̣hoóṛ/c̣hòor also reduces an entire initial syllable. Its Low may interact with aspiration and onset reanalysis, so it is not a simple same-root monosyllable correspondence.',
'10716':'Song rhoó/róo follows Palula L→Kalkoti H1, while explicitly lacking Low despite rh. These two dimensions must be kept separate.',
'8399':'Boy phoó/púu has an accented LONG final vowel in Palula; it is not in the short unaccented final-u apocope class.',
'2512':'Sheep yíiṛi/eér preserves the short final feminine vowel only in Palula and matches the final-High apocope outcome.',
}

def high(o):
    if o in ['H2','Low+H2','Hshort','P-high-rising','P-low-rising']:return 'final-High-or-rising'
    if o in ['H1','P-high-falling']:return 'early-High-or-falling'
    if o in ['0-explicit','P-high-level']:return 'zero-High-or-default'
    if o in ['Low','P-low-level']:return 'Low-without-marked-High'
    return 'unknown'

def main():
    rows=tsv('kalkoti-palula-candidates.tsv');anns=load_annotations();out=[]
    for r in rows:
        fid=r['family_id'];reasons=[]
        if fid in VERBS:reasons.append('unmatched-verbal-cells')
        if r['palula_outcome']=='vowel-sequence-marked':reasons.append('Palula-vowel-sequence')
        if r['palula_final']=='short-final-vowel' and r['palula_accent_from_right']!='2':reasons.append('not-a-simple-unaccented-final-vowel')
        if r['palula_final']!='short-final-vowel' and int(r['palula_nuclei'])!=1:reasons.append('Palula-polysyllabic-other-formation')
        if r['palula_final']=='short-final-vowel':cl='Palula-prefinal-accent-plus-short-final-vowel';pred='final-High-or-rising'
        elif r['palula_outcome']=='E':cl='Palula-E-without-short-final-vowel';pred='zero-High-or-default'
        elif r['palula_outcome']=='L':cl='Palula-L-without-short-final-vowel';pred='early-High-or-falling'
        else:cl='other-comparative-structure';pred=''
        obs=high(r['kalkoti_outcome']);status='excluded' if reasons or not pred else 'unscorable' if obs=='unknown' else 'consistent' if obs==pred else 'Low-interaction' if obs=='Low-without-marked-High' else 'residual'
        out.append({**r,'input_class':cl,'prediction':pred,'observed_category':obs,'status':status,'exclusion':';'.join(reasons),'adjudication':NOTES.get(fid,anns[fid]['analysis'])})
    # The wordlist's generic horse gloss versus Palula horse (generic), stallion
    # is an independently inspected semantic match missed by exact-gloss retrieval.
    allrows=load_records();kk=[r for r in allrows if r['language_id']=='Kalk' and r['source_keys'] in ['kalkoti','hultman2023kalkoti'] and r['research_family_id']=='4516'];pp=[r for r in allrows if r['language_id']=='Phal' and r['source_keys']=='liljegren' and r['reading_form']=='ghúuṛu']
    assert len(pp)==1
    for k in kk:
        out.append(dict(family_id='4516',gloss='horse',palula='ghúuṛu',palula_gloss=pp[0]['research_gloss'],palula_nuclei=2,palula_final='short-final-vowel',palula_outcome='E',palula_accent_from_right=2,kalkoti=k['reading_form'],kalkoti_source=k['source_keys'],kalkoti_outcome=k['modern_outcome'],kalkoti_record_id=k['id'],palula_record_id=pp[0]['id'],input_class='Palula-prefinal-accent-plus-short-final-vowel',prediction='final-High-or-rising',observed_category=high(k['modern_outcome']),status='consistent',exclusion='',adjudication='Horse has both an unaccented final u in Palula and initial voiced aspiration. Kalkoti Low plus final High shows the two conditioning dimensions together.'))
    write_tsv('kalkoti-palula-adjudicated.tsv',out)
    summaries=[]
    for cl in sorted({r['input_class'] for r in out}):
        for source in ['kalkoti','hultman2023kalkoti']:
            rr=[r for r in out if r['input_class']==cl and r['kalkoti_source']==source]
            cells=defaultdict(list)
            for r in rr:cells[(r['family_id'],r['gloss'])].append(r)
            counts=Counter()
            for key,rs in cells.items():
                ss={r['status'] for r in rs};valid=ss-{'unscorable','excluded'}
                status='conflicting' if len(valid)>1 else next(iter(valid)) if valid else 'unscorable' if 'unscorable' in ss else 'excluded'
                counts[status]+=1
            summaries.append(dict(input_class=cl,source=source,lexical_cells=len(cells),broad_families=len({r['family_id'] for r in rr}),statuses=dict(counts),scope='Manually reviewed DB cognates; different gloss cells in a family remain separate. Author-selected phonetic examples are not an unbiased known-tone sample.'))
    write_tsv('kalkoti-palula-summary.tsv',summaries)
    combined=[]
    for cl in sorted({r['input_class'] for r in out}):
        cells=defaultdict(list)
        for r in out:
            if r['input_class']==cl:cells[(r['family_id'],r['palula'])].append(r)
        for (fid,form),rs in cells.items():
            valid=[r for r in rs if r['status'] not in ['excluded','unscorable']]
            states={r['status'] for r in valid}
            status='conflicting' if len(states)>1 else next(iter(states)) if states else 'unscorable' if any(r['status']=='unscorable' for r in rs) else 'excluded'
            combined.append(dict(input_class=cl,family_id=fid,palula=form,glosses=sorted({r['gloss'] for r in rs}),kalkoti_forms=sorted({r['kalkoti'] for r in rs}),observed=sorted({r['observed_category'] for r in valid}),status=status,sources=sorted({r['kalkoti_source'] for r in rs}),exclusions=sorted({r['exclusion'] for r in rs if r['exclusion']}),adjudication=rs[0]['adjudication']))
    write_tsv('kalkoti-palula-combined.tsv',combined)
    csum=[]
    for cl in sorted({r['input_class'] for r in combined}):
        rr=[r for r in combined if r['input_class']==cl]
        csum.append(dict(input_class=cl,lexeme_form_cells=len(rr),broad_families=len({r['family_id'] for r in rr}),statuses=dict(Counter(r['status'] for r in rr))))
    write_tsv('kalkoti-palula-combined-summary.tsv',csum)
    print(json.dumps(summaries,ensure_ascii=False,indent=2))
    print('COMBINED',json.dumps(csum,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
