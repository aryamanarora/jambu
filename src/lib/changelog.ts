export type ChangelogEntry = {
	date: string;
	label: string;
	title: string;
	changes: string[];
	ingested?: {
		languages: ChangelogLink[];
		sources: ChangelogLink[];
	};
};

type ChangelogLink = {
	id: string;
	label: string;
};

// Keep entries newest-first. Dates are split into an ISO value and a display label so the
// homepage remains deterministic when it is prerendered in a different timezone.
export const changelog: ChangelogEntry[] = [
	{
		date: '2026-09-26',
		label: '26 September 2026',
		title: 'Historical vocabularies, native witnesses and reviewed source expansions',
		changes: [
			"Added reviewed Munda dictionary and archive material: CUJ Asur; paired print and online CFEL Koda dictionaries; CFEL Mahali; the preserved Gorum, Gtaʔ and Kharia MLA responses; and the archived A–C portion of Deeney’s Ho dictionary. Printed senses, native spelling, grammatical labels and uncertain source claims remain distinct.",
			"Recovered Norton’s Korku grammar and bidirectional vocabulary, Hahn’s Asur primer including expressions and song, Crooke’s Korwa glossary, Samuells’s Juang article, Dalton–Haldar’s Juang columns and list, Hislop’s Kuri/Muasi material, Prendergast’s Savara vocabulary and Roy’s Birhor Appendix I. Specific damaged or ambiguous readings remain documented.",
			"Added Grierson’s Haijong, Handuri, Kaikadi, Kanjari, Koda, Korvi/Yerukula, Rangri, Sansi, Shoracholi, Sikalgari, Simla Siraji, Sodochi, Suketi, Turi and Holiya material: source-attributed grammar, specimens and comparative tables where supplied. Native witnesses and exact repeated attestations retain their citations; later Kaikadi and Korvi corrections are separate witnesses.",
			"Added Bailey chapters and vocabularies for Bhadrawahi, Bhalesi, Inner and Outer Siraji, Kiunthali, Kotguru, Kotkhai, Padari, Poguli, Rambani, Sainji and Surkhuli, plus the Baghi, Bilaspuri, Kagani, North Jubbal, Rampur and Rohru glossaries. The installed Rohru scope is the glossary; paused chapter-recovery drafts are not included.",
			"Added Bhattacharya’s Ollari vocabulary, Bhat’s Belari appendix, the Gutob and Gorum SIL survey lists, the Pattapu ISO wordlist and credited numeral tables across Dravidian varieties. Kept primary-source attestations distinct from Lindgren’s derived dataset and added source-comparison qualifications to the latter.",
			"Added scoped modern sources: Das and colleagues’ Yerava comparative table, Peterson and colleagues’ Turi Appendix 1, Gaddi lexical and numeral Appendices II–III, Niranjan’s Chakma main wordlist and Dhakal’s Darai chapter 3. These do not represent whole-book ingestion; pending Darai recovery and other uninstalled proposals are excluded.",
			"Updated shared house-transcription profiles while preserving original spelling, authorial phonemic input, hyphens and source-specific marks. Expanded grammatical and register labels, including argot, classifier, prospective and non-past, and preserved uncertain readings without invented pronunciation. Fixed duplicate-attestation merging so site dialect and grammatical tags survive together, restoring tags on 10,654 existing compiled records across 93 languages without changing their lexical content.",
			"Grouped shape-inferred CDIAL reflexes under explicitly inferred extension nodes. Updated derivation-aware deduplication and entry graphs so same-language derived terms remain distinct from cross-language compounds and derivatives; retained aliases for changed identities.",
			"Added source-keyed comparative prose and corrected native-script, sense and reference handling across the new source packages, including provenance links with explanatory filename notes. Isolated browser database coordination by release version so older tabs cannot answer queries for a newer database. Release downloads are checked against their exact published hashes. The download budget rises from 60 to 65 MB for the expanded corpus (about 60.77 MB compressed)."
		],
		ingested: {
			languages: [
				{ id: "Adilabad Gondi", label: "Adilabad Gondi" },
				{ id: "AdivasiOriya", label: "Adivasi Oriya" },
				{ id: "Aheri Gondi", label: "Aheri Gondi" },
				{ id: "AluKurumba", label: "Alu Kurumba" },
				{ id: "amri_karbi", label: "Amri Karbi" },
				{ id: "Aranadan", label: "Aranadan" },
				{ id: "As", label: "Ashokan Prakrit" },
				{ id: "Asuri", label: "Asuri" },
				{ id: "bagheli_lakshman", label: "Bagheli" },
				{ id: "ba", label: "Baghi" },
				{ id: "bagri_fatehabad", label: "Bagri" },
				{ id: "Barari", label: "Barari" },
				{ id: "Belari", label: "Belari" },
				{ id: "BettaKurumba", label: "Betta Kurumba" },
				{ id: "bhad", label: "Bhadrawahi" },
				{ id: "bhal", label: "Bhalesi" },
				{ id: "bil", label: "Bilaspuri" },
				{ id: "Birhor", label: "Birhor" },
				{ id: "Bote", label: "Bote" },
				{ id: "Brahui", label: "Brahui" },
				{ id: "Brj", label: "Braj" },
				{ id: "Bugun", label: "Bugun" },
				{ id: "bfu", label: "Bunan (Gahri)" },
				{ id: "bundeli_atarra", label: "Bundeli" },
				{ id: "Chakma", label: "Chakma" },
				{ id: "NDu", label: "Chhattisgarhi" },
				{ id: "cih", label: "Chinali" },
				{ id: "Dakpakha", label: "Dakpakha (Tawang Monpa)" },
				{ id: "Dandami Maria", label: "Dandami Maria" },
				{ id: "Darai", label: "Darai" },
				{ id: "dhundari_bamore", label: "Dhundari" },
				{ id: "as", label: "Domari" },
				{ id: "Dotyali", label: "Dotyali" },
				{ id: "EasternGorkhaTamang", label: "Eastern Gorkha Tamang" },
				{ id: "Eastern Muria", label: "Eastern Muria" },
				{ id: "Eravallan", label: "Eravallan" },
				{ id: "eur", label: "European Romani" },
				{ id: "Gadaba", label: "Gadaba" },
				{ id: "ga", label: "Gaddi" },
				{ id: "Gondi", label: "Gondi" },
				{ id: "go", label: "Gorum" },
				{ id: "gt", label: "Gtaʔ" },
				{ id: "Goj", label: "Gujari" },
				{ id: "Gurung", label: "Gurung" },
				{ id: "gu", label: "Gutob" },
				{ id: "had", label: "Hadauti" },
				{ id: "Hajong", label: "Hajong" },
				{ id: "Hinduri", label: "Hinduri" },
				{ id: "ho", label: "Ho" },
				{ id: "Holiya", label: "Holiya" },
				{ id: "Humla", label: "Humla Tibetan" },
				{ id: "Kal", label: "Indo-Aryan Kalasha" },
				{ id: "insir", label: "Inner Siraji" },
				{ id: "Jennu Kurumba", label: "Jennu Kurumba" },
				{ id: "ju", label: "Juang" },
				{ id: "Kaikadi", label: "Kaikadi" },
				{ id: "Kakkala", label: "Kakkala" },
				{ id: "KalaktangMonpa", label: "Kalaktang Monpa" },
				{ id: "Kam", label: "Kamviri" },
				{ id: "Kanjari", label: "Kanjari" },
				{ id: "Kannada", label: "Kannada" },
				{ id: "karbi", label: "Karbi" },
				{ id: "Kt", label: "Katë" },
				{ id: "kh", label: "Kharia" },
				{ id: "Khirwar", label: "Khirwar" },
				{ id: "Kho", label: "Khowar" },
				{ id: "kiuth", label: "Kiunthali" },
				{ id: "KochilaTharu", label: "Kochila Tharu" },
				{ id: "Koda", label: "Koda" },
				{ id: "Kodagu", label: "Kodagu" },
				{ id: "Kodaku", label: "Kodaku" },
				{ id: "Kolami", label: "Kolami" },
				{ id: "Konda", label: "Konda" },
				{ id: "Koraga", label: "Koraga" },
				{ id: "ko", label: "Korku" },
				{ id: "Korra Koraga", label: "Korra Koraga" },
				{ id: "kw", label: "Korwa" },
				{ id: "Kota", label: "Kota" },
				{ id: "Kotguru", label: "Kotguru" },
				{ id: "Kotkhai", label: "Kotkhai" },
				{ id: "Koya", label: "Koya" },
				{ id: "Kudiya", label: "Kudiya" },
				{ id: "Kui", label: "Kui" },
				{ id: "kul", label: "Kullui" },
				{ id: "Kumarbhag Paharia", label: "Kumarbhag Paharia" },
				{ id: "Kurux", label: "Kurux" },
				{ id: "Kuwi", label: "Kuwi" },
				{ id: "lhl", label: "Lahul Lohar" },
				{ id: "Lohorung", label: "Lohorung" },
				{ id: "Loy", label: "Loke" },
				{ id: "Mahali", label: "Mahali" },
				{ id: "Majhi", label: "Majhi" },
				{ id: "Malasar", label: "Malasar" },
				{ id: "Malayalam", label: "Malayalam" },
				{ id: "Malto", label: "Malto" },
				{ id: "mewari_basad", label: "Malvi" },
				{ id: "Malw", label: "Malwai" },
				{ id: "Manda", label: "Manda" },
				{ id: "M", label: "Marathi" },
				{ id: "Maria (India)", label: "Maria (India)" },
				{ id: "Marw", label: "Marwari" },
				{ id: "mewari_dholpura", label: "Mewari" },
				{ id: "mewati_akera", label: "Mewati" },
				{ id: "Miji", label: "Miji" },
				{ id: "Muduga", label: "Muduga" },
				{ id: "Mullu Kurumba", label: "Mullu Kurumba" },
				{ id: "Naikri", label: "Naikri" },
				{ id: "New", label: "Newari" },
				{ id: "Ni", label: "Nihali" },
				{ id: "NorthernGhale", label: "Northern Ghale" },
				{ id: "Northern Hindko", label: "Northern Hindko" },
				{ id: "Wg", label: "Nuristani Kalasha" },
				{ id: "Nyishi", label: "Nyishi-Hill Miri" },
				{ id: "OSi", label: "Old Sinhala" },
				{ id: "OllariGadaba", label: "Ollari Gadaba" },
				{ id: "OuterSiraji", label: "Outer Siraji" },
				{ id: "Padri", label: "Padri" },
				{ id: "Phal", label: "Palula" },
				{ id: "Paniya", label: "Paniya" },
				{ id: "Parji", label: "Parji" },
				{ id: "Psht", label: "Pashto" },
				{ id: "lae", label: "Pattani" },
				{ id: "Pattapu", label: "Pattapu" },
				{ id: "Pengo", label: "Pengo" },
				{ id: "pog", label: "Poguli" },
				{ id: "Pr", label: "Prasun" },
				{ id: "Puroik", label: "Puroik" },
				{ id: "Rabha", label: "Rabha" },
				{ id: "Rj", label: "Rajasthani" },
				{ id: "ram", label: "Rambani" },
				{ id: "ramp", label: "Rampuri" },
				{ id: "Ravula", label: "Ravula" },
				{ id: "re", label: "Remo" },
				{ id: "roh", label: "Rohrui" },
				{ id: "sai", label: "Sainji" },
				{ id: "Sansi", label: "Sansi" },
				{ id: "Sartang", label: "Sartang" },
				{ id: "dhundari_badagaon", label: "Shekhawati" },
				{ id: "Sherdukpen", label: "Sherdukpen" },
				{ id: "ShimlaSiraji", label: "Shimla Siraji" },
				{ id: "Shoracholi", label: "Shoracholi" },
				{ id: "Sik", label: "Sikalgari" },
				{ id: "so", label: "Sora" },
				{ id: "SouthernGhale", label: "Southern Ghale" },
				{ id: "SouthernYamphu", label: "Southern Yamphu" },
				{ id: "sbu", label: "Stod Bhoti" },
				{ id: "suk", label: "Suketi" },
				{ id: "surkh", label: "Surkhuli" },
				{ id: "Tagin", label: "Tagin" },
				{ id: "Tamil", label: "Tamil" },
				{ id: "Telugu", label: "Telugu" },
				{ id: "Ths", label: "Thakali" },
				{ id: "lbf", label: "Tinani" },
				{ id: "Toda", label: "Toda" },
				{ id: "Tshangla", label: "Tshangla" },
				{ id: "Tulu", label: "Tulu" },
				{ id: "Turi", label: "Turi" },
				{ id: "VB", label: "Vaagri Boli" },
				{ id: "WK", label: "Wadiyara Koli" },
				{ id: "mewari_bannoda", label: "Wagri" },
				{ id: "Kjl", label: "Western Parbate Kham" },
				{ id: "Yamphu", label: "Yamphu" },
				{ id: "Yerukula", label: "Yerukula" },
			],
			sources: [
				{ id: "DHED", label: "Deeney, Ho–English Dictionary (archived A–C)" },
				{ id: "DSGO", label: "Donegan–Stampe, Gorum (MLA)" },
				{ id: "DSGT", label: "Chatterji Gtaʔ vocabulary (MLA)" },
				{ id: "DSKH", label: "Kharia lexical archive (MLA)" },
				{ id: "andronov1995koya", label: "Andronov–India, Koya Numeral List (1995)" },
				{ id: "babu2018malasar", label: "Babu, Malasar Numeral List (2018)" },
				{ id: "bailey1908bhadrawahi", label: "Bailey, Bhadrawahi (1908)" },
				{ id: "bailey1908bhalesi", label: "Bailey, Bhalesi (1908)" },
				{ id: "bailey1908innersiraji", label: "Bailey, Inner Siraji (1908)" },
				{ id: "bailey1908kiunthali", label: "Bailey, Kiunthali (1908)" },
				{ id: "bailey1908kotguru", label: "Bailey, Kotguru (1908)" },
				{ id: "bailey1908kotkhai", label: "Bailey, Kotkhai (1908)" },
				{ id: "bailey1908outersiraji", label: "Bailey, Outer Siraji (1908)" },
				{ id: "bailey1908padari", label: "Bailey, Padari (1908)" },
				{ id: "bailey1908poguli", label: "Bailey, Poguli (1908)" },
				{ id: "bailey1908rambani", label: "Bailey, Rambani (1908)" },
				{ id: "bailey1908sainji", label: "Bailey, Sainji (1908)" },
				{ id: "bailey1920baghi", label: "Bailey, Baghi (1920)" },
				{ id: "bailey1920bilaspuri", label: "Bailey, Bilaspuri (1920)" },
				{ id: "bailey1920kagani", label: "Bailey, Kagani (1920)" },
				{ id: "bailey1920northjubbal", label: "Bailey, North Jubbal (1920)" },
				{ id: "bailey1920rampur", label: "Bailey, Rampur (1920)" },
				{ id: "bailey1920rohru", label: "Bailey, Rohru (1920)" },
				{ id: "bailey1920surkhuli", label: "Bailey, Surkhuli (1920)" },
				{ id: "bhat1971koraga", label: "Bhat, Belari appendix to The Koraga Language" },
				{ id: "bhattacharya1957ollari", label: "Bhattacharya, Ollari vocabulary" },
				{ id: "cfel2026koda", label: "CFEL Visva-Bharati, Koda Online Dictionary (2026)" },
				{ id: "crooke1892korwa", label: "Crooke, A Vocabulary of the Korwa Language (1892)" },
				{ id: "cuj2020asur", label: "CUJ, Asur–Hindi–English Dictionary" },
				{ id: "cust1884korku", label: "Norton, Korku grammar and vocabulary (Cust 1884)" },
				{ id: "dalton1872haldarjuang", label: "Dalton–Haldar, Juang comparative column and list" },
				{ id: "daniel2013paniya", label: "Daniel, Paniyan Numeral List (2013)" },
				{ id: "das1987yerava", label: "Das et al., Yerava comparative wordlist" },
				{ id: "dhakal2011darai", label: "Dhakal, The Darai Language (chapter 3)" },
				{ id: "edward2019kumarbhag", label: "Edward, Kumarbhag Paharia Numeral List (2019)" },
				{ id: "erza2015pattapu", label: "Erza–Edward, Pattapu Numeral List (2015)" },
				{ id: "grierson1903haijong", label: "Grierson, Haijong (LSI V.I)" },
				{ id: "grierson1906holiya", label: "Grierson, Gōlarī (or Hōliyā) (1906)" },
				{ id: "grierson1906kaikadi", label: "Grierson, Kaikāḍī (1906)" },
				{ id: "grierson1906korava", label: "Grierson, Korava or Yerukala (1906)" },
				{ id: "grierson1906lsi4", label: "Grierson, Koda and Turi (LSI IV)" },
				{ id: "grierson1908malvirangri", label: "Grierson, Rangri (LSI IX.II)" },
				{ id: "grierson1916handuri", label: "Grierson, Handuri (LSI IX.IV)" },
				{ id: "grierson1916shoracholi", label: "Grierson, Shoracholi (LSI IX.IV)" },
				{ id: "grierson1916simlasiraji", label: "Grierson, Simla Siraji (LSI IX.IV)" },
				{ id: "grierson1916sodochi", label: "Grierson, Sodochi (LSI IX.IV)" },
				{ id: "grierson1916suketi", label: "Grierson, Suketi (LSI IX.IV)" },
				{ id: "grierson1922lsi11", label: "Grierson, Sansi, Kanjari and Sikalgari (LSI XI)" },
				{ id: "grierson_addenda_minora_iv_boundin", label: "LSI IV, bound-in Addenda Minora (undated witness)" },
				{ id: "hahn1900asur", label: "Hahn, A Primer of the Asur Dukmā, a Dialect of the Kolarian Language (1900)" },
				{ id: "hislop1866papers", label: "Hislop, Kuri/Muasi wordlists" },
				{ id: "jeba2018jennukurumba", label: "Jeba, Jennu Kurumba Numeral List (2018)" },
				{ id: "jeba2018mullu", label: "Jeba, Mullu Kurumba Numeral List (2018)" },
				{ id: "john2013pottangiollargadaba", label: "John, Pottangi Ollar Gadaba Numeral List (2013)" },
				{ id: "kapp1995alukurumba", label: "Kapp, Alu Kurumba Numeral List (1995)" },
				{ id: "kardile2013southeasternkolami", label: "Kardile, Southeastern Kolami Numeral List (2013)" },
				{ id: "kujur-perumalsamy2018kisan", label: "Kujur–Perumalsamy, Kisan (Odisha) Numeral Lists (2018)" },
				{ id: "kumari2026gaddi", label: "Kumari et al., Gaddi lexical and numeral appendices" },
				{ id: "kuriakose2018muduga", label: "Kuriakose–Daniel, Muduga Numeral List (2018)" },
				{ id: "kurian2018aherigondi", label: "Kurian, Aheri Gondi Numeral List (2018)" },
				{ id: "lindgren2023dravidian", label: "Lindgren, Dravidian dataset (source comparison)" },
				{ id: "mathew-chamberlain2022bonda-didayi", label: "Mathew–Chamberlain, Gutob and Gorum survey lists" },
				{ id: "metry2017holiya", label: "Metry, Holiya Numeral Elicitation (2017)" },
				{ id: "mini2018khirwar", label: "Mini, Khirwar Numeral List (2018)" },
				{ id: "nagaraja2014", label: "Nagaraja, Nihali vocabulary" },
				{ id: "nair2017kakkala", label: "Nair, Kakkala Numeral List (2017)" },
				{ id: "niranjan2010chakma", label: "Niranjan, Chakma main wordlist" },
				{ id: "penny2017adilabadgondi", label: "Penny, Western Southern Gondi (Adilabad Gondi) Numeral List (2017)" },
				{ id: "peterson2024turi", label: "Peterson et al., Turi wordlist (Appendix 1)" },
				{ id: "pradhan-tripathi2022koda", label: "Pradhan–Tripathi, English–Hindi–Bangla–Koda Dictionary (2022)" },
				{ id: "pradhan-tripathi2022koda-native", label: "Pradhan–Tripathi, Koda–Bangla–Hindi–English Dictionary (2022)" },
				{ id: "pradhan-tripathi2024mahali", label: "Pradhan–Tripathi, Mahali–Bangla–Hindi–English Dictionary (2024)" },
				{ id: "prendergast1881savara", label: "Prendergast, Savara vocabulary" },
				{ id: "rebbavarapu2013pattapu", label: "Rebbavarapu, Pattapu ISO wordlist" },
				{ id: "riezen2013easternmuria", label: "Riezen, Eastern Muria Numeral List (2013)" },
				{ id: "rosemary2017aranadan", label: "Rose Mary–Swaraj Prabha, Aranadan Numeral Elicitation (2017)" },
				{ id: "roy1925birhors", label: "Roy, Birhor vocabulary (Appendix I)" },
				{ id: "samuells1856juang", label: "Samuells, Juang vocabulary and expressions" },
				{ id: "selvaraj1996bettakurumba", label: "Selvaraj, Betta Kurumba Numeral List (1996)" },
				{ id: "sharma1990korra", label: "Sharma, Korra Koraga Numeral List (1990)" },
				{ id: "sounderaraj1995dandamimaria", label: "Sounderaraj–Sounderaraj, Bison-Horn Madiya Numeral List (1995)" },
				{ id: "vaz2011hillmaria", label: "Vaz, Hill Madia Numeral List from Bhamragad (2011)" },
				{ id: "vijayan2018eravallan", label: "Vijayan, Eravallan Numeral List (2018)" }
			]
		}
	},
	{
		date: '2026-09-18',
		label: '18 September 2026',
		title: 'Survey-site coordinates, resolved dictionary glosses, and no more non-word rows',
		changes: [
			'Reviewed the map location of 587 survey-site dialects that had been sharing one coordinate with their parent language or a sibling site, each placed by hand from the survey’s own site descriptions, gazetteers, and OpenStreetMap: Pashai and Prasun villages, the Bhil, Malvi, Bagheli, Kullu, Pothwari, Ho, Korwa, Koya, Desia, Karbi and Kurumba lists, Zoller’s West Pahari toponyms, and Romani country centroids. 1,967 dialects are now located at 1,732 distinct points (was 1,569 at 1,317), and 25 more languages have a centroid.',
			'Resolved Turner’s and Burrow–Emeneau’s “id.” and “do.” glosses to the meaning they refer back to, including chains and the entry-initial meaning stated only in the headword, so those forms carry a real gloss instead of an abbreviation.',
			'Filled 10,375 blank CDIAL glosses (15,353 → 4,978) following Turner’s conventions: an unglossed reflex takes the headword or the meaning printed for its run, borrowings inherit the lender’s gloss, and “the tree” / “its fruit” shorthand is anchored to the sense it abbreviates. Forward grammatical labels (m., f., impv., instr., …) are stored as notes and tags rather than left in the gloss.',
			'Removed 1,118 CDIAL rows that were never words: sound-change fragments such as “-kk-” and “ch-”, and starred reconstructions quoted inside the discussion, which are now kept as notes on the form they explain.',
			'Repaired botanical markup in DEDR so Latin species names stay attached to their common-name glosses.',
			'Refreshed the dictionary: 792,933 browser records in a 55.93 MB download.'
		]
	},
	{
		date: '2026-09-16',
		label: '16 September 2026',
		title: 'Sheth’s Prakrit dictionary, Munda surveys, and 38,000 reviewed etymologies',
		changes: [
			'Added Sheth’s Paia-sadda-mahannavo (1923–1928) from the Digital Dictionaries of South Asia transcription: 42,118 Prakrit headword, sense, and alternate records from 31,501 articles, with 26,191 source-local Sanskrit equivalents and 27,484 lexical comparison links kept as comparisons rather than asserted ancestry.',
			'Added three manually keyed SIL Munda surveys: fourteen Ho field lists (Varenkamp 2024, 2,900 cells), ten Bhumij and Bhumij-Mundari lists (Bailey and Maggard 2015, 2,100 cells), and four Dhurwa lists (Joseph and Joseph 2021, 809 cells), each transcribed cell by cell from the source images.',
			'Re-parsed Berger’s Burushaski dictionary from a repaired image, font, and column extraction (3,743 gold records restored, 1,068 more automatic entries) and Yoshioka’s Eastern Burushaski glossary with checked cross-references (1,703 more records); superseded parsing fragments are retired through recorded aliases so existing links survive.',
			'Etymologised 38,549 previously unlinked survey attestations across 77 languages in a joint review of the Indo-Aryan SIL surveys: Gondi, Nimadi, Pothwari, Gojri, Hajong, Mewari, Awankari, Dangaura Tharu, Rathwi and Pauri Bareli, Bhilali, Haryanvi, Bhatri, Jaunsari, Bagheli, Rana Tharu, Magahi, Noiri, Bishnupriya, Danuwar, Bundeli, Dotyali, Adivasi Oriya, Majhi, and the Kannauji, Rajasthani, Tharu, Kalkoti, Palula, and northern Pakistan survey lists. Accepted links cite CDIAL or DEDR with the reviewer’s evidence; uncertain cases are held, not guessed.',
			'Registered reviewed Mewari regional lexical families and donor heads for the central surveys, and grouped Nuristani reflexes under their CDIAL heads.',
			'Curated etymologies now live beside each source in per-source sidecar files, and every source declares its transcription, identity, and reference settings in a sibling YAML file, replacing per-source branches in the build.',
			'Markodi wordlist cells are now individually keyed, so a form elicited for two concepts is two attestations; three previously merged cells are separated.',
			'Refreshed the dictionary with the latest ingested sources: 794,256 browser records in a 55.97 MB download. The download budget rises from 50 to 60 MB to carry Sheth’s articles.'
		],
		ingested: {
			languages: [
				{ id: 'Pk', label: 'Prakrit' },
				{ id: 'Ap', label: 'Apabhramsha' },
				{ id: 'As', label: 'Ashokan Prakrit' },
				{ id: 'ho', label: 'Ho' },
				{ id: 'mu', label: 'Mundari (Bhumij)' },
				{ id: 'Parji', label: 'Dhurwa (Parji)' },
				{ id: 'Bur', label: 'Burushaski' },
				{ id: 'Gondi', label: 'Gondi' },
				{ id: 'Nimadi', label: 'Nimadi' },
				{ id: 'poth', label: 'Pothwari' },
				{ id: 'Goj', label: 'Gojri' },
				{ id: 'Hajong', label: 'Hajong' },
				{ id: 'mewari_basad', label: 'Mewari' },
				{ id: 'awan', label: 'Awankari' },
				{ id: 'Dang', label: 'Dangaura Tharu' },
				{ id: 'RathwiBareli', label: 'Rathwi Bareli' },
				{ id: 'Bhilali', label: 'Bhilali' },
				{ id: 'kaithal', label: 'Haryanvi' },
				{ id: 'Bhatri', label: 'Bhatri' },
				{ id: 'jaun', label: 'Jaunsari' },
				{ id: 'bagheli_lakshman', label: 'Bagheli' },
				{ id: 'Rana', label: 'Rana Tharu' },
				{ id: 'MagahiNepal', label: 'Magahi' },
				{ id: 'Noiri', label: 'Noiri' },
				{ id: 'Bishnupriya', label: 'Bishnupriya' },
				{ id: 'markodi', label: 'Markodi' }
			],
			sources: [
				{ id: 'sheth1923', label: 'Sheth, Paia-sadda-mahannavo (DDSA)' },
				{ id: 'varenkamp2024ho', label: 'Varenkamp, A study of Ho dialects (SIL 2024)' },
				{ id: 'baileymaggard2015bhumij', label: 'Bailey and Maggard, Bhumij survey (SIL 2015)' },
				{ id: 'josephmichael2021dhurwa', label: 'Joseph and Joseph, Dhurwa survey (JLSR 2021)' },
				{ id: 'berger', label: 'Berger, Die Burushaski-Sprache (re-parsed)' },
				{ id: 'yoshioka2012', label: 'Yoshioka, Eastern Burushaski glossary (re-parsed)' }
			]
		}
	},
	{
		date: '2026-09-13',
		label: '13 September 2026',
		title: 'New dialect surveys, dictionaries, and Zoller comparative vocabulary',
		changes: [
			'Standardised search filters, source selection, pagination, sound-alignment chips, and the responsive layouts of language and source pages.',
			'Compare sound correspondences with three inputs: ancestor patterns and Entries search filters, descendant languages, and outcome classes such as aligned sounds or tone.',
			'Filter comparison languages by total forms or matching outcome forms, using the same searchable language picker as Favorites and form filters.',
			'Choose an aligned target within a larger sound pattern, such as k between vowels; a class picker helps build patterns and parsed chips distinguish the target from its context.',
			'Group ancestor table columns by sound properties or form properties, including accent, syllable count, and weight patterns; use the same groups on the map and open downloadable evidence from each pie.',
			'Added a release checklist to keep source coverage, data publication, and deployment verification consistent.',
			'Added 17,754 attestations from the linguistic data sections of Zoller’s 2023 study, spanning 328 languages after separating its West Pahari varieties, with exact source locators.',
			'Preserved source transcription, 341 direct CDIAL links, and 70 explicit variant links; unresolved comparisons remain unlinked.',
			'Separated 15 named West Pahari varieties into individual languages in the West Pahari clade, including Bangani, Deogari, Himachali, Khashdhari, and Padri; kept unspecified attestations clearly labelled.',
			"Added the online Survey of Dialects of the Marathi Language, Ghatage’s South Kanara Konkani and Kudali vocabularies, and the Dadra and Nagar Haveli Varli survey.",
			"Added the Nirmaan Mewari Dictionary, Kharia Living Dictionary, and the vocabulary in Seligmann’s The Veddas.",
			"Expanded Dravidian coverage with DravLex, the Lindgren comparative dataset, the Kannada-English Etymological Dictionary (KEED), Bhat’s Koraga lexicon, and Arsenault and Abraham’s Muduga data.",
			"Added Census linguistic surveys for Tamil Nadu, Uttar Pradesh, Bihar, Sikkim, Jharkhand, Himachal Pradesh, Rajasthan, West Bengal, and Orissa.",
			"Added the Nepal surveys of Bajjika, Danuwar, Tharu, Kisan, Angika, and Majhi.",
			"This release includes 28 newly ingested primary sources and 73 supporting bibliographic references, including the works cited through KEED and DravLex.",
			'Refreshed the dictionary with the latest ingested sources: 720,736 browser records in a 48.80 MB download.',
			'Fixed decoding of large compressed databases and added lossless verification before staging.',
			'Simplified the sources list with reference pills, clade coverage on form-count hover, and one-click BibTeX copying.',
			'Aligned source and language pages, placed form searches above the tables, and removed map-point shadows.',
			'Published a Dardic–Plains lexical comparison with interactive evidence maps and downloadable research tables.'
		],
		ingested: {
			languages: [
				{ id: 'Bangani', label: 'Bangani' },
				{ id: 'Deogari', label: 'Deogari' },
				{ id: 'Himachali', label: 'Himachali' },
				{ id: 'Padri', label: 'Padri' },
				{ id: 'Pr', label: 'Prasun' },
				{ id: 'kw', label: 'Korwa' },
				{ id: 'Tampuan', label: 'Tampuan' },
				{ id: "M", label: "Marathi" },
				{ id: "Kannada", label: "Kannada" },
				{ id: "mewari_dholpura", label: "Mewari" },
				{ id: "kh", label: "Kharia" },
				{ id: "Vedda", label: "Vedda" },
				{ id: "Varli", label: "Varli" },
				{ id: "Koraga", label: "Koraga" },
				{ id: "Muduga", label: "Muduga" },
				{ id: "Angika", label: "Angika" },
				{ id: "KisanIA", label: "Kisan" },
				{ id: "Majhi", label: "Majhi" }
			],
			sources: [
				{ id: "nirmaan2018mewari", label: "Nirmaan · Mewari" },
				{ id: "seligmann1911vedda", label: "Seligmann 1911 · Vedda" },
				{ id: "pattanaik-koul2003varli", label: "LSI 2003 · Varli" },
				{ id: "ghatage-konkani1963", label: "Ghatage 1963 · Konkani" },
				{ id: "ghatage-kudali1965", label: "Ghatage 1965 · Kudali" },
				{ id: "living-kharia2026", label: "Kharia Living Dictionary" },
				{ id: "sdml2026", label: "Marathi dialect survey online" },
				{ id: "regmi2014bajjika", label: "Regmi 2014 · Bajjika" },
				{ id: "lindgren2023dravidian", label: "Lindgren 2023 · Dravidian" },
				{ id: "kolipakam2018dravlex", label: "DravLex 2018" },
				{ id: "census2023tamilnadu", label: "LSI · Tamil Nadu" },
				{ id: "census2023uttarpradesh", label: "LSI · Uttar Pradesh" },
				{ id: "census2020bihar", label: "LSI · Bihar" },
				{ id: "census2012sikkim2", label: "LSI · Sikkim II" },
				{ id: "regmi-thakur2016danuwar", label: "Regmi & Thakur · Danuwar" },
				{ id: "mitchell-eichentopf2013tharu", label: "Mitchell & Eichentopf · Tharu" },
				{ id: "census2023jharkhand", label: "LSI · Jharkhand" },
				{ id: "census2023himachal", label: "LSI · Himachal Pradesh" },
				{ id: "census2011rajasthan", label: "LSI · Rajasthan I" },
				{ id: "census2016westbengal", label: "LSI · West Bengal I" },
				{ id: "mahato2014kisan", label: "Mahato 2014 · Kisan" },
				{ id: "regmi2017angika", label: "Regmi 2017 · Angika" },
				{ id: "chalise2014majhi", label: "Chalise 2014 · Majhi" },
				{ id: "bhat1971koraga", label: "Bhat 1971 · Koraga" },
				{ id: "census2002orissa", label: "LSI · Orissa" },
				{ id: "arsenault-abraham2022muduga", label: "Arsenault & Abraham · Muduga" },
				{ id: "uchida-rajapurohit2018", label: "KEED 2018 · Kannada" },
				{ id: "zoller2023", label: "Zoller 2023" }
			]
		}
	},
	{
		date: '2026-09-10',
		label: '10 September 2026',
		title: 'Dameli vocabulary, reviewed etymologies, and research essays',
		changes: [
			'Added vocabulary from Perder’s Dameli grammar, preserving source transcription, grammatical tags, and exact citations.',
			'Expanded reviewed etymologies and donor links for Dameli, Kalkoti, Shina, Brokskat, Palula, Sauji, and Ushojo, including derivations and compound analyses.',
			'Published quantitative essays on Telugu metathesis and Shinaic accent, with annotated examples, interactive charts, and downloadable evidence.',
			'Entry pages now organize word forms, meanings, sources, and descendant coverage more clearly.',
			'Rebuilt the dictionary with 591,456 records and a 43.34 MB browser download.'
		],
		ingested: {
			languages: [
				{ id: 'Dm', label: 'Dameli' },
				{ id: 'Kalk', label: 'Kalkoti' },
				{ id: 'Sh', label: 'Shina' },
				{ id: 'bro', label: 'Brokskat' },
				{ id: 'Phal', label: 'Palula' },
				{ id: 'Sv', label: 'Sauji' },
				{ id: 'Ush', label: 'Ushojo' }
			],
			sources: [
				{ id: 'perder2013dameli', label: 'Perder 2013' },
				{ id: 'oped2026', label: 'Open Pashto-English Dictionary' }
			]
		}
	},
	{
		date: '2026-09-08',
		label: '8 September 2026',
		title: 'Kusunda sources and Nihali etymologies',
		changes: [
			'Entry pages now give words and meanings a clearer header, organize sources and descendant coverage, and offer useful next steps when no descendants are recorded.',
			'Added Blogs: static essays with human or agent attribution and links to dictionary forms, entries, concepts, languages, and sources.',
			'Added Kusunda vocabulary from Aaley and Bodt, Watters, and Aaley’s Kusunda Gipan, preserving source spellings, grammatical information, and exact citations.',
			'Expanded Nihali etymological groupings and source comparisons, keeping provisional analyses and uncertain contact proposals visible.',
			'The dictionary now downloads as a smaller compressed file and restores into the browser’s local cache, preserving its lexical evidence and search features.',
			'Cleaned editorial notes while retaining their source evidence and stable form links.'
		],
		ingested: {
			languages: [{ id: 'Kusunda', label: 'Kusunda' }],
			sources: [
				{ id: 'aaley-bodt2020kusunda', label: 'Aaley & Bodt 2020' },
				{ id: 'watters2006kusunda', label: 'Watters 2006' },
				{ id: 'aaley2021kusundagipan', label: 'Aaley 2021' }
			]
		}
	},
	{
		date: '2026-09-01',
		label: '1 September 2026',
		title: 'A lighter dictionary download',
		changes: [
			'The complete dictionary download is now 42.54 MB—less than half its former size—while preserving every entry, citation locator, structured tag, article block, alignment, alias, and graph relation.'
		]
	},
	{
		date: '2026-08-30',
		label: '30 August 2026',
		title: 'Survey wordlists and a broader dialect atlas',
		changes: [
			'Added 139,355 forms, 96 references, 57 languages, and 582 named dialects from modern surveys and historical lexical sources across South Asia.',
			'Completed 20,734 scan-backed survey records for Western Tharu, Irula, Koch and Kurux in Bangladesh, Kurumba, Northern Dhule Bhils, Noira, Adi, and Haryanvi, preserving hand-transcribed IPA, exact page and item citations, and each survey site as a dialect.',
			'Expanded Munda, Indo-Aryan, Nuristani, and Romani coverage with reproducible source audits, stable form identities, and clearer source-specific dialect handling.',
			'Language and concept browsing now uses an atlas-style map and reusable browse cards; correspondences, isoglosses, entry evidence, filters, and source links are easier to inspect across desktop and mobile.'
		],
		ingested: {
			languages: [
				{ id: 'Buksa', label: 'Bhuksa Tharu' },
				{ id: 'Irula', label: 'Irula' },
				{ id: 'AluKurumba', label: 'Alu Kurumba' },
				{ id: 'Koch', label: 'Koch' },
				{ id: 'Kurux', label: 'Kurux' },
				{ id: 'Vasavi', label: 'Vasavi' },
				{ id: 'Noiri', label: 'Noiri' },
				{ id: 'MisingPadamMiriMinyong', label: 'Adi varieties' },
				{ id: 'kaithal', label: 'Haryanvi' }
			],
			sources: [
				{ id: 'webster', label: 'Webster 2017 · manual IPA' },
				{ id: 'ernest-oleary-kelsall2018irula', label: 'Ernest et al. 2018' },
				{ id: 'blairetal2012kurumba', label: 'Blair et al. 2012' },
				{ id: 'kim-ahmad-kim-sangma2011kochbd', label: 'Kim et al. 2011 · Koch' },
				{ id: 'kim-ahmad-kim-sangma2011kurux', label: 'Kim et al. 2011 · Kurux' },
				{ id: 'watters2013northerndhule', label: 'Watters 2013' },
				{ id: 'varghesekumar2015noira', label: 'Varghese & Kumar 2015' },
				{ id: 'padung-sako2015adi', label: 'Padung & Sako 2015' },
				{ id: 'webster2024haryanvi', label: 'Webster 2024' }
			]
		}
	},
	{
		date: '2026-08-28',
		label: '28 August 2026',
		title: 'Best guesses in concept maps',
		changes: [
			'Concept maps can now preview strong phonological matches for unetymologised forms, using only etyma already attested for that meaning and keeping every suggestion visibly marked.'
		]
	},
	{
		date: '2026-08-25',
		label: '25 August 2026',
		title: 'Corpus totals on the homepage',
		changes: [
			'The homepage now opens with the size of the corpus — headwords, forms, languages, dialects, concepts, and sources — with each figure linking to the list it counts.',
			'Source pages open immediately. The cited-form list, its count, and the language breakdown used to be computed by reading every form in the dictionary — on the largest sources that took over a minute; they are now looked up directly and appear as soon as the page does.',
			'Filtering any list by source is much faster as well, and the language breakdown on a source page now counts exactly the forms the list below it shows.'
		]
	},
	{
		date: '2026-08-23',
		label: '23 August 2026',
		title: 'Dravidian reconstructions, Torwali, and source-backed comparisons',
		changes: [
			'Added 6,672 Proto-Dravidian and subgroup reconstructions from Merriam and Fuls’s Dravidian Database, with Starostin and Krishnamurti attributions preserved and links to matching DEDR entries.',
			'Added 1,943 forms from Torwali’s illustrated student dictionary, 320 manually collated Grangali, Ningalami, and Shumashti records, and 263 source-linked Nuristani forms.',
			'Added reviewed evidence from Burrow and Emeneau’s Dravidian Etymological Notes and Emeneau’s new Brahui etymologies, plus 2,376 exact CDIAL links to Mayrhofer’s scanned KEWA articles.',
			'Cross-family proposals now appear as source-attributed comparisons instead of asserted ancestry; language pages add a dialect explorer, richer family and map browsing, and clearer source evidence.',
			'The homepage now has direct dictionary search, while lists, filters, favourites, errors, and mobile navigation are more consistent and easier to use.'
		],
		ingested: {
			languages: [
				{ id: 'PDr', label: 'Proto-Dravidian' },
				{ id: 'Tor', label: 'Torwali' },
				{ id: 'Gng', label: 'Grangali' },
				{ id: 'Ning', label: 'Ningalami' },
				{ id: 'Shum', label: 'Shumashti' },
				{ id: 'PNur', label: 'Proto-Nuristani' },
				{ id: 'Brahui', label: 'Brahui' }
			],
			sources: [
				{ id: 'merriam2026dravidiandb', label: 'Merriam & Fuls 2026' },
				{ id: 'torwali2023student', label: 'Torwali 2023' },
				{ id: 'buddruss-grangali1979', label: 'Buddruss 1979 · scan' },
				{ id: 'nured', label: 'Nūristānī Etymological Dictionary' },
				{ id: 'burrow-emeneau1972den1', label: 'Burrow & Emeneau 1972 I' },
				{ id: 'burrow-emeneau1972den2', label: 'Burrow & Emeneau 1972 II' },
				{ id: 'emeneau1997brahui', label: 'Emeneau 1997' },
				{ id: 'mayrhofer-kewa', label: 'Mayrhofer 1953–1980 · scans' }
			]
		}
	},
	{
		date: '2026-08-18',
		label: '18 August 2026',
		title: 'Badaga, Nihali, and source-rich comparisons',
		changes: [
			'Added all 16,706 rows from Hockings and Pilot-Raichoor’s Badaga-English dictionary, with exact page and column citations, preserved source spellings, and reviewed DEDR links.',
			'Added Ghatage’s Marati of Kasargod vocabulary and four curated Nihali lexicons from Mundlay, Nagaraja, Bhattacharya, and Konow, preserving their source-specific forms, notes, and locators.',
			'Added Southworth’s Marathi and Old Marathi comparison with Dravidian, keeping the printed evidence, corrections, and uncertain borrowing analyses visible.',
			'Source links and filters now work consistently across entries, reflex lists, references, and language comparisons; a new local review workspace supports scan-backed correction of OCR-derived records.',
			'Author-hosted bibliography links now open reliably when their URLs contain special characters.'
		],
		ingested: {
			languages: [
				{ id: 'Badaga', label: 'Badaga' },
				{ id: 'M', label: 'Marathi' },
				{ id: 'OM', label: 'Old Marathi' },
				{ id: 'Ni', label: 'Nihali' }
			],
			sources: [
				{ id: 'hockings-pilotraichoor1992', label: 'Hockings & Pilot-Raichoor 1992 · OCR' },
				{ id: 'ghatage-kasargod1970', label: 'Ghatage 1970 · OCR' },
				{ id: 'mundlay1996', label: 'Mundlay 1996' },
				{ id: 'nagaraja2014', label: 'Nagaraja 2014' },
				{ id: 'bhattacharya1957', label: 'Bhattacharya 1957' },
				{ id: 'konow1906', label: 'Konow 1906' },
				{ id: 'nihali-database2026', label: 'Nihali Database 2026' },
				{ id: 'southworth2005m', label: 'Southworth 2005 · OCR' }
			]
		}
	},
	{
		date: '2026-08-17',
		label: '17 August 2026',
		title: 'Faster comparative etymology work',
		changes: [
			'The local etymology lab now finds semantic-and-phonological groups of unetymologised forms, ranks etyma against the whole group, supports inherited or borrowed decisions per form, and saves reviewed groups together.'
		]
	},
	{
		date: '2026-08-14',
		label: '14 August 2026',
		title: 'The Linguistic Survey of India and 31 modern surveys',
		changes: [
			'Added 119,687 forms across 536 language varieties, including the Linguistic Survey of India comparative vocabulary and 31 modern dictionaries and dialect surveys.',
			'Added detailed coverage for Brahui, Toda, Kota, Domaaki, Magar, Tamang, Rai, Tharu, Santali, and many languages of Nepal and Northeast India.',
			'Entry pages now preserve structured source text, concept views distinguish immediate etymologies more clearly, and tables and maps have improved loading and empty states.',
			'Returning visitors now receive the current dictionary release instead of continuing to use an older cached database.'
		],
		ingested: {
			languages: [
				{ id: 'Brahui', label: 'Brahui' },
				{ id: 'Toda', label: 'Toda' },
				{ id: 'Kota', label: 'Kota' },
				{ id: 'D', label: 'Domaaki' },
				{ id: 'Humla', label: 'Humla Tibetan' },
				{ id: 'KochilaTharu', label: 'Kochila Tharu' },
				{ id: 'Dotyali', label: 'Dotyali' },
				{ id: 'EasternMagar', label: 'Eastern Magar' },
				{ id: 'WesternMagar', label: 'Western Magar' },
				{ id: 'Gurung', label: 'Gurung' },
				{ id: 'Hajong', label: 'Hajong' },
				{ id: 'Loy', label: 'Loke' },
				{ id: 'Kurux', label: 'Kurux' },
				{ id: 'Kjl', label: 'Western Parbate Kham' },
				{ id: 'Majhi', label: 'Majhi' },
				{ id: 'Bote', label: 'Bote' },
				{ id: 'Chhulung', label: 'Chhulung' },
				{ id: 'EasternMewahang', label: 'Eastern Mewahang' },
				{ id: 'Sampang', label: 'Sampang' },
				{ id: 'Rabha', label: 'Rabha' },
				{ id: 'sa', label: 'Santali' },
				{ id: 'Tagin', label: 'Tagin' },
				{ id: 'Puroik', label: 'Puroik' },
				{ id: 'Ths', label: 'Thakali' },
				{ id: 'Yamphu', label: 'Yamphu' },
				{ id: 'Sk', label: 'LSI comparative vocabulary' }
			],
			sources: [
				{ id: 'grierson-lsi1928', label: 'Grierson 1928' },
				{ id: 'ali-kobayashi2024', label: 'Ali & Kobayashi 2024' },
				{ id: 'bhaskararao-toda2025', label: 'Bhaskararao & Kobayashi 2025' },
				{ id: 'wolf-kota', label: 'Wolf 2023' },
				{ id: 'weinreich2008', label: 'Weinreich 2008' },
				{ id: 'webster2022north-gorkha', label: 'Webster 2022' },
				{ id: 'swenson2024magar', label: 'Swenson 2024' },
				{ id: 'abraham-sako2021', label: 'Abraham & Sako 2021' },
				{ id: 'kim-kim-ahmad-sangma2010santali-cluster', label: 'Kim et al. 2010' },
				{ id: 'hilty-mitchell2014', label: 'Hilty & Mitchell 2014' },
				{ id: 'rai-rai-thokar2014chhulung', label: 'Rai et al. 2014' },
				{ id: 'rai-rai-thokar2015sampang', label: 'Rai et al. 2015' }
			]
		}
	},
	{
		date: '2026-08-13',
		label: '13 August 2026',
		title: 'Kullui, Old Marathi, and deeper comparisons',
		changes: [
			'Added all 2,003 entries from the live Kullui-English-Russian dictionary, preserving grammatical and etymological detail and linking exact Old Indo-Aryan matches into the etymology graph.',
			'Added 4,718 Old Marathi forms from Tulpule and Feldhaus, with stable dictionary-entry citations.',
			'Connected 706 Burushaski dialect attestations into reconstructed Proto-Burushaski cognate sets.',
			'Improved CDIAL and DEDR parsing, dialect mapping, source metadata, and concept distributions across Indo-Iranian, Dravidian, and other reflexes.'
		],
		ingested: {
			languages: [
				{ id: 'kul', label: 'Kullui' },
				{ id: 'OM', label: 'Old Marathi' },
				{ id: 'Bur', label: 'Burushaski' }
			],
			sources: [
				{ id: 'kullui-org', label: 'Krylova & Ioannissiani 2026' },
				{ id: 'tulpule1999', label: 'Tulpule & Feldhaus 1999' }
			]
		}
	},
	{
		date: '2026-08-10',
		label: '10 August 2026',
		title: 'Vaagri, Palula, and the Hindu Kush',
		changes: [
			'Expanded Vaagri Boli from a small etymological sample to the complete 2,456-item dictionary, with page and item citations for every form.',
			'Expanded Palula to the complete 3,493-form dictionary, including Biori forms and structured grammatical information.',
			'Added 11,600 forms from the Hindu Kush areal-typology survey, covering 59 language varieties from Ladakh to Afghanistan.'
		],
		ingested: {
			languages: [
				{ id: 'VB', label: 'Vaagri Boli' },
				{ id: 'Phal', label: 'Palula' },
				{ id: 'HKAT-ask', label: 'Ashkun' },
				{ id: 'HKAT-bsk_h', label: 'Burushaski' },
				{ id: 'HKAT-khw', label: 'Khowar' },
				{ id: 'HKAT-mvy', label: 'Indus Kohistani' },
				{ id: 'HKAT-aee_at', label: 'Pashai' },
				{ id: 'HKAT-scl_p', label: 'Shina' },
				{ id: 'HKAT-wbl_a', label: 'Wakhi' }
			],
			sources: [
				{ id: 'srinivasa', label: 'Srinivasa Varma 1970 · OCR' },
				{ id: 'liljegren', label: 'Liljegren 2019' },
				{ id: 'liljegren-hindukush', label: 'Liljegren et al. 2026' }
			]
		}
	},
	{
		date: '2026-08-08',
		label: '8 August 2026',
		title: 'Etymology graph rework',
		changes: [
			'Competing etymologies are now first-class: forms with more than one proposed source show an "also proposed" line with the alternative etyma, instead of a bare "derived" badge.',
			'Compound entries list their members in the right order, and variant forms now link to the exact form they vary (the etymon is reached through it).',
			'Borrowed forms are labelled "Borrowed from" consistently, including on form pages.',
			'Under the hood, all etymological relations moved to a single typed edge table with a curation queue for auto-classified hypotheses.'
		]
	},
	{
		date: '2026-08-07',
		label: '7 August 2026',
		title: 'Much smaller database',
		changes: [
			'The in-browser database was restructured and is now 49.5 MB — less than half its previous size — so the one-time download is much faster on slow connections.',
			'Page-number provenance on OCR-derived dictionary entries (e.g. Shackle 1995) now appears with the source citation instead of cluttering the notes.',
			'Stray page-navigation markup scraped from digitised dictionaries no longer appears in notes.'
		]
	},
	{
		date: '2026-08-05',
		label: '5 August 2026',
		title: 'Gāndhārī, Aśokan Prakrit, and etymology tooling',
		changes: [
			'Added the online Gāndhārī dictionary and Andersen’s edition of the Minor Rock Edicts of Aśoka.',
			'Source citations can now identify the exact page, column, dictionary article, or survey item for a form.',
			'Added a local etymology lab with concept, sound, and cognate-based candidate ranking for curating previously unetymologised forms.'
		],
		ingested: {
			languages: [
				{ id: 'Dhp', label: 'Gāndhārī' },
				{ id: 'As', label: 'Aśokan Prakrit' }
			],
			sources: [
				{ id: 'gandhari', label: 'Baums & Glass 2002–' },
				{ id: 'andersen1990', label: 'Andersen 1990 · OCR' }
			]
		}
	},
	{
		date: '2026-08-04',
		label: '4 August 2026',
		title: 'Durable form links',
		changes: [
			'Form links now remain stable when source files are reordered, transcription profiles change, or an etymology is corrected.',
			'Existing form links continue to resolve through permanent aliases.'
		]
	},
	{
		date: '2026-08-03',
		label: '3 August 2026',
		title: 'Site analytics',
		changes: ['Added Google Analytics page-view tracking across site navigation.']
	},
	{
		date: '2026-07-26',
		label: '26 July 2026',
		title: 'Burushaski, Old Sinhalese, and source confidence',
		changes: [
			'Added new Burushaski and Old Sinhalese lexical sources.',
			'Forms parsed with optical character recognition are now highlighted throughout Jambu, with an explanation that their spelling may need checking against the original source.',
			'Added grammatical class labels for Burushaski nouns and Kalasha verbs.'
		],
		ingested: {
			languages: [
				{ id: 'Bur', label: 'Burushaski' },
				{ id: 'OSi', label: 'Old Sinhalese' }
			],
			sources: [
				{ id: 'berger-auto', label: 'Berger 1998 · OCR' },
				{ id: 'yoshioka2012', label: 'Yoshioka 2012' },
				{ id: 'paranavitana', label: 'Paranavitana 1956' }
			]
		}
	},
	{
		date: '2026-07-25',
		label: '25 July 2026',
		title: 'Concept browsing and richer reflexes',
		changes: [
			'Added a Concepts index for exploring the dictionary by meaning.',
			'Reworked the concept map: hover an etymon to see where it is used, and pin several to compare their distributions.',
			'Concept maps now plot individual dialects wherever a form is tagged with one.',
			'Concept distribution bars now show unetymologised forms alongside the etyma.',
			'Added automatic tag filtering and secondary-reflex display.',
			'Improved the presentation of derived forms from CDIAL.'
		],
		ingested: {
			languages: [
				{ id: 'Kho', label: 'Khowar' },
				{ id: 'Kal', label: 'Kalasha' },
				{ id: 'K', label: 'Kashmiri' },
				{ id: 'Sh', label: 'Shina (Dras)' },
				{ id: 'WK', label: 'Wadiyara Koli' }
			],
			sources: [
				{ id: 'bashir2023', label: 'Bashir 2023' },
				{ id: 'trail-cooper1999', label: 'Trail & Cooper 1999' },
				{ id: 'schmidt', label: 'Schmidt & Kaul 2008' },
				{ id: 'rajapurohit2012', label: 'Rajapurohit 2012' },
				{ id: 'zubair', label: 'Zubair 2016' },
				{ id: 'backstrom1992', label: 'Backstrom & Radloff 1992' }
			]
		}
	},
	{
		date: '2026-07-24',
		label: '24 July 2026',
		title: 'Isoglosses and source coverage',
		changes: [
			'Reworked the isogloss models and their presentation.',
			'Improved lone-node, dialect, and reference displays.',
			'Added Markodi and several new lexicographic sources.'
		],
		ingested: {
			languages: [
				{ id: 'markodi', label: 'Markodi' },
				{ id: 'OP', label: 'Old Punjabi' },
				{ id: 'Mai', label: 'Indus Kohistani' }
			],
			sources: [
				{ id: 'canvin2025', label: 'Canvin et al. 2025' },
				{ id: 'shackle', label: 'Shackle 1995' },
				{ id: 'shackle-auto', label: 'Shackle 1995 · auto' },
				{ id: 'zoller2005', label: 'Zoller 2005' }
			]
		}
	},
	{
		date: '2026-07-21',
		label: '21 July 2026',
		title: 'Faster data, better cross-references',
		changes: [
			'Added previews for cross-references and more predictable popover behaviour.',
			'Made one-character reflex searches available.',
			'Added Tamil verb classes, era tags, and clearer origin summaries.',
			'Reduced the downloadable database from roughly 308 MB to 90 MB.'
		]
	},
	{
		date: '2026-07-20',
		label: '20 July 2026',
		title: 'Unified entries and mobile polish',
		changes: [
			'Unified etymons, reflexes, borrowed forms, and derived forms in one entry view.',
			'Added ancestry, relation, variant, and derived-term displays.',
			'Added structured tag filters and category colours.',
			'Made dense tables, alignments, navigation, and maps friendlier on small screens.',
			'Made Jambu installable as a home-screen web app.'
		]
	},
	{
		date: '2026-07-19',
		label: '19 July 2026',
		title: 'The new static Jambu',
		changes: [
			'Launched the static, browser-powered edition of Jambu.',
			'Added local database caching and reliable support for multiple open tabs.'
		]
	}
];
