"""Extension test outside the aa/ee+i subclass, selected without accent.

All43 new full-form candidates were read individually. Variant metadata can
still attach the main lemma's inflection to a different citation stem.
"""
import re,json,unicodedata as ud
from collections import Counter,defaultdict
from analysis_data import load_analysis_tokens,HERE,write_tsv
from phonology import modern_features

SPECIAL={
'f_btzw7q43us6ic':'Biori thupéek is a variant of toobaák but the attached toobakí inflection belongs to the main lemma. The distinct stem frame and vowel history make this an unverified dialect paradigm, like the rainbow synonym problem; retain the real early citation accent but exclude this pair from the strict paradigm test.',
'f_ujvlyk74hm24w':'Nose náas/nastí has a consonantal stem alternation as well as shortening. Early citation accent matches the independently attested Biori short nas and ordinary short-a lengthening; final plural i is a different accent-bearing position.',
'f_lke2sojllsqo6':'Grass čáar/čarí has E in the citation but final i in the inflection. The independent Biori short čar distinguishes newly lengthened aa from the aa/ee umlaut noun class.',
'f_stjehsosoczzo':'Lake sáar/sarí has E after ordinary short-a lengthening, independently supported by short Biori sar; it is a mobile i-declension noun despite citation E.',
'f_n3bocqps2kva2':'Plateau ḍáab/ḍabí preserves the ordinary short-a/new-long correspondence, with short Biori ḍab. Its final plural accent shows that i-declension membership does not alone force citation L.',
'f_zwahgkgiydy3e':'Colour ráang/rangí has E in the long citation and final i in the plural; short Biori rang provides independent quantity evidence. A regional loan can enter the same mobile class.',
'f_iu66i4pnaulcm':'Stream náaṛ/naṛí has E citation accent with a short inflected root and final i. It belongs to a different full paradigm from canal náaṛ/neeṛí and must not be merged merely because the citation spellings coincide.',
'f_enduuhx4of64m':'Defeat haár/haarí keeps aa in the inflected root and accents final i; absence of umlaut distinguishes this from aa/ee+i even though citation L is shared.',
'f_65qtgf7zbnfua':'Sacrifice qurbaán/qurbaaní retains long aa before final i, a regional loan formation without ee umlaut. It independently supports suffix accent but not the aa/ee vowel rule.',
'f_yh3due6ygh6rc':'Happiness xeerát/xeereetí has a short citation a and long inflected ee, so it is not in the long-aa citation subclass. The inflection nevertheless accents final i; verify the dialect quantity alternation before reconstructing an old stem.',
}
def main():
    out={}
    for r in load_analysis_tokens():
        if r['language_id']!='Phal' or r['source_keys']!='liljegren' or not r['modern_single_word'] or r['modern_vowel_sequence'] or r['modern_final_vowel']:continue
        m=re.search(r'Inflection: i-decl \(([^)]+)\): ([^;]+)',r['description'])
        if not m:continue
        inf=ud.normalize('NFC',m[2].strip())
        if re.search(r'[- ,/()\u0325]',inf):continue
        f=modern_features({**r,'original':inf})
        if f['modern_nuclei']!=r['modern_nuclei']+1 or f['modern_final_segment']!='i' or not f['modern_quantity_pattern'].endswith('S'):continue
        if r['modern_vowel_bases'].endswith('a') and r['modern_quantity_pattern'].endswith('L') and f['modern_vowel_bases'].endswith('ei'):continue
        status='excluded-unverified-variant-paradigm' if r['id']=='f_btzw7q43us6ic' else 'consistent' if f['modern_accent_from_right']==1 else 'residual'
        note='The full source inflection accents final i. Citation accent is retained as a separate outcome; the class was selected by consonant-final citation and source i-declension, not by either accent.'
        note+=' '+SPECIAL.get(r['id'],'')
        key=r['reading_form'],r['research_gloss'],inf
        out[key]=dict(record_id=r['id'],family_id=r['research_family_id'],citation=r['reading_form'],gloss=r['research_gloss'],inflected=inf,
          citation_outcome=r['modern_outcome'],citation_position=r['modern_accent_from_right'],inflected_outcome=f['modern_outcome'],inflected_position=f['modern_accent_from_right'],
          quantity_pattern=r['modern_quantity_pattern'],inflected_quantity_pattern=f['modern_quantity_pattern'],status=status,analysis=note,description=r['description'])
    assert len(out)==43
    rr=list(out.values());valid=[r for r in rr if not r['status'].startswith('excluded')]
    lexemes=defaultdict(list)
    for r in valid:lexemes[r['gloss'],r['inflected']].append(r)
    summary=dict(candidates=len(rr),valid_form_cells=len(valid),valid_lexemes=len(lexemes),status_counts=dict(Counter(r['status'] for r in rr)),
       citation_outcomes=dict(Counter(r['citation_outcome'] for r in valid)),inflected_positions=dict(Counter(r['inflected_position'] for r in valid)),
       scope='Extension outside the long-aa/ee+i subclass; full i-declension inflections only, one extra nucleus, consonant-final citations. This is a new structural subset, not random held-out sampling.')
    write_tsv('palula-i-decl-extension.tsv',rr)
    (HERE/'palula-i-decl-extension-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    ann=[dict(record_ids=[r['record_id']],analysis=r['citation']+' / '+r['inflected']+' ('+r['gloss']+'). '+r['analysis'],source='Liljegren2019 full dictionary inflection metadata; i-declension extension test') for r in rr]
    (HERE/'lexical_annotations_05.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ann))
    print(summary)
if __name__=='__main__':main()
