"""Export manually inspected Dras paradigms and bounded lexical comparisons.

All 287 candidate rows were read, together with their SG variants and lexical
comparators. Indexes refer to the frozen dras-plural-candidates.tsv. The
dictionary below is a manual adjudication, not a similarity acceptance rule.
"""
import json,re,unicodedata as ud
from collections import defaultdict,Counter
from analysis_data import tsv,load_records,HERE,write_tsv

LINKS={3:'549',5:'2025',9:'13355',19:'13415',20:'7785',21:'4161',22:'5798',23:'11348',
27:'9209',37:'13544',41:'8298',43:'4255',47:'12528',49:'13776',51:'9746',54:'3906',55:'12583',56:'920',57:'2349',58:'6694',59:'10512',60:'10258',65:'3329',66:'10258',70:'11009',72:'7733',73:'12062',74:'3438',75:'4889',79:'5589',83:'3607',84:'3257',85:'3135',86:'2757',87:'43',92:'2417',93:'5075',94:'12497',97:'12064',99:'2563',100:'10394',102:'7031',103:'7948',104:'13839',105:'4701',108:'13073',110:'6152',111:'4460',118:'f_iizwuh3wokzh6',120:'2860',121:'2860',132:'2629',133:'3942',141:'4842a',144:'13551',156:'9229',158:'5717',159:'5717',163:'4336',167:'1600',182:'3202',186:'12326',188:'10582',195:'7047',197:'2712',208:'3735',211:'8306',215:'6628',216:'2589',223:'7733',227:'12468',228:'2934',234:'100',236:'48',242:'5488',244:'14028',247:'4190',252:'10910',260:'3448',275:'9479',279:'10395'}

