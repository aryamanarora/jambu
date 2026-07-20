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
import csv
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

# Clade → colour + canonical order (== ../data clade scheme, ported from the old make_database.py).
CLADE_COLORS = {
    "OIA": "E2DFD2", "MIA": "FFDEAD", "Migratory": "63666A", "Nuristani": "9132a8",
    "Pashai": "FFD6F6", "Chitrali": "FFACEF", "Shinaic": "FF81E6", "Kohistani": "FF25D5",
    "Kunar": "ff68e0", "Kashmiric": "FF00CD", "Sindhic": "0066FF", "Lahndic": "a4d6f5",
    "Punjabic": "7164FF", "W. Pahari": "B94E16", "C. Pahari": "9E521B", "E. Pahari": "79421B",
    "Eastern": "FFDE54", "Bihari": "FFCD00", "E. Hindi": "FF9A54", "W. Hindi": "FF6600",
    "Rajasthanic": "6BCD00", "Gujaratic": "00CF4A", "Marathi-Konkani": "D50000", "Bhil": "09AD02",
    "Khandeshi": "2FFF2F", "Halbic": "AB8900", "Insular": "AC0000", "Old Dravidian": "679267",
    "S. Dravidian I": "74C365", "S. Dravidian II": "98FB98", "C. Dravidian": "29AB87",
    "N. Dravidian": "4B6F44", "Brahui": "49796B", "Munda": "00ffd0", "Burushaski": "f3ff05",
    "Nihali": "ff9a00", "Other": "FAF9F6",
}
CLADE_ORDER = list(CLADE_COLORS.keys())

# Text columns on `lemmas` exposed to substring search. Only these three are actual filter
# columns in the UI (search.py filters: word, gloss, notes; `origin` reuses the word index).
# native/phonemic/original are displayed but never filtered, so we don't index them — this keeps
# the trigram index (and thus the whole DB) markedly smaller.
LEMMA_FTS_COLUMNS = ["word", "gloss", "notes"]


def log(msg: str) -> None:
    print(f"[build_static_db] {msg}", flush=True)


# ── Build the base tables directly from the CLDF dataset (retires the old data.db) ──────────────


