"""Explicit first-pass review of every entry in the 187-entry nominal screen.

The screen selects entries, not independent etymological families. These notes
assess what an accent argument needs; they do NOT accept every source etymology,
claim every form was checked against a page image, or calculate a success rate.
Run inventory.py first. No lexical data is changed.
"""
import csv
import json
import unicodedata as ud
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Keys combine headword and Turner number where homographs require it.
# C compatible with retention/regular vowel history; A apocope/mobile-compatible;
# F formation must be controlled; K contraction/segment alignment needs work;
# P unexplained accent or paradigm; Q quantity/aspiration chronology uncertain;
# S source reading or etymological input uncertain. Codes can overlap.
ANNOTATIONS = """
áabru|F;K|Extended cloud formation; root accent is compatible with Basu's generalization. Epenthesis and aspiration position intervene between abhrá and the modern word.
áaḍu|F;C|Extended adjective; root accent plus open short-a lengthening. Final OIA accent is not copied across the extension.
áangu|F;C|Extended sickle noun has root accent, with later short-a lengthening before the internal nasal-stop cluster. The retained u makes simple final-vowel apocope an inappropriate whole-word derivation.
áašuṇ|P;K|Initial accent and vowel/consonant history are not derived from aśáni by the core rules. Extension is a possibility, not an established solution.
áaṣṭ|A;C|aṣṭā́ > short aṣṭ after loss of the final vowel, then closed-a lengthening predicts early aa. No independent numeral reset is required.
aawíiṛu|F;K|Extended adjective has root-final accent; vocalic-r development and cluster/length history need separate reconstruction.
aaghaá|A;K|Final accent is compatible with ākāśá, but medial consonant loss, contraction and aspiration need analysis; not simple final apocope alone.
aaghaabáanu|F;S|Compound with 'sky' and a colour element. First ancestral token concerns only one component and has a nonstandard transcription; not an independent várṇa accent test.
ac̣híi|F;S|Prefer testing the attested accented dual akṣī́ over singular ákṣi. Number/gender remodeling and kṣ development remain necessary; no priority claim.
akóoš|F;K|Contracted teen compound; aa-to-oo raising is visible, but accent selection within the contracted compound is not reconstructed.
angeerí|F;K|Accented feminine comparison broadly fits final prominence. ai/ee and feminine suffix history must be established before assigning mora correspondence.
angóor|P;C|Accent on the old long vowel fits proposed attraction from a preceding accented short vowel; shared Shina evidence supports this limited hypothesis.
angúṭ|A;K|Mobile short citation compatible with final-accent apocope; medial cluster and vowel history are additional questions.
aṣṭóoš|F;K|Contracted teen compound. Modern oo presupposes earlier early aa; the old compound accent does not determine that stage mechanically.
báaṣ|A;C|Mobile baṣá preserves final-accent class; short a then late closed lengthening accounts for early singular aa.
bac̣húuṛu|F|Extended calf formation with additional diminutive material; root-final/derivational accent, not a bare vatsá reflex.
bakáara|F;P|Plural/collective and consonant history differ from bárkara. Root-final accent is a formation hypothesis, not demonstrated inheritance.
basaánd|A;C|Mobile basandá and late aa fit final-accent apocope plus later lengthening after a pretonic syllable; nt > nd is separate.
batshaár|A;C|Mobile batshará; late aa fits the pretonic/aspiration environment. Retained derivational material must be included in the input.
bháaru|F;S;Q|Short bhára offers a plausible alternative to long bhārá; an appropriate short-vowel extension is not established, whereas bhāraka is attested.
bhiiroó|F;K|Masculine derivative differs from bhíiru despite the same remote root. Final oo requires formation/contraction and later accent history.
bhíiru|F;C|Extended masculine noun with root accent and retained ii. Final vīrá accent is superseded by the formation, if that analysis is established.
bhiíš|A;K;Q|Late accent compatible with loss of final prominence, but contraction of the numeral and source morphemic short i need separate chronology.
bhoóy|A;K|Mobile bhooyí supports final accent; substantial consonant/vowel contraction and kinship inflection intervene after vadhū́.
bhróo|C;S;F|Old initial accent and raising fit the current headword, but 2011 head/phonetic fields disagree and Puri bhruú differs. Exclude from precise dating.
bhruk|P;Q|Short citation alone is uninformative; fixed inflection contrasts with vr̥kká. Compare divergent Shina kidney paradigms before proposing a family-wide retraction.
bíi|C;S|Old bī́ja supports early long accent after j/final-vowel loss. The dictionary's first proto token bíja omits the old length.
bíǰi|F;P|Feminine formation and palatal cluster development differ from vidyút. Initial accent needs derivation or another independently supported history.
biṣ|A;C|Short citation plus mobile biṣá fits viṣá and opposes a universal inherited fixed-class reconstruction for this family.
bóolu|F;C|Extended hair noun; old early ā raises to oo. Stem accent is compatible with both the old accent and the formation rule, so not two independent confirmations.
bóoš|C;K|First-member accent broadly compatible with dvā́daśa; compound contraction and resulting aa > oo still need their own derivation.
bráam|C;K|Fixed early accent fits márman after r metathesis and closed-a lengthening; initial m > b and nasal history are separate.
čandíiš|F;K|Teen-series contraction and ee > ii visible; present medial/final accent not a simple copy of cáturdaśa.
čhaál|A;K|Mobile inflection and late aa fit final accent with intervening consonant loss; exact contraction versus short-a lengthening route needs control.
čhay|A;Q|Mobile short citation compatible with final accent. Old long ā and the final glide require a quantity/contraction history.
čoór|A;C|Old long o retained with second-mora accent after final-accent apocope; mobile inflection independently supports the class.
čúkru|F;C|Root-accented extended adjective; short vowel and retained cluster show why closed high vowels cannot all be assumed to lengthen.
čúur|C;K|Accent on the formerly medial accented nucleus is compatible; loss of the first syllable and diphthong history change alignment.
c̣haár|A;C|Mobile c̣harí and late closed aa fit final-accent class plus aspiration-conditioned lengthening; i-class morphology is additional.
c̣hiír|A;C|Late old long ii plus mobile inflection is compatible with kṣīrá after apocope.
c̣híiri|F|Derivative 'udder' is not the same formation as 'milk'; feminine suffix/accent assignment explains why the two cannot be scored as contradictory reflexes.
c̣híitr|C|Fixed early ee > ii fits kṣḗtra. Cluster development and aspiration position are separate from retention of the old stem accent.
c̣hiṇ|A;Q|Mobile accent compatible with kṣīṇá, but earlier long ī has shortened. This datum needs the high-vowel shortening history.
c̣huúr|A;P;Q|Rising citation is compatible with an old final accent, but fixed inflection and new long uu from short u remain unexplained.
dáand:6152|C|Fixed tooth paradigm and later early closed-a lengthening fit dánta; nt > nd does not need to create late accent.
dáand:6724|A;P;S|Hill noun is mobile dandá, unlike its homographic tooth. Proposed dhánu etymology requires semantic, consonantal and class justification.
dáaš|C|Old accented short a with later closed lengthening gives early aa; the loss of the final syllable is separate.
deec̣híṇu|F;Q|Root-final accent fits extended adjective, but initial old accented a > unaccented ee is not explained by the accent rule alone.
deés|A;C|Mobile deesá and late ee support final-accent apocope; contraction creating ee precedes that stage.
dharaáṇ|A;C|dharaṇí is mobile. Late aa follows aspiration/pretonic lengthening, while the modern feminine class and old ī need reconstruction.
dhií|A;F;K|Mobile daughter paradigm broadly fits final accent; vocalic-r, aspiration movement and kinship contraction prevent a literal vowel-to-vowel derivation.
dhráac̣|C;Q|Old initial accent is compatible; the short Biori vowel and Palula morphemic form require intervening shortening. Early aa is not predicted by unrestricted aspiration-conditioned lengthening.
dhreég|A;K|Late ee broadly compatible with final accent, but diphthong/cluster development and this predicate formation require checking.
dhrígu|F;Q|Extended adjective has root accent; old ī was shortened before the modern stage. Retention of the old OIA vowel length would give the wrong input.
dhrúuk|P;Q|Fixed early long uu is not derived from durgá by apocope alone. Metathesis and quantity history are unresolved.
díir|C;S|Attested dḗvara variant supports early ee > ii. First-listed dēvará is not the only source-accent option.
díiš|P|Fixed early accent and ee > ii require retraction before raising if dēśá is the ancestor; explicitly recognized counterexample in the grammar.
haál|A;C|Mobile halá fits final accent; late aa is also independently predicted by h-conditioned closed lengthening.
haát|C|Fixed háata fits hásta. Later closed lengthening with h gives late singular aa, while earlier open lengthening gives early plural aa.
haṇoó|F;K|Egg gender formation and final oo are not a direct reflex of āṇḍá. Aspiration, old shortening and suffix contraction require reconstruction.
héeṛi|F;S;P|Duck comparison ātí is uncertain in the larger etymological literature; feminine extension, consonant and accent history must be justified.
heewaánd|A;C|Mobile heewandá; pretonic closed-a lengthening yields late aa, consistent with old final accent. Initial ee has separate history.
híṛu|F;C|Root-accented heart formation is compatible with initial OIA accent, but hṛd versus hṛdaya and the added ending require morphological comparison.
iṇc̣|C;K|Fixed short paradigm compatible with initial accent; vocalic r and nasal/affricate history are independent of the mora question.
iṣṭú|F;P|Final accented short u differs from íṣṭakā. Gender/derivational remodeling or borrowing must be checked; do not invoke unmotivated accent advancement.
izraáṇ|F;K|Contracted compound with its own final accent and umlaut in izreeṇí. Not a single-root accent comparison.
ǰáandu|F;C|Extended adjective has root accent; earlier shortening/loss in jīvantá and subsequent closed-a lengthening before nd create the modern shape.
ǰáanu|F;C|Root-accented extended person noun with short-a lengthening; contrasts with the potential loan zaán.
ǰáar|A;C|Mobile ǰará continues final-accent behavior; later closed-a lengthening gives early aa.
ǰaṣṭáanguṛ|F;K|Compound/extended 'big toe'; only one component is cited by the proto token. Its stress is not a direct test of jyḗṣṭha alone.
ǰhanduraá|F;K|Snake derivative adds substantial material to jantú; final suffix accent and contraction require formation reconstruction.
ǰhaní|F;P|Final accent versus jáni needs a feminine/abstract formation or an analogical history; source comparison alone does not explain it.
ǰhangaár|A;K;P|Mobile liver noun and late closed aa are regular internally, but yákr̥t does not directly predict its extra syllable, nasal or accentual class.
ǰhií~|A;S;K|Mobile long rising vowel fits final accent; the louse comparison with jīvá needs etymological scrutiny and nasal/aspiration history.
ǰip|A;C|Mobile ǰipí fits jihvā́; fixed tongue in Kohistani/Gilgiti is opposing evidence to unchanged family-wide class assignment.
káac̣|C|Fixed root accent and closed-a lengthening fit kákṣa, with cluster simplification separate.
kaál|A;C|Old long ā remains late after final-accent apocope; mobile inflection fits kālá.
káand|A;C;Q|Mobile kaná fits skandhá despite early singular aa. Aspiration must have disappeared or moved before late lengthening, and d is absent in the inflected form.
káaṇ|C|Fixed accent plus later closed-a lengthening fits kárṇa; r loss/retroflexion predates the modern shape.
káaṇḍu|F;C|Extended thorn noun with root accent and closed-a lengthening before ṇḍ; cluster and suffix history are separate.
karáaṛu|F;C;Q|Root-final accent can follow formation remodeling, or attraction to an old long vowel. Those explanations are not distinguished by this form alone.
kéengi|F;K|Feminine comb formation with umlaut and cluster simplification; old initial accent compatible, exact e length/quality chronology requires reconstruction.
kháaṇ|P;Q|Early aa and fixed class remain problematic under both khaṇḍá and skandhá. Alternative etymological labels do not remove the aspiration/length problem.
khaṣíi|F;C|Final accented feminine extension broadly compatible with karṣí; final vowel length and aspiration movement require separate treatment.
kiroóṛ|A;C|Late oo with mobile inflection fits krōḍá after epenthesis and apocope; the unaccented inserted syllable does not itself require a new accent rule.
kóok|C|Old early ā > oo, fixed inflection and final-vowel loss fit kā́ka.
koomáalu|F;C|Root-final accent in the extended adjective plus open-a lengthening. Unaccented initial oo is not governed by the accented-vowel raising rule.
kóoṇ|C|Old early ā > oo and fixed inflection fit kā́ṇḍa; cluster reduction is separate.
kráam|C;K|Fixed kárman accent with metathesis and open/closed lengthening. Biori kram/kráama supplies a direct chronological test.
kriṣíṇu|F;C|Extended adjective with epenthesis and root-final accent; key test of formation-specific accent rather than literal copying of kṛṣṇá.
lhoóku|F;K|Root-accented adjective has internal contraction and aspiration movement. A formation rule fixes the syllable but does not by itself predict the late mora.
lhoóṇ|A;K|Mobile salt noun supports final accent, but lavaṇa contraction and aspiration creation/movement must be reconstructed separately.
máakaṛ|P;K|Initial accent and aa do not follow mechanically from markáṭa. Metathesis, formation or earlier accent hypotheses need independent support.
meec̣hí|F;Q|Feminine honey formation differs from adjectival mākṣiká. Initial old ā and modern ee need shortening/umlaut history, not just an accent change.
méeṭi|F;C|Feminine formation, old vocalic r and i-triggered fronting are involved; initial accent broadly compatible with mŕ̥ttikā.
mhaás|A;C;Q|Mobile late old aa fits māṃsá; secondary sonorant aspiration is not a basis for assuming Kalkoti low tone must be inherited.
mheél|A;K|Mobile buttermilk form fits final accent after internal consonant loss and contraction. Derive the long vowel before testing its mora accent.
mhoóru|F;K|Extended sweet adjective with madhura contraction/aspiration movement; root-final accent alone does not predict the contracted contour.
míi|C;K|Fixed early vowel compatible with mḗdas after intervocalic/final material loss and raising; contracted intermediate remains reconstructed.
móoṇ|C;S|Fixed early ā > oo fits the cited mā́na; nest sense and retroflex nasal need independent etymological support.
móoṇuṣ|C;F|Initial accent and raising compatible with mā́nuṣa; retained internal syllables distinguish it from a simple monosyllabic apocope example.
mring|P;S;K|Fixed class does not directly continue mr̥gá. Animal sense, nasal and consonant history require an etymological comparison before an accent law.
mulái|F;K|Radish is a feminine extended formation, not bare mū́la. Final diphthong/inflection and earlier shortening require reconstruction.
mung|P;K|Fixed short-vowel paradigm opposes a mechanical mudgá mobile-class prediction; nasal/stop sequence also changes.
múṣṭi|F;P|Feminine formation may assign root accent, but retained i does not prove extension. Initial accent differs from muṣṭí and needs morphological evidence.
múṭi|F;P|Related arm formation shares the muṣṭí issue; cluster loss and semantic specialization mean it is not an independent family confirmation.
múutr|C|Fixed early uu compatible with mū́tra; final-vowel loss leaves the root accent intact.
náanu|F;C|Root-accented extended naked adjective; gn reduction and open-a lengthening, with productive feminine umlaut.
náawu|F;C|Root accent compatible with náva and the extended-adjective rule; open lengthening/umlaut do not prove which source of accent was decisive.
neeṛíi|F;Q;S|Biori root noun is a feminine formation with final accent. Turner gives nāḍī́, with long final ī, unlike the first dictionary proto token. Compare nóoṛ from the same family; ā-to-ee quality history needs checking.
níilu|F;C|Old early ī is retained before a gender vowel; compatible with both nī́la and the formation-specific root accent.
níindra|P;K|Plural-only sleep noun has initial accent against nidrā́. Pre-Vedic accent, morphology and analogy remain alternatives, not established solutions.
nóo|C;K|Early old ā raising plus m > w and final w loss fits nā́man; nóowa retains the glide and fixed accent.
nóong|P;K|Fixed early accent and raised oo are not derived from nakhá alone; nasal and long-vowel history must be established before invoking old accent.
nóoṛ|P;F;S|Fixed early oo contrasts with Biori neeṛíi. Turner gives nāḍī́, with long final ī, unlike the dictionary proto token. Separate formation/class histories are plausible but unproven.
núu|C;K|Early accent compatible with náva 'nine' after glide/diphthong contraction; not evidence for a universal aa > uu rule.
óomu|F;C|Root-accented extended raw adjective plus old early aa > oo; ā was already long, unlike the new aa in táatu.
páam|C;K|Fixed early accent compatible with pákṣman; cluster simplification precedes closed-a lengthening.
páand|C|Fixed stem accent and later closed-a lengthening fit pánthā; nasal-stop history and loss of aspiration precede that stage.
páanǰ|C|Old stem accent and later closed-a lengthening fit páñca; nc > nǰ is segmental.
panǰíiš|F;K|Teen compound needs accent selection and contraction; no direct inference from first-member páñca accent to the modern late syllable.
paṇáaru|F;Q|Extended white adjective has root-final accent. Old first-syllable ā was shortened, and modern root-final aa lengthened later.
peeróoṇ|C;K|Accent broadly continues old medial ā in paridhā́na after syllable/consonant loss and raising; exact initial ee history is separate.
phalúuṛu|F|Grain derivative has additional suffixal material; root phála is not an equivalent full formation for testing accent retention.
phiíṇ|P;Q|Mobile rising ii against phḗna would require raising before later class/accent change, or another formation. Not explained by final-accent apocope alone.
phóol|C|Fixed early aa > oo fits phā́la despite aspiration; old long aa is not a test of later short-a lengthening.
píṇi|F;C|Feminine calf-of-leg formation with early root accent; compatible with píṇḍa after cluster loss and suffix change.
pitrí|F;P|Kinship formation has final accent against pítriya. Loss of medial material and class analogy need independent demonstration.
práašu|C;K|First-syllable accent compatible with párśu after r metathesis and open-a lengthening; plural-only inflection complicates the modern citation.
preṣ|A;K|Mobile short citation compatible with final accent in śvaśrū́, but substantial kinship contraction/metathesis and shortening intervene.
puróoṇu|F;C|Root-final accent in extended old adjective precedes aa > oo raising; the OIA final accent is superseded by the formation.
putr|A;C|Short citation has no mora contrast, while putrá exposes the old final-accent class.
puunǰí|F;S|Adjectival result/full formation is compared to a finite passive verb pūryátē. That is a root link, not an accent-equivalent ancestral word.
púutru|F;C|Old accented au develops to early uu before gender vowel; compatible with initial paútra accent and extended formation.
ráaǰ|C|Fixed early accent and later closed-a lengthening fit rájju after geminate reduction.
raát|P;Q|Mobile night paradigm and unraised late aa differ from old rā́trī and from róot. Separate formation or loan history is unresolved.
sáar|P;C|Early citation aa fits sáras plus lengthening, but mobile sarí is an opposing inflectional-class fact.
sáat|A;C|saptá > short sat through apocope, then later nonaspirated closed-a lengthening predicts early sáat; no special numeral retraction needed.
saṇḍá|F;Q;P|Final accented a and -agaán plural identify a remodeled noun class; old ā shortening and initial-accent loss require formation history.
satóoš|F;K|Teen compound with contraction/raising; simplex saptá cannot predict the accent of the full compound without its morphology.
séeti|F;K|Feminine thigh formation with fronting and cluster history; comparison to a weak/oblique sakthán stem requires paradigm reconstruction.
síiu|C;K|Fixed early ee > ii with intervocalic t loss/glide outcome is compatible with sḗtu; síiwa preserves fuller material.
sígal|C;K|Initial accent compatible with síkatā despite final-syllable loss and consonant changes; shortening needs its own segmental account.
soór|S;P|Turner has sā́ra and sārá, not plain sára, and calls the ice comparison phonetically doubtful with a Wakhi comparison. Exclude from secure accent tests.
súuri|C;F|Early accent and retained uu compatible with sū́riya; feminine suffix development remains distinct from root accent inheritance.
súutr|C|Fixed early long uu compatible with sū́tra and final-vowel loss.
šaák|A;C|Mobile late aa compatible with old final accent in śākhyá; old length and cluster simplification are separate from new closed-a lengthening.
šaraál|A;C;F|Mobile šaralá and later pretonic aa fit internally, but śarád requires the expanded l-stem before a full historical derivation.
šarái|F;K|Feminine deer formation and final diphthong/plural alternants require contraction and suffix history; not bare śarabhá apocope.
šidáalu|F;Q|Root-final accent and open-a lengthening in extended cold adjective; old initial ī has separately shortened.
šíin|C;K|Fixed initial accent compatible with śáyana after contraction to ee and raising to ii; modern spelling does not preserve the old syllable count.
šilúuk|P;Q;S|Final-syllable accent against ślṓka needs epenthesis/quantity and possible loan history. Not a straightforward early oo > uu example.
šišáwu|F;S|Reduplicated comparison śṓśucat is a morphological lead, not an established immediate source of this beautiful adjective.
šóong|P;K|Early accent/raised oo against śaṅkú requires accent and quantity history; fixed inflection alone does not prove a pre-Vedic accent.
šumaáṇ|P;F;Q|Late aa and mobile inflection fit the modern pattern but not a literal continuation of syū́man. Compound/derivational and vowel history remain open.
šúur|C;K|Early accent compatible with śváśura after contraction to a diphthong and Ashret uu; Biori aa and the glide-bearing related collective support the vowel history.
ṣáak|P;C|Later early aa fits the root, but mobile ṣaká opposes unchanged initial-accent class from srákva.
ṣing|C;K|Fixed short paradigm compatible with śŕ̥ṅga. Vocalic r and final cluster simplification are separate changes.
ṣiṣ|A;Q|Mobile short citation compatible with śīrṣá; shortening and r/ṣ cluster development precede the modern form.
ṣoṛíiš|F;K|Contracted sixteen formation requires compound accent selection and ee > ii; not direct first-member śṓḍaśa retention.
ṣúuṛu|F;C|Extended hole noun has root accent and retained long uu; formation supersedes the final accent of śūrtá.
táatu|F;C|Root-accented extended adjective after geminate reduction, then open-a lengthening. Gilgiti late aa requires a different relative history.
thúlu|F;Q|Root-accented extended adjective, but earlier ū shortened. A general rule retaining all high-vowel quantity would fail.
thúri|F;Q|Feminine heel formation with root accent and shortened old ū; formation and quantity need reconstruction independently.
thúuṇi|C;F|Initial accent and long uu compatible with sthū́ṇā; feminine ending differs but does not force an accent change.
tíiṇu|F;C|Root-accented extended sharp adjective with retained old ī after cluster simplification. Contrasts with short dhrígu and limits a blanket cluster-shortening rule.
tóoru|F;C;S|Compare tā́rakā or tā́ra, not unrelated tāraká alone. Early old ā > oo fits; final gender formation still matters.
traambú|S;F;P|Wasp comparison with tántra requires substantial semantic and derivational support; not secure evidence for an inherited accent shift.
tríiš|F;K;S|The Palula dictionary accents *trayédaśa, but Turner6001 prints unaccented *trayēdaśa beside tráyōdaśa. Contracted tréeš/raised tríiš is compatible with the vowel chain; it cannot independently prove the reconstructed compound accent.
tríṣṭu|F;C|Root-accented extended adjective; short vowel before retained cluster prevents any automatic general lengthening.
tuúš|F;K;Q|Quantifier has contraction/cluster and new long-vowel history; final accent broadly compatible but is not explained by apocope alone.
uts|C|Fixed short paradigm compatible with útsa after final-vowel loss; citation by itself would not reveal the class.
wíi|P;K|Fixed early long vowel is not derived from udaká by simple final-accent docking. Extensive contraction and possible alternate formations require work.
yáab|P;S|Source token yavyá should be yavyā́ in Turner. Fixed early modern accent is still unexplained; correcting the source does not solve it.
yáandr|P;K|Fixed early accent differs from yantrá. Late short-a lengthening explains aa but not the fixed class; pre-Vedic and analogical alternatives need testing.
yúu|C;K|Initial accent compatible with yáva through glide/diphthong contraction and uu outcome; do not analyze this as old ā raising.
zaán|S;P|Loan hypothesis from Iranian jān/dzān family is preferable to counting secure jána retention; variant ǰaán and mobile ǰaní, plus Pashto dzāˈe > zhaáy with zh, require donor/adaptation work.
ẓamí|F;Q|Kinship formation and final accent differ from jāmí; initial old length shortened. Full old/new paradigms needed.
gháanu|F;C;S|Root-accented extended adjective and open-a lengthening in Liljegren; h does not induce late accent in this earlier/open environment. Strand independently records late ghâʹnu, so preserve the source distinction.
ghiíṛ|A;K;Q|Mobile late vowel fits final accent in ghṛtá, but vocalic-r and consonant history must derive the long ii before mora assignment is tested.
ghoóm|A;K|Mobile wheat noun retains late prominence, but contraction from gōdhū́ma rather than final accented-vowel loss supplies the relevant vowels.
ghoóṣṭ|A;C;K|Mobile ghooṣṭá and late oo fit gōṣṭhá after aspiration movement and apocope; fixed house in other Shina varieties is opposing comparative evidence.
ghreéṇḍ|A;K|Mobile knot paradigm with late ee; r metathesis, nasal-stop and fronting history intervene after granthí.
ghríinǰu|F;K|Extended eagle noun has root accent; vocalic-r, nasal and aspiration/metathesis histories are not captured by the accent pattern alone.
ghróom|C|Fixed early old ā > oo compatible with grā́ma; secondary/shifted aspiration does not make an old long vowel a late-lengthening test.
ghróoṇ|P;F|Fixed early accent and raised oo against ghrāṇá require a pre-raising accent change or another formation; old long quantity does not explain retraction.
gúu|C;K|Fixed early accent compatible with gṓ through vowel raising and kinship-like stem inflection gúa; full old go-paradigm still matters.
"""


