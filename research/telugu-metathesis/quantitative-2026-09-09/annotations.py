"""Manually reviewed etymon analyses, kept separate from automatic extraction.

The compact source is expanded into fully documented TSV/JSON appendices by analyse.py.
Outcome codes: D displacement-family development, R original order retained,
M both D and R formations/variants, A ambiguous, O other development, B likely loan.
D is deliberately not a claim that a literal vowel/consonant exchange rather than
assimilation+syncope has been independently demonstrated. Mechanism is recorded below.
Only explicitly listed languages are reviewed; missingness is computed from the corpus.
Each language tuple is (outcome, evidence forms separated by |, local explanation).
"""

CASES = []
TOKEN_OUTCOMES = {}
def tokens(entry, language, **groups):
    """Explicit per-form outcomes where a family-language cell is mixed/uncertain."""
    for code, words in groups.items():
        for word in words.split('|'):
            key=(entry,language,word)
            assert key not in TOKEN_OUTCOMES,key
            TOKEN_OUTCOMES[key]=code
def add(id, concept, reconstruction, c1, v1, c2, v2, structure, pos,
        support, direction, history, issues, outcomes, *,
        confidence='medium', references='DEDR', eligibility='core',
        family=None, quantity='short', c2_structure='singleton',
        boundary='plausible formative boundary; not independently dated',
        input_confidence='medium', mechanism='Target initial-order comparison; literal exchange, assimilation and syncope distinguished in the derivation and language notes'):
    CASES.append(dict(
        entry_id=id, family_id=family or id, concept=concept,
        reconstruction=reconstruction, c1=c1, v1=v1, v1_quantity=quantity,
        c2=c2, c2_structure=c2_structure, v2=v2, structure=structure,
        grammatical_category=pos, boundary_evidence=boundary,
        input_support=support, input_confidence=input_confidence,
        direction_argument=direction, derivation=history,
        exception_notes=issues, confidence=confidence, references=references,
        eligibility=eligibility, mechanism=mechanism, outcomes=outcomes,
        review_status='reviewed', review_date='2026-09-09'))

add('d63','hide, subdue, be compressed','*aṭ-a-nk- / *aṭ-a-nkk-',
    'Ø','a','ṭ','a','VC-a-NP / VC-a-NPP','verb',
    'Tamil aṭaŋku/aṭakku, Kannada aḍaŋgu/aḍaku and Telugu aḍãgu/aḍacu independently support the uncontracted low-vowel formative. K03 p.107 reconstructs these derivatives at Proto-South Dravidian level; PDr labels in CLDF are not precise historical levels.',
    'The shared vowel-initial aṭ/aḍ order in SD I and aṛ- in Kurux–Malto, including the same stop/nasal formative contrasts, favors older *aṭ-aŋ- over an initial *ḍā- followed by multiple independent vowel insertions.',
    '*aṭ-aŋ- > *aḍ-aŋ- > *ḍāŋ- > Telugu ḍā̃gu/dā̃gu; independently *aṭ-aŋkk- > *ḍāŋc- > ḍā̃cu/dā̃cu. Literal *ḍaaŋ- contraction and assimilation/stress-induced V1 loss are competing implementations; the Telugu nasal-loss and initial ḍ>d are subsequent developments.',
    'Telugu retains aḍagu/aḍãgu “submit” and aḍacu “suppress” beside displaced “hide” forms: a real within-family semantic/formation split, not proof of a phonological exceptionless class. Kui also retains āṛpa/āṭpa. Kolami and Naikri are diagnosed as early Telugu loans by K03 p.107; aspiration in Naikri needs a recipient history. Tulu aḍeŋgɯ : ḍeŋgɯ/deŋguni is compatible with local aphaeresis, not independently the Telugu contraction. d80 shares compressed/piled semantics and homophonous Toda/Kannada evidence; sensitivity analysis should collapse d63+d80 without asserting that DEDR erred.',
    {
      'Telugu':('M','aḍagu|aḍãgu|aḍacu|ḍāgu|ḍā̃gu|dā̃gu|ḍācu|dā̃cu','Semantic specialization accompanies divergent reflexes; both orders are attested.'),
      'Tamil':('R','aṭaŋku|aṭakku','Both root and formative vowels remain.'),
      'Malayalam':('R','aṭaŋŋuka|aṭakkuka','Same order and formative distinction.'),
      'Kannada':('A','aḍaŋgu|aḍagu|aḍaku|tāguḍi','Unchanged derivatives and an initial tā- ambush noun; independent status of tāguḍi unresolved, so do not count it as an independent inherited displacement.'),
      'Kodagu':('R','aḍak- (aḍaki-)','Retains initial vowel and apical order.'),
      'Kota':('R','aṛg- (aṛgy-)|aṛk- (aṛky-)','Medial vowel deletion yields aṛ-C; no initial displacement.'),
      'Toda':('R','oḍg- (oḍgy-)|oṛk- (oṛky-)','Vowel change and syncope preserve V–apical order.'),
      'Tulu':('A','aḍeŋgɯ|ḍeŋgɯ|deŋguni','Local aphaeresis retains the attested second vowel e; insufficient evidence for the same contraction as Telugu.'),
      'Konda':('D','ḍāŋ- (-it-)|ḍāp','Vowel-initial apical promoted; low long vowel. Derivational consonants differ by transitivity.'),
      'Kui':('M','āṛpa (āṛt-)|āṭpa (āṭt-)|ḍāpa (ḍāt-)','Retained and displaced related formations; length in retained root requires separate quantity history.'),
      'Kolami':('B','ḍāŋg- (ḍāŋkt-)|ḍāp- (ḍāpt-)','K03 early Telugu loan diagnosis; do not count as independent innovation.'),
      'Naikri':('B','ḍʰāŋ|ḍʰāp','K03 early Telugu loan diagnosis; aspiration is separate.'),
      'Kurux':('R','aṛknā','Order retained with suffix-vowel syncope.'),
      'Malto':('R','aṛge|aṛke','Order retained with suffix-vowel syncope.'),
      'Badaga':('R','adangu|adaku','Imported records marked uncertain; corroborative order only.')
    }, confidence='high',references='K03 pp.107,162; PSS83 pp.229,233; K61 pp.51–54; DEDR 63',
    boundary='Nasal intransitive versus stronger transitive formations recur independently in Tamil, Kannada, Telugu and the reconstruction.', input_confidence='high')

