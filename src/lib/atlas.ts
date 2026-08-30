/**
 * The shared vocabulary of an atlas map point.
 *
 * Both atlases draw the same three states over the same `Map.svelte`, and they have to keep
 * agreeing: a point you picked, a point that is merely present, and a point the current selection
 * has pushed into the background. Defining them here means a change to what "picked" looks like
 * lands on every atlas at once, instead of drifting apart one page at a time.
 */
import type { MapMarker } from '$lib/types';

/**
 * The marker a reconstructed or historical unit wears. This is `languages.map_marker` from the
 * database verbatim, so a page that has no language row to read it from (the concept atlas, the
 * isogloss atlas) draws exactly the same rhombus as one that does. Map.svelte recolours the first
 * `fill` to the point's colour.
 */
export const HISTORICAL_MARKER =
	'<svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg"><polygon points="0,15 15,0 30,15 15,30" fill="#FFDEAD" stroke="black" stroke-width="2"/></svg>';

/**
 * A marker split between several colours, sized by weight — for a place that answers the question
 * more than one way. A language rarely has a single outcome for a proto-segment, and a majority
 * colour would hide exactly the variation worth seeing; the wedges show the mix instead.
 *
 * Pass equal weights for an even split. Returns an SVG string for `MapMarker.svg`; leave
 * `MapMarker.color` unset so Map.svelte draws it as an icon rather than recolouring it.
 */
export function pieMarker(slices: { color: string; n: number }[], size = 16): string {
	const total = slices.reduce((sum, s) => sum + s.n, 0) || 1;
	const c = size / 2;
	const r = size * 0.3875;
	const ring = `<circle cx="${c}" cy="${c}" r="${(size * 0.419).toFixed(2)}" fill="none" stroke="rgba(48,35,47,.86)" stroke-width="${(size * 0.106).toFixed(2)}"/>`;
	const body =
		slices.length === 1
			? `<circle cx="${c}" cy="${c}" r="${r.toFixed(2)}" fill="${slices[0].color}"/>`
			: (() => {
					let acc = 0;
					return slices
						.map((s) => {
							const a0 = -Math.PI / 2 + (2 * Math.PI * acc) / total;
							acc += s.n;
							const a1 = -Math.PI / 2 + (2 * Math.PI * acc) / total;
							const at = (a: number) =>
								`${(c + r * Math.cos(a)).toFixed(2)} ${(c + r * Math.sin(a)).toFixed(2)}`;
							// an arc wider than a half-circle needs the large-arc flag or it draws inside out
							const large = a1 - a0 > Math.PI ? 1 : 0;
							return `<path d="M${c} ${c} L${at(a0)} A${r.toFixed(2)} ${r.toFixed(2)} 0 ${large} 1 ${at(a1)} Z" fill="${s.color}"/>`;
						})
						.join('');
				})();
	return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}">${body}${ring}</svg>`;
}

/** What a deactivated point falls back to — a slate that never reads as anybody's data colour. */
export const ATLAS_NEUTRAL = '#9a958c';

type PointStyle = Pick<MapMarker, 'color' | 'radius' | 'ring' | 'foreground' | 'dim'>;

/** Picked: filled in its own colour, ringed, and raised above its neighbours. */
export function activePoint(color: string): PointStyle {
	return { color, radius: 5.5, ring: true, foreground: true };
}

/**
 * The same treatment without the raise — for a map where *everything* is live and so nothing needs
 * lifting over anything else. `foreground` costs a DOM move and a drop-shadow filter per point, so
 * it must be reserved for the few points that are genuinely above the rest.
 */
export function livePoint(color: string): PointStyle {
	return { color, radius: 5.5, ring: true };
}

/** Present, with nothing singled out anywhere on the map: plain coverage in the neutral slate. */
export function plainPoint(): PointStyle {
	return { color: ATLAS_NEUTRAL, radius: 4 };
}

/**
 * Merely pointed at — the pointer is over its row, but nothing has been picked. It swells and
 * rises above its neighbours instead of pushing them down, so the map stays whole while you read.
 */
export function highlightPoint(color: string): PointStyle {
	return { color, radius: 8.5, ring: true, foreground: true };
}

/** Deactivated because something else is picked: small, grey and faded, but still on the map. */
export function mutedPoint(): PointStyle {
	return { color: ATLAS_NEUTRAL, radius: 2.5, dim: true };
}
