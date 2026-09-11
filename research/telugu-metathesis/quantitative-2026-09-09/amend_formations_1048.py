from pathlib import Path
p=Path(__file__).with_name('formation_tests.py');s=p.read_text()
for a,b in [
 ("'ulavalu'","'uddulu'"),
 ('Full bean formation; detailed Telugu suffix/lateral history remains separate from initial retention.','Full bean formation; medial apical assimilation yields uddulu, an O outcome rather than secure apical retention.'),
 ("'ṛūva'","'ṛūva (ṛūt-)'"),
 ("'rūga'","'rūga (rūgi-)'"),
 ("'rūma|rūmba'","'rūma (rūmi-)|rūmba (rūmbi-)'"),
 ("'pṛēnu'","'pṛēnu ( pṛēka)'"),
]:s=s.replace(a,b)
p.write_text(s)
