"""Manually assessed unetymologized records; suggestions, never database edits."""
CANDIDATES=[]
def u(ids,entry,decision,explanation,confidence,followup):
    for fid in ids.split('|'):
        CANDIDATES.append(dict(Form_ID=fid,Candidate_Entry_ID=entry,Assessment=decision,
            Explanation=explanation,Confidence=confidence,Follow_Up=followup,
            Counting_Policy='No additional independent root; excluded from primary language numerators pending accepted cognacy/source review.'))
u('f_2sb4plhwfmflk|f_e6xqnxx4weh7k','d4449','strong additional cognate candidate',
  'Kurux pēn louse in Bhokraha and Siddhapur closely matches already-linked Kurux pē̃n and cross-family *pēn. Nasalization variation is not metathesis. Two wordlist records corroborate one family.',
  'high lexical comparison','Check source nasalization conventions and dialect history; attach as evidence only after editorial review.')
u('f_52itbqspbtivm','d4449','plausible additional cognate candidate',
  'Kannada Kurumba henu louse is compatible with southern *pēn through initial p>h and source quantity conventions. Language/lect label and absence of macron must be preserved.',
  'medium-high','Check whether source omits quantity and confirm the Kannada Kurumba lect identity.')
u('f_gsga3uyc7tchg','d4449','uncertain candidate',
  'Belavarthy Kannada Kurumba śēnū louse agrees in vowel/nasal and meaning but initial ś is not the expected p/h reflex. Transcription, borrowing and distinct ancestry compete.',
  'low','Inspect original transcription and elicitation list; do not invent p>ś to make a cognate.')
u('f_lspz7e3hrzwgg|f_s3tkle2p6xd62','d845;d919','competing morphological analyses',
  'Brahui elode/elozde day after tomorrow could involve the independently attested ēlō other plus a day element, rather than the southern elli tomorrow root. The source pair does not uniquely choose cognacy or metathesis.',
  'medium for local comparison; low for deeper root','Compare Brahui dē/day compounds and original vowels before choosing845 versus919.')
u('f_fjreikzlk3avu|f_ipbqa6jmx4wvw','','negative control for proposed tomorrow comparison',
  'Brahui pagga tomorrow and palme day after tomorrow are distinct formations. Shared temporal meaning alone does not justify attaching them to elli/ēlō or deriving a liquid shift.',
  'high for exclusion from unsupported elli derivation','A separate inherited or contact etymology requires a broader temporal vocabulary analysis.')
u('f_dmmdwidbkiseu|f_v55bks6xvr6b4|f_lch56fryqr57y','d4411','plausible swell/grow connection',
  'Brahui pir-ing/piris/piriff-ing swell form a local derivational family compatible with per grow. Initial p-i-r retains order; causative/derived forms are not separate etyma.',
  'medium','Check Brahui source semantics and regular e/i correspondence; distinguish native derivation from Iranian borrowing.')
u('f_fy2qpmytfrgvm','d4176','candidate distinct from twist4177',
  'Brahui pirɣ-ing break must be compared semantically with break4176, not automatically with homophonous pirɣẖing twist4177. Root-final velar and aspiration conventions need source comparison.',
  'medium-low','Inspect both Brahui dictionary entries and determine whether break/twist is established polysemy or separate ancestry.')
u('f_nptqcsdiogtwk','d3195','reject automatic link from shape alone',
  'Brahui dranj-ing hang resembles dranzing sift but the meaning and consonant distinction are material. Sift’s independently full tāring does not establish the earlier order of hang.',
  'high for withholding unsupported link','Find a semantic bridge and full-form cognate of hang before proposing common origin.')
u('f_rgr7c5ipqwmgm','d4885','strong additional cognate candidate',
  'Unlinked Gondi mīna fish matches linked mīn and other long-nasal fish reflexes; final vowel adaptation may involve source or contact variation, not nasal metathesis.',
  'high lexical comparison','Check dialect/source and possible Indo-Aryan mīna contact; no extra root vote.')
u('f_3olcvsfaco7cq|f_soi7nqnjikpxo','d4876','plausible star cognate candidate',
  'Badaga/Kannada Kurumba mīnu star fits the independently long star formation of shine4876. Do not silently assign star to fish4885 merely from homophony.',
  'medium-high','Check source gloss and distinguish star/fish polysemy; possible common origin enters sensitivity only.')
u('f_npt7dammyw4cq|f_sbh7xzcyudnke','d4885','strong additional cognate candidate',
  'Kannada Kurumba mīnu fish matches the long-nasal fish family. Two list attestations are corroboration, not independent roots.',
  'high lexical comparison','Preserve local lect/source labels and verify whether forms are inherited or borrowed from neighboring Kannada.')
