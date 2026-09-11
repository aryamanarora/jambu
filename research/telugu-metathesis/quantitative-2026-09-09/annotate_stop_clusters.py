#!/usr/bin/env python3
"""Adjudicate every hit of the complete Kui/Pengo velar–labial screen.

Manual entry lists identify the source-supported input analyses. The parser only
copies explicitly printed derivations; output order alone never establishes input.
These process-specific observations do not expand the classical apical numerator.
"""
import csv,html,json,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n):
    with (P/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rs):
    with (P/n).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t');w.writeheader();w.writerows(rs)
# Each listed entry was inspected in stop-cluster-screen.log, 2026-09-09.
KUI_D=set(('1080 1349 1628 1817 1851 1868 1980 2136 2180 2260 228 2363 240 2557 2585 2654 2800 2955 325 3339 3359 3376 3430 3439 3451 3482 3514 3665 3714 3783 3808 3962 4008 4152 4194 4235 4414 4423 4470 4760 4761 4870 4891 4975 5002 5180 520 5200 5334 5363 5411 5432 5519 5522 706 710 715 757 859 874 931').split())
PENGO_D={'1079','2804','3253','809'}
PLURALS={'1273','178','2018','2364','2881','2115'}
AMBIG={'1957','2024','2335','333','502','5450'}
NOTE={
 'd2800':'Source prints sek-p- beside sēpka and sēkt-. Vowel-length mismatch is separate from local k-p reversal; exact vowel needs original vocabulary checking.',
 'd4235':'Surface põpka versus source pōk-p- includes a nasal/diacritic difference. Local velar-labial order is still explicit; quantity/nasal spelling needs source checking.',
 'd325':'Parser splits abga (<) and explanatory ag-b into separate records. Only abga is the attested lexeme; ag-b is a supplied pre-reordering analysis.',
 'd1851':'kōpka and kṛōpka are related formations within one entry; do not count two independent roots.',
 'd3376':'trupka and drūpka are related intransitive/transitive swing formations; one family.',
 'd4152':'brupka and pṛupka are related pluck/break formations; one family, cluster voicing/place history separate.',
 'd809':'ipka and ipka vā are simplex and compound uses of one intensive; one family.',
 'd5519':'Homophonous vēpka stretch and d5522 cease are not merged merely from their surface identity.',
 'd5522':'Homophonous with d5519 stretch, but no independent semantic/derivational connection established.'}
