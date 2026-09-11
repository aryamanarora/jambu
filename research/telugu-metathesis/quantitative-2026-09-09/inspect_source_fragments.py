import csv
from pathlib import Path
P=Path(__file__).resolve().parent
spec={'d3115':{'aṛ̆al','*c','*t'},'d4716':{'maru mane','kēdu mane'},'d5372':{'b&lt','br&lt','&gt','atuku','LSI','(Mariā of Bastar'}}
with (P/'corpus.tsv').open() as f:
 rows=list(csv.DictReader(f,delimiter='\t'))
print('fields',list(rows[0]))
for r in rows:
 if r.get('Form') in {v for vv in spec.values() for v in vv}:print(r)
