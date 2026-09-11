#!/usr/bin/env python3
"""Read-only, reproducible inventory of Jambu's DEDR evidence.

Regex flags identify records worth reading; they are not sound-change decisions.
No source tables or graph edges are written. Standard library only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data"
CLDF = DATA / "cldf"
V = "aeiouāēīōū"
R = "rṟlḷẓḻḍṭṯṛ"
C = "kgcjśsṣṭḍtdnpbmvywhñṇŋṅrṟlḷẓḻṯṛ"
TARGET_LANGS = ["Telugu", "Tamil", "Malayalam", "Kannada", "Tulu", "Kota",
               "Toda", "Kodagu", "Gondi", "Konda", "Kui", "Kuwi", "Pengo",
               "Manda", "Kolami", "Naiki", "Parji", "Ollari", "Gadaba",
               "Kurux", "Naikri", "Malto", "Brahui"]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_tsv(name, rows, fields):
    with (HERE / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


def main():
    paths = [CLDF / f"{n}.csv" for n in ["forms", "edges", "languages", "pdr-headword-audit"]]
    paths += [DATA / "data/dedr/pdr.csv"]
    forms = {r["ID"]: r for r in read_csv(paths[0])}
    edges = read_csv(paths[1])
    parent = {r["Child_ID"]: r for r in edges
              if r["Rank"] == "1" and r["Kind"] in {"reflex", "variant", "borrowed"}}
    heads = {r["Parameter_ID"]: r for r in read_csv(paths[3])}

    def dedr_ancestor(fid):
        seen = set()
        while fid and fid not in seen:
            if re.fullmatch(r"d\d+[a-z]?", fid):
                return fid
            seen.add(fid)
            fid = parent.get(fid, {}).get("Parent_ID", "")
        return ""

    grouped = defaultdict(list)
    for fid, r in forms.items():
        if r["Language_ID"] not in TARGET_LANGS and not r["Language_ID"].startswith("P"):
            continue
        eid = dedr_ancestor(fid)
        if eid and fid != eid:
            grouped[eid].append({k: r[k] for k in ["ID", "Language_ID", "Form", "Original",
                "Gloss", "Description", "Tags", "Source"]} | {
                    "Immediate_Parent": parent.get(fid, {}).get("Parent_ID", ""),
                    "Edge_Kind": parent.get(fid, {}).get("Kind", "")})

    all_sets = {}
    candidates = []
    for eid, rows in grouped.items():
        telugu = [r for r in rows if r["Language_ID"] == "Telugu"]
        if not telugu:
            continue
        all_sets[eid] = {"head": forms[eid], "head_audit": heads.get(eid, {}), "forms": rows}
        for r in telugu:
            # CLDF Form expands m(r)ānu into separate mānu and mrānu rows.
            # Original remains available in sets.json for source verification.
            word = unicodedata.normalize("NFC", r["Form"]).strip()
            scan = word.replace("ṛ̆", "ẓ").replace("r̤", "ẓ").lower()
            flags = []
            if re.match(fr"^(?:[{C}])?[{R}][{V}]", scan):
                flags.append("initial-apical-or-cluster")
            if re.match(fr"^[{C}][{R}][{V}]", scan):
                flags.append("initial-cluster")
            if re.match(fr"^(?:[{C}])?[aeiou][{R}][{V}]", scan):
                flags.append("uncontracted-comparison-candidate")
            if flags:
                candidates.append({"Entry_ID": eid, "Form_ID": r["ID"], "Word": word,
                    "Gloss": r["Gloss"], "Flags": ";".join(flags),
                    "Headword": forms[eid]["Form"], "Head_Strategy": heads.get(eid, {}).get("Strategy", ""),
                    "Source": r["Source"], "Tags": r["Tags"]})

    legacy = []
    with paths[-1].open(newline="", encoding="utf-8") as f:
        for n, r in enumerate(csv.reader(f), 1):
            note = r[6]
            if re.search(r"(?:\bSD|\bPSD|\bPCD|\bPND|\bCD\b|\bND\b|PTelugu|Pre-Telugu|PGondi)", note):
                legacy.append({"Row": n, "Language_ID": r[0], "Entry_ID": r[1], "Form": r[2],
                    "Gloss": r[3], "Note": note, "Source": r[7],
                    "Audit": "historical-level-or-distribution-note: requires source review"})

    summary = {
        "inputs": {str(p.relative_to(DATA)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "total_cldf_forms": len(forms), "total_cldf_edges": len(edges),
        "dedr_head_strategies": dict(Counter(r["Strategy"] for r in heads.values())),
        "dedr_sets_with_telugu": len(all_sets),
        "telugu_records_in_those_sets": sum(sum(r["Language_ID"] == "Telugu" for r in s["forms"]) for s in all_sets.values()),
        "candidate_records": len(candidates), "candidate_sets": len({r["Entry_ID"] for r in candidates}),
        "flags": dict(Counter(f for r in candidates for f in r["Flags"].split(";"))),
        "legacy_level_note_flags": len(legacy),
        "legacy_level_note_entries": len({r["Entry_ID"] for r in legacy}),
        "warning": "Candidate flags and level-note flags require manual review; none are error or loan classifications.",
    }
    (HERE / "sets.json").write_text(json.dumps(all_sets, ensure_ascii=False, indent=2) + "\n")
    (HERE / "inventory-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    write_tsv("candidate-records.tsv", candidates, list(candidates[0]))
    write_tsv("legacy-level-flags.tsv", legacy, list(legacy[0]))
    print(json.dumps({k: v for k, v in summary.items() if k != "inputs"}, indent=2))


if __name__ == "__main__":
    main()
