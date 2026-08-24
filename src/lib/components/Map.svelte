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
		mutedTiles = false
	}: {
		markers: MapMarker[];
		center?: [number, number];
		zoom?: number;
		height?: string;
		showAllTooltips?: boolean;
		bounds?: [[number, number], [number, number]]; // fixed initial framing (overrides auto-fit)
		fitOnce?: boolean; // auto-fit only the first draw, never re-adjust the view on later updates
		mutedTiles?: boolean; // soften the basemap so dense data overlays remain dominant
	} = $props();

	let el: HTMLDivElement;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let map: any = null;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let L: any = null;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let layer: any = null;
	let lastFitSig = ''; // coord signature of the last auto-fit (skip refit on colour-only redraws)
	let hasFit = false; // whether the view has been auto-fit at least once (for fitOnce)

	function iconUrl(svg: string): string {
		return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
	}

	function draw() {
		if (!map || !L) return;
		if (layer) layer.remove();
		layer = L.layerGroup().addTo(map);
		const pts: [number, number][] = [];
		const foreground: any[] = [];
		for (const m of markers) {
			if (m.lat == null || m.long == null) continue;
			let marker: any;
			const iconSize = m.foreground ? 14 : 16;
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
			if (m.popupHtml) marker.bindPopup(m.popupHtml);
			if (m.onClick) marker.on('click', m.onClick);
			if (m.foreground) foreground.push(marker);
			pts.push([m.lat, m.long]);
		}
		// Raise emphasis markers only after every point exists. Calling bringToFront while drawing is
		// not sufficient: a later context point can otherwise be appended above the highlight.
		for (const marker of foreground) {
			marker.bringToFront?.();
			marker.setZIndexOffset?.(1000);
		}
		// auto-fit the view. With fitOnce, only the first draw fits — later redraws (recolouring on
		// selection, re-jittering) leave the user's pan/zoom untouched. Otherwise re-fit only when the
		// set of point coordinates actually changes, so a colour-only redraw won't reset the view.
		const sig = pts.map((p) => p.join()).join('|');
		const shouldFit = fitOnce ? !hasFit : sig !== lastFitSig;
		if (!center && !bounds && pts.length && shouldFit) {
			map.fitBounds(pts, { padding: [30, 30], maxZoom: 7 });
			lastFitSig = sig;
			hasFit = true;
		}
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
		map = L.map(el, { scrollWheelZoom: false }).setView(center ?? [20.5937, 78.9629], zoom);
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
		draw();
	});

	// redraw when markers change
	$effect(() => {
		markers;
		showAllTooltips;
		if (map) draw();
	});

	onDestroy(() => {
		if (map) map.remove();
	});
</script>

<div class="map-frame" style="height: {height}">
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
	.map-frame :global(.map-point-foreground) {
		filter: drop-shadow(0 1px 1px rgba(20, 14, 12, 0.9)) drop-shadow(0 0 3px rgba(20, 14, 12, 0.35));
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
