import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_static_db


FIELDS = [
    "ID", "Language_ID", "Form", "Gloss", "Native", "Phonemic", "Original",
    "Cognateset", "Description", "Tags", "Source", "Etymology", "Redirect", "Status",
]


class UnlinkedDialectDedupTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
