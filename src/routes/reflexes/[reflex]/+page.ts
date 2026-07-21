import { redirect } from '@sveltejs/kit';
import { base } from '$app/paths';

// Reflexes and etyma are the same kind of node now — one universal page lives at /entries/[id].
// Old /reflexes/[id] links (290k, not prerendered) permanently redirect there.
export const prerender = false;

export function load({ params }: { params: { reflex: string } }) {
	throw redirect(308, `${base}/entries/${params.reflex}`);
}
