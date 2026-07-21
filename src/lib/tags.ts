/**
 * tags.ts — client-side classification of the structured `tags` tokens (mirrors ../data/tags.py).
 * Used to colour tag pills by category and to build the tag filter.
 */
export type TagCategory = 'gender' | 'grammatical' | 'source' | 'era';

export const GENDER_TAGS = ['m', 'f', 'n'];
export const GRAMMATICAL_TAGS = [
	'sg', 'pl', 'du',
	'adj', 'adv', 'pron', 'num', 'postp', 'prep', 'conj', 'interj', 'part', 'indecl', 'ord',
	'nom', 'acc', 'dat', 'gen', 'loc', 'abl', 'instr', 'voc', 'obl',
	'tr', 'intr', 'caus', 'pass', 'pp', 'ppp', 'pres', 'fut', 'inf', 'ger'
];
// The most common attestation sources, offered in the filter (the full set is larger; see
// ../data/tags.py). `lex` = "known only from lexicographers".
export const COMMON_SOURCES = [
	'RV', 'AV', 'VS', 'TS', 'ŚBr', 'Mn', 'MBh', 'R', 'Suśr', 'Pāṇ', 'Dhātup', 'BhP', 'Kathās',
	'Kāv', 'MW', 'lex'
];
// era of the earliest Sanskrit attestation (from ../data/sanskrit_works.tsv)
export const ERA_TAGS = ['Early-Vedic', 'Late-Vedic', 'Epic', 'Classical', 'Medieval'];

const GENDER_SET = new Set([...GENDER_TAGS, 'mn', 'fn', 'mf']);
const GRAMMATICAL_SET = new Set(GRAMMATICAL_TAGS);
const ERA_SET = new Set(ERA_TAGS);

/** A tag's category — anything not gender/grammatical/era is treated as an attestation source. */
export function tagCategory(tag: string): TagCategory {
	if (GENDER_SET.has(tag)) return 'gender';
	if (GRAMMATICAL_SET.has(tag)) return 'grammatical';
	if (ERA_SET.has(tag)) return 'era';
	return 'source';
}

export const TAG_NAMES: Record<string, string> = {
	m: 'masculine', f: 'feminine', n: 'neuter',
	sg: 'singular', pl: 'plural', du: 'dual',
	adj: 'adjective', adv: 'adverb', pron: 'pronoun', num: 'numeral', postp: 'postposition',
	prep: 'preposition', conj: 'conjunction', interj: 'interjection', part: 'particle',
	indecl: 'indeclinable', ord: 'ordinal',
	nom: 'nominative', acc: 'accusative', dat: 'dative', gen: 'genitive', loc: 'locative',
	abl: 'ablative', instr: 'instrumental', voc: 'vocative', obl: 'oblique',
	tr: 'transitive', intr: 'intransitive', caus: 'causative', pass: 'passive',
	pp: 'past participle', ppp: 'past passive participle', pres: 'present', fut: 'future',
	inf: 'infinitive', ger: 'gerund',
	lex: 'lexicographers only', RV: 'Ṛgveda', AV: 'Atharvaveda', VS: 'Vājasaneyi Saṁhitā',
	TS: 'Taittirīya Saṁhitā', 'ŚBr': 'Śatapatha Brāhmaṇa', Mn: 'Manu', MBh: 'Mahābhārata',
	R: 'Rāmāyaṇa', 'Suśr': 'Suśruta', 'Pāṇ': 'Pāṇini', Dhātup: 'Dhātupāṭha', BhP: 'Bhāgavata Purāṇa',
	'Kathās': 'Kathāsaritsāgara', 'Kāv': 'Kāvya', MW: 'Monier-Williams',
	'Early-Vedic': 'Early Vedic', 'Late-Vedic': 'Late Vedic', Epic: 'Epic period',
	Classical: 'Classical Sanskrit', Medieval: 'Medieval'
};
