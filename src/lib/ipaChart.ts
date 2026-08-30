/**
 * The IPA chart's own geometry, kept separate from Jambu's transcription of it.
 *
 * These are the standard pulmonic-consonant and vowel layouts: the rows, columns and cells of
 * the printed chart, with `null` where the IPA judges an articulation impossible and an empty
 * string where the chart leaves a cell blank. The house glyphs are not here — the page joins
 * these positions against `transcriptionChart.json`, which is generated from the sound profiles
 * in the data repository, so the overlay always reflects what the profiles actually do.
 */

export type Cell = { ipa: string; voiced: boolean } | null;

export const CONSONANT_PLACES = [
	'Bilabial',
	'Labiodental',
	'Dental',
	'Alveolar',
	'Postalveolar',
	'Retroflex',
	'Palatal',
	'Velar',
	'Uvular',
	'Pharyngeal',
	'Glottal'
] as const;

/** Each cell is a voiceless/voiced pair; `null` marks an articulation judged impossible. */
export const CONSONANT_ROWS: { manner: string; cells: [string, string][] | (null | [string, string])[] }[] = [
	{
		manner: 'Plosive',
		cells: [['p', 'b'], ['', ''], ['t̪', 'd̪'], ['t', 'd'], ['', ''], ['ʈ', 'ɖ'], ['c', 'ɟ'], ['k', 'ɡ'], ['q', 'ɢ'], null, ['ʔ', '']]
	},
	{
		manner: 'Nasal',
		cells: [['', 'm'], ['', 'ɱ'], ['', 'n̪'], ['', 'n'], ['', ''], ['', 'ɳ'], ['', 'ɲ'], ['', 'ŋ'], ['', 'ɴ'], null, null]
	},
	{
		manner: 'Trill',
		cells: [['', 'ʙ'], ['', ''], ['', ''], ['', 'r'], ['', ''], ['', ''], ['', ''], ['', ''], ['', 'ʀ'], null, null]
	},
	{
		manner: 'Tap or flap',
		cells: [['', 'ⱱ'], ['', ''], ['', ''], ['', 'ɾ'], ['', ''], ['', 'ɽ'], ['', ''], ['', ''], ['', ''], null, null]
	},
	{
		manner: 'Fricative',
		cells: [['ɸ', 'β'], ['f', 'v'], ['θ', 'ð'], ['s', 'z'], ['ʃ', 'ʒ'], ['ʂ', 'ʐ'], ['ç', 'ʝ'], ['x', 'ɣ'], ['χ', 'ʁ'], ['ħ', 'ʕ'], ['h', 'ɦ']]
	},
	{
		manner: 'Lateral fricative',
		cells: [['', ''], ['', ''], ['', ''], ['ɬ', 'ɮ'], ['', ''], ['', ''], ['', ''], ['', ''], ['', ''], null, null]
	},
	{
		manner: 'Approximant',
		cells: [['', ''], ['', 'ʋ'], ['', ''], ['', 'ɹ'], ['', ''], ['', 'ɻ'], ['', 'j'], ['', 'ɰ'], ['', ''], null, null]
	},
	{
		manner: 'Lateral approximant',
		cells: [['', ''], ['', ''], ['', ''], ['', 'l'], ['', ''], ['', 'ɭ'], ['', 'ʎ'], ['', 'ʟ'], ['', ''], null, null]
	}
];

/**
 * Affricates and the aspirates are not cells of the pulmonic chart, but South Asian sources
 * write them constantly and the profiles map them as units, so they get their own table.
 */
export const CLUSTER_GROUPS: { label: string; note: string; symbols: string[] }[] = [
	{
		label: 'Affricates',
		note: 'Mapped as single units, not as stop plus fricative.',
		symbols: ['tʃ', 'dʒ', 'ts', 'dz', 'tʂ', 'dʐ', 'tɕ', 'dʑ', 'ʦ', 'ʣ']
	},
	{
		label: 'Aspirates',
		note: 'The house transcription keeps aspiration as a superscript hook on the stop.',
		symbols: ['pʰ', 'bʰ', 'tʰ', 'dʰ', 'ʈʰ', 'ɖʰ', 'kʰ', 'ɡʰ', 'tʃʰ', 'dʒʰ', 'ɽʰ']
	},
	{
		label: 'Diacritics and suprasegmentals',
		note: 'Applied to the segment they follow.',
		symbols: ['ʰ', 'ʱ', '̃', 'ː', '̩', '̪', '̟', 'ʲ', 'ʷ', 'ˑ']
	}
];

export const VOWEL_HEIGHTS = ['Close', 'Near-close', 'Close-mid', 'Mid', 'Open-mid', 'Near-open', 'Open'] as const;
export const VOWEL_BACKNESS = ['Front', 'Central', 'Back'] as const;

/** Each cell is an unrounded/rounded pair at that height and backness. */
export const VOWEL_ROWS: { height: string; cells: [string, string][] }[] = [
	{ height: 'Close', cells: [['i', 'y'], ['ɨ', 'ʉ'], ['ɯ', 'u']] },
	{ height: 'Near-close', cells: [['ɪ', 'ʏ'], ['', ''], ['', 'ʊ']] },
	{ height: 'Close-mid', cells: [['e', 'ø'], ['ɘ', 'ɵ'], ['ɤ', 'o']] },
	{ height: 'Mid', cells: [['', ''], ['ə', ''], ['', '']] },
	{ height: 'Open-mid', cells: [['ɛ', 'œ'], ['ɜ', 'ɞ'], ['ʌ', 'ɔ']] },
	{ height: 'Near-open', cells: [['æ', ''], ['ɐ', ''], ['', '']] },
	{ height: 'Open', cells: [['a', 'ɶ'], ['', ''], ['ɑ', 'ɒ']] }
];

/** Nasal and long vowels are written as their own graphemes in most South Asian sources. */
export const VOWEL_EXTRAS: { label: string; note: string; symbols: string[] }[] = [
	{
		label: 'Nasal vowels',
		note: 'Sources write these precomposed; the profiles map them as units.',
		symbols: ['ã', 'ẽ', 'ĩ', 'õ', 'ũ', 'ə̃', 'ɔ̃', 'ɛ̃']
	},
	{
		label: 'Long vowels',
		note: 'A source that marks length with ː is normalised to the macron.',
		symbols: ['aː', 'eː', 'iː', 'oː', 'uː', 'ɛː', 'ɔː']
	}
];
