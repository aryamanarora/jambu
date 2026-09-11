"""Individually checked historical observations; dates never become root votes."""
HISTORY=[]
def h(key,entry,form,input,date,lower,upper,kind,place,source,locator,link,evidence,inference,caution):
    HISTORY.append(dict(Observation_ID=key,Entry_ID=entry,Form=form,Reconstructed_Input=input,
        Date_Label=date,Date_Not_Before=lower,Date_Not_After=upper,Date_Status=kind,
        Place=place,Source=source,Source_Locator=locator,URL=link,
        Direct_Evidence=evidence,Historical_Inference=inference,Uncertainty=caution))
S='https://archive.org/details/in.ernet.dli.2015.169957'
D='https://dharmalekha.info/texts/'
h('S69-9-destroy','d277','ḻaccinavānṟu','*aẓ-i-ntt','first quarter of seventh century',600,625,'Sastri scholarly attribution','Potladurti; Inpuḻōli officials',
  'Sastri1969; DHARMA00099','p.285 inscription9 line3; DHARMA line3',D+'INSTelugu00099',
  'Date heading and initial underlined-l form visually checked in Sastri PDF312. DHARMA independently reads ḻaccinavānṟu.',
  'Displaced initial apical exists by this source-attributed period; this is earlier than the separately checked Nalajanampāḍu example.',
  'Approximate palaeographic/historical attribution, not an explicit calendar date or date of onset of the rule; original 1933 photograph not newly inspected.')
h('S69-16-destroy','d277','ḻaccina-/ḻacchina-','*aẓ-i-ntt','670–680 CE',670,680,'Sastri scholarly attribution','Nalajanampāḍu',
  'Sastri1969; DHARMA00026; Master EI XXVII:203–206','pp.291–292 inscription16 lines18–21; DHARMA lines18,21',D+'INSTelugu00026',
  'Date heading and text visually checked; DHARMA apparatus preserves earlier ḍ reading versus current ḻ.',
  'Promoted ḻ precedes later initial ḍ within this family under the accepted reading.',
  'Editorial ḍ/ḻ alternatives are not two attested ancient dialects. Two tokens remain one root and inscription.')
h('S69-38-destroy-D','d277','ḻassi','*aẓ-i-ntt','890 CE',890,890,'Sastri source date heading','Bezwada',
  'Sastri1969; EI XV:150–159,366–367','pp.310–311 inscription38 line14',S,
  'Date heading and line14 visually checked.',
  'Initial ḻ survives in an inflected destroy form at the same period as full forms.',
  'Not proof of identical-form free variation; morphology differs from aḻisina/aḻiputa.')
h('S69-38-destroy-R','d277','aḻisina; aḻiputa','*aẓ-i + tense/voice morphology','890 CE',890,890,'Sastri source date heading','Bezwada',
  'Sastri1969; EI XV:150–159,366–367','pp.310–311 inscription38 lines20–21,35',S,
  'Full aḻ sequence visually checked in the same inscription as ḻassi.',
  'The family has historically coexisting full and displaced formations; no simple replacement of the entire lexical family.',
  'Different morphology leaves analogy, conditioning and lexicalization as competing explanations.')
h('S69-9-locative-disputed','d698','oḷana [older edition] / ēḷan [re-edition]','*uḷ-an versus *ēḷ rule','first quarter of seventh century',600,625,'date attributed; lexical reading disputed','Potladurti/Inpuḻōli',
  'Sastri1969; DHARMA00099; Sōmaśēkhara Śarma1933','p.285 n.1; DHARMA apparatus line1 and commentary',D+'INSTelugu00099',
  'Sastri rejects oḷana in favor of ēḷan by comparison with reign formulae; DHARMA adopts ēḷaN.',
  'The alleged early locative cannot currently date a full-to-displaced oḷana>lōna sequence.',
  'DEDR does not identify the inscription in its short entry. Another genuine oḷana witness could restore the argument; that source trail remains to be established.')
h('DEDR698-lona','d698','ḷōna','*uḷ-an','ninth–tenth century',800,999,'dictionary date claim; inscription not localized','unspecified',
  'DEDR1984','entry698 p.68', 'https://dsal.uchicago.edu/dictionaries/burrow/',
  'DEDR page directly checked; date belongs to ḷōna, while plain lōna is undated.',
  'Provisional historical displacement evidence; do not assign preceding seventh-century parenthesis to modern lōna.',
  'Inscription identity and original reading remain unverified; not a primary dated attestation in this audit.')
h('DHARMA40-two','d474','rēṇḍ-agun','*ir-aṇṭ','Vijayāditya-Satyāśraya regnal year2','','','regnal date in text; calendar not independently fixed here','Niṭūru/Nitturu',
  'DHARMA00040; Ramesh and Ramachandra Murthy1969–1970','edition line3; first edition p.335 item56C',D+'INSTelugu00040',
  'Edition writes long ē in rēṇḍ; the adjacent reign formula supplies year2.',
  'Supports investigating an earlier long numeral stage before modern reṇḍu shortening.',
  'Quantity in this transcription still needs independent photograph checking; do not transfer the editor’s quantity inference for nearby ḷēnṟu onto the numeral.')
