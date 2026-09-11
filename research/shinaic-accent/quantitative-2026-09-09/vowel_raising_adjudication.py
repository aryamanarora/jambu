"""Adjudication of all 78 retrieved dialect pairs, read individually.

The six aa-to-uu pairs remain counterexamples to an aa-to-oo surface rule.
An independently established proto-au class is narrower than those six.
"""
import json
from collections import Counter,defaultdict
from analysis_data import tsv,HERE,write_tsv

SPECIAL={
 'four':('proto-au-proposal-in-primary-literature','Liljegren2009pp21–25 explicitly reconstructs *au for čáar/čúur. This is an alternative proto-vowel analysis, not an exceptionless prediction from Biori aa alone.'),
 "father-in-law; husband's or wife's father":('proto-au-with-internal-w-alternation','Liljegren2009p21 cites ša(w)úra household of father-in-law as independent internal evidence for *au. The šáar/šúur correspondence cannot be derived from an undifferentiated proto-aa class.'),
 'story, tale':('proto-au-proposal-in-primary-literature','Liljegren2009p25 explicitly includes šiláak/šilúuk in the proposed proto-au class. The OIA śloka connection and intermediate vowel history require their own argument.'),
 'stream; streambed, gorge':('unresolved-aa-to-uu','dhráak/dhrúuk has uu instead of predicted oo. Extending the *au reconstruction solely to fit this outcome would be circular; seek independent inflectional or older-source evidence.'),
 'lap':('unresolved-aa-to-uu','máaṛ/múuṛ has uu rather than oo. A former diphthong is possible but not independently established by this pair; retain as a genuine residual of the surface aa-to-oo prediction.'),
 'Drosh (bazaar town in southern Chitral); sub-district (tehsil) centre for the area where Palula is spoken':('place-name-aa-to-uu','dhráa~ṣ/dhrúu~ṣ is a place name with a separate local transmission history. Neither its proper-name status nor a proposed *au automatically explains the correspondence.'),
 'buffalo bull':('final-vowel-quantity-difference','saṇḍaá/saṇḍá is a final accented vowel with a quantity difference, not a closed-syllable raising example. The lexical gender/citation formation needs comparison.'),
 'them (dist acc)':('late-accusative-plural-control','lenaám/lanaám keeps late aa while the preceding unstressed vowel changes. This is one member of the shared -aám accusative plural pattern, not an independent lexical history from tenaám.'),
 'them (rem acc)':('late-accusative-plural-control','tenaám/tanaám keeps late aa. Together with lenaám, this supplies two surface forms but only one inflectional-suffix control.'),
 'late summer or autumn; 80-day period during which various kinds of fruit are ripe, the maize harvest is gathered, and people are stocking up for the cold season (appr. 11 Sep-30 Nov)':('extended-seasonal-formation','šaraháaṛu/šaaraháaṛu changes earlier unstressed vowel length while accented aa before the final ending remains. It lies outside the word-final closed-syllable test.'),
 'hill; rock':('nonfinal-aa-residual-outside-test','táapeṛ/táapaṛ retains initial aa and changes the following unstressed vowel. Its long root and original formation are not established, so it must not be used to prove the source of every nonfinal aa.'),
 'Chitral (the district or the adminitrative centre of the district)':('proper-name-raising-with-unstressed-change','c̣hetráal/c̣hatróol raises the final accented aa to oo and changes an earlier unstressed e to a. The borrowing history of the name is separate from the regular local vowel adaptation.'),
 'lawful; lawfully slaughtered':('contact-vocabulary-raising','haláal/halóol is the regional Arabic-origin halal word. Its integration into the same raising correspondence as inherited nouns constrains the lexical reach of the process, but does not independently date each borrowing.'),
 'free':('contact-vocabulary-raising','xaláas/xalóos is the regional Arabic-origin khalas word. It shows raising in the nonverb element of a complex predicate, so the correspondence is not confined to inherited nouns.'),
 'bazaar, market':('contact-vocabulary-raising','baazáar/baazóor is the Persian bazaar word. Liljegren2016Table3.15p80 also gives Biori baazáar/baazúura, an independent inflectional alternation showing that syllable structure matters.'),
 'prayer':('contact-vocabulary-raising','nimáas/nimóos is the regional namaz prayer word. Liljegren2016 explicitly cites the dialect pair in the discussion of conjunct verbs; it follows the same local raising correspondence.'),
 'sign, mark; mole':('contact-vocabulary-raising','niṣáan/niṣóon is the regional nishan mark/sign word; the dictionary even preserves morphemic niṣáan for the raised Ashret form.'),
 'hunting':('contact-vocabulary-raising','iṣkáar/iṣkóor compares the regional shikar hunting word; its regional history is distinct from the local aa-to-oo correspondence.'),
 'shirt':('contact-vocabulary-raising','peeráaṇ/peeróoṇ is the regional shirt formation associated with Persian pairāhan; initial and final vowel histories should be separated. Only the final early aa-to-oo correspondence is tested here.'),
}

def main():
    rr=tsv('vowel-raising-candidates.tsv');assert len(rr)==78
    out=[];annotations=[];summary=defaultdict(Counter)
    for r in rr:
        closed=r['tested_syllable_domain']=='word-final-closed';v=r['biori_test_vowel'];o=r['ashret_test_vowel'];acc=r['biori_accent']
        if closed and acc=='E':
            expected='o' if v=='a' else 'i';cl='Biori-early-'+v+'-long-final-closed'
            status='consistent' if o==expected else 'other-quality'
            note='Same consonantal frame and gloss; the Biori early long vowel is in the final closed syllable. Test aa→oo or ee→ii without changing the prediction for residuals.'
        elif closed and acc=='L':
            expected=v;cl='Biori-late-'+v+'-long-final-closed';status='consistent' if o==expected else 'other-quality'
            note='Late-mora Biori long vowel in final closed syllable; the quality-retention control is independent of the Ashret result.'
        else:
            expected='';cl='other-syllable-domain';status='outside-closed-syllable-test'
            note='The tested vowel is not in a final closed syllable. Most nonfinal aa pairs are verbal stems with additional morphology; their long aa may result from earlier short-vowel lengthening and cannot be assumed identical to inherited long aa.'
        special,specific=SPECIAL.get(r['gloss'],('',''))
        if r['gloss'] in ['our (1pl gen)',"whose, somebody's, anybody's",'his; her; its (dist)','his; her; its (rem)','your (2pl gen)']:
            special='genitive-ending-raising';specific='Final early -ée corresponds to -íi in a genitive form. Five pronominal forms instantiate one shared grammatical ending; do not count them as five independent sound changes.'
        note+=' '+specific
        out.append({**r,'input_class':cl,'predicted_quality':expected,'status':status,'special_analysis':special,'analysis':note})
        annotations.append(dict(record_ids=json.loads(r['record_ids']),analysis=r['biori']+' / '+r['ashret']+' ('+r['gloss']+'). '+note,
                                review_type='manual-dialect-pair-comparison',source='Liljegren2019 dictionary, with Liljegren2009pp20–25 and2016pp28–29,80 controls'))
        summary[cl][status]+=1
    write_tsv('vowel-raising-reviewed.tsv',out)
    write_tsv('vowel-raising-summary.tsv',({'input_class':cl,'form_pairs':sum(c.values()),**dict(c)} for cl,c in summary.items()))
    (HERE/'lexical_annotations_02.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in annotations))
    print({k:dict(v) for k,v in summary.items()})
if __name__=='__main__':main()
