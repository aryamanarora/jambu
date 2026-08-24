// Fixed categorical palette for etyma, assigned by rank (etyma sorted by form count, the
// order both the concept-page legend and the index-page bars use) and cycled beyond 8.
// The first four are intentionally far apart in hue because they are the default comparison
// set on concept maps. Later slots continue the colourblind-friendly categorical sequence.
export const ETYMON_PALETTE = [
	'#0072b2', // blue
	'#d55e00', // vermillion
	'#009e73', // bluish green
	'#cc79a7', // reddish purple
	'#e69f00', // orange
	'#6f4c9b', // violet
	'#1696a7', // teal
	'#cf3f4d' // red
];

/** Slot colour for the etymon ranked `i` within a concept. */
export function etymonSlotColor(i: number): string {
	return ETYMON_PALETTE[i % ETYMON_PALETTE.length];
}