def main():
    rs=read('stop-cluster-screen.tsv');out=[]
    for r in rs:
        entry=r['Research_Group'];num=entry[1:] if entry.startswith('d') else '';lang=r['Language_ID']
        f=unicodedata.normalize('NFC',html.unescape(r['Form']));g=unicodedata.normalize('NFC',html.unescape(r['Gloss']))
        joined=f+' '+g
        category='lexical-ineligible';inp='';past='';mechanism='';obs='';stage='';confidence=''
        if lang in {'Kuwi','Manda'}:
            if (lang,entry) in {('Kuwi','d1628'),('Kuwi','d766'),('Manda','d1079'),('Manda','d3570')}:
                category='comparatively-supported-verbal-input';obs='D';stage='verbal-velar+labial-formative'
                inp={('Kuwi','d1628'):'kug/kok + pi#ki',('Kuwi','d766'):'ek/eng + pi#ki',('Manda','d1079'):'kak + intensive-ba',('Manda','d3570'):'nēk + intensive-ba'}[(lang,entry)]
                mechanism='Independent local full stem in panel-029 supports a final velar. Labial derivation and voicing assimilation yield the observed p-k/b-g order; purely phonetic origin versus analogical history remains unresolved.'
                confidence='medium-high for local morphological ordering'
            elif lang=='Kuwi' and entry=='d1080':
                category='possible-retained-counterexample';obs='R?';stage='verbal-velar+labial-formative'
                inp='kak + pi-nai'
                mechanism='DEDR explicitly records Schulze1913 kakpinai joke beside kak laugh. This retains k-p, whereas Hume2002 p.38 ex.39 reports Israel1979 kap-ki a- laugh at each other. Different sources and grammatical formations must be preserved; lexicalization, dialect variation and transcription error compete. Schulze1913 page not obtained, so do not either erase the counterexample or treat it as secure falsification.'
                confidence='high for database spelling; lower for original transcription and exact suffix'
            elif num in {'178','2468','2958','3032','4979'}:
                category='nominal-plural-control';obs='O';stage='nominal-stem+plural-k'
                inp={'178':'amb + plural-k','2468':'hāp + plural-k','2958':'ḍīmb + plural-k','3032':'dṛa / dṛap? + plural-k','4979':'mūrm / mrū? + plural-k'}[num]
                mechanism='This is a noun plural formation; the record supplies no velar-before-labial input. Nasal/labial alternation or plural allomorphy is separate from verbal k-p reversal.'
                confidence='medium; exact nominal allomorphy partly unresolved'
            elif (lang=='Manda' and entry=='d1731') or (lang=='Kuwi' and num in {'3143','3323','4527'}):
                category='labial-stem-plus-velar-control';obs='O';stage='labial-stem+velar-formative'
                inp={'d1731':'kup(p) heap + k-i','d3143':'tap stop + k-ali','d3323':'hūp spit + k-i/a','d4527':'pomp interlace + k-i'}[entry]
                mechanism='Independent labial base (panel-029 for heap, quiet and spit) supports original p-before-k, not an underlying velar-before-labial sequence. The interlace compound remains less fully segmented.'
                confidence='high for labial bases except interlace, medium for exact derivation'
            elif lang=='Kuwi' and num in {'2800','2926'}:
                category='input-unresolved';obs='A'
                mechanism='A velar-labial analysis is possible, but the exact local full stem and labial formative are not independently both supplied. For nabgali, southern namukku includes a nasal absent in the output; for hēpk, related Kui sēpka is suggestive but not a Kuvi paradigm.'
            elif lang=='Kuwi' and entry=='d1224':
                category='different-noninitial-contraction';obs='A';inp='*kVppokk > *kpōk > pōke [source proposal]'
                mechanism='The screen matched a proposed word-initial k-p cluster formed by vowel deletion, not a verbal velar+labial suffix. Subsequent k loss is a separate historical proposal.'
            else:
                category='english-or-metadata-match';obs='ineligible';mechanism='English gloss or bibliographic shorthand matched the broad screen; no relevant lexical sequence.'
        elif num in (KUI_D if lang=='Kui' else PENGO_D):
            if entry=='d325' and r['Form']=='ag-b':
                category='editorial-input-fragment';obs='not-an-attestation';inp='ag-b-';mechanism='Source derivational analysis, not a retained-order lexical counterexample.'
            elif entry=='d4975' and r['Form']=='mrunga vīpka':
                category='input-unresolved';obs='A';mechanism='Compound vīpka is not independently supplied with a velar stem in this record; do not transfer mruk-p- from neighboring mrupka.'
            else:
                category='source-supported-verbal-input';obs='D';stage='verbal-velar+labial-formative'
                # HTML italics are not a reconstructed input. The d325 source
                # splits its explicit ag-b analysis into another database row.
                candidates=re.findall(r'<\s*([^;)>]+)',joined)
                candidates=[s.strip() for s in candidates if re.search(r'[kg]-?[pb]',s.replace(' ',''))]
                inp='ag-b-' if entry=='d325' else (candidates[0] if candidates else '')
                assert inp and re.search(r'[kg]-?[pb]',inp.replace(' ','')), (entry,lang,f,'No explicit velar-labial input extracted')
                q=re.search(r';\s*([^;)]+t-)\s*\)',joined);past=q.group(1).strip() if q else ''
                mechanism='The source explicitly supplies velar-before-labial morphological input; attested labial-before-velar supports a synchronic exchange analysis. Garrett and Blevins2009 pp.537–543 propose an analogical origin through replacement and double marking, so these forms do not independently prove prehistoric phonetic transposition.'
                confidence='high for local source analysis; deeper root history not asserted'
        elif lang=='Kui' and entry=='d1691':
            category='duplicate-compound';obs='same-family';mechanism='gunḍis kopka contains the already-counted sitting verb1628; squat construction is not a second independent velar–labial event.'
        elif num in PLURALS:
            category='nominal-plural-control';obs='O';stage='nasal/labial-stem+plural-k'
            inp={'d1273':'krēmbu + plural-k','d178':'āmbu/am + plural-k','d2018':'klāmbu + plural-k','d2364':'jrāmbu + plural-k','d2881':'sōmbu + plural-k','d2115':'branch stem + plural-k; exact base not given'}[entry]
            mechanism='Labial precedes the plural velar in the morphological input already; nasal loss and/or devoicing can yield p-k without k-p reversal. This is an independently different input class.'
            confidence='medium; precise plural allomorphy requires full paradigms'
        elif lang=='Kui' and num in {'1957','2024'}:
            category='vowel-stem-plus-complex-pk-control';obs='O';stage='vowel-stem+p+ki'
            inp='gī + p + ki' if num=='1957' else 'kī + p + k'
            mechanism=('Winfield1928 p.73 directly supplies gīva:gīpki do and explains p strengthening before ki. The lexical gipka form differs in written quantity, but no velar-before-labial input is established.' if num=='1957' else 'DEDR2024 supplies kīva put on clothes beside plural kīpka:kīpki. A vowel base plus complex p-k formation fits the independently recorded third-conjugation pattern. This is not the homophonous pour verb in Winfield p.73, and not evidence for kī-k-p.')
            confidence='high for independent vowel-final stem; medium for exact historical morphology'
        elif (lang=='Kui' and num in AMBIG) or (lang=='Pengo' and num in {'153','2800','2872','297','4527'}):
            category='input-unresolved';obs='A'
            mechanism={'d1957':'gipka (gip ki-) has a labial followed by a separate do element; no inherited k-p input supplied. Source parser strands the compound in gloss.',
                'd2024':'kīpka past kīpki- preserves pk throughout; no independent velar-final stem supplied.',
                'd2335':'japka reduplicated slapping construction can be expressive; no independent jak-p input.',
                'd333':'Affirmative āpka (āpki-) has no independently supplied velar-final input.',
                'd502':'Set-down dīpka past dīpki- is not a source-derived dīk-p- paradigm; initial apical history belongs to separate case analysis.',
                'd5450':'Swift vīpka (vīpki-) lacks an independently given vīk-p- input.',
                'd153':'Only apka may involve particle combination; full morphological input not established.',
                'd2800':'Cow-itch hēpkor could contain an itch stem, but neither velar-final stem nor formation is independently supplied in the Pengo record.',
                'd2872':'Database record alone supplies no full stem. Garrett and Blevins2009 p.538 independently supplies hōk-ba > hōbga wash clothes; counted in the separate source-paradigm audit, not silently upgraded to a database-internal derivation.',
                'd297':'Database priest ṛābga may be agent morphology. Garrett and Blevins2009 p.538 independently supplies ṛāk-ba > ṛābga sacrifice; source-paradigm evidence is separate and exact agent/verb relation remains to establish.',
                'd4527':'popka has no independently supplied pok-p input; source gloss id requires full etymon comparison.'}[entry]
        elif lang=='Pengo' and entry=='d5190':
            category='word-boundary-control';obs='R';inp='lup#gaṭ';mechanism='p followed by g across a word boundary is already labial–velar; no velar–labial input or metathesis.'
        else:
            category='english-or-metadata-match';obs='ineligible';mechanism='Screen matched English text (pumpkin, climbing, scoop, bag-pipe, etc.), not a relevant lexical velar–labial sequence.'
        out.append({'Record_ID':r['ID'],'Entry_ID':entry,'Language_ID':lang,'Source_Form':r['Form'],'Source_Gloss':r['Gloss'],'Source':r['Source'],
            'Input_Class':stage or 'not-established','Proposed_Immediate_Input':inp,'Supporting_Past_Stem':past,
            'Disposition':category,'Observed_Outcome':obs,'Derivation_and_Direction':mechanism,'Confidence':confidence,
            'Exception_Notes':NOTE.get(entry,''),'Family_ID':'d1628' if entry=='d1691' else entry,
            'Review_Scope':'Complete screen hit adjudicated for local velar/labial process; wider etymon comparison is limited unless separately present in casebook.'})
    write('stop-cluster-annotations.tsv',out)
    counts=[];members=[]
    for lang in ['Kui','Kuwi','Pengo','Manda']:
        subset=[r for r in out if r['Language_ID']==lang]
        for category in sorted({r['Disposition'] for r in subset}):
            hits=[r for r in subset if r['Disposition']==category];fs=defaultdict(list)
            for r in hits:fs[r['Family_ID']].append(r)
            counts.append(dict(Language_ID=lang,Disposition=category,N_Records=len(hits),N_Families=len(fs)))
            for fam,rr in fs.items():members.append(dict(Language_ID=lang,Disposition=category,Family_ID=fam,Record_IDs=';'.join(r['Record_ID'] for r in rr)))
    write('stop-cluster-counts.tsv',counts);write('stop-cluster-count-membership.tsv',members)
    print(json.dumps(counts,ensure_ascii=False,indent=2))
    assert len(out)==len(rs) and len({r['Record_ID'] for r in out})==len(out)
    (P/'stop-cluster-results.json').write_text(json.dumps({'screen_records':len(out),'counts':counts,
       'Caution':'Source-supported verbal inputs give an ascertainment-limited denominator. Their printed derivations were selected by the lexicographer; no claim of exhaustive productive paradigms or random sampling. Nominal pk plurals and unknown-input pk forms are separate, not negative members of the same reconstructed-input class.'},indent=2)+'\n')
if __name__=='__main__':main()
