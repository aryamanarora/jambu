"""Conservative source-aware descriptive features; historical analysis is separate."""
import re
import html
import unicodedata as ud

VOWELS = set('aeiouæɑɒɪʊəɛɔɨɘɜɐʌɯɤœøʉɞɚɩɷ')


def clusters(s):
    out=[]
    for c in ud.normalize('NFD',s):
        if ud.combining(c) and out: out[-1] += c
        else: out.append(c)
    return out


def old_features(word):
    cs=clusters(word); vs=[]; i=0
    while i<len(cs):
        c=cs[i]
        if c[0] in 'aeiou' or (c[0] in 'rl' and any(x in c for x in ['\u0323','\u0325','\u0329'])):
            text=c; end=i
            if c[0]=='a' and '\u0304' not in c and i+1<len(cs) and cs[i+1][0] in 'iu':
                end=i+1;text+=cs[end]
            long=('\u0304' in text or c[0] in 'eo' or end>i)
            vs.append(dict(start=i,end=end,text=text,long=long,accent='\u0301' in text))
            i=end
        i+=1
    ai=[j for j,v in enumerate(vs) if v['accent']]
    chosen=vs[ai[0]] if len(ai)==1 else None
    return dict(old_nuclei=len(vs),old_accent_count=len(ai),
                old_accent_position=ai[0]+1 if len(ai)==1 else '',
                old_accent_from_right=len(vs)-ai[0] if len(ai)==1 else '',
                old_accent_quantity=('long' if chosen['long'] else 'short') if chosen else '',
                old_final_quantity=('long' if vs[-1]['long'] else 'short') if vs else '',
                old_later_long=int(any(v['long'] for v in vs[ai[0]+1:])) if len(ai)==1 else '',
                old_reconstructed=int('*' in word),
                old_aspiration=int(bool(re.search(r'[bgdjḍ]h|[bgdjḍ]ʰ',ud.normalize('NFC',word)))),
                old_initial_h=int(bool(re.match(r'\*?h',word))),
                old_quantity_pattern=''.join('L' if v['long'] else 'S' for v in vs),
                old_first_quantity=('long' if vs[0]['long'] else 'short') if vs else '',
                old_first_vowel=vs[0]['text'][0] if vs else '',
                old_intervocalic_cluster=ud.normalize('NFC',''.join(cs[vs[0]['end']+1:vs[1]['start']])) if len(vs)>1 else '',
                old_shape=''.join('V'+('V' if v['long'] else '') for v in vs))


def source_system(row):
    ss=set(row['source_keys'].split(';')); lang=row['language_id']
    if 'hultman2023kalkoti' in ss: return 'kalkoti-HL-2023'
    if 'kalkoti' in ss and lang=='Kalk': return 'kalkoti-HL-2013'
    if 'liljegren' in ss: return 'palula-mora'
    if 'degener-shina2008' in ss or 'buddruss-shina1996' in ss: return 'gilgit-mora'
    if 'schmidt' in ss: return 'brokskat-stress' if lang=='bro' else 'shina-mora'
    if 'strand' in ss: return 'strand-phonatory-accent'
    if 'kund' in ss: return 'kundal-mixed-legacy'
    if 'rajapurohit2012' in ss: return 'dras-stress-vowel-sequence'
    if ss & {'backstrom1992','decker1992','rensch-decker-hallberg1992'}: return 'survey-phonetic'
    if ss & {'liljegren-hindukush','knobloch2020sauji'}: return 'accent-not-investigated'
    if 'grierson-lsi1928' in ss: return 'historical-list'
    return 'historical-dictionary'


