# Working checkpoint — final delivery

## Final state — supersedes every working checkpoint below

Research and delivery are complete for the authorized eight-hour pass. Substantive analysis froze at 11:55:44 UTC, before narrative composition. `REPORT.md` and `REPORT.html` contain the final 12-section narrative, with 16 main tables. The offline appendices contain all 1,686 family dossiers, 25,505 raw records and 25,593 analysis tokens; 43 quantitative tables include 27 explicit class domains and all-seven-language counterpart ranges. Five supplementary etymological proposals remain outside the frozen family registry. All review and primary-source access limitations are explicit.

The final 22-program reproduction passed. `presentation-audit.json` records 561 successful checks; `presentation-qa.json` records browser inspection. `integrity-audit.json` passes with no missing records, altered raw fields, duplicate/missing family annotations, unresolved research ancestors or drift in any of the nine live database inputs. `artifact-manifest.json` seals the final deliverables. The only changes after the analytical freeze were report composition, presentation, reproducibility documentation and joins of existing frozen class inventories for fuller counterpart tables.

Verified archive: `../quantitative-2026-09-09.zip`, 251 files, 20,315,168 bytes; SHA-256 `cff67a3590fcffebc2f5177a4bc34f3abd99d71cdc6f53eef4825cb0208595e6`. The sibling `.zip.audit.json` records CRC verification. The archive includes every manifested file and the manifest itself; mutable working checkpoints, logs and caches are excluded. Do not modify a manifested artifact without rerunning audits and deliberately rebuilding the archive.

The local preview server remains in tmux `shinaic-quant-0909:1`, serving this directory at `http://127.0.0.1:8765/`. Analysis shell is window 0. No database, parent report or website files were edited; the research directory and archive are new untracked artifacts. No agents were used. No further work is pending in this pass.

---

## 12:13 final presentation checkpoint — newest

Analysis frozen at 11:55:44 UTC; `ANALYSIS_FREEZE.json` records counts and the fact that the narrative had not yet been drafted. `REPORT.md` and `REPORT.html` now contain the final 12-section, approximately 6,300-word narrative. Substantive research is complete for this time-bounded pass; remaining work is presentation, replication documentation and final artifact QA. Deadline remains 13:07:11 UTC.

All frozen counts and corrections from the 11:49 checkpoint are in the report. Browser verification confirms report typography, full contents/navigation, exact family search (10702 gives one dossier), and rebuilt appendix labels. Continue with exact record search, table navigation and final link/number audits. Report and appendix browser tabs exist (iab browser 1; tabs 2 and 1), local preview server remains tmux window 1. CUA session was reset and reinitialized; only `appendixTab` binding currently exists. Use `cua.getTab('2',{browser:'1'})` for report handle. Analysis commands must still target `shinaic-quant-0909:0`.

No PDF is required or being created. Deliver Markdown, self-contained report HTML, offline searchable full appendices, TSV/JSONL exports and reproducible analyses. Add a package README and supplement-ancestor explanation to the generated data dictionary; rerun reference builder and renderer after copy edits. Rerun `audit_analysis.py` last so the manifest includes the final report and QA artifacts. The last analytical audit passed and all nine database hashes match the starting snapshot. No database/site files were edited.

---

## 11:49 continuation checkpoint — newest

Time budget ends13:07UTC, ~78min remain. Still NO FINAL NARRATIVE REPORT. Freeze substantive research around12:00, then write report/QA. New full i-declension extension:43 non-aa/ee+i candidates,42 valid cells/30lexemes all final-i accent; citationL24,E6,S5,short-unmarked7. One excluded gun variant thupéek/toobakí is mismatched dialect metadata. Combined with aa/ee+i73cells/66lexemes =115 valid cells and **95 distinct lexemes, not96** (happiness xeeraát/xeerát→xeereetí overlaps). `idecl_extension.py`, `lexical_annotations_05`. All43 read individually. Independent Biori short roots explain E citations grass/nose/lake/plateau/colour; stream náaṛ/naṛí differs from canal náaṛ/neeṛí. No claim i-declension alone predicts citationL.

