/**
 * tags.ts — client-side classification of the structured `tags` tokens (mirrors ../data/tags.py).
 * Used to colour tag pills by category and to build the tag filter.
 */
export type TagCategory = 'gender' | 'grammatical' | 'source' | 'era' | 'dialect';

export const GENDER_TAGS = ['m', 'f', 'n'];
export const GRAMMATICAL_TAGS = [
	'sg', 'pl', 'du', 'double-plural',
	'noun', 'adj', 'adv', 'pron', 'num', 'postp', 'prep', 'conj', 'interj', 'part', 'indecl', 'ord',
	'nom', 'acc', 'dat', 'gen', 'loc', 'abl', 'instr', 'voc', 'obl',
	'tr', 'intr', 'caus', 'pass', 'refl', 'denom', 'pp', 'ppp', 'pres', 'fut', 'inf', 'ger', 'ind',
	'ipfv', 'pfv', 'neg', 'participle', 'conjunctive-participle',
	'subj', 'obj', 'direct-object', 'indirect-object',
	'abs', 'erg', 'ade', 'ine', 'ess', 'prox', 'dist', 'indef', 'finalis',
	'verb', 'poss', 'conditional', 'prefix', 'suffix', 'emph', 'interr', 'dir', 'impersonal',
	'1sg', '2sg', '3sg', '1pl', '2pl', '3pl', 'pret', 'aor', 'opt', 'perfect', 'stem',
	'weak', 'middle', 'strong', 'reduplicated', 'uncertain', 'sound-variant',
	'derived', 'loanword', 'diminutive', 'intensive', 'compound', 'not-reconstructed',
	'impv', 'alternate', 'replaced',
	'poetic', 'dialectal', 'archaic', 'modern', 'colloquial', 'vulgar',
	'Tamil-class-1', 'Tamil-class-2', 'Tamil-class-3', 'Tamil-class-4', 'Tamil-class-5',
	'Tamil-class-6', 'Tamil-class-7',
	'Kalasha-class-1', 'Kalasha-class-2', 'Kalasha-class-3', 'Kalasha-class-4',
	'Burushaski-class-H', 'Burushaski-class-HM', 'Burushaski-class-HF',
	'Burushaski-class-X', 'Burushaski-class-Y', 'Burushaski-class-Z',
	'Palula-noun-class-a', 'Palula-noun-class-i', 'Palula-noun-class-m',
	'Palula-noun-class-aan', 'Palula-noun-class-ee', 'Palula-noun-class-irregular',
	'Palula-verb-class-L-a', 'Palula-verb-class-L-e', 'Palula-verb-class-L-consonant',
	'Palula-verb-class-L-minor', 'Palula-verb-class-T', 'Palula-verb-class-suppletive',
	'Kalkoti-verb-class-L', 'Kalkoti-verb-class-T', 'Kalkoti-verb-class-suppletive',
	'Sauji-noun-class-1', 'Sauji-noun-class-2', 'Sauji-noun-class-3',
	'Sauji-verb-class-1', 'Sauji-verb-class-2', 'Sauji-verb-class-3', 'Sauji-verb-class-4',
	'determiner', 'discourse-marker', 'auxiliary', 'negator', 'mood-marker', 'relative', 'honorific',
	'formal', 'informal', 'inclusive', 'exclusive', 'near-future',
	'comitative', 'superessive', 'subjunctive', 'progressive', 'contextualiser',
	'remoteness', 'complementizer', 'definite',
	'proper-noun', 'multiword-expression', 'demonstrative', 'personal', 'reciprocal',
	'copula', 'modal', 'conjunct-verb', 'incorporating', 'non-incorporating',
	'temporal', 'spatial', 'manner', 'degree', 'sentential', 'onomatopoeia', 'quantifier'
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
	if (tag.startsWith('dialect:')) return 'dialect';
	// CDIAL derived-form markers: extension morphemes (ext:kk), the shared morpheme entries
	// (morpheme:extension) — all morphological
	if (tag.startsWith('ext:') || tag.startsWith('morpheme:')) return 'grammatical';
	if (tag.startsWith('loan:')) return 'source';
	if (GENDER_SET.has(tag)) return 'gender';
	if (GRAMMATICAL_SET.has(tag)) return 'grammatical';
	if (ERA_SET.has(tag)) return 'era';
	return 'source';
}