add('d72','foot, base','*aṭ-V; regional *aṭ-Vk-',
    'Ø','a','ṭ','unknown','VC-V(k)','noun',
    'Tamil aṭi, Kannada aḍi and Telugu aḍugu support *aṭ- and different vowel/consonant formatives. K03-derived CLDF reconstructions explicitly leave V unspecified.',
    'Initial vowel preceding the apical occurs in SD I and Gondi–Konda, supporting V–C order without using Telugu as the sole conservative witness.',
    '*aṭ-Vk- > *aḍ-Vg- > Telugu aḍugu; Konda aḍgi shows medial-vowel loss without movement. Tamil/Kannada *aṭ-i gives aṭi/aḍi; they are not the identical -Vk derivative.',
    'The independent suffix-vowel quality is not securely recovered: do not use Telugu u alone to prove a historical high-vowel class. Gadaba aḍugu is explicitly marked a Telugu loan. The Indo-Aryan heel forms attached to this family are contact comparisons, not votes for a Dravidian proto-vowel.',
    {'Telugu':('R','aḍugu|aḍime','Relevant derivatives preserve vowel-first order.'),
     'Tamil':('R','aṭi|aṭimai','Short-vowel base and derived noun retain order.'),
     'Malayalam':('R','aṭi|aṭima','Same order.'),
     'Kannada':('R','aḍi|aḍime','Same order.'),
     'Tulu':('R','aḍi','Same order.'),
     'Kodagu':('R','aḍi','Same order.'),
     'Kota':('R','aṛy','Postvocalic apical with later glide.'),
     'Toda':('R','oṛy','Root-vowel change; no apical displacement.'),
     'Gondi':('R','aḍi|aṛgi|aḍita','Several dialects preserve initial V; geminate variant is separate strengthening.'),
     'Konda':('R','aḍgi','Syncope produces medial cluster; no metathesis.'),
     'Gadaba':('B','aḍugu','Source explicitly says from Telugu.'),
     'Badaga':('R','adi-','Order retained; uncertainty tag belongs to the source/import.')},
    references='DEDR 72; K03 reconstruction records in Jambu',
    boundary='*-Vk expansion contrasts regionally with bare *aṭ-V; independent of metathesis outcome.')

add('d77','pound, beat','*aṭ-V-; *aṭ-aŋ- / *aṭ-Vmp- derivatives',
    'Ø','a','ṭ','unknown','VC-V-NP and other formations','verb',
    'Tamil aṭu/aṭi/aṭar and Kannada aḍi/aḍar establish short a and postvocalic retroflex; Telugu aḍucu and aḍupu retain that ordering. Kui ḍāmba and Kuvi ḍamb- support a labial nasal formative but do not independently establish Telugu *-aŋ-.',
    'Independent SD I vowel-initial forms plus Parji/Gadaba aṭ(t)- support earlier V–ṭ; deriving them all by vowel insertion before Proto-*ḍa- is poorly motivated.',
    'Possible *aṭ-aŋ- > *aḍ-aŋ- > *ḍāŋ- > ḍaŋgu > daŋgu, with shortening before NP; alternatively a consonantal formative produces short vowel directly. Transitive ḍancu/dancu and dampu have distinct extensions. Konda ḍaŋ-/ḍak-/ḍas- shows related displaced stems; exact shared suffixes require reconstruction.',
    'Kui ā in ḍāmba supports investigating an early long vowel but is not an attested intermediate of Telugu ŋg. The Telugu non-displaced beat/fight forms must not be dropped. Tulu darpuni could reflect *aḍar- with aphaeresis, but the local vowel/stop history does not uniquely identify a literal swap. Kota ayṛ-/aṛc- is a distinct glide alternation.',
    {'Telugu':('M','aḍupu|aḍucu|aḍaru|ḍaŋgu|daŋgu|ḍancu|dancu|dampu','Displacement restricted among related beat/pound formations; no output-independent suffix law yet established.'),
     'Tamil':('R','aṭu|aṭi|aṭar','Retained root ordering in multiple derivatives.'),
     'Malayalam':('R','aṭi|aṭikka|aṭar','Order retained.'),
     'Kannada':('R','aḍi|aḍar|aḍacu','Order retained; aṇe is an additional consonant development.'),
     'Kodagu':('R','aḍi- (aḍip-, aḍic-)','Order retained.'),
     'Kota':('R','ayṛ- (aṛc-)','Apical remains after vowel; glide position needs separate Kota analysis.'),
     'Tulu':('A','darpuni|aḍikai|aṇepuni','Initial loss/reordering in dar-; derivation and cognacy of individual extensions unresolved.'),
     'Konda':('M','aṭ- (-t-)|ḍaŋ- (-it-)|ḍak- (-t-)|ḍas- (-t-)','Non-displaced hit root alongside displaced pound/beat derivatives.'),
     'Kui':('D','ḍāmba (ḍāmbi-)','Displaced long-vowel labial formation.'),
     'Kuwi':('D','ḍamb- (-it-)|ḍap- (-h-)','Displaced labial derivatives, including Sunkarametta.'),
     'Parji':('R','aṭṭ','Order retained; geminate strengthened formation.'),
     'Gadaba':('R','aṭ|aṭṭ','Ollari and Salur source labels preserved in corpus.')},
    references='K61 pp.53–54; PSS83 comparison of pound; DEDR 77')

