"""All-language outcome ranges for the counterparts of tested lexical classes.

Exact class membership and broader etymological-family counterparts are
different fields. These panels display evidence, not cross-language accuracy.
Unlinked class members are retained without inventing cognates elsewhere.
"""
import json
from collections import defaultdict,Counter
from analysis_data import load_analysis_tokens,load_annotations,tsv,write_tsv,HERE
from quantify import LANGS,lect,outcome

def main():
    tokens=load_analysis_tokens();anns=load_annotations();byid=defaultdict(list);byfam=defaultdict(list)
    for r in tokens:byid[r['id']].append(r);byfam[r['research_family_id']].append(r)
    memberships=[];catalog={}
    def add(cl,ids,definition,source_table,exact_tokens=None,source_filter=None):
        catalog[cl]=dict(class_id=cl,definition=definition,source_table=source_table,
          interpretation='Counterpart ranges are all records in the same research family, including different formations and senses. Only records explicitly selected by the source table are direct class members; no automatic transfer of the grammatical class to another language.')
        for rid in ids:
            for r in byid[rid]:
                if exact_tokens is not None and r['analysis_token_id'] not in exact_tokens:continue
                if source_filter is not None and r['source_keys'] not in source_filter:continue
                memberships.append(dict(class_id=cl,record_id=rid,analysis_token_id=r['analysis_token_id'],family_id=r['research_family_id'],language=r['language_id'],form=r['reading_form'],gloss=r['research_gloss']))
    for cl in ['short-a-without-h','short-a-with-h']:
        rr=[r for r in tsv('palula-short-a-pairs.tsv') if r['input_class']==cl]
        if rr:add(cl,{rid for r in rr for rid in json.loads(r['record_ids'])},'Biori short-a comparative input, partitioned by h/aspiration; consult closed-syllable and lexeme sensitivity.','palula-short-a-pairs.tsv',source_filter={'liljegren'})
    # Use the actual labels present rather than silently dropping a spelling variant.
    for cl in sorted({r['input_class'] for r in tsv('palula-short-a-pairs.tsv')}):
        if cl in catalog:continue
        rr=[r for r in tsv('palula-short-a-pairs.tsv') if r['input_class']==cl]
        add(cl,{rid for r in rr for rid in json.loads(r['record_ids'])},'Biori short-a comparative input, with h/aspiration; consult the full tested-pair scope.','palula-short-a-pairs.tsv',source_filter={'liljegren'})
    for file,cl,definition in [
      ('gilgit-o-adjectives.tsv','Gilgit-short-o-adjectives','Source-tagged Gilgit adjectives ending in short o.'),
      ('palula-tagged-u-adjectives.tsv','Palula-short-u-adjectives','Source POS-tagged Palula adjectives ending in short u, including accented ú.'),
      ('palula-umlaut-i-nouns.tsv','Palula-aa-ee-i-nouns','Source i-declension full comparable aa/ee+i paradigms; no accent used for selection.'),
      ('palula-i-decl-extension.tsv','Palula-other-i-nouns','Full i-declension paradigms outside the aa/ee+i selection, with one additional final-i nucleus.')]:
        rr=[r for r in tsv(file) if not r.get('status','').startswith('excluded')]
        add(cl,{r['record_id'] for r in rr},definition,file,source_filter={'degener-shina2008','buddruss-shina1996'} if cl.startswith('Gilgit') else {'liljegren'})
    rr=[r for r in tsv('palula-u-adjectives.tsv') if r['input'].startswith('Uml')]
    add('Palula-umlaut-u-adjectives',{r['record_id'] for r in rr},'Independently tagged umlaut masculine-u/feminine-i class, including unknown accent readings.','palula-u-adjectives.tsv',source_filter={'liljegren'})
    rr=tsv('palula-u-adjectives.tsv')
    add('Palula-grammatical-u-adjectives',{r['record_id'] for r in rr},'Full regular/umlaut gender-inflecting short-u class, including participles, residuals and unscorable citations.','palula-u-adjectives.tsv',source_filter={'liljegren'})
    # These are presentation joins of the already frozen model inventories.
    # They do not rerun a selection against new lexical evidence.
    raising=tsv('vowel-raising-reviewed.tsv')
    for cl in sorted({r['input_class'] for r in raising if r['tested_syllable_domain']=='word-final-closed'}):
        rr=[r for r in raising if r['input_class']==cl]
        add('raising-'+cl,{rid for r in rr for rid in json.loads(r['record_ids'])},
          'Biori input accent, vowel quality and final closed syllable, before observing Ashret quality; both sides of the reviewed pair are shown.','vowel-raising-reviewed.tsv',source_filter={'liljegren'})
    paired=tsv('kalkoti-palula-adjudicated.tsv')
    for cl in sorted({r['input_class'] for r in paired if r['input_class'].startswith('Palula-')}):
        rr=[r for r in paired if r['input_class']==cl and not r['status'].startswith('excluded')]
        add('Kalkoti-comparison-'+cl,{r[k] for r in rr for k in ['palula_record_id','kalkoti_record_id']},
          'Palula comparative structure selected independently of the Kalkoti outcome; model-excluded pairings omitted, unknown and residual outcomes retained.','kalkoti-palula-adjudicated.tsv',source_filter={'liljegren','kalkoti','hultman2023kalkoti'})
    dras=tsv('dras-suffix-accent-review.tsv')
    for suffix in sorted({r['suffix'] for r in dras}):
        add('Dras-plural-'+suffix,{r['plural_id'] for r in dras if r['suffix']==suffix},
          'Dras plural citations selected by their final segments; counterparts elsewhere are lexical relatives, not claims of identical plural morphology.','dras-suffix-accent-review.tsv',source_filter={'rajapurohit2012'})
    clusters=tsv('short-root-cluster-screen.tsv')
    for vowel in sorted({r['input_vowel'] for r in clusters}):
        rr=[r for r in clusters if r['input_vowel']==vowel]
        add('short-root-cluster-'+vowel,{r['record_id'] for r in rr},
          'The frozen exploratory cluster screen partitioned by old root vowel. Source/formation caveats in the original table remain; no universal compensatory mechanism is asserted.','short-root-cluster-screen.tsv',source_filter={r['source'] for r in rr})
    properties=tsv('property-location-screen.tsv')
    add('retained-ending-core-properties',{r['record_id'] for r in properties},
      'The frozen core-property family/sense inventory with a retained short final vowel; all marked, unmarked and excluded source readings remain in the source table.','property-location-screen.tsv')
    for cl,nums in [('ten-compounds',set(range(11,19))),('nineteen-twenty-comparison',{19,20})]:
        rr=[r for r in tsv('numeral-series-records.tsv') if int(r['numeral']) in nums]
        add(cl,{r['record_id'] for r in rr},'Numerals selected by meaning and independently identified ten versus twenty formations; whole-compound identity varies across languages.','numeral-series-records.tsv',exact_tokens={r['analysis_token_id'] for r in rr})
    # The nominal old-long inputs are already selected by formation and meaning.
    nominal={r['family_id'] for r in tsv('old-long-nominal-formation-audit.tsv')}
    for cl in ['old-long-barytone','old-long-oxytone']:
        rr=[r for r in tsv('historical-observations.tsv') if r['family_id'] in nominal and r['input_class']==cl]
        add(cl+'-nominals',{r['record_id'] for r in rr},'Restricted29-family nominal follow-up, two-nucleus old-long input, independently marked old accent.','old-long-nominal-formation-audit.tsv',exact_tokens={r['analysis_token_id'] for r in rr})
    unique={(r['class_id'],r['analysis_token_id']):r for r in memberships};memberships=list(unique.values())
    write_tsv('class-memberships.tsv',memberships)
    out=[];summary=[]
    for cl in catalog:
        members=[r for r in memberships if r['class_id']==cl];keys=defaultdict(set)
        for r in members:keys[r['family_id'] or 'unlinked:'+r['record_id']].add(r['analysis_token_id'])
        counts=defaultdict(lambda:defaultdict(set));available=defaultdict(set)
        for key,selected in keys.items():
            rr=byfam[key] if not key.startswith('unlinked:') else byid[key.split(':',1)[1]]
            for lang in LANGS:
                ll=[r for r in rr if r['language_id']==lang]
                if ll:available[lang].add(key)
                obs=sorted({outcome(r) for r in ll});forms=sorted({r['reading_form']+' ['+r['research_gloss']+'; '+r['source_keys']+'; '+lect(r)+']' for r in ll})
                for o in obs:counts[lang][o].add(key)
                out.append(dict(class_id=cl,family_or_unlinked_member=key,language=lang,forms=forms,outcomes=obs,
                  selected_class_tokens=sorted({r['analysis_token_id'] for r in ll if r['analysis_token_id'] in selected}),
                  all_counterpart_tokens=[r['analysis_token_id'] for r in ll],strict_exclusions=sorted({r['strict_exclusion'] for r in ll if r['strict_exclusion']}),
                  interpretation=catalog[cl]['interpretation'],family_analysis=anns[key]['analysis'] if key in anns else 'No secure ancestral alignment; counterparts in other languages cannot be supplied from meaning alone.'))
        for lang in LANGS:
            summary.append(dict(class_id=cl,language=lang,selected_family_or_unlinked_member_count=len(keys),
              families_or_members_with_counterpart_records=len(available[lang]),families_or_members_without_counterpart_records=len(keys)-len(available[lang]),
              observed_counterpart_outcome_counts={o:len(v) for o,v in sorted(counts[lang].items())},
              note='Outcome counts overlap for source/lect/cell variants. These are counterpart ranges, not direct tests of identical morphology in all languages.'))
    write_tsv('class-counterparts-all-languages.tsv',out);write_tsv('class-counterpart-outcome-summary.tsv',summary)
    write_tsv('class-definitions.tsv',catalog.values())
    (HERE/'class-catalog.json').write_text(json.dumps(list(catalog.values()),ensure_ascii=False,indent=2)+'\n')
    print(len(catalog),'classes',len(memberships),'exact membership tokens',len(out),'family/language counterpart rows')
if __name__=='__main__':main()
