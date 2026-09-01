import type { Action } from 'svelte/action';

/**
 * Svelte action: pin `node` as `position: fixed` beside an anchor element so it escapes any
 * ancestor's `overflow` clipping (e.g. the horizontally-scrollable `.table-wrap` around the list
 * tables). It opens on the roomier side, constrains itself to the viewport, and re-places when the
 * panel grows, the page scrolls, or the viewport resizes. Pass the anchor element as the action
 * parameter; pass `null` to leave the node where it is.
 */
export const floatingPanel: Action<HTMLElement, HTMLElement | null> = (node, anchor) => {
	function place() {
		if (!anchor) return;
		const edge = 8;
		const gap = 5;
		// Clear a constraint from the previous placement before measuring again. The component's own
		// CSS max-height still applies, while a short phone viewport can impose a tighter inline one.
		node.style.maxHeight = '';
		node.style.overflowY = '';
		const r = anchor.getBoundingClientRect();
		const panelRect = node.getBoundingClientRect();
		const left = Math.max(edge, Math.min(r.left, window.innerWidth - panelRect.width - edge));
		const below = Math.max(0, window.innerHeight - r.bottom - gap - edge);
		const above = Math.max(0, r.top - gap - edge);
		const opensBelow = panelRect.height <= below || below >= above;
		const available = opensBelow ? below : above;
		const height = Math.min(panelRect.height, available);
		node.style.position = 'fixed';
		node.style.top = `${opensBelow ? r.bottom + gap : Math.max(edge, r.top - gap - height)}px`;
		node.style.left = `${left}px`;
		if (panelRect.height > available) {
			node.style.maxHeight = `${available}px`;
			node.style.overflowY = 'auto';
		}
	}
	place();
	const observer = new ResizeObserver(place);
	observer.observe(node);
	window.addEventListener('scroll', place, true);
	window.addEventListener('resize', place);
	return {
		update(next) {
			anchor = next;
			place();
		},
		destroy() {
			observer.disconnect();
			window.removeEventListener('scroll', place, true);
			window.removeEventListener('resize', place);
		}
	};
};
