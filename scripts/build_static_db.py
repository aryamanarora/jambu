#!/usr/bin/env python3
"""
build_static_db.py — transform the raw Jambu SQLite DB into a static, browser-queryable form.

The raw data.db (published as a GitHub release asset on moli-mandala/data) is optimised for a
server with an ORM. For the static GitHub Pages site we query it directly in the browser via
sql.js-httpvfs, so we bake in everything the client needs:

  1. Build compact browser tables directly from the unified CLDF data.
  2. Add the compact set of indexes the client query layer relies on.
  3. ANALYZE + VACUUM so the B-trees are laid out contiguously.

Tiny lookup tables (languages and references) are searched with plain LIKE on
the client — no index needed — so we do not build FTS for them.

Usage:
    python build_static_db.py OUTPUT.db [--cldf ../data/cldf] [--page-size 16384]

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

sys.path.insert(0, str(Path(__file__).parent))
import compact_db


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
# KEWA's 2,575 source-attributed OCR blocks move the compact database baseline to about 80.6 MB.
# Report future growth above this narrow allowance without interrupting an otherwise valid build.
OUTPUT_SIZE_WARNING_BYTES = 83_000_000

# These inputs define independently addressable reconstruction records. Even when two rows have
# identical lexical content and the same parent, their record locators are part of their identity
# and must survive browser compaction as distinct scholarly analyses.
SOURCE_DEFINED_RECORD_REFERENCES = {"merriam2026dravidiandb"}

def log(msg: str) -> None:
    print(f"[build_static_db] {msg}", flush=True)


def warn_if_database_large(output_bytes: int, *, compact: bool = True) -> bool:
    """Report a size regression without turning an otherwise valid database into a failed build."""
    if not compact or output_bytes < OUTPUT_SIZE_WARNING_BYTES:
        return False
    log(
        f"WARNING: database size regression: {output_bytes / 1e6:.1f} MB "
        f"(expected below {OUTPUT_SIZE_WARNING_BYTES / 1e6:.0f} MB)"
    )
    return True


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
            editor TEXT, ocr INTEGER NOT NULL DEFAULT 0, etymology_provenance TEXT,
            lemma_count INTEGER DEFAULT 0,
            unetymologised_count INTEGER DEFAULT 0
        );
        -- CLDF Original is an import-time transliteration source; no display/query path reads it.
        -- The rendered form is word, so omitting Original avoids shipping ~2.1M dead characters.
        -- origin_lemma_id = the rank-1 (accepted) edge target: the actual variant target for
        -- variants, the loan source for borrowed forms. etymon_id = the attestation-tree root.
        -- relation = the rank-1 edge kind, or 'unlinked' for unetymologised imports.
        CREATE TABLE lemmas (
            id TEXT PRIMARY KEY, word TEXT, gloss TEXT, native TEXT, phonemic TEXT,
            notes TEXT, clades TEXT, cognateset TEXT, "order" INTEGER, language_id TEXT,
            origin_lemma_id TEXT, etymon_id TEXT, tags TEXT, reflex_count INTEGER,
            lang_count INTEGER, etymology TEXT, relation TEXT, redirect_to TEXT
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
        -- Ordered, independently attributable prose attached to a lexical node.  Etymology remains
        -- on lemmas as a migration/search cache; entry pages read these blocks instead of parsing
        -- source-specific delimiters out of that scalar field.
        CREATE TABLE lemma_text (
            lemma_rid INTEGER NOT NULL, pos INTEGER NOT NULL, kind TEXT NOT NULL,
            format TEXT NOT NULL, content TEXT NOT NULL, reference_rid INTEGER, locator TEXT,
            PRIMARY KEY (lemma_rid, pos)
        ) WITHOUT ROWID;
        -- Article-to-article comparisons are deliberately separate from the ancestry graph and
        -- ordinary reflex table: the source may compare families without settling loan direction.
        CREATE TABLE comparisons (
            id TEXT PRIMARY KEY, entry_rid INTEGER NOT NULL, compared_rid INTEGER NOT NULL,
            relation TEXT NOT NULL, direction TEXT NOT NULL, confidence TEXT NOT NULL,
            reference_rid INTEGER NOT NULL, locator TEXT NOT NULL, evidence TEXT NOT NULL
        );
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
    con: sqlite3.Connection, path: Path, dialect_path: Path
) -> dict[str, str]:
    """Load explicit base languages and their separately catalogued dialect tags."""
    with path.open(encoding="utf-8") as f:
        language_rows = list(csv.DictReader(f))
    with dialect_path.open(encoding="utf-8") as f:
        source_dialects = list(csv.DictReader(f))

    rows = []
    clade_of = {}
    names = {}
    for r in language_rows:
        if ": " in r["Name"]:
            raise ValueError(f"Colon dialect remains in languages.csv: {r['ID']} {r['Name']}")
        language_id, name, clade = r["ID"], r["Name"], r["Clade"]
        rows.append(
            (
                language_id, name, name, "", r.get("Glottocode") or "",
                r.get("Longitude") or None, r.get("Latitude") or None,
                clade, CLADE_COLORS.get(clade),
                CLADE_ORDER.index(clade) if clade in CLADE_ORDER else 999,
                _marker_svg(clade, name),
            )
        )
        clade_of[language_id] = clade
        names[language_id] = name

    dialect_rows = []
    for r in source_dialects:
        language_id = r["Language_ID"]
        if language_id not in clade_of:
            raise ValueError(f"Unknown dialect parent {language_id!r} for {r['Tag']}")
        clade = r.get("Clade") or clade_of[language_id]
        dialect_rows.append(
            (
                r["Tag"], language_id, r["ID"], r["Name"], names[language_id], r["Name"],
                r.get("Glottocode") or "", r.get("Longitude") or None,
                r.get("Latitude") or None, clade, CLADE_COLORS.get(clade),
                r.get("Location") or "", r.get("Quality") or "",
                CLADE_ORDER.index(clade) if clade in CLADE_ORDER else 999,
                _marker_svg(clade, names[language_id]),
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
    log(f"loaded {len(rows)} languages and {len(dialect_rows)} explicit dialect tags")
    return clade_of


def load_references(con: sqlite3.Connection, path: Path) -> None:
    with path.open(encoding="utf-8") as f:
        rows = [
            (
                r["ID"], r["Short"], r["Source"], r["Progress"],
                r.get("Provenance", ""), r.get("Editor", ""),
                int(r.get("OCR", "").strip().lower() in {"yes", "true", "1"}),
                r.get("Etymology_Provenance", ""),
            )
            for r in csv.DictReader(f)
        ]
    con.executemany(
        'INSERT INTO "references" '
        '(id,short,source,progress,provenance,editor,ocr,etymology_provenance) '
        'VALUES (?,?,?,?,?,?,?,?)',
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


def load_edge_rows(cldf: Path) -> list[dict]:
    with (cldf / "edges.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_lemmas(
    con: sqlite3.Connection,
    forms_csv: Path,
    edge_rows: list[dict],
    clade_of: dict[str, str],
) -> dict[str, str]:
    """Build the unified lemmas table from the edge-model CLDF: forms.csv carries node content
    (+ Status ∈ {entry, unlinked, ''}) and cldf/edges.csv carries the typed graph. Each node's
    accepted parent is its rank-1 reflex/variant/borrowed edge (`origin_lemma_id` — for a
    variant this is its actual target, not the etymon); `etymon_id` is the attestation-tree
    root above it. Sets the parent-anchored `order`, tags, per-etymon clade set, and the
    lemma↔reference links."""
    with forms_csv.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    rank1: dict[str, tuple[str, str]] = {}
    for e in edge_rows:
        if e["Rank"] == "1" and e["Kind"] in ("reflex", "variant", "borrowed"):
            rank1[e["Child_ID"]] = (e["Parent_ID"], e["Kind"])

    # Dialects are already tags in CLDF. Collapse exact attested copies while retaining every
    # dialect tag and citation on the surviving row.
    # The rank-1 edge is part of a linked row's identity (identical text under different parents
    # must never merge). Unlinked attestations use their lexical content as the identity instead;
    # Source is provenance, so merge its citations onto the retained row rather than using it to
    # distinguish otherwise identical forms. Etyma/entries remain identified by ID and never merge.
    aliases: dict[str, str] = {}
    unique: dict[tuple, dict[str, str]] = {}
    unlinked_unique: dict[tuple, list[tuple[dict[str, str], set[str]]]] = defaultdict(list)
    deduped = []
    # Citations describe where an attestation was found; they are not lexical content. Exclude
    # Source from every attested-form identity and union it below when otherwise identical rows
    # collapse. (Parentless entries never reach this deduper.)
    ignored = {"ID", "Language_ID", "Tags", "Source"}
    for r in rows:
        base_tags = (r.get("Tags") or "").split()
        tags = list(base_tags)
        content_tags = [tag for tag in base_tags if not tag.startswith("dialect:")]
        dialect_identity = tuple(sorted(tag for tag in base_tags if tag.startswith("dialect:")))
        source_lect = dialect_identity or (r["Language_ID"],)
        source_defined_record = tuple(
            (reference, locator)
            for reference, locator in _parse_ref(r.get("Source", ""))
            if reference in SOURCE_DEFINED_RECORD_REFERENCES
        )
        # Parentless etyma/entries stay distinct (blank proto heads would otherwise collapse).
        # Unlinked rows are attestations too, despite having no accepted edge.
        is_unlinked = r.get("Status") == "unlinked"
        if r["ID"] not in rank1 and not is_unlinked:
            deduped.append(r)
            continue
        key = (r["Language_ID"],) + tuple(
            r.get(k, "") for k in r.keys() if k not in ignored
        ) + tuple(content_tags) + source_defined_record + (
            ("unlinked",) if is_unlinked else rank1[r["ID"]]
        )
        if is_unlinked:
            # A repeated spelling within one lect may be a genuine homonym or separate lexical
            # record. Merge only when a different source lect normalises to the same language.
            candidates = unlinked_unique[key]
            match = next(
                ((candidate, lects) for candidate, lects in candidates
                 if source_lect not in lects),
                None,
            )
            original, merged_lects = match if match else (None, None)
        else:
            original = unique.get(key)
            merged_lects = None
        if original is None:
            if is_unlinked:
                unlinked_unique[key].append((r, {source_lect}))
            else:
                unique[key] = r
            deduped.append(r)
            continue
        if merged_lects is not None:
            merged_lects.add(source_lect)
        aliases[r["ID"]] = original["ID"]
        merged_tags = list(dict.fromkeys((original.get("Tags") or "").split() + tags))
        original["Tags"] = " ".join(merged_tags)
        # Preserve every source locator on the retained lexical record. _parse_ref understands
        # top-level semicolon separation and keeps semicolons inside CLDF locator brackets intact.
        if r.get("Source"):
            original["Source"] = ";".join(
                part for part in (original.get("Source", ""), r["Source"]) if part
            )
    rows = deduped
    if aliases:
        # Re-point every edge endpoint through the collapse map; a collapsed linked child's own
        # edges drop out (the retained row carries the identical edge, guaranteed by the key).
        def canon(i: str) -> str:
            while i in aliases:
                i = aliases[i]
            return i

        rank1 = {
            child: (canon(parent), kind)
            for child, (parent, kind) in rank1.items()
            if child not in aliases
        }
        for e in edge_rows:
            e["Child_ID"] = canon(e["Child_ID"])
            e["Parent_ID"] = canon(e["Parent_ID"])
        log(f"collapsed {len(aliases)} identical attested lemma rows")

    def canonical_id(node_id: str) -> str:
        while node_id in aliases:
            node_id = aliases[node_id]
        return node_id

    # A canonical-language entry may be represented only by dialect attestations.  Carry those
    # dialect tokens onto the parent when parent and child share the canonical language, so
    # entries-mode dialect filters describe where the lemma is actually attested.
    by_id = {r["ID"]: r for r in rows}
    for r in rows:
        e = rank1.get(r["ID"])
        parent = by_id.get(e[0]) if e else None
        if not parent or parent["Language_ID"] != r["Language_ID"]:
            continue
        dialect_tags = [t for t in (r.get("Tags") or "").split() if t.startswith("dialect:")]
        if not dialect_tags:
            continue
        parent_tags = (parent.get("Tags") or "").split()
        parent["Tags"] = " ".join(dict.fromkeys(parent_tags + dialect_tags))

    def etymon_of(node: str) -> str | None:
        seen = set()
        cur = node
        while cur in rank1 and cur not in seen:
            seen.add(cur)
            cur = rank1[cur][0]
        return None if cur == node else cur

    lemmas = []
    etymon_order: dict[str, int] = {}
    lemma_refs = set()
    # pass 1: parentless nodes (etyma + unlinked) — order sequential in file order (× 1000).
    i = 0
    for r in rows:
        if r["ID"] in rank1:
            continue
        etymon_order[r["ID"]] = i * 1000
        lemmas.append(
            (r["ID"], r["Form"], r["Gloss"], r["Native"] or None, r["Phonemic"] or None,
             r["Description"] or "", None, None, i * 1000,
             r["Language_ID"], None, None, (r["Tags"] or None), (r["Etymology"] or None),
             ("unlinked" if r.get("Status") == "unlinked" else None),
             (r.get("Redirect") or None))
        )
        for ref, locator in _parse_ref(r["Source"]):
            lemma_refs.add((r["ID"], ref, locator))
        i += 1

    # pass 2: attested nodes — order anchored just after their accepted parent (a variant now
    # sorts right after the sibling/parent it varies, a borrowed form after its source).
    param_cts: dict[str, int] = defaultdict(int)
    param_clades: dict[str, set] = defaultdict(set)
    node_order: dict[str, int] = dict(etymon_order)
    for r in rows:
        e = rank1.get(r["ID"])
        if e is None:
            continue
        pid, kind = e
        param_cts[pid] += 1
        order = node_order.get(pid, 0) + param_cts[pid]
        node_order[r["ID"]] = order
        lemmas.append(
            (r["ID"], r["Form"], r["Gloss"], r["Native"], r["Phonemic"],
             r["Description"] or "", None, r["Cognateset"], order,
             r["Language_ID"], pid, etymon_of(r["ID"]), (r["Tags"] or None),
             (r["Etymology"] or None), kind, None)
        )
        cl = clade_of.get(r["Language_ID"])
        if cl and kind == "reflex":
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
        '"order",language_id,origin_lemma_id,etymon_id,tags,etymology,relation,redirect_to) '
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        lemmas,
    )
    con.executemany(
        "UPDATE lemmas SET clades=? WHERE id=?",
        [(",".join(sorted(cs)), pid) for pid, cs in param_clades.items()],
    )
    # A richer importer may provide several independently typed/attributed blocks per node in an
    # optional CLDF sidecar. Its final public Form_IDs are used directly; distinct sidecar rows
    # supplement the legacy Etymology scalar below.
    explicit_texts: list[dict[str, str]] = []
    text_reference_ids: set[str] = set()
    texts_path = forms_csv.parent / "entry-texts.csv"
    if texts_path.exists():
        with texts_path.open(encoding="utf-8") as handle:
            explicit_texts = list(csv.DictReader(handle))
        # A source-side prose file can legitimately lag one durable-ID pass (for example when a
        # generator re-emits its historical ``m1`` identifier after forms.csv has already been
        # assigned ``f_…`` IDs). Resolve the public alias table here, before validating the prose
        # owner, and then apply any same-build dialect-collapse alias. The normal alias loader runs
        # after this function, too late to make the sidecar ownership check safe on its own.
        durable_aliases: dict[str, str] = {}
        durable_alias_path = forms_csv.parent / "form-id-aliases.csv"
        if durable_alias_path.exists():
            with durable_alias_path.open(encoding="utf-8") as handle:
                durable_aliases = {
                    row["Legacy_ID"]: row["Form_ID"]
                    for row in csv.DictReader(handle)
                    if row.get("Legacy_ID") and row.get("Form_ID")
                }

        def resolve_text_owner(form_id: str) -> str:
            original = form_id
            seen: set[str] = set()
            while form_id in durable_aliases and form_id not in seen:
                seen.add(form_id)
                form_id = durable_aliases[form_id]
            resolved = canonical_id(form_id)
            active_original = canonical_id(original)
            # Some dictionary-native identifiers are deliberately restored after an earlier
            # migration assigned an opaque ID; the historical alias row remains for old URLs but
            # its target is then retired. In that case the active original is the prose owner.
            if resolved not in known_lemma_ids and active_original in known_lemma_ids:
                return active_original
            return resolved

        known_lemma_ids = {lemma[0] for lemma in lemmas}
        for block in explicit_texts:
            block["Form_ID"] = resolve_text_owner(block.get("Form_ID", ""))
            if block["Form_ID"] not in known_lemma_ids:
                raise ValueError(
                    f"entry-texts.csv references unknown Form_ID {block['Form_ID']!r}"
                )
            text_reference_ids.update(ref for ref, _ in _parse_ref(block.get("Source", "")))

    # References cited by forms or prose blocks but absent from the bibliography still need
    # complete display-safe rows.
    # rows. This is a last-resort guard; make_refs.py normally supplies richer catalog metadata.
    ref_ids = {r[0] for r in con.execute('SELECT id FROM "references"')}
    con.executemany(
        'INSERT OR IGNORE INTO "references" '
        '(id,short,source,progress,provenance,editor,ocr,etymology_provenance) '
        'VALUES (?,?,?,?,?,?,?,?)',
        [
            (
                m, m, f"Reference abbreviation `{m}`; full citation not yet catalogued.", "No",
                "Automatically discovered in CLDF Source fields", "Aryaman Arora",
                0, "",
            )
            for m in (
                {ref for _, ref, _ in lemma_refs} | text_reference_ids
            ) - ref_ids
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
    source_by_id = {r["ID"]: r.get("Source", "") for r in rows}
    text_rows = []
    # Explicit sidecars supplement legacy dictionary prose.  Historically, the mere presence of
    # an external block (NurED, Southworth, KEWA, …) suppressed the owning CDIAL entry's own
    # etymology.  Skip only a block whose content is already represented explicitly (the Munda
    # compatibility path), and retain every distinct legacy block ahead of high-position sidecars.
    explicit_content_by_owner: dict[str, set[str]] = defaultdict(set)
    for block in explicit_texts:
        explicit_content_by_owner[block["Form_ID"]].add(block.get("Content", "").strip())
    for sequence, block in enumerate(explicit_texts):
        lemma_id = block["Form_ID"]
        if lemma_id not in lemma_rowids:
            raise ValueError(f"entry-texts.csv references unknown Form_ID {lemma_id!r}")
        citations = _parse_ref(block.get("Source", ""))
        ref, locator = citations[0] if citations else (None, "")
        position = int(block.get("Position", "") or sequence)
        kind = (block.get("Kind") or "etymology").strip()
        fmt = (block.get("Format") or "text").strip()
        if fmt not in {"html", "markdown", "text"}:
            raise ValueError(f"unsupported entry-text format {fmt!r} for {lemma_id}")
        content = block.get("Content", "").strip()
        if content:
            text_rows.append(
                (
                    lemma_rowids[lemma_id], position, kind, fmt, content,
                    reference_rowids.get(ref) if ref else None, locator or None,
                )
            )
    for lemma_id, old_rid, etymology in con.execute(
        "SELECT id, rowid, etymology FROM lemmas WHERE etymology IS NOT NULL AND etymology != ''"
    ):
        citations = _parse_ref(source_by_id.get(lemma_id, ""))
        ref, locator = citations[0] if citations else (None, "")
        ref_rid = reference_rowids.get(ref) if ref else None
        # CDIAL addenda historically shared one scalar field with an HTML-comment delimiter.
        # Materialise each snippet as a real block; all other sources naturally produce one block.
        blocks = [b.strip() for b in etymology.split("<!--addendum-->") if b.strip()]
        text_rows.extend(
            (
                old_rid, pos, "etymology",
                "html" if content.lstrip().startswith("<") else "text",
                content, ref_rid, locator or None,
            )
            for pos, content in enumerate(blocks)
            if content not in explicit_content_by_owner.get(lemma_id, set())
        )
    # Dialect/attestation compaction above can alias two source nodes that carry the same
    # independently installed text block (NurED's two PNur *kur siblings are one example).
    # Coalesce that exact duplicate, but keep the position key strict so genuinely conflicting
    # prose can never be discarded silently.
    distinct_text_rows = {}
    for text_row in text_rows:
        key = text_row[:2]
        previous = distinct_text_rows.setdefault(key, text_row)
        if previous != text_row:
            raise ValueError(
                f"conflicting structured text blocks for lemma row {key[0]}, position {key[1]}"
            )
    text_rows = list(distinct_text_rows.values())
    con.executemany(
        "INSERT INTO lemma_text (lemma_rid,pos,kind,format,content,reference_rid,locator) "
        "VALUES (?,?,?,?,?,?,?)",
        text_rows,
    )
    con.execute(
        'UPDATE "references" SET '
        'lemma_count = (SELECT COUNT(*) FROM ('
        ' SELECT lemma_rid FROM lemma_reference lr WHERE lr.reference_rid = "references".rowid'
        ' UNION SELECT lemma_rid FROM lemma_text lt WHERE lt.reference_rid = "references".rowid'
        ')), '
        'unetymologised_count = (SELECT COUNT(*) FROM ('
        ' SELECT lemma_rid FROM lemma_reference lr WHERE lr.reference_rid = "references".rowid'
        ' UNION SELECT lemma_rid FROM lemma_text lt WHERE lt.reference_rid = "references".rowid'
        ") cited JOIN lemmas l ON l.rowid = cited.lemma_rid WHERE l.relation = 'unlinked')"
    )
    con.execute(
        "UPDATE languages SET lemma_count = "
        "(SELECT COUNT(*) FROM lemmas WHERE lemmas.language_id = languages.id)"
    )
    dialect_counts: dict[str, int] = defaultdict(int)
    dialect_entry_counts: dict[str, int] = defaultdict(int)
    loan_sources = {e[0] for e in rank1.values() if e[1] == "borrowed"}
    for r in rows:
        for tag in (r.get("Tags") or "").split():
            if tag.startswith("dialect:"):
                dialect_counts[tag] += 1
                if r["ID"] not in rank1 or r["ID"] in loan_sources:
                    dialect_entry_counts[tag] += 1
    con.executemany(
        "UPDATE dialects SET lemma_count=?, entry_count=? WHERE token=?",
        (
            (count, dialect_entry_counts.get(token, 0), token)
            for token, count in dialect_counts.items()
        ),
    )
    con.commit()
    log(
        f"loaded {len(lemmas)} lemmas, {len(lemma_refs)} lemma↔reference links, "
        f"{len(text_rows)} structured text blocks"
    )
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


def load_comparisons(con: sqlite3.Connection, cldf: Path, aliases: dict[str, str]) -> None:
    """Load validated, source-attributed article comparisons with symmetric query endpoints."""
    path = cldf / "comparisons.csv"
    if not path.exists():
        log(f"(no comparisons.csv at {cldf}; skipping cross-family comparisons)")
        return
    rowid_of = {entry_id: rid for rid, entry_id in con.execute("SELECT rowid,id FROM lemmas")}
    ref_rowid = {ref_id: rid for rid, ref_id in con.execute('SELECT rowid,id FROM "references"')}
    relations = {"loan", "influence", "related"}
    directions = {"entry-from-compared", "compared-from-entry", "undetermined"}
    confidences = {"high", "medium", "low"}
    rows = []
    with path.open(encoding="utf-8", newline="") as fin:
        for source_row in csv.DictReader(fin):
            comparison_id = source_row["ID"]
            entry_id = aliases.get(source_row["Entry_ID"], source_row["Entry_ID"])
            compared_id = aliases.get(
                source_row["Compared_Entry_ID"], source_row["Compared_Entry_ID"]
            )
            if entry_id not in rowid_of or compared_id not in rowid_of:
                raise ValueError(
                    f"Comparison {comparison_id} has missing endpoint(s): {entry_id}, {compared_id}"
                )
            if entry_id == compared_id:
                raise ValueError(f"Comparison {comparison_id} links an entry to itself")
            if source_row["Relation"] not in relations:
                raise ValueError(f"Comparison {comparison_id} has invalid relation")
            if source_row["Direction"] not in directions:
                raise ValueError(f"Comparison {comparison_id} has invalid direction")
            if source_row["Confidence"] not in confidences:
                raise ValueError(f"Comparison {comparison_id} has invalid confidence")
            citations = _parse_ref(source_row["Source"])
            if len(citations) != 1 or citations[0][0] not in ref_rowid:
                raise ValueError(
                    f"Comparison {comparison_id} requires one resolvable source citation: {citations}"
                )
            reference_id, locator = citations[0]
            if not source_row["Evidence"].strip():
                raise ValueError(f"Comparison {comparison_id} lacks printed evidence")
            rows.append(
                (
                    comparison_id,
                    rowid_of[entry_id],
                    rowid_of[compared_id],
                    source_row["Relation"],
                    source_row["Direction"],
                    source_row["Confidence"],
                    ref_rowid[reference_id],
                    locator,
                    source_row["Evidence"],
                )
            )
    con.executemany("INSERT INTO comparisons VALUES (?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    log(f"loaded {len(rows)} cross-family comparisons")


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
                           WHERE lc.concept_id=concepts.id AND l.relation IS NOT 'unlinked'),
          unetym_count= (SELECT COUNT(*) FROM lemma_concept lc JOIN lemmas l ON l.rowid=lc.lemma_rid
                           WHERE lc.concept_id=concepts.id AND l.relation = 'unlinked')
        """
    )
    con.commit()
    log(f"loaded {len(seen)} concept links across "
        f"{con.execute('SELECT COUNT(*) FROM concepts').fetchone()[0]} concepts")