def build_base_schema(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE languages (
            id TEXT PRIMARY KEY, name TEXT, language TEXT, dialect TEXT, glottocode TEXT,
            long FLOAT, lat FLOAT, clade TEXT, color TEXT, lemma_count INTEGER,
            "order" INTEGER, map_marker TEXT
        );
        CREATE TABLE "references" (id TEXT PRIMARY KEY, short TEXT, source TEXT, progress TEXT);
        CREATE TABLE lemmas (
            id TEXT PRIMARY KEY, word TEXT, gloss TEXT, native TEXT, phonemic TEXT, original TEXT,
            notes TEXT, clades TEXT, cognateset TEXT, "order" INTEGER, language_id TEXT,
            origin_lemma_id TEXT, tags TEXT, reflex_count INTEGER, lang_count INTEGER
        );
        CREATE TABLE lemma_reference (lemma_id TEXT, reference_id TEXT);
        """
    )


def _marker_svg(clade: str, name: str) -> str:
    color = CLADE_COLORS.get(clade, "999999")
    if clade in ("MIA", "OIA") or "Old" in name or "Proto" in name:
        return (
            '<svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">'
            f'<polygon points="0,15 15,0 30,15 15,30" fill="#{color}" stroke="black" stroke-width="2"/></svg>'
        )
    return (
        '<svg viewBox="-2 -2 32 32" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="14" cy="14" r="13" fill="#{color}" stroke="black" stroke-width="2"/></svg>'
    )


def load_languages(con: sqlite3.Connection, path: Path) -> dict[str, str]:
    """languages.csv → languages table. Returns id→clade (needed for per-etymon clade aggregation)."""
    rows, clade_of = [], {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            name, clade = r["Name"], r["Clade"]
            language, dialect = name.split(": ", 1) if ": " in name else (name, "")
            rows.append(
                (
                    r["ID"], name, language, dialect, r.get("Glottocode") or "",
                    r["Longitude"] or None, r["Latitude"] or None, clade,
                    CLADE_COLORS.get(clade), CLADE_ORDER.index(clade) if clade in CLADE_ORDER else 999,
                    _marker_svg(clade, name),
                )
            )
            clade_of[r["ID"]] = clade
    con.executemany(
        'INSERT INTO languages (id,name,language,dialect,glottocode,long,lat,clade,color,"order",map_marker)'
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    con.commit()
    log(f"loaded {len(rows)} languages")
    return clade_of


def load_references(con: sqlite3.Connection, path: Path) -> None:
    with path.open(encoding="utf-8") as f:
        rows = [(r["ID"], r["Short"], r["Source"], r["Progress"]) for r in csv.DictReader(f)]
    con.executemany('INSERT INTO "references" (id,short,source,progress) VALUES (?,?,?,?)', rows)
    con.commit()
    log(f"loaded {len(rows)} references")


def _parse_ref(src: str) -> list[str]:
    """"ref1:page;ref2" → ['ref1','ref2'] (ports make_database.parse_ref)."""
    if not src:
        return []
    return list({r.split("[")[0] for r in src.split(";") if r.split("[")[0]})


def load_lemmas(con: sqlite3.Connection, forms_csv: Path, clade_of: dict[str, str]) -> None:
    """Build the unified lemmas table from the one CLDF forms.csv (etyma + reflexes). Etyma have an
    empty Origin_ID; reflexes point at their etymon. Sets the self-referential origin_lemma_id, the
    etymon-anchored `order`, tags, per-etymon clade set, and the lemma↔reference links."""
    with forms_csv.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    lemmas = []
    etymon_order: dict[str, int] = {}
    # pass 1: etyma (Origin_ID empty) — word=headword, gloss=full CDIAL HTML, notes=Description
    # (Etyma); no attested-form fields (NULL). `order` is sequential in file order (× 1000).
    i = 0
    for r in rows:
        if r["Origin_ID"]:
            continue
        etymon_order[r["ID"]] = i * 1000
        lemmas.append(
            (r["ID"], r["Form"], r["Gloss"], None, None, None, r["Description"] or "",
             None, None, i * 1000, r["Language_ID"], None, None)
        )
        i += 1

    # pass 2: reflexes — origin from Origin_ID (strip borrowing/semi-tatsama markers), order anchored
    # just after their etymon.
    param_cts: dict[str, int] = defaultdict(int)
    param_clades: dict[str, set] = defaultdict(set)
    lemma_refs = []
    for r in rows:
        pid = r["Origin_ID"]
        if not pid:
            continue
        if pid[0] in ">~":
            pid = pid[1:]
        param_cts[pid] += 1
        lemmas.append(
            (r["ID"], r["Form"], r["Gloss"], r["Native"], r["Phonemic"], r["Original"],
             r["Description"] or "", None, r["Cognateset"], etymon_order.get(pid, 0) + param_cts[pid],
             r["Language_ID"], pid, (r["Tags"] or None))
        )
        cl = clade_of.get(r["Language_ID"])
        if cl:
            param_clades[pid].add(cl)
        for ref in _parse_ref(r["Source"]):
            lemma_refs.append((r["ID"], ref))

    con.executemany(
        'INSERT INTO lemmas (id,word,gloss,native,phonemic,original,notes,clades,cognateset,'
        '"order",language_id,origin_lemma_id,tags) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
        lemmas,
    )
    con.executemany(
        "UPDATE lemmas SET clades=? WHERE id=?",
        [(",".join(sorted(cs)), pid) for pid, cs in param_clades.items()],
    )
    # references cited by forms but absent from the bibliography → id-only rows
    ref_ids = {r[0] for r in con.execute('SELECT id FROM "references"')}
    con.executemany(
        'INSERT OR IGNORE INTO "references" (id) VALUES (?)',
        [(m,) for m in {ref for _, ref in lemma_refs if ref not in ref_ids}],
    )
    con.executemany(
        "INSERT INTO lemma_reference (lemma_id,reference_id) VALUES (?,?)", lemma_refs
    )
    con.execute(
        "UPDATE languages SET lemma_count = "
        "(SELECT COUNT(*) FROM lemmas WHERE lemmas.language_id = languages.id)"
    )
    con.commit()
    log(f"loaded {len(lemmas)} lemmas, {len(lemma_refs)} lemma↔reference links")


def load_derivation(con: sqlite3.Connection, deriv_csv: Path) -> None:
    """Load the derivation graph (derived-term → ancestor etymon) from ../data/link_refs.py output
    into a `derivation` table, indexed both directions for 'ancestors of X' and 'derived from X'."""
    con.executescript(
        """
        DROP TABLE IF EXISTS derivation;
        CREATE TABLE derivation (child_id TEXT, parent_id TEXT);
        """
    )
    with deriv_csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        con.executemany(
            "INSERT INTO derivation (child_id, parent_id) VALUES (?, ?)",
            ((r["Child_ID"], r["Parent_ID"]) for r in reader),
        )
    con.executescript(
        """
        CREATE INDEX idx_derivation_parent ON derivation(parent_id);
        CREATE INDEX idx_derivation_child ON derivation(child_id);
        """
    )
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM derivation").fetchone()[0]
    log(f"loaded derivation graph: {n} edges from {deriv_csv}")


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
    # small index for the correspondence drill-down (all reflexes for one etymon→reflex segment
    # pair). The proto/clade filters and the display columns come from joins to lemmas/languages,
    # which are cheap on the locally-loaded DB — so we don't denormalise them onto every row.
    con.execute("CREATE INDEX idx_alignment_seg ON alignment(etymon_seg, reflex_seg, form_id)")
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
            e.language_id AS proto,        -- the etymon's (proto) family, e.g. Indo-Aryan
            rl.clade      AS clade,        -- the reflex language's clade
            rf.language_id AS lang,        -- the reflex language
            a.etymon_seg  AS etymon_seg,
            a.prev_seg    AS prev_seg,      -- environment
            a.next_seg    AS next_seg,
            a.reflex_seg  AS reflex_seg,
            a.change      AS change,
            COUNT(*)      AS n,
            MIN(a.form_id) AS example
        FROM alignment a
        JOIN lemmas e     ON e.id = a.parameter_id
        JOIN lemmas rf    ON rf.id = a.form_id
        JOIN languages rl ON rl.id = rf.language_id
        WHERE a.etymon_seg <> ''
        GROUP BY e.language_id, rl.clade, rf.language_id, a.etymon_seg,
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


def transform(out: Path, page_size: int, cldf: Path) -> None:
    if not cldf.exists():
        log(f"FATAL: CLDF directory not found: {cldf}")
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    con = sqlite3.connect(out)
    con.execute("PRAGMA foreign_keys=OFF")
    check_trigram_available(con)

    # 1. Build the base tables directly from the CLDF dataset (../data) — the frozen data.db and
    #    neojambu's builder are no longer in the loop; ../data is the single source of truth.
    build_base_schema(con)
    clade_of = load_languages(con, cldf / "languages.csv")
    load_references(con, cldf / "references.csv")
    load_lemmas(con, cldf / "forms.csv", clade_of)

    # 2. Indexes: the base four (from the old ORM model) + citation-join + list-ordering.
    con.executescript(
        """
        CREATE INDEX idx_lemmas_language_id     ON lemmas(language_id);
        CREATE INDEX idx_lemmas_origin_lemma_id ON lemmas(origin_lemma_id);
        CREATE INDEX idx_lemmas_order           ON lemmas("order");
        CREATE INDEX idx_lemmas_cognateset      ON lemmas(cognateset);
        CREATE INDEX idx_lemma_reference_reference_id ON lemma_reference(reference_id);
        CREATE INDEX idx_lemma_reference_lemma_id     ON lemma_reference(lemma_id);
        CREATE INDEX idx_lemmas_language_order   ON lemmas(language_id, "order");
        -- partial index for the Entries list (headwords): ORDER BY "order" with no temp sort.
        CREATE INDEX idx_entries_order ON lemmas("order") WHERE origin_lemma_id IS NULL;
        """
    )
    log("created lemma + citation-join + ordering indexes")

    # 3. Derivation graph (derived-term → ancestor etymon).
    deriv = cldf / "derivation.csv"
    if deriv.exists():
        load_derivation(con, deriv)
    else:
        log(f"(no derivation.csv at {deriv}; skipping derivation graph)")

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
    alignments = cldf / "alignments.csv"
    if alignments.exists():
        load_alignments(con, alignments)
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
    ap = argparse.ArgumentParser(
        description="Build the static-site SQLite DB directly from the CLDF dataset (../data)."
    )
    ap.add_argument("output", type=Path, help="output DB path (e.g. .dbwork/jambu.db)")
    ap.add_argument("--cldf", type=Path, default=Path("../data/cldf"),
                    help="CLDF directory (forms.csv, parameters.csv, languages.csv, references.csv, "
                         "alignments.csv, derivation.csv)")
    ap.add_argument("--page-size", type=int, default=8192,
                    help="SQLite page size for the output (default 8192, range-fetch friendly)")
    args = ap.parse_args()

    t0 = time.time()
    transform(args.output, args.page_size, args.cldf)
    log(f"elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
