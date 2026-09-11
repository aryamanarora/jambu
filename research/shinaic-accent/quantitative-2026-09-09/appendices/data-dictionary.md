# Data dictionary and appendix guide

The appendices contain all 25,505 frozen Shinaic raw records, all 25,593 analysis tokens after 88 additional source/lexeme branches, and all 1,686 original anchored family dossiers. Old Shina has zero records. New-family proposals remain supplementary. Raw-record and branch-level research associations can differ: 13,270 raw records and 13,272 analysis tokens lack a research family.

- `../corpus.tsv`: every original database field, language/source tags, nearest non-Shinaic ancestor, broad family and full accepted ancestry path. This frozen input is never silently corrected.
- `../annotated-records.tsv` / `complete-records.jsonl`: the same 25,505 IDs with research-only decisions, source readings, parser features, review level and annotations. Every raw field remains available.
- `../analysis-tokens.tsv` / `analysis-tokens.jsonl`: all raw records, with 88 additional branches where one source record merged distinct words or independently transcribed sources. `analysis_token_id` adds `#1`, `#2` where necessary; `id` remains the original database ID.
- `family-dossiers.jsonl`: 1,686 dossiers, applying every later annotation revision, with all seven language panels, every linked record ID, source outcomes and ancestor metadata. Original raw members reassigned during research remain visible in the browser dossier.
- `../historical-observations.tsv`: every research-linked token, its immediate input or explicitly labelled broad-head proxy, independently calculated input features, outcome, exclusions and family analysis.
- `../record-edges.tsv`, `../ancestral-records.tsv`, `../families.tsv`, `../languages.tsv`, `../references.tsv`: frozen graph, ancestral and bibliographic evidence.
- `../supplementary-ancestors.tsv`: the existing database subentry 10310-2, needed by a documented reference correction but absent from the original ancestry walk. Its extraction was permitted only after verifying that the live forms file still matched the starting hash; `../supplementary-ancestor-provenance.json` records that check. The original ancestral extract is unchanged.
- `tables.html`: all quantitative model tables and their full downloadable TSVs. `sources.html` records notation and the actual level of source access. `proposals.html` preserves new etymological hypotheses separately.

## Fields that must not be conflated

`family_id` and `ancestor_id` are original database associations. `research_family_id` and `research_ancestor_id` apply the explicitly recorded research decisions. A broad family can contain several distinct historical formations and lexical senses. An empty research ancestor means the headword is a proxy, not a verified immediate input.

`original` is the raw citation; `reading_form` is the source-aware reading used for analysis. `research_original`, when present, records a documented correction or split. `record_decisions`, `formation_decisions`, `source_observations`, `primary_table_readings`, `additional_record_annotations` and their locator fields preserve the reasons and audit trail. No lexical database was changed.

`individual_review` distinguishes a family-context first pass, an unlinked inventory entry, a manual lexical/source-group assessment, a research link, a structural/paradigm review and an explicit primary reading. These levels are not interchangeable. In particular, the complete appendix does not claim that every raw citation received an independent printed-page check.

`strict_exclusion` identifies record-level obstacles to strict historical predictions. Model-specific exclusions additionally include multiword expressions, fragments, uncertain vowel-sequence syllabification, provisional etymologies and unmatched grammatical formations. Excluded records are retained and searchable.

## Accent and tone labels

- E/L: first/second-mora accent only in explicitly compatible Gilgit/Shina, Palula or Strand notation.
- S: one marked short vowel; its syllable location is recorded separately.
- H1/H2/Hshort: Kalkoti High on first mora, second mora or a short vowel, in the 2023 analysis. Low can coexist with High. `0-explicit` is reserved for explicitly analyzed toneless examples.
- P-high-level, P-low-level, P-high-rising, P-low-rising, P-high-falling: 2013 primary phonetic contour observations. These are not automatically identical to the 2023 phonological categories.
- F/R/LR: a source-specific falling, rising or low-rising contour; consult the notation field. Kundal and survey conventions are not assumed identical to Shina E/L.
- stress-marked and its position: syllable stress in Brokskat, Dras or survey notation. It is not relabelled E/L.
- unmarked: the source citation does not supply usable accent information. It does not mean toneless.
- `@-1`, `@-2`, etc.: final, penultimate, etc., where the source notation and conservative syllabification permit a location. `position-unresolved` retains a mark while withholding an uncertain syllable analysis.

`modern_nuclei` is a conservative orthographic nucleus count. Unequal or interrupted vowel sequences remain flagged. Dras repeated vowels may be distinct nuclei; colon marks length. Sanskrit grave/svarita inputs are not silently treated as historically accentless merely because the acute counter is zero.

## Units and reproducibility

Raw citations, split analysis tokens, unique form/gloss types, morphological cells, paradigms, lexemes and broad etymological families are different units. Family tables use outcome sets rather than majority voting. Multiple outcomes can contribute overlapping counts; table notes state this explicitly. Eight teen numerals or several forms of one suffix are not eight independent historical changes.

In the two Palula i-declension tests, the operational lexeme grouping uses the dictionary gloss together with the full inflected form, merging citation variants. The happiness variants occur in both structural subsets and share one inflected form: 66 plus 30 therefore yields 95 combined lexemes, not 96. The complete candidate tables preserve each source record, citation and inflection.

`../reproduce.py` rebuilds quantitative outputs from the frozen corpus and reviewed analytical inputs. It does not re-extract a changed live database. JSONL review/decision files and reviewed paradigm tables are human analytical inputs; their generation scripts preserve retrieval and selection procedures. `../input-manifest.json` records the original database hashes; `../integrity-audit.json` and `../artifact-manifest.json` document final checks and output hashes.