/** Human-readable pill text. Dialect tokens carry their label after the final colon. */
export function tagLabel(tag: string): string {
	if (tag.startsWith('dialect:')) {
		const encoded = tag.slice(tag.lastIndexOf(':') + 1);
		try {
			return decodeURIComponent(encoded);
		} catch {
			return encoded;
		}
	}
	return TAG_NAMES[tag] ?? tag;
}

export const TAG_NAMES: Record<string, string> = {
	m: 'masculine', f: 'feminine', n: 'neuter',
	sg: 'singular', pl: 'plural', du: 'dual', 'double-plural': 'double plural',
	noun: 'noun', adj: 'adjective', adv: 'adverb', pron: 'pronoun', num: 'numeral', postp: 'postposition',
	prep: 'preposition', conj: 'conjunction', interj: 'interjection', part: 'particle',
	indecl: 'indeclinable', ord: 'ordinal',
	nom: 'nominative', acc: 'accusative', dat: 'dative', gen: 'genitive', loc: 'locative',
	abl: 'ablative', instr: 'instrumental', voc: 'vocative', obl: 'oblique',
	tr: 'transitive', intr: 'intransitive', caus: 'causative', pass: 'passive',
	refl: 'reflexive', denom: 'denominative', ind: 'indicative',
	pp: 'past participle', ppp: 'past passive participle', pres: 'present', fut: 'future',
	inf: 'infinitive', ger: 'gerund', impv: 'imperative', ipfv: 'imperfective', pfv: 'perfective', neg: 'negative',
	participle: 'participle', impersonal: 'impersonal',
	'conjunctive-participle': 'conjunctive participle', subj: 'subject', obj: 'object',
	'direct-object': 'direct object', 'indirect-object': 'indirect object',
	abs: 'absolutive', erg: 'ergative', ade: 'adessive', ine: 'inessive', ess: 'essive',
	prox: 'proximal', dist: 'distal', indef: 'indefinite', finalis: 'finalis',
	verb: 'verb', poss: 'possessive', conditional: 'conditional', prefix: 'prefix', suffix: 'suffix',
	emph: 'emphatic', interr: 'interrogative', dir: 'direct case',
	'1sg': 'first-person singular', '2sg': 'second-person singular', '3sg': 'third-person singular',
	'1pl': 'first-person plural', '2pl': 'second-person plural', '3pl': 'third-person plural',
	pret: 'preterite', aor: 'aorist', opt: 'optative', perfect: 'perfect', stem: 'stem form',
	weak: 'weak verb', middle: 'middle verb', strong: 'strong verb',
	reduplicated: 'reduplicated', alternate: 'alternate form', replaced: 'replaced form',
	'sound-variant': 'sound variant',
	poetic: 'poetic', dialectal: 'dialectal', archaic: 'archaic', modern: 'modern',
	colloquial: 'colloquial', vulgar: 'vulgar',
	derived: 'synchronically derived', loanword: 'loanword',
	'not-reconstructed': 'not a reconstruction',
	diminutive: 'diminutive', intensive: 'intensive', compound: 'compound',
	'Tamil-class-1': 'Tamil verb class 1', 'Tamil-class-2': 'Tamil verb class 2',
	'Tamil-class-3': 'Tamil verb class 3', 'Tamil-class-4': 'Tamil verb class 4',
	'Tamil-class-5': 'Tamil verb class 5',
	'Tamil-class-6': 'Tamil verb class 6', 'Tamil-class-7': 'Tamil verb class 7',
	'Kalasha-class-1': 'Kalasha verb class 1', 'Kalasha-class-2': 'Kalasha verb class 2',
	'Kalasha-class-3': 'Kalasha verb class 3', 'Kalasha-class-4': 'Kalasha verb class 4',
	'Burushaski-class-H': 'Burushaski noun class H',
	'Burushaski-class-HM': 'Burushaski noun class HM',
	'Burushaski-class-HF': 'Burushaski noun class HF',
	'Burushaski-class-X': 'Burushaski noun class X',
	'Burushaski-class-Y': 'Burushaski noun class Y',
	'Burushaski-class-Z': 'Burushaski noun class Z',
	'Palula-noun-class-a': 'Palula noun declension a',
	'Palula-noun-class-i': 'Palula noun declension i',
	'Palula-noun-class-m': 'Palula noun declension m',
	'Palula-noun-class-aan': 'Palula noun declension aan',
	'Palula-noun-class-ee': 'Palula noun declension ee',
	'Palula-noun-class-irregular': 'Palula irregular noun',
	'Palula-verb-class-L-a': 'Palula L-verb (a-ending)',
	'Palula-verb-class-L-e': 'Palula L-verb (e-ending)',
	'Palula-verb-class-L-consonant': 'Palula L-verb (consonant-ending)',
	'Palula-verb-class-L-minor': 'Palula minor L-verb',
	'Palula-verb-class-T': 'Palula T-verb',
	'Palula-verb-class-suppletive': 'Palula suppletive verb',
	'Kalkoti-verb-class-L': 'Kalkoti L-verb (perfective -il, -aal, -ääl)',
	'Kalkoti-verb-class-T': 'Kalkoti T-verb (perfective in a plosive)',
	'Kalkoti-verb-class-suppletive': 'Kalkoti suppletive verb',
	'Sauji-noun-class-1': 'Sauji noun class 1 (plural -a)',
	'Sauji-noun-class-2': 'Sauji noun class 2 (plural -ee)',
	'Sauji-noun-class-3': 'Sauji noun class 3 (plural -e)',
	'Sauji-verb-class-1': 'Sauji verb class 1 (perfective -il)',
	'Sauji-verb-class-2': 'Sauji verb class 2 (perfective -al)',
	'Sauji-verb-class-3': 'Sauji verb class 3 (perfective -t)',
	'Sauji-verb-class-4': 'Sauji suppletive verb',
	determiner: 'determiner', 'discourse-marker': 'discourse marker', auxiliary: 'auxiliary',
	negator: 'negator', 'mood-marker': 'mood marker', relative: 'relative', honorific: 'honorific',
	formal: 'formal', informal: 'informal', inclusive: 'inclusive', exclusive: 'exclusive',
	'near-future': 'near future',
	'proper-noun': 'proper noun', 'multiword-expression': 'multiword expression',
	demonstrative: 'demonstrative', personal: 'personal', reciprocal: 'reciprocal',
	comitative: 'comitative', superessive: 'superessive', subjunctive: 'subjunctive',
	progressive: 'progressive', contextualiser: 'contextualising marker',
	remoteness: 'remoteness marker', complementizer: 'complementiser', definite: 'definite',
	copula: 'copula', modal: 'modal verb', 'conjunct-verb': 'conjunct verb',
	incorporating: 'incorporating', 'non-incorporating': 'non-incorporating',
	temporal: 'temporal', spatial: 'spatial', manner: 'manner', degree: 'degree',
	sentential: 'sentential', onomatopoeia: 'onomatopoeia',
	lex: 'lexicographers only', RV: 'Ṛgveda', AV: 'Atharvaveda', VS: 'Vājasaneyi Saṁhitā',
	TS: 'Taittirīya Saṁhitā', 'ŚBr': 'Śatapatha Brāhmaṇa', Mn: 'Manu', MBh: 'Mahābhārata',
	R: 'Rāmāyaṇa', 'Suśr': 'Suśruta', 'Pāṇ': 'Pāṇini', Dhātup: 'Dhātupāṭha', BhP: 'Bhāgavata Purāṇa',
	'Kathās': 'Kathāsaritsāgara', 'Kāv': 'Kāvya', MW: 'Monier-Williams',
	'Early-Vedic': 'Early Vedic', 'Late-Vedic': 'Late Vedic', Epic: 'Epic period',
	Classical: 'Classical Sanskrit', Medieval: 'Medieval'
};
