/**
 * cladeTree.ts — a PROTOTYPE phylogenetic grouping of clades into higher branches, so the
 * descent view can show real tree structure rather than a flat list.
 *
 * NOTE: this hierarchy is hardcoded linguistic knowledge (Indo-Aryan mostly), not yet data. In
 * the real system it should live in ../data (e.g. a nested clade table). It's good enough to make
 * the tree meaningful for the Indo-Aryan showcase and degrades to a flat "Other" branch elsewhere.
 */
import { CLADE_ORDER } from './clades';

// clade → intermediate branch
const GROUP: Record<string, string> = {
	OIA: 'Old Indo-Aryan',
	MIA: 'Middle Indo-Aryan',
	'Early NIA': 'Early NIA',
	Nuristani: 'Nuristani',
	Pashai: 'Dardic',
	Chitrali: 'Dardic',
	Shinaic: 'Dardic',
	Kohistani: 'Dardic',
	Kunar: 'Dardic',
	Kashmiric: 'Dardic',
	Sindhic: 'Northwestern',
	Lahndic: 'Northwestern',
	Punjabic: 'Punjabi',
	'W. Pahari': 'Pahari',
	'C. Pahari': 'Pahari',
	'E. Pahari': 'Pahari',
	Eastern: 'Eastern',
	Bihari: 'Eastern',
	'E. Hindi': 'Central',
	'W. Hindi': 'Central',
	Rajasthanic: 'Central',
	Gujaratic: 'Central',
	Bhil: 'Central',
	Khandeshi: 'Central',
	'Marathi-Konkani': 'Southern',
	Halbic: 'Southern',
	Insular: 'Insular',
	'Old Dravidian': 'Dravidian',
	'S. Dravidian I': 'Dravidian',
	'S. Dravidian II': 'Dravidian',
	'C. Dravidian': 'Dravidian',
	'N. Dravidian': 'Dravidian',
	Brahui: 'Dravidian',
	Munda: 'Munda',
	Burushaski: 'Isolates',
	Nihali: 'Isolates',
	Migratory: 'Other',
	Other: 'Other'
};

export function cladeGroup(clade: string): string {
	return GROUP[clade] ?? 'Other';
}

// intermediate branch → super-branch (deep phylogeny for the tree backbone)
const SUPER: Record<string, string> = {
	'Old Indo-Aryan': 'Old Indo-Aryan',
	'Middle Indo-Aryan': 'Middle Indo-Aryan',
	'Early NIA': 'New Indo-Aryan',
	Nuristani: 'New Indo-Aryan',
	Dardic: 'New Indo-Aryan',
	Northwestern: 'New Indo-Aryan',
	Punjabi: 'New Indo-Aryan',
	Pahari: 'New Indo-Aryan',
	Eastern: 'New Indo-Aryan',
	Central: 'New Indo-Aryan',
	Southern: 'New Indo-Aryan',
	Insular: 'New Indo-Aryan',
	Dravidian: 'Dravidian',
	Munda: 'Munda',
	Isolates: 'Other',
	Other: 'Other'
};

export function superBranch(group: string): string {
	return SUPER[group] ?? 'Other';
}

/** Canonical display order of super-branches. */
export const SUPER_ORDER = [
	'Old Indo-Aryan',
	'Middle Indo-Aryan',
	'New Indo-Aryan',
	'Dravidian',
	'Munda',
	'Other'
];

/** All groups a super-branch can contain, in order — used to show gaps (branches with no reflex). */
export const SUPER_GROUPS: Record<string, string[]> = {
	'Old Indo-Aryan': ['Old Indo-Aryan'],
	'Middle Indo-Aryan': ['Middle Indo-Aryan'],
	'New Indo-Aryan': [
		'Early NIA',
		'Nuristani',
		'Dardic',
		'Northwestern',
		'Punjabi',
		'Pahari',
		'Eastern',
		'Central',
		'Southern',
		'Insular'
	],
	Dravidian: ['Dravidian'],
	Munda: ['Munda'],
	Other: ['Isolates', 'Other']
};

const cladeRank = (c: string) => {
	const i = CLADE_ORDER.indexOf(c);
	return i === -1 ? 999 : i;
};

/** Coarse etymon family a clade belongs to (Indo-Aryan / Dravidian / Munda / Other). */
export type Family = 'Indo-Aryan' | 'Dravidian' | 'Munda' | 'Other';
export function cladeFamily(clade: string): Family {
	const s = superBranch(cladeGroup(clade));
	if (s === 'Dravidian') return 'Dravidian';
	if (s === 'Munda') return 'Munda';
	if (s === 'Other') return 'Other';
	return 'Indo-Aryan'; // Old / Middle / New Indo-Aryan supers
}

/** The family of a proto-language id (as used on the Sounds page): PDr, PMu, PNur, Indo-Aryan. */
export function protoFamily(proto: string): Family {
	if (proto === 'PDr') return 'Dravidian';
	if (proto === 'PMu') return 'Munda';
	return 'Indo-Aryan'; // Indo-Aryan and PNur (Nuristani is Indo-Aryan)
}

/** Order a set of groups by the earliest clade they contain (roughly the canonical family order). */
export function orderGroups(groups: string[], cladesOf: (g: string) => string[]): string[] {
	return [...groups].sort(
		(a, b) => Math.min(...cladesOf(a).map(cladeRank)) - Math.min(...cladesOf(b).map(cladeRank))
	);
}

export { cladeRank };
