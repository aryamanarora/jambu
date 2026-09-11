"""Independent numeral-compound comparison, with every source token retained.

11–18 are ten compounds; 19 is compared separately as a twenty formation in
Palula/Kalkoti. These are eight members of one morphological series, not eight
independent innovations. Source reading: Hultman2023 Table16 printed p28.
"""
import json
from collections import defaultdict
from analysis_data import load_analysis_tokens,write_tsv,HERE
from quantify import LANGS,outcome

WORDS=['eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty']
NOTES={
11:'Palula akóoš/akáaš has E in the final syllable; Kalkoti äkaáš has H2. Brokskat qudeš has initial stress and a distinct compound shape; Kundal yagáy marks final prominence without a recoverable mora contrast.',
12:'Palula bóoš/báaš E versus Kalkoti baáš H2 is a real exception to the simple monosyllabic E→zero mapping, but it agrees with the independent ten-compound series. Shina baai vowel sequences require source-specific interpretation; Brokskat budeš has initial stress.',
13:'Palula tríiš/tréeš E versus Kalkoti treéš H2 belongs to the same ten-compound pattern as twelve. Brokskat trobeš is unmarked in print, not assigned initial stress by analogy. Shina often contracts to a vowel sequence or monosyllable.',
14:'Palula čandíiš/čandéeš E corresponds to Kalkoti čändeéš H2. Shina includes initial-long, medial-short and final-short marked variants, with different syllable reductions. Brokskat cuudeš and Ushojo cadʌš have initial stress; the western High pattern is not universal Shinaic final stress.',
15:'Palula panǰíiš/panǰéeš E corresponds to Kalkoti pänǰeéš H2. Shina preserves several differently expanded formations with final prominence; Brokskat pããdeš has initial stress. Unmarked Sauji variants do not establish an E/L value.',
16:'Palula ṣoṛíiš/ṣoṛéeš E corresponds to Kalkoti ṣureéš H2. Shina contracted ṣoo(y/i) variants and Brokskat ṣobeš are different surface formations; Brokskat has initial stress. A different stem spelling does not erase the independent ten-compound membership.',
17:'Palula satóoš/satáaš E corresponds to Kalkoti sätaáš H2. Unlike the earlier Brokskat teens, sattõõš has final stress. Shina final accented aa precedes y/i material whose syllabicity varies by source.',
18:'Palula aṣṭóoš/aṣṭáaš E corresponds to Kalkoti iṣṭaáš H2. Brokskat aṣṭõš also has final stress. The independent ten-compound series includes both mono- and polysyllabic modern words; its common Kalkoti H2 cannot be reduced to current syllable count.',
19:'Palula aṇabhiíš L and Kalkoti änbíiš H1 contain the twenty element, unlike 11–18 ten compounds. Their correspondence matches Palula bhiíš L/Kalkoti bíiš H1 twenty. Shina kuniih and Brokskat kunjaa have different one-less formations, so no identical whole-compound accent history is assumed.',
20:'Palula bhiíš L corresponds to Kalkoti bíiš H1; Shina commonly has bií L, Kundal bī̌ rising, and Brokskat bižaa final syllable stress. Survey biš panj under twenty contains five as well and is not a clean twenty citation; preserve it with an explicit exclusion.'}

def number(r):
    g=r['research_gloss'].lower().strip()
    for n,w in enumerate(WORDS,11):
        if g in [w,str(n)] or (n==20 and g=='twenty; the twenty sth or people; 20'):return n
    return None

def main():
    rows=[];annotations=[];groups=defaultdict(list)
    for r in load_analysis_tokens():
        n=number(r)
        if n is None:continue
        exclusion='twenty-plus-five-expression-misglossed' if n==20 and 'p' in r['reading_form'] and ' ' in r['reading_form'] else ''
        note=NOTES[n]
        rows.append(dict(numeral=n,formation_class='ten-compound-series' if n<=18 else 'nineteen-comparison' if n==19 else 'twenty-control',
           language=r['language_id'],analysis_token_id=r['analysis_token_id'],record_id=r['id'],form=r['reading_form'],gloss=r['research_gloss'],
           family_id=r['research_family_id'],source=r['source_keys'],dialect=r['dialect_tags'],outcome=outcome(r),
           exclusion=exclusion,reading_issues=r['reading_issues'],analysis=note))
        groups[n,r['language_id']].append(rows[-1])
        annotations.append(dict(record_ids=[r['id']],review_type='manual-numeral-series-comparison',analysis=note,
            source='Hultman2023Table16p28 plus all retrieved DB citation variants; printed Brokskat readings checked separately.'))
    write_tsv('numeral-series-records.tsv',rows)
    panel=[]
    for n in range(11,21):
        for lang in LANGS:
            rr=groups[n,lang]
            panel.append(dict(numeral=n,language=lang,forms=sorted({r['form'] for r in rr}),outcomes=sorted({r['outcome'] for r in rr if not r['exclusion']}),
             sources=sorted({r['source'] for r in rr}),excluded=sorted({r['form'] for r in rr if r['exclusion']}),analysis=NOTES[n]))
    write_tsv('numeral-series-language-panel.tsv',panel)
    tests=[]
    for n in range(11,21):
        for lang,source,pred in [('Phal','liljegren','E' if n<=18 else 'L'),('Kalk','hultman2023kalkoti','H2' if n<=18 else 'H1')]:
            rr=[r for r in rows if r['numeral']==n and r['language']==lang and r['source']==source]
            os={r['outcome'].split('@')[0] for r in rr}
            tests.append(dict(numeral=n,language=lang,source=source,predicted=pred,observed=sorted(os),consistent=int(os=={pred}),form_tokens=len(rr)))
    write_tsv('numeral-series-tests.tsv',tests)
    # Two-source split forms can share a raw ID: keep one annotation per record.
    unique={r['record_ids'][0]:r for r in annotations}
    (HERE/'lexical_annotations_04.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in unique.values()))
    print('tokens',len(rows),'raw records',len(unique),'tests',tests)
if __name__=='__main__':main()
