<script lang="ts">
	import 'leaflet/dist/leaflet.css';
	import { onMount, onDestroy } from 'svelte';
	import type { MapMarker } from '$lib/types';

	let {
		markers = [],
		center,
		zoom = 4,
		height = '500px',
		showAllTooltips = false,
		bounds,
		fitOnce = false,
		mutedTiles = false,
		flush = false,
		zoomPosition = 'topleft',
		scrollZoom = false,
		animateZoom = true
	}: {
		markers: MapMarker[];
		center?: [number, number];
		zoom?: number;
		height?: string;
		showAllTooltips?: boolean;
		bounds?: [[number, number], [number, number]]; // fixed initial framing (overrides auto-fit)
		fitOnce?: boolean; // auto-fit only the first draw, never re-adjust the view on later updates
		mutedTiles?: boolean; // soften the basemap so dense data overlays remain dominant
		flush?: boolean; // drop the frame's border/radius/shadow (for edge-to-edge use)
		// where the +/- sit; move them when something floats over their default corner
		zoomPosition?: 'topleft' | 'topright' | 'bottomleft' | 'bottomright';
		// Off by default: inside a scrolling document the wheel belongs to the page. The full-bleed
		// atlases have no page scroll to steal, so they turn it on.
		scrollZoom?: boolean;
		animateZoom?: boolean;
	} = $props();

	let el: HTMLDivElement;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let map: any = null;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let L: any = null;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let layer: any = null;
	let lastFitSig = ''; // coord signature of the last auto-fit (skip refit on colour-only redraws)
	let ro: ResizeObserver | null = null;
	let userMoved = false; // the reader has panned or zoomed, so the view is theirs now
	let fitting = false; // guard so our own fitBounds isn't mistaken for a reader gesture
	let destroyed = false;
	// the layers currently on the map, in marker order, so a style-only change can reuse them
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let drawn: { key: string; marker: any; onClick?: () => void }[] = [];

	function iconUrl(svg: string): string {
		return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
	}

	/** Identity of a marker for reuse: where it is and which of the three kinds it is drawn as. */
	function shapeKey(m: MapMarker): string {
		const kind = m.color ? (m.svg?.includes('polygon') ? 'rhombus' : 'circle') : 'icon';
		return `${m.lat},${m.long},${kind}`;
	}

	/**
	 * Restyle the markers already on the map instead of rebuilding them.
	 *
	 * Selecting, hovering and searching change how points look, never where they are — and tearing
	 * down several hundred Leaflet layers to say "this one is bigger now" is what makes a large map
	 * feel sluggish. Returns false when the point set really did change, in which case the caller
	 * falls back to a full draw.
	 */
	function restyle(): boolean {
		if (!layer || drawn.length !== markers.length) return false;
		for (let i = 0; i < markers.length; i++) {
			if (drawn[i].key !== shapeKey(markers[i])) return false;
		}
		for (let i = 0; i < markers.length; i++) {
			const m = markers[i];
			const marker = drawn[i].marker;
			if (marker.setStyle) {
				marker.setStyle({
					radius: m.radius ?? 7,
					fillColor: m.color,
					color: m.ring ? 'rgba(48,35,47,0.86)' : 'rgba(0,0,0,0.55)',
					weight: m.ring ? 1.75 : 1,
					fillOpacity: m.dim ? 0.25 : 0.92,
					opacity: m.dim ? 0.35 : 1,
					className: m.foreground ? 'map-point-foreground' : ''
				});
			} else {
				marker.setIcon(iconFor(m));
				marker.setOpacity?.(m.dim ? 0.4 : 1);
				marker.setZIndexOffset?.(m.foreground ? 1000 : 0);
			}
			if (m.foreground) marker.bringToFront?.();
			if (m.tooltip) marker.setTooltipContent?.(m.tooltip);
			if (m.label) marker.getElement?.()?.setAttribute('aria-label', m.label);
			if (m.popupHtml) {
				if (marker.getPopup?.()) marker.setPopupContent(m.popupHtml);
				else marker.bindPopup(m.popupHtml);
			} else marker.unbindPopup?.();
			if (m.tooltipOpen) marker.openTooltip?.();
			else marker.closeTooltip?.();
			// handlers close over the caller's state, so they have to be re-bound, not kept
			if (drawn[i].onClick) marker.off?.('click', drawn[i].onClick);
			if (m.onClick) marker.on('click', m.onClick);
			drawn[i].onClick = m.onClick;
		}
		return true;
	}

	function iconFor(m: MapMarker) {
		const iconSize = m.size ?? (m.foreground ? 14 : 16);
		const svg =
			m.color && m.svg?.includes('polygon')
				? m.svg.replace(/fill="[^"]*"/, `fill="${m.color}"`)
				: m.svg;
		return L.icon({
			iconUrl: iconUrl(svg),
			iconSize: [iconSize, iconSize],
			iconAnchor: [iconSize / 2, iconSize / 2],
			className: m.foreground ? 'map-point-foreground' : ''
		});
	}

	/**
	 * Re-frame the view when what it should be framing has changed.
	 *
	 * With fitOnce the first draw fits and later ones leave the reader's pan/zoom alone — but the
	 * first draw can land before every marker has arrived, and fitting to one point zooms all the
	 * way in with nothing to undo it. So keep re-fitting while the framed set is still changing,
	 * and stop the moment the reader takes the view over themselves.
	 *
	 * Markers flagged `focus` own the frame outright: picking one language out of a continent
	 * should close in on it rather than keep the continent in view. Clearing that pick is a change
	 * of frame too, even though not one coordinate moved — which is why this cannot live inside the
	 * full-rebuild path.
	 */
	function fitIfNeeded() {
		const pts: [number, number][] = [];
		const focus: [number, number][] = [];
		for (const m of markers) {
			if (m.lat == null || m.long == null) continue;
			pts.push([m.lat, m.long]);
			if (m.focus) focus.push([m.lat, m.long]);
		}
		const fitPts = focus.length ? focus : pts;
		const sig = fitPts.map((p) => p.join()).join('|');
		const shouldFit = sig !== lastFitSig && (fitOnce ? !userMoved : true);
		if (!center && !bounds && fitPts.length && shouldFit) {
			fitting = true;
			map.fitBounds(fitPts, { padding: [30, 30], maxZoom: 7, animate: false });
			fitting = false;
			lastFitSig = sig;
		}
	}

	function draw() {
		if (!map || !L) return;
		// a style-only change needs no new layers — but it can still change the frame
		if (restyle()) {
			fitIfNeeded();
			updateOffscreen();
			return;
		}
		if (layer) layer.remove();
		layer = L.layerGroup().addTo(map);
		drawn = [];
		const foreground: any[] = [];
		for (const m of markers) {
			if (m.lat == null || m.long == null) continue;
			let marker: any;
			const iconSize = m.size ?? (m.foreground ? 14 : 16);
			if (m.color && m.svg?.includes('polygon')) {
				// historical-language marker: keep the rhombus shape (as on the languages page)
				// but recolour its fill to the overlay/clade colour instead of drawing a circle.
				const svg = m.svg.replace(/fill="[^"]*"/, `fill="${m.color}"`);
				const icon = L.icon({
					iconUrl: iconUrl(svg),
					iconSize: [iconSize, iconSize],
					iconAnchor: [iconSize / 2, iconSize / 2],
					className: m.foreground ? 'map-point-foreground' : ''
				});
				marker = L.marker([m.lat, m.long], { icon, opacity: m.dim ? 0.4 : 1 }).addTo(layer);
			} else if (m.color) {
				// filled circle — recolourable (used for correspondence + isogloss overlays)
				marker = L.circleMarker([m.lat, m.long], {
					radius: m.radius ?? 7,
					fillColor: m.color,
					color: m.ring ? 'rgba(48,35,47,0.86)' : 'rgba(0,0,0,0.55)',
					weight: m.ring ? 1.75 : 1,
					fillOpacity: m.dim ? 0.25 : 0.92,
					opacity: m.dim ? 0.35 : 1,
					className: m.foreground ? 'map-point-foreground' : ''
				}).addTo(layer);
				if (m.ring) marker.bringToFront();
			} else {
				const icon = L.icon({
					iconUrl: iconUrl(m.svg),
					iconSize: [iconSize, iconSize],
					iconAnchor: [iconSize / 2, iconSize / 2],
					className: m.foreground ? 'map-point-foreground' : ''
				});
				marker = L.marker([m.lat, m.long], { icon }).addTo(layer);
			}
			if (m.tooltip) marker.bindTooltip(m.tooltip);
			if (m.label) marker.getElement?.()?.setAttribute('aria-label', m.label);
			// a point the page is pointing at names itself, rather than waiting to be hovered
			if (m.tooltipOpen) marker.openTooltip?.();
			if (m.popupHtml) marker.bindPopup(m.popupHtml);
			if (m.onClick) marker.on('click', m.onClick);
			if (m.foreground) foreground.push(marker);
			drawn.push({ key: shapeKey(m), marker, onClick: m.onClick });
		}
		// Raise emphasis markers only after every point exists. Calling bringToFront while drawing is
		// not sufficient: a later context point can otherwise be appended above the highlight.
		for (const marker of foreground) {
			marker.bringToFront?.();
			marker.setZIndexOffset?.(1000);
		}
		fitIfNeeded();
		if (showAllTooltips) layer.eachLayer((lyr: any) => lyr.openTooltip?.());
		updateOffscreen();
	}

	// markers currently outside the map viewport (recomputed on pan/zoom)
	let offscreen = $state<MapMarker[]>([]);
	function updateOffscreen() {
		if (!map) return;
		const b = map.getBounds();
		offscreen = markers.filter(
			(m) => m.lat != null && m.long != null && !b.contains([m.lat, m.long])
		);
	}

	onMount(async () => {
		L = (await import('leaflet')).default;
		if (destroyed) return;
		map = L.map(el, { scrollWheelZoom: scrollZoom, zoomAnimation: animateZoom }).setView(center ?? [20.5937, 78.9629], zoom);
		if (zoomPosition !== 'topleft') map.zoomControl.setPosition(zoomPosition);
		L.tileLayer(
			'https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
			{
				attribution: 'Tiles © Esri — US National Park Service',
				maxZoom: 8,
				className: mutedTiles ? 'map-tiles-muted' : ''
			}
		).addTo(map);
		if (bounds) map.fitBounds(bounds);
		map.on('moveend zoomend', updateOffscreen);
		map.on('movestart zoomstart', () => {
			if (!fitting) userMoved = true;
		});
		draw();

		// Leaflet caches the container size at init, so a box that grows afterwards leaves the map
		// rendering into the old one — re-measure whenever the frame resizes.
		//
		// And re-fit: a frame that had no size yet (a full-bleed panel still settling) produces a
		// nonsense fit, which is then recorded as the current one, so no later redraw would ever
		// correct it. Keep re-fitting on resize until the reader takes the view over themselves.
		ro = new ResizeObserver(() => {
			if (!map) return;
			// `pan: false`: invalidateSize otherwise recentres, and that pan arrives as a `movestart`
			// the moment after this callback returns — indistinguishable from the reader grabbing
			// the map, which would freeze the view where a zero-size frame happened to leave it.
			map.invalidateSize({ pan: false, animate: false });
			if (!userMoved) {
				lastFitSig = '';
				fitIfNeeded();
			}
		});
		ro.observe(el);
	});

	// redraw when markers change
	$effect(() => {
		markers;
		showAllTooltips;
		if (map) draw();
	});

	onDestroy(() => {
		destroyed = true;
		ro?.disconnect();
		if (map) { map.stop(); map.remove(); map = null; }
	});
