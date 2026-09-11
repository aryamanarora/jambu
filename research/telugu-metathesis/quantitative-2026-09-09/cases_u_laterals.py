"""Lateral inputs, including independently supported geminate controls."""

def populate(add,tokens):
    add('d672','pestle','regional *ul-akk-ay; contact comparison with Indo-Aryan ulūkhala',
        'Ø','u','l','a','VC-a-kk-ay','noun',
        'Tamil ulakkai, Malayalam ulakka, Kannada olake and Kodagu oḷake establish vowel-first lateral plus velar tool name. The linked Indo-Aryan mortar words form a separate comparison, not many independent Dravidian witnesses.',
        'Vowel-first order is supported within the southern comparison. The relationship to Indo-Aryan ulūkhala and Telugu rō̃kali (queried under d665) does not establish a uniquely recoverable pan-Dravidian input.',
        '*ulakkay > olake/oḷake includes lowering and daughter-language suffix changes; Kannada onake/onike has lateral-to-nasal variation. Kota elk has syncope. Toda vas̱k requires initial glide and lateral/velar developments; no initial promotion of l is visible.',
        'No Telugu record is linked here. Deriving Telugu rō̃kali from this rather than rub d665 would require an independently justified l/r correspondence and nasal origin; preserve both hypotheses. Kuruba alke is wrongly labeled Malayalam in the corpus. Do not count either the large Indo-Aryan contact fan-out or pestle derivatives as independent Dravidian etyma.',
        {'Tamil':('R','ulakkai','Vowel-first low-a velar formation.'),'Malayalam':('R','ulakka','Same order.'),
         'Kannada':('O','olake|onake|onike','Retained lateral and nasal variants.'),'Kodagu':('R','oḷake','Retained order with retroflex lateral.'),
         'Kota':('R','elk','Syncope retains vowel before lateral.'),'Toda':('O','vas̱k|vask','Initial glide and internal developments; no promoted l.'),
         'Badaga':('O','oṇake','Nasal correspondence, order remains vowel first.')},
        references='DEDR 672; compare d665, d651; Indo-Aryan CDIAL 2360',eligibility='regional-contact-uncertain',
        boundary='Velar tool formation is shared independently; Indo-Aryan relationship and Telugu alternative remain unresolved.')
    tokens('d672','Kannada',R='olake',O='onake|onike')

    add('d697','be, exist, have','*uḷ-; *uḷ-nt- > *uṇṭ-',
        'Ø','u','ḷ','zero/a','VC + person/tense formations','verb',
        'Tamil and Malayalam uḷ, Kannada uḷ/oḷ and Kota oḷ independently support short vowel before lateral. The existential nasal-stop formation is explicitly reconstructed *uḷ-nt- by K03.',
        'The full southern paradigms establish earlier u–ḷ without treating Telugu uṇḍu as an unchanged root. Its initial vowel survives an independently motivated medial cluster assimilation.',
        '*uḷ-nt > *uṇṭ > Telugu uṇḍu; related nasal causative unucu/uncu and existence noun uniki preserve the initial vowel. Toda viḷd-/vɨḍ- includes prothesis and internal strengthening. Kolami an-/Naikri anḍ require separate root-vowel history.',
        'Kui lohpa and Kuvi loy/lōi are explicitly questioned in the source comparison; exact formative vowels and cognacy are unresolved. Their l-first appearance alone does not prove metathesis. Brahui anning has a suppletive-looking present uṭ/us/un/ure/ur in the source; full paradigm history is needed. Potential semantic connection with inside d698 is a sensitivity merge, not evidence for one homogeneous input.',
        {'Tamil':('O','uḷatu|uḷḷatu|uḷḷa|uḷḷavaṉ|uṇmai','Vowel-first lateral series and assimilated nasal formation.'),
         'Malayalam':('O','uḷ|uṇṭu|uḷḷa|uḷavu|uṇma','Retained lateral and assimilated formations.'),
         'Kannada':('O','uḷ (3 pers. uṇṭu)|oḷ|uḷḷa|uṇṭu','Paradigm retains initial vowel; nt assimilation is internal.'),
         'Kota':('R','oḷ- (3 oḍo·)|ol-','Vowel-first paradigmatic lateral/stop.'),
         'Toda':('O','viḷd- (3 pers. vɨḍ-i)|viḷd-|vɨḍ-','Glide prothesis and internal cluster changes.'),
         'Kodagu':('R','uḷḷ- (3 pers. uṇḍɨ)','Vowel-first lateral/nasal paradigm.'),
         'Tulu':('R','uḷḷ- (3 uṇḍu; )','Vowel-first paradigm.'),
         'Telugu':('O','uṇḍu|unucu|uncu|uniki','Medial assimilation of lateral before nasal; no initial relocation.'),
         'Kolami':('A','an- (anḍ-)','Initial a requires history beyond medial assimilation.'),'Naikri':('A','anḍ','Same root-vowel problem; editorial fragments excluded.'),
         'Kui':('A','lohpa (loht-)','Queried comparison.'),'Kuwi':('A','loy|lōi','Queried comparison and unknown earlier formative.'),
         'Brahui':('A','anning','Present u- paradigm included inside record; deeper suppletion/alternation unresolved.'),
         'Badaga':('O','uḷḷu|uḷḷava|uḷivadu|uṇdu|unme','Retained and internally assimilated formations.')},
        references='DEDR 697 p.68 directly checked; K03 *uḷ-nt reconstruction',input_confidence='high',
        boundary='Existential *-nt is independently reconstructed, distinct from locative formations in d698.',mechanism='Medial assimilation; uncertain eastern lexical comparisons.')
    tokens('d697','Tamil',R='uḷatu|uḷḷatu|uḷḷa|uḷḷavaṉ',O='uṇmai')
    tokens('d697','Malayalam',R='uḷ|uḷḷa|uḷavu',O='uṇṭu|uṇma')
    tokens('d697','Kannada',R='uḷ (3 pers. uṇṭu)|oḷ|uḷḷa',O='uṇṭu')
    tokens('d697','Badaga',R='uḷḷu|uḷḷava|uḷivadu',O='uṇdu|unme')

    add('d698','inside, mind, house','*uḷ; locative *uḷ-a-n; geminate *uḷḷ-am mind',
        'Ø','u','ḷ','a/zero','VC-a-n versus VCC-am','postposition/noun/verb',
        'Tamil uḷ locative and Kannada oḷ/oḷa support the vowel-first singleton locative independently. The source-cited Old Telugu oḷana reading is now uncertain: DHARMA00099 and Sastri1969 p.285 n.1 read ēḷan ruling in the candidate inscription instead. Tamil/Malayalam uḷḷam independently establish a geminate mind formation.',
        'Southern and Central Dravidian vowel-first locatives favor u/o–ḷ before Telugu lōna; the alleged earlier Old Telugu oḷana is not presently secure chronological evidence. The mind noun ullamu is not a same-input counterexample: its geminate is independently matched outside Telugu.',
        '*uḷ-a-n > *oḷan > *ḷōn > lōn gives Telugu lōna/lōnu and comparable Gondi lōn/rōn, with final suffix history differing by language. *uḷḷ-am > ullamu retains order. Konda olbi and Kuvi oṛp/onp thought verbs preserve initial V with internal consonant development.',
        'DEDR dates oḷana to the seventh century and ḷōna to the ninth–tenth; a corpus lōna record incorrectly inherits the seventh-century date. These are source dating claims. The candidate seventh-century witness at Inpuḻōli has oḷana only in an older edition: Sastri1969 p.285 n.1 and DHARMA00099 read ēḷan ruling. Unless another inscription is identified, do not use oḷana to establish retention in seventh-century Telugu. Kui lai cannot be explained by the same o outcome without another vowel/formation history. Telugu submit loŋgu/loggu series is queried; Central Dravidian lopal may be Telugu loans. Brahui house urā and heart ust have explicit alternative etymologies; exclude them from secure core counts. An existence/inside common ancestor is plausible but not settled.',
        {'Tamil':('R','uḷ|uḷḷam|uḷḷu|uḷku','Singleton locative and geminate mind/thought distinguished.'),
         'Malayalam':('R','uḷḷu|uḷḷam|uḷḷakam','Vowel-first geminate formations.'),'Kannada':('R','uḷ|oḷ|oḷa|oḷagu|oḷage|oḷavu','Vowel-first locative formations.'),
         'Kota':('R','uḷ|uḷpaṛ- (uḷpaṭ-)|oḷk','Vowel-first locative/compound formations.'),'Toda':('R','uḷ|uḷpoṛ- (uḷpoṭ-)','Vowel-first locative and compound.'),
         'Kodagu':('R','oḷɨ|uḷḷɨ','Singleton inside versus geminate mind.'),'Tulu':('R','uḷa|oḷa|uḷayi|uḷāyi|oḷavu','Vowel-first locatives.'),
         'Telugu':('M','lō|lōna|lōnu|lōpala|lō̃ga|ullamu|loŋgu|lō̃gu|lō̃cu','Displaced locatives, retained geminate mind and queried submit derivatives.'),
         'OTelugu':('A','oḷana (7tʰ cent.)','Source claim, but candidate inscription is re-read ēḷan ruling by Sastri1969 p.285 n.1 and DHARMA00099; not secure locative retention.'),
         'Gondi':('D','lōn|rōn ( rōt-)|lopa|lopo|rōpā|ropā|lappa|rappoṛ','Displaced house/inside family with dialect apical and quantity variation.'),
         'Konda':('M','loˀ o|loˀ i|olbi- (-t-)','Locative displacement versus thought verb retention.'),
         'Kui':('A','lai|laiki|laiṭi|lai lai','Lateral-first, but ai and exact earlier suffix require separate reconstruction.'),
         'Kuwi':('M',"loi|ṛō'i|rō'i|oṛpali|onpinai|oṇp- (-it-)",'Locative displacement versus thought-verb medial changes.'),
         'Kolami':('A','lo·pal','Contact with Telugu possible.'),'Naikri':('A','lōpal|lōpa','Contact unresolved.'),'Naiki':('A','lopun','Contact and suffix history unresolved.'),
         'Parji':('R','ole|olek','Vowel-first house forms.'),'Gadaba':('R','ule|ullen','Vowel-first house forms.'),
         'Kurux':('A',"ulā|oṛga'ānā|oṛᵒgnā",'Inside retained; thought verb formation less secure.'),
         'Malto':('A','ule|ugli|ugleye|uglare|uglatre','Inside retained; velar in thought/mind series needs independent suffix/cluster history.'),
         'Brahui':('A','urā','Explicit alternative house etymology d752; embedded heart ust has alternative d645.'),
         'Badaga':('O','ōge|ōgāsu|ul mūla|uḷḷūr','Long-vowel locatives can arise by medial lateral loss; compounds preserve uḷ.')},
        references='DEDR 698 p.68 directly checked; K03 *uḷḷ-am and *oḷ-an records',
        input_confidence='high',c2_structure='singleton/geminate by formation',
        boundary='Singleton locative and geminate mind formation are independently attested and must receive separate formation classes.')
    tokens('d698','Telugu',D='lō|lōna|lōnu|lōpala|lō̃ga',R='ullamu',A='loŋgu|lō̃gu|lō̃cu')
    tokens('d698','Konda',D='loˀ o|loˀ i',R='olbi- (-t-)')
    tokens('d698','Kuwi',D="loi|ṛō'i|rō'i",R='oṛpali',O='onpinai|oṇp- (-it-)')
    tokens('d698','Kurux',R='ulā',A="oṛga'ānā|oṛᵒgnā")
    tokens('d698','Malto',R='ule',A='ugli|ugleye|uglare|uglatre')
    tokens('d698','Badaga',R='ul mūla|uḷḷūr',O='ōge|ōgāsu')

    add('d699','chisel','*uḷ-i','Ø','u','ḷ','i','VC-i','noun',
        'Tamil, Malayalam, Kannada and Tulu uḷi independently support short u, singleton lateral, and high i. Kota/Toda uḷy agrees in order.',
        'Multiple southern branches support vowel-first input; Telugu uli retains it with regular loss of retroflexion.',
        '*uḷ-i > uli in Telugu; Nilgiri final i > y is a separate development. No initial metathesis is required.',
        'A tool name could diffuse, but the sources supply no particular donor diagnosis. Keep this independently motivated high-i retention control, with contact chronology unresolved. Gadaba ulli strengthens the medial lateral; it is not initial metathesis.',
        {l:('R',f,'Initial vowel before lateral retained.') for l,f in [('Tamil','uḷi'),('Malayalam','uḷi'),('Kannada','uḷi'),('Tulu','uḷi'),('Kota','uḷy'),('Toda','uḷy'),('Telugu','uli'),('Gadaba','ulli'),('Badaga','uḷi')]},
        input_confidence='high',references='DEDR 699 p.69 directly checked',boundary='High-i tool formation shared outside Telugu.',mechanism='Retention; medial lateral reflex changes.')

    add('d700','woodworm, ant','*uḷ-u; *uḷ-u-pp derivatives; ant cognacy queried',
        'Ø','u','ḷ','u','VC-u-(pp)','noun/verb',
        'Tamil/Malayalam uḷu and uḷuppu independently establish vowel-first lateral and high u. Telugu lūta and Kui lupenji are explicitly queried by DEDR.',
        'The southern woodworm family has secure vowel-first order, but that cannot settle whether the two ant names are its cognates. Imported *ḷup- should not override this evidential uncertainty.',
        'If cognate, *uḷ-u > *ḷū would explain Telugu lū-, but the extra -ta is not independently matched. Kui lu-penji would also need suffix analysis and an explanation of quantity. Alternative comparison with nuḷampu d3715 admits an earlier initial nasal.',
        'Keep Telugu and Kui uncertain rather than using their output to invent *-ta or claim an exceptionless high-u class. Species identification, historical ant forms, and analysis of -penji would distinguish a displaced derivative from questionable cognacy.',
        {'Tamil':('R','uḷu|uḷuvey|uḷuppu','Southern woodworm and worm-eaten formation.'),'Malayalam':('R','uḷu|uḷuppu|uḷumpu|uḷukkuka','Vowel-first related formations.'),
         'Kannada':('A','uḷŋgu','Nit comparison explicitly queried.'),'Telugu':('A','lūta','Queried ant comparison and unmatched suffix.'),'Kui':('A','lupenji','Queried ant comparison and unmatched formation.')},
        references='DEDR 700 p.69 directly checked; cf. d3715',eligibility='cognacy-or-input-uncertain',boundary='Only southern pp derivative independently supported; ant suffixes unknown.')

    add('d703','start with fear','*uḷ-k / *uḷ-uk; Tamil uṭk; exact deep cluster uncertain',
        'Ø','u','ḷ/ṭ','zero/u/a','VC-C / VC-V-C','verb/noun',
        'Malayalam uḷukka/uḷuppu, Kannada ulaku and Telugu uluku/ulku support a lateral family; Tamil uṭku has a stop before k. Medial vowel quality varies independently.',
        'Every witness is vowel first. Tamil ṭk could arise from *ḷk cluster hardening rather than representing a proto-singleton ṭ followed by a vowel.',
        'Possible *uḷ-k > Tamil uṭk, with Telugu ulk ~ uluk and Malayalam uḷukk. This distinguishes syncope/epenthesis and cluster assimilation from movement of the apical to initial position.',
        'Which branch retained a medial vowel is unresolved. Do not manufacture a uniform *uluk input merely from Telugu or take Tamil ṭ to prove the same environment as open *uṭV animal names. Kannada low a also remains to be historically explained.',
        {'Tamil':('O','uṭku','Possible lateral–velar cluster hardening.'),'Malayalam':('R','uḷukka|uḷuppu','Lateral before velar/labial formation.'),'Kannada':('R','ulaku','Low-vowel formation retains order.'),'Telugu':('R','uluku|ulku','Full/syncopated forms retain initial vowel.')},
        references='DEDR 703 p.69 directly checked',eligibility='core-formation-uncertain',c2_structure='cluster-or-vocalic-extension',boundary='Medial vowel and cluster history not uniquely reconstructible.',mechanism='Retention with internal syncope/epenthesis and possible assimilation.')

    add('d704','snipe, lapwing','regional *uḷḷ-V(n/k)-','Ø','u','ḷ','a/i/u','VCC-V','noun',
        'Tamil uḷḷal/uḷḷān/uḷḷu, Malayalam uḷḷi and Kannada ullaŋgi independently support a medial geminate bird name.',
        'The same vowel-first geminate order is inherited or diffused across the region; no language supplies an initial lateral reflex here.',
        '*uḷḷ- > Telugu ull- with loss of retroflexion and differing bird-name suffixes; no initial promotion. Exact suffix correspondence and species identity are not needed to observe retained initial order.',
        'This is a geminate control, not a singleton metathesis exception. DEDR explicitly reports disagreement on the Telugu species; suffix/meaning differences cannot be counted as several independent roots.',
        {'Tamil':('R','uḷḷal|uḷḷān|uḷḷu','Geminate retained.'),'Malayalam':('R','uḷḷi','Geminate retained.'),'Kannada':('R','ullaŋgi','Geminate retained.'),'Telugu':('R','ullāmu|ullaŋki|ullaŋgi','Geminate retained with suffix/species variation.')},
        c2_structure='geminate',eligibility='structural-control',input_confidence='high',references='DEDR 704 p.69 directly checked',boundary='No independently supported bare singleton root; whole geminate bird name.',mechanism='Retention.')

    add('d705','onion, garlic','*uḷḷ-i','Ø','u','ḷ','i','VCC-i','noun',
        'Tamil, Malayalam and Kannada independently preserve geminate ḷḷ. K03 reconstructs *uḷḷi; the alternative singleton database reconstruction conflicts with those witnesses.',
        'Widespread u before lateral supports original vowel-first order; singleton daughter reflexes can result from degemination. It is not legitimate to reclassify their ancestors as singleton solely to enlarge the eligible denominator.',
        '*uḷḷi > Telugu ulli; Central/Eastern uli and Pengo ūṛi involve degemination and apical/quantity developments. Toda u·ḷy also changes vowel quantity. Garlic compounds with white/water modifiers retain the root internally.',
        'The plant term has Indo-Aryan comparisons (Sanskrit ūlī, Oriya uli); the contact direction is not settled here. Four corpus Manda forms are actually Kuvi F./S./Su.; source-corrected. Compound garlic forms and repetitions across sources add no independent etyma.',
        {l:('R',f,'Vowel-first root or compound member; independent source labels preserved.') for l,f in [('Tamil','uḷḷi'),('Malayalam','uḷḷi'),('Kannada','uḷḷi'),('Kota','uḷy'),('Toda','u·ḷy|pøḷ u·ḷy'),('Tulu','ulli|uḷḷi|boḷḷ-uḷḷi'),('Telugu','ulli'),('Gondi','ulli|ullī'),('Konda','uli'),('Pengo','ūṛi'),('Manda','uli'),('Kuwi','ūlli|ulli|ulli gidda|vella ūlli'),('Kolami','ulli'),('Naiki','ullig'),('Parji','ulli'),('Gadaba','ulli'),('Kurux','uli'),('Badaga','uḷḷi'),('markodi','nīruḷḷi|nīruḷḷŭ|veḷḷuḷḷi|veḷḷuḷŭ|beḷutuḷḷi')]},
        c2_structure='geminate',eligibility='structural-control',input_confidence='high',references='DEDR 705 p.69 directly checked; K03 *uḷḷi reconstruction',boundary='Geminate supported by independent southern forms; compound boundaries explicit.',mechanism='Retention with medial/quantity changes and unresolved plant-name diffusion.')
