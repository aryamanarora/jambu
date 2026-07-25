// Fixed categorical palette for etyma, assigned by rank (etyma sorted by form count, the
// order both the concept-page legend and the index-page bars use) and cycled beyond 8.
// The slot ordering maximises adjacent-pair colourblind separation — don't reshuffle it.
export const ETYMON_PALETTE = [
	'#2a78d6', // blue
	'#1baf7a', // aqua
	'#eda100', // yellow
	'#008300', // green
	'#4a3aa7', // violet
	'#e34948', // red
	'#e87ba4', // magenta
	'#eb6834' // orange
];

/** Slot colour for the etymon ranked `i` within a concept. */
export function etymonSlotColor(i: number): string {
	return ETYMON_PALETTE[i % ETYMON_PALETTE.length];
}