Complete offline appendices built by `build_appendices.py` and `build_reference_appendices.py`: `appendices/index.html` (~51MB embedded all data), fullJSONL raw46MB/tokens48MB/dossiers5.6MB, `tables.html`, `sources.html`, `proposals.html`, `data-dictionary.md`. Narrative links intentionally awaitREPORT.html. Browser smoke test works: full1686families, openingnightdossier, recordlookup and sourceannotations. Some UI improvements applied (exact numeric family/rawID lookup and humanized labels) need rebuild/reload. Final screenshot QA still needed.

**Tmux change:** session now has window0 zsh ANALYSIS and window1 `research-preview` SERVER. Always target `shinaic-quant-0909:0` for analysis commands; bare session targets current server window! Server runs `python3 -m http.server8765 --bind127.0.0.1 --directory<quantfolder>` in window1. CUA persistent bindings `browser` =iab id1, `appendixTab`=tab1 at127.0.0.1:8765/appendices/index.html. Currently searchf_526agso5rjzf6, records mode. CUA docs read; useonlyCUAforbrowserinteractions. getByLabelView failed (implicit label includesoptiontext); observed `#mode` locator selectOption works. getAXState afteractions. Browser remains hidden. Do not delete serverwindowmidanalysis. No deliverable marked yet.

Full `reproduce.py` ran successfully, allmainmodel scripts. `audit_analysis.py` found one missing analytical ancestor10310-2 ram (correctedStrandreference, existingDBsubentry absent from original ancestrywalk). Fixed with frozen `supplementary-ancestors.tsv`, `supplementary-ancestor-provenance.json`, generated only afterassertingforms.csv matchesoriginalhash. Helper `load_ancestors()` used byquantify/structural/appendices/audit. Originalrawancestralextractunchanged. AuditnowPASSES:25505raw,25593tokens,1686fams,12321historicalobservations,12235researchlinkedraw,13270unlinked. All9liveDBhashesmatchfreeze. Zerochangedrawfields, missingIDs, dupfams, unresolvedresearchancestors. `integrity-audit.json`, `artifact-manifest.json`, `report-metrics.json` exist; rerunafterfinaledits.

New `source_register.py` produces37? source/authorityentries withactualaccesslevels; nofakeprintedcheckofDegener/Buddruss. AdditionalprimaryGomesURLverified. `class_counterparts.py` adds11classcatalog andall7-language counterpartpanels (notcrosslanguageaccuracies): exactclassmembertokens separate frombroaderfamilyrecords, unlinkedmembersnoinventedcognates. CodecorrectedtofilterexactsplitIDs/sources; needsrerunafterthatpatch. `residual_ledger.py` createsexception-ledger/editorialdecisions/allfamilyopenissues. LastpatchcorrectedKundTable12selectorandDrasehcombinedlabel; rerun. Referenceappendixcatalog includesallnewtables; rerunbuilderaftertables.

Important reporting scope: Gilgit short-a cluster screen5L includes*jhalla→jeél andmanyú→moón; onlyfew/tears/hotaretheclean aa-with-ending trio. It is an exploratoryinputclusterretrieval, not5independentlyprovedsamecompensatorychanges. Allvowels→lateisfalse(úu~ṭcamel,líic̣opoor,búušicatE). Palulau-correctionstillmandatory115/129gram,111/126POS; no115/115claim. Propertyscreenfinal Sh35penult4mixed/39;Pal25penult2mixed1other/28;Sv1penult3final10unknown/14;Kalk0retainedending;Kund1unknown;Bro10penult1unknown;Ush14penult1ante4unknown/19.

