/**
 * prefs.svelte.ts — user preferences, persisted to localStorage.
 *
 * Currently: an ordered list of "favourites" (languages and/or clades) that the user pins so they
 * sort first on the entry and sound-correspondence pages. The list is a single ordered sequence
 * mixing both kinds; a language favourite also lifts its whole clade in clade-grouped views.
 */
import { browser } from '$app/environment';

export type FavKind = 'lang' | 'clade';
export interface FavToken {
	kind: FavKind;
	id: string; // language id, or clade name
	label: string; // display label
	clade?: string; // for a language favourite: its clade (so it can lift that clade)
}

const KEY = 'jambu-favorites';

let items = $state<FavToken[]>([]);
let loaded = false;

export function loadFavorites(): void {
	if (loaded || !browser) return;
	loaded = true;
	try {
		const raw = localStorage.getItem(KEY);
		if (raw) items = JSON.parse(raw);
	} catch {
		/* ignore malformed storage */
	}
}

function persist(): void {
	if (!browser) return;
	try {
		localStorage.setItem(KEY, JSON.stringify(items));
	} catch {
		/* ignore quota / disabled storage */
	}
}

export const favorites = {
	get list(): FavToken[] {
		return items;
	},
	get count(): number {
		return items.length;
	},
	has(kind: FavKind, id: string): boolean {
		return items.some((t) => t.kind === kind && t.id === id);
	},
	add(t: FavToken): void {
		if (this.has(t.kind, t.id)) return;
		items = [...items, t];
		persist();
	},
	remove(kind: FavKind, id: string): void {
		items = items.filter((t) => !(t.kind === kind && t.id === id));
		persist();
	},
	move(index: number, dir: -1 | 1): void {
		const j = index + dir;
		if (index < 0 || j < 0 || index >= items.length || j >= items.length) return;
		const next = [...items];
		[next[index], next[j]] = [next[j], next[index]];
		items = next;
		persist();
	},
	clear(): void {
		items = [];
		persist();
	}
};

/**
 * Favourite rank of a clade: the earliest position among favourites that "covers" it — the clade
 * itself pinned, or a pinned language belonging to it. `Infinity` when the clade isn't favoured.
 */
export function cladeFavRank(clade: string): number {
	let best = Infinity;
	for (let i = 0; i < items.length; i++) {
		const t = items[i];
		if ((t.kind === 'clade' && t.id === clade) || (t.kind === 'lang' && t.clade === clade)) {
			if (i < best) best = i;
		}
	}
	return best;
}

/** Favourite rank of a language (its own pin position), or `Infinity` if not pinned. */
export function langFavRank(langId: string): number {
	const i = items.findIndex((t) => t.kind === 'lang' && t.id === langId);
	return i === -1 ? Infinity : i;
}
