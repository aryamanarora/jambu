"""Alveolar comparisons and controls: uncertain source heads are not proto-evidence."""

def populate(add,tokens):
    add('d516','descend, bow; landing place','*i/eṟ-a-; *iṟ-aŋk- and *iṟ-av- formations',
        'Ø','i/e','ṟ','a','VC-a-NC / VC-av','verb/noun',
        'Tamil iṟai/iṟaŋku/iṟakku, Kannada eṟagu, Kodagu əraŋg and Telugu eṟãgu establish short vowel before the alveolar. The displayed elephant *yĀn-ay is a mislinked reconstruction and is excluded.',
        'Independent SD I witnesses support older V–ṟ. Telugu port ṟēvu/rēvu is displaced relative to the comparable Malayalam iṟavu valley noun, while Telugu descend/bow preserves the fuller nasal-velar formation.',
        'Conditional *iṟ-av > *eṟav > *ṟēv > historical ṟēvu > rēvu; *iṟ-aŋk > eṟãgu retains order. Gondi ray/rey and Konda ṟe/ṟes are shortened/extended displaced stems. Tulu ija beside japp/jāp suggests local initial-vowel loss plus ṟ-related consonant changes; an exact history is not a bare r swap.',
        'The database dates Old Telugu ṟēvu to tenth-century place names; these are source assertions pending inscription-level identification. Pengo jū has an unexplained vowel under a uniform low-a rule. K80 proposes moving some d2456 Kui jāpa/Manda forms here: treat that as a cognacy hypothesis, not an extra certain row. Irula ṟaŋgu may reflect local aphaeresis or contraction and has short/long variants. Toda hair-vow compound is explicitly borrowed from Tamil, distinct from inherited direction/swallow forms.',
        {'Tamil':('R','iṟai|iṟaŋku|iṟakku|iṟaiñcu','Independent vowel-first root and expansions.'),
         'Malayalam':('R','iṟayuka|iṟaŋŋuka|iṟakkuka|iṟavu','Vowel-first verbal and valley formations.'),
         'Kannada':('R','eṟagu','Lowering without displacement.'),'Kodagu':('R','əraŋg- (əraŋgi-)|ərak- (əraki-)','Transitivity pair retains order.'),
         'Kota':('R','erg- (ergy-)|erk- (erky-)|erg','Syncope keeps V–apical order.'),
         'Toda':('R','eṟk|iṟk- (iṟky-)','Inherited down/swallow comparison retains vowel first.'),
         'Tulu':('A','eraguni|ija|jappuni|jāpuni|jāpini|japuḍuni|ekkuni','Retained and initial-loss forms, plus medial assimilation; correspondence history unresolved.'),
         'Telugu':('M','eṟãgu|erãgu|erãguḍu|rēvu','Retained bow/descend derivative versus displaced port noun.'),
         'OTelugu':('D','ṟēvu','Tenth-century place-name attestation according to DEDR.'),
         'Gondi':('D','ray|rey|reyānā|raggānā|ragstānā|rehtānā','Initial displacement likely; suffix and vowel variants retained.'),
         'Konda':('D','ṟe- (-t-)|ṟes- (-t-)|ṟep','Initial displacement with distinct intransitive/transitive suffixes.'),
         'Kuwi':('D',"recali|repʰali|re'nai|jespi",'Displaced forms; r/j and aspiration belong to local development.'),
         'Pengo':('A','jū- (-t-)','Initial apical-related consonant plausible; unexpected u needs independent account.'),
         'Badaga':('R','eragu|eraku','Retained transitivity pair.'),
         'Irula':('A','ṟa·ŋgu̇|ṟaŋgu','Initial-loss/contraction variants, not automatically the SC process.'),
         'Koraga':('A','jāvu','Possible local displacement/aphaeresis or regional diffusion.')},
        input_confidence='high',references='DEDR 516; K80 table 1 item 5 and reassignment discussion; original DEDR historical labels',
        boundary='The nasal-velar verb and -av landing-place noun have independent comparative support and must be separately tested.')
    tokens('d516','Telugu',R='eṟãgu|erãgu|erãguḍu',D='rēvu')
    tokens('d516','Tulu',R='eraguni|ija',A='jappuni|jāpuni|jāpini|japuḍuni',O='ekkuni')

    add('d517','prawn, shrimp','*i/eṟ-a/v/y-; exact nominal formation uncertain',
        'Ø','i/e','ṟ','a','VC-a-v / VC-V-y','noun',
        'Tamil iṟavu/iṟā and Malayalam iṟāvu support vowel-first alveolar order. Tulu eṭṭi has an additional geminate/consonant history. The prawn reconstructions mislinked to d533 are related scholarly proposals, not fly inputs.',
        'Southern vowel-first names favor earlier V–ṟ, making Telugu reyya/royya plausibly innovative. Regional rēy nouns could nevertheless have spread after a single change.',
        'Possible *iṟ-ay > *eṟay > *ṟēy > reyya with gemination/shortening; royya additionally requires vowel rounding or an independently rounded variant. Tamil -av and eastern -y are not silently assumed identical. Konda ṟeyo preserves distinct alveolar transcription.',
        'The o in royya is not predicted by a uniform *i+a > ē account; contact or rounding needs independent evidence. Gondi Koya and Gadaba reyya are especially close to Telugu and remain contact candidates. Parji rēḍa has a different consonant ending; its inheritance versus regional diffusion needs historical support. No separate root counts for dialect variants.',
        {'Tamil':('R','iṟavu|iṟā|iṟāl|iṟal','Related shellfish names retain order; meanings and quantity vary.'),
         'Malayalam':('R','iṟāvu','Vowel-first shrimp name.'),'Tulu':('O','eṭṭi','Vowel first with a separate medial strengthening history.'),
         'Telugu':('D','reyya|royya','Probable displacement; e/o variation unresolved.'),
         'Gondi':('A','reyya|rēyi kīke','Koya forms could be Telugu-area loans.'),
         'Konda':('D','ṟeyo','Probable inherited displacement, exact vowel/ending development uncertain.'),
         'Kuwi':('D','rēya','Probable displacement; contact cannot be ruled out solely by this noun.'),
         'Parji':('A','rēḍa','Possible regional diffusion; final consonant history unresolved.'),
         'Gadaba':('A','reyya','Close Telugu match, probable contact candidate.')},
        references='DEDR 517; prawn *eṯ-V-y reconstruction is mislinked under d533 in Jambu',
        boundary='Southern -av and eastern -y noun formations are related hypotheses, not one unexamined suffix.')

    add('d520','break, snap','*iṟ-u-; eastern *iṟ-aŋk / *iṟ-ek-p?',
        'Ø','i','ṟ','u/unknown','VC-u / VC-NC / VC-C-p','verb',
        'Tamil iṟu and Malayalam iṟuka independently establish a high-u formation and vowel-first alveolar. Telugu iriyu differs in final vowel, while Kui renga/repka contains additional consonantal morphology.',
        'The southern comparison plus Kurux e-initial cognates favors earlier initial vowel. Kui initial r is plausibly displaced but its exact formative vowel is not established from the southern u verb.',
        'Telugu *iṟ-i > iriyu retains order. Kui *iṟ-Vŋk > reng and *iṟ-Vk-p > *rekp > repk could reflect initial displacement followed by a morphologically motivated k/p exchange. The first operation’s vowel history is underdetermined; the second is explicitly given in DEDR.',
        'Do not infer a low formative from Kui e alone. Kurux esnā/eṣ-type consonant development is separate and does not erase the initial vowel. The published underlying rek-p and past rekt provide stronger direction evidence for consonant-cluster metathesis than this set provides for the exact earlier initial vowels.',
        {'Tamil':('R','iṟu','High-u formation retains order.'),'Malayalam':('R','iṟuka','Retained order.'),
         'Telugu':('R','iriyu','Retained order in the i/y formation.'),
         'Kui':('D','renga (rengi-)|repka','Displaced family under cognacy; exact vowel conditioning unresolved.'),
         'Kurux':('R','esnā (essas)|esrnā','Initial vowel retained with local consonant change.')},
        references='DEDR 520; explicit Kui <rek-p-, past rekt- in source',
        boundary='High-u southern stem distinguished from eastern nasal/causative expansions.')

    add('d524','be tight, squeeze, narrow place','*iṟ-u-k(k)-; other *iṟ-V formations',
        'Ø','i','ṟ','u','VC-u-k(k)','verb/noun',
        'Tamil iṟuku/iṟukku, Kannada iṟuku and Telugu iṟuku independently support the same high-u velar expansion. Konda iRku/iṟmu and Kota irg/irk corroborate vowel-first order after syncope.',
        'Broad southern and Konda agreement supports retained V–ṟ. Medial apical loss in ikku-type words is distinct from movement to word onset.',
        '*iṟ-uk > Telugu iṟuku; syncope *iṟ-k > ikk can produce ikku/ikkaṭṭu by medial assimilation. *iṟ-m > imm is a plausible route in immudappu; ibbandi has additional unexplained morphology. Kui ṛuhpa may reflect initial loss before a retained u vowel or a separately formed displaced stem.',
        'Kui u does not demonstrate a vowel swap from the independent i/u input: aphaeresis preserves the second vowel directly. Telugu iṟi/iṟiyu retain high-i formations too. The complex adversity nouns must not be counted as independent retained roots or assumed fully derived merely from semantic similarity.',
        {'Tamil':('O','iṟuku|iṟukku|ikku|ikkaṭṭu','Retained root plus medial-assimilation formations.'),
         'Malayalam':('O','iṟukuka|iṟukkuka|ikku|ikkaṭṭu','Same distinction.'),
         'Kannada':('O','iṟuku|iṟiku|irku|iṟaŋku|ikkaṭṭu|irkaṭṭu','Vowel variants, syncope and medial assimilation retain initial vowel.'),
         'Kota':('O','irg- (irgy-)|irk- (irky-)|ikaṭ','Retained initial vowel; medial cluster assimilation in derivative.'),
         'Toda':('O','ikoṭ','Complex narrowness noun, medial loss/assimilation.'),
         'Tulu':('O','iriyuni|irbuliyuni|ikkaṭṭɯ','Retained roots and medial-assimilation compound.'),
         'Telugu':('O','iṟuku|iṟi|iṟiyu|iṟiyincu|iṟumu|ikkaṭṭu|ikku-pāṭu|immudappu|ibbandi','Retention plus medial assimilation and uncertain complex nouns.'),
         'Konda':('R','iRku|iṟaŋa|iṟzu|iṟmu','Vowel-first tightness series.'),
         'Gondi':('R','ihittānā','Initial vowel retained, local consonant history.'),
         'Kui':('A','ṛuhpa (ṛuht-)','Initial loss versus displacement and suffix ancestry uncertain.'),
         'Kurux':('R','eṭṭnā (iṭṭyā)','Initial vowel retained with strengthening.'),
         'Badaga':('O','iruku|irupe|irupu|ikku','Retained roots plus medial loss.')},
        input_confidence='high',references='DEDR 524',
        boundary='The -uk(k) formation is independently matched across Tamil, Kannada and Telugu.')
    tokens('d524','Telugu',R='iṟuku|iṟi|iṟiyu|iṟiyincu|iṟumu',O='ikkaṭṭu|ikku-pāṭu|immudappu',A='ibbandi')
    tokens('d524','Tamil',R='iṟuku|iṟukku',O='ikku|ikkaṭṭu')
    tokens('d524','Malayalam',R='iṟukuka|iṟukkuka',O='ikku|ikkaṭṭu')
    tokens('d524','Kannada',R='iṟuku|iṟiku|irku|iṟaŋku|irkaṭṭu',O='ikkaṭṭu')
    tokens('d524','Kota',R='irg- (irgy-)|irk- (irky-)',O='ikaṭ')
    tokens('d524','Tulu',R='iriyuni|irbuliyuni',O='ikkaṭṭɯ')
    tokens('d524','Badaga',R='iruku|irupe|irupu',O='ikku')

    add('d527','lord, king, husband','*i/eṟ-ay-; human *iṟ-ay-anṟu',
        'Ø','i/e','ṟ','a','VC-ay + human suffix','noun',
        'Tamil iṟai/iṟaivaṉ and Kannada eṟe/eṟeya establish vowel-first low-ay input independently. Telugu historical eṟa is a retained title, while ṟē̃ḍu incorporates a human ending.',
        'Independent SD I agreement plus historical Telugu eṟa favors older vowel before alveolar. The displaced extended title is not a reason to reclassify the bare historical title as noncognate.',
        '*iṟ-ay-anṟu > *eṟayanṟu > *ṟēyanṟu > ṟē̃ḍu is a plausible schematic path; exact y loss and human-ending assimilation require their own chronology. Malayalam iṟān > rān can instead result from aphaeresis.',
        'DEDR identifies eṟa in a seventh–eighth-century Nellore inscription, citing Master BSOAS 12:351. This date belongs to that source claim pending primary inscription check. The singular/human morphology is independently motivated, but no blanket claim that all human suffixes trigger metathesis follows.',
        {'Tamil':('R','iṟai|iṟaivaṉ|iṟaiyavaṉ|iṟaivi','Retained base and gendered forms.'),
         'Malayalam':('O','iṟān|rān','Retained and initial-vowel-loss address forms.'),
         'Kannada':('R','eṟe|eṟeya|eṟati','Retained order.'),
         'Telugu':('M','eṟa|ṟē̃ḍu','Historical retained bare title versus displaced extended human noun.')},
        input_confidence='high',references='DEDR 527; Master BSOAS 12:351 cited there; K03 *eṯ-ay-anṯu reconstruction in corpus',
        boundary='Human suffix and bare title distinguished; exact prehistoric ending reconstructed, not attested.')
    tokens('d527','Telugu',R='eṟa',D='ṟē̃ḍu')
    tokens('d527','Malayalam',R='iṟān',O='rān')

    add('d528','eaves, roof, edge','*i/eṟ-ay-; *iṟ-ak- roof formation',
        'Ø','i/e','ṟ','a','VC-ay / VC-ak; second compound member','noun',
        'Tamil iṟai/iṟappu, Malayalam iṟa and Kannada eṟake/eṟakil establish initial vowel and low formative; Kodagu ərakɨ corroborates the velar roof formation.',
        'The southern vowel-first forms make Konda ṟēkam, Kui rēpa and Pengo jēgom likely innovations. Telugu retains eṟa as the second member of a well-parapet compound.',
        'Possible *iṟ-ak > *eṟak > *ṟēk > Konda ṟēkam/Pengo jēgom, followed by local consonant/ending changes. Kui rēpa has a labial formation, compared with Tamil iṟappu. Telugu talli-y-eṟa retains the vowel of the second member, with a boundary glide.',
        'This Telugu attestation tests a compound-medial environment, not necessarily the rule’s word-initial domain. It must remain in the dataset but separate from free simplex counterexamples. Badaga topographic names multiply records without multiplying roots; only ere and ere mane are direct lexical witnesses.',
        {'Tamil':('R','iṟai|iṟappu','Retained root and labial derivative.'),'Malayalam':('R','iṟa|iṟampu','Retained order.'),
         'Kannada':('R','eṟake|eṟakil','Retained velar formation.'),'Kodagu':('R','ərakɨ','Retained velar formation.'),
         'Telugu':('R','talliyeṟa','Retained second compound member; standalone eṟa record is source extraction of that member.'),
         'Konda':('D','ṟēkam','Displaced velar roof formation.'),'Kui':('D','rēpa','Displaced labial slope/edge formation.'),
         'Pengo':('D','jēgom','Displaced velar formation with local alveolar reflex.'),'Badaga':('R','ere|ere mane','Retained veranda word.')},
        input_confidence='high',references='DEDR 528',
        boundary='Telugu relevant root occurs as second compound member; southern velar and labial expansions independently matched.')

    add('d529','meat, eat meat','*iṟ-ay-cci / *iṟ-a-cci',
        'Ø','i','ṟ','a','VC-a-cc-i','noun/denominal verb',
        'Tamil iṟacci, Malayalam iṟacci and Kodagu eraci independently support a low-vowel nominal formation; Telugu eṟaci matches it closely.',
        'Independent southern agreement supports vowel-first ordering; Konda ṟe is innovative if its eat-meat verb is derived from this noun/root.',
        '*iṟacci > *eṟacci > Telugu eṟaci through lowering and degemination without initial displacement. Konda *iṟ-a > *ṟē > ṟe could be a displaced shorter verbal formation, but its exact derivational relation is not given by the noun alone.',
        'This is a strong retained low-formative comparison. The later cc does not make the eligible first apical geminate. Pengo jey explicitly competes with d2549 sprout, so it cannot be a certain metathesis success in this family. Tamil iṟṟi is a separate strengthened noun variant.',
        {'Tamil':('R','iṟacci|iṟṟi','Retained order; distinct strengthened variant.'),'Malayalam':('R','iṟacci','Retained low-vowel formation.'),
         'Kodagu':('R','eraci','Retained lowered form.'),'Telugu':('R','eṟaci','Retained independently matched formation.'),
         'Konda':('D','ṟe- (-t-)','Probable displacement in the eat-meat formation.'),
         'Pengo':('A','jey','Explicit competing cognacy with sprout.'),'markodi':('R','eraci','Retained lexical form; source lect preserved.')},
        input_confidence='high',references='DEDR 529; K03 *iṯ-ay-cci reconstruction in corpus',
        boundary='The -acci noun is independently matched; Konda shorter verbal formation cannot test precisely the same full input.')
