from pathlib import Path
p=Path(__file__).with_name('historical_evidence.py');s=p.read_text().replace("h('S69-say','d365',","h('S69-say','d868',")
s=s.replace('DEDR mapping d365 to be verified before linking to main lexical counts; this historical row is not a new counted etymon.','DEDR868 linkage verified against database anu f_id6r5fma34f6w; all these forms remain one grammatical family.')
p.write_text(s)
p=Path(__file__).with_name('quantify_families.py');s=p.read_text().replace("if c['entry_id'] in {'d1','d410'}:domain='pronominal-morphology'", "if c['entry_id'] in {'d1','d410'}:domain='pronominal-morphology'\n    elif c['grammatical_category']=='verb/quotative':domain='nasal-quotative-morphology'")
p.write_text(s)