add('d78','be fit, be able','*aṭ-u-; Telugu *aṭ-ar- formation',
    'Ø','a','ṭ','unknown','VC-V / VC-VC','verb',
    'Tamil aṭu, Malayalam aṭukka, Kannada aḍavu, Konda aṭ-, Pengo/Manda aḍ- support vowel-initial root. Telugu aḍaru has a different extension from the bare ability root.',
    'Vowel-first root occurs in SD I, SD II and Malto, so the comparison supplies a broadly supported retained order.',
    '*aṭ-V- > aḍ-/aṭ- in daughter languages; Telugu *aḍ-ar- > aḍaru. Kui/Kuvi āḍ- lengthens while retaining V–C; this is not metathesis.',
    'A short-versus-long ability root alternation exists in Kuvi dialect/source records. Its quantity cannot be labeled concealed displacement because the apical remains postvocalic. Exact reconstruction of Telugu -ar- and whether it is productive morphology remain open.',
    {'Telugu':('R','aḍaru','No displacement in the attested derivative.'),
     'Tamil':('R','aṭu|aṭaivu','Order retained.'),'Malayalam':('R','aṭukka|aṭavu','Order retained.'),
     'Kannada':('R','aḍagu|aḍavu','Order retained; Havyaka eḍi has independent vowel history.'),
     'Konda':('R','aṭ- (-t-)','Bare stem retains order.'),
     'Kui':('R','āḍa (āḍi-)','Lengthening without displacement.'),
     'Kuwi':('R','aḍ- (-it-)|āḍ- (-it-)|āḍ|aṙdali','Quantity and consonant variants; original V–apical order retained.'),
     'Pengo':('R','aḍ- (aṛt-)','Order retained.'),'Manda':('R','aḍ','Order retained.'),
     'Malto':('R','aṭye','Order retained.')},references='DEDR 78',
    eligibility='core-formation-uncertain',boundary='Derivative status of Telugu -ar- plausible from cross-language comparison; bare ability stems do not independently test the formative-conditioned rule.')

add('d79','approach, join, near','*aṭ-ay-; *aṭ-ar- and *aṭ-Vk- extensions',
    'Ø','a','ṭ','a','VC-ay / other derivatives','verb/noun',
    'Tamil aṭai and Kannada aḍe support *aṭ-ay- independently; Tamil/Kannada aṭu/aḍar and aḍapu show distinct extensions. Long and short Telugu outcomes cannot all be assigned one suffix.',
    'SD I aṭ/aḍ-initial bases and Malto aṭg- preserve V–apical ordering; Telugu ḍā- and Kui ṛā- are innovations under the cognacy hypothesis.',
    '*aṭ-ay- > *aḍ-ay- > *ḍāy- > Telugu ḍāyu/dāyu; *aṭ-Vk- may yield *ḍak(k)- > ḍaggaṟa/daggaṟa, but the exact suffix and strengthening history are unresolved. Kui *aḍ-a-NC > ṛānja requires local ṭ/ṛ correspondence and is a separate derivation.',
    'Telugu aḍaru “arise” retains order; a derived -k- nearness noun differs from the -ay- approach verb. Kuvi dagira/daggire/ḍagre resembles the Telugu extended nearness word and may be a loan; independently proving that donor history is necessary before counting an inherited Kuvi innovation. Kui retains aḍa/aṭpa beside ṛānja etc. No semantic label is used as an automatic phonological condition.',
    {'Telugu':('M','ḍāyu|dāyu|ḍāpu|dāpu|ḍaggaṟa|daggaṟa|aḍaru','Long approach/near forms, short geminate extension and retained arise derivative.'),
     'Tamil':('R','aṭai|aṭu|aṭaicu','Original order retained.'),
     'Malayalam':('R','aṭayuka|aṭukka|aṭuppu','Original order retained.'),
     'Kannada':('R','aḍe|aḍar|aḍasu','Original order retained.'),
     'Kota':('R','aṛ- (aṭ-)','Root order retained, tense allomorphy separate.'),
     'Toda':('R','aṛpɨn','Dowry formation retains root vowel first.'),
     'Kodagu':('R','aḍɨ- (aḍɨp-, aḍɨt-)','Order retained.'),
     'Tulu':('R','aḍevuni|aḍepuni|aḍavu','Order retained.'),
     'Kui':('M','aḍa (aḍi-)|aṭpa (aṭt-)|ṛānja (ṛānji-)|ṛāspa (ṛāspi-)','Displaced marriage derivatives coexist with retained join derivatives.'),
     'Kuwi':('A','dagira|daggire|ḍagre','Displaced-looking extended near word; likely contact candidate, donor not established.'),
     'Malto':('R','aṭge|aṭgi','Postvocalic apical retained.'),
     'Badaga':('R','adasu|aduve','Order retained; import marks these uncertain.'),
     'markodi':('R','adut','Attested near form; limited lexical evidence.')},
    references='K61 vowel-initial cases pp.51–57; DEDR 79',input_confidence='high',
    boundary='The -ay- formation is supported by Tamil aṭai and Kannada aḍe; additional -ar/-Vk formations kept separate.')

add('d80','pile, arrange in tiers','*aṭ-uk(k)- / *aṭ-aŋk-',
    'Ø','a','ṭ','u','VC-u-PP','verb/noun',
    'Tamil aṭukku, Malayalam aṭukkuka, Telugu aḍuku independently support high u in a pile formation; Kannada aḍuku/aḍaku and Kodagu aḍak-/aḍaŋg- show vowel and transitivity variants.',
    'All attested branches keep the root vowel before the apical. The medial cluster in Nilgiri forms is a syncope outcome, not initial apical movement.',
    '*aṭ-ukk- > Tamil aṭukku; *aḍ-uk- > Telugu aḍuku; *aḍ-Vk- > Kota aṛk-/Toda oṛk-. No displacement is required for any reviewed reflex.',
    'This is a retained high-formative counterpart to displaced high-formative cases elsewhere: vowel height alone does not decide application. The etymon overlaps d63 in Toda oṛk- “subdue, pile” and Kannada packing vocabulary. Report both strict DEDR counts and a conservative collapse with d63; do not count the same Toda token twice as independent root evidence.',
    {'Telugu':('R','aḍuku','High-vowel derivative retains V–apical order.'),
     'Tamil':('R','aṭukku|aṭukkam','Original order retained.'),
     'Malayalam':('R','aṭukkuka|aṭukku','Original order retained.'),
     'Kannada':('R','aḍuku|aḍaku','Both medial vowels preserve order.'),
     'Kodagu':('R','aḍak- (aḍaki-)|aḍaŋg- (aḍaŋgi-)','Related transitive/intransitive stems retain order.'),
     'Kota':('R','aṛk- (aṛky-)|aṛg- (aṛgy-)','Medial-vowel syncope only.'),
     'Toda':('R','oṛk- (oṛky-)|oḍg- (oḍgy-)','Medial-vowel syncope and vowel quality change only.'),
     'Badaga':('R','adaku|adangu|aḍduku','Order retained with geminate and transitivity variants.')},
    references='DEDR 80; compare DEDR 63',boundary='-uk(k) formation corroborated across Tamil/Malayalam/Telugu; root singleton is before the formative vowel.',input_confidence='high')

