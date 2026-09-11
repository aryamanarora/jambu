"""Meaningful regression checks for incompatible source notations and Unicode."""
from phonology import modern_features,old_features

CASES=[
('Sh','degener-shina2008','báal',{'modern_outcome':'E','modern_nuclei':1}),
('Sh','degener-shina2008','baál',{'modern_outcome':'L','modern_nuclei':1}),
('Phal','liljegren','dhrígu',{'modern_outcome':'S','modern_accent_from_right':2}),
('Phal','liljegren','mhoóru',{'modern_outcome':'L','modern_accent_from_right':2}),
('Phal','liljegren','eeteeṇú',{'modern_outcome':'S','modern_accent_from_right':1,'modern_final_segment':'u','modern_quantity_pattern':'LLS'}),
('Phal','strand','mʹîš',{'modern_outcome':'E','modern_nuclei':1}),
('Phal','strand','rhôʹ',{'modern_outcome':'L','modern_nuclei':1}),
('Phal','strand','šêlʹi',{'modern_outcome':'S','modern_accent_from_right':1}),
('Phal','liljegren','lhoílu',{'modern_outcome':'vowel-sequence-marked','modern_vowel_sequence':1}),
('bro','schmidt',"'taato",{'modern_outcome':'stress-marked','stress_from_right':2}),
('bro','schmidt',"ni'lo",{'modern_outcome':'stress-marked','stress_from_right':1}),
('bro','schmidt',"'yṭi",{'modern_nuclei':2,'stress_from_right':2}),
('bro','schmidt','kʲii',{'modern_outcome':'unmarked','stress_position':''}),
('Sh','rajapurohit2012','aá',{'modern_outcome':'stress-in-vowel-sequence','modern_nuclei':2,'modern_vowel_sequence':1,'stress_from_right':1}),
('Sh','rajapurohit2012','gá:l',{'modern_outcome':'stress-marked','modern_nuclei':1,'modern_quantity_pattern':'L'}),
('Sh','rajapurohit2012','kí:lyéh',{'modern_outcome':'multiple-stress','stress_position':''}),
('Kalk','hultman2023kalkoti','šáak',{'modern_outcome':'H1'}),
('Kalk','hultman2023kalkoti','taár',{'modern_outcome':'H2'}),
('Kalk','hultman2023kalkoti','dríg',{'modern_outcome':'Hshort','modern_quantity_pattern':'S'}),
('Kalk','hultman2023kalkoti','gòór',{'modern_outcome':'Low+H2','explicit_low':1}),
('Kalk','hultman2023kalkoti','raan',{'modern_outcome':'unmarked'}),
('Kund','kund','mā̌l',{'modern_outcome':'R','contour_from_right':1}),
('Kund','kund','bā̂l',{'modern_outcome':'F','contour_from_right':1}),
('Sh','backstrom1992','kàa',{'modern_outcome':'F'}),
('Sh','backstrom1992','kaá',{'modern_outcome':'R'}),
('Sh','backstrom1992','kàá',{'modern_outcome':'LR'}),
('Ush','rensch-decker-hallberg1992',"'manuʐo",{'modern_outcome':'stress-marked','stress_from_right':3}),
('Sh','backstrom1992','nɑˈu',{'modern_vowel_sequence':1}),
('Sv','CDIAL','khḗṅgiā',{'modern_outcome':'syllable-marked'}),
('Sh','degener-shina2008','*báal',{'comparison_only':1}),
]
def main():
    for lang,source,form,expected in CASES:
        actual=modern_features(dict(language_id=lang,source_keys=source,original=form))
        for key,value in expected.items():assert actual[key]==value,(lang,source,form,key,actual[key],value)
    for form,expected in [
      ('bālá',{'old_first_quantity':'long','old_accent_position':2,'old_quantity_pattern':'LS'}),
      ('vā́la',{'old_first_quantity':'long','old_accent_position':1}),
      ('áśru',{'old_first_quantity':'short','old_intervocalic_cluster':'śr','old_nuclei':2}),
      ('ákṣi',{'old_accent_position':1,'old_quantity_pattern':'SS'}),
      ('akṣī́',{'old_accent_position':2,'old_quantity_pattern':'SL'}),
      ('áṅgāra',{'old_accent_quantity':'short','old_later_long':1,'old_quantity_pattern':'SLS'}),
      ('manuṣyà',{'old_accent_count':0}),
      ('vŕ̥kya',{'old_nuclei':2,'old_accent_position':1}),
    ]:
        actual=old_features(form)
        for key,value in expected.items():assert actual[key]==value,(form,key,actual[key],value)
    print('Passed',len(CASES),'modern notation fixtures and 8 historical-input fixtures. Old grave is not acute; no historical prediction is inferred from that parser category.')
if __name__=='__main__':main()
