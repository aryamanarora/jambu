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
		bounds
	}: {
		markers: MapMarker[];
		center?: [number, number];
		zoom?: number;
		height?: string;
		showAllTooltips?: boolean;
		bounds?: [[number, number], [number, number]]; // fixed initial framing (overrides auto-fit)
	} = $props();

	let el: HTMLDivElement;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let map: any = null;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let L: any = null;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let layer: any = null;

	function iconUrl(svg: string): string {
		return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
	}

	function draw() {
		if (!map || !L) return;
		if (layer) layer.remove();
		layer = L.layerGroup().addTo(map);
		const pts: [number, number][] = [];
		for (const m of markers) {
			if (m.lat == null || m.long == null) continue;
			let marker: any;
			if (m.color && m.svg?.includes('polygon')) {
				// historical-language marker: keep the rhombus shape (as on the languages page)
				// but recolour its fill to the overlay/clade colour instead of drawing a circle.
				const svg = m.svg.replace(/fill="[^"]*"/, `fill="${m.color}"`);
				const icon = L.icon({ iconUrl: iconUrl(svg), iconSize: [16, 16] });
				marker = L.marker([m.lat, m.long], { icon, opacity: m.dim ? 0.4 : 1 }).addTo(layer);
			} else if (m.color) {
				// filled circle — recolourable (used for correspondence overlays)
				marker = L.circleMarker([m.lat, m.long], {
					radius: m.radius ?? 7,
					fillColor: m.color,
					color: 'rgba(0,0,0,0.55)',
					weight: 1,
					fillOpacity: m.dim ? 0.25 : 0.92,
					opacity: m.dim ? 0.35 : 1
				}).addTo(layer);
			} else {
				const icon = L.icon({ iconUrl: iconUrl(m.svg), iconSize: [16, 16] });
				marker = L.marker([m.lat, m.long], { icon }).addTo(layer);
			}
			if (m.tooltip) marker.bindTooltip(m.tooltip);
			if (m.popupHtml) marker.bindPopup(m.popupHtml);
			if (m.onClick) marker.on('click', m.onClick);
			pts.push([m.lat, m.long]);
		}
		if (!center && !bounds && pts.length) {
			map.fitBounds(pts, { padding: [30, 30], maxZoom: 7 });
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
			{ attribution: 'Tiles © Esri — US National Park Service', maxZoom: 8 }
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
	}
	.map-frame :global(.map) {
		height: 100%;
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
</style>
