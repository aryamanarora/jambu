import type { Action } from 'svelte/action';

/**
 * Svelte action: pin `node` as `position: fixed` just below an anchor element so it escapes any
 * ancestor's `overflow` clipping (e.g. the horizontally-scrollable `.table-wrap` around the list
 * tables). Re-places on scroll (capture, to catch the wrapper) and resize. Pass the anchor element
 * as the action parameter; pass `null` to leave the node where it is.
 */
export const floatingPanel: Action<HTMLElement, HTMLElement | null> = (node, anchor) => {
	function place() {
		if (!anchor) return;
		const r = anchor.getBoundingClientRect();
		node.style.position = 'fixed';
		node.style.top = `${r.bottom + 5}px`;
		node.style.left = `${r.left}px`;
	}
	place();
	window.addEventListener('scroll', place, true);
	window.addEventListener('resize', place);
	return {
		update(next) {
			anchor = next;
			place();
		},
		destroy() {
			window.removeEventListener('scroll', place, true);
			window.removeEventListener('resize', place);
		}
	};
};
