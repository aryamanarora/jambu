"""Research-only source corrections; the database and frozen corpus remain intact.

Every correction names a stable form ID, the original value, and source evidence.
These are adjudications in this investigation, not an ingestion into Jambu.
"""
CORRECTIONS = {}
def relabel(ids, old, new, source, reason):
    for fid in ids.split('|'):
        CORRECTIONS[fid]={'Field':'Language_ID','Original_Value':old,
                          'Research_Value':new,'Evidence':source,'Reason':reason}

relabel('f_i34pukz24dqqw|f_l6xtr2xed6gts|f_rdt7u6xcpmj2y|f_wb53yd7odaxz6','Kannada','Kodagu',
        'DEDR946 p.91; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=91; directly read 2026-09-09',
        'The oḍe/oḍa paradigms and following noun/deverbal belong after explicit Koḍ. heading.')

relabel('f_5tju2dg66a4wg','Telugu','Parji',
        'DEDR835 p.81; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=81; directly read 2026-09-09',
        'iluŋg follows the explicit Pa. heading; the previous Telugu verb gloss swallowed that heading.')
relabel('f_o24524gveulpu|f_vajx63tptoexe|f_wyiw73bq3gwc6','Kodagu','Tulu',
        'DEDR809 p.79; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=79; directly read 2026-09-09',
        'Only ett- (etti-) is Kodagu; ettāḍuni, ettɯ and ekkɯ follow Tu. and B-K.')

relabel('f_a7ipt7v7skt22|f_fo5alzbe4sjpy|f_gmoyvnsayoiga|f_ldltkt2zezxdo','Manda','Kuwi',
        'DEDR 705 p.69; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=69; directly read 2026-09-09',
        'The four onion/garlic forms follow Kuwi, with F./S./Su. source labels; only preceding uli is Manda.')

relabel('f_7j45i7plicrwm|f_k2ix3adnipdwm|f_mhhhpmvyrmfee','Kodagu','Telugu',
        'DEDR 664 p.64; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=64; directly read 2026-09-09',
        'uralu/urlu/oralu follow Te. in the original; a missed language switch attached them to Kodagu.')
relabel('f_5iyhofvsla4v2|f_c3n2jsofrzp4s|f_cds7ss3ibcus6|f_fkuwrlq5apamq|f_oqs3d7c7m3z5i|f_uddy4fbfyz3u6|f_uee7dtwtla532|f_v6iobv7g5c4yo|f_y4k4qaqxqyomk','Kodagu','Tulu',
        'DEDR 688 p.67; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=67; directly read 2026-09-09',
        'Only preceding ūḷ plough paradigm is Kodagu; nine subsequent plough/song forms follow Tu.')
relabel('f_xn35byczjqea2','Gondi','Kui',
        'DEDR 695 p.68; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=68; directly read 2026-09-09',
        'Queried rūṭpa follows the Kui heading and is not a Gondi form.')
relabel('f_a6nyxlm7cjw6i|f_s5g2bd3nynvu2|f_7t3fatoa3mjay|f_kek56negcdvjg|f_udfxvvixjx2ik','Kodagu','Tulu',
        'DEDR 664 p.64; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=64; directly read 2026-09-09',
        'Five round/cake forms follow Tu. in the original; only two preceding roll-verb paradigms are Kodagu.')

relabel('f_7wyepvkx6uqdo|f_st3scffpxz4nm|f_wgn7ssdwgyjiw|f_xvmvtpdunbcoa|f_ybkj7hvpl54na',
        'Gondi','Konda','DEDR 260, p.25; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=25; directly read 2026-09-09',
        'The original entry places these five forms after the explicit Konḍa heading; the preceding Gondi Koya all- is a different record. The source parser failed to switch language here.')

relabel('f_bmevygelp5lac|f_f7qgdtpmoqkye|f_n2s7u3y35zyiy|f_r2ibwhzctmxp2|f_yc5x4flmsczgk',
        'Malayalam','Kannada','DEDR 242, p.23; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=23; directly read 2026-09-09',
        'These five pulse-name forms occur after Ka. in the source; only alaśaṇṭa and alasāndram are Malayalam.')