h('DHARMA40-young','d513','ḷēnṟurājula / ḷenṟurājula','*i/eḷ-a + human nṟu','Vijayāditya-Satyāśraya regnal year2','','','regnal date; disputed vowel quantity','Niṭūru/Nitturu',
  'DHARMA00040; Ramesh and Ramachandra Murthy1969–1970','edition line4; apparatus; first edition p.335 item56C',D+'INSTelugu00040',
  'Current editor proposes long ē partly from metathesis theory; older edition has short e.',
  'Initial lateral title is relevant to displacement; its long vowel cannot independently validate the contraction rule when the rule motivated the reading.',
  'New image or estampage inspection could independently resolve quantity. Do not treat the two editorial readings as chronological stages.')
h('DHARMA38-young','d513','chāḷkiḷēṁṟurājuL','*i/eḷ-a + human title','Vinayāditya-Satyāśraya regnal year10','','','regnal date in text','NiṭūraN in text; findspot to verify',
  'DHARMA00038; Ramesh and Ramachandra Murthy1969–1970','edition lines5–8; first edition p.333 item56A',D+'INSTelugu00038',
  'The edition preserves a second initial-lateral title; commentary compares Kannada eḷa-arasar prince.',
  'Supports a morphological young/prince comparison, distinct from a place-name derivation from Lendulūru.',
  'Calendar equation and exact quantity require first-edition/image audit; no new absolute date asserted.')
h('S69-20-Durga','loan-Durga','Druggādēvi / druggādēvi','Sanskrit Durgā > adapted *Durgga','c.681 CE',681,681,'Sastri approximate date attribution','Lakshmipuram, Kistna district',
  'Sastri1969; DHARMA00101; Prabhākaraśāstri1928','p.294 inscription20 line9; DHARMA line9 and commentary',D+'INSTelugu00101',
  'Sastri date heading and Druggādēvi visually checked; DHARMA gives a matching reading in a grant under Maṅgiyuvarāja.',
  'A borrowed Sanskrit name exhibits displacement/cluster restructuring during the early inscriptional period.',
  'Distinct from SII V1217 dated1290 cited elsewhere by Sastri. Geminate gg may preserve quantity or reflect prior repha-related strengthening; exact sequence not proved.')
h('S69-MT-Durga','loan-Durga','Druggādēvi','Sanskrit Durgā','1290 CE',1290,1290,'Sastri secondary inscription citation','Ganjam',
  'Sastri1969 citing SII V1217','p.72',S,
  'Printed page explicitly cites Ganj1290 and SII V1217.',
  'Later occurrence of a borrowed name does not prove productive application of the native inherited rule at that date.',
  'Original SII inscription not checked here; separate witness from the c.681 Lakshmipuram inscription.')
h('S69-say','d868','anan/nān; anābaḍu/nābaḍu; anavuḍu/nāvuḍu; anaka/nāka; anaru/naru','*an- + distinct grammatical formatives','Middle Telugu literary forms','','','period claim; individual passages not dated','literary dialect',
  'Sastri1969','p.72',S,
  'Page visually checked; source confines these displaced say forms to literary dialect.',
  'Nasal participation is morphologically restricted and cannot be absorbed uncritically into a nonnasal inherited-root rule.',
  'DEDR868 linkage verified against database anu f_id6r5fma34f6w; all these forms remain one grammatical family. Exact passages and paradigms need follow-up.')
h('S69-h-clusters','loans-h','madhyāhnamu/madhyānhamu; vahni/vanhi; Brahma/Bramha','Indo-Aryan h clusters','1290 and1313 for cited afternoon forms',1290,1313,'Sastri secondary citations; other words undated','Kurnool and unspecified',
  'Sastri1969 citing SII X464 andX503; Appakavi2.260','p.72',S,
  'Printed source distinguishes h-cluster reversals from the main inherited displacement discussion.',
  'Shows another metathesis domain; counts must not be pooled with initial vowel-apical displacement.',
  'Individual h-cluster words have different input orders and morphologies; no shared prehistoric event follows.')
h('S69-medial-play','unlinked-navvu','navvutāla / navvulāṭa','*navvu#lāṭa','Middle Telugu literary citation','','','undated cited passage','literary source',
  'Sastri1969','p.72, Bhr udyo3.116',S,
  'Image gives navvutāla < navvulāṭa, distinct from initial displacement.',
  'Medial nonadjacent consonant transposition across a compound/derived stem requires its own analysis.',
  'Cited passage not independently inspected; no extra root counted.')
