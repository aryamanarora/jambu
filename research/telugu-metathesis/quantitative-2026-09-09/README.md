# Telugu metathesis: research deliverables and reproduction

This directory contains the bounded eight-hour investigation of 9 September 2026. Start with the [report](report.html), then use the searchable [complete annotated casebook](casebook.html) to inspect the individual etymologies. The [Markdown report](report.md) and [Markdown casebook](casebook.md) are portable text versions. The source database and public site were not edited.

The analysis covers **409 DEDR entries**, grouped into **403 primary root families**, with a **365-family sensitivity partition**. All **116 previously identified Telugu initial-cluster candidates** are reviewed. Coverage is substantial but not exhaustive: **5,139 of 5,548 DEDR groups** remain outside the main casebook, including **2,326 of 2,701 Telugu-bearing DEDR groups**. Auxiliary reviews are separate and may overlap the casebook. The frozen extraction contains 162,451 research-selected records; selection does not imply verified cognacy or metathesis.

## Read the results

| File | Content |
| --- | --- |
| [report.html](report.html), [report.md](report.md) | Final narrative, written after the analysis freeze; conditioning, direction, chronology, morphology, family distribution and unresolved problems. |
| [casebook.html](casebook.html), [casebook.md](casebook.md) | All 409 entry-level analyses: reconstructions, classes, comparative direction, derivations, outcomes, confidence, exception notes, cited source forms and IDs. The HTML search matches the complete entry text. |
| [generated-tables.md](generated-tables.md) | Readable all-language, Telugu-domain, quantity, sensitivity and pairwise tables. |
| [SOURCE_ACCESS.md](SOURCE_ACCESS.md) | Bibliography, exact pages/sections used, access limits and distinctions between originals and secondary citations. |
| [source-index.md](source-index.md) | Database reference metadata and research citation strings attached to the cited evidence. Metadata is preserved rather than silently repaired. |
| [chronology-notes.md](chronology-notes.md), [historical-evidence.tsv](historical-evidence.tsv) | Inscription readings, dating qualifications, source locators and chronological inferences. |
| [conditioning.png](conditioning.png), [conditioning.svg](conditioning.svg) | Static scientific figure generated from the count tables. |

## Structured appendices and units

| File | Unit and purpose |
| --- | --- |
| [etymon-annotations.tsv](etymon-annotations.tsv) | One row per reviewed dictionary entry. |
| [language-outcomes.tsv](language-outcomes.tsv) | Entry × language, preserving missing and unreviewed statuses. |
| [cited-evidence.tsv](cited-evidence.tsv) | 9,823 evidence links: 9,742 distinct cited form IDs and 81 source-only research observations. Original word strings, source locators, labels and token outcomes are retained. |
| [complete-reviewed-records.tsv](complete-reviewed-records.tsv) | All 17,558 raw records in reviewed groups, including explicitly marked records not individually adjudicated. |
| [family-partitions.tsv](family-partitions.tsv), [family-merge-sensitivity-proposals.tsv](family-merge-sensitivity-proposals.tsv) | Primary family assignments and reasons for possible additional mergers. Related derivatives and duplicate records do not become independent roots. |
| [family-class-counts.tsv](family-class-counts.tsv) | Counts by partition, input axis/class and language. Contains disjoint outcome states, overlapping flags, explicit D/R and attested-reviewed denominators, missingness and unreviewed counts. |
| [family-count-membership.tsv](family-count-membership.tsv) | Every family's membership and contribution to each count. This is the direct audit trail for table cells. |
| [formation-tests.tsv](formation-tests.tsv), [formation-class-counts.tsv](formation-class-counts.tsv), [formation-count-membership.tsv](formation-count-membership.tsv) | Formation-specific quantity predictions, observed outputs and denominator membership. All 117 Telugu D-bearing primary families have an audit row; not every row is strictly testable. |
| [pairwise-language-counts.tsv](pairwise-language-counts.tsv), [pairwise-language-membership.tsv](pairwise-language-membership.tsv) | Comparisons restricted to families informative in both languages. |
| [stop-cluster-annotations.tsv](stop-cluster-annotations.tsv) | Complete adjudication of 152 literal-screen records in 123 groups; kept separate from initial-apical counts. |
| [kondh-source-paradigms.tsv](kondh-source-paradigms.tsv) | Independent source paradigms and controls for suffixal stop-order alternations. |
| [lowering-source-audit.tsv](lowering-source-audit.tsv) | Item-by-item test of Krishnamurti's 1980 Kui–Kuvi lowering examples and controls. |
| [kunha-published-pair-audit.tsv](kunha-published-pair-audit.tsv) | All 30 published Kurux–Kunha pairs; no assumption that modern Kurux is the unchanged ancestor. |
| [other-process-observations.tsv](other-process-observations.tsv) | Different Dravidian reordering, aphaeresis and possible insertion processes. |
| [unlinked-candidate-annotations.tsv](unlinked-candidate-annotations.tsv) | Eighteen assessed unlinked database records; proposed associations, uncertainty and follow-up needs. These are not accepted database edits. |
| [coverage-results.json](coverage-results.json), [remaining-dedr-groups.tsv](remaining-dedr-groups.tsv), [pending-input-screen.tsv](pending-input-screen.tsv) | Exact reviewed and pending scope. The inclusive input screen is based on modern full forms and is not itself a reconstructed-input annotation. |