No matplotlib in system or bundledPython; skipfiguresoruseanotherstandardtoolonlyifhelpful. Tables already clear. NoPDFrequired; mainMD+HTMLwithcompleteappendices sufficient. Needfinalreport likely~5–8kwords clear narrative, all7scope, strictdomains, fullresidualtable andprimarylinks. Mainfindingsknownfromliteratureversusnewquantificationsdistinguished. Writing startsONLYafterfreeze. Fullnarrativemustnotclaimindividualprimaryreviewall25505records;11800+remainunlinkedinventory. UserDB/siteuntouched, unrelatedgitmodspreserved. Noagents.

---

**11:24 update supersedes older statistics.** Deadline13:07UTC; freeze substantive analysis around12:00–12:15 and only then write final narrative. All1686 family dossiers have first-pass notes; record QA remains explicitly uneven. New work: all573 Knobloch Sauji records reviewed in335 gloss groups,294 new research links (`research_links_13`, `lexical_annotations_01`). New source-based formation decisions correct Palula boy to unaccented *phōta8399-9, spleen to unaccented *śyāmī12664-3, brother-in-law to dēvará6546-2 with dḗvara alternative, and exclude phonetically doubtful ice13355. `formation_decisions.jsonl` applies last to raw and split tokens. Revisions through_10. Fig nearest correction means Gilgit short-a cluster screen5, not6.

New independent productive nominal class: Palula i-declension, citation last root aa, full inflected ee+i, same stem frame:74 candidates,73 valid cells=66 lexemes, all citationL→final accented i. One excluded Biori rainbow niildhráal/izreeṇí is mismatched synonym metadata, not an actual paradigm. `umlaut_nouns.py` and `lexical_annotations_03`; night raát/reetí belongs here. This modern class includes book, glass, programme and native abstract nouns; it does not alone explain the historical reaccentuation.

New vowel-raising pairs:78 all reviewed. Closed final Biori E-aa35→Ashret oo29/uu6; E-ee11→ii11; L-aa2→aa2, but both L controls instantiate one accusative ending. Proto-au has independent internal w evidence only in father-in-law; four/story are published proposals, stream/lap/Drosh unresolved. Other syllable domains30. The adjudication script had a quoting error and was finally fixed and successfully run11:20; `lexical_annotations_02` now exists. Do not claim it existed earlier.

Restricted old-long nominal follow-up29families: Sh bary10E+1conflict, oxy9L+2conflict; Palula bary9E+1conflict, oxy5L+2E(smell/village). Degener-only17/17 (7baryE10oxyL). This is an explicitly selected nominal subset after a broad falsification screen, not an exhaustive a-stem rule. Competing old accents/inputs sensitivity included. `old_long_nominals.py` outputs all7-language panel and12 source/input scopes.

Dras plural suffix review: eh/eɦ60 citations,57 final accent (53 final-only+4 dual),3 stem-only; plain e176,24 final accent (22 single+2 dual),130 stem-only22 unmarked. All287 plural citations already annotated. Raw citations not independent etyma. Palula short-a sensitivity:37allpairs,36closed,35closedlexemes; collapsed closed no-h25E1L(today), h7L2E(mountain/grape).

New numeral series: Hultman Table16p28 has11–18 all8H2, Palula all8E on the final syllable;19 and20 both PalulaL/KalkotiH1. Independent ten compounds versus twenty formation explains twelve/thirteen as a coherent series hypothesis, not two individually rescued exceptions. All381 retrieved numeral tokens (379rawrecords) retained in all7-language panel with source notes; `lexical_annotations_04`. Survey twenty biš panj contains five and is excluded as a clean twenty citation. Modern creaky phonation in HKAT is not silently recoded as High.

Five supplementary etymology proposals in `etymology_proposals.jsonl`, outside frozen1686-family registry: Sauji skin gaːɬ→gā́tra4124 (precise Gawar-Bati gaλ skin parallel, possible contact); Sauji grass drab→darbhá6203 (Lahnda drab independent parallel); Brokskat deodar→6531; Ushojo joŋ/pɑ̃ split→5082/8056; Ushojo widow→10593branch5. No DB edits.