def load_graph_edges(con: sqlite3.Connection, edge_rows: list[dict]) -> None:
    """Ship the non-attestation graph: component/derived edges (the old derivation graph, now
    typed and ordered) plus rank>=2 alternate-etymology hypotheses. Rank-1 attestation edges are
    already materialised on the lemmas rows. Endpoints were canonicalised by load_lemmas."""
    con.executescript(
        """
        DROP TABLE IF EXISTS edges;
        CREATE TABLE edges (
            child_id TEXT NOT NULL, parent_id TEXT NOT NULL, kind TEXT NOT NULL,
            rank INTEGER NOT NULL, pos INTEGER, note TEXT
        );
        """
    )
    known = {r[0] for r in con.execute("SELECT id FROM lemmas")}
    rows = []
    dropped = 0
    for e in edge_rows:
        if e["Kind"] not in ("component", "derived") and e["Rank"] == "1":
            continue  # attestation edges live on the lemma rows
        if e["Child_ID"] not in known or e["Parent_ID"] not in known:
            dropped += 1
            continue
        rows.append((
            e["Child_ID"], e["Parent_ID"], e["Kind"], int(e["Rank"]),
            int(e["Pos"]) if e["Pos"] else None,
            e["Note"] or (e["Source"] or None),
        ))
    con.executemany(
        "INSERT INTO edges (child_id, parent_id, kind, rank, pos, note) VALUES (?,?,?,?,?,?)",
        rows,
    )
    con.commit()
    log(f"loaded typed graph edges: {len(rows)} shipped ({dropped} with unknown endpoints dropped)")


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
    align_origin: dict[int, int] = {}  # form_rid → aligned-origin rowid (corr build only)

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
                origin_id = aliases.get(r[1], r[1])
                if origin_id in lemma_rowids:
                    align_origin[lemma_rowids[form_id]] = lemma_rowids[origin_id]
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
    con.execute("DROP TABLE IF EXISTS align_origin")
    con.execute("CREATE TABLE align_origin (form_rid INTEGER PRIMARY KEY, origin_rid INTEGER NOT NULL)")
    con.executemany("INSERT INTO align_origin VALUES (?,?)", align_origin.items())
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
            JOIN align_origin ao ON ao.form_rid = a.form_rid
            JOIN lemmas e      ON e.rowid = ao.origin_rid
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

        DROP TABLE align_origin;

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
    clade_of = load_languages(con, cldf / "languages.csv", cldf / "dialects.csv")
    load_references(con, cldf / "references.csv")
    edge_rows = load_edge_rows(cldf)
    build_aliases = load_lemmas(con, cldf / "forms.csv", edge_rows, clade_of)
    aliases = load_lemma_aliases(con, cldf, build_aliases)
    load_comparisons(con, cldf, aliases)

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
        -- partial index for the intermediate-schema Entries list. A CDIAL article remains a
        -- dictionary headword after an accepted external ancestry link gives it an origin.
        CREATE INDEX idx_entries_order ON lemmas("order") WHERE
            (origin_lemma_id IS NULL AND relation IS NOT 'unlinked') OR
            (language_id = 'Indo-Aryan' AND etymology IS NOT NULL);
        """
    )
    log("created compact lemma lookup + hot-path ordering indexes")

    # 3. Derivation graph (derived-term → ancestor etymon).
    load_graph_edges(con, edge_rows)

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
            ('total_entries',  (SELECT COUNT(*) FROM lemmas WHERE redirect_to IS NULL AND (
                (origin_lemma_id IS NULL AND relation IS NOT 'unlinked') OR
                (language_id = 'Indo-Aryan' AND etymology IS NOT NULL)
            ))),
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
        WHERE (origin_lemma_id IS NULL AND relation IS NOT 'unlinked') OR
              (language_id = 'Indo-Aryan' AND etymology IS NOT NULL);
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

    # 4. Rewrite the v1 schema into the compact schema that actually ships (see compact_db.py).
    #    JAMBU_SKIP_COMPACT=1 keeps the intermediate v1 schema — used only to produce the OLD.db
    #    side for scripts/parity_check.mjs.
    import os
    if os.environ.get("JAMBU_SKIP_COMPACT"):
        log("JAMBU_SKIP_COMPACT set — emitting the v1 intermediate schema")
    else:
        compact_db.compact(con, CLADE_ORDER)

    # 5. Analyse and compact the file for range-friendly layout.
    con.execute("ANALYZE")
    con.commit()
    log(f"setting page_size={page_size} and VACUUMing (this rewrites the file)…")
    con.execute(f"PRAGMA page_size={page_size}")
    con.execute("VACUUM")
    con.commit()

    # Sanity: the scan-based substring search must return rows.
    probe_table = "lemmas" if os.environ.get("JAMBU_SKIP_COMPACT") else "lem"
    probe = con.execute(
        f"SELECT COUNT(*) FROM {probe_table} WHERE instr(lower(word), ?) > 0", ("amb",)
    ).fetchone()[0]
    log(f"sanity: substring 'word:amb' -> {probe} lemmas")

    con.close()
    output_bytes = out.stat().st_size
    warn_if_database_large(output_bytes, compact=not os.environ.get("JAMBU_SKIP_COMPACT"))
    log(f"done: {out} ({output_bytes / 1e6:.1f} MB)")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build the static-site SQLite DB directly from the CLDF dataset (../data)."
    )
    ap.add_argument("output", type=Path, help="output DB path (e.g. .dbwork/jambu.db)")
    ap.add_argument("--cldf", type=Path, default=Path("../data/cldf"),
                    help="CLDF directory (forms.csv, languages.csv, dialects.csv, references.csv, "
                         "alignments.csv, edges.csv)")
    ap.add_argument("--page-size", type=int, default=16384,
                    help="SQLite page size for the output (default 16384, range-fetch friendly)")
    args = ap.parse_args()

    t0 = time.time()
    transform(args.output, args.page_size, args.cldf)
    log(f"elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
