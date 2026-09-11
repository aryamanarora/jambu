"""Geminate, nasal-cluster and non-apical controls from the e-section."""

def populate(add,tokens):
    add('d844','all, whole; additive clitic','*ell-a(m), personal expansions',
        'Ø','e','ll','a','VCC-a(m)','quantifier/pronoun/clitic',
        'Tamil ellām, Malayalam ellām, Kannada ella, Kodagu ella· and Telugu ella independently support geminate l. Kota/Toda final el cannot independently diagnose historical singleton intervocalic l.',
        'Initial vowel before the lateral is shared throughout; the Tulu additive enclitic -la has a different morphological position and needs separate grammaticalization history.',
        '*ell-am > ellām/ella involves final quantity and nasal history, not initial metathesis. Conditional *ella > -la would require clitic reduction/aphaeresis, possibly degemination, rather than evidence for the ordinary initial root rule.',
        'Tulu source writes -la (? -lā) and compares its function with *-um; the parser drops the hyphen and turns the editorial reconstruction *-um into a lexical record. The clitic cannot be counted as a secure metathesized lexical all root. Personal suffixes and compounds remain nested observations.',
        {'Tamil':('R','ellām|ellavarum|ellārum|ellēmum|ellōmum|ellīrum','Geminate quantifier with personal morphology.'),'Malayalam':('R','ellām|ellāvum|ellīrum','Same.'),'Kota':('R','el|elm','Final cluster/root reduction.'),'Toda':('R','el|elm|elm ( elnm, eltkm)|om elom|omelom|nɨm elom|nɨmelom','Case and pronominal compounds, same initial order.'),'Kannada':('R','ella|ellarum','Geminate root.'),'Kodagu':('R','ella·','Geminate root.'),'Tulu':('A','la (? -lā)','Bound additive clitic, possible grammatical reduction.'),'Telugu':('R','ella|ellaru|ellavā̃ḍu','Geminate root and persons.'),'Kuwi':('R',"ele'e",'Full vowel-first form; consonant notation differs.'),'Kolami':('R','ittar el','Both compound with independent all member.'),'Badaga':('R','ella|ellāru','Geminate quantifier.')},
        c2_structure='geminate',input_confidence='high',references='DEDR844 p.82 directly read; MBE1974a pp.107–108 cited there, not directly read',eligibility='geminate-control',boundary='Clitic and personal suffix morphology independent of phonological outcome.',mechanism='Geminate retention; Tulu clitic reduction unresolved.')

    add('d845','tomorrow, day after tomorrow','regional *ell-i/e',
        'Ø','e','ll','i/e','VCC-V; compounds','adverb',
        'Tulu elle and Telugu elli independently agree on short e and geminate l; Markodi elle/yelle supports the same regional shape.',
        'All witnesses place the vowel before the geminate. Initial y in Markodi is prothesis or a separate local onset, not a moved root liquid.',
        '*elli/e > elli/elle retains order. Telugu elluṇḍi and Tulu ellañji are different day-after-tomorrow formations whose endings require separate reconstruction.',
        'This is a regional control, not proof of a Proto-Dravidian time adverb. K03 p.407 includes Brahui elli in a broader distribution statement, but the database group and DEDR entry lack a Brahui attestation; that published claim remains source-only and unverified here. Potential relation to light/day829, all844 or limit846 should be tested as family sensitivity, not assumed from ell alone.',
        {'Tulu':('R','elle|ellañji','Geminate root and compound.'),'Telugu':('R','elli|elluṇḍi','Geminate root and compound.'),'markodi':('R','elle|yelle|yelleᵘ̆','Prothetic/quantity variants preserved.')},
        c2_structure='geminate',input_confidence='high regional shape',references='DEDR845 p.82 directly read; K03 adverbial discussion',eligibility='geminate-control',boundary='Bare adverb versus subsequent day compounds.',mechanism='Geminate retention.')

    add('d846','boundary, limit','*ell-ay; Malayalam *el-u-k variant',
        'Ø','e','ll/l','a/ay/u','VCC-ay / VC-uK','noun',
        'Tamil ellai, Malayalam ella, Kannada elle and Telugu ella independently establish a geminate low-vowel formation. Malayalam eluka instead has a singleton lateral and different velar expansion.',
        'The initial vowel precedes lateral in all forms; single final Toda l does not prove a singleton intervocalic ancestor.',
        '*ell-ay > ellai/elle/ella retains order; Toda ely follows its own final sequence reduction. Malayalam eluka may be a separately expanded grade, not metathesis or evidence against the geminate reconstruction of the main formation.',
        'Classify the common ell-ay formation as geminate and the Malayalam singleton separately. Boundary place names repeat the same root. A possible connection with all844 or day845 is a deeper lexical hypothesis; shared spelling alone is insufficient.',
        {'Tamil':('R','ellai','Geminate low-vowel formation.'),'Malayalam':('R','ella|eluka','Geminate main form, different singleton derivative.'),'Toda':('R','ely','Reduced final sequence.'),'Kannada':('R','elle','Geminate formation.'),'Telugu':('R','ella','Same.'),'Badaga':('R','elle|boddelle|ellekal','Root and compounds.')},
        c2_structure='geminate main formation; singleton derivative',input_confidence='high by formation',references='DEDR846 p.82 directly read',eligibility='geminate-control',boundary='Independent contrast between ell-ay and el-u-k retained.',mechanism='Original initial order retained.')

    add('d856','slight, weak, contemptible','*eḷ-i; *iḷ-a; strong *eḷḷ',
        'Ø','e/i','ḷ','i/a/u','VC-i / VC-a / VCC','adjective/verb/noun',
        'Tamil eḷi/eḷimai and Malayalam eḷi/eḷima establish high-i singleton formation, alongside independently low-a iḷamai/iḷama and strong eḷḷu.',
        'Southern forms and historical Kannada iḷi agree on vowel-first order. Telugu ellidamu retains the vowel and a strengthened lateral; the strengthening is a local or borrowed formation, not evidence of universal original gemination.',
        '*eḷ-i > eḷi/iḷi retains order; *eḷḷ > Tamil eḷḷu and Telugu ellidamu-like strength has a separate history. Tamil eṇmai follows l/n assimilation in a nominal suffix environment.',
        'Telugu is a retained-order observation but exact input strength and inheritance of ellidamu are uncertain. Do not classify all weak/light words as geminate merely from Telugu. Possible relation to young513 and poor911 or contempt776 is semantic/derivational and must be tested, not used to manufacture one regular class.',
        {'Tamil':('O','eḷi|eḷimai|eḷumai|eḷiyaṉ|eḷiyavaṉ|eḷiñar|eḷitaravu|iḷamai|iḷappam|eḷḷu|eḷku|eṇmai','High/low and strong forms; nasal assimilation.'),'Malayalam':('R','eḷi|eḷima|eḷuppam|eḷutu|iḷama|iḷappam','Several independent formations.'),'Kannada':('R','iḷisu','Retained causative.'),'Tulu':('R','elli|ellya','Strengthened lateral.'),'Telugu':('R','ellidamu','Retained strengthened nominal form.'),'pampa':('R','iḷi','Historical Kannada high-i formation.')},
        c2_structure='singleton/strong by formation',input_confidence='high root; medium exact Telugu formation',references='DEDR856',boundary='High-i, low-a and strong formations are independently attested.')
    tokens('d856','Tamil',R='eḷi|eḷimai|eḷumai|eḷiyaṉ|eḷiyavaṉ|eḷiñar|eḷitaravu|iḷamai|iḷappam|eḷḷu|eḷku',O='eṇmai')

    add('d857','bear','*eḷ-V-ñc; regional *uḷ-iy-am and *el-uK',
        'Ø','e/i/u','ḷ/l','unknown/i/u','VC-V-NC / VC-uK / VC-iy-am','noun',
        'Tamil iḷai/uḷiyam/elu, Malayalam uḷiyam, Parji ili and Gondi eṛj establish vowel-first lateral/apical forms with several extensions. Konda olzu/oṛzu independently supports apical before z.',
        'The distribution supports an earlier vowel preceding the apical; the displayed alternative *joḷǯ- is a separate reconstruction and cannot override the comparative onset evidence without an initial-y account.',
        '*eḷ-Vñc > Gondi eṛj and Konda olzu/oṛzu involves syncope and palatal/nasal changes while retaining vowel-first order. Kui oli/oḍi and Kuvi oṛi reflect apical merger/stop development. Tamil eṇku and Malto eju have medial cluster reductions. Telugu elūgu is unusual in its long second vowel and needs separate suffix history.',
        'No positive initial displacement is attested despite several eastern languages. Exact ancestral vowel/formative varies and is not inferred from modern outcomes. Konda north/west rhotic versus south/east lateral is useful dialect correspondence, not necessarily metathesis variation. Animal-name diffusion remains possible but does not explain away the retained forms.',
        {'Tamil':('O','iḷai|uḷiyam|elu|eṇku','Full and medially assimilated forms.'),'Malayalam':('R','uḷiyam','Different nasal noun expansion.'),'Telugu':('R','eluvu|elūgu','Vowel-first lateral, second-vowel quantity unresolved.'),'Gondi':('R','arje|eṛju (aṛjahk/aṛjalor)|arjāl ( -or)|eṛj (aṛjahk/aṛjalor)|aṛjal (aṛjahk/aṛjalor)|eṛji (aṛjahk/aṛjalor)|aṛjāl (aṛjahk/aṛjalor)|eṛjal (aṛjahk/aṛjalor)','Dialect/apical/plural variation, same initial order.'),'Konda':('R','oṛzu|olzu ( olsku)','North/west rhotic versus south/east lateral.'),'Kui':('R','oli|oḍi','Lateral/stop reflexes.'),'Kuwi':('R',"o'ṛi|ouḍi",'Glottal/quantity/apical variation.'),'Parji':('R','ili ( ilil)','Lateral noun and plural.'),'Gadaba':('R','illij ( iljīl; j = dz)|ilij ( iljil)','Lateral/palatal formation.'),'Malto':('O','eju','Medial cluster simplification.')},
        input_confidence='high for order; medium for full root',references='DEDR857; K03 reconstruction *eḷ-V-ñc',boundary='Different animal-name extensions and paradigms remain distinct.')
    tokens('d857','Tamil',R='iḷai|uḷiyam|elu',O='eṇku')

    add('d865','red','*eṯ-V; *eṯ-a/*eṯ-up',
        'Ø','e','ṟ/ṯ','a/u','VC-a / VC-uP; strengthened VCC-a','adjective/noun',
        'Konda eṟa/eṟani and Tamil eṟuṛ̆am red-flowered tree independently support short initial e before an alveolar; Telugu eṟupa and historical Eṟama have singleton evidence beside modern eṟṟa.',
        'The independent Konda form and singleton variants favor a vowel-first root, not a primitive initial r. Gemination in Telugu is not uniformly ancestral.',
        '*eṯ-a > eṟa and strengthened eṟṟa retain initial order; *eṯ-up > eṟupa has a different noun expansion. Gondi erra is explicitly borrowed from Telugu and must not become an independent inherited retention.',
        'The source dates Eṟama as an eighth-century name and Eṟṟana as the fourteenth-century author; these are lexicographic date claims pending inscription verification. Tamil botanical semantic link is less direct than Konda colour, and Kolami eroṛi/erroḍī may be regional loans. Possible relationship to red/dog817 and clay820 requires a cognacy argument, not automatic merging of colour roots.',
        {'Tamil':('R','eṟuṛ̆|eṟuṛ̆am','Red-flowered tree comparison.'),'Telugu':('R','eṟupa|eṟṟa|eṟṟana|eṟṟani|Eṟama|Eṟṟana','Retained root with chronological/formation variation.'),'Gondi':('B','erra','DEDR explicitly < Telugu.'),'Konda':('R','eṟa|eṟani','Independent singleton low-a adjective.'),'Kolami':('A','eroṛi|erroḍī','Vowel-first shape but possible Telugu contact.')},
        c2_structure='singleton and strengthened formations',input_confidence='high regional order; medium deeper cognacy',references='DEDR865; K03 regional *eṯ-V',boundary='Low-a adjective and -up noun independently distinguished.')

    add('d869','sunshine, dry in sun','*en-ṯ-V / *enṯ',
        'Ø','e','nṯ','u/a','VNC-V','noun/verb',
        'Tamil eṉṟu and Telugu eṇḍa/eṇḍu independently establish a nasal-apical cluster. Gondi eddi/addī and Naiki edde can reflect medial assimilation of that cluster.',
        'Nasal and apical follow the initial vowel in the independent southern witnesses. Parji nendi/nenḍi adds an initial nasal whose origin cannot simply be called initial apical displacement.',
        '*enṯ > eṉṟ/eṇḍ retains cluster order; *enṯ > edd is assimilation and possible denasalization. Parji nendi could reflect nasal prothesis, analogy with day words or a different extension; the medial nasal remains, so simple swapping of the sole n is inadequate.',
        'A root-cluster control, not an exception invented from its retained result. Toda eṟ in a song is explicitly labeled probably spurious by the newer dictionary, so it contributes no secure singleton evidence. Connection to el shine829 or eṟi861 is a lexical hypothesis; no automatic collapse until the lateral/nasal/stop derivation is supported.',
        {'Tamil':('R','eṉṟu|eṉṟ ūṛ̆','Independent nasal-apical source.'),'Toda':('A','eṟ|eṟ oṭ ṇelp','Source explicitly doubts the entry/interpretation.'),'Telugu':('R','eṇḍa|eṇḍu|eṇḍugulu','Noun/verb and grain derivative.'),'Gondi':('R','addī|addi|adī|ed|eddi|yaddi','Medial assimilation and prothetic y.'),'Naiki':('R','edde','Medial assimilation.'),'Parji':('A','nendi|nenḍi','Initial nasal source unresolved, not simple metathesis.')},
        c2_structure='nasal-stop cluster',input_confidence='high for cluster',references='DEDR869; Toda2025 p.15 entry20 explicitly doubtful',eligibility='root-cluster-control',boundary='Nasal cluster independently reconstructed; derived dry/grain forms nested.',mechanism='Cluster retention/assimilation; Parji prothesis/analogy unresolved.')