def main():
    annotations = {}
    for line in ANNOTATIONS.strip().splitlines():
        key, codes, note = line.split('|', 2)
        key = ud.normalize('NFC', key)
        assert key not in annotations, key
        annotations[key] = (codes, note)
    rows = list(csv.DictReader((HERE / 'accented-nominals.tsv').open(), delimiter='\t'))
    seen = set()
    for r in rows:
        key = ud.normalize('NFC', r['headword'])
        if key == 'dáand':
            key += ':' + r['turner']
        r['assessment_codes'], r['historical_assessment'] = annotations[key]
        r['verification_scope'] = 'Explicit first-pass historical screen; page-checked central examples documented separately in research notes'
        seen.add(key)
    assert seen == set(annotations), sorted(set(annotations) - seen)
    with (HERE / 'palula-nominal-screen.tsv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(c for r in rows for c in r['assessment_codes'].split(';'))
    cross_tab = Counter(('initial' if r['proto_accent_nucleus'] == '1' else 'noninitial', r['accent_type']) for r in rows)
    noninitial_early = [r for r in rows if r['proto_accent_nucleus'] != '1' and r['accent_type'] == 'first-mora']
    summary = {
        'entries': len(rows),
        'distinct_turner_links': len({r['turner'] for r in rows}),
        'overlapping_assessment_counts': dict(counts),
        'source_accent_vs_modern_contour': [
            {'source_accent': old, 'modern_contour': modern, 'records': count}
            for (old, modern), count in sorted(cross_tab.items())],
        'noninitial_source_early_modern': len(noninitial_early),
        'noninitial_source_early_modern_formation_flag': sum('F' in r['assessment_codes'].split(';') for r in noninitial_early),
        'not_a_success_rate': True,
        'selection_limit': 'Only nominal/numeral entries with Turner links and an acute in the first source proto token; not all inherited vocabulary.',
        'verification_limit': 'Manual screening is not universal page-image verification or acceptance of the supplied etymology.',
    }
    (HERE / 'palula-nominal-screen-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
