from pathlib import Path
P=Path(__file__).resolve().parent
p=P/'formation_tests.py';s=p.read_text()
s=s.replace("'CVC-u-TT','full','krotta|kotta'","'CVC-u-TT','conditional','krotta|kotta'")
s=s.replace("'CVC-a-NC','full','trā̃cu'","'CVC-a-NC','conditional','trā̃cu'")
if "'say-infinitive'" not in s:
 s+='''
# Grammatical domains are explicitly covered but excluded from the lexical rule.
f('d868','say-infinitive','Telugu','*an-an','a','a','VC-AN','full','anan|nān','mixed','Literary infinitive alternation is independently paired; grammatical nasal domain is not the classical apical rule.',target='grammatical-nasal')
f('d868','say-negative','Telugu','*an-aka','a','a','VC-AKA','full','anaka|nāka','mixed','Negative suffix supplies low a; analogy/contraction may generalize an allomorph.',target='grammatical-nasal')
f('d868','say-negative-person','Telugu','*an-aru','a','a','VC-ARU','full','anaru|naru','short','Short output despite two source a vowels is an explicit paradigm challenge.',target='grammatical-nasal')
f('d1','distal-oblique','Telugu','*ad-an-i','a','a','VC-AN-I','full','adi|dāni-','mixed','Comparative oblique augment; mixed direct/oblique paradigm, not a lexical quantity test.',target='grammatical-deictic')
f('d410','proximal-oblique','Telugu','*id-an-i','i','a','VC-AN-I','conditional','idi|dīni-','mixed','Exact proximal prehistory depends on comparison with distal augment; high output may be analogical.',target='grammatical-deictic')
'''
p.write_text(s)
p=P/'other_processes.py';s=p.read_text().replace('labial causative suffix','verbal labial formative').replace('labial causative','verbal labial formative')
if "event('d931','Kui'" not in s:
 s+='''
event('d931','Kui','stop-cluster-transposition','*ok-p-',{'D':'opka (&lt; ok-p-; okt-)'},
      'Source explicitly supplies ok-p- and past okt-, independently placing velar before labial formative.',
      'Morphological combination precedes k-p reversal; no target apical displacement is implicated.',
      'high for local source analysis','DEDR931')
'''
p.write_text(s)
p=P/'cases_pronouns.py';s=p.read_text().replace('not demonstrated by a directly attested earlier *deni stage.','not demonstrated by a directly attested earlier *deni stage. Sastri1969 pp.178,184 explicitly treats historical dēni as interrogative; an inscriptional English translation this grant is not sufficient to identify a proximal ancestral stage.')
p.write_text(s)
p=P/'source_corrections.py';s=p.read_text()
if 'f_36i43w5b54vmc' not in s:
 s+='''
SOURCE_ISSUES.extend([
 {'Form_ID':'f_36i43w5b54vmc','Entry_ID':'d4395','Issue':'Long louse *pēn reconstruction crosslinked to another etymon','Disposition':'Use actual louse4449 comparison; do not let wrong head define reconstructed input','Evidence':'DEDR4449 full comparative panel versus unrelated4395 head linkage'},
 {'Form_ID':'d698','Entry_ID':'d698','Issue':'Old Telugu oḷana locative may rest on a superseded inscription reading','Disposition':'Retain raw record but classify alleged early locative A until inscription identity is established','Evidence':'Sastri1969 p.285 n.1 and DHARMA00099 read ēḷan/ēḷaN instead of earlier oḷana'},
 {'Form_ID':'d513','Entry_ID':'d513','Issue':'DHARMA40 long vowel in ḷēnṟu is partly inferred from metathesis theory','Disposition':'Initial lateral is usable evidence; long quantity cannot independently validate the same theory','Evidence':'DHARMA00040 apparatus and commentary compare older ḷenṟu; photograph not newly checked'},
])
'''
p.write_text(s)
