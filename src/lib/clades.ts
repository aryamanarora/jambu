/**
 * Clade colour scheme + ordering, ported verbatim from the ETL
 * (`neojambu/scripts/make_database.py:13-52`). This is the single source of truth for the
 * functional clade colours used by the clade bars and (implicitly) the language marker fills.
 *
 * Colours are hex WITHOUT a leading '#', matching the DB's `languages.color` convention;
 * use `cladeColor()` / `hashColor()` to get a CSS-ready value.
 */
export const CLADE_COLORS: Record<string, string> = {
	OIA: 'E2DFD2',
	MIA: 'FFDEAD',
	'Early NIA': 'B08D57',
	Migratory: '63666A',
	Nuristani: '9132a8',
	Pashai: 'FFD6F6',
	Chitrali: 'FFACEF',
	Shinaic: 'FF81E6',
	Kohistani: 'FF25D5',
	Kunar: 'ff68e0',
	Kashmiric: 'FF00CD',
	Sindhic: '0066FF',
	Lahndic: 'a4d6f5',
	Punjabic: '7164FF',
	'W. Pahari': 'B94E16',
	'C. Pahari': '9E521B',
	'E. Pahari': '79421B',
	Eastern: 'FFDE54',
	Bihari: 'FFCD00',
	'E. Hindi': 'FF9A54',
	'W. Hindi': 'FF6600',
	Rajasthanic: '6BCD00',
	Gujaratic: '00CF4A',
	'Marathi-Konkani': 'D50000',
	Bhil: '09AD02',
	Khandeshi: '2FFF2F',
	Halbic: 'AB8900',
	Insular: 'AC0000',
	'Old Dravidian': '679267',
	'S. Dravidian I': '74C365',
	'S. Dravidian II': '98FB98',
	'C. Dravidian': '29AB87',
	'N. Dravidian': '4B6F44',
	Brahui: '49796B',
	Munda: '00ffd0',
	Burushaski: 'f3ff05',
	Nihali: 'ff9a00',
	Other: 'FAF9F6'
};

/** Ordered list of clades — the canonical display/sort order (== Python `list(colors.keys())`). */
export const CLADE_ORDER: string[] = Object.keys(CLADE_COLORS);

/** CSS colour for a clade, or a neutral grey if unknown. */
export function cladeColor(clade: string | null | undefined): string {
	if (clade && clade in CLADE_COLORS) return `#${CLADE_COLORS[clade]}`;
	return 'var(--clade-empty)';
}

/** Prefix a bare DB hex (e.g. `languages.color`) with '#'; falls back to a neutral. */
export function hashColor(hex: string | null | undefined): string {
	if (!hex) return 'var(--clade-empty)';
	return hex.startsWith('#') ? hex : `#${hex}`;
}
