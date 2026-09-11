# Working notes

## 05:12–05:35 UTC: corpus, scholarly formulation, first families

- Corpus inputs currently match the prior forms/edges snapshot. Expanded selection adds
  all Dravidian lects (including the separate Brahui clade) and unlinked forms, rather
  than limiting to the previous 23-language Telugu-bearing DEDR inventory.
- Reconstructed-language detection must use language metadata, not initial P: Pengo,
  Parji, Paliya and Palu Kurumba are attested languages. Reconstructions attached to
  a DEDR tree through Indo-Aryan loans are not reconstructed Dravidian inputs.
- Candidate normalization strips acute/grave stress marks only for search; it preserves
  other diacritics and never changes the evidence strings. Rebuild required after this
  screen correction; the annotation resolver always uses exact database strings.
- Visually read K03 p.157 (`krishnamurti-rule20-163.png`) and PSS83 p.229
  (`pss-259.png`). K03 Rule 20 literally conditions its short branch on differing
  vowel qualities. PSS83 explicitly excludes free roots and long/cluster roots and
  explicitly admits retained eṟuŋgu/perugu/aḍagu. These formulations must be tested,
  not silently reconciled into one purportedly deterministic rule.
- K78 full-text link currently redirects to an abstract. The abstract's percentages
  and common-stage claim are accessible, but the underlying data matrix is not.
  K83 (Krishnamurti, Moses & Danforth), *Language* 59(3):541–568, DOI 10.2307/413903,
  abstract: 63 etymologies, 945 trees, best score 71. This is a published result to
  distinguish from a fresh replication. Do not claim the full text has been read.
- DEDR 63 has retained and displaced Telugu formations, partially separated by
  hide versus submit meanings. DEDR 80 shares some exact Toda/Kannada lexical senses;
  potential root-family collapse must be a sensitivity test, not duplicate evidence.
- DEDR 236 illustrates both reference contamination and source dependence:
  `Malto alaŋku` is really a parsed editorial note mentioning Tamil; negative *al-
  is irrelevant to this lexical comparison; Sanskrit-derived Telugu lampaṭũḍu
  coexists with a tentative DEDR Dravidian-to-Sanskrit analysis of lampaṭa.
  No database corrections are installed during this research.
- DEDR 236/240 explicitly discuss semantic convergence of originally distinct roots.
  Retain the source's separation, but test collapsing them for independence.
- Every manually cited lexical string is checked against the frozen corpus; the first
  eight cases resolve to 182 form IDs without linkage errors after correcting the
  Malayalam citation spelling aṭukka in DEDR 78.

## Immediate follow-ups

1. Rebuild the corrected corpus screen; regenerate annotation tables after token-level
   outcomes are connected in `analyse.py`.
2. Resolve the difference between a language's mixed status and each evidence token's
   own outcome; do not label Gondi borrowed rāl as “retained” because the inherited
   member ar is retained.
3. Read K61's original discussion, especially secondary ṟ spellings and vowel-initial
   derivatives; local old preview searches are not substitutes for page inspection.
4. Continue the vowel-initial apical series, then review consonant-initial liquid
   inputs, nasal/lateral/long-root controls and comparable non-Telugu processes.
5. Need explicit formation-level predictions and rule tests, historical-level fields,
   systematic review prioritization, root-family sensitivity, source dependence,
   contact alternatives, and all unreviewed coverage exported in final appendices.

## Initial retroflex controls and direct K61 check (began 05:35 UTC)

- Corrected corpus rebuilt: 162,451 selected records, 53,253 groups, 5,548 DEDR
  groups, 2,701 Telugu-bearing DEDR groups. Eight metadata language IDs are
  reconstructed/generic; 46 are attested Dravidian language/lect IDs.
- 25 manually annotated DEDR entries now resolve to 547 exact evidence form IDs;
  233 language cells have explicit review outcomes. These remain working counts.
- Token outcomes now distinguish the status of a single cited form from the status
  of its mixed or ambiguous family-language cell. Uncited records in a reviewed
  group are explicitly not individually adjudicated.
