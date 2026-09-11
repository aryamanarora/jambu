"""Source paradigms and controls, separate from the database lexical screen.

Hume2001 p.9 (3), Hume2002 p.38 (38–39), and Garrett & Blevins2009
pp.538–542 supply actual morphological contrasts. The 2002 manuscript is cited
as such, not confused with the shorter final2004 article. Ancillary forms are
not ingested into Jambu and do not create independent etyma.
"""
PARADIGMS=[]
def p(key,lang,stem,affix,output,control,gloss,source,loc,entry='',ids='',note=''):
    PARADIGMS.append(dict(Observation_ID=key,Language_ID=lang,Stem=stem,Suffix=affix,
        Surface_Form=output,Independent_Stem_Evidence=control,Gloss=gloss,Source=source,Locator=loc,
        Candidate_Entry_ID=entry,Linked_Database_IDs=ids,Notes=note,
        Input_Class=('velar+labial' if stem.rstrip('-').endswith(('k','g')) and affix.startswith(('p','b')) else 'nonvelar+labial' if affix.startswith(('p','b')) else 'other-suffix'),
        Historical_Caution='Synchronic morphological input is not automatically a phonetic ancestral string; analogical creation of the alternation competes with sound change.'))
H='Hume2002 September manuscript, https://roa.rutgers.edu/files/546-0902/546-0902-HUME-0-0.PDF'
for key,stem,form,ctl,gloss,entry,ids in [
 ('ah','ah','ahpi; ahpa','ahi; ahte','hold','d51','f_xf5mwkbqpvjxe'),
 ('gas','gas','gaspi; gaspa','gasi; gaste','hang oneself','d1099','f_wkb7hjfto3jeo'),
 ('mil','mil','milpi; milpa','mili; milte','turn over','d4870','f_g4iyzmyw7b3y6'),
 ('sap','sap','sappi; sappa','sapi; sapte','source gives no gloss','',''),
 ('ut','uṭ','uṭpi; uṭpa','uṭi; uṭte','give to drink','',''),
 ('bluk','bluk','blupki; blupka','bluki; blukte','break down','',''),
 ('kok','kok','kopki; kopka','koki; kokte','sit down','d1628','f_yb2hf7hg3kv2y'),
 ('mlik','mlik','mlipki; mlipka','mliki; mlikte','turn over','d4870','f_uiwvufb4jbbli'),
 ('pok','pōk','pōpki; pōpka','pōki; pōkte','announce','d4235','f_i4oxp3x7orv7k'),
 ('lek','lek','lepki; lepka','leki; lekte','break','d5200','f_3o5nmdtypifz2'),
 ('dik','ḍik','ḍipki; ḍiksa','ḍiki; ḍikte','light fire','',''),
 ('kak','kak','kapki; kaksa','kakki; kakte','laugh','d1080','f_ds72snylx7xny')]:
    p('H02-Kui-'+key,'Kui',stem,'pi / pa',form,ctl,gloss,H,'p.38 ex.38 second conjugation',entry,ids,
      'Hume2002 table labels ḍiksa/kaksa as infinitives, but Winfield1928 p.72 places -sa in the PERFECT verbal participle and -pa in the infinitive. The lexical source has kapka. Preserve the discrepancy; do not count the apparent -sa infinitives as independently confirmed grammatical cells.' if key in {'dik','kak'} else 'Future and past independently preserve the base-final consonant; present participle/infinitive contrasts are one paradigm.')
for key,stem,form,ctl,gloss,entry,ids in [
 ('sol','sol','solbi; solba','soli; soṭe','enter','',''),
 ('pan','paṇ','paṇbi; paṇba','pai; paṭe','obtain','',''),
 ('nog','nog','nobgi; nobga','nogi; nogde','wash','d3783','f_mkjsnqeyhyxs6'),
 ('geg','geg','gebgi; gebga','gegi; gegde','associate','d1980','f_zec6tdhg4tmzu'),
 ('ag','ag','abgi; abga','agi; agde','be fitting','d325','f_2shiah6khbeyq')]:
    p('H02-Kui-'+key,'Kui',stem,'bi / ba',form,ctl,gloss,H,'p.38 ex.38 fourth conjugation',entry,ids)
for key,stem,affix,form,gloss,entry in [
 ('gok','gok','pi-n-esi','gop-ki-n-esis','caught continuously, he',''),
 ('mek','mek','pi-t-u','mep-ki-t-u','plucked, they',''),
 ('kak','kak','pi a-','kap-ki a-','laugh at each other','d1080'),
 ('nik','nik','pi ki','nip-ki ki-','cause to stand','d3665'),
 ('ok','ok','pi ki','op ki ki-','cause to carry','d931'),
 ('tuk','tuk','p-esi','tup-k-esi','let him weigh',''),
 ('huk','huk','p-esi','hup-k-esi','let him remove it','')]:
    p('H02-Kuvi-'+key,'Kuwi',stem,affix,form,'Underlying form explicitly segmented in source',gloss,H,'p.38 ex.39, citing Israel1979',entry,
      note='Israel1979 original pages not directly inspected; source-only comparison. For laugh, compare separate DEDR Schulze kakpinai retaining k-p.')
