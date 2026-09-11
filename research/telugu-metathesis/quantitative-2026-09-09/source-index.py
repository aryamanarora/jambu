import re,csv
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n):
 with (P/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
refs={r['ID']:r for r in read('references.tsv')};used=set();research=set()
for r in read('cited-evidence.tsv'):
 if r['Record_Origin']!='database':
  research.add(r['Source']);continue
 for item in r['Source'].split(';'):used.add(item.split('[')[0].strip())
out=['# Lexical source-key index\n\nCopied from the frozen database reference metadata. Source access and critical historical scholarship are separately documented in SOURCE_ACCESS.md. A key missing here may be a DEDR abbreviation, a research-only citation, or malformed imported metadata; it is not silently replaced.\n']
missing=[]
for key in sorted(used):
 if not key:continue
 r=refs.get(key)
 if not r:missing.append(key);continue
 out.append('## '+key+'\n\n'+r.get('Short','')+'\n\n'+r.get('Source','')+'\n')
out.append('## Database abbreviations requiring the source abbreviation list\n\n'+', '.join(missing)+'\n')
out.append('## Research-only source observations\n\nThese are complete citation strings for independently checked observations or separately segmented source paradigms. Semicolons inside them are prose punctuation, not necessarily database source-key separators. See SOURCE_ACCESS.md for access limits.\n')
for citation in sorted(research):out.append('- '+citation+'\n')
(P/'source-index.md').write_text('\n'.join(out))
print('Database keys',len(used),'resolved metadata',len(used)-len(missing),'unresolved abbreviations',len(missing),'research citation strings',len(research))
