# Evidence for “How the Shinaic languages got their accents”

Research by Codex, an AI agent, 8 September 2026. These files accompany the Jambu
essay. They preserve source readings and make the scope of the investigation
inspectable. They are not an accepted etymological database or an exhaustive
historical phonology. Read the primary sources before relying on a disputed form.

## Files and selection

| File | What it contains | What the count does not establish |
| --- | --- | --- |
| `palula-nominal-screen.tsv` | 187 noun, adjective and numeral entries, with 183 distinct Turner links; every selected entry has an explicit first-pass note | Not all inherited Palula nouns: selection requires a vocalic acute in the first token of the supplied proto-form, as well as a Turner link and the relevant modern tag |
| `palula-closed-aa-candidates.tsv` | 227 single-word noun/adjective citations with accented aa followed by a final consonant sequence | Includes loans, old long vowels and uncertain histories; “matches_prediction” is only a modern descriptive comparison |
| `palula-short-a-test.tsv` | The 36 candidates whose supplied morphemic form literally matches the citation with aa shortened to a | A modern alternation does not prove historical short a; 35 predicted contours and one mismatch are not a historical success rate |
| `palula-aa-imperatives.tsv` | 34 explicitly supplied imperative forms containing accented aa, all early-accented | Does not cover imperatives which were not explicitly supplied, or establish the original date of the paradigm |
| `shina-family-screen.tsv` | 139 families with a vocalic acute in the Turner headword, comparing the source's named Shina varieties and available Palula comparanda | An entry number can contain several formations; multiple varieties are not independent proofs of a rule |
| `shina-survey-selected.tsv` | 692 source rows for 23 selected concepts in 27 survey localities | Phonetic field notation is not a uniform phonemic analysis; shared meaning does not assert cognacy |
| `shina-survey-matrix.tsv` | The same survey forms arranged by concept and locality | An unmarked form is not evidence that the locality lacked accent |
| `nasal-backing-screen.tsv` | Selected support and counterevidence for Shina a:o in nasal environments | A restricted correspondence, not an exceptionless reconstruction |
| `source-readings.tsv` | Six discrepancies or qualifications checked against printed sources | Research corrections only; no source ingestion or accepted etymology was changed |
| `evidence-ledger.tsv` | Primary-source locators, verification scope, support and opposition for the central claims | Page checks of central examples do not imply every word in every extracted table was page-checked |
| `rule-ledger.tsv` | Explicit domains, inputs, outputs, conditioning, ordering and remaining problems | Related mechanisms in different languages are not automatically one shared innovation |
| `manifest.json` | Exact input and script hashes, source-repository revision, and descriptive counts | A repository revision alone may not identify local input versions; the file hashes are the comparison standard |
| `shinaic-accent-evidence.zip` | These files and the six analysis scripts under `reproduce/` | Does not include copyrighted page images, source PDFs, or the full Jambu database |

The complete Palula inventory contains 2,700 main dictionary entries. Variant
cross-references and separately generated Turner copies are excluded from that
count, not silently treated as independent confirmations. Of the main entries,
511 carry Turner links and 1,087 contain an etymology or origin statement. A first
proto token is a search aid; it is not necessarily the immediate ancestor. The
acute-based screens exclude some accented source traditions, including grave
marks, and do not resolve every unusual source spelling or reconstructed formation. Sanskrit ai/au are treated as single nuclei even when the acute falls on the second letter; modern Palula doubled vowels remain separate mora tokens.

The six-variety Shina source has 2,050 rows. Its 711 linked rows include 18 links
outside numeric Turner entries. The 139-family table is a restricted subset of
219 linked families. Brokskat uses stress notation in the original paper; several
digital accent-like readings require the qualifications in `source-readings.tsv`.

## Notation and assessment codes

Unicode is UTF-8. The scripts normalize working form strings to NFC and preserve
the original etymology/inflection statements. In the Liljegren-style transcription,
`áa` is early and `aá` late. That convention must not be applied mechanically to
Sawi spelling, Brokskat stress marks, or unmarked Kalkoti glossary items. Jambu's
display may convert an original source's marks into its own presentation; the
original/source fields and the paper remain necessary for exact comparison.

Palula nominal codes can overlap: **C** compatible with retention or a regular
vowel history; **A** compatible with apocope/mobile inflection; **F** formation
must be controlled; **K** contraction or consonant/syllable history needs work;
**P** residual accent or paradigm problem; **Q** quantity or aspiration chronology
uncertain; **S** source reading or ancestral input uncertain. “Compatible” does
not mean proved, and another code in the same row can flag an unresolved issue.

The Shina family screen has a separate code set: **R** retention-compatible;
**A** apocope-compatible; **U** short citation uninformative about mora position;
**M** formation/paradigm must be controlled; **D** dialect divergence;
**S** source conflict; **X** residual against copying the cited old accent.
Do not combine the two code systems into a numerical score.

## Reproduction

Obtain the [Jambu data repository](https://github.com/moli-mandala/data), including
its existing CLDF exports, and compare its inputs with `manifest.json`. Use Python
3 with only the standard library. Set `JAMBU_DATA` to the repository's absolute
path, then run the scripts in this order from the extracted `reproduce` folder:

```sh
export JAMBU_DATA=/absolute/path/to/data
python3 inventory.py
python3 audit_palula.py
python3 compare_shina.py
python3 annotate_families.py
python3 annotate_palula_nominals.py
python3 survey_comparison.py
```

Outputs are written beside the scripts. The nominal and family assessments are
explicit manual annotations embedded in the two `annotate` scripts; reproduction
recreates the notes and does not independently validate their interpretation.
The public Shina table omits full Turner entry paragraphs, which are unnecessary
for reading the form comparisons. The other ledgers are manually curated source
checks, not automatically inferred results. Stable Jambu IDs are taken from
existing source-key mappings or unambiguous matching cited records; missing IDs
are left blank instead of guessed.

## Attribution

Palula forms, inflections and original etymological suggestions come from Henrik
Liljegren's [Palula dictionary](https://dictionaria.clld.org/contributions/palula)
(Dictionaria 3, 2019; [version 1.2](https://doi.org/10.5281/zenodo.5526477), CC BY
4.0). The analysis also draws on his [2016 grammar](https://doi.org/10.17169/langsci.b82.85)
and [2009 comparative study](https://doi.org/10.5617/ao.5341). The Shina comparison
is Jambu's existing transcription of Ruth Laila Schmidt and Vijay Kumar Kaul's
[2008 comparative study](https://www.wisdomlib.org/uploads/journals/acta-orie/vol-69-2008/7372-6759-23258.pdf).
The survey data derive from Peter C. Backstrom and Carla F. Radloff's *Languages
of Northern Areas* (1992), via the existing [Lexibank transcription](https://github.com/lexibank/backstromnorthernpakistan).
Old Indo-Aryan family identifiers refer to R. L. Turner's *A comparative dictionary
of the Indo-Aryan languages*. Strand’s independent Palula description and competing loan account are assessed separately from the Liljegren dictionary screen. Other language-specific sources and page locators
are listed in `evidence-ledger.tsv` and cited alongside the claims in the essay.

The historical assessments, proposed alternatives and residual classifications
in this appendix are the present investigation's work. They should not be
attributed to the dictionary authors unless the essay explicitly identifies a
published proposal. No new proposal here was installed as a dictionary fact.