add('d81','ask, beg','*aṭ-uk-?; wider root *aṭ-/aḷ- uncertain',
    'Ø','a','ṭ','u','VC-u-C','verb',
    'Telugu aḍugu and Parji aḍ-/aḍi support older vowel–apical order; Tamil aḷavu has a lateral and Tulu naṭṭu adds n and gemination. The precise PDr reconstruction is less secure than its starred CLDF display suggests.',
    'Vowel-first Telugu and Parji agree, while Kui jāpa is analyzed in DEDR as an innovative reflex with a special ṭ : j correspondence. The disparate Tamil/Tulu roots prevent simply assuming all strings are regular descendants of one fully specified stem.',
    'Telugu *aḍ-ug- > aḍugu retains order. Under DEDR cognacy, Kui *aṭ-a-p- > *ṭāp- > jāp- is a possible displacement derivation, requiring a low formative distinct from Telugu u and independent support for ṭ>j.',
    'DEDR cites Burrow and Bhattacharya, IIJ 5:122 for ṭ : Kui j; that primary argument has not yet been obtained. The Kui history remains tentative, not a secure success in a quantitative sound-law test. Tamil lateral and Tulu n require either separate changes, morphological analysis, or revised cognacy.',
    {'Telugu':('R','aḍugu','Order retained; u is securely attested, reconstruction of identical derivative across branches is not.'),
     'Parji':('R','aḍ|aḍi','Order retained in a shorter related stem.'),
     'Tamil':('A','aḷavu','Meaning compatible; ṭ : ḷ needs an independent account.'),
     'Tulu':('A','naṭṭuni|naṭṭu|naṭṭā','Initial n and gemination unresolved; not counted as displacement.'),
     'Kui':('A','jāpa (jāt-)','Published displacement comparison with exceptional consonant correspondence; insufficient primary verification.')},
    references='DEDR 81, citing Burrow and Bhattacharya IIJ 5:122; Starostin via Merriam record 86',
    confidence='low',input_confidence='low',eligibility='cognacy-or-input-uncertain')

add('d86','anvil, support','*aṭ-ay(-kal)',
    'Ø','a','ṭ','a','VC-ay + noun compound','noun',
    'Tamil aṭai “support” and aṭai-kal “anvil”, Malayalam aṭa-kkallu and Kannada aḍe-gal/aḍa-gallu establish the support-stone compound independently of Telugu.',
    'Vowel-first support nouns in three southern languages and Kota aṛ gal favor original *aṭay; Telugu initial ḍā is an innovation in the first compound member.',
    '*aṭ-ay-kal > *aḍ-ay-kal > *ḍāy-kal > ḍā-kallu / ḍā-kali > dākali; dāyi can reflect the uncompounded first member. Intermediate y loss and changes of the stone component are separate from displacement.',
    'This compound shows that a morphological boundary after the eligible first member need not block displacement. It does not license moving arbitrary consonants across a compound boundary. The detailed kali/gali/kallu variation needs suffix/compound history; it is not a free phonological substitution. No independent SCDr non-Telugu attestation is in this set.',
    {'Telugu':('D','ḍā-kallu|ḍā-kali|dākali|dāyi|dā-gali','Initial member displaced and lengthened; dental merger and compound alternation later.'),
     'Tamil':('R','aṭai|aṭai-kal','Support base and compound retain order.'),
     'Malayalam':('R','aṭa-kkallu','Compound retains order.'),
     'Kannada':('R','aḍegal|aḍagallu|aḍe','Compound and free base retain order.'),
     'Kota':('R','aṛ gal','Syncope in first member; apical still follows vowel.'),
     'Tulu':('R','aṭṭɛ','Support word has strengthened medial consonant; not identical compound.')},
    references='DEDR 86; K61 vowel-initial displacement pp.51–57',
    boundary='Support + stone composition independently visible in Tamil, Malayalam, Kannada and Telugu.',input_confidence='high')

tokens('d63','Telugu',R='aḍagu|aḍãgu|aḍacu',D='ḍāgu|ḍā̃gu|dā̃gu|ḍācu|dā̃cu')
tokens('d63','Kannada',R='aḍaŋgu|aḍagu|aḍaku',A='tāguḍi')
tokens('d63','Tulu',R='aḍeŋgɯ',O='ḍeŋgɯ|deŋguni')
tokens('d63','Kui',R='āṛpa (āṛt-)|āṭpa (āṭt-)',D='ḍāpa (ḍāt-)')
tokens('d77','Telugu',R='aḍupu|aḍucu|aḍaru',D='ḍaŋgu|daŋgu|ḍancu|dancu|dampu')
tokens('d77','Tulu',A='darpuni',R='aḍikai|aṇepuni')
tokens('d77','Konda',R='aṭ- (-t-)',D='ḍaŋ- (-it-)|ḍak- (-t-)|ḍas- (-t-)')
tokens('d79','Telugu',R='aḍaru',D='ḍāyu|dāyu|ḍāpu|dāpu|ḍaggaṟa|daggaṟa')
tokens('d79','Kui',R='aḍa (aḍi-)|aṭpa (aṭt-)',D='ṛānja (ṛānji-)|ṛāspa (ṛāspi-)')

