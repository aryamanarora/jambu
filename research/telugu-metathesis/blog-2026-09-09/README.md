# Telugu metathesis blog: approved six-claim edition

This is a presentation layer over the frozen 2026-09-09 study, plus an explicitly
descriptive exact paired-form screen. It does not mutate the database or frozen study.

Run `python3 prepare.py`, then `python3 build.py` from this directory (or use their
full paths). Only the Python standard library is required. `examples.py` contains
the sixty editorial selections, `post.md.in` the narrative. `build.py` matches each
displayed form to actual cited evidence, checks ten distinct primary families per
section, recomputes chart counts, and generates the Markdown, chart JSON and public
downloadable evidence. In this workspace submit those commands through tmux.

The source tables must be in the sibling `quantitative-2026-09-09` directory and
the prior `cluster-triage.tsv` in their parent. In the repository, generated website
files go to `src/lib/blog/posts`, `src/lib/blog/data`, and
`static/research/telugu-metathesis`. The archive recreates the research input tree;
to regenerate website outputs, place it beneath a jambu-static/research/telugu-metathesis
directory with src/lib/blog/posts available.

Counting notes:

- `chart-membership.tsv` gives one row per counted primary family within a chart
  view and row. The quantities are regrouped from formation-level annotations;
  a family can occur in more than one input class but cannot be counted twice
  inside the same row. The downloadable original formation tables explain those
  overlaps and distinguish retained controls from strictly testable outputs.
- Different language comparisons have different common-attestation denominators.
  Missing, unreviewed, borrowing, unresolved and other outcomes are explicit.
  Mixed families count once in their displayed class.
- The input classes are copied from comparative reconstruction annotations,
  not fitted to Telugu outcomes. The two discovery screens differ in ascertainment.
- `reduction-screen.json` contains 56 exact pairs from 41 of the 117 Telugu
  D-bearing families. This is evidence availability, not a loss frequency or an
  automatic causal adjudication. All original derivations and exception notes
  travel with the pairs in `reduction-audit.json`. Especially A-marked reduced
  forms, direct-assimilation alternatives and different formations remain qualified.
- The stop-cluster screen is separate from the 403-family apical review. Its
  source-supported input families include etyma not in the full comparative casebook.
- Each section has ten distinct primary families. Reappearance across sections
  illustrates a different claim and is never presented as an additional root.
- Displayed short labels sometimes omit a parenthetical paradigm from the
  original source form. The exact original string and stable ID remain exported.
- These data describe reviewed evidence, not random-sample language-wide rates.

`input-hashes.json` records the frozen table hashes read by the generator. The
full original study also contains a broader merger sensitivity analysis and
unreviewed-ID queues; the blog deliberately uses the primary partition consistently.
