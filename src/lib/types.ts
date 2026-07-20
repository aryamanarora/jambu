/** Row shapes mirroring the SQLite schema (see neojambu/src/neojambu/models.py). */

export interface Language {
	id: string;
	name: string;
	language: string;
	dialect: string;
	glottocode: string;
	long: number;
	lat: number;
	clade: string;
	color: string;
	lemma_count: number;
	order: number;
	map_marker: string;
}

export interface Reference {
	id: string;
	short: string;
	source: string;
	progress: string;
}

export interface Lemma {
	id: string;
	word: string;
	gloss: string;
	native: string;
	phonemic: string;
	original: string;
	notes: string;
	tags: string; // structured tokens lifted from notes (gender + grammatical), space-separated
	clades: string;
	cognateset: string;
	order: number;
	language_id: string;
	origin_lemma_id: string | null;
	// per-entry aggregates (materialised columns; populated on headwords)
	reflex_count?: number;
	lang_count?: number;
	// hydrated relations (optional)
	language?: Language;
	origin_lemma?: Lemma | null;
	references?: Reference[];
}

/** Query params shared by the list views, mirroring the old URL keys (search.py). */
export interface ListParams {
	lang?: string;
	word?: string;
	gloss?: string;
	notes?: string;
	source?: string;
	origin_lang?: string;
	origin?: string;
	clade?: string;
	tags?: string; // space-separated tags; a row must carry ALL of them
	sort?: string; // "asc-<col>" | "desc-<col>"
	page?: number;
}

export const PAGE_SIZE = 50;

/** Minimum characters before a full-text (trigram) lemma filter activates. */
export const MIN_FTS_CHARS = 3;

/** A cognate-set group on the entry page: [groupKey, [ [language, reflexes[]], ... ] ]. */
export type CognateGroup = [string | null, Array<[Language, Lemma[]]>];

/** A Leaflet marker built from a language row. */
export interface MapMarker {
	lat: number;
	long: number;
	svg: string; // inline SVG string (languages.map_marker)
	tooltip?: string;
	popupHtml?: string;
	onClick?: () => void;
	color?: string; // when set, drawn as a filled circle in this colour instead of the SVG icon
	radius?: number;
	dim?: boolean; // draw faded (e.g. languages with no reflex at the selected position)
}