add('d202','pipal tree','*ar-a- (extensions *-c, *-ḷ, *-y and Telugu -v/-g)',
    'Ø','a','r','a','VC-a-C','noun',
    'Tamil aracu/arai, Malayalam aracu/arayāl and Kannada arase/araḷi support initial ar-a- and several lexical extensions. K03 p.10 lists *ar-ac/-aḷ; those are not literal ancestors of Telugu rāvi.',
    'Several SD I languages retain ar- and show internal suffix variation. The parsimonious directional comparison is ar-a- > rā-, but it does not independently reconstruct the final Telugu consonant.',
    '*ar-a-... > *rā-... > rāvi/rāgi, with the -v/-g material unexplained by displacement itself. A specific *ar-avi or *ar-agi intermediate would be a fitted reconstruction and is not asserted.',
    'Kannada rāvi is explicitly borrowed from Telugu. Kolami ra·vi and Konda rāyi maran could reflect contact with Telugu tree terminology; no independent chronology establishes separate innovations. Tamil arai already has a reduced extension, so later truncation is possible but does not explain all v/g/y correspondences.',
    {'Telugu':('D','rāvi|rāgi','Displaced/contracted initial portion; final consonant derivation unresolved.'),
     'Tamil':('R','aracu|arai','Old Tolkāppiyam arai retained; botanic identification itself marked probable in source.'),
     'Malayalam':('R','aracu|arayāl','Different extensions, retained ordering.'),
     'Kannada':('R','arase|araḷi|rāvi','Native vowel-first derivatives plus explicit Telugu loan rāvi.'),
     'Kodagu':('R','araḷi-mara','Vowel-first first compound member.'),
     'Konda':('A','rāyi maran','Possible Telugu loan; no inherited innovation counted.'),
     'Kolami':('A','ra·vi','Possible Telugu loan; middle dot is retained source quantity notation.')},
    references='K03 p.10; DEDR 202',input_confidence='high')
tokens('d202','Kannada',R='arase|araḷi',B='rāvi')

add('d221','rare, difficult','*ar-u(-t)- / *ar-i(-t)-',
    'Ø','a','r','u/i','VC-high-C','adjective/noun',
    'Tamil aru/ariya, Malayalam arutu/ariya and Kannada arudu/aridu independently support a short ar- base with high-vowel extensions. Telugu arudu/aridi preserves both qualities.',
    'All reviewed languages place a before r; there is no evidence for earlier initial r followed by inserted a.',
    '*ar-u-tu > arudu in Telugu/Kannada, beside *ar-i- formations; Kota arg-/Toda arx- show ordinary loss of a medial high vowel. No displacement is required.',
    'The bare root may be free, but the -t- nominal/adjectival formation is independently comparable and supplies a retained formative-bearing control. Tamil long āri etc. are root-quantity variants, not inferred metathesis stages. Kota “cry out in pain” appears as a separate lexicographic sense and is not used to reconstruct this family.',
    {'Telugu':('R','arudu|aridi','Both high-vowel formations retain order.'),
     'Tamil':('R','aru (arum, ār)|ariya|aruku','Short root and extensions retain order.'),
     'Malayalam':('R','arutu|ariya|arukuka','Direct suffix and quality comparisons.'),
     'Kannada':('R','arudu|aridu|aradu','Additional a variant does not reverse order.'),
     'Tulu':('R','arkuni','Syncope creates internal rk, not initial r.'),
     'Kota':('R','arg- (argy-)|ark- (arky-)','Medial high-vowel loss.'),
     'Toda':('R','arx- (arxy-)|ark- (arky-)','Medial high-vowel loss and local consonant development.')},
    references='DEDR 221',boundary='Adjectival *-t- corroborated in Malayalam arutu and Telugu/Kannada arudu; not inferred from desired outcome.',input_confidence='high')

add('d228','rub, grind, smear','*ar-ay-; additional *ar-a-C formations',
    'Ø','a','r','a','VC-ay / VC-a-C','verb/noun',
    'Tamil arai, Malayalam arayuka and Kannada are/arayisu establish the ar-ay type independently. Telugu ṟ/r doublets need historical rhotic checking; their existence does not overturn the cross-language V–rhotic ordering.',
    'The wide SD I ar- comparison and Gondi aṛs make vowel-first order preferable; Telugu rā- and several SCDr r-initial formations are innovative. The initial vowel cannot be restored merely from a hypothesized ban on initial r.',
    '*ar-ay- > *rāy- > Telugu rāyu; strengthened/transitive derivatives give rācu/ṟācu and rāpu/ṟāpu. Different rē-/re- formations in Konda, Kui and Pengo require a vowel or suffix history beyond simple a+a contraction. Kui rāk-p- > rāpka illustrates separate stop metathesis after the initial displacement.',
    'Telugu fragment nouns aravuḍu/aṟavaṟalu preserve order; ragulu/ravulu “kindle” have short a and semantic drift, so no unique long-to-short derivation is assumed. Kuvi mlekʰ\'nai lacks a convincing segmental path from ar- and remains a questionable member. Gondi Koya rāy may be influenced by Telugu; Kolami rāk is a loan candidate. Malayalam rākuka beside irāvuka could arise by local aphaeresis plus v/k derivational variation. Neither southern nor central initial r automatically demonstrates shared inheritance.',
    {'Telugu':('M','rāyu|rācu|ṟācu|rāpu|ṟāpu|aravuḍu|aṟavaṟalu|ragulu|ravulu','Related formations preserve both orders; short fire verbs need separate derivation.'),
     'Tamil':('R','arai|arāvu|aruvu','Several suffixes and quantity variants retain initial ar-.'),
     'Malayalam':('A','arayuka|arakkuka|irāvuka|rākuka','Retained basic forms; initial r in file verb compatible with independent aphaeresis.'),
     'Kannada':('R','are (arad-)|arayisu|araccu','Retained ordering; transitive morphology explicit.'),
     'Kodagu':('R','ara- (arap-, arat-)','Retained ordering.'),
     'Tulu':('R','arevuni|arepuni|araḍuni','Retained ordering.'),
     'Kota':('R','arv- (art-)|arm ( art-)','Internal syncope.'),
     'Toda':('R','arθ-','Internal syncope; DEDR Q is a transcription issue, not a new phoneme.'),
     'Gondi':('A','aṛs|rāy','Maria retains vowel; Koya rāy has possible Telugu contact.'),
     'Konda':('D','rās- (-t-)|rēs- (-t-)','Initial displacement good; e/a derivational alternation unresolved.'),
     'Kui':('D','rāga (rāgi-)|rēsa (rēsi-)|rāpka','Displaced forms with multiple vowel/stop formations; stop cluster reversal separately identified.'),
     'Kuwi':('A','rāc|rāk|mlekʰ\'nai','rā- forms support displacement; mlekʰ- cannot yet be assigned the same root.'),
     'Pengo':('D','rec- (-c-)','Innovative initial rhotic; exact e history unresolved.'),
     'Kolami':('A','rāk','Possible regional loan, not a demonstrated independent change.'),
     'Badaga':('R','are','Retained ordering.'),
     'Irula':('A','re- (ret-)','Initial loss and contraction plausible; no independent common SCDr chronology.')},
    references='DEDR 228; PSS83 pp.246–248 on independent southern aphaeresis',input_confidence='high')
