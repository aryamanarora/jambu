<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { base } from '$app/paths';
	import { segmentKey } from '$lib/phonology';
	onMount(() => {
		const p = new URLSearchParams(page.url.searchParams);
		p.set('view', 'evidence');
		if (p.has('s')) p.set('s', segmentKey(p.get('s')!));
		if (p.has('r')) p.set('r', segmentKey(p.get('r')!) || '∅');
		void goto(`${base}/correspondences?${p}`, { replaceState: true });
	});
</script>
<p>Opening the <a href="{base}/correspondences">correspondence explorer</a>…</p>