Next: build complete appendix renderer and source register, rerun every model and full analysis_data build, integrity/denominator audits, then freeze and narrative. Old annotated-records/families and structural screens are STALE until rerun. No agents, no final report drafted.

---

## 10:42 checkpoint (superseded where noted above)

**10:42 update supersedes all older statistics below.** CRITICAL: the earlier Palula 115/115 adjective claim selected literal final u and wrongly omitted accented ú. Correct selection uses accent-stripped final_segment. Grammatical regular/umlaut gender-inflecting short-u types:129 unique,115 penultimate,8 final,6 unscorable. Explicitly POS-tagged adjectives:126 unique,111 penultimate,9 final,6 unscorable. The 9 final types have individual source-based explanations in adjective_residuals.jsonl: two age comparatives, four quality pro-adjectives, one tail-less compound, kirpuṭú unresolved, and muṣṭú which the grammar treats as an adverb. Umlaut subclass37/37 scorable penultimate; Gilgit short-o adjectives110/110 scorable penultimate plus11 unscorable, selector checked to include ó. User already informed of correction. NEVER repeat the unqualified115/115 Palula generalization.

Revisions through _08, decisions through _15, research links through _12, source observations through _05. New Dras review covers all287 plural candidates and attaches source/paradigm notes;139 added research links. Raw eh plural citations60:53 final,4 dual accent,3 stem; knife occurs twice with conflicting stress. Source has internally conflicting people, knife, spindle, egg, dates paradigms. New Kundal primary appendix has21 paradigms and records unresolved long-stem postaccenting ox/shoe; source is2004 draft. New Kalkoti/Palula81 manually reviewed comparison groups: pref inal-accent plus short-final-vowel class has10 scorable formcells (9 broad families), all final High/rising,10 unknown,8 excluded; E without short-final vowel has7 consistent zero/default,4 residual (village/man/12/13),14 unknown,10 excluded; L class4 H1/falling,4 Low-interaction,4 unknown,1 excluded. Units and source differences explicit in generated tables. All figures require final rerun.

Source-aware phonology fixtures30 modern+8 old passed. Dras repeated vowels are separate nuclei, colon is length; vowels separated only by a stress sign now flag unresolved syllabification. This affects property-location screens; rerun them. Short-root cluster screen previously contained a false short input for fig: decisions_15 correct three modern records to existing *phālgu9063-2, preserving family9063. Gilgit short-a cluster set should then have5 families all late, not6. All15 property-screen residual records annotated, including real Ushojo initial-stressed trisyllabic 'kinono black. Do not normalize away unexplained stress.

Next: Palula pair unit sensitivity, source/lect/input sensitivity, remaining Sauji source review, source/notation register, and complete final exports. Full analysis build needs rerun after new annotations. Freeze analysis around12:00–12:15, write final narrative only then, deadline13:07 UTC. No report draft or agents.

---

## 10:10 checkpoint (superseded)

**Newest update, superseding everything below:** first-pass family annotations complete 1,686, revisions through _06; record decisions through _14. All 473 previously unlinked Hultman Kalkoti records manually reviewed in review_sets_01–06. Research links through _10 plus 505 manually accepted same-language identity records in identity_links.jsonl. Identity acceptance now reproducible from the frozen 313-candidate snapshot; 3 rejected. All 590 selected Brokskat/Ushojo unlinked records assessed. All 269 printed Brokskat Table 2 items read. Fourteen Bro splits plus 74 reviewed two-source merged records split; expect 25,593 tokens, full build still needs rerun.

Quantitative programs now exist: quantify.py (nearest-input family/source outcome sets and broad old-long falsification screen), palula_pairs.py (37 Biori short-a / Ashret long pairs: 27/28 no-h early, 7/9 h late), adjective_test.py (115/115 scorable Palula regular/umlaut u citation types penultimate), adjective_extension.py (running Gilgit tagged short-o adjective test and full family panel), dras_pairs.py (287 plural candidates, all manually inspected as a compact list; 236 have exact-gloss SG counterparts). Source contour observations through _04; Hultman Table 9 page corrected to 16. Kundal source is 2004 draft, not unread final 2005. Phonology now includes contour position and separate old/modern quantity patterns; fixtures still required. Sources disagree on Dras knife, spindle, people and date plurals within the same book: retain both attestations, do not overwrite vocabulary entries using grammar examples.

