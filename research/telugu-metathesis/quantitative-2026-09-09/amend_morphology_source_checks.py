from pathlib import Path
P=Path(__file__).resolve().parent
p=P/'kondh_paradigms.py';s=p.read_text()
s=s.replace("'Nonlabial -sa infinitive in fire/laugh retains velar-s order; it is not a k-p counterexample.'", "'Hume2002 table labels ḍiksa/kaksa as infinitives, but Winfield1928 p.72 places -sa in the PERFECT verbal participle and -pa in the infinitive. The lexical source has kapka. Preserve the discrepancy; do not count the apparent -sa infinitives as independently confirmed grammatical cells.'")
s=s.replace("('pat','paṟ','pa','paṟ-pa'", "('pat','paṭ','pa','paṭ-pa'")
s=s.replace("('kaz','kāẓ','ba','kāẓ-ba'", "('kaz','kāḍ','ba','kāḍ-ba'")
s=s.replace("('rik','ṛik','pa','ṛipka'", "('rik','ḍrik','pa','ḍripka'")
s=s.replace("('rek','ṛēk','pa','ṛēpka'", "('rek','ḍēk','pa','ḍēpka'")
s=s.replace('Transcription from extracted text must be checked against image for unusual apicals; source affix and velar/labial ordering are clear.', 'Source p.538 image checked; IPA retroflex symbols rendered as corresponding dotted consonants and length as macrons. Source affix and velar/labial ordering are explicit.')
if "W28-lek" not in s:
 s+='''
W='Winfield1928, https://ignca.gov.in/Asi_data/37202.pdf'
p('W28-lek','Kui','lek','p-a / p-i','lepka; lepki','lek base; leksa perfect participle; lekte past','break',W,'p.72, PDF89 image checked','d5200','f_3o5nmdtypifz2','Velar-before-s in perfect participle is distinct from velar+labial class; suffix identity independently predicts the alternation.')
p('W28-sug','Kui','sug','b-a / b-i','subga; subgi','sug base; sugde past; sugdi past relative','roast',W,'p.74, PDF91 image checked','d2654','f_ejxzdnny5tjf6','Voiced g before b reverses; g before the past dental instead induces voicing, retaining g-d order.')
p('W28-grap','Kui','grāp','p-a','grāppa / grāpa','grāp base; grāpai present; grāpsa perfect; grāpte past','teach',W,'p.73, PDF90 image checked',note='p-final base retains p; double-p infinitive is sometimes spelled with one p. Present allomorph is -ai, not an automatically added -pi.')
p('W28-meh','Kui','meh','p-a / p-i','mehpa; mehpi','meh base; meha perfect; mehte past','see',W,'p.73, PDF90 image checked',note='h+p is retained; h affects the perfect participle differently.')
p('W28-nol','Kui','nol','p-a','nolpa','nol base; noṭe past; noṭi past relative','ladle out',W,'p.73, PDF90 image checked',note='l+p remains; l disappears before t with retroflexion, a separate conditioned change.')
for base,out,gloss,entry in [('dī','dīpki','fall',''),('gī','gīpki','do','d1957'),('kī','kīpki','pour',''),('sī','sīpki','give',''),('vī','vīpki','shoot','')]:
 p('W28-p-strengthening-'+base,'Kui',base,'p + ki',out,base+'va third-conjugation citation form',gloss,W,'p.73, PDF90 image checked',entry,
   note='Winfield explicitly adds p to strengthen a vowel-final base before -ki. The output pk therefore does not prove a velar-before-labial input. Relevant to Garrett and Blevins2009 double-marking hypothesis, without proving every proposed historical stage.')
'''
p.write_text(s)
p=P/'literature-claims.json'
import json
rs=json.loads(p.read_text())
for r in rs:
 if r['id']=='H04-kp':
  r['status']='Hume2004 p.203, Hume2001 p.9, Hume2002 p.38 and Winfield1928 pp.72–75 read; complete four-language literal cluster screen under adjudication'
  r['claim']='Stem-final velar plus labial verbal formative surfaces in reversed order; nonvelar controls retain their order. The suffix is not uniformly causative.'
  r['test']='152 screen records include 61 Kui source-supported verbal families, nominal and labial-stem pk controls, and Kuvi Schulze kakpinai as a possible retained counterexample. Garrett and Blevins2009 analogical-origin hypothesis remains distinct from synchronic regularity.'
 if r['id']=='S69-destroy':
  r['claim']='Source-attributed first-quarter seventh-century initial-ḻ destroy at Potladurti, independent670–680 witness, and890 coexisting full/displaced formations.'
  r['status']='Sastri285 inscription9,291–292 inscription16,310–311 inscription38 images checked; DHARMA00099 and00026 edition evidence checked'
rs.extend([r for r in [
 {'id':'GB09-analogy','source':'Garrett and Blevins2009 pp.537–543, §22.4; p.538 image checked','claim':'Kondh kp/pk and gb/bg alternations may arise from causative replacement, reinterpretation, plural-action double marking and analogical generalization rather than a phonetic KP>PK sound change.','status':'Relevant argument read in full; historical intermediates explicitly hypothetical','test':'Winfield73 vowel-final bases with strengthened -p plus -ki and database labial-base pk derivatives establish a nonmetathetic source of pk. These support possibility, not unique historical proof.'},
 {'id':'H02-table-discrepancy','source':'Hume2002 p.38 ex.38 versus Winfield1928 p.72 and DEDR1080','claim':'The manuscript table labels kaksa/ḍiksa as infinitives, whereas Winfield assigns -sa to perfect participles and -pa to infinitives.','status':'Both page images checked; DEDR kapka confirms labial infinitive in laugh','test':'Retain the source discrepancy; use verified suffix cells, not a silently repaired table.'},
 {'id':'BB63-source-quality','source':'Burrow and Bhattacharya1963 p.231, https://brill.com/previewpdf/journals/iij/6/3-4/article-p231_3.xml','claim':'Schulze/Fitzgerald transcriptions can be inaccurate; Bisamkatak consultant resident in Kui area may show contact effects.','status':'Primary introductory page retrieved/read','test':'Preserve source/dialect labels; neither source criticism nor possible contact licenses automatic deletion of kakpinai or treating every Bisamkatak feature as borrowed.'}
] if r['id'] not in {x['id'] for x in rs}])
p.write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
