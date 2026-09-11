# Telugu metathesis investigation

The expanded 9 September investigation is in
[quantitative-2026-09-09](quantitative-2026-09-09/README.md):
[final report](quantitative-2026-09-09/report.html),
[409-entry annotated casebook](quantitative-2026-09-09/casebook.html), and
reproducible family-level counts with explicit coverage and uncertainty.
The material described below is the earlier 8 September investigation.

Research date: 8 September 2026. Started 05:43 UTC with an eight-hour allowance.
The blog post and its generated public supplement were removed at the user's
request on 9 September 2026. The analysis code, evidence, and research notes remain here.
It analyzes existing evidence and published hypotheses. No lexical-source
installation, reconstruction replacement, or ancestry-edge mutation was performed.

## Deliverables

- `inventory.py`: read-only CLDF inventory, candidate searches, and legacy-level flags.
- `inspect_sets.py`: comparative panels for specified DEDR groups.
- `triage_panels.py`: numbered panels for reviewing cluster candidates.
- `casebook.md`: six detailed derivations, additional Telugu cases, unchanged
  controls, other Dravidian patterns, and borrowing diagnostics.
- `vowel-lowering-audit.md`: all 18 numbered positive examples in Krishnamurti
  1980, seven numbered controls, and one additional high-formative comparison.
  Published labels, disputed cognacy, source dependence, and quantity discrepancies
  are evaluated separately; the counts are not validated sound-law success rates.
- `cluster-triage.tsv`: individual assessments of all 116 initial-cluster groups.
- `reconstruction-audit.tsv`: 13 documentary or analytical audit items, with
  proposed actions and evidential status. These are not 13 implemented corrections.
- `bibliography.md`: editions, pages, links, and explicit access limitations.
- `source-notes.md`: working reading log, including later corrections and refinements.
- `inventory-summary.json`: input SHA-256 checksums and descriptive counts.
- `candidate-records.tsv`, `legacy-level-flags.tsv`: machine-generated search aids.

`build-supplement.mjs` is retained as the former presentation generator; it is
not needed to run the analysis. Running it would recreate the removed public
supplement, including its obsolete blog link. Reference books and page images
remain working sources under `../../../tmp/telugu-metathesis`. The large local
`sets.json` cache is ignored.

## Reproduce

From `jambu-static`, with the sibling `data` repository present:

```sh
python3 research/telugu-metathesis/inventory.py
python3 research/telugu-metathesis/inspect_sets.py d1787 d5409 --ids
python3 research/telugu-metathesis/triage_panels.py 0 20
```

The first command reads CLDF and legacy source tables and regenerates only the
inventory, candidate files, and local cache. Compare input checksums before
expecting identical counts. It does not regenerate the manually reviewed
casebook or triage decisions. `inspect_sets.py d1787 d5409` and `triage_panels.py`
are inspection helpers, not automatic etymology classifiers.

Snapshot counts: 677,797 forms and 357,003 edges; 2,701 Telugu-bearing DEDR groups
with 8,403 Telugu records. The candidate searches flag 2,311 records across 881
groups; 247 cluster-bearing records fall in the 116 manually triaged groups.
The flags overlap. There is no claimed success rate for all eligible Telugu
formations, and the 1,811 uncontracted candidates were not all manually analyzed.

## Historical validation (before removal)

The checks below and `validation.json` record the original 8 September delivery;
they refer in part to the subsequently removed publication artifacts.

- `node --test tests/blog.test.mjs`: four existing renderer/link tests passed.
- `npm run check`: zero errors; seven existing warnings in unrelated components.
- Production build passed with the deployed `/jambu` base path and the iteration
  command below. Although seeded with `PRERENDER_LIMIT=50`, the crawler produced
  23,125 HTML pages. This is not represented as an unrestricted-seed build.
- The final essay was reloaded in the local browser; its typography, reconstruction
  stars, evidence links, and jump to the minimal account were inspected.
- The static supplement builder asserts the 116-group count and TSV column
  consistency. Final link and browser checks are recorded in `validation.json`.

```sh
JAMBU_DB=.dbwork/jambu.db PRERENDER_LIMIT=50 BASE_PATH=/jambu SITE_URL=https://aryamanarora.github.io npm run build
```

This work has not pushed or deployed the site. Database repairs remain reviewable
proposals, with source uncertainty and competing analyses preserved.
