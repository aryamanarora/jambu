"""The numeral two: one root family, several independently defined formations."""

def populate(add,tokens):
    add('d474','two','*īr / *ir-V; nonhuman *ir-aṇ-ṭ; human *ir-u-var',
        'Ø','i','r','a/u','VC-V + gender/number formation','numeral',
        'Tamil iru-/īr, Kannada iru/ir and eraḍu, Central Dravidian ir- forms and Brahui irā/iraṭ support vowel-first order independently. Nonhuman aṇṭ and human u-var formations can be distinguished by their morphology before their outcomes are inspected.',
        'Wide independent retention of bound ir-/īr and the different human and nonhuman derivatives favors earlier ir-, not original r- with prothesis throughout the family. The shared r-initial nonhuman numeral across SCDr is strong comparative evidence, but recent Tamil/Malayalam/Tulu initial loss must be evaluated separately.',
        'K03 pp.159–160: *ir-aṇṭ > *eraṇḍ > hypothetical *rēṇḍ > Telugu reṇḍu with shortening before a nasal-stop cluster; other SCDr *ir-i/u-ṇṭ > *rīṇḍ with variable shortening and Konda backing to runḍi. Human *iru-var remains vowel-first in Telugu iruvuru and Gondi irvur; r+v assimilation yields Kannada/Old Telugu ibbar forms. Tamil/Malayalam/Tulu aphaeresis produces reṇṭu/raṇṭu/raḍḍɯ in later language histories. Malto *irw > iwr (corpus ivr) is a separate medial consonant transposition.',
        'Do not count human, nonhuman, twenty, two hundred and ordinal derivatives as independent roots. Telugu retained iru/īr is a bound root and cannot be treated as an identical free-word input to reṇḍu. The short Telugu output does not prove that a long intermediate existed; *rēṇḍ is K03’s conditional reconstruction. Kui rīnḍe shows that pre-cluster shortening was not universal across languages. Konda iddum retains an initial vowel in a measure compound and needs separate cluster-assimilation/contact analysis. Kodagu daṇḍɨ, Markodi dad and Badaga ratte require local phonological/contact histories; do not automatically equate them with the SCDr innovation. Kurux ēṇḍ has a vowel history K03 explicitly calls puzzling. Toda ačok/acok is a measure term within an example, not another reflex of two.',
        {'Telugu':('M','reṇḍu|reṇḍava|reṭṭa|reṭṭi|reṭṭincu|reṭṭimpu|reṇṭa|renca|iru|īr- = reṇḍu|iruvuru|iruguru|iruvadi|iruvai|iddaṟu|in-nūṟu|inu māṟu|panneṇḍu','Free numeral displaced; bound/human forms retained or assimilated; one root.'),
         'OTelugu':('O','ibbaru|ibbaṇḍru','Human formation retains initial vowel with medial assimilation/added plural material.'),
         'Tamil':('O','iraṇṭu|reṇṭu|iru (before consonant)|īr|iruvar|iraṭṭai','Retained forms and later colloquial aphaeresis.'),
         'Malayalam':('O','raṇṭu|iraṭṭi|iruvar|īr|iru (before consonant)','Free numeral initial loss, bound/human forms retained.'),
         'Kota':('R','eyḏ|ir va·d|i·r a·ṛ','Initial vowel survives; medial/final correspondences differ by formation.'),
         'Toda':('R','ēḍ|īr ōṛ|īr ak','Vowel first; formation-specific medial changes.'),
         'Kannada':('O','eraḍu|erḍu|eraṛ̆|iru|ir|irvar|irbar|ibbar|irpattu|ippattu|innūṟu','Retention plus medial assimilation, no initial apical promotion.'),
         'Kodagu':('A','daṇḍɨ|daṇḍane|pann-eraṇḍɨ|iru-vadɨ|i·r a·ṇḍɨ|ibba','Initial-loss and rhotic-to-stop history of free numeral unresolved; bound formations preserve older order.'),
         'Tulu':('O','raḍḍɯ|raḍḍanɛ|irɯ|ir|irverɯ|irva','Local initial loss versus bound/human retention.'),
         'Gondi':('M','ranḍ|ranḍu|renḍ|ranṭe|rancē|rahk rahk|irvur|irvuṛ|iruṛ|irū|irūr|iver|ivir|ivur','Nonhuman displacement, human original order with medial variation.'),
         'Konda':('A','ri|riˀ|runḍi|riˀ er|rineṇḍ|riyaŋa|iddum','Displaced numeral formations; measure-compound iddum has a separate retained/assimilated history.'),
         'Kui':('D',"rī|ri|rīnḍe|rīnḍi|rinḍi|rīaru|ri'er|ri'ari|rīhe",'Displacement generalized across free/bound/human formations; quantity varies by source.'),
         'Kuwi':('D',"rī|ri|rīari|riari|ri'ari|rindi|riṇḍi|ri'ni",'Source/lect quantity and consonant variants preserved.'),
         'Pengo':('D','ri|rikar|rinḍek|rinḍaŋ','All sampled grammatical formations displaced.'),
         'Manda':('D','ri|rikar|rikehiŋ','All sampled grammatical formations displaced.'),
         'Kolami':('O','indiŋ|iddar|i·ral|in nal|irve','Retention of initial vowel; apical loss/assimilation in some formations.'),
         'Naikri':('O','indiŋg|iddar|iraḷ|ernḍi|iroṭel|iroṭer|ira|ir nān','Source lect and grammatical variants preserved; no initial r.'),
         'Parji':('R','irḍu|irul|iral|ir|iroṭ','Order retained across gender/count formations.'),
         'Gadaba':('O','inḍi|iḍḍig|irul|iral|ir','Initial vowel retained; medial assimilation in nonhuman forms.'),
         'Kurux':('R','ēṇḍ|ē̃ṛ|irb|irbar|irbarim','All vowel first; vowel quality and final cluster history separately uncertain.'),
         'Malto':('R','ivr|ivresti|is|isti','Initial vowel retained; medial rw reversal tracked on another process axis.'),
         'Brahui':('R','iraṭ|irā','Vowel-first free and attributive numeral.'),
         'Badaga':('A','eradu|ratte|ratte kūsu|iru nūru|ibba|ippattu','Basic eradu retains order; ratte double may be local loss/contact, other derivatives assimilate.'),
         'Irula':('O','raṇḍu|reṇḍu','K03 discusses local aphaeresis, with possible Tamil borrowing of reṇḍu.'),
         'Koraga':('R','eyḍi','Initial vowel retained after medial cluster changes.'),
         'markodi':('A','dad|dadᵘ|daḍ|irupatu|ŭrupāt|pāndraṇd|pandraṇd','Free numeral has local initial-loss/stop outcome; compounds preserve vowel/r material.')},
        references='DEDR 474 p.46 directly checked; K03 pp.159–160 and p.116; Hockings–Pilot-Raichoor 1992 pp.54,86,507; Canvin 2025 lect data',
        quantity='short-and-long-bound-allomorphs',input_confidence='high',confidence='high',
        boundary='Bound īr/iru, nonhuman aṇṭ and human u-var are independently motivated categories; comparisons/counts must not treat them as repeated independent etyma.')
    tokens('d474','Telugu',D='reṇḍu|reṇḍava|reṭṭa|reṭṭi|reṭṭincu|reṭṭimpu|reṇṭa|renca',
           R='iru|īr- = reṇḍu|iruvuru|iruguru|iruvadi|iruvai',O='iddaṟu|in-nūṟu|inu māṟu',A='panneṇḍu')
    tokens('d474','Tamil',R='iraṇṭu|iru (before consonant)|īr|iruvar|iraṭṭai',O='reṇṭu')
    tokens('d474','Malayalam',O='raṇṭu',R='iraṭṭi|iruvar|īr|iru (before consonant)')
    tokens('d474','Kannada',R='eraḍu|erḍu|eraṛ̆|iru|ir|irvar|irbar|irpattu',O='ibbar|ippattu|innūṟu')
    tokens('d474','Kodagu',A='daṇḍɨ|daṇḍane',R='pann-eraṇḍɨ|iru-vadɨ|i·r a·ṇḍɨ',O='ibba')
    tokens('d474','Tulu',O='raḍḍɯ|raḍḍanɛ',R='irɯ|ir|irverɯ|irva')
    tokens('d474','Gondi',D='ranḍ|ranḍu|renḍ|ranṭe|rancē|rahk rahk',R='irvur|irvuṛ|iruṛ|irū|irūr',O='iver|ivir|ivur')
    tokens('d474','Konda',D='ri|riˀ|runḍi|riˀ er|rineṇḍ|riyaŋa',A='iddum')
    tokens('d474','Kolami',O='indiŋ|iddar|in nal',R='i·ral|irve')
    tokens('d474','Naikri',O='indiŋg|iddar',R='iraḷ|ernḍi|iroṭel|iroṭer|ira|ir nān')
    tokens('d474','Gadaba',O='inḍi|iḍḍig',R='irul|iral|ir')
    tokens('d474','Badaga',R='eradu|iru nūru',A='ratte|ratte kūsu',O='ibba|ippattu')
    tokens('d474','markodi',A='dad|dadᵘ|daḍ',R='irupatu|ŭrupāt|pāndraṇd|pandraṇd')
