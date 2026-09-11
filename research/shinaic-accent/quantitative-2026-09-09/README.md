# Shinaic accent research package

Start with the [narrative report](REPORT.html), also available as [Markdown](REPORT.md). It was written only after the analytical freeze on 9 September 2026. The working notes retain superseded hypotheses and counts for provenance; the report and final generated tables state the adjudicated results.

The package covers all seven living Shinaic languages represented in the frozen Jambu database: Shina, Palula, Sauji, Kalkoti, Kundal Shahi, Brokskat and Ushojo. Old Shina has no records. It contains 1,686 individually annotated anchored families, all 25,505 original records, and 25,593 analysis tokens after documented splits. Individual printed-source verification remains uneven and is explicitly labelled.

## Reading and inspecting the evidence

- [Complete family and record explorer](appendices/index.html): search a Turner family number, form, meaning or exact database record ID. Select the record view to include unlinked vocabulary; language and review filters are available. Open a dossier for the narrative analysis and all seven language panels.
- [Quantitative tables](appendices/tables.html): candidate sets, outcome ranges, sensitivity checks, exclusions, consolidated exception ledger and every family-level open question. Every table has a full TSV download.
- [Source register](appendices/sources.html): bibliographic information, notation conventions and the actual level of access.
- [Five etymological proposals](appendices/proposals.html): hypotheses kept separate from the frozen family registry.
- [Data dictionary](appendices/data-dictionary.md): fields, units, source readings, splits and research-only changes.

The HTML files embed their data and require no external libraries or network connection. The complete explorer is approximately 51 MB and may take a moment to open. Keep the directory structure intact so relative links and downloads continue to work. The report has print styles; the large appendices are intended for search and data export. Wide quantitative tables show the central fields first; expand “Complete row” for every remaining field.

## Complete data

`corpus.tsv` and the original graph/ancestor/reference TSVs are frozen inputs. `annotated-records.tsv` preserves every original field and adds research annotations. `analysis-tokens.tsv` retains source/lexeme splits. Equivalent JSONL exports are in `appendices/`; `family-dossiers.jsonl` contains all 1,686 revised dossiers. Raw database associations and research associations are separate fields. No database corrections have been installed.

The family JSONL inputs, later `annotation_revisions*`, lexical/source decisions, research links and reviewed paradigm tables are scholarly analytical inputs. Their comments and locators explain individual judgments. Generation scripts preserve retrieval and selection; reproduction does not independently repeat the human linguistic judgments.

## Rebuilding from the frozen analysis

The Python analysis uses the standard library. Run these commands from this directory, in order:

```sh
python3 reproduce.py
python3 source_register.py
python3 build_appendices.py
python3 build_reference_appendices.py
node render_report.mjs
python3 audit_presentation.py
python3 audit_analysis.py
```

`reproduce.py` runs the 22 required analytical invocations in dependency order, preserving per-program logs. It does not re-extract the live database or access the network. The source register and appendices are presentation builds. `render_report.mjs` uses the installed `marked` package; its import path points to the bundled Codex runtime on the research machine and must be adjusted if that dependency is elsewhere.

`audit_analysis.py` checks raw-field preservation, identifiers, annotation completeness, analytical inventories and local database hashes, then rebuilds the artifact manifest. Its database-drift check requires the original input directory named in `input-manifest.json`; the frozen analysis itself remains usable when copied elsewhere. `audit_presentation.py` checks local links, embedded appendix counts, table exports and central report denominators. Browser checks are recorded separately in `presentation-qa.json`.

`ANALYSIS_FREEZE.json` records the freeze before narrative composition. `integrity-audit.json`, `report-metrics.json`, `reproduction-audit.json` and `artifact-manifest.json` provide the final audit trail. Source PDFs and cached originals outside this directory were consulted where recorded; they are not silently represented as part of the portable package.

After both final audits, `python3 package_research.py` creates a ZIP archive beside this directory. It includes all files in the artifact manifest and verifies their hashes and archive CRCs. It refuses to overwrite an existing archive.
