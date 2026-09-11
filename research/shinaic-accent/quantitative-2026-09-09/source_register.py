"""Evidence register: interpretation, access level and database coverage."""
import re
from collections import Counter,defaultdict
from analysis_data import tsv,write_tsv,HERE

# access distinguishes a primary printed-page check from a database reading.
NOTES={
'CDIAL':('Historical citations with heterogeneous original conventions. A macron plus acute identifies a syllable; it is not automatically a modern first-mora accent. Broad dictionary headword and nearest formation are distinct. Grave/svarita and competing old accents remain meaningful.',
 'Complete cached original entries read for diagnostic and disputed etymologies; first-pass review of every frozen family. This is not a page-by-page rereading of the entire dictionary.',
 'https://dsal.uchicago.edu/dictionaries/soas/'),
'liljegren':('First/second doubled-vowel acute is E/L; short accented vowel is S. Retain morphological cells, dialect variants, homonyms and full inflectional strings. Unmarked forms remain unmarked.',
 'Database dictionary records reviewed by family and selected complete morphological/dialect sets; grammar and dictionary documentation used for primary cross-checks. This is not an independent page check of every source record.',
 'https://dictionaria.clld.org/contributions/palula'),
'strand':('Circumflex denotes length; accent before a long vowel is early, after it late. Underlying forms and inflection classes are separate from surface citation words.',
 'Primary cached lexical HTML checked for diagnostic entries, reference corrections, night/measure distinction and conflicting paradigms; remaining entries retained as database evidence.',
 'https://nuristan.info/IndoAryan/Indus/Atsaret/AtsaretLanguage/Lexicon/phon.html'),
'degener-shina2008':('Gilgit doubled-vowel acute gives E/L; short acute gives syllable location. Verb stems and cited perfectives cannot be treated as identical grammatical cells.',
 'Checked-in diplomatic transcription and database entries inspected. A printed facsimile was not available for independent scan verification; source versus transcription errors remain distinguishable only where internal evidence permits.',
 ''),
'buddruss-shina1996':('Gilgit mora-accent notation is retained independently of Degener. Conflicting forms are not harmonized by majority vote.',
 'Database and checked-in transcription/audit evidence inspected; original printed pages were not independently available.',
 ''),
'schmidt':('Non-Brokskat first/second doubled-vowel acute represents high-falling/low-rising mora accent. Brokskat notation records syllable stress, not that mora contrast. Short monosyllables may be unmarked.',
 'Primary notation discussion pp234,244–245 and all269 Brokskat Table2 items read against print; selected other diagnostic Shina table entries checked. Source glyph quality remains uncertain for some central vowels.',
 'https://www.wisdomlib.org/uploads/journals/acta-orie/vol-69-2008/7372-6759-23258.pdf'),
'kalkoti':('2013 Low analysis and phonetic contours are preserved separately from 2023 H1/H2 analysis. Table12 contour observations are explicit overrides, not deductions from an unmarked string.',
 'Complete relevant phonology and Tables12–13 read; source/dialect-tag mismatch corrected. Published sample is selected phonetic evidence, not an unbiased lexicon-wide tone sample.',
 'https://journals.dartmouth.edu/journals/xmlpage/1/article/423?htmlOnce=yes'),
'hultman2023kalkoti':('H1/H2 and syllable-wide Low remain distinct. Unmarked words can have uncertain tone. Only explicit Table9 toneless examples receive 0-explicit.',
 'Tone discussion and Tables9–10, comparative Table6 and numeral Table16 checked; all473 previously unlinked source records reviewed in lexical groups.',
 'https://www.diva-portal.org/smash/get/diva2%3A1772061/FULLTEXT01.pdf'),
'kund':('Legacy circumflex/caron are provisionally read as falling/rising; explicit primary readings supersede compressed database notation. Accent mobility is a paradigm property, not a wordlist vowel mark.',
 'Primary source actually read is the 9 January 2004 prepublication draft, including 21 paradigms. The final 2005 publication was not independently retrieved; do not cite draft pagination as final-publication pagination.',
 'http://www.sil.org/silewp/abstract.asp?ref=2005-008'),
'rajapurohit2012':('Acute is stress; colon is vowel length. Repeated aá/uú can be separate nuclei, not Gilgit first/second-mora notation. Multiple acute marks and inconsistent paradigms are preserved.',
 'Notation and nominal grammar checked in primary PDF; all287 plural citations reviewed with available singular comparators. Selected anomalous vocabulary entries checked against print; the entire3021-record source was not individually revalidated.',
 'https://www.aa.tufs.ac.jp/~tjun/shina/Grammar_of_Shina_Language_And_Vocabulary.pdf'),
'backstrom1992':('Pre-syllable stress and marked phonetic contours are distinct. First-mora grave/falling and second-mora acute/rising interpretation is source-specific. Unmarked survey words have unknown accent.',
 'Primary methodological discussion and notation footnote read. Database forms included in every family appendix; not all survey tokens individually phonologically reanalyzed.',
 'https://github.com/lexibank/backstromnorthernpakistan'),
'decker1992':('Survey stress marks are retained. Segmental quantity alone does not identify mora accent. Slash alternatives and multiword numeral expressions need separate treatment.',
 'Database forms compared in family and selected lexical panels; no complete primary wordlist-page audit.',
 ''),
'rensch-decker-hallberg1992':('Survey pre-syllable marks record stress. Word boundaries, alternatives and secondary marks must not be parsed as one ordinary long-vowel accent.',
 'All selected previously unlinked Ushojo records assessed; boundary corrections and source comparisons preserved. This does not establish a full Ushojo tonal system from the wordlist.',
 ''),
'knobloch2020sauji':('The author explicitly did not analyze stress and pitch accent. Unmarked tokens therefore carry unknown accent; tentative suffix observations are not propagated as lexical stress labels.',
 'Primary phonology discussion read; all573 database source records reviewed in335 gloss groups, including verbs, loans and compounds.',
 'https://urn.kb.se/resolve?urn=urn:nbn:se:su:diva-182519'),
'buddruss1967sau':('Historical accented-vowel citations can supply syllable location; do not automatically convert a macron-acute to modern E/L.',
 'Database citations retained with their bibliographic identity; the whole primary monograph was not reread.',
 ''),
'liljegren-hindukush':('Areal dataset supplies segmental/phonation evidence but not a uniform comparable lexical accent annotation. Creaky vowels are not silently relabelled High tone. HKAT dialect tags do not identify the source of a merged record.',
 'Database source records included throughout and selected identical lexemes linked by manually reviewed evidence; no new source ingestion or full source phonological audit.',
 'https://github.com/cldf-datasets/liljegrenhindukush/tree/v1.1.0'),
'grierson-lsi1928':('Historical comparative-list notation is heterogeneous and unevenly accented. Digital edition date2023 is not the date of Grierson1928 observations.',
 'Frozen digital comparative records included; no comprehensive rescanning of the original volume.',
 'https://github.com/lexibank/lsi/tree/v1.0'),
}
EXTRA=[
 ('liljegren2016','Henrik Liljegren. 2016. A grammar of Palula. Language Science Press.',
  'Primary morphology, dialect comparison and phonology: pp28–29,78–81,112–123,162–164,178 and cited examples.',
  'https://langsci-press.org/catalog/view/82/85/399-1.pdf'),
 ('liljegren2009','Henrik Liljegren. 2009. The Dangari tongue of Choke and Machoke: Tracing the proto-language of Shina enclaves in the Hindu Kush.',
  'Primary dialect correspondence discussion pp20–25, including proposed proto-au and quantity chronology.',
  'https://doi.org/10.5617/ao.5341'),
 ('gomes2014','Andrew Gomes. 2014. Investigating the tonal contours of Sawi nouns: A contrastive analysis with established tonal features of Palula. Stockholm University.',
  'Primary methods, results and limitations read:71 nouns, one male speaker,284 recordings. The proposed absence of Palula-like lexical pitch accent is limited by this sample.',
  'https://www.diva-portal.org/smash/get/diva2%3A1055060/FULLTEXT01.pdf'),
]
def clean(s):return re.sub(r'\\([.\-(),_])',r'\1',s).replace('&ndash;','–')
def main():
    counts=Counter();langs=defaultdict(set)
    for r in tsv('corpus.tsv'):
        for source in r['source_keys'].split(';'):
            counts[source]+=1;langs[source].add(r['language_id'])
    out=[]
    for r in tsv('references.tsv'):
        key=r['ID'];n=NOTES.get(key)
        out.append(dict(source_key=key,bibliography=clean(r['Source']),raw_records=counts[key],languages=sorted(langs[key]),
         notation=n[0] if n else 'Legacy citation or abbreviated authority within a composite historical source; no uniform accent interpretation assigned independently.',
         access_and_review=n[1] if n else 'Citation metadata preserved; see the primary source containing the quotation. This is not an independent new phonological study.',
         url=n[2] if n else ''))
    for key,bib,access,url in EXTRA:
        out.append(dict(source_key=key,bibliography=bib,raw_records=0,languages=[],notation='Supplementary primary analysis, not a frozen database source.',access_and_review=access,url=url))
    write_tsv('source-register.tsv',out)
    print(len(out),'source/authority entries')
if __name__=='__main__':main()
