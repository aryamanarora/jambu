"""Record newly verified epigraphic cautions without changing the source database."""
from pathlib import Path
P=Path(__file__).resolve().parent
p=P/'cases_u_laterals.py';s=p.read_text()
s=s.replace('Tamil uḷ locative, Kannada oḷ/oḷa and Old Telugu oḷana support a singleton lateral locative with low a independently of displaced forms.',
 'Tamil uḷ locative and Kannada oḷ/oḷa support the vowel-first singleton locative independently. The source-cited Old Telugu oḷana reading is now uncertain: DHARMA00099 and Sastri1969 p.285 n.1 read ēḷan ruling in the candidate inscription instead.')
s=s.replace('Southern and Central Dravidian vowel-first locatives plus earlier Old Telugu oḷana favor u/o–ḷ before Telugu lōna.',
 'Southern and Central Dravidian vowel-first locatives favor u/o–ḷ before Telugu lōna; the alleged earlier Old Telugu oḷana is not presently secure chronological evidence.')
s=s.replace('These are source dating claims pending epigraphic localization.',
 'These are source dating claims. The candidate seventh-century witness at Inpuḻōli has oḷana only in an older edition: Sastri1969 p.285 n.1 and DHARMA00099 read ēḷan ruling. Unless another inscription is identified, do not use oḷana to establish retention in seventh-century Telugu.')
s=s.replace("'OTelugu':('R','oḷana (7tʰ cent.)','Source-dated earlier locative; displaced ḷōna is attached to Telugu metadata.')",
 "'OTelugu':('A','oḷana (7tʰ cent.)','Source claim, but candidate inscription is re-read ēḷan ruling by Sastri1969 p.285 n.1 and DHARMA00099; not secure locative retention.')")
p.write_text(s)
p=P/'formation_tests.py';s=p.read_text().replace(
 'Old Telugu oḷana and Kannada oḷa independently support singleton low-a locative.',
 'Kannada oḷa supports singleton low-a locative; the claimed Old Telugu oḷana witness is a disputed reading, now ēḷan ruling in DHARMA00099.')
p.write_text(s)
p=P/'chronology-notes.md';s=p.read_text()
s=s.replace('DHARMA00101 independently discusses druggādēvi and mora preservation.',
 'DHARMA00101 independently discusses druggādēvi and mora preservation, but is a DIFFERENT Lakshmipuram inscription, source-dated c.681 by Sastri p.294; it must not inherit the 1290 date of SII V1217.')
p.write_text(s)
