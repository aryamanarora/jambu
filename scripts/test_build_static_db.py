import csv
import io
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_static_db


FIELDS = [
    "ID", "Language_ID", "Form", "Gloss", "Native", "Phonemic", "Original",
    "Cognateset", "Description", "Tags", "Source", "Etymology", "Redirect", "Status",
]


class UnlinkedDialectDedupTest(unittest.TestCase):
    def test_database_size_regression_is_only_a_warning(self):
        output = io.StringIO()
        with redirect_stdout(output):
            warned = build_static_db.warn_if_database_large(
                build_static_db.OUTPUT_SIZE_WARNING_BYTES
            )
        self.assertTrue(warned)
        self.assertIn("WARNING: database size regression", output.getvalue())

    def test_external_entry_text_supplements_distinct_legacy_prose(self):
        con = sqlite3.connect(":memory:")
        build_static_db.build_base_schema(con)
        con.executemany(
            'INSERT INTO "references" (id,short,source,progress,provenance,editor,ocr) '
            "VALUES (?,?,?,'Full','','',0)",
            [("legacy", "Legacy", "Legacy"), ("external", "External", "External",)],
        )
        con.execute("UPDATE \"references\" SET ocr=1 WHERE id='external'")
        rows = [
            {
                "ID": "entry", "Language_ID": "language", "Form": "*aka", "Gloss": "one",
                "Native": "", "Phonemic": "", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "", "Source": "legacy[p. 1]",
                "Etymology": "Legacy dictionary prose.", "Redirect": "", "Status": "entry",
            },
            {
                "ID": "deduplicated", "Language_ID": "language", "Form": "*iki",
                "Gloss": "two", "Native": "", "Phonemic": "", "Original": "",
                "Cognateset": "", "Description": "", "Tags": "", "Source": "legacy[p. 2]",
                "Etymology": "Already explicit.", "Redirect": "", "Status": "entry",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            forms = directory / "forms.csv"
            with forms.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            with (directory / "entry-texts.csv").open(
                "w", encoding="utf-8", newline=""
            ) as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["Form_ID", "Position", "Kind", "Format", "Content", "Source"],
                )
                writer.writeheader()
                writer.writerows([
                    {
                        "Form_ID": "entry", "Position": "300001", "Kind": "etymology",
                        "Format": "text", "Content": "External source prose.",
                        "Source": "external[p. 9]",
                    },
                    {
                        "Form_ID": "deduplicated", "Position": "0", "Kind": "etymology",
                        "Format": "text", "Content": "Already explicit.",
                        "Source": "legacy[p. 2]",
                    },
                ])
            build_static_db.load_lemmas(con, forms, [], {"language": "Other"})

        entry_texts = con.execute(
            "SELECT pos,content FROM lemma_text WHERE lemma_rid="
            "(SELECT rowid FROM lemmas WHERE id='entry') ORDER BY pos"
        ).fetchall()
        self.assertEqual(
            entry_texts,
            [(0, "Legacy dictionary prose."), (300001, "External source prose.")],
        )
        self.assertEqual(
            con.execute(
                "SELECT COUNT(*) FROM lemma_text WHERE lemma_rid="
                "(SELECT rowid FROM lemmas WHERE id='deduplicated')"
            ).fetchone()[0],
            1,
        )
        # A prose block may be OCR-derived without making the owning dictionary headword OCR.
        self.assertEqual(
            con.execute(
                "SELECT COUNT(*) FROM lemma_reference lr JOIN \"references\" r "
                "ON r.rowid=lr.reference_rid WHERE lr.lemma_rid="
                "(SELECT rowid FROM lemmas WHERE id='entry') AND r.ocr=1"
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            con.execute(
                "SELECT lemma_count FROM \"references\" WHERE id='external'"
            ).fetchone()[0],
            1,
        )

    def test_identical_text_blocks_coalesce_when_linked_forms_are_aliased(self):
        con = sqlite3.connect(":memory:")
        build_static_db.build_base_schema(con)
        con.execute(
            'INSERT INTO "references" (id,short,source,progress,provenance,editor,ocr) '
            "VALUES ('nured','NurED','NurED','Full','','',0)"
        )
        rows = [
            {
                "ID": "entry", "Language_ID": "Indo-Aryan", "Form": "*kura",
                "Gloss": "hoof", "Native": "", "Phonemic": "", "Original": "",
                "Cognateset": "", "Description": "", "Tags": "", "Source": "",
                "Etymology": "", "Redirect": "", "Status": "entry",
            },
            *[
                {
                    "ID": form_id, "Language_ID": "PNur", "Form": "*kur", "Gloss": "",
                    "Native": "", "Phonemic": "", "Original": "", "Cognateset": "",
                    "Description": "", "Tags": "", "Source": "", "Etymology": "",
                    "Redirect": "", "Status": "",
                }
                for form_id in ("pnur-a", "pnur-b")
            ],
        ]
        edges = [
            {
                "Child_ID": form_id, "Parent_ID": "entry", "Kind": "borrowed", "Rank": "1",
                "Pos": "", "Source": "", "Note": "",
            }
            for form_id in ("pnur-a", "pnur-b")
        ]
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            forms = directory / "forms.csv"
            with forms.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            with (directory / "entry-texts.csv").open(
                "w", encoding="utf-8", newline=""
            ) as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["Form_ID", "Position", "Kind", "Format", "Content", "Source"],
                )
                writer.writeheader()
                for form_id in ("pnur-a", "pnur-b"):
                    writer.writerow({
                        "Form_ID": form_id, "Position": "101435", "Kind": "etymology",
                        "Format": "html", "Content": "<p>Same commentary.</p>",
                        "Source": "nured[page 1435]",
                    })
            aliases = build_static_db.load_lemmas(
                con, forms, edges, {"Indo-Aryan": "Indo-Aryan", "PNur": "Nuristani"}
            )

        self.assertEqual(aliases, {"pnur-b": "pnur-a"})
        self.assertEqual(con.execute("SELECT COUNT(*) FROM lemma_text").fetchone()[0], 1)

    def test_explicit_dialect_registry_loads_without_name_parsing(self):
        con = sqlite3.connect(":memory:")
        build_static_db.build_base_schema(con)
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            with (directory / "languages.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "ID", "Name", "Glottocode", "Latitude", "Longitude", "Clade",
                    "Location", "Quality",
                ])
                writer.writeheader()
                writer.writerow({"ID": "palula", "Name": "Palula", "Clade": "Shinaic"})
            with (directory / "dialects.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "ID", "Tag", "Language_ID", "Source_Language_ID", "Name", "Glottocode",
                    "Latitude", "Longitude", "Clade", "Location", "Quality",
                ])
                writer.writeheader()
                writer.writerow({
                    "ID": "biori", "Tag": "dialect:palula:biori:Biori",
                    "Language_ID": "palula", "Source_Language_ID": "biori", "Name": "Biori",
                    "Glottocode": "nort2667", "Latitude": "35.46", "Longitude": "71.81",
                    "Clade": "Shinaic", "Location": "Biori", "Quality": "A",
                })
            clades = build_static_db.load_languages(
                con, directory / "languages.csv", directory / "dialects.csv"
            )

        self.assertEqual(clades, {"palula": "Shinaic"})
        self.assertEqual(con.execute("SELECT name FROM languages").fetchone()[0], "Palula")
        self.assertEqual(
            con.execute("SELECT token,language_id,name FROM dialects").fetchone(),
            ("dialect:palula:biori:Biori", "palula", "Biori"),
        )

    def test_unlinked_copies_merge_but_keep_dialects_citations_and_alias(self):
        con = sqlite3.connect(":memory:")
        build_static_db.build_base_schema(con)
        con.execute(
            'INSERT INTO "references" (id,short,source,progress,provenance,editor,ocr) '
            "VALUES ('survey','Survey','Survey','Full','','',0)"
        )
        rows = [
            {
                "ID": "entry-a", "Language_ID": "language", "Form": "", "Gloss": "",
                "Native": "", "Phonemic": "", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "", "Source": "", "Etymology": "",
                "Redirect": "", "Status": "entry",
            },
            {
                "ID": "entry-b", "Language_ID": "language", "Form": "", "Gloss": "",
                "Native": "", "Phonemic": "", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "", "Source": "", "Etymology": "",
                "Redirect": "", "Status": "entry",
            },
            {
                "ID": "form-a", "Language_ID": "language", "Form": "aka", "Gloss": "one",
                "Native": "", "Phonemic": "aka", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "num dialect:language:lect-a:A", "Source": "survey[form a-1]",
                "Etymology": "", "Redirect": "", "Status": "unlinked",
            },
            {
                "ID": "form-b", "Language_ID": "language", "Form": "aka", "Gloss": "one",
                "Native": "", "Phonemic": "aka", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "num dialect:language:lect-b:B", "Source": "survey[form b-1]",
                "Etymology": "", "Redirect": "", "Status": "unlinked",
            },
            {
                "ID": "form-a-homonym", "Language_ID": "language", "Form": "aka",
                "Gloss": "one", "Native": "", "Phonemic": "aka", "Original": "",
                "Cognateset": "", "Description": "", "Tags": "num dialect:language:lect-a:A",
                "Source": "survey[form a-2]", "Etymology": "", "Redirect": "",
                "Status": "unlinked",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            forms = Path(directory) / "forms.csv"
            with forms.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            aliases = build_static_db.load_lemmas(
                con,
                forms,
                [],
                {"language": "Other"},
            )

        self.assertEqual(aliases, {"form-b": "form-a"})
        # Same-lect duplicates remain distinct because they may be homonyms; only the copy in the
        # other lect is folded into the first record.
        self.assertEqual(con.execute("SELECT COUNT(*) FROM lemmas").fetchone()[0], 4)
        tags = con.execute("SELECT tags FROM lemmas WHERE id='form-a'").fetchone()[0].split()
        self.assertEqual(
            set(tags),
            {"num", "dialect:language:lect-a:A", "dialect:language:lect-b:B"},
        )
        citations = con.execute(
            'SELECT locator FROM lemma_reference JOIN "references" '
            'ON reference_rid="references".rowid WHERE lemma_rid='
            "(SELECT rowid FROM lemmas WHERE id='form-a') ORDER BY locator"
        ).fetchall()
        self.assertEqual(citations, [("form a-1",), ("form b-1",)])

    def test_linked_copies_merge_and_union_reference_locators(self):
        con = sqlite3.connect(":memory:")
        build_static_db.build_base_schema(con)
        con.executemany(
            'INSERT INTO "references" (id,short,source,progress,provenance,editor,ocr) '
            "VALUES (?,?,?,'Full','','',0)",
            [
                ("dictionary", "Dictionary", "Dictionary"),
                ("survey", "Survey", "Survey"),
            ],
        )
        rows = [
            {
                "ID": "entry", "Language_ID": "language", "Form": "*aka", "Gloss": "one",
                "Native": "", "Phonemic": "", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "", "Source": "", "Etymology": "",
                "Redirect": "", "Status": "entry",
            },
            {
                "ID": "form-a", "Language_ID": "language", "Form": "aka", "Gloss": "one",
                "Native": "", "Phonemic": "aka", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "", "Source": "dictionary[p. 10]", "Etymology": "",
                "Redirect": "", "Status": "",
            },
            {
                "ID": "form-b", "Language_ID": "language", "Form": "aka", "Gloss": "one",
                "Native": "", "Phonemic": "aka", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "", "Source": "dictionary[p. 12];survey[p. 9]", "Etymology": "",
                "Redirect": "", "Status": "",
            },
        ]
        edges = [
            {
                "Child_ID": form_id, "Parent_ID": "entry", "Kind": "reflex", "Rank": "1",
                "Pos": "", "Source": "", "Note": "",
            }
            for form_id in ("form-a", "form-b")
        ]
        with tempfile.TemporaryDirectory() as directory:
            forms = Path(directory) / "forms.csv"
            with forms.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            aliases = build_static_db.load_lemmas(
                con,
                forms,
                edges,
                {"language": "Other"},
            )

        self.assertEqual(aliases, {"form-b": "form-a"})
        self.assertEqual(con.execute("SELECT COUNT(*) FROM lemmas").fetchone()[0], 2)
        citations = con.execute(
            'SELECT "references".id, locator FROM lemma_reference JOIN "references" '
            'ON reference_rid="references".rowid WHERE lemma_rid='
            "(SELECT rowid FROM lemmas WHERE id='form-a') ORDER BY \"references\".id, locator"
        ).fetchall()
        self.assertEqual(
            citations,
            [("dictionary", "p. 10"), ("dictionary", "p. 12"), ("survey", "p. 9")],
        )

    def test_source_defined_reconstruction_records_do_not_merge(self):
        con = sqlite3.connect(":memory:")
        build_static_db.build_base_schema(con)
        con.execute(
            'INSERT INTO "references" (id,short,source,progress,provenance,editor,ocr) '
            "VALUES ('merriam2026dravidiandb','M2026','Database','Partial','','',0)"
        )
        rows = [
            {
                "ID": "entry", "Language_ID": "language", "Form": "*aka", "Gloss": "one",
                "Native": "", "Phonemic": "", "Original": "", "Cognateset": "",
                "Description": "", "Tags": "", "Source": "", "Etymology": "",
                "Redirect": "", "Status": "entry",
            },
            *[
                {
                    "ID": f"record-{record}", "Language_ID": "language", "Form": "*aka",
                    "Gloss": "one", "Native": "", "Phonemic": "", "Original": "aka",
                    "Cognateset": "", "Description": "", "Tags": "",
                    "Source": f"merriam2026dravidiandb[record {record}, DEDR 1]",
                    "Etymology": "", "Redirect": "", "Status": "",
                }
                for record in (1, 2)
            ],
        ]
        edges = [
            {
                "Child_ID": f"record-{record}", "Parent_ID": "entry", "Kind": "reflex",
                "Rank": "1", "Pos": "", "Source": "", "Note": "",
            }
            for record in (1, 2)
        ]
        with tempfile.TemporaryDirectory() as directory:
            forms = Path(directory) / "forms.csv"
            with forms.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            aliases = build_static_db.load_lemmas(con, forms, edges, {"language": "Other"})

        self.assertEqual(aliases, {})
        self.assertEqual(con.execute("SELECT COUNT(*) FROM lemmas").fetchone()[0], 3)

    def test_cross_family_comparisons_load_as_source_attributed_article_links(self):
        con = sqlite3.connect(":memory:")
        build_static_db.build_base_schema(con)
        con.execute(
            'INSERT INTO "references" (id,short,source,progress,provenance,editor,ocr) '
            "VALUES ('dedr','DEDR','Dictionary','Full','','',0)"
        )
        con.executemany(
            "INSERT INTO lemmas (id,word,gloss,language_id,relation) VALUES (?,?,?,?,?)",
            [
                ("d50", "*aṭ-", "to wander", "PDr", None),
                ("1347", "aṭati", "wanders", "Indo-Aryan", None),
            ],
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comparisons.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "ID", "Entry_ID", "Compared_Entry_ID", "Relation", "Direction",
                        "Confidence", "Source", "Evidence",
                    ],
                )
                writer.writeheader()
                writer.writerow({
                    "ID": "dedr:d50:cdial:1347", "Entry_ID": "d50",
                    "Compared_Entry_ID": "1347", "Relation": "loan",
                    "Direction": "entry-from-compared", "Confidence": "medium",
                    "Source": "dedr[entry 50]", "Evidence": "Probably < IA.",
                })
            build_static_db.load_comparisons(con, Path(directory), {})

        row = con.execute(
            'SELECT c.id,e.id,o.id,c.relation,c.direction,c.confidence,r.id,c.locator,c.evidence '
            'FROM comparisons c JOIN lemmas e ON e.rowid=c.entry_rid '
            'JOIN lemmas o ON o.rowid=c.compared_rid '
            'JOIN "references" r ON r.rowid=c.reference_rid'
        ).fetchone()
        self.assertEqual(
            row,
            (
                "dedr:d50:cdial:1347", "d50", "1347", "loan", "entry-from-compared",
                "medium", "dedr", "entry 50", "Probably < IA.",
            ),
        )


if __name__ == "__main__":
    unittest.main()