tokens('d228','Telugu',D='rāyu|rācu|ṟācu|rāpu|ṟāpu',R='aravuḍu|aṟavaṟalu',A='ragulu|ravulu')
tokens('d228','Malayalam',R='arayuka|arakkuka|irāvuka',A='rākuka')
tokens('d228','Gondi',R='aṛs',A='rāy')
tokens('d228','Kuwi',D='rāc|rāk',A="mlekʰ'nai")

add('d229','half','*ar-ay',
    'Ø','a','r','a','VC-ay; free nominal base','noun/adjective',
    'Tamil arai, Kannada are, Telugu ara/aṟa and Naiki ar establish V–r ordering and the ay/a/e regional vowel correspondences.',
    'The same ordering is widespread within SD I and retained in Telugu and Naiki. Nothing requires either a prior displacement or reinsertion.',
    '*aray > Tamil arai, Kannada/Tulu are, Malayalam/Telugu ara; Kota/Toda/Naiki ar lose the final vowel. These changes do not relocate the rhotic.',
    'This is a useful contrast to *ar-ay “grind”, but historical identity of the formative -ay is not proven: half may be a lexical free base, whereas grind enters verbal derivation. The distinction cannot be manufactured after noticing opposite outcomes. Telugu ṟ/r is recorded but its chronology remains unestablished.',
    {'Telugu':('R','ara|aṟa','Both rhotic spellings retain original order.'),'Tamil':('R','arai','Retained free nominal.'),
     'Malayalam':('R','ara','Retained nominal.'),'Kannada':('R','are|ara|arake','Retained base and derived quantity noun.'),
     'Tulu':('R','are|areke','Retained base and extension.'),'Kota':('R','ar','Apocope, not displacement.'),
     'Toda':('R','ar','Apocope, not displacement.'),'Naiki':('R','ar','Apocope, not displacement.'),
     'Badaga':('R','are','Retained base.')},references='DEDR 229',
    eligibility='free-base-control',boundary='The historical separability of -ay is unproved; retain as a root-shape control instead of forcing the core classification.',input_confidence='high')

add('d233','fall, drop','*ar-; Telugu *ar-al-? and regional high-vowel derivatives',
    'Ø','a','r','unknown','VC-VC / VC-V','verb',
    'Gondi ar, Konda ar/arap and Pengo ar- support the vowel-first root. The -al required by Telugu rālu is not independently preserved in this current DEDR set; K61 p.56 compares Tamil aṟ-al, outside the present grouping.',
    'Regional ar- stems independently favor earlier V–r order. Telugu rāl- has an added lateral formation; the Koya rāl loan cannot be counted as independent support for its antiquity.',
    'If the older -al comparison is accepted, *ar-al- > *rāl- > Telugu rālu, with causative rāl-p-/rāl-c-. Pengo ar- : rat- suggests displacement in a derived causative. Kuvi rī- and Manda re- cannot be predicted from *ar-al; their formations and vowel histories remain separate.',
    'Gondi rāl is explicitly labeled from Telugu. Kolami/Naikri rāl- forms are probable contact comparanda but have not been independently dated. K61 source comparison must be checked before *ar-al is treated as a secure low-vowel input. A shared abstract “fall” meaning does not make every derivative identical.',
    {'Telugu':('D','rālu|rālpu|rālcu','Root ordering supports displacement; exact low formative is conditional.'),
     'Gondi':('R','ar|rāl','Inherited ar retained; Koya rāl explicitly borrowed.'),
     'Konda':('R','ar|arap','Retained base and causative.'),
     'Kuwi':('A','rī|rīali', 'Initial r innovation plausible; i versus a and derivative identity unresolved.'),
     'Pengo':('M','ar- (-t-)|rat- (-t-)','Retained intransitive versus displaced-looking causative; suffix identity needs analysis.'),
     'Manda':('A','re- (-t-)|ret','Initial r plausible, but e and formation history unresolved.'),
     'Kolami':('A','rāl- (rāṭ-)|rāp','Probable contact series; not counted as independent displacement.'),
     'Naikri':('A','rāl- (rāṭ-)|rālp','Probable contact series; not counted as independent displacement.')},
    references='K61 p.56; PSS83 p.233; DEDR 233',eligibility='core-formation-uncertain',
    boundary='-al in Telugu is recoverable conditionally from the older Tamil comparison, not independently from current DEDR descendants.')
tokens('d233','Gondi',R='ar',B='rāl')
tokens('d233','Pengo',R='ar- (-t-)',D='rat- (-t-)')

