"""Orthogonal process observations: do not pool unlike metatheses into one rate.

Main R denotes retention of target initial vowel/apical order, not absence of every
kind of metathesis. Each event below has its own input domain and control outcomes.
"""
PROCESSES=[]
def event(entry, language, process, input, outcomes, direction, chronology, confidence, reference):
    for outcome, words in outcomes.items():
        for word in words.split('|'):
            PROCESSES.append(dict(Entry_ID=entry,Language_ID=language,Process=process,
                Reconstructed_Input=input,Observed_Form=word,Process_Outcome=outcome,
                Direction_Evidence=direction,Relative_Chronology=chronology,
                Confidence=confidence,References=reference))

event('d3986','Gondi','compound-liquid-transposition','*pal#kar tooth-stick',
      {'R':'palkār|pelkiaṛ','D':'parkal'},
      'Free pal tooth and DEDR1389 kar/kaṟ wood independently segment the compound; Mandla palkār supports l before r, reversed in Koya/Muria parkal.',
      'Compounding precedes exchange of the two liquids. Dialect forms are not a dated sequence; relation to Parji perkal could involve shared development or diffusion.',
      'medium-high for internal order; medium for history','DEDR3986 and1389')

event('d809','Pengo','stop-cluster-transposition','*ik-pa intensive',
      {'R':'ika|ika vā','D':'ipka|ipka vā'},
      'DEDR explicitly derives ipka from ik-pa; simplex ika independently supplies the stem velar and the source identifies the intensive function.',
      'Intensive suffixation precedes k-p > p-k. This establishes a comparable local process outside Kui, but shared origin versus parallel development requires a larger morphological sample.',
      'high for local exchange','DEDR809 p.79 directly read')
event('d859','Kui','stop-cluster-transposition','*ig-b-',
      {'D':'ibga'},
      'DEDR explicitly supplies ig-b- and igd-, independently establishing the velar before the labial suffix.',
      'Suffixation creates g-b before b-g. Uncertain deeper relation between ig and an apical throwing root does not weaken this local morphological ordering.',
      'high for local exchange; deeper cognacy separate','DEDR859')
event('d3986','Parji','compound-liquid-transposition','*pel#kar tooth-stick',
      {'D':'perkal|perkela'},
      'Parji pel tooth and the independent wood member support l before r; neighboring Gondi palkār gives an unreversed compound.',
      'Compound formation precedes liquid exchange if inherited; borrowing a reversed Gondi compound remains a competing account.',
      'medium','DEDR3986 and1389')
event('d810','Kannada','nonadjacent-liquid-transposition','*er-al / *el-ar',
      {'R':'eral|eraḷ','D':'elar','O':'elal'},
      'Telugu temm-eral and the cited Tamil nir̤ali wind comparison weakly favor r-l; Kannada itself has both orders and assimilation.',
      'Exact direction remains less certain than the existence of the order alternation; this is not initial V/l metathesis.',
      'medium-low for direction','DEDR810; DEN1 p.416 S96')
event('d2674','Gondi','vowel-order-alternation','*sov-ar',
      {'R':'hovar|ovar','A':'savvor|savvar'},
      'K03 p.97 explicitly calls sawwor beside sovar vowel metathesis. DEDR savvor is compatible with o-a > a-o, but savvar also permits progressive/regressive vowel assimilation; gemination is independent.',
      'This vowel-vowel process precedes no uniquely established apical displacement and must not enter the initial-metathesis count.',
      'medium for savvor exchange; low for savvar mechanism','K03 p.97 example10; DEDR2674')

event('d4760','Kui','stop-cluster-transposition','*mrāk-p-',{'D':'mrāpka (&lt; mrāk-p-; mrākt-)'},
      'DEDR explicitly supplies mrāk-p- and past mrākt-, independently placing root-final k before the verbal labial formative.',
      'Suffixation precedes k-p > p-k. Initial m-a-r displacement is a separate change; its ordering with the local stop exchange is not uniquely established by the output.',
      'high for local exchange','DEDR 4760')