G='Garrett and Blevins2009, https://julietteblevins.ws.gc.cuny.edu/files/2013/04/GarrettBlevins2009d-AnalogicalMorphophonology.pdf'
for key,stem,affix,form,gloss,entry in [
 ('kat','kat','ka','kat-ka','cut',''),('ker','kēr','ka','kēr-ka','sing',''),('hip','hīp','ka','hīp-ka','sweep',''),('raz','raz','ka','ras-ka','cut',''),
 ('kap','kap','pa','kap-pa','bite',''),('grut','grūt','pa','grūt-pa','fell',''),('pat','paṭ','pa','paṭ-pa','break',''),('hon','hon','pa','hon-pa','run',''),
 ('tub','tūb','ba','tūb-ba','blow',''),('kaz','kāḍ','ba','kāḍ-ba','burn',''),('ven','ven','ba','ven-ba','hear',''),('hi','hī','ba','hī-ba','give',''),
 ('rik','ḍrik','pa','ḍripka','break',''),('kuk','kūk','pa','kūpka','call',''),('rek','ḍēk','pa','ḍēpka','seek',''),
 ('kak','kak','ba','kabga','vomit','d1079'),('rak','ṛāk','ba','ṛābga','sacrifice','d297'),('hok','hōk','ba','hōbga','wash clothes','d2872'),
 ('paglong','pāg','ba','pābga','kill',''),('pag','pag','ba','pabga','be split',''),('tog','tog','ba','tobga','trample','')]:
    p('GB09-Pengo-'+key,'Pengo',stem,affix,form,'Free root listed in source table',gloss,G,'p.538 ex.19–20',entry,
      note='Source p.538 image checked; IPA retroflex symbols rendered as corresponding dotted consonants and length as macrons. Source affix and velar/labial ordering are explicit. Published example set, not random lexical denominator.')

W='Winfield1928, https://ignca.gov.in/Asi_data/37202.pdf'
p('W28-lek','Kui','lek','p-a / p-i','lepka; lepki','lek base; leksa perfect participle; lekte past','break',W,'p.72, PDF89 image checked','d5200','f_3o5nmdtypifz2','Velar-before-s in perfect participle is distinct from velar+labial class; suffix identity independently predicts the alternation.')
p('W28-sug','Kui','sug','b-a / b-i','subga; subgi','sug base; sugde past; sugdi past relative','roast',W,'p.74, PDF91 image checked','d2654','f_ejxzdnny5tjf6','Voiced g before b reverses; g before the past dental instead induces voicing, retaining g-d order.')
p('W28-grap','Kui','grāp','p-a','grāppa / grāpa','grāp base; grāpai present; grāpsa perfect; grāpte past','teach',W,'p.73, PDF90 image checked',note='p-final base retains p; double-p infinitive is sometimes spelled with one p. Present allomorph is -ai, not an automatically added -pi.')
p('W28-meh','Kui','meh','p-a / p-i','mehpa; mehpi','meh base; meha perfect; mehte past','see',W,'p.73, PDF90 image checked',note='h+p is retained; h affects the perfect participle differently.')
p('W28-nol','Kui','nol','p-a','nolpa','nol base; noṭe past; noṭi past relative','ladle out',W,'p.73, PDF90 image checked',note='l+p remains; l disappears before t with retroflexion, a separate conditioned change.')
for base,out,gloss,entry in [('dī','dīpki','fall',''),('gī','gīpki','do','d1957'),('kī','kīpki','pour',''),('sī','sīpki','give',''),('vī','vīpki','shoot','')]:
 p('W28-p-strengthening-'+base,'Kui',base,'p + ki',out,base+'va third-conjugation citation form',gloss,W,'p.73, PDF90 image checked',entry,
   note='Winfield explicitly adds p to strengthen a vowel-final base before -ki. The output pk therefore does not prove a velar-before-labial input. Relevant to Garrett and Blevins2009 double-marking hypothesis, without proving every proposed historical stage.')

# Explicit observed-order annotation of the read tables, not inferred from input.
DISPLACED={
 'H02-Kui-'+k for k in ['bluk','kok','mlik','pok','lek','dik','kak','nog','geg','ag']
}|{'H02-Kuvi-'+k for k in ['gok','mek','kak','nik','ok','tuk','huk']}|{
 'GB09-Pengo-'+k for k in ['rik','kuk','rek','kak','rak','hok','paglong','pag','tog']
}|{'W28-lek','W28-sug'}
for r in PARADIGMS:
 if r['Observation_ID'].startswith('W28-p-strengthening-'):
  r['Input_Class']='vowel+complex-pk-formative';r['Observed_Order']='O-original-p-before-k'
 else:r['Observed_Order']='D-labial-before-velar' if r['Observation_ID'] in DISPLACED else 'R-input-order'
