# Sound correspondence explorer

The explorer at `/correspondences` separates three query choices from their display:

1. Ancestor entries, a sound/class sequence, optional form properties, and an input facet.
2. Descendant languages (all, individual selections, or matching a branch).
3. A descendant outcome grouping: aligned sequences, accent position, tone/mark type,
   syllable count/change, or place/manner of articulation.

The ancestor toolbar reuses Entries search components and the same query conditions
in `src/lib/query.ts`: broad search, form, meaning, etymology, tags, source, entry
types, and relaxed Unicode matching. The preview link opens those filters in Entries.
Search is applied to the resolved alignment ancestor, not the descendant form.
The Entries query string is nested in `entry` so its parameters cannot collide
with descendant language choices or correspondence properties.

Input edits are drafts until **Run/Update comparison**. Table/Map is a separate
choice and preserves pending edits. The table has languages as rows and input
facets as columns; pie slices show descendant outcomes. The explicit **Group
ancestor inputs by** control defines those columns. Its Sound properties section
covers target sequences, full sequences including context, C/V shape, place,
manner, voicing, and aspiration. Sound properties describe the aligned target;
Full sequence, including context preserves the complete matching ancestor sequence. Its Form properties section covers ancestor
accent, syllable count, complete weight/quantity patterns, starred status, and
matched-syllable weight, quantity, or closure. Unknown readings remain separate.
Weight patterns use H/L (heavy/light); quantity patterns use S/L (short/long). The map uses the same
cells with an input-group selector. A cell or map popup opens a URL-backed evidence
drawer; Escape closes it and Back restores the previous state. Shared links retain
the full query, display, selected map group, and evidence selection. Legacy `/set`
links, including deletion outcomes, redirect into the same explorer.

## Sequence matching

`src/lib/soundPattern.ts` accepts compact or spaced literals (`kt`, `k t`),
classes (`VCV`, `V C V`, `[retroflex]`), class conjunctions
(`[retroflex+stop]`), and word boundaries (`#kt`, `VCV#`). One parenthesized
span selects the aligned target: `V (k) V` requires k between vowels but counts
only the descendant sequence aligned to k. `V (kt) V` targets the consonant pair.
Without parentheses, the complete matched sequence is the target. `*` or an empty
input selects the whole form. Class patterns can be split by actual sound sequence
without changing how descendant outcomes are grouped.

The focused text field opens a class picker that inserts at the caret or replaces
selected text. Inside brackets, descriptor buttons combine classes with `+`.
Parsed-token buttons select the target; Shift-click extends it, and selected text
can also be wrapped as the target. On blur, the field shows parsed chips with the
target highlighted and context muted. Enter applies; Escape or Done closes the
picker. The picker remains keyboard-accessible and uses an inline layout on phones.

Matches are contiguous in the ancestor's nonempty alignment columns. All context
must match. Descendant insertions inside the target are part of its outcome;
insertions outside the target's edges are excluded, including those inside the
surrounding context. Whole-form selection includes edge insertions. Overlapping matches
are separate occurrences. Legacy detached modifiers remain a data limitation;
nonsegmental notation aligned to an ancestor sound produces the explicit `?`
outcome. Matching works on stored alignments, not a newly inferred segmentation.

## Features and interpretation

`src/lib/phonology.ts` computes descriptive prosody from alignment tokens. It
preserves positions when legacy columns split combining marks, and distinguishes
syllable count, nucleus quantity, conventional weight/closure, marked accent
position, and barytone/oxytone class. Unmarked forms are unknown. Svarita, multiple
marks, alternatives, ambiguous vowel sequences, and unreadable segments retain
flags. These are citation-form properties, not inferred inflectional accent paradigms.

OIA ai/au are single long nuclei, e/o are long, and syllabic liquids are nuclei.
Syllable division follows V.CV / VC.CV; metrical exceptions need review. No schwa
deletion is inferred from orthography. Segment identities preserve length,
nasalization, and consonantal diacritics such as ś while removing vowel accent.
Matched-syllable properties refer to the start of the aligned target.