- DEDR 64 and 88 share an areca/bag family, explicitly cross-referenced and repeated
  in the source. Assigned one family ID d64+d88; current entry-level count tables
  are diagnostic only until family aggregation is implemented.
- DEDR 76's displayed pancake *aṭṭu must not define the whole etymon's input:
  Tamil/Kannada cooking paradigms independently show a singleton root and tense
  strengthening. DEDR 83 similarly combines singleton closing verbs with
  strengthened transverse nouns. Preserve these input differences below the root.
- DEDR 88 contains a Latin botanical name parsed as Kannada; exclude it as lexical
  evidence. DEDR 83 includes Kuvi kīnai extracted from a light-verb expression,
  which must not be treated as a standalone reflex of the apical root.
- Read K61 p.55 directly in the Google Books authorized preview (book ID
  56PXtopfoscC; https://books.google.com/books?id=56PXtopfoscC&pg=PA55): §1.129
  places predominance of initial ḍ spellings in the 11th-century Bhārata, coexistence
  in the 12th–13th centuries, and more frequent dental forms from the 14th onward.
  This is K61's textual claim, not a new census of dated attestations. Its argument
  from neighboring ḍ loans presupposes their donor identification, which must be
  tested etymon by etymon. p.55 §1.130 compares rajju with *ar-j-, ruddu with
  *ur-d- and rubbu with a separate *ur-upp- formation; §1.131 gives rāyu/rācu
  from *ar-a-. These reconstructions differ in specificity from the independent
  comparison *aray used in the present d228 annotation.
- Read K61 p.56 directly: rālu comparison invokes Tamil aṟ-al 'become detached'
  and aṟu 'be severed'. Its end paragraph explicitly treats r in fall/increase/hate
  forms as replacing earlier ṟ, and infers early weakening of that contrast. The
  current d233 family contains regional ar-, so the alternative cross-family
  etymology and rhotic identity remain to be adjudicated, not silently unified.
- Generic web searches for Kui ḍākoli and Telugu dappi did not obtain a historical
  argument. A 2025 nominalization paper mentions dayyu : dappi, which is a lead
  for a primary dictionary/paradigm check, not evidence already accepted here.

## 05:55–06:40 UTC: source corrections, liquid classes, relative chronology

- 55 DEDR entries now individually annotated, 428 language cells, 1,018 cited form
  IDs, 2,121 raw records in those groups. All cited forms resolve exactly, with no
  linkage errors. These are review-progress counts, not final independent-root counts.
- Five DEDR 260 records labeled Gondi are Konda in the original DEDR p.25. The
  correction is explicit and ID-specific in source_corrections.py; original corpus
  labels are retained. Only Koya all- remains Gondi. A misassigned language can
  alter the apparent geographical distribution without any historical sound change.
- King d201 is Sanskrit borrowing with prothesis: arusu/arasu cannot be treated
  as an inherited vowel-initial input merely because the head is starred. K03
  pp.476–478 discusses the loan history. Kannada/Telugu inherited-looking ar- is
  thus demonstrably not always the earlier stage of an r-initial word.
- Kannada/Tulu blossom alar/aral d247 is nonadjacent liquid metathesis, separate
  from initial vowel/apical displacement. Its original l...r order is supported by
  Tamil, Malayalam, Telugu and retained Kannada alar. The two processes are coded
  on separate axes, so a retained initial vowel does not mean no metathesis anywhere.
- Kui rākp/rāpk and lākp/lāpk illustrate stop-cluster exchange. Initial apical
  displacement and that exchange can commute: a possible derivation listing one
  first is not itself proof of relative chronology.
- Obtained Winfield's complete Kui vocabulary from North Bengal University.
  The title page confirms 1929 (A Vocabulary of the Kui Language; Asiatic Society
  of Bengal). Visually checked p.3 akali rinse and p.24 ḍākoli shield, both actual
  entries rather than database artefacts; this confirms attestation, not cognacy.
  Intro p.xii explicitly lists dialectal brūnga/būrnga, brungi/burngi, kliu/kilu,
  kriu/kiru, krua/kura, plīpa/pīlpa, priu/piru and vliu/vilu. Need compare these
  independently: a descriptive arrow does not alone establish historical direction.
  P/B labels are Phulbani/Barma dialects; O marks Oriya vocabulary.
- DEDR 277 provides inscriptional Telugu ṛ̆accu (=ẓaccu) 'destroy'. K03 p.195
  explicitly connects it to *aẓ-i-ntt > *aẓ-i-cc and compares ḍappi from the
  labial transitive formation. Under this account, front-vowel-conditioned
  palatalization precedes loss of i, and displacement precedes ẓ>ḍ. Exact dated
  inscription still pending; Sastri's book covers a range, which is not the date
  of the individual token. Telugu retained aṛ̆isina/aṛ̆ipuṭa remain in the matrix.
- Cry d282 has Telugu ēḍucu/ēḍupu with a vowel still before the apical: long ē
  is not evidence of displacement. Pengo aṛ-/aṛba contrast with causative ṛat
  and intensive causative ṛatpa. DEN1 p.400 explicitly corrects earlier aratpa;
  accepting that older spelling would incorrectly convert a positive into a negative.
- Measure d295 has Telugu alavi/lāvu; Tulu short lappuni is compatible with
  local aphaeresis (K03 p.117). Badaga ādu 'measured' has a cited older aldu:
  lateral loss can yield length without initial movement. Manda lēc and eastern
  cry ṛī need independent vowel histories; exact quantity counts must not erase this.
- Desire d301 independently supports high i but Telugu lā̃cu has long ā. A
  compensatory-lengthening account after nasal loss is testable; the exact matching
  nasal-palatal derivative is not yet independently reconstructed. Do not invent *a
  merely to make the quantity law fit. Added this as a genuine unresolved rule test.
- Still needed: family aggregation (including newly encountered d291/d295 overlap),
  formation-specific input predictions, source access ledger, wider controls and
  systematic unreviewed inventory. No final narrative report has been drafted.

### 07:08 UTC: 89 etyma and primary inscription checks

- Now 89 individually annotated entries, 663 reviewed language cells, 1,536 cited
  database form IDs plus six source-only observations; zero form-linkage errors.
  Counts remain diagnostic entry counts, not the final independent-family analysis.
- Sastri p.310 gives inscription38 the date 890 CE. Its p.311 directly shows ḻassi
  line14 and aḻisina lines20–21 / aḻiputa line35: different formations of destroy
  coexist in the same inscription. The earlier unlocated-date note above is superseded.
  Sastri p.291 dates inscription16 to 670–680; DHARMA00026 verifies its ḻaccina and
  records the older editors' competing ḍaccina reading. Dates are source attributions.
- Downloaded the public DHARMA Telugu XML research snapshot (101 texts, commit
  9cd04e21aa21e9f401090a7db76d25675cce5a27). Text-specific metadata is CC BY-SA 4.0;
  repository-level license differs. This is a reading cache, not Jambu ingestion.
- The iṭ-series now compares same-quality i+i in beat d443 (Telugu ḍī) with i+u
  in put d442 (Telugu iḍu; retention also in Kui/Kuvi/Pengo/Manda). Rule20 explicitly
  permits high-vowel contraction when the two vowels match. Food iḍi d439 retains
  the same i+i order but culinary borrowing chronology is unresolved, not assumed old.
- Original DEDR p.43 corrects two apparent Kolami beat forms to Konda: source ṛey
  and ṛī. Actual Kolami iṛ- retains order. Page44 corrects Telugu-labeled edamakei
  to Hislop Kolami and explicitly calls it a Telugu loan. Geographic conclusions
  would be wrong without checking these source headings.
- Spatial d434/d448 share forms and meanings, so primary family is d434+d448.
  Related separation, obstacle and left-side roots are potential sensitivity merges,
  not automatically one etymon. Telugu davvu, ḍā/dā and ḍayyu need a vowel/formation
  history beyond a formulaic i+a > ē contraction; these are marked unresolved.
- Sastri p.111 links dappi thirst to dayyu weary (d447), an alternative to d109's
  southern aṭ/ṇṭ comparison. OCR located; image verification next. Homophonous
  ḍappi destruction remains a separate family. No final report drafted.

### 07:50 UTC: 129 reviewed entries; morphology and regional comparisons

- Validated 129 entries, 1,010 language cells and 2,438 cited database IDs, plus
  12 source supplements before the latest 15 additions. Every cited form resolves;
  this checks linkage, not the truth of each proposed historical derivation.
- Sastri p.111 image verified: dappi thirst is explicitly connected with dayyu
  weary. The 890 inscription date and its differently formed destroy tokens were
  checked in printed pages 310–311, not inferred from dictionary order.
- Final Hume 2004 Language 80(2):203–237 obtained and pp.225–226 visually checked.
  Kuvi long-vowel plural formations (rope, fish, louse) show a later, different
  subsystem; historical Telugu’s restrictions must not be projected onto them.
  Hume’s 1,535 open/736 closed counts are text syllables, not etymon denominators.
- Two d474 now has explicit human/nonhuman formations. Telugu/Gondi displaced
  nonhuman numerals coexist with retained iru-var human forms; Malto iwr is a
  separate medial rw > wr event, not initial-vowel metathesis. Tamil/Malayalam
  initial-loss free numerals cannot automatically count as the SC contraction.
- d475 jujube source p.46 recovers missing Telugu rē̃gu/rēnu and identifies an
  explicit Kannada Telugu loan. A parser error had labeled Kolami rēŋga Telugu.
- d502 descend: K03 pp.188–190 supports old -k/-p and -nt/-ntt formations with
  Tamil, Toda, Kannada, Parji and Gadaba comparison. Short digu can continue a
  consonantal formative, gemination and degemination, rather than an otherwise
  unexplained exception to two-vowel contraction. Old paradigmatic functions are
  K03’s reconstruction; intermediate proto-stages are not textual attestations.
- d527 lord has historical retained eṟa beside extended displaced ṟē̃ḍu. d516
  descend/port has eṟãgu versus ṟēvu. These require formation-level predictions.
- d528 eaves survives in Telugu only as second member talli-y-eṟa in this source:
  do not treat it as an unqualified word-initial counterexample. d529 eṟaci meat
  and d586 oḍalu body provide independently matched low-vowel retentions.
- d561 nail has southern ukir, SC/CD/Brahui gōr/kōr, and Kurux–Malto ork. Its
  deeper direction is unresolved; do not solve it by an outcome-selected *okar.
  Original DEDR p.55 supplies missing Gondi gōr and Gadaba gēre, research-only.
- Additional erroneous display reconstructions: elephant on d516 descend,
  cardamom on d513 young, prawn on d533 fly, pestle on d572 ring. Excluded from
  input inference with stable IDs recorded. These are not database modifications.
- Next: finish a bounded u-initial comparison set, then consonant-initial core
  and independently selected controls, other-family processes and unlinked data.
  Family/formation denominators and final narrative remain pending; no report yet.
# 08:18 UTC checkpoint — vowel-initial review expanded to 182 entries

The linkage check passes for 182 entry analyses, 1,472 reviewed language cells,
3,577 distinct cited database form IDs and 30 source-only observations. These are
work-progress counts, not independent-root rates. Root-family and formation
denominators have not yet been finalized.

The new u-initial review distinguishes plough *uẓ-n / *uẓ-kk from eastern *uẓ-u;
comb and stroke share one counting family. Black gram uddulu, exist uṇḍu and
urine ucca preserve the initial vowel despite losing the medial apical through
cluster changes. They should not be called hidden initial metathesis without an
independent restoration argument. Sweep has both long and short formations;
Kui ḍupka cannot establish displacement of a long root until its exact input is
known. The original source gives its separate k-p > p-k morphology explicitly.

Inside d698 contains a genuine input distinction: singleton *uḷ-a-n locatives
versus independently geminate *uḷḷ-am mind. The imported date on Telugu lōna is
wrong: DEDR dates preceding Old Telugu oḷana to the seventh century and ḷōna to
the ninth–tenth. Those dictionary dates still need epigraphic localization.
By contrast, low-a sleep/recline, steady/support and sheath formations give
real retained Telugu comparisons; semantic labels are not an explanation of
application. Heed d712 supplies a specifically negative Telugu formation with
an independently negative historical Kannada counterpart, worth comparing
with destroy and silent/speak, but insufficient for a blanket negative rule.

Research-only language corrections now additionally restore the Telugu roll
forms from Kodagu, Tulu plough forms from Kodagu, Kui sweep from Gondi and four
Kuvi onion forms from Manda. Raw corpus and database remain untouched. The
source supplies both Kui ubga 'butt' (706) and 'be fit' (710): the repeated
cluster is not a parser error and must not count as two independent metathesis
innovations merely because DEDR places the meanings in separate entries.

Next: consonant-initial core and independently selected retained controls,
followed by quantitative formation annotation, family collapse and wider
non-apical/dialectal processes. No report drafted yet.
# 08:30 UTC checkpoint — 199 annotated entries

The 13 newly reviewed core/chronology entries and four first lowering entries
are linked successfully to their cited forms (199 entry analyses total).
Core new/tree/finger/blind/swallow/sink are now freshly reviewed rather than
copied from the parent casebook. In the new group, Telugu koḍuku/kōḍalu and
krotta occupy distinct formation classes. K03 supplies modern kotta absent
from the corpus group; its presence after krotta is positive evidence of
concealed displacement, unlike unattested hypothetical Cr stages for every
southern assimilated form. Konda Araku marán and Sova mrānu are source-only
observations linked to the same tree root; dialect pairs are not time series.

K03 Rule20 pp.157–158 has a formal-description problem to discuss carefully:
the prose initially permits every listed nonnasal apical for long branches
a/b, restricts short branches a′/b′, but the immediately following Telugu
reflex table gives no postconsonantal ḍ/l/ḷ. Do not silently treat the most
permissive formula as an exceptionless empirical generalization. Its two
claims about Konda productivity also differ: p.158 says ceased, p.160 gives
ongoing dialectal formation; report as historical source evidence, not a
2026 productivity survey. The published Gondi/Konda/etc percentages exclude
Telugu and have their own denominator, never ours.

For lowering: scoop1959 gives independent Konda ker order but no independently
attested a formative. Pit1818 has independent high-i pit versus low-a tube
formations; a pit-name ā cannot itself demonstrate that its input was the
low-a tube formation. Cut1859 has genuine independent low-ay support; the
only Old Telugu record is long kōṟa. Friend2018 independently has both short
kiḷai and long kēḷ. The latter’s Badaga plant cluster is not friend evidence.
No final quantitative rates or report have yet been written.

# 09:15 UTC checkpoint — 234 annotated entries

Validated 2,161 language cells, 5,975 evidence links to 5,939 distinct database
records and 36 source-only observations; no linkage errors. These remain entry
coverage counts, not independent root frequencies. Full reviewed groups contain
9,669 records; inclusion in that appendix does not mean each record was adjudicated.

The consonant-initial core is now substantially reviewed. Turn d3246 gives an
especially useful independent formation contrast: Tamil tir-u-pp/tir-u-kk and
tir-u-k versus Telugu trippu/trikku and retained tirugu. Exact suffix support
must nevertheless be checked separately in every family. Telugu vrīlu d5411
has a proposed -il/-ul derivative that K61 explicitly says is unattested elsewhere;
its reconstruction cannot independently confirm a vowel rule. Burst d4194 and
prattle d4430 both contain Telugu prēlu, but they are distinct etymological
problems; neither justifies inventing *per-al from the outcome. Jump d3364
truḷḷu is a secondary-r comparison, not a secure initial metathesis case.

For eastern lowering, bone d4418 has independent e/i formations, not an
independently recovered a. Hare d4968 involves secondary apical development
from earlier c/y, and last-year d5153 is a compound problem, distinct from the
long bare year control. Sell d4536 was separated from spread by K80 partly
because of its vowel outcome: that editorial decision cannot independently
validate the same conditioning claim. Salt d2674 is next as a nonmetathetic
contraction control. More free-root, geminate and nasal-cluster controls follow.

K80 p.498 was visually checked again. K61 Google Books p.131 now displays a
preview limit, so prior verified page notes remain the source for that location;
no new visual verification is claimed and the restriction was not bypassed.
Burrow 1976's Manda sketch has been identified bibliographically, but its
pp.40–41 discussion of incline is not yet directly read.

No final report or final rates have been drafted. Remaining work includes the
formation/family denominator, broader processes and unlinked-data review,
structured epigraphic chronology and a precise pending-scope ledger.

# 09:48 UTC checkpoint — 269 validated entries before pronoun additions

Validated 2,514 reviewed language cells, 6,988 evidence links, 6,949 distinct
database IDs, 39 supplementary observations and 10,975 raw records in reviewed
groups; zero linkage errors. These are coverage diagnostics, not root frequencies.
The e-initial cohort adds retention controls and several important challenges:
white-ant d837 has independent elub/elum but eastern līm, voice d835 has full
Parji iluŋg (misassigned Telugu in the database) versus līŋ/lēŋ, and long rise d916
has independent ēṟ/ēl versus Telugu rē-/lē-. Do not invent hidden -a or short
grades to regularize them. Rise d851 short *eẓ has Telugu eccarika, whose r is
derivational, whereas Telugu lēcu belongs to the distinct d916 comparison.

Tooth, leg, paddy, pig and anthill controls distinguish closed free roots, long
roots and inherited nasal/geminate clusters. Tooth-brush compounds have a
separate internal liquid exchange in Gondi/Parji. Pengo ipka supplies an additional
non-apical stop-cluster process, so the Kui kp comparison is not geographically
exclusive. Telugu enumu buffalo has medial r>n before m (PSS83 p.394), not secure
concealed metathesis. Salt has labial loss and contraction; K03's Gondi sawvor
also needs separate vowel-order comparison.

DEDR pp.79,81,82,88 directly checked. K03 pp.97,100,222–223 and PSS83 p.267
checked in full-text source. PSS83 places Old Kannada syncope before vowel
heightening, using erumay/erutu/elump; this independent chronology is relevant
to avoiding a metathesis analysis for emme/eddu/emmu-like outcomes.

Pronoun work now separates direct and oblique cells in research observations
linked to the original database paradigms. The distal/proximal entries are one
process family, with apical AND labial participation. Konda deni versus Telugu
dīni is a vowel-history test, not a reason to silently reconstruct *idin.

# 11:09 UTC checkpoint — 314 validated entries; auxiliary morphology audit underway

Since the preceding checkpoint, completed long/o-initial controls, late Kuvi nasal
paradigms, Brahui comparison and the literary say paradigm. Main validation now
has 2,862 language cells, 8,030 evidence links, 7,949 distinct cited database IDs,
81 source-only observations and 14,034 raw records in reviewed groups, with zero
linkage errors. These are coverage diagnostics, not independent root counts.

Root-family quantification is implemented in quantify_families.py, with a primary
partition and a separately justified sensitivity partition. Historical language
aliases are combined only in the time-aggregated view. All class numerators and
denominators have explicit membership rows. Formation tests now distinguish full,
cluster, conditional and mixed input evidence. Downgraded new2149 and snake2359
to conditional because their precise consonantal formations are not independently
matched as strongly as the lexical root vowel. Deictic and literary nasal cases
have explicit formation rows outside the classical lexical apical test.

Brahui needs both new positive and negative cases. Emeneau1997 p.445 identifies
tāring beside dranzing sift, confirming the short *tar comparison rather than long
*tūr winnow. pirɣẖing twist remains a genuine closed-stem retention challenge.
trikking sprout and trikking wither are distinct semantic families; no automatic
merge from homophony. mux knee and bēɣ woman can lose medial l in clusters without
undergoing hidden initial metathesis. PSS83’s seven cases are a source sample,
not the full database denominator.

Historical source corrections materially change the chronology argument:

- Sastri1969 p.285 inscription9 attributes initial-ḻ destroy to the first quarter
  of the seventh century (600–625), earlier than the independent 670–680 witness.
- The same page’s n.1 rejects an earlier oḷana reading in favor of ēḷan ruling.
  DHARMA00099 adopts ēḷaN. DEDR’s early locative may rest on this superseded
  reading; until its inscription is identified it is A, not a dated R control.
- Two Druggādēvi witnesses must not be confused: Lakshmipuram c.681 in Sastri294/
  DHARMA00101, versus Sastri72’s SII V1217 Ganjam1290 citation.
- DHARMA40 rēṇḍ-agun merits image checking as an early long numeral; nearby
  ḷēnṟu has long ē partly inferred by the editor from metathesis theory and therefore
  cannot independently validate that theory. Older edition has ḷenṟu.
- Historical dēni cannot be claimed as an attested earlier proximal *dēni > dīni
  merely from an English this-grant translation: Sastri178,184 treats dēni as
  interrogative. Earlier proximal identity remains unproved.

Kuvi louse4449 adds a particularly explicit long-nasal paradigm: Sunkarametta
pēnu:pṇēka versus Bisamkatak pēnu:pēnka. Keep dialects separate; this is not
demonstrated free variation. The god4438 and louse4449 roots are homophonous
but distinct. Fish4885 singular mṇīnu has two nasals and needs plural analogy or
excrescence, not a literal one-nasal swap. The proposed primary nasal input of
eel4737 is false: independent full forms have l.

The local velar/labial screen was expanded to all four Kondh languages: 152 records
in 123 groups. Every hit is being adjudicated. Kui has 61 source-supported verbal
families (64 forms) with explicit velar-before-labial analyses; nominal -pka plurals
and English pumpkin/climbing false hits are separate. Important new challenge:
DEDR1080 S. kakpinai joke retains k-p, unlike Hume2002 p.38 Israel1979 kap-ki a-
laugh at each other. Keep the source/dialect/formation distinction; Schulze1913
original page is not yet obtained. Do not erase it to make the cross-language
statement exceptionless. Kuvi hūpki spit and tapkali quiet, and Manda kupki fill,
have independently labial bases: they are p+k developments without k+p input.

Read Garrett and Blevins2009 pp.537–543 and Hume2001 p.9, Hume2002 p.38 closely.
The former proposes an analogical origin of the apparently regular Kondh process:
old g/p causative replacement, reinterpretation as kp reduction, double plural-
action marking with k, then generalized synchronic kp>pk. The intermediate lexical
forms are explicitly hypothetical. Database regularity tests the resulting
alternation, not its phonetic historical origin. A suffix can be participial,
infinitival, intensive or desiderative; do not call all labial forms causatives.

Read all 30 Kurux–Kunha pairs printed in Kujur and Dash2025 pp.118–119. A separate
annotated appendix distinguishes plausible initial/final/CC reversals, laryngeal
migration, syncope-plus-final-vowel alternatives, suffix selection and internally
inconsistent transcription. Kunha is absent from the snapshot language inventory.
The reported 5,000 elicited items are not published as an analyzable denominator.
Neither contemporary Kurux ancestry nor word-specific contact is established by
the paper’s general discussion. Database bow789 and flank3520 comparisons are
reviewed individually and do not show Telugu-type initial displacement.

## Final cluster sweep and quantitative freeze

The coverage crosscheck found90 of the prior116 Telugu cluster candidates absent
from the expanded case annotations. All90 have now been reviewed in comparative
panels and annotated in cases_cluster_031 through035. The final frame contains409
DEDR entries,403 primary families and365 sensitivity families. Every prior cluster
candidate is represented; this does not mean every candidate is metathesis.

Extra-r cases receive explicit alternatives:1898 krūru has two rhotics;3411 treḍḍu
retains the original retroflex;5368/5369 vrālu retains l;5250 vranti retains nt;
5555 vrēyu has no independent full r cognate.5087 Old Telugu mṛ̆ēka is explicitly
of unknown meaning, so goat gloss cannot be copied onto it.4608 prāmu and regional
Manda prēmba lack an independent full-order input. Competing roar4973/4989 and
ripen5017/5046 assignments remain A under both entries and are merged only in
sensitivity. Plant compound4716 and expressive sleepy4710 are not secure positives.

Strong added directional comparisons include1292 karãgu:krā̃gu melt,1774 Kannada
koralcu:Telugu krōlcu recite,4971 moraḍu:mrōḍu stump,4728 marbu:mrabbu cloud,
4559 poẓtu:proddu day, and5372 barduku:braduku live. The last belongs to a short
expanded derivative despite the independently long bare root vāẓ. New long-root
residuals are retained rather than supplied with invented low-a suffixes.

The formation audit now has182 rows in135 entries, covering every117 Telugu
D-bearing primary family. Strict surface quantity tests:25/33 long predicted from
full low/equal-vowel inputs,8/8 short predicted from different high vowels,21/21
short from independently supported consonantal inputs. The eight first-class
exceptions are474,694,1787,4993,1767,2687,4312,4975. Several independently possess
consonantal variants; earlier syncope can explain them, but is not proven in Telugu
merely by the modern short output. All rows with unresolved exact inputs remain
outside the strict tests. Formation denominators overlap and must not be summed.

Input-label audit normalized synonymous apical labels, including ḍ, ṟṟ and ẓ/r,
and explicitly classified mixed nasal/apical inputs. No outcome was altered to
make a class more regular. Added joint Domain×V2, Domain×apical and Domain×V1
tables and an independent C1 identity axis. Family-count membership independently
reproduces19823 table rows and429312 memberships; exact-form linkage has zero errors.

The source sweep also found editorial fragments3115 and5372 and plant/home
mislinks4716. They are documented without mutating Jambu. Monier-Williams1899
p.322 confirms that Sanskrit krūra has sharp/hard senses, leaving borrowing or
convergence viable for1898; direct Telugu source history still needs verification.

Analysis is now frozen for report drafting. The remaining5139 DEDR groups, including
2326 Telugu-bearing groups, and3101 pending independent-screen candidates are
explicitly exported. Unetymologized exploration assessed18 records only. These
coverage limits cannot be repaired by treating unreviewed material as retention.

## Final report and artifact audit, 12:26–13:00 UTC

The narrative was drafted only after the 12:26 analysis freeze. It separates
application from conditional output quantity, historical shared background from
word-specific shared innovations, and initial-apical displacement from the later
Kuvi and stem–suffix stop processes. The report links all highlighted cases to
the complete casebook or the relevant auxiliary appendix.

Independent recounting passes for 19,823 class rows, 429,312 family-membership
rows, 17 formation-class rows and 5,796 pairwise groups. The report's source index
now keeps research-only prose citations separate from database source-key
abbreviations. The manuscript, README and source-access links were checked.

Presentation checking found and fixed a casebook hash-navigation defect after
search filtering. A final field audit found two stop-input extraction defects:
d325's split ag-b analysis had been replaced by its English gloss, and Pengo
d1079's italic HTML tag had been mistaken for an input. The corrected fields are
ag-b- and kag-ba-, respectively, directly supported by the already-reviewed source
records. The extraction now rejects any claimed explicit stop input lacking the
velar–labial sequence. These corrections do not change classifications or counts.

The repository check completed with zero errors and seven warnings in five
application files. No application implementation or source-database mutation was
made for this investigation. The final appendices preserve missingness, uncertain
analyses, source corrections and the exact pending queues.
