"""Additional initial-i comparisons, including Telugu gaps and nasal controls."""

def populate(add,tokens):
    add('d444','pinch, pincers, tongs','*iṭ-uk-; distinct tool-name formations',
        'Ø','i','ṭ','u','VC-u-CC','verb/noun',
        'Tamil/Malayalam iṭukku and iṭukki independently support high u after ṭ. Kannada iḍaku provides a low-vowel variant, while Old Kannada iẓkuẓi has a different apical and internal structure.',
        'Vowel-first southern pinch verbs favor earlier V–apical order, but the tool nouns do not all share an independently recoverable complete stem.',
        'Tamil *iṭ-uk > iṭukku retains order. Kannada ikkuẓ and Tulu ikkuḷ may involve medial assimilation of the first apical, leaving another apical after k; alternatively their internal apical order reflects a different noun formation. Kui ḍīpa is an initial-displacement candidate, but i+u does not straightforwardly produce ī and its labial noun suffix differs.',
        'No Telugu attestation in this database group: record a gap, not a failure to change. Reconstructing *iṭi-pp solely to predict Kui ī would be circular. A source paradigm connecting the pinch verb to a labial noun, or an independently attested i-bearing formative, would distinguish contraction from another etymology. The superficial k/l reversal in tongs needs its own analysis, not the initial-metathesis label.',
        {'Tamil':('R','iṭukku|iṭukki|iṭṭiṭai','Singleton high-u base plus distinct strong tool formation.'),
         'Malayalam':('R','iṭukku|iṭukki|iṭukkuka','Independent u-bearing pinch paradigm.'),
         'Kannada':('A','iḍaku|ikkuṛ̆|ikkuṛ̆a|ikkaṛ̆a|ikṛ̆a','Retained verb; medial-loss or distinct-formation tool nouns.'),
         'pampa':('A','iṛ̆kuṛ̆i','Two apicals and different phoneme; cannot be treated as a simple iṭuk derivative without argument.'),
         'Tulu':('A','iḍumbulu|ikkuḷi|ikkuḷe|ikkuḷu','Retained pinch formation and complex tool names.'),
         'Kota':('A','ikḷ','Tool-name medial consonant ancestry unresolved.'),
         'Kui':('A','ḍīpa','Probable initial displacement, but matching input vowel and labial formation unestablished.')},
        references='DEDR 444 p.43 directly checked',eligibility='core-formation-uncertain',input_confidence='medium',
        boundary='Velar verb/tool formation independently supported; labial Kui tool formation must be reconstructed separately.')
    tokens('d444','Kannada',R='iḍaku',A='ikkuṛ̆|ikkuṛ̆a|ikkaṛ̆a|ikṛ̆a')
    tokens('d444','Tulu',R='iḍumbulu',A='ikkuḷi|ikkuḷe|ikkuḷu')

    add('d451','parch, roast grain','Kurux–Malto *i/eṛ-; deeper apical source unresolved',
        'Ø','i/e','ṛ','unknown','VC plus language-specific inflection','verb',
        'Kurux iṛnā and Malto eṛye agree on vowel before retroflex rhotic. This two-language comparison does not recover a uniquely Proto-Dravidian ṭ/ẓ input or a formative vowel.',
        'Both attested branches preserve V–ṛ; there is no displacement contrast from which to infer an earlier opposite order.',
        'Regional *i/eṛ- plus distinct Kurux -nā and Malto -ye endings gives the forms with order retained. The first-vowel correspondence needs the wider Kurux–Malto system, not an outcome-selected assumption.',
        'Retain as a northern apical-root comparison, with Telugu and other SCDr unattested. It does not create seven negatives for languages with no cognate. The imported reconstruction is regional even when the interface groups it under PDr.',
        {'Kurux':('R','iṛnā','Vowel-first parch verb.'),'Malto':('R','eṛye','Vowel-first cognate, quality correspondence unresolved.')},
        references='DEDR 451 p.44',eligibility='regional-input-only',input_confidence='medium',
        boundary='Infinitival endings are language-specific; no unattested common V2 invented.')

    add('d452','wall','regional *iṬ-V-p; Ṭ likely retroflex, V2 unknown',
        'Ø','i','ṭ','unknown','VC-(V)-p','noun',
        'Kolami Kinwat iṛp and Gondi Muria ḍīpi form the comparison. The database incorrectly assigns both to Kolami; source DEDR p.44 explicitly switches language.',
        'Kolami vowel-first order and the regular possibility of retroflex-rhotic correspondence favor *iṬVp, but only one unshifted language is available; initial prothesis/loan history remains possible.',
        'Conditional *iṭ-i-p > *ḍīp > Gondi ḍīpi would fit equal-vowel contraction, whereas Kolami iṛp could reflect medial syncope. However the missing formative i is not independently observed and must not be used as a deterministic prediction.',
        'Treat Gondi as a probable but uncertain displacement case, not a dialectal Kolami D/R alternation. More wall nouns or a source derivational base could establish V2 and direction. No Telugu form is supplied; this is a comparative gap there.',
        {'Kolami':('R','iṛp','Source-corrected Kinwat vowel-first form.'),
         'Gondi':('A','ḍīpi','Source-corrected Muria form; input vowel/loan direction unresolved.')},
        references='DEDR 452 p.44; DEN2 p.475 S²8',eligibility='cognacy-or-input-uncertain',input_confidence='medium',
        boundary='Final labial matches; no independent common formative vowel survives in the pair.')

    add('d453','touch, feel','regional *iṭ-(V)-; velar extension, quantity unresolved',
        'Ø','i','ṭ','unknown','VC-(V)-k / VC-C','verb/noun',
        'Gondi iṭ/iṭṭānā provides the vowel-first branch; Kui ḍīga, Kuvi dīg-/dī- and Pengo ḍū- have initial apicals. The imported *ḍū cannot simply be accepted as ancestral to all.',
        'Gondi order plus the recurring ṭ/ḍ correspondence supports a vowel-first regional input provisionally, but the common vowel and velar formative are not uniquely reconstructed.',
        'A hypothesized *iṭ-i-k would contract to ḍīk and yield Kui/Kuvi ḍīg-. Pengo ḍū requires a different vowel or subsequent rounding, neither demonstrated here. Gondi gemination in the long citation form may be paradigm-specific; short iṭ is also attested.',
        'Four Kuvi forms were parsed as Kui and are research-corrected. This is not five Kui variants with Kuvi missing. The whole comparison remains an uncertain mechanism test until independent i/u formative evidence and the Gondi tense classes are checked. No Telugu token is supplied.',
        {'Gondi':('R','iṭ|iṭṭānā','Short stem and strong citation form preserve order.'),
         'Kui':('A','ḍīga (ḍīgi-)','Initial-displacement candidate with long ī and velar extension.'),
         'Kuwi':('A','dīgali|dīginai|dīnai|ḍīg- (-it-)','Corrected language labels; velar loss and source variation preserved.'),
         'Pengo':('A','ḍū- (-t-)','Initial stop, but ū has no demonstrated origin from the Gondi i input.')},
        references='DEDR 453 p.44 directly checked',eligibility='core-formation-uncertain',input_confidence='medium',
        boundary='Velar present in Kui/Kuvi but absent Pengo; neither its vowel nor the exact Gondi strong-stem ancestry forced.')

    add('d454','notched timber block, mortice','regional *iṭṭaṟa / *iṭṭire',
        'Ø','i','ṭ','a/i','VCCVCV','noun',
        'Malayalam iṭṭaṟa and Tulu iṭṭarɛ/iṭṭire independently support initial i plus geminate ṭṭ in the shared carpentry term.',
        'Both source languages are vowel-first; no positive supports an earlier initial ṭi order.',
        'Retained iṭṭ- with later a/i variation and regular source orthographic r/ṟ difference; exact later rhotic correspondence is not settled by the first syllable.',
        'A regional geminate control, with no Telugu attestation. Ultimate borrowing or specialized compound origin is possible; it cannot be projected as a securely Proto-Dravidian technical term solely from two languages.',
        {'Malayalam':('R','iṭṭaṟa','Geminate block noun.'),'Tulu':('R','iṭṭarɛ|iṭṭire','Two vowel variants, both retain initial order.')},
        references='DEDR 454 p.44',eligibility='geminate-contact-control',c2_structure='geminate',input_confidence='high',
        boundary='Whole technical word compared; no independently established inner morpheme division.')

    add('d457','join, equal, pair','*iṇ-ay / *iṇ-aŋk-; nasal control',
        'Ø','i','ṇ','a','VC-ay / VC-a-NC','verb/noun',
        'Tamil iṇai/iṇaŋku, Malayalam iṇa/iṇayuka, Kannada eṇe and Telugu ena/enayu support a retroflex nasal after an initial vowel, and low formative independently.',
        'Agreement supports earlier iṇ-, with Telugu ṇ>n and southern lowering. Telugu nenayu retains a second n as well as an initial n, so it is not the result of simply moving the sole root nasal.',
        '*iṇ-ay > *eṇay > enayu; derivative enucu/enupu has distinct palatal/labial morphology. nenayu can reflect added n through rebracketing or analogical reinforcement, but a source context is needed to choose. Tamil eḷḷu equal is explicitly questioned by DEDR and is not secure proof of a nasal/lateral root alternation.',
        'A control for the published exclusion of nasal C2. The initial n in nenayu cannot be counted as metathesis on surface inspection. The n survives medially, so deletion-plus-insertion or morphology would be required under a movement account. Comparison with iẓai d507 is tentative.',
        {'Telugu':('A','ena|enayu|eniyu|enucu|enupu|enika|enike|nenayu','Retained main forms; initial n addition in one variant unresolved.'),
         'Tamil':('A','iṇai|iṇaŋku|iṇakku|eḷḷu','Secure nasal base, queried lateral comparison.'),
         'Malayalam':('R','iṇa|iṇayuka|iṇekka|iṇaŋŋuka','Order retained across formations.'),
         'Kannada':('R','eṇa|eṇe','Lowered root vowel, order retained.'),'Kodagu':('R','əṇe|əṇe a·ḍ','Nominal and mating construction retain order.'),
         'Tulu':('R','iṇɛ|inɛ','Nasal place variants, no relocation.')},
        references='DEDR 457 p.44 directly checked; K03 Rule20 excludes nasal apicals',eligibility='nasal-control',input_confidence='high',
        boundary='Low-vowel formative independently attested; the extra initial n in nenayu needs a separate morphological account.')
    tokens('d457','Telugu',R='ena|enayu|eniyu|enucu|enupu|enika|enike',A='nenayu')
    tokens('d457','Tamil',R='iṇai|iṇaŋku|iṇakku',A='eḷḷu')

    add('d472','beg, borrow','*ir-a / *ir-av-',
        'Ø','i','r','a','VC-a / VC-a-v','verb/noun',
        'Tamil ira/iravu, Malayalam iravu/irakkuka, Kannada era/eravu and Telugu eravu independently support i/e before r and a low formative.',
        'The widespread vowel-first form, corroborated by Malto irɣre, favors original ir-; Tulu randuni is innovated under this comparison.',
        '*ir-av > *erav > Telugu eravu preserves the order despite an input that could permit contraction. Tulu randuni may follow initial vowel loss in a nasal-bearing begging formation; its exact preceding full form is not attested here.',
        'Do not explain Telugu retention by assigning an unsupported high formative: southern av words directly match its loan noun. Late lexical borrowing remains possible but is not documented, so this stays a genuine low-vowel retention counterexample. Tulu verbal morphology differs from eravu and does not prove a shared event.',
        {'Telugu':('R','eravu','Low-formative retained noun.'),'Tamil':('R','ira|iravu|iraval','Low-vowel base and derivatives.'),
         'Malayalam':('R','iravu|irakkuka|irappu','Order retained.'),'Kannada':('R','era|ere (erad-)|eravu|eraval','Lowering with retained order.'),
         'Kodagu':('R','era- (erap-, erand-)|erapə|erapaci','Verbal paradigm and agent nouns.'),
         'Tulu':('A','eravu|randuni|randelɯ','Retained lending noun, initial-loss verbal derivative uncertain.'),
         'Malto':('R','irɣre','Retained order, extended borrowing verb.')},
        references='DEDR 472',input_confidence='high',
        boundary='av noun matched in several languages; Tulu nd verb is a different formation, not a reason to change its input class.')
    tokens('d472','Tulu',R='eravu',A='randuni|randelɯ')

    add('d490','food, prey','*ir-ay',
        'Ø','i','r','a','VC-ay','noun',
        'Tamil irai/erav, Malayalam ira, Kannada ere, Kota er and Telugu era independently support a vowel-first r with low a/ay formation.',
        'The cross-branch agreement, including Brahui iraɣẖ food, favors earlier ir- rather than repeated prothesis before a hypothetical rē.',
        '*ir-ay > *eray > Telugu era, Kannada ere and Kota er with lowering/final contraction while maintaining V–r order. Brahui has a different final extension.',
        'A genuine simple low-vowel retention comparison, semantically basic and not source-marked as a loan. No attested SCDr comparison in this group besides Telugu: missing elsewhere is not retention. Full Brahui suffix reconstruction is unnecessary for the initial-order observation but remains unresolved.',
        {'Telugu':('R','era','Retained food noun.'),'Tamil':('R','irai|erav','Source lect and final-consonant variants retained.'),
         'Malayalam':('R','ira','Retained prey/food noun.'),'Kannada':('R','ere','Retained order after lowering.'),
         'Kota':('R','er','Final loss, initial order retained.'),'Brahui':('R','iraɣẖ','Vowel-first food noun, final suffix different.')},
        references='DEDR 490',input_confidence='high',
        boundary='ay formation independently supported in southern comparison; Brahui final material not equated mechanically.')
