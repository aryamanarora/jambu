"""Research transcription of Rehman/Baart 9-Jan-2004 Tables10–12.

Supplementary primary-source observations, not new database records. Distinct
forms in one paradigm are not independent lexical confirmations. Tone labels
are the authors' explicit classifications; short citations may omit accents.
"""
from analysis_data import write_tsv,load_records

# gloss, nom.sg, nom.pl, obl.sg, obl.pl, independent formation, observation
DATA=[
('hair','báal','báal','báal','báalan','ordinary-noun','fixed-stem'),
('path','gɔ́ɔr','gɔ́ɔr','gɔ́ɔr','gɔ́ɔran','ordinary-noun','fixed-stem'),
('dog','kucúr','kucúr','kucúr','kucúran','ordinary-noun','fixed-stem'),
('day','díiz','díiz','díiz','díizin','ordinary-noun','fixed-stem'),
('maize','makɛ́y','makɛ́y','makɛ́y','makɛ́yin','ordinary-noun','fixed-stem'),
('knee','kuṭ','kuṭ','kuṭ','kúṭan','ordinary-noun','fixed-stem'),
('girl, woman','küṛ','küṛ','küṛ','kǘṛin','ordinary-noun','fixed-stem'),
('dish','baán','baán','baán','baanán','ordinary-noun','suffix-accented-oblique-plural'),
('horse','gɔɔ́ṛ','gɔɔ́ṛ','gɔɔ́ṛ','gɔɔṛán','ordinary-noun','suffix-accented-oblique-plural'),
('cupboard','almɛɛrí / almɛɛ́r','almaaríi','almaaríi','almaaríin','feminine-ii-with-truncated-nominative','final-short-i-or-root-R; umlaut'),
('ring (thumb-ring)','aṅgüüṭhí / aṅgüǘṭh','aṅguuṭhíi','aṅguuṭhíi','aṅguuṭhíin','feminine-ii-with-truncated-nominative','final-short-i-or-root-R; umlaut'),
('ring','wɛɛǰí','waaǰíi','waaǰíi','waaǰíin','feminine-ii-with-truncated-nominative','final-short-i; umlaut'),
('pillar','thuún','thuuníi','thuuníi','thuuníin','feminine-ii-with-truncated-nominative','root-R'),
('lamp','bɛtí / bɛ̀t','batíi','batíi','batíin','feminine-ii-with-truncated-nominative','final-short-i-or-short-root-Low; umlaut'),
('river','nad','nadíi','nadíi','nadíin','feminine-ii-with-truncated-nominative','short-root-unmarked/post-accented'),
('chair','kürsí','kursíi','kursíi','kursíin','feminine-ii-with-truncated-nominative','final-short-i; umlaut'),
('button','ṭax','ṭax','ṭàx','ṭaxán','post-accenting-noun-origin-unexplained','non-R-stem; suffix-accented-oblique-plural'),
('face','mukh','mux','mùx','muxɔ́n','post-accenting-noun-origin-unexplained','non-R-stem; suffix-accented-oblique-plural'),
('plough','hal','hal','hàl','halán','post-accenting-noun-origin-unexplained','non-R-stem; suffix-accented-oblique-plural'),
('ox','daan','daan','dàan','daanán','post-accenting-noun-origin-unexplained','non-R-LONG-stem; suffix-accented-oblique-plural'),
('shoe','buuṭ','buuṭ','bùuṭ','buuṭɔ́n','post-accenting-noun-origin-unexplained','non-R-LONG-stem; suffix-accented-oblique-plural'),
]

def main():
    rows=load_records();out=[]
    for i,(g,ns,np,os,op,cl,obs) in enumerate(DATA):
        table=10 if i<9 else 11 if i<16 else 12;page=11 if table<12 else 12
        matches=[r['id'] for r in rows if r['language_id']=='Kund' and r['source_keys']=='kund' and r['research_gloss'].lower() in g.split(', ')]
        note='Explicit author classification; normalizing font glyphs to Unicode does not change the printed accent position. Matching DB IDs are gloss candidates only and are not new ancestry assignments.'
        if i>=16:note+=' The authors explicitly leave this class unexplained. Ox and shoe have long roots, refuting a blanket short-stem explanation. A floating accent describes the paradigm but does not establish its historical source.'
        if 9<=i<16:note+=' Full feminine forms independently demonstrate the lost/shortened accented ii; fronting is a segmental trace of that ending. This is stronger evidence for truncation than the isolated nominative tone.'
        out.append(dict(item=i+1,gloss=g,nom_singular=ns,nom_plural=np,obl_singular=os,obl_plural=op,input_formation=cl,observed_pattern=obs,source='Rehman and Baart, draft 9 January 2004',table=table,page=page,db_gloss_candidate_ids=matches,analysis=note))
    write_tsv('kundal-primary-paradigms.tsv',out)
    print('21 primary paradigms: 9 ordinary, 7 feminine ii truncations, 5 post-accenting residuals. Supplementary source data, not DB additions.')
if __name__=='__main__':main()
