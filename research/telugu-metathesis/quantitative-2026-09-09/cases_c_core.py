"""Consonant-initial core comparisons; cluster loss is a separate observed event."""

def populate(add,tokens):
    add('d2149','new, sprout, young; kinship derivatives','*koẓ-utt-V; short *koẓ-V and long *kōẓ formations',
        'k','o','ẓ','u/unknown','CVC-u-tt / CVC-V / CVVC','adjective/verb/noun',
        'Tamil koẓuntu, Malayalam koẓunnu, Gondi koṛs and Parji koṛ/koṛc independently establish k-V-apical order. K03 pp.159,198 distinguishes short *koẓ-utt-V new from short/long kinship formations.',
        'Full southern and Central Dravidian forms support V before apical; Telugu krotta has changed order. Modern kotta is independently documented by K03 as the r-loss continuation, making concealed displacement demonstrable here.',
        '*koẓ-utt-V > *koẓ-tt-V > *kẓott-V > krott-V > kotta is the proposed short branch. The tt belongs to the formation before metathesis in K03, not automatic new gemination. Telugu koḍuku preserves medial *ẓ > ḍ; kōḍalu has a long root grade. Kui kuṛa/kṛua and Kuvi koṛgi/kṛōgi show different formations and dialect outcomes.',
        'Tamil koẓuntu has nt, not the identical tt formation: do not invent nt>tt to derive Telugu from Tamil directly. Exact *-utt support is the comparative reconstruction, whereas high-u formation is independently visible. Kui kṛua preserves two vowels and need not represent contraction; Kuvi long ō needs its own vowel/quantity history. Some kinship/nasal forms may have assimilated medially; neither those nor the related crop and kinship derivatives count as independent roots. Konda kodma is explicitly Telugu borrowing.',
        {'Tamil':('R','koṛ̆untu|koṛ̆unaṉ|koṛ̆untaṉ|kuṛ̆antai|kuṛ̆ai|kuṛ̆avi','Distinct young/sprout/kinship formations retain V before apical.'),
         'Malayalam':('R','koṛ̆unnu|koṛ̆untu','High-u nasal formation.'),'Kannada':('O','koḍa|koṇasu','Medial apical reflex versus nasal formation.'),'Tulu':('R','korɛ','V remains between initial k and r.'),
         'Toda':('R','kvɨζ|kvɨz̡','Initial labial glide accompanies vowel change; apical remains after vowel.'),
         'Telugu':('M','krotta|kotta|koḍuku|kōḍalu|kodama|komma|koṇḍika','Displaced new adjective, retained short/long kinship forms, uncertain nasal developments.'),
         'Gondi':('R','koṛs|kōṛsānā|kōrsānā|koṛkēlā|koḍiyāḍ|koṛiyaṛ','Several dialect formations retain medial apical.'),
         'Konda':('A','koṛo|koṛya|koṛesi|koṛonali|kodma','Retained native formations and explicit borrowed calf term.'),
         'Kui':('M','koṛgi|koṛgari|kōṛu|kōṛa|kuṛa|kṛua|kṛuha|kōna|gōṇi','Both orders in wife formation; long sprout and nasal derivatives distinguished.'),
         'Kuwi':('M','koṛgi|kṛōgi|kʰrogi kōma|kuṛia|kūria|kuṛva','Both orders across source/formation variants.'),
         'Pengo':('M','kṛogi|koṛiya gāṛ','Displaced new versus retained kinship formation.'),'Manda':('M','kṛugdi|kuṛiya gāṛ','Same formation distinction with additional cluster history.'),
         'Kolami':('O','koral|kommal|kovve','Retained rhotic kinship and internally assimilated formations.'),'Naikri':('O','koraḷ|kommaḷ|kovve','Same distinction.'),'Naiki':('O','kola|komma','Medial lateral/nasal developments.'),
         'Parji':('R','koṛ|koṛc|koṛol|koṛuŋg','Independent retained young/sprout series.'),'Gadaba':('R','koḍus|koḍc|koṛal|koṛuŋ','Ollari/Salur/Pottangi retained series.'),
         'Kurux':('R','korrā|xōr|xōrnā (xūryā)','Medial apical retained; long and strengthened variants.'),'Malto':('R','qóro|qóroce','Medial apical retained.'),
         'Brahui':('R','xarring|xarrun|xarrunī','Medial rhotic retained; local vowel history separate.'),'Koraga':('R','korayi|kori|korti','Medial rhotic in kinship derivatives.'),'Badaga':('A','koḷa koḷa','Expressive soft/sticky comparison, exact cognacy unclear.')},
        confidence='high',input_confidence='high',references='K03 pp.158–159 example 90, p.198 *koẓ-utt-V; DEDR 2149',
        quantity='mixed by formation',boundary='Short new adjective and short/long kinship formations must be separate input classes; exact tt extension is reconstructed, not identical to Tamil nt.')
    tokens('d2149','Kannada',R='koḍa',O='koṇasu')
    tokens('d2149','Telugu',D='krotta|kotta',R='koḍuku|kōḍalu|kodama',O='komma',A='koṇḍika')
    tokens('d2149','Konda',R='koṛo|koṛya|koṛesi|koṛonali',B='kodma')
    tokens('d2149','Kui',D='kṛua|kṛuha',R='koṛgi|koṛgari|kōṛu|kōṛa|kuṛa',O='kōna|gōṇi')
    tokens('d2149','Kuwi',D='kṛōgi|kʰrogi kōma',R='koṛgi|kuṛia|kūria|kuṛva')
    tokens('d2149','Pengo',D='kṛogi',R='koṛiya gāṛ')
    tokens('d2149','Manda',D='kṛugdi',R='kuṛiya gāṛ')
    tokens('d2149','Kolami',R='koral',O='kommal|kovve')
    tokens('d2149','Naikri',R='koraḷ',O='kommaḷ|kovve')

    add('d4711','tree','*mar-am / *mar-an','m','a','r','a','CVC-a-N','noun',
        'Tamil/Malayalam maram, Kannada/Kodagu/Tulu mara, Gondi mara and Gadaba marin independently establish ma-r-a order; Konda maran independently supplies final n. K03 pp.150,160–161 discusses nominal n/m and dialect stress.',
        'Widespread uncontracted mar- and matching low second vowel make *mar-an earlier than mrān. A consonant-first ancestor would require multiple independent epentheses plus a low-vowel restoration without independent motivation.',
        '*mar-an > *mrān > Telugu mrānu > mānu. Literal *mraan contraction and *marán > *marān > mrān via stress and first-vowel loss are competing implementations. Konda Araku marán versus Sova mrānu supplies a synchronic phonetic analogue, not a directly observed prehistoric time series.',
        'Do not derive Telugu n from modern Tamil m: both nominal suffix types have comparative support. Telugu mrā̃ku/mā̃ku has an additional velar formation whose source must be reconstructed separately. Kuvi marnu/mrānu/mārnu preserves dialect and paradigm variation; the long-vowel mārnu type is not a retained exact short input. Kolami/Naikri māk could reflect direct internal assimilation or a borrowed/reduced mrā-type, so its lost r alone cannot prove metathesis. Kurux mann/Malto manu similarly admit medial assimilation.',
        {'Tamil':('R','maram','Full low-vowel input.'),'Malayalam':('R','maram','Same input.'),'Kannada':('R','mara','Final nasal lost; initial order retained.'),'Kodagu':('R','mara','Same.'),'Tulu':('R','mara|marakalɯ|markalɯ','Base and measure derivatives retain initial order.'),
         'Kota':('R','marm ( mart-)','Medial syncope, r remains after initial vowel.'),'Toda':('O','me·ṇ ( me·ṇt-)|mēṇ','Medial rhotic/nasal assimilation and vowel changes; no demonstrated initial cluster stage.'),
         'Telugu':('D','mrānu|mānu|mrā̃ku|mā̃ku','Displaced tree with documented rhotic-free variants; final velar variant distinct.'),
         'Gondi':('R','mara|maṛa|maṛā|marnu|mārnu|māra|māṛa|muranoo','All preserve vowel between m and apical; quantities and endings vary by dialect.'),
         'Konda':('M','maran ( marak)|marán|mrānu','Araku retained versus Sova displaced; stress source explicitly retained.'),
         'Kui':('D','mrānu|mrahnu|mrahunḍi ( mrahka)','Initial cluster throughout, differing spelling and paradigms.'),
         'Kuwi':('M','mara|mṛānū (i.e.mrānū; <i>pl.</i> mārka)|mārnu ( mārka) (i.e.mrānū; <i>pl.</i> mārka)|marnu ( marka)|mrānu|marnu','Source variants include both orders; mārnu quantity separate.'),
         'Pengo':('R','mar ( -ku)','Short vowel before r retained.'),'Manda':('R','mar ( -ke)','Same.'),
         'Kolami':('A','ma·k ( ma·kul)','Missing rhotic: medial assimilation versus concealed displacement/contact.'),'Naikri':('A','māk','Same alternatives.'),
         'Parji':('R','meri ( merkul)','Vowel-quality change but r remains after V.'),'Gadaba':('R','marin ( markil)|māren ( markīl)|mar','Retained order and n/quantity variants.'),
         'Kurux':('O','mann','Medial r+n assimilation sufficient.'),'Malto':('O','manu','Medial assimilation sufficient.'),'markodi':('R','maram','Three locality attestations, one lexical family.')},
        confidence='high',input_confidence='high',references='K03 pp.107,150,160–162 n.16; DEDR 4711(a)',
        boundary='Low-a nominal formation independently supported; n/m endings and velar derivatives kept distinct.')
    tokens('d4711','Konda',R='maran ( marak)|marán',D='mrānu')
    tokens('d4711','Kuwi',R='mara|marnu ( marka)|marnu',D='mṛānū (i.e.mrānū; <i>pl.</i> mārka)|mrānu',A='mārnu ( mārka) (i.e.mrānū; <i>pl.</i> mārka)')

    add('d5409','finger','*wir/wer-al; distinct *wir-and/anj derivatives',
        'w','i/e','r','a','CVC-a-L / CVC-a-NC','noun',
        'Tamil/Malayalam viral, Kannada beral/beraḷ and Tulu berel independently establish initial labial, V, rhotic, then a second vowel/liquid. Gondi varanj/virinj and regional *-and/anj forms are different formations. K03 pp.101–106 explains historical i/e ambiguity.',
        'The full southern forms and retained Gondi/Konda variants support labial–vowel–rhotic order. Telugu vrēlu reverses the relative vowel/rhotic order, and vēlu is its documented cluster-reduced counterpart.',
        'Immediate *wer-al > *wrēl > vrēlu > vēlu. Deeper *wir-al > *wer-al lowering is one analysis; ancestral e is an alternative where southern vowel mergers obscure the contrast. Simple initial-vowel deletion from weral would give wral with wrong quality; prior a>e assimilation plus deletion gives wrēl without literal exchange.',
        'The exact mechanism remains underdetermined but plain deletion alone is inadequate. Konda veṛska versus ṛeska/ṛaska permits *vṛ- > ṛ- with first-member loss; exact a/e suffix history differs from Telugu -al. Kui vanju/Kuvi vansu and Central vande admit medial r assimilation in a nasal-stop formation; they are not secure concealed initial metathesis. Toda pēḷ can likewise arise by medial r loss and contraction. Badaga bēru index finger has a competing relation to full beralu or another finger-name root.',
        {'Tamil':('R','viral|veraṭṭi','Full root order, different nominal extensions.'),'Malayalam':('R','viral','Full low-al formation.'),'Kannada':('R','beral|beraḷ','Labial b and final lateral variation, order retained.'),'Tulu':('R','berelɯ|birelɯ|pirelɯ','Vowel and labial variants retain order.'),'Kota':('R','verl','Medial syncope.'),'Kodagu':('R','bera','Final lateral loss.'),
         'Toda':('O','pe·ḷ|pēɫ̣','Medial rhotic loss/contraction; no directly evidenced initial cluster.'),'Telugu':('D','vrēlu|vēlu','Displaced and subsequently r-reduced variants.'),
         'Gondi':('R','vaṛanj|varēnj|virinj|veṛenj|vaṛnj|vaṛnji ( vaṛsku)|vaṛnj ( vaṛsku)|vers|viṛaskū (pl)','Different regional formations retain initial vowel before rhotic.'),
         'Konda':('M','veṛska|ṛeska|ṛaska','Retained versus displaced with first-member loss; quantity and suffix not identical to Telugu.'),
         'Kui':('O','vanju ( vaska)','Medial r assimilation/loss in nasal formation possible.'),'Kuwi':('O','vansu ( vaska)|vvānjū ( vvāska)|vanju ( vaska)|veṛma','Nasal formations mostly lack r; Bisamkatak veṛma retains it.'),
         'Pengo':('O','vacka','Medial apical/cluster reduction, exact prehistory unresolved.'),'Manda':('O','vehpe','Different derivative and internal consonant history.'),'Kolami':('O','vende','Internal rhotic/nasal assimilation possible.'),'Naikri':('O','vende','Same.'),'Parji':('O','vanda ( vandel)','Same.'),'Gadaba':('O','vande','Same.'),
         'Badaga':('A','beralu|bēru','Full finger form and ambiguous shortened index-finger name.'),'Koraga':('R','berolu|berlɨ','Order retained, syncope in Mudu.'),'markodi':('R','viral|veṛaḷŭ|viräl','Locality variants retain order.')},
        confidence='high',input_confidence='high',references='K03 pp.101–106,483; K61 pp.61–62,67; PSS83 ch.15; DEDR 5409',
        boundary='Southern -al and regional -and/-anj are independently different formations; no free substitution of suffix consonants.')
    tokens('d5409','Konda',R='veṛska',D='ṛeska|ṛaska')
    tokens('d5409','Kuwi',R='veṛma',O='vansu ( vaska)|vvānjū ( vvāska)|vanju ( vaska)')
    tokens('d5409','Badaga',R='beralu',A='bēru')

    add('d1787','blind','*kur-uṭ-V; immediate *kur-ḍ-V',
        'k','u','r','u','CVC-u-ṭV / CVC-ḍV','adjective/noun',
        'Tamil/Malayalam kuruṭu and Kannada kuruḍu independently supply high-u disyllabic input. Tulu kurḍu and Kota kurḍ independently support the syncopated medial cluster, while Kannada kuḍḍu shows its assimilated alternative.',
        'The full and syncopated southern series establishes k-u-r ordering. Telugu gruḍḍi/gruḍḍu has the rhotic before u; guḍḍi is attested beside it but cannot be mechanically generalized to every language with guḍḍi.',
        '*kur-uḍ-V > *kur-ḍ-V > *kru-ḍḍ-V > gruḍḍi/gruḍḍu > guḍḍi, with initial k/g alternation and later r loss. Strengthening might precede displacement; *kurḍḍ > kruḍḍ yields the same result. Contraction followed by shortening is another possible route. Final i/u and gender formations remain separate.',
        'Identical u+u does not guarantee a long modern vowel: the independently attested consonantal branch is crucial. Initial g is not explained by naming the r/vowel exchange. Gondi/Kolami/Naikri guḍḍi could be Telugu loans or local medial assimilation; no observed cluster establishes independent metathesis there. Malto qoṭri may involve internal consonant reversal relative to kur-ṭ, but its precise morphology and quantity require separate study.',
        {'Tamil':('R','kuruṭu|kuruṭaṉ|kuruṭi','Full high-u input and person suffixes.'),'Malayalam':('R','kuruṭu|kuruṭan|kuruṭi','Same.'),'Kannada':('O','kuruḍu|kuruḍa|kuruḍi|kuraḍu|kuraḍa|kuraḍi|kuruḷu|kuḍḍu|kuḍḍa','Full retained rhotic versus internally assimilated forms.'),
         'Tulu':('R','kuruḍu|kuruḍa|kuruḍe|kurḍu|kurḍe|kurute','Full and syncopated order retained.'),'Kodagu':('R','kurɨḍ|kurɨḍə|kurɨḍi','Retained order.'),'Kota':('O','kurḍ|kurḍṇ|kurḍy|ku·ṛ|ku·ṛṇ','Medial syncope and separate long reduced forms.'),
         'Telugu':('D','gruḍḍi|gruḍḍu|guḍḍi|guḍḍitanamu','Displaced and r-reduced variants.'),'Gondi':('A','guḍḍi','Potential loan or medial assimilation; initial cluster not attested.'),'Kolami':('A','guḍḍi','Same alternatives.'),'Naikri':('A','guḍḍi','Same alternatives.'),
         'Malto':('A','qoṭre|qoṭri','Internal r/stop order differs; exact prehistory unresolved.'),'Badaga':('R','kuruḍdu|kuradu|kuruda|kurudi|kurada','Initial order retained despite medial strength and vowel variation.')},
        confidence='high',input_confidence='high',references='K61 §§1.142–154; K03 pp.130–131,157–162; DEDR 1787',
        boundary='Whole blindness stem supported independently; person endings do not add etyma; timing of V2 syncope remains inferential.')
    tokens('d1787','Kannada',R='kuruḍu|kuruḍa|kuruḍi|kuraḍu|kuraḍa|kuraḍi|kuruḷu',O='kuḍḍu|kuḍḍa')
    tokens('d1787','Kota',R='kurḍ|kurḍṇ|kurḍy',O='ku·ṛ|ku·ṛṇ')

    add('d4866','swallow','*miẓ-u-nk; regional *miẓ-i-nk and mu/v variants',
        'm','i','ẓ','u/i','CVC-V-NK','verb',
        'Tamil miẓuŋku and Malayalam miẓuŋŋuka independently give m-i-apical-u; Konda miṛiŋ supplies an independent high-i second-vowel variant. K03 p.161 explicitly uses *miẓ-u-ŋ.',
        'Full southern and Konda forms establish m-V-apical order. Telugu mriŋgu is innovative, and its miŋgu variant can be traced through r loss because the cluster is independently attested in Telugu.',
        '*miẓ-u-ŋk > *miẓ-ŋk > *mẓiŋk > mriŋgu > miŋgu, with nasal-stop voicing and postconsonantal ẓ>r. Konda miṛiŋ > *mṛiŋ > ṛiŋ gives first-member loss under the displacement account. Tamil/Malayalam v-initial forms need a separate labial history.',
        'Do not replace all historical V2 values with u: the Konda i form is real and may involve assimilation. Kannada/Kota/central miŋ(g) can result directly from medial ẓ loss, or contact with Telugu, so matching modern Telugu miŋgu is not independent proof of concealed metathesis. Pengo ṛuggiŋga/ṛugginda is explicitly onomatopoeic and has different vowels/formation. Tamil English gloss words consume/devour are parser errors, not linguistic witnesses.',
        {'Tamil':('R','miṛ̆uŋku|muṛ̆untu|viṛ̆ukku','Full apical forms; initial vowels and labials vary.'),'Malayalam':('R','miṛ̆uŋŋuka|miṛ̆uŋŋikka|viṛ̆uŋŋuka','Full retained apical.'),
         'Telugu':('D','mriŋgu|miŋgu','Attested cluster and later r-loss form.'),'Konda':('M','miṛiŋ|ṛiŋ- (-it-)','Retained Gūṛi versus displaced/initial-m-lost form.'),
         'Kannada':('O','miŋgu|muŋgu','Direct medial apical loss/assimilation sufficient.'),'Kota':('O','miŋg- (miŋgy-)|miŋg|ming-|mingy-','No directly observed initial cluster; possible medial loss.'),'Kodagu':('O','mugg- (muggi-)','Medial and nasal-cluster assimilation.'),
         'Gondi':('A','miŋg|miŋ','Inherited medial reduction versus borrowing unresolved.'),'Kolami':('A','miŋg|miŋ','Same alternatives.'),'Naikri':('A','miŋg','Same alternatives.'),'Naiki':('A','miŋg- (miŋkt-)','Same alternatives.'),
         'Pengo':('A','ṛuggiŋga|ṛugginda','Expressive formation not a securely matched ordinary verb.'),'Kurux':('O','munxnā','Medial apical loss and vowel history; no initial cluster evidence.')},
        confidence='high',input_confidence='high',references='K03 pp.161–162; K61 pp.61–64; DEDR 4866',
        boundary='Nasal-velar extension independently supported, with u/i V2 variants; no new geminate needed for existing NK cluster.')
    tokens('d4866','Konda',R='miṛiŋ',D='ṛiŋ- (-it-)')

    add('d4993','sink, immerse, drown','*muẓ-u-nk / *muẓ-u-nkk; long and shorter formations',
        'm','u','ẓ','u/i/a','CVC-u-NK / CVVC-K / CVC-C','verb/noun',
        'Tamil muẓuku, Malayalam muẓukuka, Kannada muẓuŋgu and Gondi muṛuŋg independently establish m-u-apical-u. Tulu murk and Konda muṛg/muṛk support a medial consonant-cluster branch.',
        'Full SD I and Gondi/Konda forms establish earlier m-V-apical; Telugu bruŋgu has a moved apical and an additional initial m>b change. Full muḍũgu remains in Telugu itself.',
        '*muẓ-u-ŋk > *muẓ-ŋk > *mẓuŋk > *mruŋg > bruŋgu; the initial denasalization m>b is separate (K61 p.28 §1.69). Alternatively vowel contraction and later shortening before NK can give the same short output. Bruncu has a different stronger transitive formation. Telugu muṇugu/munũgu and southern muŋg/mukk can arise by medial assimilation without initial metathesis.',
        'This is another independent same-u short outcome, contradicting obligatory surface ū but not uniquely deciding syncope versus contraction plus shortening. Kui bṛuḍga adds a retroflex stop whose origin cannot be read off the Telugu ŋg; Kuvi mrūkʰali differs in quantity and suffix/aspiration. The shared initial b in Telugu and Kui is suggestive but insufficient to choose inheritance, independent denasalization or contact. None of the surviving mu-initial assimilated forms can be labeled hidden metathesis without separate evidence.',
        {'Tamil':('O','muṛ̆uku|muṛ̆ucu|muṛ̆uttu|mūṛ̆ku|mūṛ̆|mūṛ̆ttu|muŋku|mukku','Full short/long apical forms plus internal assimilation.'),
         'Malayalam':('O','muṛ̆ukuka|muṛ̆ukikka|muŋŋuka|muŋŋikka|mukkuka','Full and assimilated voice formations.'),'Kannada':('O','muṛ̆uŋgu|muṛ̆uŋku|muṛ̆ugu|muṛ̆uku|muṛ̆iŋku|muṛ̆igu|muṛ̆agu|muṇugu|muṇigu|muṇagu','Independent formative vowels; nasalized apical outcomes separate.'),
         'Kota':('O','muḷk- (muḷky-)|muḷg- (muḷgy-)|mu·k- (mu·yk-)|mu·g- (mu·yg-)','Retained medial lateral versus loss with long vowel/glide.'),'Toda':('O','muḷk- (muḷky-)|muḷx- (muḷxy-)|mu·x- (mu·xy-)|mu·k- (mu·ky-)','Same broad internal distinction.'),
         'Kodagu':('O','muŋŋ- (muŋŋi-)|mukk- (mukki-)','Medial assimilation; no displaced cluster attested.'),'Tulu':('O','murkuni|murkāvuni|murgelɯ|muḷuguni|muṇuguni|muŋguduni','Retained medial apical and internally reduced variants.'),
         'Telugu':('M','bruŋgu|bruncu|muḍũgu|muṇugu|munũgu|mungu|muncu|munucu|mumpu|munuka|munīgincu','Displaced b-r series versus retained/assimilated m-V series with distinct morphology.'),
         'Gondi':('O','muṛuŋg|muṛuŋ|muṛandānā|muṛnd|murītānā|murahtānā|muṛhuttānā|muṇŋ|mu','Retained full apical and internal reductions.'),'Konda':('R','muṛg- (-it-)|muṛk- (-t-)','Medial cluster retained in both voice stems.'),
         'Kui':('A','bṛuḍga (bṛuḍgi-)|munja (munji-)|muspa (must-)','Displaced-looking bṛ with unmatched medial ḍ; other formations show internal reduction.'),
         'Kuwi':('M','mrūkʰali|munjinai|mūnjali|munj- (-it-)|muh- (must-)','Displaced long cluster form versus medially assimilated formations.'),
         'Pengo':('O','munj- (munc-)|muc- (mucc-)','Medial reduction and voice alternation.'),'Manda':('O','munj|muc','Same.'),'Kolami':('O','muŋg- (muŋkt-)|muŋgip- (muŋgipt-)','Internal apical loss; no direct initial cluster evidence.'),'Naikri':('O','muŋg|mupp','Internal assimilation with distinct voice formations.'),'Naiki':('O','muŋ|muŋgup','Internal apical loss.'),
         'Parji':('R','mulg|muli','Medial lateral retained.'),'Gadaba':('R','mulg','Medial lateral retained.'),'Kurux':('O',"mulᵘxnā (mulxyas)|mulxa'ānā|mulᵘxta'ānā|munᵘxnā",'Lateral and nasal variants; no initial displacement.'),'Malto':('R','mulɣe|mulɣre','Medial lateral retained.'),
         'Badaga':('O','mūgu|muggirida|muggirududu','Long reduced and strengthened expressive formations.'),'OMal':('R','muḷkkuka','Historical medial lateral-cluster form.')},
        confidence='high',input_confidence='high',references='K61 p.28 §1.69, pp.61–64; K03 *muẓ-u-nk/nkk; DEDR 4993',quantity='mixed by formation',
        boundary='Independent high-u nasal-velar formation; long roots and different voice suffixes remain distinct.')
    tokens('d4993','Tamil',R='muṛ̆uku|muṛ̆ucu|muṛ̆uttu|mūṛ̆ku|mūṛ̆|mūṛ̆ttu',O='muŋku|mukku')
    tokens('d4993','Malayalam',R='muṛ̆ukuka|muṛ̆ukikka',O='muŋŋuka|muŋŋikka|mukkuka')
    tokens('d4993','Kannada',R='muṛ̆uŋgu|muṛ̆uŋku|muṛ̆ugu|muṛ̆uku|muṛ̆iŋku|muṛ̆igu|muṛ̆agu',O='muṇugu|muṇigu|muṇagu')
    tokens('d4993','Kota',R='muḷk- (muḷky-)|muḷg- (muḷgy-)',O='mu·k- (mu·yk-)|mu·g- (mu·yg-)')
    tokens('d4993','Toda',R='muḷk- (muḷky-)|muḷx- (muḷxy-)',O='mu·x- (mu·xy-)|mu·k- (mu·ky-)')
    tokens('d4993','Tulu',R='murkuni|murkāvuni|murgelɯ|muḷuguni',O='muṇuguni|muŋguduni')
    tokens('d4993','Telugu',D='bruŋgu|bruncu',R='muḍũgu',O='muṇugu|munũgu|mungu|muncu|munucu|mumpu|munuka|munīgincu')
    tokens('d4993','Gondi',R='muṛuŋg|muṛuŋ|muṛandānā|muṛnd|murītānā|murahtānā|muṛhuttānā',O='muṇŋ|mu')
    tokens('d4993','Kui',A='bṛuḍga (bṛuḍgi-)',O='munja (munji-)|muspa (must-)')
    tokens('d4993','Kuwi',D='mrūkʰali',O='munjinai|mūnjali|munj- (-it-)|muh- (must-)')
    tokens('d4993','Kurux',R="mulᵘxnā (mulxyas)|mulxa'ānā|mulᵘxta'ānā",O='munᵘxnā')