SPECIAL={
2:'Cave bó/bóyé retains a root acute and adds a suffix acute. The same two marks occur in the grammar discussion; do not normalize to a single final accent. Proposed khola/kotara comparisons are segmentally insufficient.',
6:'The flood candidates mix mu:s/mu:ze with a different multi-component expression. Use only the mu:s paradigm for segmental comparison; neither citation marks stress.',
8:'Hillock changes ʈhúko to ʈhuké: stress moves to the replacement plural vowel. The unextended -e rule is not sufficient.',
10:'Two singular vowel/accent variants occur under isthmus. Plural tóre agrees with tóri, but the source also has torí:. Preserve both as source-internal variation.',
14:'Mountain ʃeí/ʃʌyé involves vowel-sequence and glide alternation; old mountain synonyms do not establish its etymology. Final plural stress is marked.',
24:'Blind has two plural formations ʂé:ʋe and ʂé:. The first retains the consonant and adds a vowel; the second contracts. The suggested śrēḍa comparison requires independent segmental support.',
25:'Contracted plural of blind; keep separate from the extended ʂé:ʋe. Final accent is not the same suffixal mechanism as -éh.',
29:'The kin gloss maternal uncle’s wife needs checking against the phapi word’s usual paternal-aunt association; gender/kinship substitutions cannot be silently repaired.',
31:'People ʤʌ́k/ʤʌ́keɦ is stem-accented in vocabulary item170, whereas grammar p42 prints ʤʌ́kéɦ with an additional final acute. This is a real source-internal difference, not an exception to hide.',
32:'Wife’s brother has final-vowel/glide alternation, with several adjacent vowels; positional statistics require explicit syllabification.',
33:'The gloss group contains plain donkey and a female-donkey compound. The plural is the simple stem plus i; do not treat all SG strings as the same grammatical cell.',
35:'Bedbug has ə:/ʌ and e/i variants. The plural retains first-syllable stress across these variants.',
36:'Female-dog compound has two lexical stress marks; compound prosody is outside the one-stress simplex test.',
38:'Buffalo group conflates male/female compounds under a he-buffalo gloss. The two constituent accents must be retained; the compounds are not simple nominal citation words.',
39:'Female-buffalo compound is present under the he-buffalo gloss. Its final i and consonant voicing belong to the female paradigm, not an alternative plural of the male compound.',
43:'Dras gaa(v) belongs to the cow lexeme; comparative family gō is used as a root-level anchor, not proof that its citation singular is directly the old nominative.',
48:'Plural earthworm ʧh is visibly truncated relative to its singular compound. Exclude from accent tests; source extraction needs independent repair outside this research task.',
49:'Vocabulary egg ʈhuléh has suffix stress, whereas grammar discussion prints ʈhúle. Competing -eh/-e plural formations are independently attested; do not choose one for regularity.',
52:'The duplicated gnat/mosquito string and leaked number markers are extraction problems. Preserve as unresolved; do not parse as a single lexical form.',
56:'Dras ašp-like horse has an sp cluster shared with Iranian horse vocabulary. The comparative áśva family is a root comparison; inherited versus contact transmission remains open.',
58:'Leopard dĩ and dĩye preserve nasalization but no written accent. Their reduced shape matches the dvīpin family; no E/L outcome can be inferred.',
59:'Louse jũ/jũẽ has no explicit accent in this source. It cannot adjudicate the Gilgit/Palula late-long result.',
61:'Nest halo:l differs from the maa-derived nest comparison. No etymology is assigned from meaning alone.',
63:'Paw no:ryé illustrates the independently discussed -yé plural allomorph, with final accent; compare plain claw nó:re separately.',
67:'Raven/crow korkus has an expressive bird-name shape; do not force it under kāka solely by semantics. Final s/c alternation is visible in the plural.',
70:'Tail lamuṭe agrees segmentally with older Dras lumuṭ in the lāṅgūla family. Competing lūma/lamba and compound analyses are retained in the broader tail dossiers; this is not secure preservation of that headword’s accent.',
71:'Trunk has a ui/ue sequence; retain marked accent but leave syllable-count statistics unscored.',
73:'Wolf uruk/urke is a direct segmental and semantic comparison with vṛka; initial cluster vocalization and plural syncope are relevant, not the suggested unrelated wolf synonyms.',
82:'Canine tooth is a compound with accents on both constituents. The plural changes more than the final suffix; exclude from single-stress simplex tests.',
88:'Eyebrow includes the eye stem plus a second accented component. Compound accent and number agreement must be separated from simple noun stress.',
89:'Eyelid is an eye-plus-cover compound with two accent marks; the source lacks a matched simple SG in this candidate group.',
90:'Finger has nasalized adjacent vowels and leaked SG markers in the gloss. Accent exists but exact syllabification is unresolved.',
96:'Joints khriʦí has final i accent, contrasting with ankle khríʦ/khríʦi. Related anatomy is not sufficient to erase semantic or paradigm differences.',
101:'Lung ḍo:ro does not segmentally match the bhaṣma or phupphusa candidates. Leave its etymology open rather than propagating the earlier lung-reference problem.',
106:'Stomach has two acute marks and an additional stem element; its plural is a contraction/replacement pattern, outside the simple one-stress test.',
108:'Thigh śasna/śasne is compared with the independently recorded sakthan family through its distinctive sibilant/cluster structure. The exact nasal/long-vowel formation is not fixed by this comparison.',
118:'Fruit meva is an independently recorded regional loan comparison. The plural is an adapted vowel replacement; no Old Indo-Aryan inherited accent is claimed.',
120:'Knife item556 p95 has kəɽá:r/kəɽá:reh, stem stress. Item655 gives kʌɽá:r/kʌɽa:réh, suffix stress. Both readings are printed; treat the lexeme as conflicting.',
121:'Second knife entry has final plural stress; preserve its disagreement with item556 rather than selecting the regular-looking token.',
124:'Scissors dukʌ́ṭ/dukʌ́ṭeh retains stem stress despite final eh. The vocabulary prints it this way. A possible lexical compound/dual origin does not yet establish why its suffix differs.',
127:'Spoon has nasalized vowel sequences and an incomplete gloss boundary. Inflection is visible but nucleus/mora interpretation is unresolved.',
134:'Footwear khʌ́ɽʌk/khʌɽʌké retracts neither accent nor quantity uniformly; its plural shifts to final e. No independent class feature yet distinguishes it from stem-retaining e nouns.',
136:'Coat ko:ṭ is compatible with the English/regional loan coat. Its -eh plural is fully integrated into Dras suffix stress; lexical origin is a contact lead, not an established historical sound correspondence.',
146:'Pyjama has a parenthesized optional segment. Preserve as a variant expression and exclude from a single-form count.',
147:'Pearl motik suggests a regional motī plus k formation; māṇiya is not accepted from the shared pearl gloss alone.',
152:'Sapphire nilim resembles regional nīlam. The plural has suffix stress; an inherited nīla-derived analysis and a loan route remain alternatives.',
157:'Soap sabon is a regional loan-shaped stem and takes final-stressed eh; no Vedic-accent ancestry is asserted.',
158:'Spindle item690 has final-stressed ʈʂʌké, whereas item1001 and the grammar have root-stressed ʈʂʌ́ke. Retain the same-lexeme conflict and the SG quantity difference.',
159:'The second spindle plural has root stress; it agrees with the grammar example and conflicts with item690. More tokens do not resolve the disagreement.',
166:'Bolster uné:h has final long e plus h. It is listed separately from the short-eh screen because segmental identity of the suffix is not established by spelling alone.',
167:'Brick diṣṭik resembles iṣṭakā with an additional initial d and modified suffix. This is a provisional root comparison, excluded from strict historical-accent tests.',
170:'Carpet qali:n/kali:ne shows q/k variation and preserves stem stress. It is a regional loan-shaped stem; -e does not automatically attract stress.',
171:'Chair kurči resembles regional kursī. The -eh replacement is final-stressed; unrelated chair gloss comparisons are rejected.',
176:'The mat gloss groups three different nouns. Pair chhari only with chharyeh; the other mat nouns are not allomorphs selected by accent.',
177:'The purported plural is a multiword mat expression combining separate lexemes. Exclude from the simplex paradigm test.',
178:'The zangoṣ mat plural pairs with zangoṣ, not the other two singular mat nouns.',
182:'Nail vocabulary prints kí:l yéh with a space and two accents; the merged DB form kí:lyéh retains both. This may be a clitic-like/plural expression or inconsistent accent typography; do not silently remove the root mark.',
187:'The roof candidate chhiliṣeh is not the plural of śaro:ṇ. Its root and suffix both have acute marks. The other roof noun has an ordinary final-stressed eh plural.',
191:'Horse-shed is a compound with a separate horse word. Its final eh is stressed, but it is outside the simplex test.',
195:'Tube nāli/nālyeh is an i-derived form within the reed/channel complex. Do not transfer the unextended bamboo headword’s accent to it.',
201:'Cardamom elachi is a regional plant-name form; final i is replaced by ye with final stress, which is not simple addition of unstressed e.',
202:'Carrot gajar has suffix-stressed eh; regional lexical transmission is plausible, but plural behavior is directly observed regardless of etymology.',
207:'Vocabulary item827 prints khrméh, while grammar p42 prints khórméh with both root and suffix acute marks. Preserve this source-internal segment/accent difference.',
209:'Farmer zamin-dar is a transparently regional Persian-derived compound/title; the Dras plural assigns final suffix stress despite stem stress in the singular.',
212:'Fodder chhak/chhaké is unmarked in the monosyllabic SG and final-stressed in the plural. The SG omission does not establish a toneless or preaccenting class.',
213:'Garden ba:k/bakeh is a regional bāgh-shaped loan, with final devoicing and shortening before the accented plural suffix.',
214:'Garlic gokpa suggests a regional Himalayan contact form; uṣṇa is not a sufficient segmental match. Vowel replacement forms its final-stressed plural.',
219:'The combined hawk/plant gloss may conflate homonyms. Final plural accent is printed, but its lexical identity requires source clarification.',
224:'Maize makai is not securely inherited from markaka bird. The historical semantic/contact problem is retained; the nasal/adjacent-vowel spelling also prevents a simple nucleus count.',
225:'Mace ḍophos has final-stressed eh. The botanical sense must be distinguished from the club/weapon sense before proposing a compound etymology.',
227:'Mushroom śiṇṭili has an extended feminine ending; its plural yé carries stress after the i-to-y alternation. It is not a direct unextended śilīndhra citation reflex.',
230:'Pigeon-pea khukuṇé also retains a root acute. Preserve multiple accent marking; no single-stress rule can be tested without resolving it.',
232:'Pulley gʌ́ɽa:ri/gʌɽa:ré: shifts stress to the replacement final vowel. This differs from additive unstressed e.',
234:'Sickle oŋo/oŋe agrees with the aṅka-derived extended tool noun; root stress remains. The precise historical extension remains distinct from the simplex hook headword.',
237:'Water-wheel kopuh/kopue loses final h and introduces a vowel sequence. The acute stays on u; exact syllabicity must be checked before calling it penultimate.',
239:'Yoke na:l/nalé shortens the root and stresses final e. The semantic candidates yugá and upastambha do not establish a segmental origin; this remains a lexical inflectional residual.',
242:'Barber thakur is a regionally circulating title/occupation word within the ṭhakkura comparison. Its accented eh is an inflectional adaptation, not a direct old-accent reflex.',
243:'Brush buruš has acute on both the stem and eh. The likely regional/English loan route cannot itself explain whether the two marks represent two prosodic domains or inconsistent notation.',
244:'Hammer aṭho:ra/aṭho:reh retains the root acute and adds another on eh. The hastakūṭa-derived regional hammer family is plausible; contact and fossilized compound history remain open.',
246:'Touchstone pali/palyé loses the final i nucleus through glide formation and adds final stress. Vowel-replacement morphology is independently visible.',
248:'Vehicle ga:ri is a regional gaṛī form; the plural replaces final i with stressed long e through y. It is a contact/formation case rather than a simplex old-accent test.',
250:'Whip has nasalized vowel sequences plus leaked number markers; keep the form in the inventory but leave its nucleus interpretation unresolved.',
252:'Shame laś/laʒé has a voiced plural alternant and final stress, a clear residual against universal stress-preserving -e.',
255:'Blotting paper is a regional compound involving ink and sucking. Its plural preserves the final component’s stem stress; do not treat it as one inherited nominal root.',
260:'Line kiṣi/kiśyé can be compared with the independently listed kṛṣi furrow/line family. The final vowel becomes a glide and the new final e bears stress.',
261:'Nib nip/nibé is compatible with a recent regional/English loan and shows intervocalic voicing plus final-stressed e. Contact status is a lead, not a substitute for an inflection rule.',
263:'Boundary bana/bané has stress on the final vowel in both cells, which is vowel replacement rather than adding a new accented syllable.',
264:'Minister vazir is a regional Perso-Arabic title and preserves stem stress before e. This contrasts with similarly borrowed stems taking stressed eh.',
265:'Office daftar/daftari is unmarked; regional loan identity does not supply a missing accent.',
266:'Officer afsar/afsari is unmarked; do not infer stress from related regional pronunciations.',
268:'Friendship sati/satye has final-vowel replacement with glide formation and final plural stress.',
269:'Gunpowder śorah/śore has loss of final h and vowel replacement. Its regional nitrate/chemical-name history is distinct from a simple inherited noun.',
270:'Prisoner qaidi/qaidye involves a regional loan stem and vowel sequence. Final accent is present, but conservative syllabification remains unresolved.',
271:'Shield phalie has adjacent vowels; the khēṭa comparison is not sufficiently constrained here.',
273:'Debt u:ṣ/u:ʐe is unmarked and shows voicing. The generic debt comparators duḥkha and dhana are not accepted from meaning alone.',
274:'Debtor uṣ-yar is visibly related to the debt noun through a suffix. The plural eh bears final stress; the inherited source of the debt root remains open.',
276:'Message bo:t/bó:de has an unmarked monosyllabic SG and explicitly root-stressed PL with voicing. The SG omission is not evidence for accent shift.',
278:'Altar is represented by a descriptive phrase containing diś place, whereas the plural candidate is just diśe. These are not matched whole-word cells.',
279:'Ghost/giant yaṣ/yaṭṣe agrees with yakṣa, retaining/reintroducing the affricate in the plural; final long e bears stress. The extended plural differs from the bare old stem.',
280:'Hermitage chila/chile is a regional religious term with final vowel replacement; contact history is more plausible than an arbitrary ancient synonym.',
281:'Nun chomo/chome has the shape of a regional Tibetan religious title; final-vowel replacement preserves the final stress domain. Treat contact origin as a lead pending a primary lexicon.',
285:'Player dopa/dope has initial stress before a long final vowel in both cells. Final-vowel length does not automatically attract accent.',
}