SOURCE_ISSUES = [
    {'Form_ID':'f_cu4amtk2eqzri','Entry_ID':'d1818','Issue':'Long porridge reconstruction attached to hollow/pit',
     'Disposition':'Exclude from pit/tube input classification; actual short and long formations require their own comparisons',
     'Evidence':'DEDR 1818 pit/tube reflexes; unrelated K03 porridge gloss'},
    {'Form_ID':'f_6fgvgegslhanw','Entry_ID':'d2018','Issue':'Badaga plant kliūgidu linked to friend/kindred despite distinct Kannada kriyā comparison',
     'Disposition':'Do not count plant cluster as inherited friend-root displacement; classify linkage/cognacy unresolved',
     'Evidence':'Badaga record gloss explicitly plant with Kannada kriyā + Badaga gidu, unlike DEDR 2018'},
    {'Form_ID':'f_bciwzeefupo34;f_eul3jbf66u7yu;f_fy5meitvwzth4','Entry_ID':'d4866','Issue':'English gloss words parsed as Tamil forms; gulp appended to muẓuŋku',
     'Disposition':'Exclude consume/devour and malformed appended-gloss record; retain independently parsed miẓuŋku and original source',
     'Evidence':'DEDR 4866 lexical versus English-gloss distinction'},
    {'Form_ID':'f_bizfzqn6oj7je','Entry_ID':'d698','Issue':'Seventh-century date duplicated from preceding Old Telugu oḷana onto lōna',
     'Disposition':'Use undated source-only lōna and preserve raw record; ḷōna is explicitly ninth–tenth century',
     'Evidence':'DEDR 698 p.68 directly checked; oḷana, not lōna, bears seventh-century parenthesis'},
    {'Form_ID':'d710;f_yl4fmzonetbjm','Entry_ID':'d710','Issue':'Shark reconstruction linked to happen/be fit',
     'Disposition':'Exclude *coṯ-ac from root reconstruction and class assignment',
     'Evidence':'DEDR 710 p.70 directly checked: uṟu happen and related formations'},
    {'Form_ID':'f_fv4ejpqhhooyg;f_u4qjadj52fldi','Entry_ID':'d672','Issue':'Kuruba pestle alke and heading fragment parsed as Malayalam',
     'Disposition':'Exclude from Malayalam comparison; Kuruba language identifier unresolved',
     'Evidence':'DEDR 672 source formatting: Kurub. (LSB 1.11) alke'},
    {'Form_ID':'f_d6ykhtysg47w6;f_emynt4gsbupp6','Entry_ID':'d695','Issue':'Kui and Konda headings embedded in forms assigned Gondi',
     'Disposition':'Use source-supplemented Kui ḍupka and Konda ūṛs; original records retained',
     'Evidence':'DEDR 695 p.68 directly checked; explicit headings'},
    {'Form_ID':'f_g3wyicp32jhyy;f_s2dq2rcs75kce','Entry_ID':'d697','Issue':'Editorial reconstruction/derivation fragment parsed as Naikri lexical forms',
     'Disposition':'Only anḍ is the lexical Naikri root; isolated ḍ and *uṇṭu are not extra attestations',
     'Evidence':'DEDR 697 p.68 explanatory prose after Kolami/Naikri existential verbs'},
    {'Form_ID':'f_7ckhe7mh2bva6;f_4qy6lhalkznu4;f_5cyt6cflh7wcy;f_hwlk36u6at5v6','Entry_ID':'d588','Issue':'Keikadi hot word and bibliographic fragments parsed as Tamil',
     'Disposition':'Exclude from inherited Tamil evidence; udku is explicitly a Telugu loan in Keikadi, language ID unresolved',
     'Evidence':'DEDR 588 source note quotes Hislop Keikadi, Part II p.19'},
    {'Form_ID':'f_ffsdxfom7jcou','Entry_ID':'d560','Issue':'Latin Careya arborea parsed as Malayalam lexeme',
     'Disposition':'Exclude as linguistic reflex',
     'Evidence':'DEDR 560 p.55 directly checked'},
    {'Form_ID':'f_26xgxodqegvw6','Entry_ID':'d592','Issue':'Latin Varanus bengalensis parsed as Tamil lexeme',
     'Disposition':'Exclude as linguistic reflex; zoological identification preserved in source gloss',
     'Evidence':'DEDR 592 lexical and species-name formatting'},
    {'Form_ID':'d516;f_wcv5bqdv5qvyo','Entry_ID':'d516','Issue':'Elephant *yĀn-ay reconstruction linked to descend/bow',
     'Disposition':'Exclude elephant head from reconstruction and input class',
     'Evidence':'DEDR 516 reflexes and source note concern descend; K03 elephant gloss is unrelated'},
    {'Form_ID':'f_kjlaopfa4uvp6','Entry_ID':'d513','Issue':'Cardamom *ēl-V- reconstruction linked to young/tender',
     'Disposition':'Exclude cardamom reconstruction from young-root input',
     'Evidence':'DEDR 513 young/tender comparisons; different meaning and quantity'},
    {'Form_ID':'f_iubhckfx6topy','Entry_ID':'d504','Issue':'Tamil iẓu editorial comparison parsed as a Toda lexeme',
     'Disposition':'Exclude as Toda attestation; genuine Toda īṣf has an explicit alternative cognacy',
     'Evidence':'Record gloss introduces Tamil semantic comparison; Toda 2025 lexical record preserves alternative d542'},
    {'Form_ID':'f_u7ruqk5tqpl4w;f_yc2tp47frrclo','Entry_ID':'d533','Issue':'Prawn *eṯ-V-y reconstructions attached to fly entry',
     'Disposition':'Exclude from fly input; compare actual prawn d517 separately',
     'Evidence':'Original DEDR 533 p.53 directly read: fly/bee only'},
    {'Form_ID':'f_tf2s2eoodjkrc','Entry_ID':'d533','Issue':'Latin Bombinatrix glabra parsed as Telugu word',
     'Disposition':'Exclude botanical/zoological gloss from lexical evidence',
     'Evidence':'Original DEDR 533 p.53 directly read'},
    {'Form_ID':'d572;f_kp7gdn4a62ysy','Entry_ID':'d572','Issue':'Pestle *ula-kk-V reconstruction linked to ring entry',
     'Disposition':'Exclude pestle head; reconstruct regional uŋgar ring from its own reflexes',
     'Evidence':'DEDR 572 ring reflexes; unrelated reconstruction gloss'},
    {'Form_ID':'d494;f_4xfrxhjo7nlfe;f_hjypgimb7svrw;f_jas6dsum73sxq;f_moa2z4kzcizos;f_p76mfufes4dx6;f_sbm4ovmwfoplq;f_wm66slpexmrwg','Entry_ID':'d494','Issue':'Descend-root *iẓi paradigms attached to house *il',
     'Disposition':'Exclude these reconstructions from house input; review descent separately in d502',
     'Evidence':'DEDR 494 is house; K03 and DEDR 502 distinguish iẓi descend from il house'},
    {'Form_ID':'f_kxmv6dundkbmu','Entry_ID':'d477','Issue':'Cassia botanical genus parsed as Telugu lexeme',
     'Disposition':'Exclude genus gloss; rēla-ceṭṭu and historical ṛēla are the actual words',
     'Evidence':'DEDR 477 p.46 directly inspected'},
    {'Form_ID':'f_qa5sgdixq6bwk','Entry_ID':'d443','Issue':'Konda heading prefixed to ṛey and whole string assigned Kolami',
     'Disposition':'Use source-only Konda ṛey observation, retain malformed database record',
     'Evidence':'DEDR 443 p.43 explicitly switches from Kol. (Kin.) iṛ- to Koṇḍa ṛey, (BB also) ṛī-'},
    {'Form_ID':'d306;f_h7k225qhqedsc','Entry_ID':'d306','Issue':'Unrelated jackal reconstruction attached to fear etymon',
     'Disposition':'Exclude nari- reconstruction from input inference; retain records and choose independent fear-root comparison',
     'Evidence':'DEDR 306 p.29 has aḷukku fear; neither nari nor jackal occurs in its source entry'},
    {'Form_ID':'f_ewhqm7bgvncvc;f_d2ml5hgtgcgcg','Entry_ID':'d242','Issue':'Botanical Latin parsed as lexical forms',
     'Disposition':'Exclude as lexical evidence; the Tulu gloss additionally contains an unparsed real variant alataṇḍɛ',
     'Evidence':'Original DEDR p.23 distinguishes species names from pulse lexemes'},
    {'Form_ID':'f_qxbh5uhmxmj5u;f_usbuypsdcge2k','Entry_ID':'d256','Issue':'Botanical name and explicitly contrasted pulli parsed as root-family reflexes',
     'Disposition':'Neither is an independent reflex of alli waterlily',
     'Evidence':'Original DEDR p.24 gives Nymphaea lotus as Latin gloss and pulli in an as-opposed-to clause'},
    {'Form_ID':'f_jceeymrnocioy;f_pskgs2dzlcqic','Entry_ID':'d257','Issue':'Botanical gloss parsed as form or appended to form',
     'Disposition':'Exclude bare Memecylon; recover Tulu alimārɯ only as a source-labeled research annotation',
     'Evidence':'DEDR p.24 prints Tu. alimarů, alimārů Memecylon'},
    {'Form_ID':'f_m4xkfhgr6osde;f_dax24yy2mjr2q','Entry_ID':'d308','Issue':'Kurub. language heading parsed as Malayalam form; following aḷe mislabeled Malayalam',
     'Disposition':'aḷe is Kuruba (LSB 1.11), exact Jambu language ID to resolve; heading fragment excluded',
     'Evidence':'Original DEDR p.29 explicitly labels Kurub. (LSB 1.11) aḷe hole'},
    {'Form_ID':'f_5lyxsgnsmc5z4;f_utlcofw7ovbqu','Entry_ID':'d310','Issue':'Kolami ārankei and editorial n-not-ŋ comment split into lexical fragments',
     'Disposition':'Recover ārankei as source form; isolated ŋ is not an attestation',
     'Evidence':'DEDR p.29: Kol. (SR.) ārankei (n, not ŋ), (Hislop) árungkei'},
    {'Form_ID':'f_x7smouaxgvw5u','Entry_ID':'d236','Issue':'Editorial prose parsed as Malto lexical record',
     'Disposition':'Do not use as Malto attestation or a reconstruction witness',
     'Evidence':'Gloss explicitly discusses the convergence of two Tamil roots; DEDR 236/240'},
    {'Form_ID':'f_ycboqqa34f6pa','Entry_ID':'d88','Issue':'Botanical Latin parsed as Kannada',
     'Disposition':'Exclude from lexical evidence; retain raw record in appendix',
     'Evidence':'Areca catecʰu plus continuation of italic species gloss'},
    {'Form_ID':'f_pxzkpsn2ogcei','Entry_ID':'d244','Issue':'Botanical Latin parsed as Kannada',
     'Disposition':'Exclude from lexical evidence; retain raw record in appendix',
     'Evidence':'Alysicarpus plus continuation of italic species gloss'},
    {'Form_ID':'f_eq5bsq6jp4ujm','Entry_ID':'d83','Issue':'Light verb extracted as standalone root cognate',
     'Disposition':'Keep construction context; not a reflex of the obstruction root',
     'Evidence':'Kuvi addu ānai/kīnai light-verb expression in DEDR 83'},
]

