# Changelog

## db-v29 — 2026-09-08

- Added 2,210 Kusunda attestations from Aaley and Bodt (662), Watters (1,387), and
  Aaley’s *Kusunda Gipan* (161), with source spellings, grammatical tags, and citation locators.
- Expanded Nihali provisional etymologies, lexical groupings, and audited contact comparisons.
- Removed extraction-only clutter from form notes while retaining the source audit records.
- Compressed the browser download with Zstandard; restored databases preserve citation locators,
  structured tags, article text, alignments, aliases, and graph relations.
- Rebuilt 588,949 database nodes, including 29,362 entries and 290,267 reflexes, across
  409 languages and 523 references. The download is 43.00 MB (97.04 MB expanded).
- Updated browser cache versioning and deployment to serve the compressed artifact.

Validation: data build, database integrity, complete compaction parity, browser decompression
round-trip, and eight DB builder tests passed. Svelte check: zero errors, seven warnings.
Data suite: 1,430 passed, 14 skipped, 21 failures, all present in the pre-run failure cache.

## db-v28 — 2026-08-31

### Added

- Added a Concepts view to entry pages. It shows every reflex's parsed Concepticon concepts,
  colours the distribution map by concept, uses pie markers for mixed locations, and provides an
  interactive concept legend.
- Added form-only table filters alongside the global table search.
- Added relaxed Unicode matching that ignores diacritics and common presentation variants such as
  superscript letters.

### Changed

- Global table search now searches every visible column by default.
- Active global and column-level searches highlight their matching substrings throughout table
  cells, including forms, meanings, languages, ancestry, tags, notes, and sources.
- Concepts, languages, and the other atlas-style pages now reflow into touch-friendly stacked
  layouts on narrow screens.

### Fixed

- Restored CDIAL dictionary entries to the Entries view when they also have accepted
  Proto-Indo-Iranian or Proto-Dravidian ancestors. Source-headword status is now stored separately
  from ancestry in the compact database.
- Corrected concept membership lookups for delta-encoded form lists, so entry concept columns and
  map colours reflect the same assignments as the concept atlas.

### Data

- Rebuilt the browser database from the 2026-08-31 CLDF corpus: 591,889 lemmas, 26,610 entries,
  288,969 reflexes, 408 languages, and 519 references.
