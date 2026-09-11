#!/usr/bin/env python3
"""Inspect a numbered slice of cluster candidates; never classify them automatically."""
import argparse
import csv
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("start", type=int, nargs="?", default=0)
parser.add_argument("count", type=int, nargs="?", default=20)
args = parser.parse_args()
here = Path(__file__).resolve().parent
sets = json.loads((here / "sets.json").read_text())
with (here / "candidate-records.tsv").open() as f:
    candidates = list(csv.DictReader(f, delimiter="\t"))
ids = sorted({r["Entry_ID"] for r in candidates if "initial-cluster" in r["Flags"]},
             key=lambda x: int(re.search(r"\d+", x)[0]))
for index, eid in enumerate(ids[args.start:args.start + args.count], args.start):
    s = sets[eid]
    print(f"\n{index}: {eid} {s['head']['Form']}")
    cluster = dict.fromkeys(r["Word"] + " ‘" + r["Gloss"][:80] + "’"
                            for r in candidates if r["Entry_ID"] == eid and
                            "initial-cluster" in r["Flags"])
    print("Telugu clusters:", "; ".join(cluster))
    for lang in ["Tamil", "Kannada", "Tulu", "Gondi", "Konda", "Kui", "Kuwi", "PDr"]:
        rows = list(dict.fromkeys(r["Form"] + " ‘" + r["Gloss"][:55] + "’"
                                 for r in s["forms"] if r["Language_ID"] == lang))
        if rows:
            print(lang + ": " + "; ".join(rows[:3]))
