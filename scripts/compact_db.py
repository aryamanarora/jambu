#!/usr/bin/env python3
"""
compact_db.py — second-phase schema compaction for the static Jambu DB.

build_static_db.py first constructs the legacy ("v1") browser schema exactly as before; this
module then rewrites it into the compact ("v2") schema that actually ships. Keeping the phases
separate means the v1 generation logic (dedup, aliases, tag folding, corr summaries) stays
untouched and the compaction is a pure, verifiable transformation.

v2 schema (mirrored by src/lib/dbShared.ts — the two codecs MUST stay in sync):

  lem            base lemma table. rowid = rank of the binary-encoded lemma id (so the sorted
                 id array doubles as both the id→rowid search structure and the rowid→id map).
                 Text ids, tag strings, cognateset labels, relation strings, citation links and
                 the origin/language indexes are all replaced by integer refs, bit flags and
                 varint blobs. link_rid holds redirect_to on relation-none rows and variant_of
                 on variant/borrowed rows (verified mutually exclusive); counts packs
                 reflex_count*1024 + lang_count on entry rows.
  ids            one row; concatenation of the 376k sorted fixed-width (10-byte) id records.
  ids_misc       rank → id text for the handful of ids the fixed-width codec can't express.
  tagsets        rowid → the distinct `tags` strings (lem.tagset_rid).
  cogsets        rowid → the distinct cognateset labels (lem.cogset_rid).
  cites          rowid → (reference_rid, locator): the distinct citation edges (lem.cites blob).
  aliases        legacy-id redirects, grouped: prefix → blob of (ΔM varint, lemma rowid varint)
                 pairs sorted by M, where the alias is "<prefix>-<M>".
  aliases_misc   alias → lemma rowid for aliases that don't fit the "<prefix>-<M>" shape.
  alignment      form_rid (rowid) → varint cell-id blob, one varint per aligned segment in
                 position order.  cells rowid → (pair_id, context_id).
  corr_lang2     (proto_rid, etymon_sid, lang_rid) → blob of (cell_id, n, example_rid) varints;
                 replaces both corr and corr_lang (clade rollups are aggregated at query time).
  concepts.rids  varint-delta blob of linked lemma rowids (replaces lemma_concept).
  languages.lex  per-language lemma rowids in display ("order") order (replaces the
                 (language_id, "order") index).
  derivation     same edges, integer child_rid/parent_rid.

lem.flags bit layout: bits 0-2 relation (0 etymon/none, 1 reflex, 2 variant, 3 borrowed,
4 local); bit 3 cites an OCR source; bit 4 CDIAL section-form id; bit 5 loan source (has a
borrowed child).
"""
from __future__ import annotations

import re
import sqlite3
from collections import defaultdict

F_ALPHABET = "234567abcdefghijklmnopqrstuvwxyz"
F_INDEX = {c: i for i, c in enumerate(F_ALPHABET)}

TAG_NUM, TAG_NM, TAG_NUML, TAG_D, TAG_F, TAG_MISC = 1, 2, 3, 4, 5, 6

RELATION_CODE = {None: 0, "": 0, "reflex": 1, "variant": 2, "borrowed": 3, "local": 4}
FLAG_OCR = 8
FLAG_SECTION = 16
FLAG_LOAN_SOURCE = 32

_NUM = re.compile(r"0|[1-9]\d*")


def log(msg: str) -> None:
    print(f"[compact_db] {msg}", flush=True)


# ── varints ──────────────────────────────────────────────────────────────────


def put_varint(out: bytearray, n: int) -> None:
    assert n >= 0
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return


def varints(values) -> bytes:
    out = bytearray()
    for v in values:
        put_varint(out, v)
    return bytes(out)


# ── id codec ─────────────────────────────────────────────────────────────────


