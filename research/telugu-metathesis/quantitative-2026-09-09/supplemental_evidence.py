"""Source-verified forms omitted or truncated by the database parser.

These are research observations with explicit links to existing database entries,
not new Jambu IDs and not database edits. They cannot add independent etyma.
"""
EXTRA=[]
def source_form(key,entry,lang,form,gloss,source,linked,reason):
    EXTRA.append(dict(ID='research:'+key,Research_Group=entry,DEDR_ID=entry,
        Language_ID=lang,Database_Language_ID='',Form=form,Original='',Gloss=gloss,
        Source=source,Tags='research-only source-verified observation',Description=reason,
        Borrowed_In_Path='0',Is_Dravidian='1',Status='research-only',
        Research_Correction=reason,Record_Origin='source-supplement',Linked_Database_IDs=linked))

for form in ['pēnu','pṇēka']:
    source_form('d4449-Sunkarametta-'+form,'d4449','Kuwi',form,'louse; Sunkarametta singular/plural component',
        'DEDR4449; Su. Isr.; full source paradigm preserved in linked database record',
        'd4449;f_55zkf7il6a7rs','Split singular and plural of one explicitly attested paradigm; source dialect Sunkarametta preserved.')
source_form('d4449-Bisamkatak-penka','d4449','Kuwi','pēnka','lice; Bisamkatak retained plural',
    'DEDR4449; P.; full source paradigm preserved in linked database record',
    'd4449;f_p2afavq75txyu','Split retained plural; source dialect Bisamkatak preserved. Not free variation asserted within Sunkarametta.')

for form in ['anan','nān','anābaḍu','nābaḍu','anavuḍu','nāvuḍu','anaka','nāka','anaru','naru']:
    source_form('d868-literary-'+form,'d868','Telugu',form,'literary grammatical derivative of anu say',
        'Sastri1969 p.72, image PDF97 directly checked; literary Middle Telugu, individual passage dates not supplied',
        'd868;f_id6r5fma34f6w','Source pairs full/reduced infinitive, passive, post-action and negative formations. Research observation only; no independent root added.')

for entry,lang,fid,forms in [
    ('d1','Telugu','f_xyg34hnf324gu',['adi','dāni-']),
    ('d1','Telugu','f_nxyysjn4efeuo',['avi','vāṭi-']),
    ('d410','Telugu','f_papzle6h7zsbw',['idi','dīni-']),
    ('d410','Telugu','f_yy5ihgoamqbww',['ivi','vīṭi-']),
    ('d1','Konda','f_y543pnnelt56m',['adi','dani-']),
    ('d1','Konda','f_lbx6olf6zwfj4',['avi','vanka-']),
    ('d410','Konda','f_xxmnduuboq7nm',['idi','deni-']),
    ('d410','Konda','f_s46cyeeg4a5ru',['ivi','venka-'])]:
    for form in forms:
        source_form(entry+'-'+lang+'-paradigm-'+form,entry,lang,form,'demonstrative: direct form or oblique stem',
            'DEDR'+entry[1:]+'; source paradigm already preserved in linked database record; compare Krishnamurti2003 pp.222–223',
            entry+';'+fid,'Split one attested paradigm to annotate its direct and oblique outcomes separately; no new lexical attestation or independent root.')

for entry,linked,forms in [
    ('d4438','f_fm36hjmxgpg22;f_rfvppue7sk6vu;f_zt6ushuz6ei2c',['pēnu','pēṇka','pṇēka','pēnka']),
    ('d4885','f_2m2d5367gggug;f_623ooaklmcdzw;f_fzpvjwsuj3r2m;f_zfbwv4ozp5voy',['mīnu','mīnka','mrīka','mnīka','mṇīka','mṇīnu'])]:
    for form in forms:
        source_form(entry+'-Kuwi-paradigm-'+form,entry,'Kuwi',form,'god/devil or fish; singular/plural paradigm component',
            ('DEDR4885 p.436 directly read; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=436' if entry=='d4885' else 'DEDR4438 source paradigms preserved in database; compare Hume2004 p.225'),
            entry+';'+linked,'Split printed paradigm for per-form outcomes; Isr. fish forms were stranded in the shared gloss. No additional independent root.')
for lang,form,tag in [('Gadaba','mīn (mīnil)','Oll.'),('Gondi','mīn','Tr. A. W. Ph. Mu. etc.; Voc.2852'),('Konda','mīn (mīnga)','BB')]:
    source_form('d4885-'+lang+'-source','d4885',lang,form,'fish; plural in parentheses',
        'DEDR4885 p.436; '+tag+'; directly read; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=436',
        'd4885','Actual printed language evidence omitted by corpus parser; one root per language regardless of dialect listing.')

for form in ['le','leˀ e','ledu']:
    source_form('d916-konda-'+form,'d916','Konda',form,'get up, rise; defective imperative paradigm',
        'DEDR916 p.88; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=88; directly read 2026-09-09',
        'd916;f_3o3sco6gvxt5o','Defective rise verb and singular/plural imperatives are stranded in the gloss of ēṟasi steep; one paradigm, not three independent roots.')

for form in ['ḍolucu','ḍolcu']:
    source_form('d2698-'+form,'d2698','Telugu',form,'cause to roll',
        'DEDR original local SQL row 63997, form field ḍol(u)cu; DEDR 2698',
        'd2698;f_huorhdtptiy7a;f_siomky4eyhipi;f_dgxfshhu7n7ws',
        'Expand source optional u in a form damaged by HTML parsing; two variants of one formation, not two roots.')
