"""Export canonical citations for reference-pill copying.

Run with the data project's environment after updating its bibliography:
  ../data/.venv/bin/python scripts/export_bibtex.py
"""
import json
from pathlib import Path
from pybtex.database import BibliographyData, parse_file

root = Path(__file__).resolve().parent.parent
bibliography = parse_file(root.parent / 'data/cldf/sources.bib')
editorial = {'included', 'provenance', 'jambu_editor', 'ocr', 'etymology_provenance'}
records = {}
for key, entry in bibliography.entries.items():
    for field in list(entry.fields):
        if field.lower() in editorial:
            del entry.fields[field]
    records[key] = BibliographyData(entries={key: entry}).to_string('bibtex').strip() + '\n'
output = root / 'static/bibtex.json'
output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(f'Exported {len(records)} canonical BibTeX records to {output}')