def encode_id(id_: str, misc_index: dict[str, int]) -> bytes:
    """10-byte record; byte order over records defines the canonical rowid ranking."""
    if id_.startswith("f_") and len(id_) == 15:
        body = id_[2:]
        if all(c in F_INDEX for c in body):
            n = 0
            for c in body:
                n = (n << 5) | F_INDEX[c]
            return bytes([TAG_F]) + n.to_bytes(9, "big")
    if _NUM.fullmatch(id_):
        return bytes([TAG_NUM]) + int(id_).to_bytes(9, "big")
    m = re.fullmatch(r"(0|[1-9]\d*)-(0|[1-9]\d*)", id_)
    if m and int(m.group(1)) < 2**32 and int(m.group(2)) < 2**32:
        return (
            bytes([TAG_NM])
            + int(m.group(1)).to_bytes(4, "big")
            + int(m.group(2)).to_bytes(4, "big")
            + b"\x00"
        )
    m = re.fullmatch(r"(0|[1-9]\d*)([a-z])", id_)
    if m:
        return bytes([TAG_NUML]) + int(m.group(1)).to_bytes(8, "big") + m.group(2).encode()
    m = re.fullmatch(r"d(0|[1-9]\d*)", id_)
    if m:
        return bytes([TAG_D]) + int(m.group(1)).to_bytes(9, "big")
    if id_ not in misc_index:
        misc_index[id_] = len(misc_index)
    return bytes([TAG_MISC]) + misc_index[id_].to_bytes(9, "big")


def decode_id(rec: bytes, misc: list[str]) -> str:
    tag, payload = rec[0], rec[1:]
    if tag == TAG_F:
        n = int.from_bytes(payload, "big")
        chars = []
        for _ in range(13):
            chars.append(F_ALPHABET[n & 31])
            n >>= 5
        return "f_" + "".join(reversed(chars))
    if tag == TAG_NUM:
        return str(int.from_bytes(payload, "big"))
    if tag == TAG_NM:
        return f"{int.from_bytes(payload[:4], 'big')}-{int.from_bytes(payload[4:8], 'big')}"
    if tag == TAG_NUML:
        return str(int.from_bytes(payload[:8], "big")) + chr(payload[8])
    if tag == TAG_D:
        return "d" + str(int.from_bytes(payload, "big"))
    if tag == TAG_MISC:
        return misc[int.from_bytes(payload, "big")]
    raise ValueError(f"bad id record tag {tag}")


# ── notes trimming (user-approved: OCR page provenance moves into the citation) ──────────────

SHACKLE_NOTE = re.compile(r"^Shackle PDF p\. (\d+) \(printed p\. ([^)]*)\);?\s*(.*)$", re.S)
PAGE_JUNK = re.compile(r"\s*<div id=\"display_toggle\">.*$", re.S)


def trim_ocr_notes(con: sqlite3.Connection) -> None:
    """Move 'Shackle PDF p. X (printed p. Y)' provenance out of notes into the citation locator
    (RefList renders locators inline), and strip scraped page-navigation HTML from notes."""
    shackle_rid = con.execute(
        "SELECT rowid FROM \"references\" WHERE id = 'shackle-auto'"
    ).fetchone()
    moved = junk = 0
    if shackle_rid:
        shackle_rid = shackle_rid[0]
        rows = con.execute(
            """SELECT l.rowid, l.notes, lr.locator FROM lemmas l
               JOIN lemma_reference lr ON lr.lemma_rid = l.rowid
               WHERE lr.reference_rid = ? AND l.notes LIKE 'Shackle PDF p.%'""",
            (shackle_rid,),
        ).fetchall()
        for rid, notes, locator in rows:
            m = SHACKLE_NOTE.match(notes)
            if not m:
                continue
            pdf, printed, rest = m.group(1), m.group(2).strip(), m.group(3).strip()
            new_locator = f"p. {printed} (PDF p. {pdf})" if printed else f"PDF p. {pdf}"
            con.execute("UPDATE lemmas SET notes = ? WHERE rowid = ?", (rest, rid))
            if not locator:
                # PK includes locator, so this is a delete+insert rather than an UPDATE.
                con.execute(
                    "DELETE FROM lemma_reference WHERE lemma_rid=? AND reference_rid=? AND locator=''",
                    (rid, shackle_rid),
                )
                con.execute(
                    "INSERT OR IGNORE INTO lemma_reference (lemma_rid,reference_rid,locator) VALUES (?,?,?)",
                    (rid, shackle_rid, new_locator),
                )
            moved += 1
    for rid, notes in con.execute(
        "SELECT rowid, notes FROM lemmas WHERE notes LIKE '%display_toggle%'"
    ).fetchall():
        con.execute(
            "UPDATE lemmas SET notes = ? WHERE rowid = ?", (PAGE_JUNK.sub("", notes).strip(), rid)
        )
        junk += 1
    con.commit()
    log(f"OCR notes: moved {moved} shackle page locators, stripped {junk} page-nav HTML blocks")


