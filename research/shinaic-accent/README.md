# Shinaic accent investigation

Started 2026-09-08, 05:30 UTC. User budget: eight hours (through 13:30 UTC).
Requested outcome: a Jambu blog post explaining the development of Palula accent,
with a minimal defensible chronology of sound changes, explicit counterevidence,
and justified new etymological proposals where useful.

## Scope and method

- Read the published phonological descriptions and comparative studies first.
- Analyze existing Jambu lexical data without modifying source ingestions.
- Distinguish Ashret (Southern Palula) from Biori (Northern Palula).
- Preserve source notation; distinguish vocalic length, accent locus, and aspiration.
- Distinguish source etymologies, new proposals, and illustrative reconstructions.
- Evaluate inherited accent, accent retraction after apocope, contraction, vowel
  lengthening/raising, aspiration movement, and morphological analogy independently.
- Count a word family once when evaluating evidence; do not treat inflections,
  dialect variants, or duplicated citations as independent confirmations.
- Keep counterexamples in the analysis instead of creating a rule for each word.

## Initial evidence

- Liljegren & Haider 2009 distinguish lexical mora accent from aspiration-induced
  pitch perturbation. Both first- and second-mora accent occur with aspiration.
- Liljegren 2016 §5.6 links mobile noun accent to lost final accented *-a, but
  explicitly gives counterexamples (including 'village'). This is a hypothesis to
  test across the lexicon, not a universal rule to assume.
- Jambu already contains the complete Dictionaria Palula dictionary ingestion,
  including unetymologized words, source proto-forms, variants, and inflection data.

## Sources to examine

1. Liljegren 2016. *A grammar of Palula*. https://doi.org/10.17169/langsci.b82.85
   Open PDF: https://langsci-press.org/catalog/view/82/85/399-1 (CC BY 4.0).
2. Liljegren 2009. *The Dangari Tongue of Choke and Machoke*.
   https://doi.org/10.5617/ao.5341
3. Liljegren & Haider 2009. *Palula*. https://doi.org/10.1017/S0025100309990193
4. Liljegren 2019. *Palula dictionary*, Dictionaria 3, version 1.2.
   https://doi.org/10.5281/zenodo.5526477 (CC BY 4.0).
5. Liljegren 2013. *Notes on Kalkoti: A Shina Language with Strong Kohistani Influences*.
   https://journals.dartmouth.edu/journals/xmlpage/1/article/423?htmlOnce=yes
6. Morgenstierne 1941. *Notes on Phalura* (original accent evidence to check).
7. Köhnlein. *Mora stress in Shina as Contrastive Foot Structure*.
   https://ojs.ub.uni-konstanz.de/jsal/index.php/fasal/article/view/252/144

## Delivery gates

- [x] Source-page checks for the central correspondences and disputed diacritics; the public appendix explicitly limits this to central examples, not every screening row.
- [x] Reproducible lexical evidence tables with explicit inclusion/exclusion criteria; fresh archive replay passed all six scripts and seven exact table comparisons.
- [x] Competing analyses evaluated; residual problems, unavailable works, and uneven language coverage explicitly stated.
- [x] Finished post and correctly labeled agent authorship in blog metadata.
- [x] All 17 semantic Jambu records resolve against the build database; its SHA-256 matches release db-v29 exactly.
- [x] Blog tests 4/4; Svelte check 0 errors, 7 existing warnings; full production build; browser inspection and static-only 404 fallback pass.

## Workspace context

The site already had uncommitted blog infrastructure and two other essays when
this task began. Preserve that work; restrict task edits to the new post, its
metadata/changelog entry, and this research directory.

## Scope expanded at user request, 06:07 UTC

Cover the full Shinaic group: Shina (including Kohistani, Gilgiti, Gurezi, Astori, Drasi and other documented dialects), Palula, Sawi/Sauji, Kalkoti, Kundal Shahi, Ushojo, and Brokskat. Compare all available varieties without claiming equal documentation. Keep Indus Kohistani distinct from Kohistani Shina. Brokpa/Brokkat Tibetan languages are not Brokskat. Original eight-hour window remains unchanged.

New coverage gates: primary-source accent assessment for every language; language-specific notation; shared innovations distinguished from parallel changes; comparative cognate table; explicit gaps where recordings or accent-marked paradigms are unavailable.

## Final validation

The publication is being built in `/tmp/jambu-shinaic-publication` from HEAD `8f61af6275e6956b5611ba01f06520b6ae3fe850`, with only the Shinaic essay, its evidence, and necessary blog infrastructure. Other uncommitted essays and entry-display changes remain in the shared workspace. No lexical source or accepted etymology was changed.

Latest evidence archive SHA-256: `49f97972f92c3b3f8ea98d0b918acbafd2ad252433c8113290527a8aa8e83998`. It contains 187 Palula nominal records, 139 Shina families, 692 survey rows, 62 evidence-ledger rows and 32 rule/mechanism records. The nine-row compact account groups branch-specific changes; the ledger also includes inheritance, morphological mechanisms, provisional proposals and gaps, so 32 is not a count of sound laws.

The full build emitted 33,169 entry pages, 3,261 concept pages, 1,928 language pages and 521 reference pages, plus the essay and index. Production HTML contains the complete article and 17 resolved semantic records. All internal anchors resolve. The downloaded archive matches the replay-verified hash. A static-only server returned `404.html` with HTTP 404 for non-prerendered `f_ma6j5px33fee6`; the browser loaded its Palula headword, source, ancestry and alignment successfully. Default-width browser inspection showed no page overflow. The viewport override API did not actually resize the in-app browser, so no phone-viewport result is claimed. Publication is the remaining delivery step.