add('d236','suffer, tire','*al-a- and *al-a-NC- formations',
    'Ø','a','l','a','VC-a-(NC)','verb/noun',
    'Tamil alai/alaŋku, Malayalam alayuka/alaŋŋuka, Telugu alayu/alãgu independently supply short al-a- and extended stems. The CLDF negative *al “be not” is not evidence for this lexical family.',
    'SD I, Telugu, Kolami and Parji agree on initial al-; r/l-initial variants need their own histories rather than a uniform reconstructed initial liquid.',
    'Retained *al-a-y > Telugu alayu and *al-aŋ- > alãgu. Telugu lampaṭa and Kannada lampaṭe admit initial-vowel loss or contact-related restructuring; their exact earlier compound is unknown. Kui laha may reflect loss/reordering from al-a-, but short a and h are not fully explained.',
    'DEDR explicitly separates Sanskrit-derived Telugu lampaṭũḍu from the trouble noun and tentatively proposes Dravidian > Sanskrit borrowing for lampaṭa. This can involve export and reborrowing, not a simple one-way loan label. Kurux layā- vs algā requires separate suffix and vowel analysis. A bogus Malto alaŋku row is actually the opening of DEDR editorial prose about Tamil; only Malto alesi is lexical evidence. DEDR warns that d236 “suffer” and d240 “move” have converged semantically; separate roots remain the primary partition, with a collapsed sensitivity analysis.',
    {'Telugu':('A','alayu|alãgu|alapu|lampaṭa|lampaṭũḍu','Clear retentions plus unresolved initial-liquid trouble noun and explicit Sanskrit loan.'),
     'Tamil':('R','alai|alaŋku|alacu','Retained derived stems.'),'Malayalam':('R','alayuka|alaŋŋuka|alasuka','Retained derived stems.'),
     'Kannada':('A','alasu|alapaṭe|lampaṭe','Retained roots and unresolved initial-liquid extension.'),
     'Kodagu':('R','ala- (alap-, aland-)|alas- (alasi-)','Retained roots with semantic specialization.'),
     'Tulu':('R','alevuni|albe','Retention and internal syncope.'),'Kota':('R','alv- (ald-)','Retention with internal syncope.'),
     'Kui':('A','alāṛi|laha','Retained long-medial-vowel formation and uncertain short initial-liquid form.'),
     'Kolami':('R','alay- (alayt-)|alp- (alapt-)','Root order retained across transitivity.'),
     'Parji':('R','alac','Root order retained.'),'Kurux':('A','algā|layākoyā|laikoyornā','Initial loss candidate; precise morphological correspondence unresolved.'),
     'Malto':('R','alesi','Lexical sweat/heat form; discard editorial-prose artefact alaŋku as an attestation.'),
     'Badaga':('R','ale|alasu','Retained roots; imported source uncertainty preserved.')},
    references='DEDR 236 and preserved editorial comparison; PSS83 pp.246–248',
    boundary='-ay and nasal extensions are independently attested; lampaṭa segmentation remains unresolved.')
tokens('d236','Telugu',R='alayu|alãgu|alapu',A='lampaṭa',B='lampaṭũḍu')
tokens('d236','Kannada',R='alasu|alapaṭe',A='lampaṭe')
tokens('d236','Kui',R='alāṛi',A='laha')
tokens('d236','Kurux',R='algā',A='layākoyā|laikoyornā')

add('d237','blade, tip','*al-ak- / *al-uk-',
    'Ø','a','l','a/u','VC-V-C','noun',
    'Tamil/Malayalam alaku and Kannada alagu/alugu establish vowel-first lateral and an extended stem; Telugu alũgu has nasalization and high medial u.',
    'All witnesses retain a before l. Vowel change and nasalization in Telugu are not evidence that earlier metathesis has occurred.',
    '*al-ak- > alaku/alagu, beside *al-uk- > alugu and Telugu alũgu; no apical relocation. The origin of nasalization needs source or derivative evidence.',
    'Root/formative segmentation is plausible but not established by a corresponding bare *al “blade”. Keep exact V2 classification variable, not a chosen vowel tailored to expected length. The root is phonologically eligible if that segmentation is accepted; retention itself does not establish non-eligibility.',
    {'Telugu':('R','alũgu','Retained order; nasalization unresolved.'),'Tamil':('R','alaku|alakku','Retained singleton/strengthened extensions.'),
     'Malayalam':('R','alaku','Retained order.'),'Kannada':('R','alagu|alugu','V2 varies without displacement.')},
    references='DEDR 237',eligibility='core-formation-uncertain')

add('d240','move, shake, wave','*al-ay-; *al-aŋ- / *al-uk- extensions',
    'Ø','a','l','a','VC-ay / VC-a-NC','verb/noun',
    'Tamil alai/alaŋku, Malayalam alayuka/alaŋŋuka and Kannada ale/alagu supply medial l and low formative independently; Telugu ala and allāḍu preserve the order.',
    'The shared vowel-first SD I/Telugu base plus Kurux alr- favors original al-. Kui lāng- is a derived innovative outcome, not a reason to reverse the reconstructed comparison.',
    '*al-aŋ- > *lāŋ- > Kui lānga; its causative lāk-p- > lāpka requires separate stop-cluster metathesis. Telugu allāḍu can be analyzed as a reinforced/reduplicated formation associated with “move” and must not be reduced to an imaginary initial *lā-. Pengo lem- and Irula le·- require a separate vowel and derivative history.',
    'Tulu landuni/landele may show independent aphaeresis in a wanderer derivative; no shared SCDr event follows. Pengo e and Irula e· cannot be generated by simple a+a contraction without another change. Malayalam alaŋŋ-/anaŋŋ- is l/n assimilation/variation, not vowel–liquid displacement. DEDR treats this root as originally distinct from d236 but acknowledges semantic convergence.',
    {'Telugu':('R','ala|allāḍu|allalāḍu|allārucu','Base and reinforced/compound derivatives retain initial vowel.'),
     'Tamil':('R','alai|alaŋku|alukku','Low/high extensions retain order.'),'Malayalam':('R','alayuka|alaŋŋuka|anaŋŋuka','Root order retained; l/n variation separately tracked.'),
     'Kannada':('R','ale|alagu|aluku|aḷku','Internal quality/retroflexion variations; no initial movement.'),
     'Kota':('R','alg- (algy-)|alk- (alky-)','Internal syncope.'),'Toda':('R','alx- (alxy-)|alk- (alky-)','Internal syncope.'),
     'Tulu':('A','aleyuni|alaŋguni|landuni|landele','Retained core; initial-liquid wanderer formation admits local aphaeresis.'),
     'Kui':('D','lānga (lāngi-)|lāpka (&lt; lākp-; lākt-)','Long displaced stems; separate kp>pk in causative.'),
     'Pengo':('A','lem- (-t-)','Initial liquid consistent with displacement, e and suffix not yet independently accounted for.'),
     'Kurux':('R',"alra'ānā|alrārnā",'Medial cluster/derivation keeps vowel first.'),
     'Badaga':('R','alagu|alugu|aluku','Retained order.'),
     'Irula':('A','le·- (lend-)','Aphaeresis/contraction comparison; no unique vowel history.')},
    references='DEDR 240; DEDR 236 editorial note',
    boundary='-ay and -aŋ/-uk formations independently visible in SD I; exact Pengo/Irula formations unknown.',input_confidence='high')
