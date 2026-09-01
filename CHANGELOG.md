# Changelog

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