Critical new finding: Strand distinguishes ordinary night rʹôt (rātra10700, a declension) from râʹt night/day measure (rā́tri10702, i declension); Liljegren róot/róota versus raát/reetí supports it. Four research links added to10700; unaccented rātra cannot independently prove barytonesis. Child bālá has OLD LONG ā (contrary to one earlier context summary); hair vā́la vs child bālá remains clean old-long bary/oxy comparison. Speech báaṣ vs lung baáṣ is NOT armpit; lung etymology doubtful as correctly stated below. All latest primary readings in PRIMARY_READINGS.md.

Next: finish Dras inflection quantitative adjudication; stronger cross-language input-defined classes and explicit residual ledger; Palula short-a unit sensitivity; Kundal paradigm appendix; source-aware parser fixtures; complete final exports and audit. Aim analysis freeze 12:00–12:15, only then final narrative report and appendices, deadline13:07 UTC. No final report drafted. No agents.

---

## 09:10 checkpoint (superseded)

**This update supersedes the older details below.** All1,686 first-pass families DONE, annotations through _37; revisions through _05. All590 selected Schmidt Brokskat / SSNP Ushojo unlinked records individually assessed;335 rawrecords have research links through _09. All269 printed Brokskat Table2 entries read (PDF28–50, printed258–280); primary readings in six JSONLfiles, manual alignments and14lexical splits. Analysis has25,505rawrecords and25,519tokens. All research families resolve; zero unresolved primary Brokskat alternatives after splits. Fullbuild needs rerun after latest changes.

