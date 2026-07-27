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
