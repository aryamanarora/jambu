"""Contiguous e-initial comparisons, including retained and opaque outcomes."""

def populate(add,tokens):
    add('d810','wind, breeze','regional *er-al / *el-ar',
        'Ø','e','r/l','a','VC-aC / compound#VC-aC','noun',
        'Kannada eral/eraḷ/elar/elal and Telugu compound temm-eral independently establish an initial vowel before the first liquid; exact liquid order is variable within Kannada.',
        'Telugu temm-eral and the cited Tamil nir̤ali comparison favor r before l, but restricted distribution and alternative elar prevent a certain ancestral order between the two liquids.',
        '*er-al > Kannada eral and Telugu temm-eral retains initial order; Kannada elar can be an internal r/l exchange, elal assimilation, and Telugu temm-era final-l loss. payy-ara has its own compound vowel history.',
        'This is not initial metathesis. Treat Kannada internal exchange as a separate medium-confidence process. Source temm-eral is attested in Kumārasambhava and an inscription reference via Sastri p.99, but no date is assigned until those references are localized. Badaga Eranda dog name has uncertain relationship and contributes no secure wind evidence.',
        {'Kannada':('R','eral|eraḷ|elar|elal','Initial vowel retained; internal liquid-order variation separate.'),'Telugu':('R','temm-eral|temm-era|payy-ara','Wind member in compounds, final segment loss/grade differs.'),'Badaga':('A','Eranda','Dog name lacks demonstrated wind derivation.')},
        input_confidence='medium for regional vowel-first root; low for liquid order',references='DEDR810; DEN1 1972 p.416 S96',eligibility='compound-process-separate',boundary='Telugu root is only attested inside compounds; first member must be removed before classification.',mechanism='Initial order retained; internal liquid exchange possible.')

    add('d813','manure, defecate','*er-u(k)/er-Vk; nasal velar extensions',
        'Ø','e','r','u/unknown','VC-uK / VC-NK','noun/verb',
        'Tamil eru/eruku, Malayalam eru/erukuka and central/northern erŋg/erx independently place e before r. High u is supported in the southern velar formation; nasal extensions are distinct.',
        'Southern, central and northern agreement favors vowel-first order independently of Telugu eruvu/ērugu.',
        '*er-uK > Telugu ērugu involves unexplained or morphological lengthening but preserves V-r order. *er-uV > eruvu is retained. Kannada ekku allows medial r/velar assimilation; Gondi ērg adds quantity and syncope, not initial reversal.',
        'The long Telugu velar stem must not be used to reconstruct a universally long proto-root: Tamil eruku is short. Different noun/verb derivatives and existing Kannada ēru suggest a quantitative grade, but its conditioning is not established. Medial r loss in Kannada is opaque for detailed chronology, not automatically hidden initial metathesis.',
        {'Tamil':('R','eru|eruku','Independent high-u full forms.'),'Malayalam':('R','eru|erukuka','Same.'),'Kannada':('O','ēru|eraṇa|erubu|ekku','Retained and medially assimilated forms.'),'Telugu':('R','eruvu|ērugu','Order retained despite quantity contrast.'),'Gondi':('R','ērg','Long syncopated root.'),'Kolami':('R','erŋg- (ereŋkt-)','Nasal velar extension.'),'Naikri':('R','erŋg','Same.'),'Naiki':('R','eruŋ|eruŋta','Full/extended formation.'),'Gadaba':('R','erg','Syncope, no reversal.'),'Kurux':('R','erxnā (irxyas)','Full paradigm vowel grade.'),'Malto':('R','erɣe|erɣtre','Root/causative.')},
        input_confidence='high for order; medium for exact shared formation',references='DEDR813; DEN1 1972 p.401 entry696',boundary='Noun and velar/nasal verbal formations kept distinct.')
    tokens('d813','Kannada',R='ēru|eraṇa|erubu',O='ekku')

    add('d815','bull, ox; consecrated bull compound','*er-ut / *er-t',
        'Ø','e','r','u/zero','VC-uT / VCT','noun',
        'Tamil/Malayalam erutu, Tulu eru and Kannada eṛ̆tu establish older vowel-r order with a stop extension independently of Telugu eddu. Whether all branches inherited a vowel or a cluster at the relevant date is not fixed.',
        'Shared fuller er-u-t and r-t show r before the dental rather than a primitive initial r. Medial assimilation readily yields eddu/ettu in several languages.',
        '*erut > *ert > ett/edd gives Kannada eddu/ettu, Telugu eddu and central eḍ. Telugu compound gaŋgi-reddu could contain inserted/linking r after an already assimilated eddu, or a separately displaced/shortened formation; neither chronology is established by the compound alone.',
        'Do not count gaŋgi-reddu as certain inherited metathesis. Original DEDR writes -reddu, explicitly bound, beside gaṅg-eddu; parser removes the initial hyphen and creates an apparent free word. Short e and geminate dd require explanations under any *erut>rēt route. Toda eṭ in song is explicitly a Badaga loan; inherited ešt/eśt remains separate. Telugu eddu is an opaque apical-loss development, not a clean retained-r example.',
        {'Tamil':('R','erutu','Full high-u formation.'),'Malayalam':('R','erutu','Same.'),'Kota':('O','et','Medial r loss/assimilation.'),'Toda':('O','ešt|eśt|eṭ ṭešk|e ṭešk|e(ṭ) ṭeśk','Inherited consonant change plus explicit Badaga song loan.'),'Kannada':('O','eṛ̆tu|eddu|ettu','r-t retained versus assimilation.'),'Kodagu':('O','əttɨ','Medial assimilation.'),'Tulu':('R','eru','Root order retained, stop extension absent.'),'Telugu':('A','eddu ( eḍlu)|eddu paṭṭu|reddu|gaŋgi-reddu','Assimilated simplex and uncertain bound r form.'),'Kolami':('O','eḍ ( eḍl)','Medial assimilation.'),'Naikri':('O','heḍḍ ( heḍḷ)','Prothesis plus medial assimilation.'),'Kurux':('O','aḍḍō','Vowel change plus assimilation.'),'Badaga':('O','ettu','Medial assimilation.')},
        input_confidence='high for full order; uncertain pre-metathesis syncope',references='DEDR815; original SQL rows9924–9927; PSS83 pp.393–394 medial-r loss',boundary='Simplex versus specifically bound -reddu distinguished.',mechanism='Medial assimilation; compound r origin unresolved.')
    tokens('d815','Kannada',R='eṛ̆tu',O='eddu|ettu')
    tokens('d815','Toda',O='ešt|eśt',B='eṭ ṭešk|e ṭešk|e(ṭ) ṭeśk')
    tokens('d815','Telugu',O='eddu ( eḍlu)|eddu paṭṭu',A='reddu|gaŋgi-reddu')

    add('d816','buffalo','*er-um-ay / regional *erm',
        'Ø','e','r','u','VC-uM-ay / VCM','noun',
        'Tamil erumai, Malayalam eruma and Badaga erume independently support e-r-u-m; Tulu and historical Kannada erme and Gondi ermi preserve the rhotic before a nasal after syncope.',
        'Broad full and syncopated comparisons favor earlier r before m. Telugu enumu can result from r nasalization before m, independently compared with inumu iron by PSS83 p.394.',
        '*erum > Telugu enumu involves r>n before a nasal, not movement of r. Kannada/Kodagu emme follows medial syncope and assimilation of rm; Kota im loses r, Toda ɨr loses final nasal material. Each reduces a different part of the full form.',
        'This is a candidate interaction that could remove the target before initial metathesis, but the relative date of nasal assimilation and metathesis is not independently established. No surviving mr/nr onset licenses a concealed-displacement claim. Badaga has both erume and emme; retain those as variation, not a dated sequence. Historical Kannada erme supplies relative support for later assimilation in that language.',
        {'Tamil':('R','erumai','Full root.'),'Malayalam':('R','eruma|erima','Full root with vowel grade.'),'Kota':('O','im','Rhotic loss.'),'Toda':('O','ɨr|ɨ','Final-member loss and vocative shortening.'),'Kannada':('O','emme','rm assimilation.'),'Kodagu':('O','emme','Same.'),'Tulu':('R','erme','Medial vowel syncope preserves order.'),'Telugu':('O','enumu|enu|enupa|enu pōtu|enu peṇṭi','r nasalization and compound truncation.'),'Gondi':('R','hermi|ermi|ermī|armī|aṛmi|arm','Prothesis/vowel grades, r remains after V.'),'Badaga':('O','erume|emme','Full and assimilated variants.'),'markodi':('R','eruma','Full form.'),'pampa':('R','erme','Historical Kannada retains r before m.')},
        input_confidence='high',references='DEDR816; PSS83 p.394 *r>n before nasal',boundary='High-u and nasal extension independently supported; later compounds do not define the proto-root.',mechanism='Nasalization/assimilation and segment loss, no proven initial metathesis.')
    tokens('d816','Badaga',R='erume',O='emme')

    add('d817','red/dark colour; wild dog','*er-Vc; related *er-om/*er-uv',
        'Ø','e/i','r','i/u/unknown','VC-VC / VC-VM#dog','noun/adjective',
        'Tamil eruvai blood, Kannada ere colour, Parji iric netta and Gondi erom/erm dog compounds independently establish vowel-first order. Exact -Vc and -Vm formations are distinct.',
        'The matching Parji iric dog formation strengthens the comparison with Telugu rēcu beyond using colour semantics alone. Gondi rasi/rac dog stems reverse initial order relative to full erm/erom variants but differ in suffix.',
        '*er-Vc > *rēc > Telugu rēcu is plausible displacement with contraction; Parji iric supplies a full high-i formation but does not uniquely justify e versus i in the shared input. Gondi rac/rasi and Gadaba rēs may share or borrow the displaced dog adjective. Kolami resn a·te reflects compound boundary res#na·te, not root-final n.',
        'Agricultural/hunting vocabulary may diffuse between Telugu, Gondi and central languages; identical compound meaning is compatible with inherited formation or calquing/borrowing. Do not label every central r form an independent innovation. Gondi ce is an editorial cross-reference to red1931, not a dog root. Badaga red-fruit comparison supports colour association only, not the precise dog suffix.',
        {'Tamil':('R','eruvai','Full blood/colour noun.'),'Kannada':('R','ere','Full colour stem.'),'Telugu':('D','rēcu|rēcu-kukka','Displaced colour/dog stem.'),'Gondi':('M','erom nay|erm ney|aṛm nay|arm|rasi ney|rac nāī','Full nasal and displaced-looking s/c formations.'),'Kolami':('A','resn a·te','Compound r stem, contact history unresolved.'),'Parji':('R','iric netta','Full matched dog adjective.'),'Gadaba':('A','rēs nete','Potential contact/displacement outcome.'),'Badaga':('R','erande','Red-fruit association, broader root only.')},
        input_confidence='high for order; low for exact shared V2',references='DEDR817; DEN1 1972 p.402 entry700',boundary='Colour root versus distinct c- and nasal dog modifiers.',confidence='medium')
    tokens('d817','Gondi',R='erom nay|erm ney|aṛm nay|arm',D='rasi ney|rac nāī')

    add('d820','black soil, clay','regional *er-e? + *kaṭṭ clod',
        'Ø','e','r','unknown','VC-V#clod','noun',
        'Kannada ere black soil supplies an independent vowel-r comparison for Telugu compound rē-gaḍa/rē-gaḍi. Only these two languages establish the narrow set, so deeper reconstruction is tentative.',
        'Full Kannada ere and the transparent Telugu clod second member favor vowel-r before Telugu rē, but loan adaptation or a separate long regional noun remains possible.',
        'Conditional *ere#kaḍḍa > *rē#gaḍa yields the Telugu compound through displacement/contraction plus independent compound consonant changes. An original V2 e cannot be equated with inherited a or i without additional comparison.',
        'Count as medium-confidence regional displacement, outside strict V2 prediction tests. The DEDR entry was split from oldDED700, shared with the red/dog material now817; a common colour/soil root is plausible but not proven and should be a sensitivity merge. Root-gaḍa is not the source of the moved r.',
        {'Kannada':('R','ere','Full soil noun.'),'Telugu':('D','rē-gaḍa|rē-gaḍi','Long r-initial first member; clod compound independent.')},
        input_confidence='medium for regional order; low for V2',references='DEDR820; original SQL rows9967–9968',boundary='Soil plus clod compound; suffix vowel in first member unresolved.')

    add('d822','worm, bait','*ir/er-ay; regional *eṟ-a',
        'Ø','i/e','r/ṟ','a/ay','VC-ay','noun',
        'Tamil irai, Malayalam ira, Kannada/Kodagu ere and Telugu eṟa independently support a short vowel followed by a rhotic/alveolar and a low-vowel formation.',
        'Agreement across southern and Gondi branches favors V-r order; Telugu eṟṟa is a strengthened variant rather than evidence that every input was geminate.',
        '*ir-ay > ere/eṟa follows regional vowel changes without initial displacement. Telugu eṟṟa strengthens the medial consonant. Gondi eṛe puṛuk and Kodagu ere puḷu add independently recognizable worm nouns.',
        'A low-a nominal retention counterexample to unrestricted application; do not exclude it simply because it lacks a metathesized variant. Geminate Telugu eṟṟa does not erase the singleton eṟa or the comparative singleton evidence. Relationship to general bait/prey-root material needs further semantic comparison but is not assumed.',
        {'Tamil':('R','irai','Full low-vowel formation.'),'Malayalam':('R','ira','Same.'),'Kannada':('R','ere','Expected ay/e correspondence.'),'Kodagu':('R','ere|ere puḷu','Simplex and compound.'),'Tulu':('R','eru','Different final vowel.'),'Telugu':('R','eṟa|eṟṟa','Singleton and strengthened alternatives.'),'Gondi':('R','erad|eṛe puṛuk','Full root/compound.')},
        input_confidence='high for order and low-vowel root',references='DEDR822 p.80',boundary='Low-vowel nominal formation independently established; later gemination is not an input-based exclusion.')

    add('d826','branch, twig','regional *ir-k / *eŋk / *ekk; Telugu comparison queried',
        'Ø','i/e','r/ŋ/kk','unknown','VC-C / VCC','noun',
        'Kota irg places r before a velar, while Kannada ege/eŋkli, Tulu eggɛ/eggelɯ and Koraga eŋkili motivate other cluster formations. There is no independently agreed full *ir-Vv input for Telugu rivva.',
        'Kota can support a vowel-initial rhotic input, but lateral/nasal/velar comparisons do not uniquely establish the same root or exact derivative as Telugu rivva/rivaṭa.',
        'If related, *ir-Vk/w > *ri-kk/vv could involve displacement and velar-labial development, but each step needs independent evidence. Alternatively the Telugu twig noun is a separate root; DEDR explicitly prefixes its comparison with a question mark.',
        'The parser suppresses the source question mark before Telugu, creating spurious certainty. Keep Telugu A, not a short-vowel metathesis counterexample or positive. Needed: early Telugu spelling, velar/labial correspondence and fuller cognates; Kota irg alone cannot justify the whole proposed chain.',
        {'Kota':('R','irg','V-r-velar order.'),'Kannada':('A','ege|eŋkli','Medial cluster relationship unresolved.'),'Tulu':('A','eggɛ|eggelɯ','Velar/lateral structure differs.'),'Koraga':('A','eŋkili','Nasal/velar/lateral structure.'),'Telugu':('A','rivva|rivaṭa','Source explicitly questionable cognacy.')},
        c2_structure='cluster/uncertain',input_confidence='low',references='DEDR826 p.81 directly read; source ?Te.',eligibility='questionable-cognacy',boundary='No identical full derivative reconstructed.',mechanism='Unresolved cognacy and cluster history.')

    add('d827','chest, heart, courage','regional *ed-V; *erd-V alternative',
        'Ø','e','d/rd?','a/unknown','VC-V / VCC-V','noun',
        'Kota ed, Toda eθy, Kannada ede/edde/erde, Tulu ede and Telugu eda establish initial e followed by a coronal. Kannada r-containing variant alone cannot establish an original r for the entire set.',
        'Vowel-before-coronal order is stable; Telugu eda/eḍæda and Konda eduṟam do not move an apical to the initial position.',
        '*edV > eda/ede and strengthened edda/eḍḍa retain order. Konda eduṟam and Parji edram/edrom may contain an r-formation; Kannada erde could preserve a cluster or add r, with no unique direction yet.',
        'Coronal identity and singleton/cluster reconstruction remain uncertain; this is a retained-order comparison but not a decisive test of a specifically *ṭ or *r law. Telugu eḍæda shows additional syllabic material; do not count its repeated coronal as a second root. No plausible initial metathesis in this set.',
        {'Kota':('R','ed|ed ma·r','Root and compound.'),'Toda':('R','eθy|eQy','Coronal fricative reflex.'),'Kannada':('R','ede|edde|erde|edegāṟa','Singleton, geminate and rhotic variant.'),'Tulu':('R','ede','Full noun.'),'Telugu':('R','eda|eḍæda|eḍḍa','Strength and formation variation.'),'Konda':('R','eduṟam ( -ku)','Expanded formation.'),'Parji':('R','edram|edrom','r-containing expansion with syncope.'),'Badaga':('R','ede','Full root.')},
        c2_structure='singleton/cluster uncertain',input_confidence='medium for order; low for exact input',references='DEDR827 p.81 directly read',eligibility='input-uncertain-control',boundary='Regional coronal root, exact r formation uncertain.')

    add('d829','sunshine, shine','*el; *il-a-k/ŋk',
        'Ø','e/i','l','zero/a','VC free root / VC-a-K/NC','noun/verb',
        'Tamil el and Malayalam el independently attest a short closed light noun; ilaŋku/ilaku supplies low-a verbal extensions. Telugu elamu is a different low-a labial extension.',
        'All independent southern forms retain vowel before l. A nasal *en-ṯu head belongs to a distinct connected sun/day comparison, not proof of nasal input for every shine formation.',
        '*el > el retains the free root; *il-aŋk > ilaŋku and Telugu *el-am > elamu retain the expanded order. Strengthened ella/elli has its own derivational history.',
        'Separate bare root from low-a extensions in prediction tests. Telugu elamu is a useful retained vowel-initial lateral comparison, but the exact shared -am extension lacks independent support here. Prakrit alla day is a queried contact comparison and provides no additional Dravidian vote.',
        {'Tamil':('R','el|elli|ellai|ilaku|ilaŋku','Bare and expanded formations.'),'Malayalam':('R','el|ella|ilakuka|ilaŋkuka','Same distinctions.'),'Telugu':('R','elamu','Retained low-a labial extension.')},
        input_confidence='high for root; medium for shared formation',references='DEDR829 p.81 directly read',boundary='Free noun and separately extended verbs; no outcome-selected lexical class.')

    add('d832','joy, enliven','regional *el-ar / *el-ay',
        'Ø','e','l','a','VC-ar / VC-ay','noun/verb',
        'Kannada elarcu and Telugu elarucu/elarupu independently support e-l-a-r; Telugu elayu/elami has related non-r extensions.',
        'The two languages agree on initial vowel-l order, with no consonant-initial alternative attested in the reviewed set.',
        '*el-ar > elarcu/elarucu retains order; syncope in Kannada elarcu creates a later r-c cluster. Telugu elayincu contains productive causative material and is not a separate root vote.',
        'Regional cognacy is plausible but contact between Kannada and Telugu cannot be excluded from the forms alone. This independently low-a lateral formation remains a retained comparison. The relation to shine829 or other delight roots is a possible family merge, not established by semantic similarity alone.',
        {'Kannada':('R','elarcu','Low-a extended root.'),'Telugu':('R','elarucu|elarupu|elayu|elami|elayincu','Retained formations and causative.')},
        input_confidence='high regional order; medium inheritance',references='DEDR832 p.81 directly read',boundary='Shared -ar formation independent of the metathesis outcome.')

    add('d833','rat, mouse','*el-i; regional *el-i/u-k',
        'Ø','e/i','l','i/u','VC-i / VC-iK','noun',
        'Tamil/Malayalam eli and Kannada/Tulu eli/ili establish a high-i root; Telugu elika/eluka and Konda/Kolami elka share a velar extension, with high vowel versus syncope.',
        'Broad southern and central vowel-first evidence establishes e/i before l independently of Telugu. Brahui hal keeps the vowel before l after initial h addition and vowel change.',
        '*eli > eli/ili retains order. *el-i-k > elika/eluka or elka via medial syncope retains V-l; Gondi elli/allī and Naiki elli add strength/quantity history. Toda is̱y and Kota eyj reflect local lateral changes. Gadaba sirel is small+rat, not a root-initial s-l displacement.',
        'A high-vowel noun control with extensive independent comparison. Geminate Gondi/Naiki cannot be projected onto all branches when singleton southern evidence is broad. No Kui/Kuvi attestation occurs in this group, so absence of a eastern metathesized rat form is missing data, not retention. Brahui hal requires prothesis/vowel history but no initial liquid transfer.',
        {'Tamil':('R','eli','High-i noun.'),'Malayalam':('R','eli','Same.'),'Kota':('R','eyj','Local lateral development.'),'Toda':('R','is̱y','Local fricativization.'),'Kannada':('R','eli|ili','Vowel grades.'),'Kodagu':('R','eli','Full noun.'),'Tulu':('R','eli|ili','Same.'),'Telugu':('R','elika|eluka|ciṭṭ-eluka','Velar formation and small-rat compound.'),'Gondi':('R','allī ( alk)|allī|elli|ellu','Dialect quantity/strength variants.'),'Konda':('R','elka','Velar extension with syncope.'),'Kolami':('R','elka','Same.'),'Naikri':('R','elka','Same.'),'Naiki':('R','elli ( -g)','Strong lateral and plural.'),'Parji':('R','el ( elkul)','Bare root and plural.'),'Gadaba':('R','sirel','Small-rat compound.'),'Brahui':('R','hal','h-prothesis and vowel change.'),'Badaga':('R','ili|ilimari|hebbili','Root and mouse/big-rat compounds.')},
        input_confidence='high',confidence='high',references='DEDR833 p.81 directly read',boundary='High-i root, separate velar expansion and transparent compounds.')

    add('d835','voice, noise, tune','regional *el-i/u-Nk / *il-i-Nk',
        'Ø','e/i','l','i/u','VC-i/u-NK','noun/verb',
        'Telugu elũgu/elĩgincu and independently Parji iluŋg establish vowel-l-high-vowel-nasal-velar order. Parji was incorrectly labeled Telugu in the corpus and is restored from DEDR p.81.',
        'Independent central Parji full form prevents reasoning solely from Telugu. Gondi lēng/lēŋgi and Konda līŋ reverse initial order relative to the shared full formation; differing ē/ī needs its own vocalism analysis.',
        'Conditional *el-iŋ > *lēŋ or *il-iŋ > *līŋ gives eastern displacement/contraction; source variable i/e/u prevents a single secure V2-quality prediction. Gadaba lēng may be borrowed from a displaced Gondi-like form.',
        'The high-vowel suffix is independently attested but exactly matching first-vowel grade is not. Do not use long ē to invent low a. Koraga elkiri weep is explicitly queried and absent from parsed lexical evidence; no independent voice vote is assigned to it. Gondi dialect duplicates remain one family observation.',
        {'Telugu':('R','elũgu|elĩgincu|elũgincu|elũgiccu','Full noun and causatives.'),'Parji':('R','iluŋg','Source-corrected independent full form.'),'Gondi':('D','lēng|lēŋ|lēŋgi|lēŋg|lēŋgu','Displaced voice stem across dialects.'),'Konda':('D','līŋ','Displaced high-vowel form.'),'Gadaba':('A','lēng','Tune noun could be inherited displacement or regional loan.')},
        input_confidence='high for order; medium for vowel grades',references='DEDR835 p.81 directly read',boundary='Same nasal velar noun formation; causatives nested under root, not separate votes.')

    add('d839','bone','*el-u-mp / *el-u-ŋk; regional *el-mu-ka?',
        'Ø','e','l','u','VC-u-MP / VC-u-NK','noun',
        'Tamil elumpu, Malayalam elumpu/eluŋku, Kodagu elɨmbɨ and Kannada elubu/elugu independently establish e-l with high-u nasal/labial or velar extensions.',
        'The lateral precedes the nasal/labial in fuller forms; Tamil eṉpu and Telugu emmu show medial assimilation rather than evidence for an original initial m.',
        '*elump > *elmp > emmu and extended emuka/emmuka plausibly involve medial syncope/assimilation plus velar nominal material. Kannada emike/emake provides an independent parallel. Telugu makkelu bones may involve resegmentation/analogy, aphaeresis or internal rearrangement of an extended plural; its exact input is not fixed.',
        'Do not label makkelu a secure initial-l metathesis: its initial m is not the reconstructed l and an l persists later. Recovering *emukalu or *elmukalu and dated intermediate forms would distinguish aphaeresis plus analogy from consonant transposition. Toda complex spellings preserve local lateral fricative/allophonic notation, not differing metathesis events. Sanskrit/BHS monument terms are contact comparisons, not roots for this denominator.',
        {'Tamil':('O','elumpu|eṉpu|eṟpu-ccaṭṭakam','Full root versus medial assimilation/cluster changes.'),'Malayalam':('O','elumpu|eluŋku|eluvu|elpu|ellu','Full and syncopated/assimilated variants.'),'Kota':('R','elv','V-l retained with syncope.'),'Toda':('R','eł̣f|e ɫ f̣|kɨṯ eł̣f|kɨṯ-eɫf̣|pɨḏ-es̱p','Bone element keeps initial vowel; local consonant outcomes.'),'Kannada':('O','elu|eluvu|elubu|iluvu|elugu|emike|emake','Retained lateral versus assimilation in velar nouns.'),'Kodagu':('R','elɨmbɨ','Full formation.'),'Tulu':('R','elu','V-l root retained.'),'Telugu':('A','emmu|emmuka|emuka|makkelu','Medial assimilation and unresolved plural restructuring.'),'Badaga':('R','elu|ilu','Root retained.'),'Koraga':('R','elkaḷi|elkade','Velar extension with V-l order.'),'markodi':('R','ellᵉ','Strengthened root, same order.'),'pampa':('R','elvu','Historical Kannada syncopated form.')},
        input_confidence='high full root; low for makkelu formation',references='DEDR839 p.81 directly read',boundary='Labial and velar extensions independently distinguished; Telugu plural origin unresolved.',mechanism='Medial assimilation and possible plural restructuring; initial displacement not established.')
    tokens('d839','Tamil',R='elumpu|eṟpu-ccaṭṭakam',O='eṉpu')
    tokens('d839','Malayalam',R='elumpu|eluŋku|eluvu|elpu',O='ellu')
    tokens('d839','Kannada',R='elu|eluvu|elubu|iluvu|elugu',O='emike|emake')
    tokens('d839','Telugu',O='emmu|emmuka|emuka',A='makkelu')
