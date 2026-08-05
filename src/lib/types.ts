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
	entry_count: number;
	order: number;
	map_marker: string;
}

// Same shape as Language (name, language, dialect, glottocode, long, lat, clade, color,
// lemma_count, order, map_marker) plus the dialect linking fields (token, language_id, entry_count).
export interface Dialect {
	token: string;
	language_id: string;
	id: string;
	name: string;
	language: string | null;
	dialect: string | null;
	glottocode: string;
	long: number | null;
	lat: number | null;
	clade: string | null;
	color: string | null;
	location: string | null;
	quality: string | null;
	lemma_count: number;
	order: number | null;
	map_marker: string | null;
	entry_count: number;
}

export interface Reference {
	id: string;
	short: string | null;
	source: string | null;
	progress: string | null;
	provenance: string | null;
	editor: string | null;
	ocr: boolean | number;
	lemma_count: number;
	unetymologised_count: number;
	locator?: string; // page, entry, or other source-local locator for this lemma's citation
}

export interface Lemma {
	id: string;
	word: string;
	gloss: string;
	native: string;
	phonemic: string;
	notes: string;
	tags: string; // structured source, grammar, era, and dialect tokens; space-separated
	clades: string;
	cognateset: string;
	order: number;
	language_id: string;
	origin_lemma_id: string | null;
	etymology?: string; // free-text etymological header (the CDIAL entry HTML); entries only
	relation?: string | null; // '' for etyma, 'reflex' | 'variant' | 'borrowed' for children
	variant_of?: string | null; // a reflex-variant points at its main reflex (null ⇒ head variant)
	variants?: Lemma[]; // hydrated: same-form alternates of a main reflex (entry page)
	redirect_to?: string | null; // a CDIAL "Add. N" stub redirects to entry N (not listed)
	borrowed_from?: string | null; // a borrowed sub-reflex points at the reflex it was borrowed from
	sub_count?: number; // hydrated: # of borrowed sub-reflexes hanging off this reflex
	reflex_sub_count?: number; // hydrated: # of daughter reflexes hanging off this reflex (it is itself an etymon)
	// per-entry aggregates (materialised columns; populated on headwords)
	reflex_count?: number;
	lang_count?: number;
	derived_count?: number; // # of derived-term etyma built on this headword (entries view)
	concept_match?: number; // # of this entry's reflexes matching the active concept (concepts view)
	secondary?: number; // 1 when shown under an etymon it reaches by an alternate (derivation) edge
	variant_forms?: string | null; // same-language variant word forms, \x1f-separated (entries view)
	ocr_variant_forms?: string | null; // OCR-derived subset of variant_forms, same separator
	// hydrated relations (optional)
	language?: Language;
	origin_lemma?: Lemma | null;
	references?: Reference[];
	ocr?: boolean | number; // reference-backed query flag for projections without hydrated references
}

/** Query params shared by the list views, mirroring the old URL keys (search.py). */
export interface ListParams {
	lang?: string;
	word?: string;
	gloss?: string;
	etymology?: string;
	notes?: string;
	source?: string;
	origin_lang?: string;
	origin?: string;
	etymon_lang?: string; // filter reflexes by the language of their origin (etymon/source)
	dialect?: string; // exact dialect tag, used by the per-language lexicon picker
	clade?: string;
	tags?: string; // space-separated tags; a row must carry ALL of them
	rootsOnly?: boolean; // entries with no ancestor (not derived from any other etymon)
	sectionsOnly?: boolean; // CDIAL promoted section-forms (ids like 3643-2)
	loanSourcesOnly?: boolean; // reflexes that are the source of borrowings into other languages
	sort?: string; // "asc-<col>" | "desc-<col>"
	page?: number;
}

export const PAGE_SIZE = 50;

/** Minimum characters before a substring lemma filter activates (1 = any non-empty input). */
export const MIN_SEARCH_CHARS = 1;

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
	ring?: boolean; // draw a bold outline (e.g. the selected point on the isogloss map)
}

// ---- concepts (Concepticon) -----------------------------------------------

export interface ConceptBarSeg {
	etymon: string;
	n: number; // number of forms of this etymon expressing the concept (segment size)
}

export interface ConceptRow {
	id: number;
	name: string;
	category: string;
	etyma_count: number;
	unetym_count: number;
	lang_count: number;
	form_count: number;
	bars?: ConceptBarSeg[]; // top etyma for the stacked bar (index page)
	rest?: number; // forms from etyma beyond the shown segments
}

/** A point a form is plotted at: a located dialect it is tagged with, else its language. */
export interface AttestationPlace {
	key: string; // dialect token, or `language:<name>`
	name: string; // "Marathi: Konkani", or just "Marathi" for the language fallback
	lat: number;
	long: number;
}

export interface ConceptAttestation {
	form_id: string;
	word: string;
	gloss: string;
	language_id: string | null;
	language: string | null;
	clade: string | null;
	color: string | null;
	lat: number | null;
	long: number | null;
	places: AttestationPlace[];
	ocr?: boolean | number;
}

export interface ConceptEtymon {
	etymon: string;
	word: string; // headword of the root etymon (falls back to the id)
	gloss: string;
	source: string;
	languages: string[];
	forms: ConceptAttestation[];
	ocr?: boolean | number;
}

export interface ConceptDetail {
	concept: ConceptRow;
	etyma: ConceptEtymon[];
	unetym: ConceptAttestation[];
}