Outcome codes: **D**, supported displacement-family development; **R**, retention of the target initial order; **O**, other development; **A**, uncertain analysis; **B**, borrowing. Multiple flags can coexist in a family. **M** is an annotation shorthand for mixed evidence, resolved into token flags for counting. D does not necessarily distinguish literal exchange from assimilation plus vowel loss. An R word can have other changes elsewhere. Missing attestations and attested-but-unreviewed cells supply no negative votes.

The principal language aggregation combines Old Telugu with Telugu, Old Malayalam with Malayalam, and `pampa` with Kannada. Original labels remain in evidence rows. The 43 resulting attestation groups are not 43 independent language samples; `Kuwi` is the database ID for Kuvi. Reconstructed/generic language nodes are excluded from attested outcome counts.

Input classes use comparative C1, V1 quantity/quality, C2 identity and structure, V2, morphological boundaries and grammatical category. Unknown information remains unknown. The review was targeted and iterative, **not blinded, preregistered or randomly sampled**. Independence here means that a proposed input property has comparative support apart from the outcome being explained. The report states the resulting ascertainment limits. Family, formation, pairwise and source-illustration denominators must not be added together.

## Reproduce the extraction and analysis

The core pipeline uses **Python 3.10 or later and the standard library**. Run from this directory, or pass absolute script paths. The scripts resolve their own directory. They read the frozen research extraction and write only research outputs.

```sh
python3 build_corpus.py --verify-only
python3 run_analysis.py
python3 render_appendices.py
python3 validate_final.py
python3 write_report.py
python3 check_report.py
```

`build_corpus.py --verify-only` hashes the ten current sibling `data/cldf` files and compares them with [input-manifest.json](input-manifest.json), without changing the extraction. With matching inputs, `python3 build_corpus.py` regenerates the frozen corpus and inventories. It refuses to overwrite this investigation from changed inputs unless explicitly given `--allow-new-inputs`; use a separate investigation copy for that operation. `--cldf /path/to/cldf` selects another location. The saved `corpus.tsv` and `groups.jsonl` allow recounting even if the live database has changed. Raw lexical records remain source data, not instructions.

The manually curated analytical source files are `cases_*.py`, `annotations.py`, `cluster_case_helpers.py`, `source_corrections.py`, `supplemental_evidence.py`, `other_processes.py`, `formation_tests.py`, the merger list in `quantify_families.py`, `kondh_paradigms.py`, `historical_evidence.py`, `kunha_comparisons.py`, `unlinked_candidates.py`, and the explicit audit lists in the auxiliary scripts. They are the editable scholarly judgments, not automatically inferred labels. `run_analysis.py` executes the ordered export, class-count, formation, queue, auxiliary and coverage scripts and stops on failure. `report-template.md` contains the final narrative; `write_report.py` inserts tables from generated outputs and applies spacing to citation labels.

Files named `amend_*.py` and `finalize_claims.py` preserve one-off annotation-editing history. **Do not run them as regeneration steps.** Working `panel-*.log`, `compact-*.log` and retrieval logs are research history, not final results. [working-notes.md](working-notes.md), [PROTOCOL.md](PROTOCOL.md), [quantification-design-notes.md](quantification-design-notes.md), [literature-claims.json](literature-claims.json), and [analysis-freeze.json](analysis-freeze.json) document the investigation and its revisions.

## Optional HTML, figure and browser rendering

The saved HTML and figure are ready to use. To regenerate them in a Python environment with the optional dependencies:

```sh
python3 -m pip install -r requirements-render.txt
python3 plot_results.py
python3 render_report_html.py
```

The casebook renderer itself needs only the standard library. [qa_artifacts.cjs](qa_artifacts.cjs) uses Playwright and a local Chrome installation to check the HTML, search, entry expansion, figure loading and JavaScript errors. Set `PLAYWRIGHT_MODULE` to a local Playwright package path if the bundled Codex runtime path in the script is unavailable, then run `node qa_artifacts.cjs`. Screenshots are saved as `report-preview.png`, `report-figure-preview.png` and `casebook-preview.png`.

`python3 finalize_artifacts.py` combines the optional figure/HTML rendering with the appendix and statistical checks. After running the browser check, use `python3 build_manifest.py` to refresh the final hashes and `python3 verify_manifest.py` to verify them without changing files. Working `.log` files and the manifest itself are excluded from its hash list.

## Validation and provenance

[validation.json](validation.json) independently recounts **19,823 class-table rows and 429,312 family-membership rows**, checks **17 formation-table rows**, **5,796 pairwise comparison groups**, all **409 entry anchors**, evidence uniqueness and complete Telugu D-family formation coverage. [report-validation.json](report-validation.json) checks local report links and records the statistical provenance index in [report-statistics.tsv](report-statistics.tsv). [browser-qa.json](browser-qa.json) records browser behavior. These checks validate arithmetic, linkage and presentation; they cannot certify a historical reconstruction.

The repository's `npm run check` completed with **0 errors and 7 warnings in 5 files**; see [site-check.log](site-check.log). No application implementation was changed for this research. [deliverable-manifest.json](deliverable-manifest.json) records final file hashes and validation results. Downloaded scholarly originals and extraction caches remain in the workspace's research cache; [SOURCE_ACCESS.md](SOURCE_ACCESS.md) records access locations and limitations. Only brief quotations and analytical annotations are incorporated into the deliverables.
