/**
 * soundChange.ts — presentation for the materialised change codes from align.py.
 * The linguistic categorisation lives in the data (the `change` code); here we only map a code
 * to a display name and a colour class. The full surface label is composed at render from
 * (etymonSeg → reflexSeg : name).
 */

export type ChangeClass = 'kept' | 'change' | 'loss' | 'add';

interface ChangeInfo {
	cls: ChangeClass;
	name: string;
}

const CHANGES: Record<string, ChangeInfo> = {
	kept: { cls: 'kept', name: 'retained' },
	loss: { cls: 'loss', name: 'lost' },
	add: { cls: 'add', name: 'epenthesis' },
	// consonant manner
	deaffrication: { cls: 'change', name: 'deaffrication' },
	affrication: { cls: 'change', name: 'affrication' },
	spirantization: { cls: 'change', name: 'spirantization' },
	lenition: { cls: 'change', name: 'lenition' },
	fortition: { cls: 'change', name: 'fortition' },
	// consonant other
	nasalization: { cls: 'change', name: 'nasalization' },
	denasalization: { cls: 'change', name: 'denasalization' },
	devoicing: { cls: 'change', name: 'devoicing' },
	voicing: { cls: 'change', name: 'voicing' },
	aspiration: { cls: 'change', name: 'aspiration' },
	deaspiration: { cls: 'change', name: 'deaspiration' },
	retroflexion: { cls: 'change', name: 'retroflexion' },
	fronting: { cls: 'change', name: 'fronting' },
	place: { cls: 'change', name: 'place shift' },
	cons: { cls: 'change', name: 'change' },
	// vowels
	lengthening: { cls: 'change', name: 'lengthening' },
	shortening: { cls: 'change', name: 'shortening' },
	vowel: { cls: 'change', name: 'vowel shift' }
};

export function changeInfo(code: string): ChangeInfo {
	return CHANGES[code] ?? { cls: 'change', name: code };
}

/** Human label for one aligned step, e.g. "j → ʣ · fronting" or "b lost". */
export function changeLabel(etymonSeg: string, reflexSeg: string, code: string): string {
	const { cls, name } = changeInfo(code);
	if (cls === 'kept') return `${etymonSeg} retained`;
	if (cls === 'loss') return `${etymonSeg} lost`;
	if (cls === 'add') return `${reflexSeg} inserted`;
	return `${etymonSeg} → ${reflexSeg} · ${name}`;
}
