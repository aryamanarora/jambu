#!/usr/bin/env python3
"""Aggregate the data repository's sound profiles into the transcription-chart dataset.

Every source ingested into Jambu carries a profile under ``../data/conversion/<source>.txt``: a
two-column TSV mapping that source's own notation onto Jambu's house transcription. Read across
all of them, those files are a corpus of evidence for what the house transcription actually *is*
-- which glyph Jambu writes for a given IPA symbol, and where profiles legitimately disagree.

This script collapses that corpus into ``src/lib/transcriptionChart.json``, which the
``/transcription`` page overlays onto the IPA charts. The output is committed, so the site builds
in CI without the sibling data repository present.

Run from ``jambu-static/``::

    python3 scripts/build_transcription_chart.py
    python3 scripts/build_transcription_chart.py --check    # fail if the committed copy is stale
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONVERSION = ROOT.parent / "data/conversion"
OUTPUT = ROOT / "src/lib/transcriptionChart.json"

# house.txt is a pass-through allow-list of permitted output characters rather than a source
# mapping, and cdial-post is a post-processing pass over already-converted forms. Neither is
# evidence about how an IPA symbol is rendered.
EXCLUDED_PROFILES = {"house", "cdial-post"}


def read_profile(path: Path) -> list[tuple[str, str]]:
    """The (grapheme, house output) pairs in one profile, minus its header."""
    pairs = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if index == 0:
            continue
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        grapheme, output = parts[0], parts[1]
        if grapheme:
            pairs.append((grapheme, output))
    return pairs


def build(conversion_dir: Path) -> dict:
    profiles = sorted(
        path for path in conversion_dir.glob("*.txt") if path.stem not in EXCLUDED_PROFILES
    )
    if not profiles:
        raise SystemExit(f"no sound profiles found under {conversion_dir}")

    outputs: dict[str, Counter] = {}
    sources: dict[str, dict[str, list[str]]] = {}
    for path in profiles:
        for grapheme, output in read_profile(path):
            outputs.setdefault(grapheme, Counter())[output] += 1
            sources.setdefault(grapheme, {}).setdefault(output, []).append(path.stem)

    mapping = {}
    for grapheme, counter in outputs.items():
        ranked = counter.most_common()
        majority, majority_count = ranked[0]
        mapping[grapheme] = {
            "house": majority,
            "profiles": sum(counter.values()),
            "agreement": majority_count,
            "variants": [
                {
                    "house": output,
                    "profiles": count,
                    # Naming a few profiles makes a minority reading checkable rather than
                    # mysterious; the full list would swamp the payload.
                    "examples": sorted(sources[grapheme][output])[:4],
                }
                for output, count in ranked[1:]
            ],
        }

    return {
        "generatedFrom": "../data/conversion/*.txt",
        "profileCount": len(profiles),
        "graphemeCount": len(mapping),
        "map": dict(sorted(mapping.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conversion", type=Path, default=DEFAULT_CONVERSION)
    parser.add_argument("--check", action="store_true", help="fail if the committed copy is stale")
    args = parser.parse_args()

    payload = json.dumps(build(args.conversion), ensure_ascii=False, indent="\t") + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != payload:
            print(f"{OUTPUT.relative_to(ROOT)} is stale; re-run this script", file=sys.stderr)
            return 1
        print(f"{OUTPUT.relative_to(ROOT)} is up to date")
        return 0

    OUTPUT.write_text(payload, encoding="utf-8")
    data = json.loads(payload)
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: "
        f"{data['graphemeCount']} graphemes from {data['profileCount']} profiles"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
