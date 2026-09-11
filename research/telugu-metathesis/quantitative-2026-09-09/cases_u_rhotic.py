"""Rhotic u-initial families; lexical formations and competing mechanisms separated."""

def populate(add,tokens):
    add('d648','speak, roar, pant; silence','*ur-ay / *ur-a; nasal-palatal extensions',
        'Ø','u','r','a','VC-ay / VC-a-NC','verb/noun',
        'Tamil urai/ura, Malayalam ura/urekka and Kannada ore establish a low-vowel speech formation; Parji ur groan independently preserves vowel-first root order.',
        'The independent southern and central comparison supports older u–r; Telugu uraka retains that order alongside rō̃ju/rō̃juḍu.',
        'Possible *ur-añc > *orañc > *rōñc > rō̃ju requires a nasal-palatal formative not fully matched here. Telugu uraka/ūraka is source-analyzed as a negative gerund and retains the initial vowel; its length is not evidence for displacement. roda has an additional dental and may have a separate expressive or contact history.',
        'Negative morphology could contribute to retention, but a single family does not establish a rule that negation blocks metathesis. Gondi ronjānā may share the derived stem or borrow it. Codagu answer has an explicit alternative comparison with d650; the noisy/expressive series cannot be unified just by broad speech semantics.',
        {'Tamil':('R','urai|ura|uraṟu|urappu','Retained speech/noise forms.'),'Malayalam':('R','ura|urekka|urakka|uri','Retained forms.'),
         'Kannada':('R','ore|ura|uru','Retained forms.'),'Kodagu':('A','oraḍ- (oraḍuv-, oraṭ-)','Vowel first, competing cognacy.'),
         'Telugu':('A','uraka|uṟaka|ūraka (neg. gerund of *ūr-)|rō̃ju|rō̃juḍu|roda','Retained negative gerund; probable displaced pant/prattle derivative; roda uncertain.'),
         'Parji':('R','ur','Retained groan root.'),'Gondi':('A','ronjānā','Potential displaced derivative or Telugu-area loan.'),
         'Koraga':('R','ojji','Initial vowel retained after medial changes.')},
        references='DEDR 648',boundary='Negative gerund and nasal-palatal pant/prattle formation distinguished; exact suffix ancestry unresolved.')
    tokens('d648','Telugu',R='uraka|uṟaka|ūraka (neg. gerund of *ūr-)',D='rō̃ju|rō̃juḍu',A='roda')

    add('d649','strength, firmness, coarseness','*ur-a-; *ur-k- and *ur-aṭ- formations',
        'Ø','u','r','a/zero','VC-a / VC-k / VC-aṭ','noun/adjective/verb',
        'Tamil ura/uram/uravu, Malayalam uram and Kannada urku/oraṭu establish a vowel-first strength root. Kannada urku beside ukku independently shows the medial cluster potentially underlying Telugu ukku.',
        'The full southern forms and Kannada urku support r after u, with later loss/assimilation in ukku; they do not require r ever to have moved to word onset.',
        '*ur-k > *ukk > Telugu ukku, with a velar expansion and assimilation/loss of r. Kannada oraṭu > orṭu/uṭṭu supplies a parallel dental-cluster development. Toda pith ūṇ requires different nominal/nasal history.',
        'Telugu ukku hides the root rhotic, but its retained initial vowel favors medial assimilation over a concealed initial metathesis. The homophonous steel word d661 has a related heat/melting analysis; merge these only as a sensitivity scenario, not an established etymology of strength from steel.',
        {'Tamil':('R','ura|uram|uravu|uraṉ','Low-vowel full strength forms.'),'Malayalam':('R','uram|urakka','Retained forms.'),
         'Kota':('R','orp- (orpy-)','Vowel-first root with labial extension.'),
         'Kannada':('O','urku|ukku|oraṭu|orṭu|uṭṭu|orpu','Retained medial-r variants plus cluster assimilation.'),
         'Telugu':('O','ukku','Medial r loss/assimilation, initial vowel retained.'),'Toda':('A','u·ṇ|ut-mox|ut-ɨr','Different medial consonant histories; exact formations unresolved.'),
         'Badaga':('R','urudi','Retained coarse/rough formation.')},
        references='DEDR 649',boundary='Velar strength noun is independently represented by Kannada urku, rather than invented from Telugu kk.',mechanism='Medial cluster assimilation; no initial displacement.')
    tokens('d649','Kannada',R='urku|oraṭu|orṭu|orpu',O='ukku|uṭṭu')

    add('d651','mortar','*ur-al; compounds with stone',
        'Ø','u','r','a','VC-a-C','noun',
        'Tamil/Malayalam ural and Kannada oral/oraḷ independently support short u/o before r and low a after it. Tulu oralɯ/uraḷɯ supplies a fourth southern comparison.',
        'Independent agreement supports earlier vowel-first ural, making Telugu rōlu a strong displacement-family case. The displayed *uram-kkal grinding-stone compound is not silently substituted for the simpler mortar noun.',
        '*ur-al > *or-al > *rōl > Telugu rōlu. Literal *roual contraction versus lowering/assimilation followed by initial-vowel loss is not uniquely recoverable. Kannada oral > orḷu > oḷḷu instead loses/assimilates the medial rhotic and retains the initial vowel. Kota oḷkāl contains stone-compound morphology.',
        'Telugu ṟōlu versus rōlu has an alveolar/rhotic transcription issue: original non-Telugu ural supports r, and a separate Telugu r/ṟ history is required. Do not use the later spelling to reconstruct original *ṟ. The d665 rub comparison may make this a derivative of the same root; family sensitivity must collapse mortar and rubbing when assessing independence.',
        {'Tamil':('R','ural','Low-vowel mortar input.'),'Malayalam':('R','ural','Same formation.'),
         'Kannada':('O','oral|oraḷ|orḷu|oḷḷu','Full and medial-assimilated forms.'),'Kodagu':('R','ora','Final lateral loss, initial order retained.'),
         'Tulu':('R','oralɯ|oraḷɯ|uraḷɯ','Vowel and lateral variants, retained order.'),'Kota':('R','oḷka·l|oḷka·l kal','Compound and medial assimilation; vowel remains first.'),
         'Telugu':('D','rōlu|ṟōlu','Displaced mortar noun; r/ṟ variation separately unresolved.'),'Badaga':('R','oralu|oralu kallu','Retained noun and stone compound.')},
        input_confidence='high',references='DEDR 651; PSS83 p.234 example 780; K61 vowel-initial section',
        boundary='Simplex -al noun independently matched; compound stone material not part of its target domain.')
    tokens('d651','Kannada',R='oral|oraḷ|orḷu',O='oḷḷu')

    add('d655','noose, snare','*ur-i/u; *ur-ul and related extensions',
        'Ø','u','r/ṟ','i/u','VC-V / VC-V-l','noun/verb',
        'Malayalam uṟi, Kannada uril/urul and Telugu uri/urulu preserve vowel-first order; exact original r/ṟ and formative i/u vary in the comparison.',
        'Southern and Konda/Kuvi vowel-first forms favor older u–rhotic, while Kui ruhu/rusu probably lost the initial vowel or displaced the rhotic in a separately extended stem.',
        'Telugu uri retains order; urulu/uralu adds a lateral extension. A possible *ur-c > ucc underlies uccu, but this extension is not directly reconstructed from the noose noun alone. Kui *uru-s > ru-s can be aphaeresis; homogeneous vowels cannot independently show exchange. Kuvi huru adds an initial h before the retained u–r sequence.',
        'Kuvi short, long and strengthened-r variants are separate dialect/source observations, not separate roots. Konda ūri lengthens without metathesis. Possible d582 linkage noted by DEDR may alter the deeper analysis; retain uncertainty rather than count uccu as proof of an original palatal.',
        {'Malayalam':('R','uṟi','Vowel-first noose noun.'),'Kannada':('R','uril|urul|uruḷ|ural|urlu|urḷu','Vowel/suffix variants and syncope preserve order.'),
         'Kota':('R','urkl mo·r','Vowel-first compound member.'),'Tulu':('R','urlu','Syncope, no initial movement.'),
         'Telugu':('O','uri|urulu|uralu|uccu','Retained rhotic series plus uncertain medial-assimilation noun.'),
         'Konda':('R','ūri','Long initial vowel retained.'),'Kui':('A','ruhu|rusu','Aphaeresis versus displacement, exact suffix unknown.'),
         'Kuwi':('R',"uru|urru|ūṛṛū ( ūṛka)|ūṛu ogali|uruta herh'nai|huru ( -ka)",'Original vowel before rhotic retained, including h-prothetic form.')},
        references='DEDR 655',boundary='Different noose and verbal extensions distinguished.')
    tokens('d655','Telugu',R='uri|urulu|uralu',A='uccu')

    add('d656','burn, heat, sweat, grief','*ur-u / *ur-i; nominal *ur-u-m and other extensions',
        'Ø','u','r','u/i','VC-V + heat/sweat formations','verb/noun',
        'Tamil uru/uruppu/urumam, Kannada uripu/urupu, Tulu uri and Central Dravidian urj establish a vowel-first heat root. Its formatives independently vary between i and u.',
        'Agreement of southern and central branches favors earlier u–r; eastern rū/rund stems are innovative under cognacy. Telugu uriyu and uralu retain the original order.',
        'A same-u formation *ur-u > *rū can yield Konda rūṇ(u), Kuvi rūh and Pengo rūmi/rūc with further suffixes; shorter Kui ru/rut and Manda rund need distinct cluster/quantity histories. Telugu ummalincu may continue *ur-m with medial assimilation, not initial displacement.',
        'The exact suffix of Konda summer sweat and Pengo sweat is not recoverable from a generic burn root alone. Hume’s earlier VLV > LV example is therefore a family-level generalization, not proof that every *uri derivative moved. Brahui hushing may involve prothesis and consonant change but the r history is unclear. Toda yry contains a vowel represented y, not an initial palatal consonant.',
        {'Tamil':('R','uru|uruppu|uruppam|urumam','Retained high-u formations.'),'Malayalam':('R','uruppam','Retained formation.'),
         'Kota':('R','ury- (urc-)|urc','Retained order.'),'Toda':('O','yry|yrc|uf- (ut-)','Fronted initial vowel and medial consonant developments; no onset promotion.'),
         'Kannada':('O','uripu|urupu|urapu|urisu|ummaḷa|ummaḷisu','Retained roots and medial nasal-assimilated formations.'),
         'Kodagu':('R','uri|uri (-v-, -ñj-)','Retained i formation.'),'Tulu':('R','uri|uriyuni','Retained i formation.'),
         'Telugu':('O','uriyu|uralu|ummalincu|ummalika|ummalinta|ummalimpu','Retained verbs and probable medial nasal assimilation.'),
         'Gondi':('R','urbu','Retained sweat formation.'),'Konda':('D','rūṇ|rūṇu','Sovva nominal displaced series.'),
         'Kui':('D','ru- (rut-)|ruta (ruti-)','Displaced ignite series.'),'Kuwi':('D',"rūinai|rūh- (rūst-)|rund- (-it-)|gāma rūh'nai",'Displaced sweal/sweat/ignite formations; compound gāma is separately glossed sweat.'),
         'Pengo':('D','rūmi|rūc','Displaced sweat formations.'),'Manda':('D','rund','Displaced ignite formation.'),
         'Parji':('R','urj|urjukuḍ','Retained sweat root.'),'Gadaba':('R','urj|uruskur','Retained Ollari/Pottangi series.'),
         'Brahui':('A','hushing|hushinging','Apical and initial h history unresolved.'),'Badaga':('R','uri|huri|uricu|urcu','Retained root, including prothetic h variants.'),
         'Irula':('A','yri-ni·ru|ubbe','Fronted initial-vowel sweat compound versus obscure assimilated noun.')},
        input_confidence='high',references='DEDR 656; Hume 2004 p.226 VLV > LV discussion',
        boundary='Heat, sweat, causative and intensive formatives are not a single invariant V2 environment.')
    tokens('d656','Telugu',R='uriyu|uralu',O='ummalincu|ummalika|ummalinta|ummalimpu')
    tokens('d656','Kannada',R='uripu|urupu|urapu|urisu',O='ummaḷa|ummaḷisu')

    add('d657','form, shape, beauty','regional *ur-u/v; possible adaptation of Sanskrit rūpa',
        'Ø','u','r','u/a','VC-u-v','noun/verb',
        'Tamil urupu/uruvu, Malayalam uruvam and Telugu uruvu/uravu share a vowel-first shape-word family. DEDR explicitly queries derivation from Sanskrit rūpa.',
        'Under inherited analysis the attested regional order is u–r; under borrowing analysis it could arise from prothesis/adaptation of initial rū-. Neither should be silently treated as established.',
        'Regional uru-v gives Telugu uruvu and related forms without metathesis. A loan route rūpa > *urūpa > urupu/uruvu requires prothesis, shortening and labial weakening; evidence here does not select that chain over inherited morphology.',
        'This is a direction-sensitive loan control: treating Tamil urupu as necessarily conservative could reverse the history. Badaga bathing compound urugaṭṭu may have another ancestry; use the simplex uru only as a form witness.',
        {'Tamil':('A','uru|urupu|uruvu','Vowel-first forms, possible Indo-Aryan source.'),'Malayalam':('A','uru|uruvu|uruvam','Same uncertainty.'),
         'Kota':('A','urv|urp','Medial syncope and labial variants.'),'Toda':('A','urp|ušt- (ušty-)','Shape and appear formations, exact common ancestry unresolved.'),
         'Tulu':('A','oru','Vowel-first shape name.'),'Telugu':('A','uruvu|uravu','Retained regional order, deeper direction uncertain.'),'Badaga':('A','uru','Body noun with queried wider ancestry.')},
        eligibility='loan-or-inheritance-uncertain',input_confidence='low',references='DEDR 657, explicit ? < Skt. rūpa-',
        boundary='Labial shape formation; possible borrowing must precede assigning a Proto-Dravidian class.')

    add('d658','ripen, mature, become grey','regional *ur-u / *ur-i',
        'Ø','u','r','u/i','VC-V','verb',
        'Tamil uru ripe and Telugu uriyu agree on vowel-first rhotic with different final vowels. Tulu urve unripe is explicitly queried by DEDR.',
        'Both secure languages retain original-looking u–r order; no initial displacement is observed.',
        'Tamil *ur-u > uru; Telugu *ur-i > uriyu with final glide/vowel morphology, without reordering.',
        'The distinct final vowels prevent treating the two words as the same fully specified u+u input without morphological reconstruction. Queried Tulu unripe semantics needs a privative analysis or alternate cognacy. Do not merge with burn merely because the roots are homophonous.',
        {'Tamil':('R','uru','Retained u formation.'),'Telugu':('R','uriyu','Retained i formation.'),'Tulu':('A','urve','Source queries cognacy and opposite ripeness meaning.')},
        references='DEDR 658 p.64 directly checked',boundary='V2 alternation independently observed; common verbal formation not fully reconstructed.')

    add('d661','melt, steel','*ur-uk(k)-; shorter *ur- forms',
        'Ø','u','r','u','VC-u-k(k)','verb/noun',
        'Tamil uruku/urukku, Malayalam urukuka/urukku and Kannada urku independently support a u-vowel velar formation. The steel noun and melt verb have related but distinct morphological histories.',
        'Southern and Gondi vowel-first forms support older u–r; eastern rūg/rūy is displaced under the melt comparison. Telugu ukku retains the initial vowel and loses medial r.',
        '*ur-ukk > *urkk > ukku gives the Telugu steel noun by syncope/assimilation. *ur-uk > *rūg gives Konda/Kui melt stems through displacement/contraction and voicing. Kui ūra/ūrka retains initial vowel with a long root, whereas rūga displaces it in the velar formation.',
        'Kui is genuinely mixed within one source, so its retained forms cannot be coded missing or assigned to a separate outcome-defined root. Kuvi uku/ukku steel may be a regional technical loan or parallel medial assimilation; either way it is not the same displaced melt formation as rūy. d656 burn is a plausible parent-root relation, to be collapsed in sensitivity counts.',
        {'Tamil':('R','uruku|urukku','Matched intransitive/transitive and steel formations.'),'Malayalam':('R','urukuka|urukkuka|urukku','Matched formations.'),
         'Kannada':('O','urku|ukku','Retained medial r and assimilated steel noun.'),'Kodagu':('O','ur- (uri-)|urɨk- (urɨki-)|ukkɨ','Retained melt verbs and assimilated steel noun.'),
         'Kota':('O','uk','Assimilated steel noun.'),'Telugu':('O','ukku','Medial r assimilation, not initial metathesis.'),
         'Gondi':('R','urī|uṛi|urih- (<i>Voc.</i> 262)|urh- (<i>Voc.</i> 262)','Retained melt/transitive series.'),
         'Konda':('D','rūg','Displaced melt stem.'),'Kui':('M','ūra (ūri-)|ūrka (ūrki-)|rūga (rūgi-)','Long retained melt formations alongside displaced velar form.'),
         'Kuwi':('A','rūy|rūkʰnai|uku|ukku','Displaced melt verbs plus assimilated or borrowed steel nouns.'),'Badaga':('R','urugu','Retained melt verb; body uru record excluded.')},
        input_confidence='high',references='DEDR 661 p.64 directly checked',boundary='Melt verb, plural-action formation and steel noun analyzed separately.')
    tokens('d661','Kannada',R='urku',O='ukku')
    tokens('d661','Kodagu',R='ur- (uri-)|urɨk- (urɨki-)',O='ukkɨ')
    tokens('d661','Kui',R='ūra (ūri-)|ūrka (ūrki-)',D='rūga (rūgi-)')
    tokens('d661','Kuwi',D='rūy|rūkʰnai',A='uku|ukku')

    add('d663','pierce, penetrate','*ur-uv- / *ur-c-; labial nasal extension',
        'Ø','u','r','u/zero','VC-u-v / VC-c','verb',
        'Tamil/Malayalam uruvu and Kannada urcu independently support vowel-first rhotic. Tulu urumbuni supplies a nasal-labial formation beside rummuni.',
        'Independent full forms favor u–r; Telugu uccu can arise by medial cluster assimilation, while Tulu rummuni is compatible with a local initial-loss history.',
        '*ur-c > ucc yields Telugu uccu, Kannada uccu and Parji ucc, preserving initial vowel. Tulu urumbuni > rummuni would combine initial-vowel loss with nasal/labial assimilation; a literal u/r swap is not distinguishable with identical u vowels. Kuvi uh/ust reflects another medial cluster development.',
        'Do not infer hidden initial metathesis from the absence of r in Telugu: the independent Kannada urcu : uccu comparison supports medial assimilation directly. Kurux hurnā/huṛnā has an added initial h but retains the root vowel before r. Shared ucc forms could also diffuse; no precise shared-innovation date follows.',
        {'Tamil':('R','uruvu','Retained labial formation.'),'Malayalam':('R','uruvuka','Retained labial formation.'),
         'Kannada':('O','urcu|uccu','Full cluster and assimilated counterpart.'),'Tulu':('A','urumbuni|rummuni','Retained and initial-loss/assimilation variants.'),
         'Telugu':('O','uccu','Medial rhotic assimilation.'),'Parji':('O','ucc','Medial rhotic assimilation.'),
         'Kuwi':('O','uh|uh- (ust-)','Medial consonant changes, initial vowel retained.'),'Kurux':('R','hurnā|huṛnā','Prothetic h, vowel before root rhotic.'),
         'Badaga':('O','uccu','Assimilated penetrate verb; top adjective/cognacy requires separate check.')},
        input_confidence='high',references='DEDR 663 p.64 directly checked',boundary='-c cluster independently established by Kannada; Tulu nasal-labial formation separate.',mechanism='Medial cluster assimilation; Tulu initial loss or displacement not uniquely resolved.')
    tokens('d663','Kannada',R='urcu',O='uccu')
    tokens('d663','Tulu',R='urumbuni',A='rummuni')

    add('d664','roll, round object, wheel, egg','*ur-uḷ-; *ur-uṇṭ- and low-vowel variants',
        'Ø','u','r','u/a','VC-V-lateral / nasal-stop formation','verb/noun',
        'Tamil uruḷ/uruṇṭai, Malayalam uruḷ/uruṇṭa and Kannada uruḷ/uraḷu/uraṇṭu independently establish r before later lateral/nasal-stop material. Original DEDR p.64 restores Telugu uralu/urlu/oralu, mislabeled Kodagu in the database.',
        'Broad r-before-lateral agreement supports earlier urVḷ. Telugu uṇḍa loses/assimilates medial r in a round-object formation; Pengo rōnḍa/Manda runḍa promote r under the proposed egg-from-round comparison.',
        'Telugu *ur-aḷ > uralu > urlu retains initial order; *uruṇṭ > *urṇḍ > uṇḍa loses r medially. *urṇḍ > uṇḍr could instead underlie uṇḍramu/uṇḍrālu, but suffixal r or analogy is not excluded. Pengo *ur-aṇḍ > *rōṇḍ and Manda *ur-uṇḍ > runḍ are conditional different-vowel paths; neither exact egg input is independently fixed.',
        'The existence of Kannada both u and a does not license choosing whichever vowel produces the eastern outcome. Pengo egg is long rōnḍa, explicitly corrected by DEN1; Manda is short runḍa. Irula ruḷḷu/ruṭṭu may reflect local aphaeresis and strengthening. Sanskrit round-lump words are contact comparisons. Modern Telugu round-cake derivatives count once, and their possible medial r transposition is separate from initial metathesis.',
        {'Tamil':('O','uruḷ|uruṇṭai|uruṭṭu|uṇṭai','Retained fuller series and medial-loss round noun.'),'Malayalam':('O','uruḷ|uruṇṭa|uruṭṭuka|uṇṭa','Same distinction.'),
         'Kannada':('O','uruḷ|uraḷu|urḷu|uṇṭu','Full roots/syncope and medial assimilation.'),
         'Kodagu':('R','urɨḍ- (urɨṇḍ-)|urɨṭ- (urɨṭi-)','Only these verb paradigms belong to Kodagu in source.'),
         'Tulu':('O','uruṇṭɯ|uruṇḍulu|urṇḍelɯ|urṇḍe|urṇa|uṇḍɛ','Source-corrected full and reduced round nouns.'),
         'Kota':('O','urṇ- (urḍ-)|urṭ- (urṭy-)|uṇḍ|uṇḍy','Full rhotic verbal clusters and reduced round nouns.'),
         'Toda':('O','u·ḷ- (u·ḍ-)|u·ṭ- (u·ṭy-)|uḍy','Medial r loss with quantity/voice changes.'),
         'Telugu':('O','uralu|urlu|oralu|uṇḍa|uṇṭa|uṇḍramu|uṇḍrālu|uṇḍrāḷḷu','Retained roll verbs, assimilated nouns and possible later medial-r transposition.'),
         'Gondi':('O','undā','Reduced round noun.'),'Konda':('O','uṇḍa','Reduced wheel noun.'),'Gadaba':('O','unḍa','Reduced wheel noun.'),
         'Kuwi':('O','uṇḍa|unḍe|ūnda|uṇḍḷa','Reduced nouns; long variant separate.'),
         'Pengo':('A','rōnḍa','Egg comparison and precise vowel history uncertain.'),'Manda':('A','runḍa','Egg comparison and precise vowel history uncertain.'),
         'Kurux':('A','oḷᵒṇḍārnā','Possible r/l redistribution or suffix changes; initial vowel retained.'),
         'Badaga':('R','uruṇde|urundu|uruṭtu','Retained roll/round formations.'),'Irula':('A','ruḷḷu (ruṇḍ-)|ruṭṭu','Local initial loss versus displacement with strengthening.')},
        input_confidence='high',references='DEDR 664 p.64 directly checked; DEN1 p.401 Pengo correction',
        boundary='Verb, round-object noun and egg comparison distinguished; exact egg formative vowel unestablished.')
    tokens('d664','Telugu',R='uralu|urlu|oralu',O='uṇḍa|uṇṭa',A='uṇḍramu|uṇḍrālu|uṇḍrāḷḷu')
    tokens('d664','Tamil',R='uruḷ|uruṇṭai|uruṭṭu',O='uṇṭai')
    tokens('d664','Malayalam',R='uruḷ|uruṇṭa|uruṭṭuka',O='uṇṭa')
    tokens('d664','Kannada',R='uruḷ|uraḷu|urḷu',O='uṇṭu')
    tokens('d664','Tulu',R='uruṇṭɯ|uruṇḍulu|urṇḍelɯ|urṇḍe|urṇa',O='uṇḍɛ')
    tokens('d664','Kota',R='urṇ- (urḍ-)|urṭ- (urṭy-)',O='uṇḍ|uṇḍy')