**Critical corrections:** báaṣ speech vsbaáṣ is LUNG, not armpit; user informed. FullTurner11188Addenda explicitly rejects vákṣas andredirects9423a tentative *bhaṣma/*bhāṣma. Not strict cluster proof. Palula abhíiṇi cowife6534 explicitly Pashto bən loan in Turner, excluded. Schmidt person11221 wronglylinked→9827mánuṣa; fourdialectrecords corrected. These revisions are in _05 and recorddecisions_11/_12. Bro flesh moos, house gooṭ, seed bii, white šoo are UNMARKED in print. Hot 'taato is syllable stress, not Gilgit mora. Sheep ni'lo final; dream 'ṣaac̣ii initial despite finalii; birch 'ẓoẓi vsẓuru'zii differentformations. Lip 'yṭi noinitiall; name nũũ, smoke duu, mulberry ma'rõõṣ corrected. Few kʲii palatalization NOT stress. Spring/summer both 'uulo andba'zun, nooriginale/ucontrast. Walk zaa'zis finaldespitelongroot, genuinecounterexample. Sourceglyphqualityapproximateforcentralvowels; do notinferfinevowellaws.

**Next work:** quantitative model/tables still NOTBUILT; highestpriority independentinputclasses, source/dialectoutcomesets, residuals andsensitivity. Needmorecoverage KalkHultman475, Sauji573, Dras3021 andHKAT/LSI. Fixcontourpositionsinparser; addKalkexplicittonelessTable9 andphoneticTable12sourceobservations; Kundalwaterpàaníi overrideDBpā̌nī̂, weight-lightlutnot turmeric13992. CachedKundPDFis2004draftnotfinal2005(403). PendingUshboundaryfixes f_ka3fnoozlo5v6='kaṭe 'dae; f_xzhxdsi4zfe7g='horomos; f_hkx5jx4l23oou=bʌ'jala bo; f_l6b3j7lxbjo62=be; f_cfwlt56ptpaw2=ɛk 'šei; f_u3kekobdvhesa=a'ni 'šei; f_ozkuquiaj7pog='pili 'šei. Deg baṭ-káaṭo12010 actuallystone+woodcompound, exclude. Newfamiliesoutside1686optionalBrodeodar6531/Ushleg5082/widow10593, fullTurnerreadbutmetadata/dossiernotyetadded. Aimanalysisfreezearound12:00–12:15, thenwritefinalnarrativeandappendicesby13:07. NOFINALREPORTYET. Noagents.

---

## Older checkpoint (superseded where noted above)

The user authorized eight hours from 05:07 UTC, roughly until 13:07 UTC. Continue substantive research; do not write the final narrative report until analysis and data are frozen. No agents authorized or spawned. Do not alter the DB or website. Work only here. Primary skill already read: deep-research. Cluster/job-style local commands run via tmux session `shinaic-quant-0909` using approved `tmux` escalation; quick read-only inspections are direct.

## Completed first-pass review

- Every one of the original 512 acute-headword/core families is in `family_annotations.jsonl` through `_12.jsonl`.
- Fixing empty ancestral Original fields with an explicit Form fallback added family 13839 to the core group; it is in `_13.jsonl`. Core total now **513**.
- **All 463** non-unique-acute families with strong modern sources reviewed, annotations `_13` through `_23`.
- **40 of 710 legacy families** reviewed, in `_24`. Next packet: `review.py legacy 40 40`.
- Total **1,016 unique first-pass family annotations**. At the 976-family checkpoint, JSON validation and completeness checks passed with zero duplicates and all 513 core plus all 463 non-unique-acute families present.
- First-pass packets show limited sample tokens per language; this does NOT substitute for complete record-level disposition, second-pass primary-source resolution, or full quantitative testing. Those remain required.

## Files and provenance

- `build_corpus.py` freezes all 25,505 Shinaic records, 10,695 anchored and 14,810 unanchored; 1,686 broad families, 1,848 nearest formations. Seven living languages, Old Shina registered but zero records.
- Exact raw fields and graph paths in corpus.tsv; ancestral-records.tsv; per-source coverage; input hashes. The last rebuild added explicit `ancestor_original` and `ancestor_form_field` while using Form as display fallback only when Original is empty. No input database edits. Accepted rank-1 graph has no multiple-parent conflict.
- Broad family grouping is not the immediate input formation. Preserve all competing inputs, verbal stems and compounds separately.
- `annotation_revisions*.jsonl` override named fields in initial annotations in file/order sequence. Final annotated appendix MUST apply these revisions. Initial batch files deliberately retain an audit trail.
- `record_decisions*.jsonl` contain three verified reference corrections: koó 5274→2574; ram mʹinḍ 10301→10310.2; daughter-in-law bhôʹy 13801→11250. Last two verified in cached Strand primary HTML. No DB changes.
- Decisions `_04`–`_07` add: Strand strainer parʹûṇ 7483→7843 (Phal-p.html 38–39 explicit pari-pav-ana), Strand bhʹun- down 9820→9280 (Phal-b.html 319–320 explicit bundha), Degener máaz month 10114→10104 (same source ṣa-máazo six-monthly explicitly cites 10104; printed-page check still pending), and Liljegren traambú wasp component *vābha wrongly numbered 11531, actually11532. The wasp is compound tantra+vābha, not independent whole reflexes of each; Biori bhúmbur is a lexical replacement, not automatically that etymology.
- Decision `_05` corrects Turner9560 earthquake ghōmāl/ghūmāl/gahumāl glosses wrongly inherited as wheat, and excludes wheat ghōm/ghuma comparators from earthquake-reflex counts. Original cached Turner page545 explicitly proposes deformation of earthquake after wheat 'to avoid ill-luck?' (tentative source explanation, not newly proved taboo).
- Decision schemas differ across files: earlier original_family/research_family versus newer database_family_id/research_family_id/research_ancestor_id. Normalize all in the final merger. Do not ignore earlier keys.
- `PRIMARY_READINGS.md` logs new complete primary readings of Kalkoti 2013/2023 tone analyses, Palula declension history pp112–123 and checked Strand entries. Earlier source readings and findings are in conversation context and parent research folder notes.

## Critical methodological corrections

- `HKAT-xka` is a dialect tag attached to merged Kalkoti records, NOT the source. `kalkoti` source is Liljegren 2013; HKAT source is `liljegren-hindukush`. Early accidental source confusion is corrected by annotation revisions. Do not repeat it.
- Kalkoti 2013 Table12 supplies phonetic tone classes even for segment-only citations. 2013 wood šaàk is analyzed as late Low; 2023 šáak as early High. Similar falling contour, differing analysis; do not infer historical reversal from symbols. Hultman's unmarked tokens often mean uncertainty; explicitly toneless examples are a separate status.
- Old grave-marked āsyà, kāryà etc are meaningful svarita categories, not simply unaccented. The `unaccented` review label really means “not exactly one acute in broad headword.” Independently accented secondary formations can occur in that group.
- Current parser is preliminary. Unequal adjacent vowels, source-merged semicolon strings, compound boundaries, reconstructed fragments and different stress/mora systems require manual or source-aware handling. Dras and Brokskat stress must not be conflated with Gilgit mora notation. Fix and validate before final statistics.
- Backstrom survey stress marks ˈ are real syllable evidence; current parser misses them. Family700 alag/ alak has initial stress in multiple dialects and reduplicated forms. `review.py` now shows Backstrom as fallback when a language has no other records; original packets otherwise omit survey data, so second-pass source completeness is still required.
- Strong source citations often include bare verbs with no marked accent; recover actual paradigms from Degener raw transcription H|/C| blocks and Palula description fields. Do not count a dictionary lemma linked through a perfective as a direct reflex of the participle.

## Main leads requiring quantitative/primary second pass

1. Old long-root barytone→early versus oxytone→late in unextended nouns, with clear month/flesh and hair/child comparisons; separate later shortening.
2. Western new length: unaspirated short monosyllables often early (Biori sat, yab, sar, ǰar → Ashret sáat, yáab, sáar, ǰáar); h/aspirated closed-a nouns often late (hand, plough, donkey, animal hair, wolf). Disyllabic final-root lengthening late in spring, autumn, winter. Known exceptions need real explanation, especially mountain kháaṇ, grape dhráac̣, today aáǰ.
3. Extended nominal/adjective root-final accent with unaccented gender ending. Independent old accented -aka variants (nágnaka, khárvaka, báddhaka) strengthen analysis. -u does not automatically prove historical -aka; analogy and -aya convergence (heart) explicitly acknowledged by Liljegren. Final-oó and i-feminine classes distinct. dāraka→daár is a boundary case.
4. Gilgit newly long late roots after specific cluster reductions: taptá→taáto, álpa→aápo, áśru→aá~ṣo, vákṣas→baáṣ, aśakta→ašaáto. Test short controls and old-long controls; new naáwo, bow daáno residuals prevent a universal cluster-only claim.
5. Contraction-created late adjective roots mhoóru, lhoóku versus ordinary early long roots. Need independent VhV/aspiration/formation chronology.
6. Genuine source conflicts: oil, field, ghee, blue, ant, mother, root, pomegranate, iron (Degener čimár vs Buddruss čímar), postposition ǰhulí vs Strand initial, brother, foam/steam, etc. Verify actual primary entries and cell differences; never resolve by majority vote.
7. Compound/formation and graph errors create false exceptions: lō-múṭ deodar explicitly compound; multiple see/go/give/birth perfective-family links point to present dictionary lemmas; arrow šará and mountain rauléi can be lexical replacements; year saál Iranian; many one-letter or starred comparative fragments.
8. Propose new etymologies only with independent segmental/semantic support. Candidate problems include load bháaru from short bhára vs long bhārá, branch šóong vs śaṅkú/śā́khā, cowife abhíiṇi vs *dēvarajāni, and several botanical or expressive roots. Distinguish verified numerical correction from original etymological proposal.

## Additional findings from batches 17–24

- **Gilgit báaṣ speech (9479) versus baáṣ armpit (vákṣas family)** is a near-minimal early-old-long versus late-new-cluster-length comparison. Verify exact primary entries and paradigms.
- Late Shina h-related contractions before endings: **miíke urine (10337, mēha plus ka), maálo father (9935 mahallaka), loólyo red (11168 lōhila), šaŋaáli chain (12580 śr̥ṅkhala)**; compare short Astori šaṅáli. But early contractions **šóo good from šuwo (12532), báan cultivated field vāpana (11523), biléen medicine vilayana (11892)** rule out 'all contraction→late'.
- **Palula muúl price / Biori mul (10257 mūlya)** is a concrete late-new-length exception to an overbroad short-stage rule. Restrict/test vowel quality (short-a class) and independent ya-formation contraction, not all vowels.
- **Palula haáḍ bone / Biori haḍ (13952)** strengthens the closed-h-initial short-a→late class; collectives haṇḍúk/haḍúng are different formations. Do not import ásthi accent (Turner calls connection very doubtful).
- **Tail**: Lilj laméeṭi (11096 lūma) late ee vs Strand lamʹêṭi (10951 lamba) early ê. Strand primary Phal-l.html30–32 confirms underlying lamʹâṭ-i. Same lexeme with competing etymologies; real source mora conflict.
- **Unhusked rice**: Lilj šéeli early root vs Strand šêlʹi final short i. Primary Phal-sLam.html214–216 confirms underlying šâl-ʹi and -ʹa inflection. Need compare actual cells.
- **Fig9063**: broad headword pǹalgu is corrupt digital text, NOT usable svarita. Cached Turner page509 has pǹalgu but Addenda explicitly phalgu; relevant immediate branch2 *phālgu unaccented. Pal/Gil phaág late; Shina plural phăgí short root+finali.
- **Maize9879**: original Turner page568 really groups makai under markaka Ardea argala, so not parser typo. Strand Phal-jLam.html59–61 really derives unrelated ǰuwâʹr from same bird etymon. Must critically evaluate cereal-name transfer/borrowing; cannot accept as old-accent inheritance.
- **Schmidt person forms wrongly attached11221 ridgepole**: manúj̣o/manúuẓo/etc clearly mánuṣa9827 (Degener correct). Need inspect printed Schmidt table etym-reference location before record corrections. Table text around1852 in schmidt-kaul2008.
- **Degener baṭ-káaṭo compound wrongly under12010 vistīryatē**: raw line389 itself prints T12010, while separate stone11348 and wood3120 entries confirm actual components. Printed page must determine source versus transcription error; exclude from passive-spread reflexes.
- Unknown placeholder sets now/question/write are real DB families, not reconstructed phonological inputs. Palula cōṇṭō̂ and tapō̌s special comparative notation must be read source-aware. Possible contact tapos inquiry word needs external primary verification.

## Source access tips

`rg` ignores hidden/ignored cache directories by default: use `rg --hidden --no-ignore` for searches across `data/.cache/strand-legacy`; direct named files always worked. Palula j is **Phal-jLam.html**, š is **Phal-sLam.html**. Cached original Turner HTML is trusted local pickle `data/data/cdial/cdial.pickle`, list of page strings. Read with Python pickle and strip tags around target; pages545 earthquake,568 maize,509 fig verified this pass. Do not edit sources or ingest anything.

## Still required

Finish all family reviews, then source-based deep resolution and complete record annotation/disposition. Establish research-only cognate links for sparsely linked languages: Brokskat (8 families), Ushojo (2), newer Kalkoti, Sauji, Dras. Do not ignore them because the graph lacks edges. Manually validate segment/meaning candidates. Tabulate class outcomes by language/dialect/source with explicit denominators, uncertainty, conflicting readings and family-level deduplication. Strict rules must be independently conditioned and tested, not defined by the observed outcome. Build reproducible final tables and complete annotated appendices; only then compose a clean narrative report and validate artifacts.
