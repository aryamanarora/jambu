"""Independently selected u-initial inputs and adjacent nonapical comparisons."""

def populate(add,tokens):
    add('d536','winged termite','*īc-al / *īy-al; Telugu i/u-vowel variants',
        'Ø','ī','c/y','a','VVC-al','noun',
        'Tamil īcal/īyal, Malayalam īyal and Kannada īcal support a long initial vowel and medial palatal/glide, followed by a lateral suffix. Telugu isuḷḷu/usiḷḷu differs in quantity, vowel quality and lateral strengthening.',
        'Southern long ī followed by c/y precedes the later lateral, whereas Telugu has short i/u. The two Telugu variants differ in the order of their vowels, not initial promotion of an apical.',
        'Conditional *īcal > *ical > *isalu > isuḷḷu requires shortening, palatal weakening, rounding and morphological strengthening; this is not a fully demonstrated chain. isuḷḷu versus usiḷḷu is compatible with vowel-order reversal or assimilatory variation. Singular usiḍi and plural usiḷḷu require a separate ḍ/ḷḷ paradigm.',
        'Do not infer the direction of i/u reversal from which variant is listed first. Earlier Telugu attestations or dialect paradigms could distinguish vowel metathesis from rounding/unrounding. DEDR compares fly d533, so conservative sensitivity may group insect-root formations, without assuming full identity.',
        {'Tamil':('R','īcal|īyal','Long-vowel nonapical root variants.'),'Malayalam':('R','īyal','Long-vowel glide form.'),
         'Kannada':('R','īcal','Long-vowel palatal form.'),'Telugu':('A','isuḷḷu|usiḍi ( usiḷḷu)','Noninitial vowel-order and number alternations, not initial apical displacement.')},
        quantity='long',eligibility='other-process-control',references='DEDR 536 p.53 directly checked',
        boundary='Lateral noun formation and singular/plural alternation separate from the palatal root.',mechanism='Possible vowel metathesis or vowel-quality variation; initial-apical rule inapplicable.')

    add('d545','slight, minute','regional *īr',
        'Ø','ī','r','none','VVC free/bound adjective','adjective/noun',
        'Tamil īr/īrmai and Telugu īr independently attest a long initial vowel before rhotic.',
        'Both languages preserve V–r and long quantity; there is no displaced form in this entry.',
        '*īr > īr, with Tamil -mai nominal formation. Telugu īr occurs before sunlight/voice nouns, so compound/attributive behavior is explicit.',
        'Only two languages attest the root here; borrowing or restricted antiquity cannot be excluded from this small set. It is a long-vowel/root-shape control, not a guaranteed Proto-Dravidian negative.',
        {'Tamil':('R','īr|īrmai','Long root preserved.'),'Telugu':('R','īr','Long attributive root preserved.')},
        quantity='long',eligibility='long-root-control',input_confidence='high',references='DEDR 545 p.53 directly checked',
        boundary='No following formative vowel in the root; -mai belongs to a derived Tamil noun.')

    add('d558','be pleased, love; affection','*uk-a / *uv-a; possible Telugu gōmu comparison',
        'Ø','u','k/v','a','VC-a + nominal extensions','verb/noun',
        'Tamil uka/uva and Kota og support a vowel-first root with velar/labial correspondence. Malayalam uvakka and Telugu uvvāyi support a labial series. Kannada ō is compatible with medial consonant loss.',
        'Multiple southern witnesses support vowel before k/v, but DEDR explicitly questions the Telugu gōmu comparison. Its initial g does not establish a historical velar swap.',
        'Tamil uvakai > ōkai is explicitly contraction after medial consonant loss. A hypothetical *uk-am > *kōm > gōmu would require velar displacement and contraction, but the matching -am formation is not independently supplied by this set.',
        'Keep gōmu uncertain instead of creating an exception to the apical condition from a queried cognate. Telugu uvviḷ-ūru compounds retain initial uv; their additional lateral and light-verb material must not be treated as root consonants. Kannada ose and the Kota lover compounds are also queried in the original source.',
        {'Tamil':('O','uka|uva|uvakai|ōkai','Retained root variants plus explicitly derived contraction.'),
         'Malayalam':('O','uvakka|uvappu|uvavi|upavi|ōvi|ōpi','Labial variants and contractions.'),
         'Kota':('R','og- (ogy-)','Vowel-first velar root.'),'Kannada':('A','ō (ōt-)|ose|osage','Long contracted root; queried s-extended joy forms.'),
         'Telugu':('A','uvvāyi|uvviḷ-ūru|uvviḷul-ūru|gōmu','Retained uv series and explicitly queried gōmu.'),
         'Badaga':('A','osage','Shared festival word, regional diffusion/cognacy unresolved.')},
        eligibility='exceptional-nonapical-input',references='DEDR 558 p.55 directly checked',
        boundary='Distinct nominal/compound extensions; no independent common *ukam reconstructed.')
    tokens('d558','Tamil',R='uka|uva|uvakai',O='ōkai')
    tokens('d558','Malayalam',R='uvakka|uvappu|uvavi|upavi',O='ōvi|ōpi')
    tokens('d558','Telugu',R='uvvāyi|uvviḷ-ūru|uvviḷul-ūru',A='gōmu')

    add('d560','sandpaper, toothbrush and related tree names','regional *uk-a / *uv-a; Kannada *og-an-',
        'Ø','u/o','k/v','a','VC-a / VC-a-n','noun',
        'Tamil ukā/uvā, Malayalam uka-maram and Telugu uvva support vowel-first tree-name variants. Kannada ogani/uguni beside gōṇi/gōnu supplies internal initial-order variation with a nasal formation.',
        'Independent vowel-first velar forms favor earlier uk/og in the relevant regional tree-name family; exact cognacy is weakened by several botanical identifications and differing extensions.',
        'Conditional Kannada *og-an > *gōn > gōṇi/gōnu resembles nonapical displacement with contraction. Alternative initial-vowel loss plus lengthening or loan adaptation remains possible. Telugu *uv-a > uvva retains initial order and strengthens the labial.',
        'A Kannada velar case cannot automatically establish the Telugu apical rule. Careya, Dillenia, Salvadora and Aleurites identifications differ in the original source; botanical-name transfer must be evaluated before asserting one inherited etymon. Latin Careya arborea is not a Malayalam lexeme.',
        {'Tamil':('R','ukā|uvā|uvāy|ukai|ukāy|upā|ōmai','Vowel-first tree-name variants; exact phonological relation of ōmai unresolved.'),
         'Malayalam':('R','uka-maram (D. speciosa)|malay-uka','Vowel-first tree-name member; botanical annotation preserved.'),
         'Kannada':('A','ogani|uguni|gōṇi|gōnu','Retained and likely initial-displacement forms, but direction/mechanism and tree identity uncertain.'),
         'Telugu':('R','uvva','Vowel-first labial series.')},
        eligibility='exceptional-nonapical-input',input_confidence='medium',references='DEDR 560 p.55 directly checked',
        boundary='Kannada nasal ending differs from southern bare -a tree name.')
    tokens('d560','Kannada',R='ogani|uguni',A='gōṇi|gōnu')

    add('d562','shed, spill, pour','*uk-u; *uk-ipp / *uk-upp transitive formations',
        'Ø','u','k','u/i','VC-u / VC-V-pp','verb',
        'Tamil uku and Kannada ugu corroborate vowel-first velar root. Tulu ugipu directly supports an expanded transitive formation beside guppuni; Telugu guppu shares the latter consonant-first shape.',
        'Independent southern vowel-first roots and Tulu ugipu favor an earlier initial vowel in the family. Exact cognacy of the formerly separate guppu entry is a published DEDR merger, not established by shape alone.',
        'Possible *uk-upp > *ku-upp > kupp/g upp with contraction, or *ugipp > gipp/gupp by initial loss plus vowel adjustment. Telugu ūcu can reflect a different suffix/cluster development with a surviving initial vowel; it is not the retained exact counterpart of guppu.',
        'The Tulu/ Telugu transitive pair is a serious nonapical comparison, but homogeneous u vowels leave literal exchange versus aphaeresis weakly identifiable. Parji uy/uv can arise through medial velar weakening. A distinct expressive throw verb or contact between Tulu and Telugu remains to rule out; do not settle it by labeling every g-initial form metathesis.',
        {'Tamil':('R','uku|ukuvu','Vowel-first root.'),'Malayalam':('R','ūkka','Long strengthened form retains order.'),
         'Kannada':('R','ugu (okk-)|ugisu','Vowel-first root and causative.'),'Kota':('R','u·c- (u·c-)','Initial vowel retained, palatal suffix/cluster history separate.'),
         'Toda':('O','ux- (uk-)|uf- (ufQ-)|u·c- (u·č-)','Initial vowel retained with distinct medial consonant developments.'),
         'Tulu':('A','ugipu|guppuni','Internal full/initial-loss-or-displacement comparison.'),
         'Telugu':('A','ūcu|guppu','Vowel-first and consonant-first forms have different transitivity/suffix histories.'),
         'Parji':('O','uy|uv','Medial velar weakening; vowel remains first.'),'Malto':('R','ogoṛe|ogoṛtre','Vowel-first expanded tumble/roll stems.'),
         'Koraga':('R','ogi','Vowel-first pour root.')},
        eligibility='exceptional-nonapical-input',references='DEDR 562 p.55 directly checked; DEN1 merger of old DED 1443 into 480',
        boundary='Transitive -pp formation supported by Tulu ugipu; exact i/u formative correspondence remains open.')
    tokens('d562','Tulu',R='ugipu',A='guppuni')
    tokens('d562','Telugu',R='ūcu',A='guppu')

    add('d587','wear clothes; clothing','*uṭ-u-; *uṭ-upp- clothing noun',
        'Ø','u','ṭ','u','VC-u-pp','verb/noun',
        'Tamil uṭu/uṭuppu, Malayalam uṭuppu and Kannada uḍu/uḍupu independently support matching u vowels and a labial clothing formation. Telugu uḍupu directly matches this series.',
        'SD I and Konda/Gondi/Pengo/Manda vowel-first forms agree; no initial apical promotion is necessary even where medial vowels or consonants are lost.',
        '*uṭ-upp > Telugu uḍupu through voicing/lenition, retaining order. Syncope gives Konda uRpa and Pengo uspa; local apical weakening gives Manda uhpa. These histories remove/alter the medial consonant while leaving the initial vowel.',
        'Same-vowel u+u is not sufficient to trigger contraction/displacement: this is a direct counterexample to application of such a blanket rule. Indo-Aryan *ōḍḍh clothing words are linked contact comparisons and do not determine the Dravidian reconstruction. Toda non-Toda dress noun may reflect cultural diffusion and does not add a separate root.',
        {'Tamil':('R','uṭu|uṭuppu|uṭai|uṭukkai','Retained root and distinct nominal forms.'),'Malayalam':('R','uṭukka|uṭuppu|uṭa','Retained root and nouns.'),
         'Kannada':('R','uḍu (uṭṭ-)|uḍupu|uḍapu|uḍuge','Retained order with formative variation.'),'Kodagu':('R','uḍɨ- (uḍɨp- uḍɨt-)|uḍɨpɨ','Retained order.'),
         'Tulu':('R','uḍusrɛ','Retained order.'),'Toda':('R','uḍp','Retained vowel-first dress noun.'),'Telugu':('R','uḍupu','Independently matched same-vowel clothing noun.'),
         'Gondi':('R','urs|uṛsānā|urc|ūhtānā|uhuttānā','Vowel first despite apical weakening and morphological variation.'),
         'Konda':('R','uRpa- (-t-)','Initial vowel retained.'),'Pengo':('R','uspa','Initial vowel retained.'),'Manda':('R','uhpa','Initial vowel retained.'),
         'Gadaba':('R','ūḍ','Long-vowel wear stem retains order.'),'Badaga':('R','udu','Retained wear verb.')},
        input_confidence='high',references='DEDR 587; DEN1 p.401 additions; linked CDIAL 2547 kept separate',
        boundary='Labial clothing noun and transitive paradigm independently visible across branches.')

    add('d588','boil, heat','regional *uṭ-uk- / *uṭ-ik-; deeper *uṭ-V',
        'Ø','u','ṭ','u/i','VC-V-k','verb/noun',
        'Telugu uḍuku/uḍikincu, Gondi uḍk ēru and Kuvi uḍku show vowel-first retroflex-plus-velar heat words; Kurux uṛturnā supports a related vowel-first root with a different extension.',
        'The available roots all retain V–apical order. Gondi/Kuvi may have borrowed the Telugu regional heat word, so they do not independently prove its high second vowel.',
        'Telugu *uḍ-uk > uḍuku; syncope produces uḍk in hot-water compounds. Kurux *uṭ-t > uṛt is a separate derivative/correspondence hypothesis, not a displaced form.',
        'The apparent Tamil udku is actually Keikadi quoted by Hislop and explicitly < Telugu. Keikadi has no resolved research language mapping here; preserve the source observation separately rather than count it as inherited Tamil. Bibliographic fragments parsed as Tamil are excluded.',
        {'Telugu':('R','uḍuku|uḍikincu|uḍikilu|uḍikillu','Retained high-vowel velar formations.'),
         'Gondi':('A','uḍk ēru','Retained order, possible Telugu regional loan.'),'Kuwi':('A','uḍku','Retained order, possible Telugu regional loan.'),
         'Kurux':('R','uṛturnā','Vowel-first related boil root, different extension.')},
        eligibility='core-formation-uncertain',input_confidence='medium',references='DEDR 588; Hislop Keikadi note in source',
        boundary='Velar heat formation regional; causative i versus base u may be morphological.')

    add('d589','hourglass drum','regional *uṭ-ukk-ay',
        'Ø','u','ṭ','u','VC-u-kk-ay','noun',
        'Tamil uṭukkai, Malayalam uṭukka, Tulu uḍuku and Telugu uḍuka independently match vowel-first retroflex with a high-u velar extension.',
        'All forms retain initial vowel and medial apical. Sanskrit huḍukka/huḍukkā cited by DEDR raises contact and ultimate-origin questions; no modern language is assumed the original donor.',
        'Regional *uṭukkay gives uṭukkai/uṭukka/uḍuku/uḍuka through local voicing, degemination and ending changes; no initial displacement is required.',
        'A structural same-vowel control, but antiquity relative to metathesis is not known. Its later kk is distinct from the first singleton ṭ. Do not call the target apical geminate simply because the noun has a geminate later in the word.',
        {'Tamil':('R','uṭukkai','Retained order.'),'Malayalam':('R','uṭukka','Retained order.'),'Tulu':('R','uḍuku','Retained order.'),'Telugu':('R','uḍuka','Retained order.')},
        eligibility='contact-chronology-control',input_confidence='high',references='DEDR 589; Sanskrit huḍukka comparison',
        boundary='Regional instrument noun; deeper morphological segmentation and direction of diffusion unresolved.')

    add('d590','squirrel','regional *uḍ-ut-V',
        'Ø','u','ṭ/ḍ','u','VC-u-t-V','noun',
        'Kannada uḍute and Telugu uḍuta agree on vowel-first uḍu with a dental ending. The comparison with d713 uṟukku is explicitly cross-referenced, not yet established as identical morphology.',
        'Both neighboring languages have the same vowel/apical order; no independent displaced shape is present.',
        'Regional uḍutV > uḍute/uḍuta through final-vowel variation, retaining order.',
        'Two-language distribution permits lexical diffusion. A broader squirrel comparison is needed before asserting Proto-Dravidian antiquity or using this as a decisive inherited exception. Do not manufacture gemination or a low vowel to explain its retention.',
        {'Kannada':('R','uḍute','Retained same-vowel form.'),'Telugu':('R','uḍuta','Retained same-vowel form.')},
        eligibility='regional-control',references='DEDR 590, compare d713',boundary='Whole regional animal name; final dental expansion independently shared.')

    add('d592','monitor lizard','*uṭ-ump-; regional velar and labial formations',
        'Ø','u','ṭ','u','VC-u-mp','noun',
        'Tamil/Malayalam uṭumpu, Kodagu uḍumbɨ and Telugu uḍumu directly support a u-vowel labial-nasal animal name. Central Dravidian uḍug/uṛug has a distinct velar expansion.',
        'Widespread vowel-first names, including Gondi/Konda, support older u–ṭ order independent of Telugu.',
        '*uṭ-ump > Telugu uḍumu involves medial voicing and loss/assimilation of the labial stop after m, without initial displacement. Konda uṟbu and Gondi urpal involve syncope and apical/labial changes; Kolami uḍug is a different suffix formation.',
        'Another same-vowel u+u retention in an independently matched inherited-looking formation. Source identifications include monitor, pangolin and anteater; DEDR itself questions one pangolin meaning. Those zoological uncertainties may affect individual cognacy but cannot erase the stable southern monitor comparison. Naikri h is prothetic; Irula i/u differs while order is retained.',
        {'Tamil':('R','uṭumpu|oṭakkān','Retained order; lizard derivative differs.'),'Malayalam':('R','uṭumpu','Matched nasal-labial formation.'),
         'Kannada':('R','uḍu|uḍa','Shorter retained animal names.'),'Kodagu':('R','uḍumbɨ','Matched nasal-labial formation.'),
         'Tulu':('R','uḍu|oḍu|oḍḍu','Quantity/strength variants retain order.'),'Toda':('R','uḍuxu','Vowel-first Sak. form, source phonetic interpretation uncertain.'),
         'Telugu':('R','uḍumu','Matched nasal-labial formation with medial change.'),
         'Gondi':('R','urpal|urpāl|oṛpal|oṛpali|urrum ( urruhk)','Vowel-first dialect series; zoological gloss variation explicit.'),
         'Konda':('R','urbu|uṟbu','Vowel-first syncope outcome.'),'Kolami':('R','uṛug|uḍug ( uḍgul)','Vowel-first velar formation.'),
         'Naikri':('R','huṛug ( huṛgul)','Prothetic h, root vowel still precedes apical.'),'Parji':('R','uḍu ( uḍul)','Vowel-first shorter noun.'),
         'Badaga':('R','udumbu','Matched monitor-lizard form.'),'Irula':('R','uruga|iruga','Vowel quality variants, same ordering.')},
        input_confidence='high',references='DEDR 592; K03 *uṭ-ump reconstruction',boundary='Southern nasal-labial noun independently matched; central velar expansion separately recorded.')

    add('d593','property; owner, lord','*uṭ-ay-; *uṭ-ay-an human and *uṭ-am property forms',
        'Ø','u','ṭ','a','VC-ay + human/nominal suffixes','noun',
        'Tamil uṭai/uṭaimai/uṭaiyāṉ, Malayalam uṭaya/uṭama, Kannada oḍeya/oḍame and Telugu oḍami/oḍayãḍu independently support the low-ay possession formation.',
        'Several southern languages agree in initial vowel before retroflex; Telugu owner nouns preserve this sequence even with a human ending comparable in function to displaced lord d527.',
        '*uṭ-ay > *oḍay through lowering before a, followed by nominal/human suffixes, gives Telugu oḍayãḍu/oḍayũḍu without initial displacement. *uṭ-am > oḍami/oḍame gives property nouns. Kota oyṛm may reflect glide/apical reordering locally; this does not move the apical before the first vowel.',
        'This directly limits a claim that low-a or human morphology alone determines Telugu application. Kurux ūṇḍrī/ū̃ṛī requires nasal and suffix history and is less secure as the exact same formation. Old Marathi oḍēra is a contact comparison, not evidence for Proto-Dravidian order. Homophonous wear uṭu d587 may be historically related but is not automatically merged.',
        {'Tamil':('R','uṭai|uṭaimai|uṭaiyāṉ|uṭaiyavaṉ','Retained possession and human forms.'),'Malayalam':('R','uṭaya|uṭayatu|uṭayavan|uṭama','Retained order.'),
         'Kannada':('R','oḍeya|oḍame|oḍati|oḍe','Retained lowered forms.'),'Kodagu':('R','oḍeyə|oḍevə','Retained owner/husband forms.'),
         'Tulu':('R','oḍeye|oḍaye|oḍati|oḍave','Retained owner/property forms.'),'Kota':('R','oyṛm|oṛyn','Initial vowel retained; medial glide position varies by formation.'),
         'Toda':('R','vɨṛm','Prothetic v, root vowel still before apical.'),
         'Telugu':('R','oḍami|oḍame|oḍayũḍu|oḍayãḍu|oḍayurālu','Matched low-ay and gendered owner forms retain order.'),
         'Kurux':('A','ū̃ṛī|uṇḍrī|ūṇḍrī','Vowel-first house-mistress noun, exact nasal/suffix ancestry unresolved.'),
         'Badaga':('R','odeya|odave|oḍdame','Retained owner/property series; social titles and toponyms not extra roots.')},
        input_confidence='high',references='DEDR 593; Old Marathi comparison cited there',boundary='Possession -ay and human endings independently supported; no outcome-defined morphological class.')
