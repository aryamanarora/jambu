"""Retroflex approximant roots; distinguish displacement from loss and derivative sharing."""

def populate(add,tokens):
    add('d686','stroke, rub, anoint','*uẓ-i/v-; long *ū-s anoint series uncertain',
        'Ø','u','ẓ','i/u/unknown','VC-V + labial/palatal extensions','verb',
        'Malayalam uẓiyuka/uẓivu establishes vowel-first ẓ in the stroke family; Kannada ūḍu preserves vowel-first retroflex with long quantity. DEDR separates a stroke/scrape series from a long ū-s anoint series.',
        'Earlier u–ẓ is plausible for the stroke comparison, reinforced by comb d689. Whether the ū-s series reflects earlier ẓ loss or an independent root is not settled by combining the source’s two subentries.',
        'Conditional *uẓ-v > *ẓuvv > ḍuvv > duvvu gives Telugu stroke, sharing the comb formation in d689. *uẓ-u-s > *ẓūs could yield eastern ṛūs; an alternative *ūẓ-s > ūs accounts for vowel-first anoint forms by medial assimilation. ṛūs > ūs through later initial-r loss is another testable concealed-metathesis hypothesis, but requires independent evidence of that initial loss.',
        'Do not assign all ū-s forms a definite retained or concealed-metathesized status: the contrast may predate the proposed event. The exact V2 of Telugu duvvu cannot be inferred from modern u alone. Pengo ṛoh and Kui ṛōsa have an additional vowel-quality problem. Shared Telugu duvvu stroke/comb means d686+d689 form one primary counting family.',
        {'Malayalam':('O','uṛ̆iyuka|uṛ̆ivu|uṛ̆iccil|uyiccil','Retained stroke forms plus medial ẓ loss in Thiyya.'),
         'Kannada':('R','ūḍu','Long vowel retained before apical.'),'Telugu':('D','duvvu','Displaced stroke/comb formation, exact suffix history conditional.'),
         'Kui':('D','ṛūsa (ṛūsi-)|ṛūska (ṛūski-)|ṛōsa (ṛōsi-)','Displaced scrape/stroke series; u/o not collapsed.'),
         'Kuwi':('A',"rūh|lūh'nai|lūspinai|ṛūsp|ṛūh|ūssali|ūh- (ūst-)|ūsp- (-it-)",'Displaced stroke series versus vowel-first anoint/smear series of unresolved deeper relation.'),
         'Pengo':('A','ṛūc- (-c-)|ṛūcpa|ṛūz- (ṛūst-)|ṛoh- (ṛost-)|ūc- (-c-)','Same contrast; ṛoh vowel quality separately unresolved.'),
         'Manda':('D','ṛūhpa','Displaced plaster formation.'),
         'Gondi':('A','ūsānā|ūs|usānā','Vowel-first anoint series; independent root versus loss of earlier ẓ/r unresolved.'),
         'Konda':('A','ūs- (-t-)|ūspa- (-t-)|ūsis|ūspis','Vowel-first anoint and causative/reflexive series; deeper relation unresolved.')},
        family='d686+d689',references='DEDR 686(a,b) p.67 directly checked; compare 689',
        boundary='Source distinguishes two formations/semantic series; they cannot be assigned the same proto-input solely from modern similarity.')
    tokens('d686','Malayalam',R='uṛ̆iyuka|uṛ̆ivu|uṛ̆iccil',O='uyiccil')
    tokens('d686','Kuwi',D="rūh|lūh'nai|lūspinai|ṛūsp|ṛūh",A='ūssali|ūh- (ūst-)|ūsp- (-it-)')
    tokens('d686','Pengo',D='ṛūc- (-c-)|ṛūcpa|ṛūz- (ṛūst-)',A='ṛoh- (ṛost-)|ūc- (-c-)')

    add('d688','plough, root up soil','*uẓ-u; *uẓ-n- verb and *uẓ-kk- noun',
        'Ø','u','ẓ','u/zero','VC-u / VC-n / VC-kk','verb/noun',
        'Tamil/Malayalam uẓu, Kannada uẓ and Central Dravidian ur/uṛ independently support vowel-first approximant root. K03 pp.152–153 distinguishes Telugu nasal plough verb and velar tillage noun from the eastern vowel-final formation.',
        'Independent southern/central order favors u–ẓ. Eastern ṛū and Telugu dunnu/dukki are displaced under the shared root comparison; initial ẓ then has its separate daughter-language reflexes.',
        'K03 derives *uẓ-n > *ẓun(n) > ḍunn > dunnu, and *uẓ-kk > *ẓukk > ḍukk > dukki. Eastern *uẓ-u > *ẓū > ṛū contracts matching vowels. These are distinct independently discussed formations; Telugu short u need not be a shortened reflex of eastern long ū.',
        'Kui ūṛa root up retains vowel first beside ṛūva plough; its semantic/formation split must remain mixed. Gondi lum/lumm root/gore may be displaced but requires approximant-to-l and suffix history, and the gore comparison is explicitly queried. Tulu dappuni/aḍapuni has dialectal initial-vowel loss and a different vowel/root history; source corrections restore those forms from mistaken Kodagu labels. Tamil tunnu and Parji ḍukki are explicit Telugu loans. Agriculture-contact possibilities do not by themselves negate the deep comparative root.',
        {'Tamil':('A','uṛ̆u|uṛ̆avu|uṛ̆atti|uṛ̆akku|tuṉṉu','Retained native formations and explicit Telugu loan.'),
         'Malayalam':('R','uṛ̆uka|uṛ̆ukuka|uṛ̆utuka|uṛ̆avu','Retained root and extensions.'),
         'Kannada':('O','uṛ̆ (uṛ̆t, utt-)|uṛ̆ata|uṛ̆uke|ukke','Retained root/derivatives and medial assimilation.'),
         'Kota':('O','ug- (uṛt-)|ukl|u·v','Paradigmatic and medial cluster changes; initial vowel survives.'),
         'Toda':('O','uṣf- (uṣt-)','Medial approximant/suffix developments; initial vowel survives.'),
         'Kodagu':('R','u·ḷ- (upp-, utt-)','Long initial vowel, paradigmatic medial assimilation.'),
         'Tulu':('A','ūḍuni|hūḍuni|dappuni|aḍapuni|dappu|ura|uralɯ|oralɯ|oraḷɯ','Source-corrected plough series; dappuni may be local aphaeresis, exact cognacy distinct.'),
         'Telugu':('D','dunnu|dunu|dukki','Distinct displaced nasal and velar formations.'),
         'Kolami':('R','ur- (urt-)','Retained inherited plough root.'),'Naikri':('R','ur','Retained root.'),
         'Parji':('A','uṛ|ḍukki','Retained inherited root with explicit Telugu tillage loan.'),'Gadaba':('R','ūḍ','Retained long-vowel plough form.'),
         'Gondi':('A','urānā|uṛdānā|uṛānā (vrittenud-)|uṛ- (vrittenud-)|uḍ- (vrittenud-)|lum|lumm|lumiˀ','Retained plough forms and uncertain initial-l root/gore series.'),
         'Konda':('D','ṛū- (-t-)','Displaced matching-vowel formation.'),'Kui':('M','ṛūva (ṛūt-)|ūṛa (ūṛi-)','Displaced plough versus retained root-with-snout formation.'),
         'Kuwi':('D',"ṛū- (-t-)|lūnai|ruiyali (rū-)|lū'nai|ṛuki",'Displaced plough/root series, dialect and bullock derivative variation retained.'),
         'Pengo':('D','ṛū- (-t-)','Displaced plough formation.'),'Manda':('D','ṛū','Displaced plough formation.'),
         'Kurux':('O','uinā|uynā (ussas)|ugtā','Initial vowel retained with approximant loss/cluster changes.'),'Malto':('O','use','Initial vowel retained, medial consonant development.'),
         'Badaga':('O','ū|hū|ui|uvvama|uddama|uttava','Initial vowel retained, including h-prothetic and archaic derivative variants.')},
        input_confidence='high',confidence='high',references='K03 pp.152–153 example 86; PSS83 p.235 example 781; DEDR 688 p.67 directly checked',
        boundary='Consonantal -n verb, -kk noun and eastern -u formation are explicitly distinguished in the comparative scholarship.')
    tokens('d688','Tamil',R='uṛ̆u|uṛ̆avu|uṛ̆atti|uṛ̆akku',B='tuṉṉu')
    tokens('d688','Kannada',R='uṛ̆ (uṛ̆t, utt-)|uṛ̆ata|uṛ̆uke',O='ukke')
    tokens('d688','Tulu',R='ūḍuni|hūḍuni|ura|uralɯ|oralɯ|oraḷɯ',A='dappuni|aḍapuni|dappu')
    tokens('d688','Parji',R='uṛ',B='ḍukki')
    tokens('d688','Gondi',R='urānā|uṛdānā|uṛānā (vrittenud-)|uṛ- (vrittenud-)|uḍ- (vrittenud-)',A='lum|lumm|lumiˀ')
    tokens('d688','Kui',D='ṛūva (ṛūt-)',R='ūṛa (ūṛi-)')

    add('d689','comb, arrange hair','*uẓ-u/v; consonantal labial expansion',
        'Ø','u','ẓ','u/zero','VC-u / VC-v','verb/noun',
        'Tamil uẓu, Parji uṛ/uṛv and Gadaba uḍuv/uṛv independently support earlier vowel–approximant order and a labial extension. Gondi uṛ/ūs corroborates the root; Tamil uḷar is explicitly queried.',
        'Agreement of SD I and Central Dravidian supports u–ẓ independently of Telugu. Telugu duvvu and eastern ḍūs/ṛūc are innovative under the hair-arranging comparison.',
        '*uẓ-v > *ẓuvv > ḍuvv > duvvu, with labial strengthening and later initial ḍ>d, gives Telugu comb. Konda ḍūs and Kuvi ṛūc reflect different coronal extensions and possibly vowel contraction. Kodagu ū-k and Naiki ū instead lose the medial approximant while keeping the vowel first.',
        'The identical Telugu stroke duvvu in d686 is counted in the same primary family. Gondi Koya dus might be borrowed from a neighboring displaced language or reflect a local innovation; root and suffix history do not decide it yet. Tulu dūbina is a possible Telugu-area loan or local displacement, while urvaṇe retains order. Tamil uḷar does not establish a second lateral root without further evidence.',
        {'Tamil':('A','uṛ̆u|uḷar','Secure approximant root and queried lateral extension.'),
         'Kota':('O','ug a·ṭ- (a·c-)','Medial approximant change in hair-cleaning construction.'),'Kodagu':('O','u·k- (u·ki-)','Medial loss/cluster change and lengthening.'),
         'Tulu':('A','urvaṇe|uraṇɛ|dūbina','Retained comb-tool forms and uncertain consonant-first noun.'),
         'Telugu':('D','duvvu|duvvena','Displaced verb and derived tool, one root.'),
         'Gondi':('A','uṛ|ūs|uccānā|dus','Retained or medially assimilated forms alongside uncertain displaced Koya form.'),
         'Konda':('D','ḍūs|ḍūsay ā','Displaced comb verb and reflexive construction.'),
         'Kuwi':('D','rūssali|rūca|ṛūca|lūca','Displaced comb/hair series with dialect liquid variants.'),
         'Naiki':('O','ū','Medial consonant loss and lengthening.'),'Parji':('R','uṛ|uṛv','Vowel-first root and labial expansion.'),
         'Gadaba':('R','uḍuv|uṛv|uḍv','Vowel-first labial formations.'),'Koraga':('O','uyyali','Medial approximant-to-glide development, initial vowel retained.')},
        family='d686+d689',input_confidence='high',references='DEDR 689 p.67 directly checked; comparison with stroke d686',
        boundary='Labial expansion independently preserved in Parji/Gadaba; comb-tool suffix not counted as another root.')
    tokens('d689','Tamil',R='uṛ̆u',A='uḷar')
    tokens('d689','Tulu',R='urvaṇe|uraṇɛ',A='dūbina')
    tokens('d689','Gondi',R='uṛ',O='ūs|uccānā',A='dus')

    add('d690','black gram','*uẓ-unt- / *uẓ-untu',
        'Ø','u','ẓ','u','VC-u-NT','noun',
        'Tamil uẓuntu, Malayalam uẓunnu and Kolami urunde preserve vowel–approximant–vowel–nasal-stop order. Kannada urdu/uddu supplies the intermediate medial cluster and its assimilated outcome.',
        'Independent full southern and central forms favor an earlier initial vowel; Telugu uddulu lacks the medial approximant because of cluster reduction, not initial promotion.',
        '*uẓ-unt > *ur-nd > *ur-d > udd, with nasal/stop simplification and assimilation, is a schematic route to Telugu uddulu. Exact sequencing of nasal loss and r assimilation may differ; Kannada urdu : uddu directly supports the latter step.',
        'This same-u comparison retains the initial vowel despite the shared approximant found in displaced comb/tiger. Crop-name borrowing can spread either full or reduced forms, so branch distribution cannot by itself date each sound change. Marathi/Prakrit urad names are contact comparisons, not independent evidence for Dravidian metathesis.',
        {'Tamil':('R','uṛ̆untu','Full u-vowel formation.'),'Malayalam':('R','uṛ̆unnu','Vowel and approximant retained, nasal cluster altered.'),
         'Kannada':('O','urdu|uddu','Retained medial rhotic and assimilated variant.'),'Tulu':('R','urdu','Medial cluster, initial vowel retained.'),
         'Telugu':('O','uddulu','Medial assimilation, not initial displacement.'),'Kolami':('R','urunde','Fuller nasal formation.'),
         'Naikri':('R','urndaḷ','Medial syncope; plural ending does not add root evidence.'),'Badaga':('O','uḷundu|uddu','Full and medially reduced regional variants.')},
        input_confidence='high',references='DEDR 690 p.67 directly checked; K03 *uẓ-untu reconstruction',
        boundary='Nasal-stop crop-name formation independently matched.',mechanism='Medial approximant/cluster assimilation, with contact chronology unresolved.')
    tokens('d690','Kannada',R='urdu',O='uddu')
    tokens('d690','Badaga',R='uḷundu',O='uddu')

    add('d692','tiger, panther','*uẓ-uv-ay / *uẓ-v-',
        'Ø','u','ẓ','u/zero','VC-u-v-ay / VC-v','noun',
        'Tamil uẓuvai supplies a vowel-first approximant plus labial big-cat name. Gondi ḍuvval/ḍūāl and Telugu duvvu support the related labial formation but are not additional unshifted witnesses.',
        'Vowel-first ancestry is supported by the established comparative approximant correspondence and the Tamil form, but only one unshifted lexical witness survives here; direction confidence is lower than in comb/plough.',
        'K03 p.162 gives *uẓ-(u)-w > *ẓu-ww > ḍuww > duvvu. Kolami/Parji ḍū can preserve an older borrowed ḍ-initial stem with later labial loss/contraction. Gondi quantity and labial variation needs separate dialect history.',
        'K03 and PSS83 explicitly diagnose Kolami/Parji Telugu loans; their retained ḍ is evidence about relative borrowing chronology, not independent metathesis. Gondi ḍuhkyā/ḍuhkiak and Gadaba ḍuccā wolf are queried in DEDR and need separate cognacy. The identical Tamil fish name d693 is not merged on homophony alone.',
        {'Tamil':('R','uṛ̆uvai','Only full unshifted lexical witness.'),'Telugu':('D','duvvu','Displaced labial formation.'),
         'Kolami':('B','duva|ḍū','Published Telugu-loan diagnosis.'),'Parji':('B','ḍū ( ḍuvul)','Published Telugu-loan diagnosis.'),
         'Gondi':('A','ḍū|ḍūāl|ḍuvvāl|ḍuvvu|ḍuv ( ḍūk)|duvāl|ḍuhkyā|ḍuhkiak','Probable displaced big-cat forms plus queried wolf/leopard velar forms.')},
        references='K03 p.162; PSS83 p.235 example 782; DEDR 692 p.68 directly checked',
        boundary='Labial big-cat formation; Tamil -ay and Gondi -al expansions not assumed identical without argument.')
    tokens('d692','Gondi',D='ḍū|ḍūāl|ḍuvvāl|ḍuvvu|ḍuv ( ḍūk)|duvāl',A='ḍuhkyā|ḍuhkiak')

    add('d693','goby and related fish names','regional *uẓ-uv-ay; Telugu comparison uncertain',
        'Ø','u','ẓ','u','VC-u-v-ay','noun',
        'Tamil uẓuvai/uḷuvai and Malayalam uẓuva support vowel-first approximant/lateral plus labial fish name. Telugu uṇuju has both nasal and palatal consonants in place of the expected sequence.',
        'Southern vowel-first order is secure regionally; Telugu cognacy is not independently secured by the generic fish gloss.',
        'A path *uẓuvay > uṇuju would require ẓ > ṇ and v/y > j with additional vowel changes. No independently established conditions for those steps are supplied here. Initial vowel retention is observed, but a full inherited derivation remains unproved.',
        'This superficially matches the input of tiger d692 and retains the initial vowel, yet cannot be advertised as a decisive sound-law falsifier until its nasal/palatal correspondence is explained. Better species identification, historical Telugu spellings and nearby fish names could distinguish changed cognacy from irregular sound change.',
        {'Tamil':('R','uṛ̆uvai','Vowel-first fish name; uḷuvai is stranded with Latin in raw record.'),
         'Malayalam':('R','uṛ̆uva','Vowel-first fish name.'),'Telugu':('A','uṇuju','Possible cognate with unresolved multiple consonant correspondences.')},
        eligibility='cognacy-or-input-uncertain',input_confidence='medium',references='DEDR 693 p.68 directly checked',
        boundary='Whole fish name; no new suffix selected merely to fix the Telugu outcome.')

    add('d694','spotted deer, stag','*uẓ-up(p)-; southern shorter *uẓ-ay',
        'Ø','u','ẓ','u','VC-u-p(p)','noun',
        'Parji uṛup independently supplies vowel-first approximant with high u and final labial. Tamil uẓai and Tulu ure/uḷe supply shorter related deer names; they do not themselves prove the labial suffix.',
        'Parji’s full labial form and southern vowel-first shorter forms support earlier u–ẓ. Telugu duppi and Konda ḍupi are displaced under the independently supported labial comparison.',
        '*uẓ-up(p) > *ẓup(p) > ḍupp > duppi, or matching-vowel contraction followed by shortening before pp; the short output alone does not decide between these timing alternatives. Gondi luppi/lūpi involves a lateral approximant reflex plus dialectal length/strength variation.',
        'Kannada duppi, Kolami ḍuppi and Gadaba duppi may be regional loans; their donor histories are not established just by matching Telugu. Keep them uncertain in innovation counts. Parji uṛup is a valuable inherited-order control in the same family. Distinct animal suffixes and dialect variants are not extra etyma.',
        {'Tamil':('R','uṛ̆ai','Shorter vowel-first deer name.'),'Malayalam':('R','uṛ̆a-mān|uṛ̆al-mān','Vowel-first deer-compound member.'),
         'Tulu':('R','urɛ|ule|uḷe','Vowel-first liquid variants.'),'Parji':('R','uṛup ( uṛpul)','Independently matched full labial formation.'),
         'Telugu':('D','duppi','Displaced labial formation.'),'Konda':('D','ḍupi','Displaced labial formation.'),
         'Gondi':('D','ḍuppal|duppi|luppi|lūpi','Displaced family with local apical/quantity variation; diffusion remains possible for individual dialect forms.'),
         'Kannada':('A','duppi','Potential Telugu-area loan.'),'Kolami':('A','ḍuppi','Potential Telugu-area loan.'),'Gadaba':('A','ḍuppi|duppi','Potential Telugu-area loans.'),
         'Badaga':('R','ūre','Longer vowel-first deer name, exact quantity history separate.')},
        input_confidence='high',references='DEDR 694 p.68 directly checked; K03 *uẓ-u-pp reconstruction',
        boundary='Labial suffix independently preserved in Parji, unlike an inference from Telugu alone.')

    add('d695','sweep, scrape into heap','regional *ū/uẓ-C; labial, velar and coronal extensions',
        'Ø','u/ū','ẓ','zero/unknown','V(V)C-C','verb/noun',
        'Telugu ūḍucu, Konda ūṛs and Gadaba ūrs support a long-vowel series; Kolami/Naikri uṛp and Gondi uṛp support short-vowel labial formations. No unshifted SD I comparator occurs in this entry.',
        'Widespread vowel before apical establishes regional V–C order, but exact deeper approximant and root quantity are less secure. Source-corrected Kui ḍupka is the consonant-first comparison.',
        'Long *ūẓ-s > ūṛs/ūḍcu retains initial order. Conditional short *uẓ-k-p > *ẓukp > ḍupk gives Kui ḍupka with a separate, morphologically explicit k-p > p-k exchange. Kui rūṭpa is queried and has extra dental/quantity changes.',
        'This does not prove metathesis of an inherited long *ūẓ root: the Kui velar derivative may have a short stem allomorph, but that must be independently demonstrated. Until then its initial development is uncertain. The original source assigns ūṛs to Konda and both ḍupka/rūṭpa to Kui, not Gondi; that correction materially changes the geography.',
        {'Telugu':('R','ūḍucu|ūḍcu|ūrucu|ūrcu|ūḍupu|ūḍpu','Long vowel retained with r/ḍ and epenthesis variation.'),
         'Kolami':('R','uṛp','Short vowel-first labial stem.'),'Naikri':('R','uṛp','Short vowel-first labial stem.'),'Parji':('R','uṛcip- (uṛcit-)','Vowel-first coronal extension.'),
         'Gadaba':('R','ūrs- (ūrus-)','Long initial vowel retained.'),'Gondi':('R','urpānā|uṛp','Vowel-first labial series; r/ṛ source discrepancy explicit.'),
         'Konda':('R','ūṛs- (-t-)','Source-corrected long-vowel retained form.'),
         'Kui':('A','ḍupka|rūṭpa (rūṭt-)','Initial displacement probable for ḍupka but exact input quantity unresolved; rūṭpa explicitly queried.')},
        quantity='mixed/uncertain',references='DEDR 695 p.68 directly checked',
        boundary='Different suffixes and long/short stem series kept explicit; no short allomorph invented as established fact.')

    add('d696','urine, purge, diarrhoea','*ur/ẓ-c-; northern *uṛ-k- extension',
        'Ø','u','r/ẓ','zero','VC-C','noun/verb',
        'Kannada urcu and Tulu urcuni/uḷc preserve a medial liquid before a palatal; Gondi uṛk preserves a retroflex rhotic before a velar. The shared liquid identity and exact suffix relationship remain less certain than vowel-first order.',
        'The full medial clusters support r/liquid before the final stop. Telugu ucca is compatible with medial assimilation, not movement of the liquid to onset.',
        '*ur-c > *ucc > Telugu ucca and Kannada uccu/ucce; Gondi *uṛ-k retains the liquid, while Kota uc and Toda ūc have local consonant/quantity histories.',
        'Do not count medial liquid loss as hidden metathesis when an unchanged initial vowel and retained cluster comparanda provide a simpler account. Urine, purge and diarrhoea may share a root but distinct noun/verb derivations are not independent examples. The r/ẓ reconstruction should remain uncertain until more correspondences settle it.',
        {'Kannada':('O','urcu|uccu|ucce','Retained medial cluster plus assimilated forms.'),'Tulu':('R','urcuni|uḷc|urcāṭa|ūḷiyuni','Vowel-first liquid series, quantity and lateral/rhotic variation.'),
         'Telugu':('O','ucca','Medial assimilation.'),'Kota':('O','uc|uc- (uc-)|ucl','Palatal stems after medial changes.'),
         'Toda':('O','u·c- (u·č-)','Long-vowel medial-change outcome.'),'Kodagu':('O','ucce|ucc-a·ṭ','Assimilated noun and light-verb construction.'),
         'Gondi':('R','uṛk|uṛkānā|urkul|uṛkul|uṛukulu','Vowel-first velar formation with dialect variants.'),
         'Badaga':('O','ucce|ucce aṭtu','Assimilated noun and construction; compounds not extra roots.')},
        references='DEDR 696 p.68 directly checked',boundary='Palatal southern and velar Gondi extensions separately identified.',
        mechanism='Medial liquid assimilation, not initial displacement.')
    tokens('d696','Kannada',R='urcu',O='uccu|ucce')