def main():
    ps=tsv('dras-plural-candidates.tsv');assert len(ps)==287
    rows=load_records();byid={r['id']:r for r in rows};fs={r['family_id']:r for r in tsv('families.tsv')}
    reviews=[];links={};summary=[]
    for i,p in enumerate(ps):
        ids=json.loads(p['singular_ids'])+[p['plural_id']]
        p['review_index']=i;p['manual_lexical_note']=SPECIAL.get(i,'The matched source forms were inspected. The plural ending and its accent are retained as printed; no etymology is assigned from a shared English gloss alone.')
        p['reviewed_family_comparison']=LINKS.get(i,'')
        p['primary_check']='exact printed passage inspected' if i in [31,49,120,121,124,158,159,182,207,243,244] else 'database source citation and candidate lexemes inspected'
        if i in LINKS:
            fid=LINKS[i];assert fid in fs
            p['manual_lexical_note']+=' Research comparison: '+fs[fid]['headword']+' ('+fid+'), '+fs[fid]['gloss']+'. This links the root/lexeme, not each inflected cell directly to the old headword.'
            for rid in ids:
                r=byid[rid]
                if r['research_family_id']:continue
                if rid in links:assert links[rid]['family_id']==fid;continue
                links[rid]=dict(record_id=rid,family_id=fid,confidence='provisional' if i in [167] else 'reviewed-lexeme-comparison',relation='root-of-number-paradigm',basis=p['manual_lexical_note'],strict_exclusion='contact-route-unresolved' if i in [56,118,242,244] else '')
        p['morphological_assessment']=('Final eh/eɦ is an independently identified suffix; compare final versus retained stem marks without defining membership by acute placement.' if p['suffix']=='-eh/-eɦ' else 'Plain e/i must distinguish suffix addition, vowel replacement, glide formation, syncope and lexical stem alternants; the source marks are not normalized to the majority pattern.')
        reviews.append(p)
    write_tsv('dras-paradigm-review.tsv',reviews)
    (HERE/'paradigm_annotations_01.jsonl').write_text(''.join(json.dumps(dict(record_ids=json.loads(p['singular_ids'])+[p['plural_id']],source='Rajapurohit2012',status='manual-number-paradigm-review',review_index=p['review_index'],analysis=p['manual_lexical_note']+' '+p['morphological_assessment'],primary_check=p['primary_check']),ensure_ascii=False)+'\n' for p in reviews))
    # Export is intentionally one-shot unless this frozen link file already
    # exists: later research links must not change the reviewed input set.
    dest=HERE/'research_links_11.jsonl'
    if not dest.exists():dest.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in links.values()))
    for suffix in ['-eh/-eɦ','-e','-i','other']:
        rr=[r for r in reviews if r['suffix']==suffix]
        summary.append(dict(suffix=suffix,raw_plural_types=len(rr),outcomes=dict(Counter(r['plural_stress_from_right'] or r['plural_outcome'] for r in rr)),unit='Printed plural citation types; duplicate lexeme conflicts remain visible. These are morphological outcome counts, not independent ancestral etyma.'))
    write_tsv('dras-plural-summary.tsv',summary)
    print('manually reviewed candidates',len(reviews),'new root links',len(links));print(summary)
if __name__=='__main__':main()
