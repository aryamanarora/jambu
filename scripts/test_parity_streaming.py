"""Reproducible tiny-fixture coverage for the full compact parity checker.

Run: python3 scripts/test_parity_streaming.py
Uses the production compactor and JS codecs. Creates no release database;
all temporary SQLite files are small and stay inside the workspace.
"""
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

import build_static_db
import compact_db

ROOT = Path(__file__).resolve().parents[1]


def make_fixture(directory):
    old = directory / 'old.db'
    new = directory / 'new.db'
    con = sqlite3.connect(old)
    build_static_db.build_base_schema(con)
    con.executescript('''
        INSERT INTO languages(id,name,clade) VALUES
            ('L','Language L','C'),('M','Language M','C');
        INSERT INTO "references"(id,short,source,ocr) VALUES('r','R','Reference',1);
        INSERT INTO lemmas(id,word,gloss,notes,clades,"order",language_id,tags,reflex_count,lang_count)
            VALUES('1','root','root','','C',1,'L','noun',1,1);
        INSERT INTO lemmas(id,word,gloss,notes,clades,"order",language_id,tags,
            origin_lemma_id,etymon_id,relation,cognateset) VALUES
            ('2-1','reflex','reflex','','C',2,'M','noun','1','1','reflex',''),
            ('3','variant','variant','','C',3,'M','noun','2-1','1','variant','');
        INSERT INTO lemma_reference VALUES(1,1,'p.1'),(2,1,'p.2'),(3,1,'p.3');
        INSERT INTO lemma_aliases VALUES('legacy-1',2),('misc',3);
        INSERT INTO concepts(id,name) VALUES(1,'concept');
        INSERT INTO lemma_concept VALUES(1,2);
        INSERT INTO lemma_text VALUES(2,1,'comparison','text','bounded prose',1,'p.2');
        CREATE TABLE edges(child_id TEXT,parent_id TEXT,kind TEXT,rank INTEGER,pos INTEGER,note TEXT);
        INSERT INTO edges VALUES('3','1','derived',1,NULL,'source');
        CREATE TABLE alignment(form_rid INTEGER,pos INTEGER,pair_id INTEGER,context_id INTEGER,
            PRIMARY KEY(form_rid,pos));
        INSERT INTO alignment VALUES(2,0,1,1);
        CREATE TABLE corr_lang(proto_rid INTEGER,etymon_sid INTEGER,lang_rid INTEGER,
            pair_id INTEGER,context_id INTEGER,n INTEGER,example_rid INTEGER,
            PRIMARY KEY(proto_rid,etymon_sid,pair_id,lang_rid,context_id));
        INSERT INTO corr_lang VALUES(1,1,2,1,1,1,2);
        CREATE TABLE clades(id INTEGER PRIMARY KEY,name TEXT);
        INSERT INTO clades VALUES(1,'C');
        CREATE TABLE corr(proto_rid INTEGER,etymon_sid INTEGER,clade_rid INTEGER,
            pair_id INTEGER,context_id INTEGER,n INTEGER,example_rid INTEGER,
            PRIMARY KEY(proto_rid,etymon_sid,clade_rid,pair_id,context_id));
        INSERT INTO corr VALUES(1,1,1,1,1,1,2);
        CREATE TABLE corr_seg(proto_rid INTEGER,etymon_sid INTEGER,n INTEGER);
        CREATE TABLE meta(key TEXT PRIMARY KEY,value INTEGER);
        INSERT INTO meta VALUES('total_entries',1);
        CREATE INDEX idx_entries_order ON lemmas("order") WHERE redirect_to IS NULL AND (
            (origin_lemma_id IS NULL AND relation IS NOT 'unlinked') OR
            (language_id='Indo-Aryan' AND etymology IS NOT NULL));
        CREATE INDEX idx_origin ON lemmas(origin_lemma_id);
        CREATE INDEX idx_lang_order ON lemmas(language_id,"order");
    ''')
    con.commit()
    target = sqlite3.connect(new)
    con.backup(target)
    con.close()
    compact_db.compact(target, ['C'])
    target.close()
    return old, new


class StreamingParityTest(unittest.TestCase):
    def test_production_fixture_and_corruptions(self):
        scratch = ROOT / '.dbwork'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='parity-test-', dir=scratch) as tmp:
            old, new = make_fixture(Path(tmp))
            original = new.read_bytes()

            def check():
                return subprocess.run(
                    ['node', str(ROOT / 'scripts/parity_check.mjs'), str(old), str(new)],
                    cwd=ROOT, capture_output=True, text=True, timeout=30,
                )

            result = check()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('ALL CHECKS PASSED', result.stdout)
            for section in ('id codec', 'hydration', 'citation edges', 'children blobs',
                            'section + loan-source', 'alias resolution', 'alignment blob',
                            'corr_lang2', 'corr clade rollup', 'concept link',
                            'per-language lex', 'typed-edge', 'meta counts',
                            'entries default page', 'per-reference lex', 'structured article-text'):
                self.assertIn(section, result.stdout)
            corruptions = [
                ('hydration', "UPDATE lem SET word='corrupt' WHERE rowid=1", 'field word'),
                ('alias', 'DELETE FROM aliases_misc', 'alias count'),
                ('correspondence', "UPDATE corr_lang2 SET data=x'010903'", 'corr_lang group'),
                ('citation', "UPDATE lem SET cites=x'01' WHERE rowid=2", 'cites mismatch'),
                ('prose', "UPDATE text_contents SET txt='corrupt'", 'structured article text'),
                ('tags', "UPDATE tagsets SET data=x''", 'field tags'),
            ]
            for name, sql, failure in corruptions:
                with self.subTest(name=name):
                    try:
                        con = sqlite3.connect(new)
                        con.execute(sql)
                        con.commit()
                        con.close()
                        result = check()
                        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                        self.assertIn(failure, result.stderr)
                        self.assertNotIn('ALL CHECKS PASSED', result.stdout)
                    finally:
                        new.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
