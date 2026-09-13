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
		date: '2026-09-13',
		label: '13 September 2026',
		title: 'Zoller comparative vocabulary and an expanded dictionary',
		changes: [
			'Added 17,754 attestations from the linguistic data sections of Zoller’s 2023 study, spanning 313 languages with exact source locators.',
			'Preserved source transcription, 341 direct CDIAL links, and 70 explicit variant links; unresolved comparisons remain unlinked.',
			'Refreshed the dictionary with the latest ingested sources: 720,668 browser records in a 48.80 MB download.',
			'Fixed decoding of large compressed databases and added lossless verification before staging.'
		],
		ingested: {
			languages: [
				{ id: 'WPah', label: 'West Pahari' },
				{ id: 'Pr', label: 'Prasun' },
				{ id: 'kw', label: 'Korwa' },
				{ id: 'Tampuan', label: 'Tampuan' }
			],
			sources: [{ id: 'zoller2023', label: 'Zoller 2023' }]
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
