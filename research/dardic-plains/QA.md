# Validation — 11 September 2026

- Five focused analysis tests pass, including invariance to 100 additional
  unknown language units, reduced score for known alternatives/crossover,
  fractional synonym weights, OIA graph boundaries, redirects and borrowing.
- Eight blog renderer tests pass. Fractional votes require explicit opt-in;
  ordinary charts still reject fractions, and all charts reject negative or
  nonfinite values.
- `npm run check`: zero errors; seven existing warnings in five unrelated files.
- The evidence builder independently reconstructs all nine concepts from 2,104
  form–concept evidence rows and reconciles every family share and denominator.
  Full alternatives and unresolved/loan record counts are retained in downloads.
- Browser preview: all five interactive charts render; Votes/Count and Proportion
  switches work; RIVER filtering yields 12/28 linked units versus 13/31 before
  filtering; LONG's all-attested view yields 22/71 units versus 20/41 linked.
  RIVER's coverage view shows 13 linked + 9 without included family in Dardic,
  and 31 + 29 in Plains. Its complete family table expands successfully.
- At 390 × 844 the document width is 390 pixels, and the chart controls, labels
  and bars fit. Desktop preview is also visually checked, in the app's dark
  theme. Browser error log is empty. Temporary viewport override was reset.
- Production client compilation succeeded and the new post was prerendered
  successfully, resolving all its typed lexical links. Its static HTML contains
  five charts and 41 tables, without JS-only controls, preserving a readable
  server-rendered version. The subsequent site-wide crawler was stopped after
  this focused validation; a full deployment build is **not** claimed. It also
  emitted an unrelated existing malformed Webonary URL warning.
- The final small prose addition linking the complete ranking was checked in
  the local preview after prerender validation. No lexical data build,
  database refresh, publication, push or deployment was performed.

Preview: `http://127.0.0.1:5192/jambu/blogs/dardic-plains-isoglosses`.

## Inline maps and family breakdowns

- All five viewers have maps; concept and RIVER-filter changes update map evidence
  from the same frozen scope as the bars. Map weights are reconciled against every
  displayed bar, including explicit treatment of map-only unknowns in linked-only
  views. Coordinate provenance matches the original languages-table hash.
- Browser-checked RIVER Dardic map: 22 located / 22 attested units; LONG all-groups
  view: 90 located / 93 attested units, with the other three retained in the selector
  and evidence. Group filtering zooms the Dardic region without changing bars.
- Clicking Bhateri reveals sindhu and *khāḍa, source forms, one unresolved record,
  and zero excluded loan records. Marker size verified in the DOM at 10 × 10 px;
  selected markers use 16 px.
- The RIVER “Other resolved families” segment opens ten etyma with fractional
  contributions, percentages and attesting languages. All breakdowns reconcile
  numerically with their parent segments during generation and rendering.
- Nine renderer tests pass, including invalid coordinates and inconsistent
  other-family contributions. Mobile document width remains 390 px; breakdown
  tables scroll internally rather than wrapping etymon names into narrow columns.
- Fixed a Leaflet teardown race observed during hot reload: asynchronous loading
  now respects disposal, maps stop before removal, and inline maps disable zoom
  animation. Zooming and immediately switching the map group introduces no new
  browser errors. Final mobile table width is 540 px inside a 337 px scrolling
  container, with the document remaining 390 px wide.


## Extension and introduction update (11 September 2026)

- Froze all five CLDF tables with source-before/source-after/copy hash equality;
  both counting modes and age metadata use this exact snapshot.
- 662 eligible entry-family concepts, 668 separate-headword concepts. Full
  distributions reconstructed independently from form evidence in both modes.
- Ten chart viewers, 126 total views; both modes present in every viewer.
  All linked chart downloads exist; both output manifests match their files.
- Six lexical-analysis tests, three extension tests and nine blog-render tests pass.
  Svelte check: zero errors, seven pre-existing warnings in five unrelated files.
- Browser QA: intro score table renders correctly; MOUSTACHE switches from
  Plains 67% (head) to 77% (entry); LAKE alternatives show ten families whose
  contributions reconcile to its bar; asymmetric BIRCH appears in head mode;
  held-out stronger S/L cohort has 122 concepts; LAKE's Dardic-only map renders
  with small points. Page width equals viewport width at 842px; no console errors
  were returned during this check.
- Corrected held-out prose denominator to 122/123 based on the viewer.
- Full corpus evidence is downloadable in both modes as compressed CSV. No
  publishing or full-site production build was performed for this update.