source_form('d5153-konda-nrund','d5153','Konda','nṛund','last year',
    'Krishnamurti 1980 p.498 item18, image directly checked',
    'd5153','Source-only compound form; corpus Konda last-year search has no result. Exact compound input remains uncertain.')

source_form('d698-telugu-lona','d698','Telugu','lōna','within, inside',
    'DEDR 698 p.68; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=68',
    'd698;f_bizfzqn6oj7je','Remove date transferred from preceding Old Telugu oḷana; this lōna is undated in the source.')
source_form('d2149-telugu-kotta','d2149','Telugu','kotta','new',
    'Krishnamurti 2003 p.159 example 90, explicitly Mdn Te.',
    'd2149;f_ti4dmnqgr73ha','Modern r-loss reflex explicitly attested in comparative source but absent from this corpus group.')
source_form('d4711-konda-mranu','d4711','Konda','mrānu','tree',
    'Krishnamurti 2003 pp.160–161 n.16; Sova village dialect',
    'd4711;f_hjm3qovym4kum','Directly reported dialect counterpart to Araku marán; not an attested ancestral intermediate.')
source_form('d4711-konda-maran-stress','d4711','Konda','marán','tree',
    'Krishnamurti 2003 p.161 n.16; Araku valley informant',
    'd4711;f_hjm3qovym4kum','Preserve reported second-syllable stress as source evidence; same lexeme as database maran, no extra root.')

for lang,form,tag in [('Gondi','gōr','S.; Voc.1233'),('Gadaba','gēre','S.'),('Kui','unjuli','K.')]:
    source_form('d561-'+lang+'-'+form,'d561',lang,form,'nail; finger',
        'DEDR 561 p.55; '+tag+'; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=55',
        'd561','Original source directly checked; omitted lexical observation, not an extra root.')

source_form('d695-kui-dupka','d695','Kui','ḍupka','scrape together, sweep up',
    'DEDR 695 p.68; <ḍuk-p-, past ḍukt-; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=68',
    'd695;f_d6ykhtysg47w6','Restore Kui language and remove embedded source heading.')
source_form('d695-konda-urs','d695','Konda','ūṛs- (-t-)','sweep or clean a threshing floor',
    'DEDR 695 p.68; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=68',
    'd695;f_emynt4gsbupp6','Restore Konda language and remove embedded source heading.')

for lang,forms in {'Kui':['deba','debe','debo'],'Kuwi':['tebri','tēbri','ṭebri'],
                   'Gondi':['ḍema','demar','ḍāvā'],'Naikri':['ḍāva'],
                   'Parji':['ḍebri'],'Gadaba':['ḍebri']}.items():
    for form in forms:
        source_form('d449-IA-loan-'+lang+'-'+form,'d449',lang,form,'left',
            'DEDR 449 p.44; Indo-Aryan *ḍavva/*ḍevva loan comparison, CDIAL 5539; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=44',
            'd449','Source-only separate Indo-Aryan loan comparison; not an inherited reflex of *iṭam and not a metathesis denominator token.')

source_form('d443-konda-rey','d443','Konda','ṛey','to beat, strike',
    'DEDR 443 p.43; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=43',
    'd443;f_qa5sgdixq6bwk',
    'Remove Koṇḍa heading from the parsed form and restore source language; nearby ṛī is the same Konda root.')

for lang,form,tag in [('Telugu','rē̃gu',''),('Telugu','rēnu',''),('Kannada','rēgu','explicitly < Telugu'),
                      ('Kolami','reŋā','SR.'),('Gondi','rēŋgā','all dialects; Voc.3057'),('Gadaba','rēŋ','S.3')]:
    source_form('d475-'+lang+'-'+form,'d475',lang,form,'jujube',
        'DEDR 475 p.46; '+tag+'; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=46',
        'd475;f_4apt5slmaf4ze',
        'Source-verified plant-name reflex absent from the parsed corpus group; only source language/form restored, not an added independent root.')

source_form('d319-kannada-racce','d319','Kannada','racce','crying aloud, noisy and abusive clamour',
    'DEDR 319 p.30; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=30',
    'd319;f_5zw53zcyri4t2',
    'Real lexeme printed after a semicolon in DEDR and stranded in four Kannada glosses. One source observation, not four independent records.')
source_form('d307-telugu-lampu','d307','Telugu','lā̃pu','spreading (verbal noun)',
    'DEDR 307 p.29; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=29',
    'd307;f_leszidqrkkwly',
    'Original source prints Telugu lā̃ncu spread (intr.); noun lā̃pu. The noun is missing from the corpus group.')
source_form('d310-kolami-arankei','d310','Kolami','ārankei','palm of the hand',
    'DEDR 310 p.29; SR, Kamaleswaran; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=29',
    'd310;f_5lyxsgnsmc5z4',
    'Source explicitly corrects n, not ŋ. Remove the editorial parenthesis from the research citation while retaining raw database form.')
source_form('d257-tulu-alimaru','d257','Tulu','alimārɯ','iron-wood tree, Memecylon',
    'DEDR 257 p.24; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=24',
    'd257;f_pskgs2dzlcqic',
    'Remove appended Latin botanical gloss from the research form; ɯ retains the database conversion of source ů.')
source_form('d242-tulu-alatande','d242','Tulu','alataṇḍɛ','a kind of pulse',
    'DEDR 242 p.23; B-K; https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=23',
    'd242;f_d2ml5hgtgcgcg',
    'Source B-K variant alataṇḍè = alasaṇḍè is stranded in the botanical-name record’s gloss; ɛ follows corpus transcription.')