event('d4194','Kui','stop-cluster-transposition','*plik-p-',{'D':'plipka'},
      'DEDR explicitly gives plik-p- with past plikt-, establishing root-final k before the verbal labial formative.',
      'Causative combination precedes k-p > p-k. This is distinct from root-initial p-l displacement.',
      'high for local exchange','DEDR 4194')
event('d4761','Kui','stop-cluster-transposition','*mag-b-',{'D':'mabga (&lt; mag-b-; magd-)'},
      'DEDR explicitly gives mag-b- and past magd-, establishing g before the labial formative.',
      'Suffix formation precedes local g-b > b-g, independent of any root-apical loss.',
      'high for local exchange','DEDR 4761')
event('d5411','Kui','stop-cluster-transposition','*vrik-p-',{'D':'vripka (&lt; vrik-p-; vrikt-)'},
      'Source gives vrik-p- and past vrikt-, establishing k before a labial formative.',
      'Suffixation precedes k-p > p-k; no unique ordering relative to root-initial displacement follows.',
      'high for local exchange','DEDR 5411')
event('d715','Kui','stop-cluster-transposition','*jūk-p-',{'D':'jūpka'},
      'DEDR gives jūk-p- and jūkt-, independently establishing the velar before the verbal labial formative.',
      'Suffixation precedes k-p > p-k; the root’s earlier initial metathesis is a separate analysis.',
      'high for local exchange','DEDR 715 p.70')
event('d4761','Kannada','nonadjacent-liquid-transposition','*mar-al',{'R':'maral|maraḷ','D':'malar'},
      'Telugu maralu and Kannada maral/maraḷ support r before a second lateral. Kannada malar reverses the two liquids.',
      'The second-lateral formation must exist before reversal. Earlier root apical ṟ>r and later lateral retroflexion have independent chronologies not fixed by this pair.',
      'high for local order alternation; medium for relative chronology','DEDR 4761')

for lang,outputs in {
    'Tamil':{'R':'alar|alari'},
    'Malayalam':{'R':'alar|alaruka'},
    'Telugu':{'R':'alaru|alarcu'},
    'Kannada':{'R':'alar','D':'aral|araḷ|arlu','O':'alal'},
    'Tulu':{'R':'alaruni','D':'araluni|araḷuni'},
    'Badaga':{'A':'araḷu'},
}.items():
    event('d247',lang,'nonadjacent-liquid-transposition','*al-ar-',outputs,
          'Tamil, Malayalam, Telugu and retained Kannada/Tulu alar favor earlier l...r; Kannada/Tulu aral reverses the two liquids. Badaga may share the change or the word through contact.',
          'A route alar > aral > arlu places Kannada medial syncope after exchange, but an alternative alar > alr > arl plus final-vowel development is not excluded. Retroflexion of final l is a separate local change. No link to Telugu initial metathesis chronology follows.',
          'high for liquid-order alternation; medium for full trajectory','DEDR 247')

event('d228','Kui','stop-cluster-transposition','*rāk-p-',{'D':'rāpka'},
      'K61 p.55 explicitly gives rāpka < rākpa; root-final velar is supported by rāga and p is causative material. This moves the velar after the labial.',
      'Suffix combination must create k-p before reversal. Initial a/r displacement can be ordered before or after this local k/p exchange; the two operations commute in the relevant representation, so the final form does not decide their relative chronology.',
      'high for published local derivation; medium for prehistory','K61 p.55 §1.131; DEDR 228')
event('d240','Kui','stop-cluster-transposition','*lāk-p-',{'D':'lāpka (&lt; lākp-; lākt-)'},
      'DEDR explicitly provides lākp- and a velar-bearing past lākt-. The labial is causative material, making k-p > p-k direction morphologically motivated.',
      'Consonantal suffixation precedes the cluster exchange. Ordering relative to the separate initial a/l contraction is not uniquely decided by the output.',
      'high for cluster exchange','DEDR 240')

