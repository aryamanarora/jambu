#!/usr/bin/env python3
"""
build_static_db.py — transform the raw Jambu SQLite DB into a static, browser-queryable form.

The raw data.db (published as a GitHub release asset on moli-mandala/data) is optimised for a
server with an ORM. For the static GitHub Pages site we query it directly in the browser via
sql.js-httpvfs, so we bake in everything the client needs:

  1. Build compact browser tables directly from the unified CLDF data.
  2. Add the compact set of indexes the client query layer relies on.
  3. ANALYZE + VACUUM so the B-trees are laid out contiguously.

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
from urllib.parse import quote


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
# The durable-form-ID migration adds a compact 392k-row legacy redirect table (~6.2 MiB), while
# longer opaque IDs add several MiB to graph indexes. Keep a tight guard around that intentional
# compatibility cost rather than letting future schema growth pass unnoticed.
MAX_OUTPUT_BYTES = 120_000_000

# Printed dialect prefixes which differ from the canonical language name in languages.csv.
BASE_LANGUAGE_OVERRIDES = {
    "Hindi": "Hindi-Urdu",
}

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
        -- Dialects mirror the `languages` columns (name, language, dialect, glottocode, long, lat,
        -- clade, color, lemma_count, order, map_marker) so a dialect is described like a language,
        -- plus the linking fields it needs: token (PK, the tag), language_id (parent) and entry_count.
        CREATE TABLE dialects (
            token TEXT PRIMARY KEY, language_id TEXT NOT NULL,
            id TEXT NOT NULL, name TEXT NOT NULL, language TEXT, dialect TEXT, glottocode TEXT,
            long FLOAT, lat FLOAT, clade TEXT, color TEXT, location TEXT, quality TEXT,
            lemma_count INTEGER DEFAULT 0, "order" INTEGER, map_marker TEXT,
            entry_count INTEGER DEFAULT 0
        );
        CREATE TABLE "references" (
            id TEXT PRIMARY KEY, short TEXT, source TEXT, progress TEXT, provenance TEXT,
            editor TEXT, ocr INTEGER NOT NULL DEFAULT 0, lemma_count INTEGER DEFAULT 0,
            unetymologised_count INTEGER DEFAULT 0
        );
        -- CLDF Original is an import-time transliteration source; no display/query path reads it.
        -- The rendered form is word, so omitting Original avoids shipping ~2.1M dead characters.
        CREATE TABLE lemmas (
            id TEXT PRIMARY KEY, word TEXT, gloss TEXT, native TEXT, phonemic TEXT,
            notes TEXT, clades TEXT, cognateset TEXT, "order" INTEGER, language_id TEXT,
            origin_lemma_id TEXT, tags TEXT, reflex_count INTEGER, lang_count INTEGER,
            etymology TEXT, relation TEXT, redirect_to TEXT, variant_of TEXT, borrowed_from TEXT
        );
        -- Permanent redirects from pre-migration/order-dependent form IDs and build-time duplicate
        -- IDs to the retained durable lemma ID.
        CREATE TABLE lemma_aliases (
            alias TEXT PRIMARY KEY,
            lemma_rid INTEGER NOT NULL
        ) WITHOUT ROWID;
        CREATE TABLE lemma_reference (
            lemma_rid INTEGER NOT NULL,
            reference_rid INTEGER NOT NULL,
            locator TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (lemma_rid, reference_rid, locator)
        ) WITHOUT ROWID;
        -- Concepticon concept sets that glosses map to, plus per-concept rollups for the Concepts
        -- tab: etyma_count counts distinct immediate etyma (lone/unetymologised nodes excluded and
        -- counted in unetym_count instead), lang_count/form_count the attesting languages and forms.
        CREATE TABLE concepts (
            id INTEGER PRIMARY KEY, name TEXT, category TEXT,
            etyma_count INTEGER DEFAULT 0, unetym_count INTEGER DEFAULT 0,
            lang_count INTEGER DEFAULT 0, form_count INTEGER DEFAULT 0
        );
        -- link keyed by (concept_id, lemma rowid) as integers, WITHOUT ROWID so the PK is the only
        -- copy of the data (per-concept lookup is the PK's leftmost prefix — no extra index needed).
        CREATE TABLE lemma_concept (
            concept_id INTEGER NOT NULL, lemma_rid INTEGER NOT NULL,
            PRIMARY KEY (concept_id, lemma_rid)
        ) WITHOUT ROWID;
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


def load_languages(
    con: sqlite3.Connection, path: Path
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Load canonical languages plus dialect-tag metadata.

    A ``Language: Dialect`` CLDF row is no longer a language in the browser DB. Its full metadata
    is retained in ``dialects`` and its forms are remapped to the base-language row. The return
    values are (canonical-language→clade, source-id→canonical-id, source-id→dialect-token).
    """
    source_rows = []
    with path.open(encoding="utf-8") as f:
        source_rows = list(csv.DictReader(f))

    by_base: dict[str, list[dict[str, str]]] = defaultdict(list)
    exact: dict[str, dict[str, str]] = {}
    for r in source_rows:
        printed_base = r["Name"].split(": ", 1)[0]
        base = BASE_LANGUAGE_OVERRIDES.get(printed_base, printed_base)
        by_base[base].append(r)
        if ": " not in r["Name"]:
            exact.setdefault(base, r)

    rows, dialect_rows = [], []
    clade_of: dict[str, str] = {}
    canonical_of: dict[str, str] = {}
    dialect_tag_of: dict[str, str] = {}
    for base, members in by_base.items():
        representative = exact.get(base, members[0])
        canonical_id = representative["ID"]
        clade = representative["Clade"]
        # A synthesized parent has no single geographic point. Preserve every point below in the
        # dialect table; only an independently listed base language keeps base coordinates.
        has_base_row = base in exact
        glottocodes = {r.get("Glottocode") or "" for r in members} - {""}
        glottocode = representative.get("Glottocode") or ""
        if not glottocode and len(glottocodes) == 1:
            glottocode = next(iter(glottocodes))
        rows.append(
            (
                canonical_id, base, base, "", glottocode,
                (representative["Longitude"] or None) if has_base_row else None,
                (representative["Latitude"] or None) if has_base_row else None,
                clade, CLADE_COLORS.get(clade),
                CLADE_ORDER.index(clade) if clade in CLADE_ORDER else 999,
                _marker_svg(clade, base),
            )
        )
        clade_of[canonical_id] = clade
        for r in members:
            canonical_of[r["ID"]] = canonical_id
            if ": " not in r["Name"]:
                continue
            dialect = r["Name"].split(": ", 1)[1]
            # Include the source ID because the CLDF can contain two geographically distinct rows
            # with the same printed dialect name (e.g. the two Kausambi records).
            token = (
                f"dialect:{quote(canonical_id, safe='')}:{quote(r['ID'], safe='')}:"
                f"{quote(dialect, safe='')}"
            )
            dialect_tag_of[r["ID"]] = token
            dialect_rows.append(
                (
                    token, canonical_id, r["ID"], dialect, base, dialect,
                    r.get("Glottocode") or "", r["Longitude"] or None, r["Latitude"] or None,
                    clade, CLADE_COLORS.get(clade),
                    r.get("Location") or "", r.get("Quality") or "",
                    CLADE_ORDER.index(clade) if clade in CLADE_ORDER else 999,
                    _marker_svg(clade, base),
                )
            )
    con.executemany(
        'INSERT INTO languages (id,name,language,dialect,glottocode,long,lat,clade,color,"order",map_marker)'
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    con.executemany(
        'INSERT INTO dialects (token,language_id,id,name,language,dialect,glottocode,long,lat,'
        'clade,color,location,quality,"order",map_marker) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        dialect_rows,
    )
    con.commit()
    log(f"loaded {len(rows)} canonical languages and {len(dialect_rows)} dialect tags")
    return clade_of, canonical_of, dialect_tag_of


def load_references(con: sqlite3.Connection, path: Path) -> None:
    with path.open(encoding="utf-8") as f:
        rows = [
            (
                r["ID"], r["Short"], r["Source"], r["Progress"],
                r.get("Provenance", ""), r.get("Editor", ""),
                int(r.get("OCR", "").strip().lower() in {"yes", "true", "1"}),
            )
            for r in csv.DictReader(f)
        ]
    con.executemany(
        'INSERT INTO "references" (id,short,source,progress,provenance,editor,ocr) VALUES (?,?,?,?,?,?,?)',
        rows,
    )
    con.commit()
    log(f"loaded {len(rows)} references")


def _parse_ref(src: str) -> list[tuple[str, str]]:
    """``ref1[p. 12];ref2`` → ``[(ref1, p. 12), (ref2, '')]``.

    The bracket is CLDF's source locator. Keep it on the citation edge rather than flattening page
    numbers into Notes. Semicolons inside brackets are treated as locator text, not ref separators.
    """
    if not src:
        return []
    chunks, current, depth = [], [], 0
    for char in src:
        if char == "[":
            depth += 1
        elif char == "]" and depth:
            depth -= 1
        if char == ";" and depth == 0:
            chunks.append("".join(current))
            current = []
        else:
            current.append(char)
    chunks.append("".join(current))
    parsed = set()
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        if "[" in chunk and chunk.endswith("]"):
            reference, locator = chunk.split("[", 1)
            locator = locator[:-1]
        else:
            reference, locator = chunk, ""
        if reference.strip():
            parsed.add((reference.strip(), locator.strip()))
    return sorted(parsed)


def load_lemmas(
    con: sqlite3.Connection,
    forms_csv: Path,
    clade_of: dict[str, str],
    canonical_of: dict[str, str],
    dialect_tag_of: dict[str, str],
) -> dict[str, str]:
    """Build the unified lemmas table from the one CLDF forms.csv (etyma + reflexes). Etyma have an
    empty Origin_ID; reflexes point at their etymon. Sets the self-referential origin_lemma_id, the
    etymon-anchored `order`, tags, per-etymon clade set, and the lemma↔reference links."""
    with forms_csv.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Canonicalise language IDs, attach the dialect tag, then collapse exact cross-dialect copies.
    # References to an earlier duplicate (variants and borrowings) follow the retained row ID.
    aliases: dict[str, str] = {}
    unique: dict[tuple[str, ...], dict[str, str]] = {}
    deduped = []
    ignored = {"ID", "Language_ID", "Tags"}
    for r in rows:
        source_language = r["Language_ID"]
        r["Language_ID"] = canonical_of.get(source_language, source_language)
        dialect_tag = dialect_tag_of.get(source_language)
        base_tags = (r.get("Tags") or "").split()
        tags = list(base_tags)
        if dialect_tag and dialect_tag not in tags:
            tags.append(dialect_tag)
        r["Tags"] = " ".join(tags)
        for field in ("Origin_ID", "Variant_Of", "Borrowed_From"):
            if r.get(field) in aliases:
                r[field] = aliases[r[field]]
        # Etyma are identified by their ID, never merged. Many proto-etyma (e.g. unreconstructed
        # DED / Proto-Indo-Iranian headwords) have a blank Form/Gloss in the source; deduping them
        # on content would collapse thousands into one node and repoint all their reflexes onto it.
        if not r["Origin_ID"]:
            deduped.append(r)
            continue
        key = (r["Language_ID"],) + tuple(
            r.get(k, "") for k in r.keys() if k not in ignored
        ) + tuple(base_tags)
        original = unique.get(key)
        if original is None:
            unique[key] = r
            deduped.append(r)
            continue
        aliases[r["ID"]] = original["ID"]
        merged_tags = list(dict.fromkeys((original.get("Tags") or "").split() + tags))
        original["Tags"] = " ".join(merged_tags)
    rows = deduped
    if aliases:
        for r in rows:
            for field in ("Origin_ID", "Variant_Of", "Borrowed_From"):
                while r.get(field) in aliases:
                    r[field] = aliases[r[field]]
        log(f"collapsed {len(aliases)} identical cross-dialect lemma rows")

    # A canonical-language entry may be represented only by dialect attestations (for example a
    # locally created lemma with forms from three survey sites).  Carry those dialect tokens onto
    # the entry when parent and child are in the same canonical language, so entries-mode dialect
    # filters and the per-language tag inventory describe where the lemma is actually attested.
    by_id = {r["ID"]: r for r in rows}
    for r in rows:
        parent = by_id.get(r.get("Origin_ID") or "")
        if not parent or parent["Language_ID"] != r["Language_ID"]:
            continue
        dialect_tags = [t for t in (r.get("Tags") or "").split() if t.startswith("dialect:")]
        if not dialect_tags:
            continue
        parent_tags = (parent.get("Tags") or "").split()
        parent["Tags"] = " ".join(dict.fromkeys(parent_tags + dialect_tags))

    lemmas = []
    etymon_order: dict[str, int] = {}
    lemma_refs = set()
    # pass 1: etyma (Origin_ID empty) — word=headword, gloss=parsed meaning + tags/native/phonemic
    # folded up from the (dropped) self-reflex, etymology=free-text CDIAL header, notes=Description
    # (Etyma). `order` is sequential in file order (× 1000). Refs come from the folded self-reflex.
    i = 0
    for r in rows:
        if r["Origin_ID"]:
            continue
        etymon_order[r["ID"]] = i * 1000
        # A blank Origin_ID is normally an etymon (relation NULL); a lone (unetymologised) node also
        # has no origin but carries Relation="local" so it stays out of the entries listing.
        lemmas.append(
            (r["ID"], r["Form"], r["Gloss"], r["Native"] or None, r["Phonemic"] or None,
             r["Description"] or "", None, None, i * 1000,
             r["Language_ID"], None, (r["Tags"] or None), (r["Etymology"] or None),
             ("local" if r.get("Relation") == "local" else None),
             (r.get("Redirect") or None), None, None)
        )
        for ref, locator in _parse_ref(r["Source"]):
            lemma_refs.add((r["ID"], ref, locator))
        i += 1

    # pass 2: reflexes, variants, and borrowed entries — origin from Origin_ID (strip
    # borrowing/semi-tatsama markers), order anchored just after their etymon. `relation`
    # distinguishes daughter reflexes from same-language variants; only reflexes feed the entry's
    # clade bar (variants and borrowings are excluded). Borrowed dictionary head entries may still
    # carry their source dictionary's full etymological snippet, so preserve Etymology here too.
    param_cts: dict[str, int] = defaultdict(int)
    param_clades: dict[str, set] = defaultdict(set)
    # etyma orders, extended with each reflex's order as we go, so a borrowed form (whose origin is
    # a source reflex, listed earlier) sorts right after that source rather than at order 0.
    node_order: dict[str, int] = dict(etymon_order)
    for r in rows:
        pid = r["Origin_ID"]
        if not pid:
            continue
        if pid[0] in ">~":
            pid = pid[1:]
        param_cts[pid] += 1
        order = node_order.get(pid, 0) + param_cts[pid]
        node_order[r["ID"]] = order
        lemmas.append(
            (r["ID"], r["Form"], r["Gloss"], r["Native"], r["Phonemic"],
             r["Description"] or "", None, r["Cognateset"], order,
             r["Language_ID"], pid, (r["Tags"] or None), (r["Etymology"] or None),
             (r["Relation"] or None), None,
             (r.get("Variant_Of") or None), (r.get("Borrowed_From") or None))
        )
        cl = clade_of.get(r["Language_ID"])
        if cl and r["Relation"] not in ("variant", "borrowed"):
            param_clades[pid].add(cl)
        for ref, locator in _parse_ref(r["Source"]):
            lemma_refs.add((r["ID"], ref, locator))

    seen_lemma_ids: set[str] = set()
    duplicate_lemma_ids: set[str] = set()
    for lemma in lemmas:
        if lemma[0] in seen_lemma_ids:
            duplicate_lemma_ids.add(lemma[0])
        seen_lemma_ids.add(lemma[0])
    if duplicate_lemma_ids:
        sample = ", ".join(sorted(duplicate_lemma_ids)[:10])
        raise ValueError(f"duplicate lemma IDs after dialect collapsing: {sample}")

    con.executemany(
        'INSERT INTO lemmas (id,word,gloss,native,phonemic,notes,clades,cognateset,'
        '"order",language_id,origin_lemma_id,tags,etymology,relation,redirect_to,variant_of,'
        'borrowed_from) '
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        lemmas,
    )
    con.executemany(
        "UPDATE lemmas SET clades=? WHERE id=?",
        [(",".join(sorted(cs)), pid) for pid, cs in param_clades.items()],
    )
    # References cited by forms but absent from the bibliography still need complete display-safe
    # rows. This is a last-resort guard; make_refs.py normally supplies richer catalog metadata.
    ref_ids = {r[0] for r in con.execute('SELECT id FROM "references"')}
    con.executemany(
        'INSERT OR IGNORE INTO "references" '
        '(id,short,source,progress,provenance,editor,ocr) VALUES (?,?,?,?,?,?,?)',
        [
            (
                m, m, f"Reference abbreviation `{m}`; full citation not yet catalogued.", "No",
                "Automatically discovered in CLDF Source fields", "Aryaman Arora",
                0,
            )
            for m in {ref for _, ref, _ in lemma_refs if ref not in ref_ids}
        ],
    )
    lemma_rowids = {r[0]: r[1] for r in con.execute("SELECT id, rowid FROM lemmas")}
    reference_rowids = {r[0]: r[1] for r in con.execute('SELECT id, rowid FROM "references"')}
    con.executemany(
        "INSERT INTO lemma_reference (lemma_rid,reference_rid,locator) VALUES (?,?,?)",
        (
            (lemma_rowids[lemma], reference_rowids[ref], locator)
            for lemma, ref, locator in lemma_refs
        ),
    )
    con.execute(
        '''UPDATE "references" SET
           lemma_count = (SELECT COUNT(DISTINCT lemma_rid) FROM lemma_reference lr
                          WHERE lr.reference_rid = "references".rowid),
           unetymologised_count = (SELECT COUNT(DISTINCT l.rowid) FROM lemma_reference lr
                                   JOIN lemmas l ON l.rowid = lr.lemma_rid
                                   WHERE lr.reference_rid = "references".rowid
                                     AND l.relation = 'local')'''
    )
    con.execute(
        "UPDATE languages SET lemma_count = "
        "(SELECT COUNT(*) FROM lemmas WHERE lemmas.language_id = languages.id)"
    )
    dialect_counts: dict[str, int] = defaultdict(int)
    dialect_entry_counts: dict[str, int] = defaultdict(int)
    loan_sources = {r["Origin_ID"] for r in rows if r.get("Relation") == "borrowed"}
    for r in rows:
        for tag in (r.get("Tags") or "").split():
            if tag.startswith("dialect:"):
                dialect_counts[tag] += 1
                if not r["Origin_ID"] or r["ID"] in loan_sources:
                    dialect_entry_counts[tag] += 1
    con.executemany(
        "UPDATE dialects SET lemma_count=?, entry_count=? WHERE token=?",
        (
            (count, dialect_entry_counts.get(token, 0), token)
            for token, count in dialect_counts.items()
        ),
    )
    con.commit()
    log(f"loaded {len(lemmas)} lemmas, {len(lemma_refs)} lemma↔reference links")
    return aliases


def load_lemma_aliases(
    con: sqlite3.Connection, cldf: Path, build_aliases: dict[str, str]
) -> dict[str, str]:
    """Merge durable migration aliases with aliases created by dialect deduplication."""
    aliases: dict[str, str] = {}
    path = cldf / "form-id-aliases.csv"
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            aliases.update(
                (row["Legacy_ID"], row["Form_ID"])
                for row in csv.DictReader(handle)
                if row.get("Legacy_ID") and row.get("Form_ID")
            )
    aliases.update(build_aliases)
    lemma_rowids = {row[0]: row[1] for row in con.execute("SELECT id,rowid FROM lemmas")}
    resolved: list[tuple[str, str]] = []
    for alias, target in aliases.items():
        seen = {alias}
        while target in aliases and target not in seen:
            seen.add(target)
            target = aliases[target]
        if alias != target and target in lemma_rowids:
            resolved.append((alias, target))
    con.executemany(
        "INSERT OR REPLACE INTO lemma_aliases (alias,lemma_rid) VALUES (?,?)",
        ((alias, lemma_rowids[target]) for alias, target in resolved),
    )
    con.commit()
    log(f"loaded {len(resolved):,} permanent lemma ID aliases")
    return {alias: target for alias, target in resolved}


def load_concepts(con: sqlite3.Connection, cldf: Path, aliases: dict[str, str]) -> None:
    """Load Concepticon concepts (concepts.py output) and form→concept links, remapping form ids
    through the cross-dialect alias map and rolling up per-concept counts. An 'etymon' of a linked
    form is its immediate origin_lemma_id (or the entry itself); lone/unetymologised nodes
    (relation='local') don't count as etyma — they're tallied in unetym_count instead."""
    concepts_csv, links_csv = cldf / "concepts.csv", cldf / "form_concepts.csv"
    if not concepts_csv.exists() or not links_csv.exists():
        log(f"(no concepts.csv/form_concepts.csv at {cldf}; skipping concepts)")
        return
    with concepts_csv.open(encoding="utf-8") as f:
        con.executemany(
            "INSERT INTO concepts (id,name,category) VALUES (?,?,?)",
            [(int(r["ID"]), r["Name"], r["Category"]) for r in csv.DictReader(f) if r["ID"].isdigit()],
        )
    rowid_of = {r[1]: r[0] for r in con.execute("SELECT rowid, id FROM lemmas")}
    seen: set[tuple[int, int]] = set()
    with links_csv.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            fid, cid = r["Form_ID"], r["Concept_ID"]
            while fid in aliases:
                fid = aliases[fid]
            rid = rowid_of.get(fid)
            if rid is not None and cid.isdigit():
                seen.add((int(cid), rid))
    con.executemany("INSERT INTO lemma_concept (concept_id,lemma_rid) VALUES (?,?)", sorted(seen))
    con.execute(
        """
        UPDATE concepts SET
          form_count  = (SELECT COUNT(*) FROM lemma_concept lc JOIN lemmas l ON l.rowid=lc.lemma_rid
                           WHERE lc.concept_id=concepts.id),
          lang_count  = (SELECT COUNT(DISTINCT l.language_id) FROM lemma_concept lc JOIN lemmas l ON l.rowid=lc.lemma_rid
                           WHERE lc.concept_id=concepts.id),
          etyma_count = (SELECT COUNT(DISTINCT COALESCE(NULLIF(l.origin_lemma_id,''), l.id))
                           FROM lemma_concept lc JOIN lemmas l ON l.rowid=lc.lemma_rid
                           WHERE lc.concept_id=concepts.id AND l.relation IS NOT 'local'),
          unetym_count= (SELECT COUNT(*) FROM lemma_concept lc JOIN lemmas l ON l.rowid=lc.lemma_rid
                           WHERE lc.concept_id=concepts.id AND l.relation = 'local')
        """
    )
    con.commit()
    log(f"loaded {len(seen)} concept links across "
        f"{con.execute('SELECT COUNT(*) FROM concepts').fetchone()[0]} concepts")


def load_derivation(con: sqlite3.Connection, deriv_csv: Path, aliases: dict[str, str]) -> None:
    """Load the derivation graph (derived-term → ancestor etymon) into a `derivation` table, indexed
    both directions. Child ids can be reflexes (alternate-etymology edges), so remap through the
    cross-dialect alias map — promoted-form / etymon ids are untouched by it."""
    con.executescript(
        """
        DROP TABLE IF EXISTS derivation;
        CREATE TABLE derivation (child_id TEXT, parent_id TEXT);
        """
    )

    def canon(i: str) -> str:
        while i in aliases:
            i = aliases[i]
        return i

    with deriv_csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        con.executemany(
            "INSERT INTO derivation (child_id, parent_id) VALUES (?, ?)",
            ((canon(r["Child_ID"]), canon(r["Parent_ID"])) for r in reader),
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


def load_alignments(con: sqlite3.Connection, path: Path, aliases: dict[str, str]) -> None:
    """Load alignment CSV rows into dictionary-coded alignment and correspondence tables."""
    import csv

    lemma_rowids = {row[0]: row[1] for row in con.execute("SELECT id, rowid FROM lemmas")}
    symbols: dict[str, int] = {}
    pairs: dict[tuple[int, int, int], int] = {}
    contexts: dict[tuple[int, int], int] = {}

    def intern(mapping, value):
        if value not in mapping:
            mapping[value] = len(mapping) + 1
        return mapping[value]

    con.executescript(
        """
        CREATE TABLE symbols (id INTEGER PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE align_pair (
            id INTEGER PRIMARY KEY,
            etymon_sid INTEGER NOT NULL,
            reflex_sid INTEGER NOT NULL,
            change_sid INTEGER NOT NULL
        );
        CREATE TABLE align_context (
            id INTEGER PRIMARY KEY,
            prev_sid INTEGER NOT NULL,
            next_sid INTEGER NOT NULL
        );
        DROP TABLE IF EXISTS alignment;
        CREATE TABLE alignment (
            form_rid INTEGER NOT NULL,
            pos INTEGER NOT NULL,
            pair_id INTEGER NOT NULL,
            context_id INTEGER NOT NULL,
            PRIMARY KEY (form_rid, pos)
        ) WITHOUT ROWID;
        """
    )
    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        skipped = 0

        def rows():
            nonlocal skipped
            for r in reader:
                form_id = aliases.get(r[0], r[0])
                if len(r) < 9 or form_id not in lemma_rowids:
                    skipped += 1
                    continue
                etymon_sid = intern(symbols, r[4])
                reflex_sid = intern(symbols, r[5])
                change_sid = intern(symbols, r[6])
                prev_sid = intern(symbols, r[7])
                next_sid = intern(symbols, r[8])
                yield (
                    lemma_rowids[form_id],
                    int(r[2]),
                    intern(pairs, (etymon_sid, reflex_sid, change_sid)),
                    intern(contexts, (prev_sid, next_sid)),
                )

        con.executemany(
            "INSERT OR IGNORE INTO alignment VALUES (?,?,?,?)",
            rows(),
        )
    con.executemany(
        "INSERT INTO symbols(id,value) VALUES (?,?)",
        ((sid, value) for value, sid in symbols.items()),
    )
    con.executemany(
        "INSERT INTO align_pair(id,etymon_sid,reflex_sid,change_sid) VALUES (?,?,?,?)",
        ((pid, *value) for value, pid in pairs.items()),
    )
    con.executemany(
        "INSERT INTO align_context(id,prev_sid,next_sid) VALUES (?,?,?)",
        ((cid, *value) for value, cid in contexts.items()),
    )
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM alignment").fetchone()[0]
    log(f"loaded alignment table: {n} aligned segments from {path}"
        f" ({skipped} unreachable rows skipped)")

    # Aggregate a compact, queryable correspondence summary for the Sound Correspondence explorer:
    # per (proto family, reflex clade, etymon segment, reflex segment, change) → count + example.
    # Collapses ~1.5M alignment rows into a few tens of thousands, so the explorer reads a small
    # indexed table instead of scanning the alignment.
    con.executescript(
        """
        -- Language-level, environment-conditioned rows. Textual language and example IDs are
        -- represented by their source-table rowids and recovered with joins at query time.
        DROP TABLE IF EXISTS corr_lang;
        CREATE TABLE corr_lang (
            proto_rid INTEGER NOT NULL,
            lang_rid INTEGER NOT NULL,
            etymon_sid INTEGER NOT NULL,
            pair_id INTEGER NOT NULL,
            context_id INTEGER NOT NULL,
            n INTEGER NOT NULL,
            example_rid INTEGER NOT NULL,
            PRIMARY KEY (proto_rid, etymon_sid, pair_id, lang_rid, context_id)
        ) WITHOUT ROWID;
        INSERT INTO corr_lang
        WITH grouped AS (
            SELECT pl.rowid AS proto_rid, rl.rowid AS lang_rid,
                   p.etymon_sid, a.pair_id, a.context_id,
                   COUNT(*) AS n, MIN(rf.id) AS example_id
            FROM alignment a
            JOIN align_pair p  ON p.id = a.pair_id
            JOIN symbols es    ON es.id = p.etymon_sid
            JOIN lemmas rf     ON rf.rowid = a.form_rid
            JOIN lemmas e      ON e.id = rf.origin_lemma_id
            JOIN languages pl  ON pl.id = e.language_id
            JOIN languages rl  ON rl.id = rf.language_id
            WHERE es.value <> ''
            GROUP BY pl.rowid, rl.rowid, p.etymon_sid, a.pair_id, a.context_id
        )
        SELECT g.proto_rid, g.lang_rid, g.etymon_sid, g.pair_id, g.context_id,
               g.n, ex.rowid
        FROM grouped g JOIN lemmas ex ON ex.id = g.example_id;

        -- Precomputed clade roll-up keeps the default correspondence view instantaneous. It uses
        -- the same compact row references and WITHOUT ROWID layout rather than duplicating textual
        -- proto/example IDs plus a separate lookup index.
        DROP TABLE IF EXISTS clades;
        CREATE TABLE clades (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        INSERT INTO clades(name) SELECT DISTINCT clade FROM languages ORDER BY clade;
        DROP TABLE IF EXISTS corr;
        CREATE TABLE corr (
            proto_rid INTEGER NOT NULL,
            clade_rid INTEGER NOT NULL,
            etymon_sid INTEGER NOT NULL,
            pair_id INTEGER NOT NULL,
            context_id INTEGER NOT NULL,
            n INTEGER NOT NULL,
            example_rid INTEGER NOT NULL,
            PRIMARY KEY (proto_rid, etymon_sid, clade_rid, pair_id, context_id)
        ) WITHOUT ROWID;
        INSERT INTO corr
        WITH grouped AS (
            SELECT c.proto_rid, d.id AS clade_rid, c.etymon_sid, c.pair_id,
                   c.context_id, SUM(c.n) AS n, MIN(ex.id) AS example_id
            FROM corr_lang c
            JOIN languages l ON l.rowid = c.lang_rid
            JOIN clades d ON d.name = l.clade
            JOIN lemmas ex ON ex.rowid = c.example_rid
            GROUP BY c.proto_rid, d.id, c.etymon_sid, c.pair_id, c.context_id
        )
        SELECT g.proto_rid, g.clade_rid, g.etymon_sid, g.pair_id, g.context_id,
               g.n, ex.rowid
        FROM grouped g JOIN lemmas ex ON ex.id = g.example_id;

        -- tiny per-segment totals (for the segment picker; avoids scanning the big tables)
        DROP TABLE IF EXISTS corr_seg;
        CREATE TABLE corr_seg (
            proto_rid INTEGER NOT NULL,
            etymon_sid INTEGER NOT NULL,
            total INTEGER NOT NULL,
            PRIMARY KEY (proto_rid, etymon_sid)
        ) WITHOUT ROWID;
        INSERT INTO corr_seg
        SELECT proto_rid, etymon_sid, SUM(n)
        FROM corr_lang GROUP BY proto_rid, etymon_sid;
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

    # 1. Build the base tables directly from the CLDF dataset (../data) — the frozen data.db and
    #    neojambu's builder are no longer in the loop; ../data is the single source of truth.
    build_base_schema(con)
    clade_of, canonical_of, dialect_tag_of = load_languages(con, cldf / "languages.csv")
    load_references(con, cldf / "references.csv")
    build_aliases = load_lemmas(
        con, cldf / "forms.csv", clade_of, canonical_of, dialect_tag_of
    )
    aliases = load_lemma_aliases(con, cldf, build_aliases)

    # 2. Indexes: keep the lookup and hot-path ordering indexes. Deliberately omit broad secondary
    # indexes for global lemma order, reverse citation lookup, derivation edges, and the two entry
    # count sorts. Their queries retain explicit WHERE / ORDER BY clauses and therefore return the
    # same rows without these indexes; SQLite scans only a compact link table or sorts the small
    # entry set for those less common views. The omitted indexes save ~9 MB in the shipped DB.
    # The composite language/order index also serves language-only lookups through its leftmost
    # prefix, so a separate language index would duplicate the same keys.
    con.executescript(
        """
        CREATE INDEX idx_lemmas_origin_lemma_id ON lemmas(origin_lemma_id);
        CREATE INDEX idx_lemmas_language_order   ON lemmas(language_id, "order");
        -- partial index for the Entries list (headwords): ORDER BY "order" with no temp sort.
        -- Lone (unetymologised) nodes have an empty origin but Relation='local'; keep them out.
        CREATE INDEX idx_entries_order ON lemmas("order") WHERE origin_lemma_id IS NULL AND relation IS NOT 'local';
        """
    )
    log("created compact lemma lookup + hot-path ordering indexes")

    # 3. Derivation graph (derived-term → ancestor etymon).
    deriv = cldf / "derivation.csv"
    if deriv.exists():
        load_derivation(con, deriv, aliases)
    else:
        log(f"(no derivation.csv at {deriv}; skipping derivation graph)")

    # 3b. Concepticon concept sets mapped from glosses (../data/concepts.py output).
    load_concepts(con, cldf, aliases)


    # 3. Precomputed totals so the client never issues a full-table COUNT(*) (a whole-index scan
    #     is many range requests over the wire; these are 1-row lookups instead).
    con.executescript(
        """
        DROP TABLE IF EXISTS meta;
        CREATE TABLE meta (key TEXT PRIMARY KEY, value INTEGER);
        INSERT INTO meta VALUES
            ('total_lemmas',   (SELECT COUNT(*) FROM lemmas)),
            ('total_lexicon',  (SELECT COUNT(*) FROM lemmas WHERE redirect_to IS NULL)),
            ('total_entries',  (SELECT COUNT(*) FROM lemmas WHERE origin_lemma_id IS NULL AND redirect_to IS NULL AND relation IS NOT 'local')),
            ('total_reflexes', (SELECT COUNT(*) FROM lemmas WHERE relation = 'reflex')),
            ('total_variants', (SELECT COUNT(*) FROM lemmas WHERE relation = 'variant'));
        """
    )
    log("wrote meta counts: " + str(con.execute('SELECT key, value FROM meta').fetchall()))

    # 3b2. Materialise per-entry aggregates (reflex + distinct-language counts) so the Entries
    #      list can show and SORT by them. Partial indexes give sort-without-scan on the headwords.
    con.executescript(
        """
        UPDATE lemmas SET
            reflex_count = (SELECT COUNT(*) FROM lemmas r
                            WHERE r.origin_lemma_id = lemmas.id AND r.relation = 'reflex'),
            lang_count   = (SELECT COUNT(DISTINCT r.language_id) FROM lemmas r
                            WHERE r.origin_lemma_id = lemmas.id AND r.relation = 'reflex')
        WHERE origin_lemma_id IS NULL AND relation IS NOT 'local';
        """
    )
    con.commit()
    log("materialised per-entry reflex_count / lang_count")

    # 3c. Materialised etymon→reflex sound-change alignments (computed in ../data by align.py).
    #     A normalised, queryable table: one row per aligned segment. Powers the descent-tree +
    #     sound-change view and corpus-wide correspondence queries.
    alignments = cldf / "alignments.csv"
    if alignments.exists():
        load_alignments(con, alignments, aliases)
    else:
        log(f"(no alignments file at {alignments}; skipping sound-change table)")

    # 4. Analyse and compact the file for range-friendly layout.
    con.execute("ANALYZE")
    con.commit()
    log(f"setting page_size={page_size} and VACUUMing (this rewrites the file)…")
    con.execute(f"PRAGMA page_size={page_size}")
    con.execute("VACUUM")
    con.commit()

    # Sanity: the scan-based substring search must return rows.
    probe = con.execute(
        "SELECT COUNT(*) FROM lemmas WHERE instr(lower(word), ?) > 0", ("amb",)
    ).fetchone()[0]
    log(f"sanity: substring 'word:amb' -> {probe} lemmas")

    con.close()
    output_bytes = out.stat().st_size
    if output_bytes >= MAX_OUTPUT_BYTES:
        raise RuntimeError(
            f"database size regression: {output_bytes / 1e6:.1f} MB "
            f"(must remain below {MAX_OUTPUT_BYTES / 1e6:.0f} MB)"
        )
    log(f"done: {out} ({output_bytes / 1e6:.1f} MB)")


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