tokens('d240','Tulu',R='aleyuni|alaŋguni',A='landuni|landele')

from cases_vowel_controls import populate as populate_vowel_controls
populate_vowel_controls(add, tokens)
from cases_a_liquids import populate as populate_a_liquids
populate_a_liquids(add, tokens)
from cases_a_retroflex import populate as populate_a_retroflex
populate_a_retroflex(add, tokens)
from cases_a_remaining import populate as populate_a_remaining
populate_a_remaining(add,tokens)
from cases_i_retroflex import populate as populate_i_retroflex
populate_i_retroflex(add,tokens)
from cases_i_comparisons import populate as populate_i_comparisons
populate_i_comparisons(add,tokens)
from cases_two import populate as populate_two
populate_two(add,tokens)
from cases_i_rhotic import populate as populate_i_rhotic
populate_i_rhotic(add,tokens)
from cases_i_laterals import populate as populate_i_laterals
populate_i_laterals(add,tokens)
from cases_i_alveolars import populate as populate_i_alveolars
populate_i_alveolars(add,tokens)
from cases_nonapical_controls import populate as populate_nonapical_controls
populate_nonapical_controls(add,tokens)
from cases_u_first import populate as populate_u_first
populate_u_first(add,tokens)
from cases_u_rhotic import populate as populate_u_rhotic
populate_u_rhotic(add,tokens)
from cases_u_rubbing import populate as populate_u_rubbing
populate_u_rubbing(add,tokens)
from cases_u_approximant import populate as populate_u_approximant
populate_u_approximant(add,tokens)
from cases_u_laterals import populate as populate_u_laterals
populate_u_laterals(add,tokens)
from cases_u_alveolars import populate as populate_u_alveolars
populate_u_alveolars(add,tokens)
from cases_c_core import populate as populate_c_core
populate_c_core(add,tokens)
from cases_c_chronology import populate as populate_c_chronology
populate_c_chronology(add,tokens)
from cases_lowering_initial import populate as populate_lowering_initial
populate_lowering_initial(add,tokens)
from cases_c_retention import populate as populate_c_retention
populate_c_retention(add,tokens)
from cases_c_formation import populate as populate_c_formation
populate_c_formation(add,tokens)
from cases_c_controls import populate as populate_c_controls
populate_c_controls(add,tokens)
from cases_c_sibilants import populate as populate_c_sibilants
populate_c_sibilants(add,tokens)
from cases_c_residuals import populate as populate_c_residuals
populate_c_residuals(add,tokens)
from cases_c_low_and_long import populate as populate_c_low_and_long
populate_c_low_and_long(add,tokens)
from cases_c_remaining_east import populate as populate_c_remaining_east
populate_c_remaining_east(add,tokens)
from cases_c_m_series import populate as populate_c_m_series
populate_c_m_series(add,tokens)
from cases_c_final_core import populate as populate_c_final_core
populate_c_final_core(add,tokens)
from cases_v_final_controls import populate as populate_v_final_controls
populate_v_final_controls(add,tokens)
from cases_control_nouns import populate as populate_control_nouns
populate_control_nouns(add,tokens)
from cases_lowering_controls import populate as populate_lowering_controls
populate_lowering_controls(add,tokens)
from cases_e_first import populate as populate_e_first
populate_e_first(add,tokens)
from cases_e_controls import populate as populate_e_controls
populate_e_controls(add,tokens)
from cases_e_processes import populate as populate_e_processes
populate_e_processes(add,tokens)
from cases_long_exception import populate as populate_long_exception
populate_long_exception(add,tokens)
from cases_pronouns import populate as populate_pronouns
populate_pronouns(add,tokens)
from cases_long_controls import populate as populate_long_controls
populate_long_controls(add,tokens)
from cases_o_first import populate as populate_o_first
populate_o_first(add,tokens)
from cases_o_controls import populate as populate_o_controls
populate_o_controls(add,tokens)
from cases_late_kuvi import populate as populate_late_kuvi
populate_late_kuvi(add,tokens)
from cases_final_comparisons import populate as populate_final_comparisons
populate_final_comparisons(add,tokens)
from cases_brahui_comparison import populate as populate_brahui_comparison
populate_brahui_comparison(add,tokens)
from cases_say import populate as populate_say
populate_say(add,tokens)
from cases_louse_and_north import populate as populate_louse_and_north
populate_louse_and_north(add,tokens)
from cases_final_residuals import populate as populate_final_residuals
populate_final_residuals(add,tokens)
from cases_cluster_031 import populate as populate_cluster_031
populate_cluster_031(add,tokens)
from cases_cluster_032 import populate as populate_cluster_032
populate_cluster_032(add,tokens)
from cases_cluster_033 import populate as populate_cluster_033
populate_cluster_033(add,tokens)
from cases_cluster_034 import populate as populate_cluster_034
populate_cluster_034(add,tokens)
from cases_cluster_035 import populate as populate_cluster_035
populate_cluster_035(add,tokens)