def modern_features(row):
    """Read notation, not an inferred historical accent.

    Nuclei are orthographic vowel groups. Adjacent unequal vowels are flagged:
    their syllabicity must be checked manually before positional statistics.
    No unmarked long vowel is automatically assigned first-mora accent.
    """
    system=source_system(row)
    raw=row['original']
    word=ud.normalize('NFC',html.unescape(re.sub(r'<[^>]*>','',raw)))
    cs=clusters(word); vs=[]; i=0
    vowels=VOWELS | ({'y'} if row['language_id']=='bro' else set())
    while i<len(cs):
        c=cs[i]
        if c[0] in vowels:
            end=i
            while system!='dras-stress-vowel-sequence' and end+1<len(cs) and cs[end+1][0]==c[0]:end+=1
            # In doubled-vowel mora orthographies these form one long nucleus.
            long=end>i or '\u0304' in c or (system=='strand-phonatory-accent' and '\u0302' in c)
            if end+1<len(cs) and cs[end+1][0] in ['ː',':']:long=True
            ac=[j-i for j in range(i,end+1) if '\u0301' in cs[j]]
            graves=[j-i for j in range(i,end+1) if '\u0300' in cs[j]]
            caron=any('\u030c' in cs[j] for j in range(i,end+1))
            circumflex=any('\u0302' in cs[j] for j in range(i,end+1))
            startmark=i>0 and cs[i-1][0] in ['ʹ',"'",'ˈ','ˊ']
            endmark=end+1<len(cs) and cs[end+1][0]=='ʹ'
            if system=='strand-phonatory-accent':
                if startmark:ac=[0]
                elif endmark:ac=[1] if long else [0]
            vs.append(dict(start=i,end=end,long=long,acute=ac,graves=graves,
                           caron=caron,circumflex=circumflex,text=''.join(cs[i:end+1])))
            i=end
        i+=1
    accented=[j for j,v in enumerate(vs) if v['acute']]
    low=any(v['graves'] for v in vs)
    wordlike=not bool(re.search(r'\s|[=/;,()]',word))
    unequal=any(cs[j][0] in vowels and cs[j+1][0] in vowels
                and (cs[j][0]!=cs[j+1][0] or system=='dras-stress-vowel-sequence') for j in range(len(cs)-1))
    # A pre-syllable mark between two vowels must not conceal a vowel sequence
    # from the conservative syllabification audit (e.g. survey nɑˈu, le'olo).
    interrupted_sequence=any(cs[j][0] in vowels and cs[j+1][0] in ["'",'ˈ','ʹ','ˊ'] and cs[j+2][0] in vowels for j in range(len(cs)-2))
    unequal=unequal or interrupted_sequence
    reconstructed=word.lstrip().startswith('*')
    misplaced=any(any(m in c for m in ['\u0301','\u0300']) and c[0] not in vowels for c in cs)
    mora_system=system in {'palula-mora','gilgit-mora','shina-mora','strand-phonatory-accent'}
    chosen=vs[accented[0]] if len(accented)==1 else None
    contour_positions=[]
    outcome='unmarked'
    if len(accented)>1:outcome='multiple-accents'
    elif chosen:
        if chosen['long']:
            outcome='E' if chosen['acute']==[0] else 'L' if chosen['acute']==[1] else 'ambiguous-mora'
        else:outcome='S'
    elif mora_system and len(vs)==1 and not vs[0]['long'] and wordlike:outcome='short-monosyllable'
    # Stress precedes the syllable onset, not necessarily its vowel.
    stress_positions=[]
    if system in {'survey-phonetic','brokskat-stress'}:
        for j,c in enumerate(cs):
            if c[0] in ["'",'ˈ','ʹ','ˊ']:
                nxt=next((k for k,v in enumerate(vs) if v['start']>j),None)
                if nxt is not None:stress_positions.append(nxt)
        stress_positions=sorted(set(stress_positions+accented)) if system=='brokskat-stress' else sorted(set(stress_positions))
    if system.startswith('kalkoti'):
        outcome={'E':'H1','L':'H2','S':'Hshort','multiple-accents':'multiple-H'}.get(outcome,outcome)
        outcome=('Low+' if low else '')+outcome
        if outcome=='Low+unmarked':outcome='Low'
    elif system=='kundal-mixed-legacy':
        # The hand-entered DB compresses source acute+grave to circumflex,
        # grave+acute to caron. Explicit source overrides take precedence.
        contours=[k for k,v in enumerate(vs) if v['caron'] or v['circumflex']]
        contour_positions=contours
        if len(contours)==1:
            v=vs[contours[0]]
            outcome='R' if v['caron'] else 'F'
        elif len(contours)>1:outcome='multiple-contours'
        elif chosen:outcome='H-marked'
        elif low:outcome='Low'
        else:outcome='unmarked'
    elif system=='survey-phonetic':
        # Radloff1992p147n42: first-mora grave=falling, second acute=rising.
        tone=[]
        for k,v in enumerate(vs):
            if v['long'] and v['graves']==[0] and v['acute']==[1]:tone.append('LR')
            elif v['long'] and v['graves']==[0] and not v['acute']:tone.append('F')
            elif v['long'] and v['acute']==[1] and not v['graves']:tone.append('R')
            elif v['acute'] or v['graves'] or v['caron'] or v['circumflex']:tone.append('marked-contour-needs-reading')
            if v['acute'] or v['graves'] or v['caron'] or v['circumflex']:contour_positions.append(k)
        outcome=tone[0] if len(tone)==1 else 'multiple-contours' if tone else 'stress-marked' if stress_positions else 'unmarked'
    elif system=='brokskat-stress':
        outcome='stress-marked' if len(stress_positions)==1 else 'multiple-stress' if stress_positions else 'unmarked'
    elif system=='dras-stress-vowel-sequence':
        # Rajapurohit2012 explicitly labels aá/uú as vowel sequences and
        # uses a colon for length. Preserve within-sequence location only.
        if chosen:outcome='stress-in-vowel-sequence' if chosen['end']>chosen['start'] or unequal else 'stress-marked'
        elif len(accented)>1:outcome='multiple-stress'
        else:outcome='unmarked'
        stress_positions=accented
    elif not mora_system:
        if outcome in {'E','L','S'}:outcome='syllable-marked'
    if unequal and mora_system and outcome in {'E','L','S'}:outcome='vowel-sequence-marked'
    issues=[]
    if not wordlike:issues.append('multiword-or-alternatives')
    if unequal:issues.append('unequal-vowel-sequence')
    if interrupted_sequence:issues.append('vowel-sequence-interrupted-by-accent-mark')
    if misplaced:issues.append('accent-on-nonvowel')
    if reconstructed:issues.append('starred-comparison')
    if re.search('<[^>]*>',raw):issues.append('markup-removed-for-reading')
    if len(accented)>1:issues.append('multiple-accent-marks')
    if any(v['end']-v['start']>1 for v in vs):issues.append('more-than-two-identical-vowels')
    return dict(notation=system,modern_nuclei=len(vs),modern_accent_count=len(accented),
                modern_accent_position=accented[0]+1 if len(accented)==1 else '',
                modern_accent_from_right=len(vs)-accented[0] if len(accented)==1 else '',
                modern_accent_quantity=('long' if chosen['long'] else 'short') if chosen else '',
                modern_outcome=outcome,modern_single_word=int(wordlike),
                stress_position=stress_positions[0]+1 if len(stress_positions)==1 else '',
                stress_from_right=len(vs)-stress_positions[0] if len(stress_positions)==1 else '',
                contour_position=contour_positions[0]+1 if len(contour_positions)==1 else '',
                contour_from_right=len(vs)-contour_positions[0] if len(contour_positions)==1 else '',
                contour_quantity=('long' if vs[contour_positions[0]]['long'] else 'short') if len(contour_positions)==1 else '',
                modern_vowel_sequence=int(unequal),
                modern_quantity_pattern=''.join('L' if v['long'] else 'S' for v in vs),
                modern_vowel_bases=''.join(v['text'][0] for v in vs),
                reading_issues=';'.join(issues),
                comparison_only=int(reconstructed),
                reading_form=word,
                explicit_low=int(low),
                modern_final_segment=cs[-1][0] if cs else '',
                modern_final_vowel=int(bool(cs and (cs[-1][0] in vowels or cs[-1][0] in ':ː'))))


def segment_key(word):
    """Candidate retrieval only; never sufficient for automatic cognacy acceptance."""
    word=ud.normalize('NFD',word.lower())
    word=''.join(c for c in word if not ud.combining(c))
    word=word.translate(str.maketrans({'ɑ':'a','ɒ':'a','æ':'a','ɛ':'e','ɪ':'i','ʊ':'u','ɔ':'o',
                                      'ɾ':'r','ɽ':'r','ʈ':'t','ɖ':'d','ŋ':'n','ʂ':'s','ʃ':'s','ʐ':'z',
                                      'ʒ':'z','ʰ':'h','ʦ':'c','ɡ':'g','ɬ':'l'}))
    return re.sub(r'[^a-z]','',re.sub(r'([aeiou])\1+',r'\1',word))
