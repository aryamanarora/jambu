#!/usr/bin/env python3
"""Print compact comparative panels from the read-only inventory cache."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("entries", nargs="+")
parser.add_argument("--max-forms", type=int, default=8)
parser.add_argument("--ids", action="store_true")
args = parser.parse_args()
sets = json.loads(Path(__file__).with_name("sets.json").read_text())
for eid in args.entries:
    if eid not in sets:
        print(eid, "NOT IN TELUGU-ANCHORED CACHE")
        continue
    s = sets[eid]
    print(f"\n{eid} DISPLAY HEAD {s['head']['Form']} [{s['head_audit'].get('Strategy')}]")
    grouped = defaultdict(list)
    for r in s["forms"]:
        grouped[r["Language_ID"]].append(r)
    for lang in ["Tamil", "Malayalam", "Kota", "Toda", "Kannada", "Kodagu", "Tulu",
                 "Telugu", "Gondi", "Konda", "Kui", "Kuwi", "Pengo", "Manda",
                 "Kolami", "Naikri", "Naiki", "Parji", "Ollari", "Gadaba",
                 "Kurux", "Malto", "Brahui", "PDr", "PSTDr", "PSD1", "PSD2", "PCDr"]:
        rows = grouped[lang]
        if not rows:
            continue
        unique = {}
        for r in rows:
            unique.setdefault((r["Form"], r["Gloss"]), r)
        parts = []
        for r in list(unique.values())[:args.max_forms]:
            detail = f"{r['Form']} ‘{r['Gloss'][:100]}’"
            if args.ids:
                detail += f" [{r['ID']}; {r['Source']}]"
            parts.append(detail)
        extra = len(unique) - args.max_forms
        print(lang + ": " + "; ".join(parts) + (f" … +{extra}" if extra > 0 else ""))