event('d246','Kui','nonadjacent-lateral-stop-transposition','*al-akk-? or different root',{'A':'akali'},
      'Tamil/Malayalam/Kannada washing stems have l before a velar in relevant derivatives, but no independently identical full *alakali input is available. Kui akali is attested as a rinsing noun with light-verb/echo constructions.',
      'No secure order of transposition, suffix change and possible borrowing can yet be given.',
      'low','DEDR 246; Winfield 1929 A Vocabulary of the Kui Language p.3, title and page visually verified')

event('d474','Malto','rhotic-labial-cluster-transposition','*ir-w- (two persons)',{'D':'ivr|ivresti'},
      'Tamil iruvar, Kannada irvar/irbar, Telugu iruvuru and Kurux irb independently support r before the human suffix labial. DEDR source spells Malto iwr/iwresti; corpus uses v in these forms.',
      'Medial vowel loss/formation of an r-w cluster precedes local rw > wr under this derivation. This does not move r ahead of the initial i and must not be counted as initial apical displacement.',
      'high for relative order, medium for exact prehistoric suffix stages','DEDR 474 p.46; K03 p.159 explicitly iwr < irw')

event('d520','Kui','stop-cluster-transposition','*rek-p-',{'D':'repka'},
      'DEDR explicitly gives <rek-p-, with velar-bearing past rekt-. The morphological input independently establishes k before p.',
      'Suffixation creates k-p before exchange. Its relative order to initial vowel/apical displacement is not uniquely determined by repka.',
      'high for local cluster exchange','DEDR 520')

event('d695','Kui','stop-cluster-transposition','*ḍuk-p-',{'D':'ḍupka'},
      'Original DEDR gives ḍuk-p- and past ḍukt-; source-only corrected Kui record restores the language heading lost in the database.',
      'Suffixation precedes k-p > p-k. The initial vowel/apical prehistory is independently uncertain because short and long sweep formations coexist.',
      'high for local cluster exchange','DEDR 695 p.68 directly checked')
event('d710','Kui','stop-cluster-transposition','*ug-b-',{'D':'ubga (&lt; ug-b-; ugd-)'},
      'The source gives ug-b- and past ugd-, independently identifying g before labial b. Homophonous butt ubga occurs in d706 and should not create a second automatic counting unit.',
      'Stem plus labial formation precedes g-b > b-g. This is independent of any initial vowel/apical displacement; the latter does not occur in the attested form.',
      'high for local morphological exchange; root cognacy with uṟu less secure','DEDR 710 p.70 and 706 p.69 directly checked')
event('d707','Gondi','rhotic-fricative-cluster-transposition','urh- / uhr-',
      {'R':'urh- (<i>Voc.</i> 267a)','D':'uhr- (<i>Voc.</i> 267a)'},
      'The two transitive stems are given as alternatives in Gondi Koya. Related urŋg bent and southern uṟ-aŋk establish root-r before suffix material, favoring urh as earlier order.',
      'The cluster must first arise through stem formation/syncope. Exact development of h from earlier suffix material and whether the variants are dialectal need the Gondi Vocabulary 267a original.',
      'medium; lexical variant reversal clear, full suffix history pending','DEDR 707 p.69 directly checked')
event('d664','Telugu','medial-rhotic-cluster-transposition','*ur-ṇḍ / uṇḍ + r formation',
      {'A':'uṇḍramu|uṇḍrālu'},
      'Vowel-first urul/uruṇṭ roll/round comparanda support an earlier r before the nasal-stop, but an independent r-suffix or analogical formation after uṇḍa is not excluded.',
      'If metathesis, medial syncope creates the r-nasal-stop cluster before r shifts right. If suffixal/analogical, no consonant reversal need have occurred.',
      'low; competing morphology remains viable','DEDR 664 p.64 directly checked')

event('d931','Kui','stop-cluster-transposition','*ok-p-',{'D':'opka (&lt; ok-p-; okt-)'},
      'Source explicitly supplies ok-p- and past okt-, independently placing velar before labial formative.',
      'Morphological combination precedes k-p reversal; no target apical displacement is implicated.',
      'high for local source analysis','DEDR931')
