"""Exact source-form reconciliation after annotation linkage validation."""
from pathlib import Path
p=Path(__file__).with_name('cases_brahui_comparison.py')
s=p.read_text()
for old,new in [
 ('cori|cura|cōr|tōr','cori|cura|cōr|tōr (neyttōr'),
 ("('R','dalga',","('R','dalga (dalgi-)',"),
 ("('R','ḍāṭ- (-it-)',","('R','ḍāṭ- (-t-)',"),
 ("('R','tuṟbi',","('R','tuṟbi- (-t-)',"),
 ("'piri-|biri-|pirip'","'piri- (pirip-, piric-)|biri- (birip-, biric-)|pirip'"),
 ('piri|puri|piri-gonu','piri|puri|pirigonu'),
 ('pṛihpa (pṛiht-)|vṛīsa|vṛīska|bṛīc','pṛihpa (pṛiht-)|vṛīsa (vṛīsi-)|vṛīska (vṛīski-)|bṛīc'),
 ("'ṛīsk|vīskinai'","'ṛīsk- (-it-)|vīskinai'"),
 ("D='ṛīsk'","D='ṛīsk- (-it-)'"),
]: s=s.replace(old,new)
p.write_text(s)