relabel('f_osfi4ajucckey','Kolami','Konda',
        'DEDR 443 p.43; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=43; directly read 2026-09-09',
        'The ṛī form follows the Koṇḍa heading, not the preceding Kolami iṛ-.')
relabel('f_c3tujgqwn53m4','Telugu','Kolami',
        'DEDR 449 p.44; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=44; directly read 2026-09-09',
        'Hislop edamakei is explicitly labeled Kol. and borrowed from Telugu, not itself a Telugu attestation.')
relabel('f_bjfsuq3va4d5i','Kolami','Gondi',
        'DEDR 452 p.44; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=44; directly read 2026-09-09',
        'Go. (Mu.) ḍīpi follows Kol. (Kin.) iṛp. The source has different languages on the two sides of the wall comparison.')
relabel('f_5va2ta4nyxn2m|f_nqxts67yzhx3c|f_wue4o7mgxluak|f_yzkxwzeadth26','Kui','Kuwi',
        'DEDR 453 p.44; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=44; directly read 2026-09-09',
        'Four touch forms follow the explicit Kuwi heading; only ḍīga (ḍīgi-) is Kui.')
relabel('f_4apt5slmaf4ze','Telugu','Kolami',
        'DEDR 475 p.46; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=46; directly read 2026-09-09',
        'rēŋga is Kolami Kinwat; Telugu rē̃gu/rēnu are absent from the parsed group and are research-supplemented from the source.')

