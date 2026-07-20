#!/usr/bin/env python3
"""
build_static_db.py — transform the raw Jambu SQLite DB into a static, browser-queryable form.

The raw data.db (published as a GitHub release asset on moli-mandala/data) is optimised for a
server with an ORM. For the static GitHub Pages site we query it directly in the browser via
sql.js-httpvfs, so we bake in everything the client needs:

  1. Drop the empty/unused `concepts` and `lemma_concept` tables.
  2. Add the indexes the client query layer relies on (the release DB already has the four
     `idx_lemmas_*` ones; we add the citation-join indexes).
  3. Build an FTS5 **trigram** index over the lemma text columns so substring search
     (the old `LIKE '%x%'`) is fast and, crucially, page-local under HTTP Range fetching.
  4. ANALYZE + VACUUM so the B-trees and FTS shadow tables are laid out contiguously.

Tiny lookup tables (languages: 615 rows, references: 194 rows) are searched with plain LIKE on
the client — no index needed — so we do not build FTS for them.

Usage:
    python build_static_db.py INPUT.db OUTPUT.db [--page-size 8192]

The script never mutates INPUT.db; it copies it to OUTPUT.db first.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
import time
from pathlib import Path

# Text columns on `lemmas` exposed to substring search. Only these three are actual filter
# columns in the UI (search.py filters: word, gloss, notes; `origin` reuses the word index).
# native/phonemic/original are displayed but never filtered, so we don't index them — this keeps
# the trigram index (and thus the whole DB) markedly smaller.
LEMMA_FTS_COLUMNS = ["word", "gloss", "notes"]


def log(msg: str) -> None:
    print(f"[build_static_db] {msg}", flush=True)


def table_exists(con: sqlite3.Connection, name: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def count(con: sqlite3.Connection, table: str) -> int:
    return con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]


def check_trigram_available(con: sqlite3.Connection) -> None:
    try:
        con.execute("CREATE VIRTUAL TABLE _trigram_probe USING fts5(x, tokenize='trigram')")
        con.execute("DROP TABLE _trigram_probe")
    except sqlite3.OperationalError as e:  # pragma: no cover - environment guard
        log(f"FATAL: this SQLite build lacks FTS5 trigram support: {e}")
        log(f"       sqlite_version={sqlite3.sqlite_version} (need >= 3.34.0 with FTS5)")
        sys.exit(1)


def load_alignments(con: sqlite3.Connection, path: Path) -> None:
    """Load the normalised etymon→reflex alignment CSV into an indexed `alignment` table."""
    import csv

    con.executescript(
        """
        DROP TABLE IF EXISTS alignment;
        CREATE TABLE alignment (
            form_id      TEXT,     -- reflex lemma id (→ lemmas.id)
            parameter_id TEXT,     -- etymon lemma id (→ lemmas.id)
            pos          INTEGER,  -- column order within this reflex's alignment
            etymon_idx   INTEGER,  -- stable index of the etymon segment (-1 for insertions)
            etymon_seg   TEXT,
            reflex_seg   TEXT,
            change       TEXT,     -- category code (kept/loss/add/deaffrication/…); see align.py
            prev_seg     TEXT,     -- preceding etymon segment ('#' = word edge)
            next_seg     TEXT      -- following etymon segment
        );
        """
    )
    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        con.executemany(
            "INSERT INTO alignment VALUES (?,?,?,?,?,?,?,?,?)",
            (
                (r[0], r[1], int(r[2]), int(r[3]), r[4], r[5], r[6], r[7], r[8])
                for r in reader
                if len(r) >= 9
            ),
        )
    # one index serves both the per-entry tree (WHERE parameter_id) and per-entry
    # correspondence (WHERE parameter_id AND pos); language comes from a join to lemmas.
    con.execute("CREATE INDEX idx_alignment_param ON alignment(parameter_id, form_id, pos)")
    con.commit()

    # Denormalise proto family / reflex clade / reflex language onto each alignment row so the
    # correspondence drill-down page can filter with a pure index range scan (no per-row joins to
    # lemmas over HTTP range requests — those made the page unusably slow).
    con.executescript(
        """
        ALTER TABLE alignment ADD COLUMN proto TEXT;
        ALTER TABLE alignment ADD COLUMN lang  TEXT;
        ALTER TABLE alignment ADD COLUMN clade TEXT;
        UPDATE alignment SET
            proto = (SELECT language_id FROM lemmas WHERE id = alignment.parameter_id),
            lang  = (SELECT language_id FROM lemmas WHERE id = alignment.form_id);
        UPDATE alignment SET clade = (SELECT clade FROM languages WHERE id = alignment.lang);
        """
    )
    # the drill-down filters (proto, clade, etymon_seg, reflex_seg) then groups/orders by language;
    # this covering-prefix index makes the LIMITed fetch touch only the matching rows in lang order.
    con.execute(
        "CREATE INDEX idx_alignment_corr ON "
        "alignment(proto, clade, etymon_seg, reflex_seg, lang, form_id)"
    )
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM alignment").fetchone()[0]
    log(f"loaded alignment table: {n} aligned segments from {path}")

    # Aggregate a compact, queryable correspondence summary for the Sound Correspondence explorer:
    # per (proto family, reflex clade, etymon segment, reflex segment, change) → count + example.
    # Collapses ~1.5M alignment rows into a few tens of thousands, so the explorer reads a small
    # indexed table instead of scanning the alignment.
    con.executescript(
        """
        -- language-level, environment-conditioned (queried only when a branch is expanded)
        DROP TABLE IF EXISTS corr_lang;
        CREATE TABLE corr_lang AS
        SELECT
            a.proto       AS proto,        -- the etymon's (proto) family, e.g. Indo-Aryan
            a.clade       AS clade,        -- the reflex language's clade
            a.lang        AS lang,         -- the reflex language
            a.etymon_seg  AS etymon_seg,
            a.prev_seg    AS prev_seg,      -- environment
            a.next_seg    AS next_seg,
            a.reflex_seg  AS reflex_seg,
            a.change      AS change,
            COUNT(*)      AS n,
            MIN(a.form_id) AS example
        FROM alignment a
        WHERE a.etymon_seg <> ''
        GROUP BY a.proto, a.clade, a.lang, a.etymon_seg,
                 a.prev_seg, a.next_seg, a.reflex_seg, a.change;
        CREATE INDEX idx_corr_lang ON corr_lang(proto, etymon_seg, clade);

        -- compact clade-level roll-up (the default, per-segment load)
        DROP TABLE IF EXISTS corr;
        CREATE TABLE corr AS
        SELECT proto, clade, etymon_seg, prev_seg, next_seg, reflex_seg, change,
               SUM(n) AS n, MIN(example) AS example
        FROM corr_lang
        GROUP BY proto, clade, etymon_seg, prev_seg, next_seg, reflex_seg, change;
        CREATE INDEX idx_corr ON corr(proto, etymon_seg);

        -- tiny per-segment totals (for the segment picker; avoids scanning the big tables)
        DROP TABLE IF EXISTS corr_seg;
        CREATE TABLE corr_seg AS
        SELECT proto, etymon_seg, SUM(n) AS total FROM corr_lang GROUP BY proto, etymon_seg;
        """
    )
    con.commit()
    log("built correspondence summaries: corr_lang=%d, corr=%d"
        % (con.execute('SELECT COUNT(*) FROM corr_lang').fetchone()[0],
           con.execute('SELECT COUNT(*) FROM corr').fetchone()[0]))


def transform(inp: Path, out: Path, page_size: int, alignments: str | None) -> None:
    if not inp.exists():
        log(f"FATAL: input DB not found: {inp}")
        sys.exit(1)

    log(f"copying {inp} -> {out} ({inp.stat().st_size / 1e6:.1f} MB)")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inp, out)

    con = sqlite3.connect(out)
    con.execute("PRAGMA foreign_keys=OFF")
    check_trigram_available(con)

    log("before: " + ", ".join(
        f"{t}={count(con, t)}" for t in ("lemmas", "languages", "references")
    ))

    # 1. Drop unused tables (both confirmed empty in the shipped DB).
    for t in ("lemma_concept", "concepts"):
        if table_exists(con, t):
            n = count(con, t)
            con.execute(f'DROP TABLE "{t}"')
            log(f"dropped table {t} ({n} rows)")

    # 2. Indexes for the citation join (references <-> lemmas via lemma_reference).
    #    The M2M PK gives an autoindex on (lemma_id, reference_id); we add a reference_id-first
    #    index so "find all lemmas citing reference R" is a lookup, not a scan.
    con.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_lemma_reference_reference_id
            ON lemma_reference(reference_id);
        CREATE INDEX IF NOT EXISTS idx_lemma_reference_lemma_id
            ON lemma_reference(lemma_id);
        -- keep the four release indexes; add order+id compound used by list ordering
        CREATE INDEX IF NOT EXISTS idx_lemmas_language_order
            ON lemmas(language_id, "order");
        -- partial index for the Entries list (headwords) so ORDER BY "order" needs no temp sort
        -- and only touches entry rows — important for page locality under HTTP Range fetching.
        CREATE INDEX IF NOT EXISTS idx_entries_order
            ON lemmas("order") WHERE origin_lemma_id IS NULL;
        """
    )
    log("created citation-join + ordering indexes")

    # 3. FTS5 trigram over lemma text columns (external content => no duplicated text).
    #    content_rowid uses the implicit rowid since lemmas.id is a VARCHAR PK.
    cols = ", ".join(LEMMA_FTS_COLUMNS)
    con.executescript(
        f"""
        DROP TABLE IF EXISTS lemmas_fts;
        CREATE VIRTUAL TABLE lemmas_fts USING fts5(
            {cols},
            content='lemmas',
            content_rowid='rowid',
            tokenize='trigram'
        );
        INSERT INTO lemmas_fts(rowid, {cols})
            SELECT rowid, {cols} FROM lemmas;
        """
    )
    log(f"built lemmas_fts (trigram) over: {cols}")

    # 3b. Precomputed totals so the client never issues a full-table COUNT(*) (a whole-index scan
    #     is many range requests over the wire; these are 1-row lookups instead).
    con.executescript(
        """
        DROP TABLE IF EXISTS meta;
        CREATE TABLE meta (key TEXT PRIMARY KEY, value INTEGER);
        INSERT INTO meta VALUES
            ('total_lemmas',   (SELECT COUNT(*) FROM lemmas)),
            ('total_entries',  (SELECT COUNT(*) FROM lemmas WHERE origin_lemma_id IS NULL)),
            ('total_reflexes', (SELECT COUNT(*) FROM lemmas WHERE origin_lemma_id IS NOT NULL));
        """
    )
    log("wrote meta counts: " + str(con.execute('SELECT key, value FROM meta').fetchall()))

    # 3b2. Materialise per-entry aggregates (reflex + distinct-language counts) so the Entries
    #      list can show and SORT by them. Partial indexes give sort-without-scan on the headwords.
    con.executescript(
        """
        ALTER TABLE lemmas ADD COLUMN reflex_count INTEGER;
        ALTER TABLE lemmas ADD COLUMN lang_count INTEGER;
        UPDATE lemmas SET
            reflex_count = (SELECT COUNT(*) FROM lemmas r WHERE r.origin_lemma_id = lemmas.id),
            lang_count   = (SELECT COUNT(DISTINCT r.language_id) FROM lemmas r
                            WHERE r.origin_lemma_id = lemmas.id)
        WHERE origin_lemma_id IS NULL;
        CREATE INDEX idx_entries_reflex_count ON lemmas(reflex_count) WHERE origin_lemma_id IS NULL;
        CREATE INDEX idx_entries_lang_count   ON lemmas(lang_count)   WHERE origin_lemma_id IS NULL;
        """
    )
    con.commit()
    log("materialised per-entry reflex_count / lang_count")

    # 3c. Materialised etymon→reflex sound-change alignments (computed in ../data by align.py).
    #     A normalised, queryable table: one row per aligned segment. Powers the descent-tree +
    #     sound-change view and corpus-wide correspondence queries.
    if alignments and Path(alignments).exists():
        load_alignments(con, Path(alignments))
    else:
        log(f"(no alignments file at {alignments}; skipping sound-change table)")

    # 4. Optimise FTS + compact the file for range-friendly layout.
    con.execute("INSERT INTO lemmas_fts(lemmas_fts) VALUES('optimize')")
    con.commit()
    con.execute("ANALYZE")
    con.commit()
    log(f"setting page_size={page_size} and VACUUMing (this rewrites the file)…")
    con.execute(f"PRAGMA page_size={page_size}")
    con.execute("VACUUM")
    con.commit()

    # Sanity: a substring MATCH must return rows.
    probe = con.execute(
        "SELECT COUNT(*) FROM lemmas_fts WHERE lemmas_fts MATCH ?", ('word:"amb"',)
    ).fetchone()[0]
    log(f"sanity: trigram MATCH 'word:amb' -> {probe} lemmas")

    con.close()
    log(f"done: {out} ({out.stat().st_size / 1e6:.1f} MB)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Transform raw Jambu DB into a static-site DB.")
    ap.add_argument("input", type=Path, help="raw data.db (from the release)")
    ap.add_argument("output", type=Path, help="transformed output path")
    ap.add_argument("--page-size", type=int, default=8192,
                    help="SQLite page size for the output (default 8192, range-fetch friendly)")
    ap.add_argument("--alignments", default="../data/cldf/alignments.csv",
                    help="path to align.py output (materialised sound-change table); skipped if absent")
    args = ap.parse_args()

    t0 = time.time()
    transform(args.input, args.output, args.page_size, args.alignments)
    log(f"elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
