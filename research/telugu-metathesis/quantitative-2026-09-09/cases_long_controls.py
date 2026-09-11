"""Long vowel-first controls and explicitly unresolved quantity challenges."""

def populate(add,tokens):
    add('d913','song, metre; sing','regional *ēl/ēḷ; Malto el-',
        'Ø','ē','l/ḷ','e/a','VVC-V','noun/verb',
        'Kannada ēḷe and Telugu ēla independently agree in long ē before lateral. Malto éle marks stress, not independently long quantity.',
        'Both southern forms and Malto keep vowel-before-lateral order; no need to privilege Telugu.',
        '*ēḷ-V > Kannada ēḷe and Telugu ēla, with lateral correspondence and final vowel differing. Malto él-e may support the root but does not establish a long proto-vowel by itself.',
        'A regional song/metre name may diffuse; Kannada–Telugu agreement alone does not rule out borrowing. The Malto singing comparison is semantically compatible but sparsely attested. Keep the family as a qualified long-input retention control, not a metathesis case.',
        {'Kannada':('R','ēḷe','Long vowel-first metre name.'),'Telugu':('R','ēla','Long vowel-first boat song.'),'Malto':('R','éle','Vowel first; accent is not a length mark.')},quantity='long southern; northern uncertain',references='DEDR913 p.88',eligibility='long-input-control',input_confidence='medium')
    add('d914','glean, gather, select','regional *ēṟ-',
        'Ø','ē','ṟ','zero/u','VVC / VVC-C','verb/noun',
        'Kannada ēṟ and Telugu ēṟu independently establish long ē followed by alveolar. Telugu strong causative/nominal formations preserve the same root order.',
        'Both independent language witnesses have V-apical order, with no initial-r form requiring reconstruction.',
        '*ēṟ > ēṟu; strong/extended ērcu, ēṟincu and ērpu retain the root order while changing final consonantal material.',
        'The sparse regional distribution warrants contact caution. Semantic overlap with winnow/separate d915 could indicate one root family; primary partition retains the lexicographic distinction and sensitivity can merge them. Strong derivatives must not count as independent lexical controls.',
        {'Kannada':('R','ēṟ','Independent long root.'),'Telugu':('R','ēṟu|ērcu|ēṟincu|ērpu|ērpaṟacu|ērparincu','One retained root with several formations.')},quantity='long',references='DEDR914 p.88',eligibility='long-input-control',input_confidence='high for regional long order')
    add('d915','separate, winnow, sift','*ēṟ- / shorter extended *eṟ-l-; possible *cēṟ connection',
        'Ø','ē/e','ṟ','zero/i/unknown','VVC-C / VC-l-is','verb/noun',
        'Telugu ēṟu and widespread Gondi ēri/ēr, Konda ēṟ and Kui/Kuvi ē- establish long vowel-first formations. Konda eṟlis and Kuvi erl independently supply shorter extended formations, but not the complete prehistory of ṟēs/jēc.',
        'Widespread vowel-first order versus Konda ṟēs and Pengo jēc supports displacement-family comparison. It does not establish long ē as the immediate input of those precise derivatives, given the independently present short eṟl formation.',
        'Retained *ēṟ-s/p gives Gondi ērst-, Kuvi ērs/ērsp/ēhp and Konda ēṟp. Konda ṟēs and Pengo jēc could reflect long-input displacement or a lost short extended *eṟ-V-s/c; the latter is not directly attested. Kui ēspa/ēja and Kuvi ēhp show consonant developments without initial displacement. Konda nēspa requires additional prothesis or morphological history, not movement of an inherited initial n from this root.',
        'A genuine quantity challenge remains: do not classify ṟēs/jēc as verified short-input outcomes because their outputs are long. Conversely, the full set is not proof that all long roots were eligible. Malayalam ekaṟuka has extra k and cannot simply be treated as the identical unextended stem. DEDR queries relation to cēṟ/cēṭṭai2019; initial c loss, cognacy and formation must be argued separately. Konda nēspa is preserved as an unresolved variant; it could show secondary n as in other Telugu-region verbs, but no source diagnosis is asserted.',
        {'Malayalam':('A','ekaṟuka','Extra k and quantity/formation mismatch; possible relation.'),'Telugu':('R','ēṟu','Retained long sift root.'),'Gondi':('R','ērānā|ēr|ērstānā','Long root and extended paradigms.'),'Konda':('M','ēṟ|ēṟp- (-t-)|eṟlis- (-t-)|ṟēs- (-t-)|nēspa- (-t-)','Long and short retained formations, displaced winnow, unresolved n variant.'),'Kui':('R','ēspa (ēst-)|ēsp|ēja (ēji-)','Retained long vowel-first formations.'),'Kuwi':('R','ērsinai|ērs|ērsp|ēṛlali|ēhp|erl- (-it-)|ēṛsali|ērs- (-it-)','Long/short and consonant variants retain vowel-first order.'),'Pengo':('D','jēc','Displacement-family winnow; immediate quantity uncertain.'),'Kolami':('R','ers','Short vowel-first; source quantity preserved.')},
        quantity='long and independently short extended forms',references='DEDR915 p.88; DEDR source cross-reference2019',eligibility='long-short-formation-challenge',input_confidence='high for mixed quantity; low for immediate displaced input',mechanism='Displacement-family comparison; direct long exchange versus unattested short derivative unresolved.')
    tokens('d915','Konda',R='ēṟ|ēṟp- (-t-)|eṟlis- (-t-)',D='ṟēs- (-t-)',A='nēspa- (-t-)')
    add('d917','male buffalo, bull, male animal','*ēṯ / *ēṟ-',
        'Ø','ē','ṯ/ṟ','zero/u/an','VVC / VVC-V','noun',
        'Tamil ēṟu/ēṟṟai, Malayalam ēṟu/ēṟan and Kota/Toda ēṟ establish long ē before apical. Strong Tamil ṟṟ/ṭṭ supports an alveolar/dental-stop reconstruction rather than treating every r as primary rhotic.',
        'Several independent southern branches have the same vowel-first order; Brahui arē also retains a vowel before r but has its own vocalism.',
        '*ēṯ-u > Tamil ēṟu, Malayalam ēṟu and southern ēṟ; reinforced ēṟṟai/ēṭṭai. Brahui arē/arisk could involve suffixation and vowel redistribution but does not show root-apical promotion to word onset.',
        'Kota tirēr/tir e·r is a compound, not a doubled metathesis result. Brahui arē comparison requires explicit vowel and plural analysis; do not count final ē as proof of a swap because r remains preceded by a. Badaga ēgaru has extra g and an alternative calf cross-reference, so its cognacy is less secure than ēru. DEDR questions connection with sēṟi2820; initial-s history remains outside this control.',
        {'Tamil':('R','ēṟu|ēṟṟai|ēṭṭai','Long root plus strong formations.'),'Malayalam':('R','ēṟu|ēṟan','Long order retained.'),'Kota':('R','e·r|ēr|tir e·r|tirēr','Root and compounds.'),'Toda':('R','e·ṟ|ēṟ','Long root retained.'),'Brahui':('A','arē ( arisk)','Cognacy and vowel/plural prehistory unresolved; no initial-r displacement.'),'Badaga':('A','ēru|ēru kattu|ēgaru','Retained secure root, uncertain extra-g calf form.')},quantity='long',references='DEDR917 p.88; Krishnamurti reconstruction in database',eligibility='long-input-control',input_confidence='high for southern long order')
    tokens('d917','Badaga',R='ēru|ēru kattu',A='ēgaru')
    add('d919','other, the rest','*ēn-ay?; Brahui ēlō',
        'Ø','ē','n/l','ay/ō','VVC-V','pronoun/adjective',
        'Tamil ēṉai and Brahui ēlō agree in long initial ē, but disagree nasal versus lateral. The comparison is sparse and cannot independently settle the consonant reconstruction.',
        'Both witnesses retain vowel-before-sonorant order; l versus n is not a reversal of vowel and consonant.',
        'If cognate, *ēn-ay > Tamil ēṉai and Brahui ēlō requires a motivated n/l correspondence and suffix/vowel development. Alternative separate etymologies remain possible.',
        'Kamaleswaran explicitly opposed deriving Tamil ēṉai from ēṉ why. No metathesis follows from either etymology. Duplicate Tamil DEDR/supplement records represent one lexical witness.',
        {'Tamil':('R','ēṉai','Long initial vowel.'),'Brahui':('A','ēlō','Sparse cognacy with consonant and suffix mismatch.')},quantity='long',references='DEDR919 p.88; DEN13',eligibility='long-nasal-cognacy-control',input_confidence='low for common root, high for attested order')