def research_record(r):
    result=r|{'Database_Language_ID':r['Language_ID'],'Research_Correction':''}
    correction=CORRECTIONS.get(r['ID'])
    if correction:
        assert r[correction['Field']]==correction['Original_Value'],r['ID']
        result[correction['Field']]=correction['Research_Value']
        result['Research_Correction']=correction['Reason']+' Source: '+correction['Evidence']
    return result

SOURCE_ISSUES.extend([
 {'Form_ID':'f_gnijejgj2azew;f_urisgmhctnpv4;f_pl35jhsbdizp2','Entry_ID':'d3115','Issue':'Reconstructed initials and an editorial alternative comparison parsed as Kui forms','Disposition':'Exclude these fragments from lexical outcomes; preserve raw rows','Evidence':'DEDR3115 row gloss explicitly says on the assumption of original initial; *c/*t are reconstruction fragments'},
 {'Form_ID':'f_5uyyv3lfyn4za;f_ecdu4ryu2ioss','Entry_ID':'d4716','Issue':'Badaga home compounds linked to an emetic-nut tree entry','Disposition':'Do not use as plant cognates; alternative intended DEDR root requires source review','Evidence':'Source glosses natal-home visit and funeral house; Hockings/Pilot-Raichoor1992 pp.458,204; imported Etymology cites4716'},
 {'Form_ID':'f_3vyangtlizprs;f_drdkfloiennjk;f_4vemxvy7keywc;f_r7vaevbwexzfy','Entry_ID':'d5372','Issue':'HTML arrow and source-label fragments parsed as Telugu/Gondi forms','Disposition':'Exclude from lexical evidence; atuku remains A until original display is checked','Evidence':'Original b(r)&lt and -&gt are damaged editorial notation; LSI and Maria of Bastar are source headings'},
 {'Form_ID':'f_36i43w5b54vmc','Entry_ID':'d4395','Issue':'Long louse *pēn reconstruction crosslinked to another etymon','Disposition':'Use actual louse4449 comparison; do not let wrong head define reconstructed input','Evidence':'DEDR4449 full comparative panel versus unrelated4395 head linkage'},
 {'Form_ID':'d698','Entry_ID':'d698','Issue':'Old Telugu oḷana locative may rest on a superseded inscription reading','Disposition':'Retain raw record but classify alleged early locative A until inscription identity is established','Evidence':'Sastri1969 p.285 n.1 and DHARMA00099 read ēḷan/ēḷaN instead of earlier oḷana'},
 {'Form_ID':'d513','Entry_ID':'d513','Issue':'DHARMA40 long vowel in ḷēnṟu is partly inferred from metathesis theory','Disposition':'Initial lateral is usable evidence; long quantity cannot independently validate the same theory','Evidence':'DHARMA00040 apparatus and commentary compare older ḷenṟu; photograph not newly checked'},
])
