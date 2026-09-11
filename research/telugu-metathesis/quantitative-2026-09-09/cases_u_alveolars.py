"""Alveolar inputs: retained low-vowel formations and distinct medial changes."""

def populate(add,tokens):
    add('d707','sleep, recline, bend','*u/oṯ-a-nk-; shorter *u/oṯ-ak-',
        'Ø','u/o','ṟ','a','VC-a-NK / VC-a-K','verb/noun',
        'Tamil uṟaŋku, Malayalam uṟaŋŋuka and Kannada oṟaŋgu/oṟagu independently establish vowel-first alveolar and a low-a expansion. K03 reconstructs *oṯ-a-nku at Proto-South Dravidian level.',
        'The southern full formations and Parji org agree on V before alveolar, with internal syncope in the latter. Telugu oṟagu retains this order; modern Tamil is not the sole basis for direction.',
        '*oṯ-a-nk > oṟaŋg > oṟag gives Telugu recline, with nasal loss separately required. *oṟ-g > ogg is a possible route to Telugu oggu yield. Irula roŋgu can arise by initial-vowel loss; its exact vowel development does not uniquely select literal exchange. Gondi urh/uhr has a distinct medial consonant reversal.',
        'This is a clear independently low-a retained Telugu formation, despite its broad segmental eligibility. The semantic specialization bend/recline versus sleep may matter lexically but is not a deterministic sound condition. Toda v- and Gondi var- are compatible with prothesis, not promotion of the medial alveolar. The offered/given sense of oggu requires semantic history; it is not proof of hidden initial metathesis.',
        {'Tamil':('R','uṟaŋku|uṟaku|uṟakku|uṟakkam','Low-a formations retain initial vowel.'),'Malayalam':('R','uṟaŋŋuka|uṟakkuka|uṟakkam','Same order.'),
         'Kannada':('R','oṟaŋgu|oṟagu|uṟugu','Low/high formative variation independently attested.'),'Kota':('R','org- (orgy-)|ork','Medial syncope retains initial vowel.'),
         'Kodagu':('R','or- (ori-)|orakɨ','Initial vowel retained.'),'Toda':('R','vaṟx- (vaṟxy-)|vaṟ- (vaṟy-)|vaṟk- (vaṟky-)','Prothetic v precedes original vowel; alveolar remains after it.'),
         'Tulu':('R','oraguni|oragɯ|orduni|orda|orva','Initial vowel retained in different formations.'),
         'Telugu':('O','oṟagu|oragu|oṟava|oraguḍu|oragincu|oggu','Retained full forms plus proposed medial assimilation.'),
         'Parji':('R','org','Retained order with medial syncope.'),'Gondi':('R','urŋg|urh- (<i>Voc.</i> 267a)|uhr- (<i>Voc.</i> 267a)|variyānā|varah|varī|varūs','Initial order retained; urh/uhr has separate medial reversal.'),
         'Badaga':('R','oragu','Low-a order retained.'),'Irula':('A','roŋgu','Initial loss or displacement; vowel pathway needs independent history.')},
        input_confidence='high',references='DEDR 707 p.69 directly checked; K03 *oṯ-a-nku reconstruction',
        boundary='Low-a nasal/velar formation independently shared in Tamil, Malayalam, Kannada; Telugu nasal-free derivative has matching low a.')
    tokens('d707','Telugu',R='oṟagu|oragu|oṟava|oraguḍu|oragincu',O='oggu')

    add('d708','rope sling, suspend','*uṯ-i and strengthened *uṯ-C formations',
        'Ø','u','ṟ','i','VC-i / VCC-i','noun/verb',
        'Tamil/Malayalam/Kannada uṟi and Konda uRi establish a vowel-first alveolar with high i. Kannada also has uṭṭi/oṭṭi, independently matching the strengthened Telugu form.',
        'The high-i full forms support older V–alveolar. Telugu ṭṭ is an internal strengthened reflex, not an initial segment that later acquired an epenthetic vowel.',
        'Possible *uṯ-t-i or strengthened *uṯṯ-i > uṭṭi gives the Telugu sling; exact strengthening morphology is unresolved. Parji ut/utip/utka preserves a consonantal base and derivational suffixes, without initial exchange.',
        'Do not use Telugu ṭṭ alone to classify the proto-root as obligatorily geminate: singleton and strengthened formations coexist independently in Kannada. Gadaba uṭṭi is explicitly compared with Telugu but not unambiguously marked borrowed; contact is uncertain. The d570 ukkam comparison is queried and cannot establish a regular velar alternation.',
        {'Tamil':('R','uṟi','Singleton high-i formation.'),'Malayalam':('R','uṟi','Same formation.'),'Kota':('R','ury','Final glide development only.'),
         'Kannada':('O','uṟi|uṭṭi|oṭṭi','Singleton and strengthened formations.'),'Tulu':('R','uri-gejje','Compound first member retains order.'),
         'Telugu':('O','uṭṭi','Strengthened medial apical; initial vowel retained.'),'Konda':('R','uRi','Singleton high-i form.'),
         'Gondi':('O','uṭum|uṭu|uṭi','Medial stop developments, no initial displacement.'),'Naiki':('O','uttu','Medial strengthened stop.'),
         'Parji':('O','ut|uṭ|utka|uṭka|utip- (utit-)|uṭip- (uṭit-)','Stop root and productive derivative series; vowel remains first.'),
         'Gadaba':('A','uṭṭi','Telugu comparison and embedded verb require separate contact analysis.'),'Badaga':('R','uri|urikōlu','Vowel-first root and tool compound.')},
        references='DEDR 708 p.69 directly checked',c2_structure='singleton/strengthened by formation',
        boundary='Strengthening occurs independently in Kannada; its exact morphological source is unresolved.',mechanism='Retention with internal strengthening.')
    tokens('d708','Kannada',R='uṟi',O='uṭṭi|oṭṭi')

    add('d710','be, happen, be fit, join','*uṯ-u; consonantal person/tense/voice derivatives',
        'Ø','u','ṟ','u','VC-u / VC-C','verb',
        'Tamil uṟu, Malayalam uṟuka and Kannada uṟu independently establish short u followed by alveolar and high u. Kannada urt/utt alternation documents internal cluster assimilation.',
        'Southern vowel-first agreement supports earlier u–ṯ; Telugu uṟu directly preserves this order. The unrelated shark reconstruction in the database is excluded.',
        '*uṯ-u > Telugu uṟu/uru retains order. *uṯ-n > *unn > ūn is a possible route to ūnu/ūncu with medial assimilation and later quantity change; the exact stages need historical forms. Kannada uppu and Tulu uppuni/untuni similarly invite consonantal-formation assimilation. Kui ug-b > ubg is a separate morphologically explicit stop reversal.',
        'Do not treat every u-initial derivative as evidence for one invariant suffix. Kui ubga also occurs under butt d706 with a different gloss; its root-level relationship to uṟu is less secure than the local g/b exchange. Koraga ujji has a palatal medial development, not initial metathesis.',
        {'Tamil':('R','uṟu|uṟuttu|uṟuppu|uṟavu|uṟaŋku','Different native formations retain order.'),'Malayalam':('R','uṟuka|uṟayuka|uṟuppu|uṟavu','Initial order retained.'),
         'Kannada':('O','uṟu (urt-, utt-)|uṟisu|uṟe|oṟal|uppu|ūṟu','Retained alveolar and medially assimilated formations.'),'Toda':('R','uṟf- (uṟt-)|ojuṟt- (ojuṟty-)','Retained root, including compound second member.'),
         'Tulu':('O','uppuni|untuni|untāvuni|uppēruni','Medial assimilation proposed; original vowel survives.'),
         'Telugu':('O','uṟu|uru|ūnu|ūncu|ūnucu','Retained alveolar and nasal formations with lengthening.'),
         'Kui':('A','ubga (&lt; ug-b-; ugd-)','Local g-b reversal secure in source; relation to alveolar root uncertain.'),'Koraga':('O','ujji','Medial consonant development; vowel remains first.')},
        input_confidence='high',references='DEDR 710 p.70 directly checked; compare 706 p.69',
        boundary='Independent high-u base; nasal/labial derivatives need morphological reconstruction.',mechanism='Retention and internal assimilation; Kui stop-cluster metathesis is orthogonal.')
    tokens('d710','Telugu',R='uṟu|uru',O='ūnu|ūncu|ūnucu')
    tokens('d710','Kannada',R='uṟu (urt-, utt-)|uṟisu|uṟe|oṟal|ūṟu',O='uppu')

    add('d711','increase, abundance','*uṯ-u; *uṯ-a/u-v derivatives',
        'Ø','u','ṟ','u/a','VC-u / VC-V-v','verb/noun/adjective',
        'Tamil/Malayalam uṟu and Kannada uṟuvu/uṟubu support vowel-first alveolar, high u, and a labial expansion. Low-vowel derivatives also occur independently in Tamil/Kannada.',
        'Agreement of full southern forms establishes V before alveolar. Telugu uravu/uruvu preserves that order rather than requiring restoration after an undocumented initial change.',
        '*uṯ-V-v > Telugu uravu/uruvu with apical merging and suffix-vowel variation. oṟṟu/odde/ommu may represent strengthened or assimilated consonantal formations; exact nasality and labial origin in ommu are not independently demonstrated.',
        'Keep the clear retained forms as evidence even though some other derivatives are uncertain. Homophonous uṟu happen d710 and force d719 are potential semantic-family relationships, not automatic independent roots or automatic mergers. The Pampa form is historical Kannada, not another genealogically independent language.',
        {'Tamil':('R','uṟu|uṟai|uṟuttu','Root and formations retain order.'),'Malayalam':('R','uṟu','Same high-u root.'),
         'Kannada':('R','uṟuvu|uṟubu|uṟube|uṟaḷi|urvu|urme','Full and syncopated derivatives preserve initial vowel.'),'Tulu':('R','urubu|urbi|urbu|urdi','Initial vowel retained.'),
         'Telugu':('A','uṟavu|uravu|uruvu|oṟṟu|odde|ommu','Secure retained alveolar series; deeper strengthened/labial relationships vary in confidence.'),'pampa':('R','uṟu','Historical Kannada witness.')},
        input_confidence='high',references='DEDR 711 p.70 directly checked',boundary='Labial and vowel expansions independently shared; ommu history unresolved.',mechanism='Retention; strengthened/internal-assimilation derivatives uncertain.')
    tokens('d711','Telugu',R='uṟavu|uravu|uruvu',O='oṟṟu|odde',A='ommu')

    add('d712','think, care, heed','*uṯ-u; negative *uṯ-a-k/person endings',
        'Ø','u','ṟ','u/a','VC-u / negative VC-a','verb',
        'Tamil uṟu and historical Kannada uṟade negative independently establish vowel-first alveolar with both positive high-u and negative low-a formations.',
        'Tamil and Kannada agreement supports earlier vowel first; Telugu Kittel examples are specifically negative and retain this order.',
        '*uṯ-a-ka > Telugu uṟaka not minding, and *uṯ-a-person ending > uṟãḍu he does not care, as given inside the lexical record. No initial displacement is required. Exact segmentation of the personal ending remains a grammatical rather than lexical comparison.',
        'Negative forms form an independently motivated grammatical class, but one or several retained roots do not establish a universal negative blocking rule. Compare negative-only uraka d648 and the early destroy paradigm; the exact inherited stem grades must be checked before generalizing. Brahui hunning is only a cross-reference to d727, not an attestation in this entry.',
        {'Tamil':('R','uṟu|uṟuttu','Positive root and causative retain order.'),'pampa':('R','uṟade','Historical Kannada negative retained.'),
         'Telugu':('R','uṟu','Kittel attests only negative uṟaka/uṟãḍu inside this record; do not fabricate an independently attested positive token.')},
        references='DEDR 712 p.70 directly checked; cited BDCG §3.16 n.11 concerns alternative Brahui comparison',input_confidence='high',
        boundary='Negative formation explicitly identified by original source; reconstructed positive is supported independently.',mechanism='Retention in negative formations.')

    add('d713','jump, run away; squirrel','*uṯ-uk(k); *uṯ-tt-ay animal derivative',
        'Ø','u','ṟ','u','VC-u-K / VC-tt-ay','verb/noun',
        'Tamil uṟukku jump independently matches Telugu uṟuku and Konda uRk; Tamil uṟuttai squirrel matches Telugu uṟuta with a distinct coronal animal-name formation.',
        'Full Tamil/Telugu and syncopated Konda/Kuvi all keep initial vowel before alveolar, supporting V-first root without a consonant-initial comparator.',
        '*uṯ-ukk > Telugu uṟuk(u), Konda uRk and Kuvi urk, with medial-vowel loss and suffix-strength changes. Animal *uṯ-tt-ay yields Tamil uṟuttai and Telugu uṟuta after simplification; the exact cluster prehistory remains to be established.',
        'The velar is later than the first singleton apical and does not exclude the root from phonological eligibility. The associated squirrel d590 may be the same family with a strengthened/retroflex root variant; show sensitivity collapse rather than counting two independent animal counterexamples.',
        {'Tamil':('R','uṟukku|uṟuttai','Retained verb and animal formations.'),'Telugu':('R','uṟu|uṟuku|uṟuta','Retained root and derivatives.'),'Konda':('R','uRk','Medial syncope only.'),'Kuwi':('R','urk- (-it-)','Medial syncope; dance meaning requires semantic comparison.')},
        references='DEDR 713 p.70 directly checked; cf. d590',input_confidence='high',boundary='Velar verbal and coronal animal formations independently matched.',mechanism='Retention with internal syncope/cluster changes.')

    add('d718','roar, thunder, lament','*uṯ/ur-um; *u/oṟ-al; labial derivatives',
        'Ø','u/o','ṟ/r','u/a','VC-u-m / VC-a-l / VC-pp','verb/noun',
        'Tamil uṟumu, Malayalam uṟumpuka and Central Dravidian urum support initial u before rhotic and high-u labial formation. Kannada oṟalu independently matches Telugu oṟalu lament with low a and a lateral extension.',
        'Independent full forms favor V-first inputs in each formation. The long ṟōlu lament series is innovative under comparison with oṟalu; the uṟumu thunder series itself retains order in Telugu.',
        '*uṟ-um > Telugu uṟumu retains order, while conditional *oṟ-al > *ṟōl > ṟōlu/rōlu gives a displaced lament derivative. Kui *uṟ-um > *ṟūm > rūma/rūmba combines initial displacement/contraction with labial formation. Telugu roppu/rollu requires consonantal-suffix reconstruction or later shortening, not simply one uniform vowel input.',
        'Expressive sound words can converge independently; do not use their semantic resemblance as decisive cognacy. Kui ṛunja is explicitly queried and has an unexplained nasal-palatal formation. Kannada ṟoppu could be an independent development or a regional loan; Brahui hūrra has an explicit Balochi comparison. Keep these separate from secure retained thunder forms and probable displaced lament forms.',
        {'Tamil':('R','uṟumu|uṟumpu|urumu|urum|uṟukku','Related expressive formations retain initial vowel.'),'Malayalam':('R','uṟumpuka|uṟumpal','Labial thunder/roar formation retained.'),
         'Kannada':('A','oṟalu|oṟal|oṟaḷu|orlu|ṟoppu','Retained lament forms and uncertain initial-r labial form.'),
         'Telugu':('M','uṟumu|oṟalu|ṟōlu|rōlu|roppu|ṟoppu|rollu','Retained thunder/lament and displaced long lament; short labial/lateral formations uncertain.'),
         'Gondi':('R','uram|urum','Vowel-first thunder, dialect vowel variation.'),'Konda':('R','uṟmi- (-t-)|oṟli- (-t-)','Separate high/low formations retain order after syncope.'),
         'Kui':('A','rūma (rūmi-)|rūmba (rūmbi-)|ṛunja (ṛunji-)','Displaced matching-vowel roar; queried thunder form kept separate.'),
         'Kuwi':('R','oṛhali|ōrhinai','Vowel-first groan/squeal forms, quantity history separate.'),'Parji':('R','urum puyil','Thunder in compound.'),'Gadaba':('R','urum','Vowel-first thunder.'),
         'Brahui':('A','hūrra','Balochi comparison; initial h is not promoted medial r.')},
        references='DEDR 718 p.70 directly checked',boundary='Thunder -um and lament -al are independently distinct; expressive convergences and exact short-form suffixes unresolved.')
    tokens('d718','Kannada',R='oṟalu|oṟal|oṟaḷu|orlu',A='ṟoppu')
    tokens('d718','Telugu',R='uṟumu|oṟalu',D='ṟōlu|rōlu',A='roppu|ṟoppu|rollu')
    tokens('d718','Kui',D='rūma (rūmi-)|rūmba (rūmbi-)',A='ṛunja (ṛunji-)')

    add('d719','throw, speed, force','*uṯ-u-b/v; *uṯ-a-v; nasal throwing derivative',
        'Ø','u','ṟ','u/a','VC-u-b / VC-a-v / VC-m','verb/noun',
        'Kannada uṟubu independently supplies vowel-first alveolar with high u and labial expansion. Telugu uravaḍi retains a related low-a speed formation; Konda uṟmi supports a vowel-first nasal throwing derivative.',
        'Kannada and Konda agreement gives evidence for earlier V–alveolar beyond Telugu alone. Telugu ṟuvvu/ruvvu is consonant first under that comparison.',
        'Conditional *uṯ-v > *ṯuvv > ṟuvvu, or *uṯ-uv > *ṯūv with later strengthening/shortening, accounts for Telugu throw; ṟūvu supports investigating a long stage but does not uniquely establish it. Tulu rummuni/rumbu is compatible with initial-vowel loss plus medial assimilation; Konda uṟmi retains initial order.',
        'The exact correspondence between Kannada -ub and Telugu -vv is plausible but does not prove an identical syllabification before change. Kolami ruv may be an early Telugu loan or an independent related displacement; rusi is explicitly ruv+si give and is not a second etymon. Sound-symbolic/semantic relation to abundance d711 and roar d718 deserves sensitivity treatment, not automatic merging.',
        {'Kannada':('R','uṟubu','Independent high-u labial expansion.'),'Telugu':('M','uravaḍi|uravaḍincu|uraḍincu|ṟuvvu|ruvvu|ṟuppu|ṟūvu','Retained speed derivative versus displaced throw series with quantity/strength variation.'),
         'Konda':('R','uṟmi- (-t-)|uṟmis- (-t-)','Nasal throwing formation retains vowel first.'),'Tulu':('A','rummuni|rumbu','Possible local aphaeresis/assimilation, full comparative formation uncertain.'),
         'Kolami':('A','ruv- (ruvt-)|rusi- (rusit-)','Displaced-looking root with unresolved donor history; compound derivation explicit.')},
        references='DEDR 719; DED(N) 617 p.401 for Tulu',boundary='High-u labial and low-a speed formations distinguished independently; exact Telugu precluster vowels unresolved.')
    tokens('d719','Telugu',R='uravaḍi|uravaḍincu|uraḍincu',D='ṟuvvu|ruvvu|ṟuppu|ṟūvu')

    add('d721','firm, steady, support','*u/oṯ-ay; consonantal support derivatives',
        'Ø','u/o','ṟ','a/i','VC-ay / VC-C','verb/adjective/noun',
        'Tamil uṟai, Malayalam uṟayuka/uṟappu and Telugu oṟapu independently support vowel-first alveolar with low-a formation; Tamil uṟuti has a separate high-u nominal suffix.',
        'Southern forms and Kurux ordnā all put the vowel before the apical, supporting V-first ancestry. No initial displaced reflex occurs among reviewed forms.',
        '*uṯ-ay > Tamil uṟai; low-vowel labial derivative > Telugu oṟapu. Telugu uṟidi/uṟiya requires its own suffix and vowel history, while Kurux ordnā has a consonantal support stem. All retain initial V.',
        'Low-a oṟapu is a relevant retained Telugu control; do not remove it merely because firm is not a stereotypical action verb. Cross-reference to ūṉṟu d763 could relate a nasal/long formation, but does not prove this root was originally long.',
        {'Tamil':('R','uṟai|uṟaippu|uṟuti','Different retained formations.'),'Malayalam':('R','uṟayuka|uṟappu|uṟekka|uṟuka|uṟuti','Vowel-first variants.'),'Kota':('R','urv- (urd-)','Consonantal stem remains vowel first.'),
         'Telugu':('R','oṟapu|uṟidi|uṟiya','Low-a and high-i formations retained.'),'Kurux':('R','ordnā','Vowel-first support stem.')},
        references='DEDR 721; cf. d763',input_confidence='high',boundary='Low-ay base and stronger labial formation independently attested; exact personal noun suffix separate.',mechanism='Retention with vowel/suffix developments.')

    add('d722','pungent, acrid','*uṯ-ay; strengthened *uṯ-C-a',
        'Ø','u','ṟ','a','VC-ay / VCC-a','adjective/noun',
        'Tamil uṟai/uṟaippu and Malayalam uṟa establish vowel-first singleton alveolar and low vowel. Telugu oṟṟa independently displays a strengthened apical output.',
        'The southern low-vowel forms establish earlier u–ṯ; Telugu oṟṟa retains the initial vowel, and vaṟṟa has an additional v rather than the apical moving first.',
        'Conditional *uṯ-C-a > oṟṟa with strengthening and vowel lowering; vaṟṟa may have glide prothesis and quality change. The origin/timing of the strengthening needs independent evidence before asserting a geminate input blocked metathesis.',
        'This remains a structural-history uncertainty, not a conveniently defined geminate exception. Historical Telugu and related pungency derivatives would distinguish inherited strengthened stem from later local reinforcement. The o/a alternation is not consonant/vowel exchange.',
        {'Tamil':('R','uṟai|uṟaippu','Singleton base with low-ay formation.'),'Malayalam':('R','uṟa','Singleton low-a form.'),'Telugu':('O','oṟṟa|oṟṟana|oṟṟãdanamu|vaṟṟa','Strengthening and possible prothesis, original vowel before apical retained.')},
        references='DEDR 722',c2_structure='singleton/strengthened-history-uncertain',eligibility='core-formation-uncertain',boundary='Strengthening not independently reconstructed from output alone.',mechanism='Retention with strengthening/prothesis.')

    add('d723','sheath, cover','*u/oṯ-ay','Ø','u/o','ṟ','a','VC-ay','noun',
        'Tamil uṟai, Malayalam uṟa, Kannada oṟe and Kodagu/Tulu ore independently establish vowel-first alveolar plus low-vowel/ay nominal formation.',
        'Agreement across southern languages establishes earlier V–alveolar; Telugu oṟa/oṟṟa retains this initial order with variable medial strengthening.',
        '*uṯ-ay > oṟa in Telugu, with vowel lowering and suffix changes; Kittel oṟṟa has stronger medial apical. Tulu ude changes the medial consonant but keeps the vowel first. Parji/Gadaba ora are explicit Telugu loans.',
        'A useful low-a noun control: the short-vowel singleton history is independently supported and cannot be ruled out just because one Telugu source spells ṟṟ. The two Telugu spellings are source variants, not independent roots. Borrowed Central Dravidian forms cannot count as inherited retention evidence.',
        {'Tamil':('R','uṟai','Low-ay input support.'),'Malayalam':('R','uṟa','Low-a input support.'),'Kannada':('R','oṟe','Same order.'),'Kota':('R','or','Suffix loss retains order.'),'Kodagu':('R','ore','Same order.'),
         'Tulu':('O','ore|ude','Retained rhotic and medial stop variant.'),'Telugu':('R','oṟa|oṟṟa','Initial order retained despite strengthening variation.'),
         'Parji':('B','ora','Explicit Telugu loan.'),'Gadaba':('B','ora','Explicit Telugu loan.')},
        input_confidence='high',references='DEDR 723',boundary='Low nominal formation independently matched across southern languages.',mechanism='Retention with medial strengthening; Central Dravidian loans.')
    tokens('d723','Tulu',R='ore',O='ude')