Recognized normalized source conventions support mora readings for Liljegren's
Palula and Degener's Gilgit Shina. Mixed or unknown conventions keep the observed
mark without assigning a mora. Tone grouping keeps source conventions distinct;
unmarked data is not a toneless class. The folded reading notes link the references.

## Query and counts

`getSoundObservations` uses the existing compact database. A recursive query resolves
variant parents using the data aligner's accepted-ancestry rule. Descendant language
and ancestor-entry restrictions apply before parsing; property filters reduce the
retained cohort. There is no schema migration or new database artifact.

Only one cohort is cached, with shared ancestor/source objects and cancellation of
obsolete parsing. Display, evidence, facet, and outcome-group navigation reuse it.
Changing the ancestor pattern, entry search, languages, or property restrictions
loads another cohort. Broad selections still require more time and memory.

`src/lib/soundStudy.ts` owns independent input/outcome grouping and matrix cells.
`src/lib/soundExplorer.ts` supplies property filters and counting:

- Matched sequences count individual spans.
- Forms count each stable form ID once per cell.
- Families within languages count each accepted ancestry root once per cell/language.

Each cell has its own denominator. A form or family with several distinct outcomes
splits its vote equally among them. Percentages sum to 100%; supporting counts can
overlap. Forms appearing in several input facets contribute to each relevant cell.

Evidence includes complete alignments with the target highlighted and matching context shaded, descriptive
change events, reading flags, entry links, and source locators. CSV exports all
matching spans with target/context bounds, stable IDs, input/outcome groups, prosody, sources, and flags.
Tables page through six input groups and 25 languages; evidence pages show 30 forms.
Pagination limits rendering, not the underlying comparison or export.

## Validation

Run the focused checks sequentially from their respective repositories:

```sh
# jambu-static
node --test tests/soundExplorer.test.mjs
node scripts/check_sound_explorer.mjs .dbwork/jambu.db k --study
npm run check
GOMAXPROCS=1 UV_THREADPOOL_SIZE=1 BASE_PATH=/jambu JAMBU_DB=.dbwork/jambu.db PRERENDER_LIMIT=2 PRERENDER_SMOKE=1 npm run build

# data, if changing the aligner
.venv/bin/python -m pytest -q tests/test_alignment_features.py
```

The read-only database check executes the actual query module. It reconciles `k`
with existing summaries (51,623 positions / 43,653 forms / 4,110 families in the
current artifact), compares ancestor search against Entries, and checks literal
sequences, class conjunctions, language restriction, whole-form selection, and
empty searches. Pure tests cover Unicode, prosody, span boundaries/insertions,
overlapping matches, independent grouping, counting, and URL round trips.

Browser QA covers query construction, Entries filters, table/map equivalence,
popups, evidence, Back/Escape, and narrow layouts. The smoke build disables link
crawling so sampled entries cannot pull the full corpus into local prerendering;
normal production builds retain the full crawl.

The data-side `align.py` changes recognize syllabic liquids and ignore vowel-accent
differences in segment identity for future alignment builds. This feature does not
rebuild or publish the database. Full data generation and full production
prerendering remain release-workflow gates.


Language selection shares its search, branch colours, keyboard navigation and option rows with Favorites and the Entries/Forms language filters. Search by name, ID or branch; select several results or use pinned languages and clades. Favorites retain their ordering controls; form filters retain single selection and dialect options.

The comparison language picker supports inclusive minimum and maximum **total forms** (the language's full Jambu lexicon count) and **outcome forms** (distinct descendant form IDs matching the current ancestor query and conditions, across all input groups). Repeated matches, multiple outcome classes and citations never inflate the outcome-form threshold. Zero is a valid bound; blank means no bound. Limits and language choices are stored in the URL and apply together to the table, map, summary and evidence/CSV. Changing these limits, language choices, facets, display or counting unit reuses the loaded cohort. Pending ancestor edits show outcome counts as unavailable until the comparison runs, rather than presenting stale counts as current.
