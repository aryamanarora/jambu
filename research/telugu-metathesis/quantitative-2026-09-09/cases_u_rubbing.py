"""Rubbing, swelling and neighboring controls, reviewed independently of outcomes."""

def populate(add,tokens):
    add('d665','rub, grind, touchstone; pestle','*ur-ay; *ur-d / *ur-upp and other formations',
        'Ø','u','r','a/u/zero','VC-ay / VC-C / VC-V-pp','verb/noun',
        'Tamil urai, Malayalam urayuka and Kannada ore establish a low-ay formation; Kannada urdu/uddu/ujju independently supplies the medial dental cluster relevant to Telugu ruddu. Labial rubbing formations occur in Tamil/Malayalam, but their precise vowel varies.',
        'Multiple independent full roots support earlier u–r. Telugu orayu retains the low-ay formation while ruddu/rubbu promotes r in other formations; this is not a reversal of the same fully specified stem in every derivative.',
        'K61 p.55 derives ruddu from *ur-d and rubbu from *ur-upp: *ur-d > *ru-dd, and *ur-upp > *ru-pp > rubbu with displacement and strengthening/voicing. *ur-ay > *or-ay > orayu retains order. Kannada urdu > uddu/ujju instead assimilates r medially. Konda rōs can reflect a low-a derivative; Kui rūsa and Kuvi rub require distinct high-vowel/consonantal formations.',
        'Telugu rō̃kali is explicitly questioned and compared alternatively with d672 ulakkai pestle; its r/l ancestry is not solved by the rub root. Kannada rubbu may be inherited displacement or a Telugu loan; Kannada ruddu and Telugu ruttu are explicitly queried in the original source. Kolami/Naikri/Gondi pestle names are explicitly Telugu loans and are excluded from independent innovations. Telugu retained low-a forms remain genuine counterexamples to obligatory application.',
        {'Tamil':('R','urai|uraicu|uraippu|uracu|uriñcu|urāy','Different vowel/voice formations retain order.'),
         'Malayalam':('R','urayuka|urasuka|ura|uravu|urekka|urummuka','Retained low/high derivatives.'),
         'Kannada':('A','ore (orad-)|orasu|urdu|uddu|ujju|rubbu|ruddu','Retained roots, medial assimilation, potential borrowed displacement and queried beat form.'),
         'Kota':('O','orv- (ort-)|orj- (orj-)|uj- (uj-)','Retained roots plus medial r assimilation/loss.'),
         'Toda':('O','varf- (vart-)|ud- (udy-)','Prothesis in first form and medial assimilation in second.'),
         'Kodagu':('O','udd- (uddi-)','Medial rhotic assimilation.'),
         'Tulu':('O','orevuni|urduni|urepuni|uresuni|ujjuni|occuni','Retained roots and medial cluster developments.'),
         'Telugu':('M','ora|orayu|oracu|orapu|orapiḍi|uriyu|ruddu|rubbu|ruttu|rō̃kali','Retained low-ay series, displaced cluster/labial forms, queried pestle and beat comparisons.'),
         'Konda':('D','rōs- (-t-)','Displaced low-vowel touch/rub formation.'),'Kui':('D','rūga- (rūgi-)|rūsa (rūsi-)|rūska (rūski-)|rūseni','Displaced high-vowel series; number morphology distinguished.'),
         'Kuwi':('D','rūbali|rubinai|rubbinai|rub- (-it-)','Displaced smear series with quantity/strength variation.'),
         'Kolami':('B','rubgunḍ|rokāl|rōka','Explicit Telugu loans.'),'Naikri':('B','rōkal','Explicit Telugu loan.'),
         'Gondi':('A','uriyānā|urīsānā|ūc|us|rōkal','Retained powder/scrape formations plus explicit Telugu pestle loan.'),
         'Parji':('O','urc|ujip- (ujit-)','Retained root and medial-assimilated form.'),'Gadaba':('R','urs','Retained wipe root.'),
         'Badaga':('O','orucu|orcu|ujju','Retained and medially assimilated rub verbs.')},
        input_confidence='high',references='DEDR 665 p.64 directly checked; K61 p.55 §1.131 inspected in Google Books; alternative d672',
        boundary='-ay, dental cluster and labial transitive formations independently motivated; possible stone compound separately uncertain.')
    tokens('d665','Telugu',R='ora|orayu|oracu|orapu|orapiḍi|uriyu',D='ruddu|rubbu',A='ruttu|rō̃kali')
    tokens('d665','Kannada',R='ore (orad-)|orasu|urdu',O='uddu|ujju',A='rubbu|ruddu')
    tokens('d665','Gondi',R='uriyānā|urīsānā',O='ūc|us',B='rōkal')
    tokens('d665','Kota',R='orv- (ort-)|orj- (orj-)',O='uj- (uj-)')
    tokens('d665','Toda',R='varf- (vart-)',O='ud- (udy-)')
    tokens('d665','Tulu',R='orevuni|urduni|urepuni|uresuni',O='ujjuni|occuni')
    tokens('d665','Parji',R='urc',O='ujip- (ujit-)')
    tokens('d665','Badaga',R='orucu|orcu',O='ujju')

    add('d666','swell, boil over','*ur-p / *ur-k; long and short *ūr/ur',
        'Ø','u/ū','r','zero/unknown','VC-C / VVC','verb/noun',
        'Kannada urbu/urvu beside ubbu, Tulu urkuni beside ukkuni and Konda/Kui urp independently support medial rhotic-plus-stop clusters. Root quantity alternates and is not fixed by a single proto-head.',
        'Independent retained clusters favor r after u; assimilated labial/velar forms do not require initial promotion of r.',
        '*ur-p > *urb > ubb gives Telugu ubbu and related forms; *ur-k > ukk produces local boil-over forms. Telugu ūru keeps a long rhotic root. ubuku may reflect a labial root plus velar extension rather than direct r-to-b conversion, so its full derivation is separate.',
        'This is a widespread negative for initial displacement and a positive for medial assimilation. Exact Proto-Dravidian quantity and whether all swelling/boiling words descend from one root remain uncertain. Tamil upparam is explicitly Telugu-borrowed. A Manda label was swallowed into a Pengo record; do not count the duplicate Pengo-looking stem as an independent language without source correction.',
        {'Tamil':('O','uppu|uppal|upukku|upparam','Medial-assimilated forms and an explicit Telugu loan.'),
         'Kannada':('O','urbu|urvu|ubbu|ukku','Retained rhotic clusters and assimilated outcomes.'),
         'Tulu':('O','urkuni|urpelɯ|ukkuni|ubbuni','Retained clusters and assimilated outcomes.'),
         'Kota':('O','ub- (uby-)','Labial assimilation.'),'Toda':('O','ub- (uby-)','Labial assimilation.'),'Kodagu':('O','ukk- (ukki-)','Velar assimilation.'),
         'Telugu':('O','ūru|ubbu|ubuku|ubbincu|ubbaramu|uppena|uppoŋgu','Retained long root, medial assimilation and complex derivatives.'),
         'Konda':('O','urp- (-t-)|urpu|ubi- (-t-)','Retained cluster and assimilated swell form.'),'Kui':('R','urpa (urt-)','Retained rhotic cluster.'),
         'Kuwi':('R',"ūrhali|urh'nai",'Retained initial vowel, source quantity varies.'),'Pengo':('R','ur- (-t-)','Retained root; duplicate containing Manda heading not separately counted.'),
         'Kurux':('O','ubkārnā','Labial-velar extension, medial rhotic ancestry conditional.'),'Brahui':('R','ūrēnging|ūringing','Long vowel before r, source initial h fragment separately unresolved.'),
         'Gondi':('A','ukuṛ','Explicit alternative cognacy with d568.'),'Badaga':('O','ubbisu','Labial-assimilated derivative.')},
        quantity='mixed/uncertain',references='DEDR 666',boundary='Rhotic-stop clusters independently attested; quantity and complex derivatives kept unresolved.',
        mechanism='Medial rhotic assimilation, not initial displacement.')
    tokens('d666','Tamil',O='uppu|uppal|upukku',B='upparam')
    tokens('d666','Kannada',R='urbu|urvu',O='ubbu|ukku')
    tokens('d666','Tulu',R='urkuni|urpelɯ',O='ukkuni|ubbuni')
    tokens('d666','Telugu',R='ūru',O='ubbu|ubbincu|ubbaramu|uppena|uppoŋgu',A='ubuku')
    tokens('d666','Konda',R='urp- (-t-)|urpu',O='ubi- (-t-)')

    add('d675','Crataeva tree','regional *ulimiri',
        'Ø','u','l','i','VC-i-C-i-C-i','noun',
        'Kannada ulimiri and Telugu ulimiri/ulimiḍi share the full regional plant name with high i after l.',
        'Both languages retain u before l; internal final r/ḍ variation does not reverse the initial sequence.',
        'Regional ulimiri > Telugu ulimiri/ulimiḍi, requiring a separate final consonant correspondence or analogical variant; no initial displacement.',
        'Only two neighboring languages and one botanical name are available; diffusion and deeper segmentation remain open. The Latin Crataeva tapia record is a gloss, not another Kannada reflex.',
        {'Kannada':('R','ulimiri','Retained high-vowel form.'),'Telugu':('R','ulimiri|ulimiḍi','Retained order; later r/ḍ variant.')},
        eligibility='regional-control',input_confidence='medium',references='DEDR 675',boundary='Opaque regional plant name; no securely identified morpheme boundaries.')

    add('d676','hilsa fish','regional *ullam / *uḷḷam',
        'Ø','u','ll/ḷḷ','a','VCC-am + fish compound','noun',
        'Tamil ullam/uḷḷam, Malayalam ullam and Telugu ullam-cēpa independently show a geminate lateral fish name.',
        'All lexical forms preserve vowel before lateral; no initial displacement in this entry.',
        'Regional ullam combines with Telugu cēpa fish; ullāku-cēpa has a different long-vowel velar expansion, not a reversal.',
        'A clear geminate structural control, with unknown diffusion chronology. The uncertain species glosses and lexicalized compound variants do not add independent roots. The later velar extension needs its own derivation.',
        {'Tamil':('R','ullam|uḷḷam','Geminate lateral variants.'),'Malayalam':('R','ullam','Geminate retained form.'),
         'Telugu':('R','ullam-cēpa|ullāku-cēpa|ullākũjē̃pa','Geminate first compound member; nominal extensions and sandhi kept explicit.')},
        c2_structure='geminate',eligibility='geminate-contact-control',input_confidence='high',references='DEDR 676',
        boundary='Fish compound boundary occurs after the eligible first member; the first lateral itself is geminate.')
