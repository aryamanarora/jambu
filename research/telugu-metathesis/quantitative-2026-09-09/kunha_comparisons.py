"""All Kurux–Kunha lexical pairs printed in Kujur & Dash2025 pp.118–119.

Modern Kurux is a comparator, not an automatically ancestral stage. No Kunha
language ID is present in this database snapshot. These external observations
cannot enter its language frequencies or the Telugu root numerator.
"""
KUNHA=[]
def k(key,kurux,kunha,gloss,page,kind,analysis,entry='',check=''):
    KUNHA.append(dict(Observation_ID='KD25-'+key,Comparator_Language='Kurux',Comparator_Form=kurux,
        Target_Language='Kunha',Target_Form=kunha,Gloss=gloss,Source='Kujur and Dash2025',
        Page=page,Source_URL='https://doi.org/10.25077/ar.12.2.114-124.2025',
        Analysis_Category=kind,Analysis=analysis,Candidate_DEDR_ID=entry,
        Follow_Up=check or 'Earlier and fuller paradigms, recordings and additional cognates are needed to determine direction and separate phonetic change from morphological replacement.',
        Historical_Direction_Status='Paper orders Kurux before Kunha; common ancestry versus direct derivation is not independently demonstrated by this pair.'))
k('01','ekdā','ekād','who, which',118,'CV-reversal-plausible','Final d-ā becomes ā-d with vowel quality and quantity preserved. Morphological dā allomorphy remains an alternative; this is word-final, unlike initial Telugu promotion.','d5151')
k('02','tal-ī','atl-ī','copula present',118,'initial-CV-reversal-plausible','Initial t-a becomes a-t. This direction is the reverse of classical Telugu vowel-before-apical promotion; no single common directional change follows.')
k('03','apṭā','apoṭ','complete in a construction',118,'reversal-plus-vowel-change','ṭ-ā to o-ṭ entails both order and vowel quality/quantity changes. Compound context and exact base require verification.')
k('04','oṛok','uṛkū','tree bark',118,'syncope-final-vowel-alternative','Initial raising, medial vowel loss and final ū can derive the surface without a one-for-one exchange. The paper labels the input uk although its printed comparator has ok.')
k('05','orot','urtu','indefinite article',118,'syncope-final-vowel-alternative','Medial syncope plus initial raising and final u competes with literal exchange. Article morphology must be reconstructed separately.')
k('06','xall-ukhṛī','hallu-khuṛī','agriculture',118,'compound-restructuring-uncertain','Compound boundary, x/h correspondence, aspiration position and vowel placement all differ. Simple adjacent exchange alone is insufficient.')
k('07','calkur','calkrī','sand, gravel',118,'syncope-final-vowel-alternative','u-r to r-ī does not conserve the vowel. Deletion and final-vowel morphology/epenthesis compete with exchange plus vowel change.')
k('08','lidrʔ-ā','ildr-ā','get up',118,'initial-CV-reversal-plausible','Initial l-i becomes i-l with additional glottal loss. This initial direction differs from Telugu V-l > l-V.')
k('09','idim','idnā','nowadays',118,'morphological-or-lexical-uncertainty','The compared endings im and nā are not permutations: m/n and i/ā both differ. Temporal suffix substitution must be excluded before calling this metathesis.')
k('10','tuppalxō','tupphalō','saliva',118,'laryngeal-migration-plausible','Posterior fricative x may weaken to h and be realized earlier near the labial, with vowel reduction. Laryngeal migration is a distinct process from apical displacement.')
k('11','umbalxō','umbhalō','viscera: liver, kidney, heart, lungs',118,'laryngeal-migration-plausible','Parallel l-x to earlier labial-associated h, plus vowel loss. Exact semantics and compound morphology need checking; one published lexical comparison.')
k('12','guchā-baʔ-ā','ghucā-ba-a','throw away, move away',118,'aspiration-migration-plausible','Aspiration shifts from the medial affricate region to initial g; glottal loss and final-vowel details are additional. Could be a feature-level migration rather than whole-segment exchange.')
k('13','letheṛ okk-ā','thepeṛ okk-ā','sit cross-legged',118,'morphological-or-lexical-uncertainty','l versus p is not explained by transposition. Distinct lexical modifiers, assimilation or a transcription error must be evaluated; the paper does not supply the missing derivation.')
k('14','mākcūṇḍ','māskūṛ','flower name',118,'reversal-plus-consonant-change','k-c > s-k can be exchange if c>s is independently established; ṇḍ>ṛ is another change. Plant identity and cognacy are not verified.')
k('15','hoṛm-baʔ-ā','homṛa-ba-ā','throw down headlong',118,'CC-reversal-plausible','The ṛ-m > m-ṛ sequence is a clear local reversal under the given comparison; final a and glottal loss are separate. Compound/verb morphology precedes the local ordering.')
k('16','xarḍkā','haḍrkā','stolen',118,'CC-reversal-plausible','r-ḍ > ḍ-r reverses two consonants while x>h is a separate correspondence. This is a consonant-cluster process, not vowel-apical exchange.')
k('17','lapsārʔ-ā','lahpār-ā','take long strides',118,'reversal-plus-consonant-change','The actual printed input has p-s, although the paper labels the changed sequence sp. An analysis ps>hp requires s>h plus order reversal; literal segment conservation is false.')
k('18','ȭsaṛgō','ȭṛskā','mushroom',118,'reversal-plus-consonant-change','s-ṛ reversal is plausible alongside medial vowel loss, g/k and final vowel changes. Species and root segmentation remain unverified.')
k('19','khaṛiya-in / khaṛiyā-n','khaṛiyā-n','Kharia feminine affiliation',118,'morphological-allomorph-selection','Kunha retains one suffix allomorph already reported in Kurux. No new reversal need occur; the selected form cannot be treated as a direct -ni>-in change.')
k('20','corh-nī / cor-nī','cor-nī','female thief',118,'no-order-change','The compared selected variant shows h absence, with n-ī order unchanged. It does not instantiate the claimed suffix-order reversal.')
k('21','nāmukil kāl-ā','nāmuklī kāl-ā','deny, oppose',118,'reversal-or-syncope-lengthening','Medial i-l to l-ī is compatible with vowel movement plus lengthening, but syncope and final-vowel morphology must also be excluded.')
k('22','biyārī','pairī','wee hours',118,'contraction-or-vowel-reordering','b/p and glide/vowel contraction differ; the claimed ia>ai analysis is not a complete derivation from the actual source form.')
k('23','eṛeth','iṛtū','long-bow',119,'syncope-final-vowel-alternative','Database Kurux eṛetʰ and Malto eṛtu support a medial-cluster alternative. Neither establishes that the final u is the same segment as the deleted medial e.','d789')
k('24','keber mōx-ā','kebra mōh-ã̄','be scolded',119,'syncope-final-vowel-alternative','e-r to r-a differs in vowel quality. Final morphology, medial reduction and regular x>h compete with literal exchange.')
k('25','xēxel','hēhlā','land, earth',119,'syncope-final-vowel-alternative','x>h, medial e deletion and final ā can derive this without moving the initial long ē. The paper incorrectly identifies ēx>hē as the relevant local exchange.')
k('26','endrā','endēr','what, why',119,'CV-reversal-plus-vowel-change','The visible change concerns r-ā versus ē-r, not en>ne as stated in the prose. Initial en stays in place.','d5151')
k('27','tolokh','tolkhō','side, armpit',119,'syncope-final-vowel-alternative','Medial o loss and final ō morphology/epenthesis compete with vowel-kh reversal. Malayalam tokku is a queried wider cognate and does not establish this medial northern vowel.','d3520')
k('28','nakar-nukur','nu.kra-nu.kru [table] / na.kru nu.kru [prose]','tottering',119,'source-internally-inconsistent','The target vowel pattern differs between prose and table. Neither version can be silently selected to establish a deterministic vowel-order rule.')
k('29','nalakh','nalkhu','work, duty',119,'syncope-final-vowel-alternative','a before kh versus u after kh requires quality change or distinct vowel insertion; no conserved-vowel swap is established.')
k('30','marag','margū [table] / mar.gu [prose]','horn, antler',119,'syncope-final-vowel-alternative','Medial a loss and final u/ū differ in quality and source quantity. Final stem morphology is an alternative to literal exchange.')