# ── main compaction ──────────────────────────────────────────────────────────


def compact(con: sqlite3.Connection, clade_order: list[str]) -> None:
    trim_ocr_notes(con)

    # 1. id codec: encode every lemma id, sort, rank → new rowid.
    old = con.execute(
        'SELECT rowid, id, word, gloss, native, phonemic, notes, clades, cognateset, "order", '
        "language_id, origin_lemma_id, tags, reflex_count, lang_count, etymology, relation, "
        "redirect_to, variant_of FROM lemmas"
    ).fetchall()
    misc_index: dict[str, int] = {}
    encoded = [(encode_id(r[1], misc_index), r) for r in old]
    encoded.sort(key=lambda e: e[0])
    recs = [e[0] for e in encoded]
    assert len(set(recs)) == len(recs), "id codec collision"
    new_rowid_of_old = {e[1][0]: i + 1 for i, e in enumerate(encoded)}
    new_rowid_of_id = {e[1][1]: i + 1 for i, e in enumerate(encoded)}
    log(f"encoded {len(recs)} ids ({len(misc_index)} in misc table)")

    lang_rowid = {r[1]: r[0] for r in con.execute("SELECT rowid, id FROM languages")}
    # Mask alphabet: the canonical order plus any clades the data has grown that the build
    # script's constant doesn't know yet (e.g. "Early NIA") — never silently drop one.
    seen_clades: set[str] = set()
    for (clades,) in con.execute(
        "SELECT DISTINCT clades FROM lemmas WHERE clades IS NOT NULL AND clades != ''"
    ):
        seen_clades.update(clades.split(","))
    mask_alphabet = list(clade_order) + sorted(seen_clades - set(clade_order))
    assert len(mask_alphabet) <= 63, "clade mask exceeds 63 bits"
    clade_bit = {c: 1 << i for i, c in enumerate(mask_alphabet)}

    # 2. interning tables.
    tag_texts = sorted(
        t for (t,) in con.execute("SELECT DISTINCT tags FROM lemmas WHERE tags IS NOT NULL AND tags != ''")
    )
    tagset_rid = {t: i + 1 for i, t in enumerate(tag_texts)}
    cog_texts = sorted(
        c
        for (c,) in con.execute(
            "SELECT DISTINCT cognateset FROM lemmas WHERE cognateset IS NOT NULL AND cognateset != ''"
        )
    )
    cogset_rid = {c: i + 1 for i, c in enumerate(cog_texts)}
    cite_keys = sorted(
        (ref, loc)
        for ref, loc in con.execute("SELECT DISTINCT reference_rid, locator FROM lemma_reference")
    )
    cite_rid = {k: i + 1 for i, k in enumerate(cite_keys)}

    cites_of: dict[int, list[int]] = defaultdict(list)  # old lemma rowid → sorted cite ids
    for lemma_rid, ref_rid, loc in con.execute(
        "SELECT lemma_rid, reference_rid, locator FROM lemma_reference"
    ):
        cites_of[lemma_rid].append(cite_rid[(ref_rid, loc)])
    for v in cites_of.values():
        v.sort()
    ocr_refs = {r[0] for r in con.execute('SELECT rowid FROM "references" WHERE ocr = 1')}
    ocr_cites = {cite_rid[k] for k in cite_keys if k[0] in ocr_refs}

    # 3. relationship prep on old rowids.
    #    borrowed_from was verified to always equal origin_lemma_id, so it is dropped entirely.
    children_of: dict[int, list[tuple[int, int]]] = defaultdict(list)  # (child ord, child new rowid)
    loan_sources: set[str] = set()
    for old_rowid, origin_id, relation, order in con.execute(
        "SELECT rowid, origin_lemma_id, relation, \"order\" FROM lemmas WHERE origin_lemma_id IS NOT NULL"
    ):
        children_of[origin_id].append((order, old_rowid, new_rowid_of_old[old_rowid]))
        if relation == "borrowed":
            loan_sources.add(origin_id)

    # 4. dense display order (ties broken by insertion order, deterministically).
    order_rank: dict[int, int] = {}
    for i, (_, old_rowid) in enumerate(
        sorted((r[9], r[0]) for r in old)
    ):
        order_rank[old_rowid] = i + 1

    # 5. build lem rows.
    section_re = re.compile(r"[0-9].*-[0-9].*")
    lem_rows = []
    unresolved_refs = 0
    for rec, r in encoded:
        (old_rowid, id_, word, gloss, native, phonemic, notes, clades, cognateset, _order,
         language_id, origin_id, tags, reflex_count, lang_count, etymology, relation,
         redirect_to, variant_of) = r
        flags = RELATION_CODE.get(relation, 0)
        cites = cites_of.get(old_rowid)
        if cites and any(c in ocr_cites for c in cites):
            flags |= FLAG_OCR
        if section_re.fullmatch(id_):
            flags |= FLAG_SECTION
        if id_ in loan_sources:
            flags |= FLAG_LOAN_SOURCE
        mask = 0
        if clades:
            for c in clades.split(","):
                mask |= clade_bit.get(c, 0)
        kids = children_of.get(id_)
        kids_blob = None
        if kids:
            kids.sort()
            kids_blob = varints(k[2] for k in kids)
        origin_rid = new_rowid_of_id.get(origin_id) if origin_id else None
        # redirect_to occurs only on relation-none rows, variant_of only on variant/borrowed
        # rows (verified), so one link column disambiguated by the relation code suffices.
        link_id = variant_of or redirect_to
        assert not (variant_of and redirect_to), f"row {id_} has both variant_of and redirect_to"
        link_rid = new_rowid_of_id.get(link_id) if link_id else None
        if (origin_id and origin_rid is None) or (link_id and link_rid is None):
            unresolved_refs += 1
        counts = None
        if reflex_count is not None or lang_count is not None:
            assert (lang_count or 0) < 1024
            counts = (reflex_count or 0) * 1024 + (lang_count or 0)
        lem_rows.append(
            (
                new_rowid_of_old[old_rowid], word, gloss, native, phonemic, notes or None,
                etymology, order_rank[old_rowid], lang_rowid.get(language_id), origin_rid,
                link_rid,
                tagset_rid.get(tags) if tags else None,
                cogset_rid.get(cognateset) if cognateset else None,
                mask or None, counts, flags,
                varints(cites) if cites else None, kids_blob,
            )
        )
    if unresolved_refs:
        log(f"WARNING: {unresolved_refs} rows had unresolvable origin/variant/redirect targets")
    orphan_langs = {r[10] for r in old if r[10] and r[10] not in lang_rowid}
    if orphan_langs:
        log(f"WARNING: language ids missing from languages table (rows keep NULL language): "
            f"{sorted(orphan_langs)}")

    con.executescript(
        """
        CREATE TABLE lem (
            word TEXT, gloss TEXT, native TEXT, phonemic TEXT, notes TEXT, etymology TEXT,
            ord INTEGER, lang_rid INTEGER, origin_rid INTEGER, link_rid INTEGER,
            tagset_rid INTEGER, cogset_rid INTEGER, clades_mask INTEGER,
            counts INTEGER, flags INTEGER NOT NULL,
            cites BLOB, children BLOB
        );
        CREATE TABLE ids (data BLOB NOT NULL);
        CREATE TABLE ids_misc (rank INTEGER PRIMARY KEY, id TEXT NOT NULL);
        -- bit i-1 of lem.clades_mask ↔ mask_clades rowid i (the client must use THIS alphabet,
        -- not its own CLADE_ORDER constant, which can drift from the build's).
        CREATE TABLE mask_clades (name TEXT NOT NULL);
        CREATE TABLE tagsets (txt TEXT NOT NULL);
        CREATE TABLE cogsets (txt TEXT NOT NULL);
        CREATE TABLE cites (ref_rid INTEGER NOT NULL, locator TEXT NOT NULL);
        """
    )
    con.executemany(
        "INSERT INTO lem (rowid, word, gloss, native, phonemic, notes, etymology, ord, lang_rid,"
        " origin_rid, link_rid, tagset_rid, cogset_rid, clades_mask, counts, flags, cites, children)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        lem_rows,
    )
    con.execute("INSERT INTO ids (data) VALUES (?)", (b"".join(recs),))
    con.executemany(
        "INSERT INTO ids_misc (rank, id) VALUES (?,?)",
        [(rank, id_) for id_, rank in misc_index.items()],
    )
    con.executemany(
        "INSERT INTO mask_clades (rowid, name) VALUES (?,?)",
        [(i + 1, c) for i, c in enumerate(mask_alphabet)],
    )
    con.executemany("INSERT INTO tagsets (rowid, txt) VALUES (?,?)", [(i + 1, t) for i, t in enumerate(tag_texts)])
    con.executemany("INSERT INTO cogsets (rowid, txt) VALUES (?,?)", [(i + 1, c) for i, c in enumerate(cog_texts)])
    con.executemany(
        "INSERT INTO cites (rowid, ref_rid, locator) VALUES (?,?,?)",
        [(i + 1, k[0], k[1]) for i, k in enumerate(cite_keys)],
    )
    log(f"built lem ({len(lem_rows)} rows), {len(tag_texts)} tagsets, {len(cog_texts)} cogsets, "
        f"{len(cite_keys)} citation edges")

    # 6. per-language display-order lists (replaces the (language_id, "order") index).
    lex_of: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row in lem_rows:
        new_rowid, ord_, lang_rid_ = row[0], row[7], row[8]
        if lang_rid_ is not None:
            lex_of[lang_rid_].append((ord_, new_rowid))
    con.execute("ALTER TABLE languages ADD COLUMN lex BLOB")
    con.executemany(
        "UPDATE languages SET lex = ? WHERE rowid = ?",
        [(varints(rid for _, rid in sorted(v)), lang) for lang, v in lex_of.items()],
    )

    # 7. aliases → grouped blobs.
    groups: dict[str, list[tuple[int, int]]] = defaultdict(list)
    misc_aliases: list[tuple[str, int]] = []
    n_aliases = 0
    for alias, lemma_rid in con.execute("SELECT alias, lemma_rid FROM lemma_aliases"):
        n_aliases += 1
        new_rid = new_rowid_of_old[lemma_rid]
        if "-" in alias:
            prefix, m = alias.rsplit("-", 1)
            if _NUM.fullmatch(m):
                groups[prefix].append((int(m), new_rid))
                continue
        misc_aliases.append((alias, new_rid))
    con.executescript(
        """
        CREATE TABLE aliases (prefix TEXT PRIMARY KEY, data BLOB NOT NULL) WITHOUT ROWID;
        CREATE TABLE aliases_misc (alias TEXT PRIMARY KEY, lemma_rid INTEGER NOT NULL) WITHOUT ROWID;
        """
    )
    alias_rows = []
    for prefix, pairs in groups.items():
        pairs.sort()
        out = bytearray()
        prev_m = 0
        for m, rid in pairs:
            put_varint(out, m - prev_m)
            put_varint(out, rid)
            prev_m = m
        alias_rows.append((prefix, bytes(out)))
    con.executemany("INSERT INTO aliases (prefix, data) VALUES (?,?)", alias_rows)
    con.executemany("INSERT INTO aliases_misc (alias, lemma_rid) VALUES (?,?)", misc_aliases)
    log(f"packed {n_aliases} aliases into {len(alias_rows)} groups (+{len(misc_aliases)} misc)")

    # 8. concept links → per-concept sorted delta blobs.
    concept_rids: dict[int, list[int]] = defaultdict(list)
    for concept_id, lemma_rid in con.execute("SELECT concept_id, lemma_rid FROM lemma_concept"):
        concept_rids[concept_id].append(new_rowid_of_old[lemma_rid])
    con.execute("ALTER TABLE concepts ADD COLUMN rids BLOB")
    updates = []
    for cid, rids in concept_rids.items():
        rids.sort()
        out = bytearray()
        prev = 0
        for rid in rids:
            put_varint(out, rid - prev)
            prev = rid
        updates.append((bytes(out), cid))
    con.executemany("UPDATE concepts SET rids = ? WHERE id = ?", updates)

    # 9. derivation → integer edges (row order preserved: getEntryGraph orders by rowid).
    deriv = [
        (new_rowid_of_id.get(c), new_rowid_of_id.get(p))
        for c, p in con.execute("SELECT child_id, parent_id FROM derivation ORDER BY rowid")
    ]
    dropped = sum(1 for c, p in deriv if c is None or p is None)
    con.execute("DROP TABLE derivation")
    con.execute("CREATE TABLE derivation (child_rid INTEGER NOT NULL, parent_rid INTEGER NOT NULL)")
    con.executemany(
        "INSERT INTO derivation (child_rid, parent_rid) VALUES (?,?)",
        [e for e in deriv if e[0] is not None and e[1] is not None],
    )
    if dropped:
        log(f"WARNING: dropped {dropped} derivation edges with unresolvable endpoints")

    # 10. alignment → per-form cell blobs.
    if con.execute("SELECT 1 FROM sqlite_master WHERE name='alignment'").fetchone():
        # Cell ids are assigned by descending corpus frequency so the hottest cells get 1-byte
        # varints in the per-form blobs (ties broken by (pair, context) for determinism).
        freq: dict[tuple[int, int], int] = defaultdict(int)
        raw = con.execute("SELECT form_rid, pos, pair_id, context_id FROM alignment").fetchall()
        for _, _, pair_id, context_id in raw:
            freq[(pair_id, context_id)] += 1
        cell_keys = sorted(freq, key=lambda k: (-freq[k], k))
        cell_id = {k: i + 1 for i, k in enumerate(cell_keys)}
        segs_of: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for form_rid, pos, pair_id, context_id in raw:
            segs_of[form_rid].append((pos, cell_id[(pair_id, context_id)]))
        con.execute("DROP TABLE alignment")
        # single-blob cell dictionary: (pair_id, context_id) varint pairs in cell-id order,
        # loaded once by the client (it needs the whole table in JS for blob decoding anyway).
        cells_blob = bytearray()
        for p, c in cell_keys:
            put_varint(cells_blob, p)
            put_varint(cells_blob, c)
        con.execute("CREATE TABLE cells (data BLOB NOT NULL)")
        con.execute("INSERT INTO cells (data) VALUES (?)", (bytes(cells_blob),))
        con.execute("CREATE TABLE alignment (form_rid INTEGER PRIMARY KEY, segs BLOB NOT NULL)")
        align_rows = []
        for form_rid, segs in segs_of.items():
            segs.sort()
            assert segs[0][0] == 0 and segs[-1][0] == len(segs) - 1, "non-contiguous pos"
            align_rows.append((new_rowid_of_old[form_rid], varints(s[1] for s in segs)))
        con.executemany("INSERT INTO alignment (form_rid, segs) VALUES (?,?)", align_rows)
        log(f"packed alignment: {len(align_rows)} forms, {len(cell_keys)} distinct cells")

        # 11. corr_lang → grouped blobs; corr (the clade rollup) is recomputed at query time.
        con.execute(
            """CREATE TABLE corr_lang2 (
                 proto_rid INTEGER NOT NULL, etymon_sid INTEGER NOT NULL, lang_rid INTEGER NOT NULL,
                 data BLOB NOT NULL, PRIMARY KEY (proto_rid, etymon_sid, lang_rid)
               ) WITHOUT ROWID"""
        )
        cl_groups: dict[tuple[int, int, int], list[tuple[int, int, int]]] = defaultdict(list)
        for proto_rid, lang_rid_, etymon_sid, pair_id, context_id, n, example_rid in con.execute(
            "SELECT proto_rid, lang_rid, etymon_sid, pair_id, context_id, n, example_rid FROM corr_lang"
        ):
            cl_groups[(proto_rid, etymon_sid, lang_rid_)].append(
                (cell_id[(pair_id, context_id)], n, new_rowid_of_old[example_rid])
            )
        cl_rows = []
        for key, cells_list in cl_groups.items():
            cells_list.sort()
            out = bytearray()
            for cid, n, ex in cells_list:
                put_varint(out, cid)
                put_varint(out, n)
                put_varint(out, ex)
            cl_rows.append((*key, bytes(out)))
        con.executemany(
            "INSERT INTO corr_lang2 (proto_rid, etymon_sid, lang_rid, data) VALUES (?,?,?,?)",
            cl_rows,
        )
        con.execute("DROP TABLE corr")
        con.execute("DROP TABLE corr_lang")
        con.execute("DROP TABLE clades")
        log(f"packed corr_lang into {len(cl_rows)} groups; dropped corr/clades rollups")

    # 12. retire the v1 tables and build the one remaining index.
    con.executescript(
        """
        DROP TABLE lemmas;
        DROP TABLE lemma_reference;
        DROP TABLE lemma_aliases;
        DROP TABLE lemma_concept;
        CREATE INDEX idx_entries_ord ON lem(ord) WHERE origin_rid IS NULL AND (flags & 7) != 4;
        """
    )
    con.commit()
    log("compaction complete")