</script>

<div class="map-frame" class:flush style="height: {height}">
	<div class="map" bind:this={el}></div>
	{#if offscreen.length}
		<div class="offscreen" title="reflexes outside the current view — pan/zoom to reach them">
			{#each offscreen.slice(0, 16) as m, i (i)}
				<span class="odot" style="background: {m.color ?? '#888'}" title={m.tooltip}></span>
			{/each}
			<span class="oc-count">+{offscreen.length} off-map</span>
		</div>
	{/if}
</div>

<style>
	.map-frame {
		position: relative;
		overflow: hidden;
		border: 1px solid var(--border-strong);
		border-radius: 0.8rem;
		background: var(--surface-2);
		box-shadow: 0 0.45rem 1.4rem rgba(45, 30, 24, 0.08);
	}
	.map-frame.flush {
		border: 0;
		border-radius: 0;
		box-shadow: none;
	}
	.map-frame :global(.map) {
		height: 100%;
	}
	.map-frame :global(.map-tiles-muted) {
		filter: saturate(0.3) contrast(0.72) brightness(1.14);
		opacity: 0.72 !important;
	}
	:global(:root[data-theme='dark']) .map-frame :global(.map-tiles-muted) {
		filter: saturate(0.28) contrast(0.78) brightness(0.72);
		opacity: 0.68 !important;
	}
	.map-frame :global(.leaflet-control-zoom) {
		overflow: hidden;
		border: 0;
		border-radius: 0.55rem;
		box-shadow: 0 2px 10px rgba(35, 26, 22, 0.2);
	}
	.map-frame :global(.leaflet-control-zoom a) {
		border-color: var(--border);
		background: color-mix(in srgb, var(--surface) 94%, transparent);
		color: var(--ink);
	}
	.map-frame :global(.leaflet-control-zoom a:hover) {
		background: var(--surface-2);
		color: var(--plum-2);
	}
	.map-frame :global(.leaflet-tooltip),
	.map-frame :global(.leaflet-popup-content) {
		font-family: var(--font-phon);
	}
	.map-frame :global(.leaflet-tooltip) {
		border: 1px solid var(--border-strong);
		border-radius: 0.45rem;
		background: color-mix(in srgb, var(--surface) 96%, transparent);
		color: var(--ink);
		box-shadow: 0 3px 12px rgba(35, 26, 22, 0.18);
	}
	.offscreen {
		position: absolute;
		top: 8px;
		right: 8px;
		z-index: 1100;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 3px;
		max-width: 160px;
		justify-content: flex-end;
		padding: 4px 7px;
		border-radius: 999px;
		background: rgba(255, 253, 249, 0.92);
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
		font-size: 0.72rem;
	}
	:global(:root[data-theme='dark']) .offscreen {
		background: rgba(31, 23, 35, 0.92);
	}
	.odot {
		width: 9px;
		height: 9px;
		border-radius: 50%;
		border: 1px solid rgba(0, 0, 0, 0.35);
	}
	.oc-count {
		color: var(--muted);
		white-space: nowrap;
	}
	@media (max-width: 640px) {
		.map-frame {
			max-height: min(68vh, 480px);
		}
		.map-frame :global(.leaflet-control-zoom a) {
			width: 40px;
			height: 40px;
			font-size: 1.35rem;
			line-height: 40px;
		}
		.map-frame :global(.leaflet-control-attribution) {
			max-width: calc(100% - 4px);
			font-size: 9px;
			white-space: normal;
			text-align: right;
		}
	}
</style>
