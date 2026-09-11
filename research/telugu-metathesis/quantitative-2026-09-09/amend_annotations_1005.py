"""Exact source-string and citation corrections from the 10:05 review."""
from pathlib import Path
p=Path(__file__).with_name('cases_pronouns.py')
s=p.read_text()
s=s.replace("'Malayalam':('R','itu|ivan|ivaḷ|ivar|iva'", "'Malayalam':('R','itu|ivaṇ|ivaḷ|ivar|iva'")
s=s.replace('Malayalam itu/ivan','Malayalam itu/ivaṇ')
s=s.replace('K03 proposes *id-an-i > *dian-i > deni in Konda',
            'K03 proposes lowering in *id-an-i > *ed-an-i before displacement/contraction, followed by Konda deni')
p.write_text(s)
for name,old,new in [('cases_o_first.py','oṛga’ānā',"oṛga\\'ānā"),('cases_o_controls.py','otʰ’nai',"otʰ\\'nai")]:
    p=Path(__file__).with_name(name)
    p.write_text(p.read_text().replace(old,new))
