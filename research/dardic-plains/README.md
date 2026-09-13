# Dardic / Plains blog evidence

The post lives at `src/lib/blog/posts/dardic-plains-isoglosses.md` and is prepared
for the local `/blogs/dardic-plains-isoglosses` route. Nothing is deployed by this
workflow. It includes five interactive charts using the existing blog chart component,
four optional exportable figures, and expandable tables naming every resolved
family. Weighted charts explicitly opt into fractional votes; older research
charts retain their integer-count validation.

Every viewer now includes a synchronized Leaflet map. Round outlines identify
Dardic units and square outlines Plains units; circular pie fills show the same
family weights as the bars, with unknowns shown in grey even in linked-only views.
Markers are 10 px, or 16 px when selected. The group filter affects the map only
and zooms the Dardic view; language selection exposes representative records and
unresolved/excluded-loan counts. Missing coordinates remain in the selector and
bar totals. Map coordinates are frozen separately with `--refresh-coordinates`;
their provenance currently matches the original lexical snapshot exactly.

“Other resolved families” is clickable in the legend and bars. Its inline table
lists every constituent etymon, group votes, percentages and attesting languages.
The generator asserts that these rows sum exactly to the corresponding segment.

`static/research/dardic-plains/` contains the frozen nine-concept evidence,
analysis settings/input hashes, graph reader and analysis-script snapshots,
reconciled family distributions and language memberships, metric comparison,
RIVER sensitivity analysis, and SVG/PNG figures.

Regenerate from the frozen evidence with Python plus Matplotlib:

```sh
uv run --with matplotlib python research/dardic-plains/build.py --family-level head
uv run --with matplotlib python research/dardic-plains/build.py --family-level entry
python3 research/dardic-plains/extensions.py
```

Only use `--refresh-snapshot` intentionally: it replaces the frozen evidence
from the sibling data repository's current `stats/dardic-plains/` analysis.
The builder independently reconstructs all fractional family votes from form
evidence and asserts agreement with every saved share and denominator. It also
rebuilds the essay's expandable family tables between explicit markers.

The revised metric is separation among linked language units times a positive
support factor, reaching full support at five fractional votes for each focal
family on its associated side. Unknowns do not penalize the score. Its unit test
adds 100 unknown units without changing the score, while known crossover or a
different family lowers it. Scores, support votes, and old/new ranks are
preserved; the post's selected illustrations are not the new ranking's top six.

RIVER's gloss-start filter is a diagnostic only. The predicate is case-insensitive
`^(?:a\s+)?river\b` on the stripped gloss. It changes both the attested and linked
denominators and does not silently update the main ranking or lexical data.

Checks:

```sh
python3 -m unittest discover -s ../data/tests -p test_concept_isoglosses.py
node --test tests/blog.test.mjs
npm run check
JAMBU_DB=.dbwork/jambu.db PRERENDER_LIMIT=5 npm run build
```

The snapshot provenance is the compiled dataset's exact file hashes, not a claim
that pending raw editorial overlays were applied. Membership counts distinguish
unresolved records and excluded loans, including within linked language units.

## Extended analyses and counting sensitivity

Default `entry` mode collapses explicitly linked numbered CDIAL subheads into
one article family; this broader grouping includes some derivatives. `head`
mode retains distinct heads while still following accepted variant links.
Neither mode infers identity from spelling. The collapse audit names every merge.
All ten chart viewers support both modes; asymmetric concept views also include
maps, unknowns and inspectable alternative-family contributions.

The follow-up script uses full-corpus frozen results and compressed evidence in
`inputs/`, plus compact head metadata and the entry-family mapping. It produces
attestation-era comparisons, score-band diagnostics, exact S/L presence counts
(with held-out pair selection), and a one-sided Dardic score. It also regenerates
the intro table and writes a separate extension manifest. Narrative conclusions
must be reviewed if inputs change. The full-corpus input snapshot was frozen
before running either mode to avoid mixing concurrent compiled-data updates.

To refresh intentionally, run the data script twice against the **same stable
CLDF directory**, with `--family-level head --out stats/dardic-plains-head` and
`--family-level entry --out stats/dardic-plains`. Then run the two builders with
`--refresh-snapshot --refresh-coordinates`, and finally `extensions.py --freeze`.
The freeze command rejects any input hash mismatch between the two analyses.
For ordinary reproduction, the three commands above need no live CLDF tables.
Always run extensions last: it combines the two base chart packages.

Additional checks: `python3 -m unittest discover -s research/dardic-plains -p test_extensions.py`.
