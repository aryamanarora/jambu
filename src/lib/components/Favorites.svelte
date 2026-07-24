<script lang="ts">
	// Global favourites setting: pin and order languages / clades so they sort first on the entry
	// and Sounds pages. Lives in the top-left of the nav; opens a modal.
	import { favorites, type FavToken } from '$lib/prefs.svelte';
	import { getAllDialects, getAllLanguages } from '$lib/query';
	import { CLADE_ORDER, cladeColor } from '$lib/clades';
	import type { Dialect, Language } from '$lib/types';

	let open = $state(false);
	let query = $state('');
	let langs = $state<Language[]>([]);
	let dialects = $state<Dialect[]>([]);
	let loaded = $state(false);

	async function ensureLangs() {
		if (loaded) return;
		[langs, dialects] = await Promise.all([getAllLanguages(), getAllDialects()]);
		loaded = true;
	}
	function show() {
		open = true;
		query = '';
		ensureLangs();
	}

	// search results (languages + clades), excluding anything already pinned; capped for sanity
	interface Result {
		key: string;
		token: FavToken;
		sub: string;
		swatch?: string;
	}
	const results = $derived.by<Result[]>(() => {
		const q = query.trim().toLowerCase();
		if (!q) return [];
		const out: Result[] = [];
		for (const c of CLADE_ORDER) {
			if (c.toLowerCase().includes(q) && !favorites.has('clade', c))
				out.push({ key: `clade:${c}`, token: { kind: 'clade', id: c, label: c }, sub: 'clade', swatch: cladeColor(c) });
		}
		for (const l of langs) {
			if (favorites.has('lang', l.id)) continue;
			const name = l.name ?? l.id;
			if (name.toLowerCase().includes(q))
				out.push({
					key: `lang:${l.id}`,
					token: { kind: 'lang', id: l.id, label: name, clade: l.clade },
					sub: l.clade ?? '—',
					swatch: cladeColor(l.clade)
				});
		}
		const byId = new Map(langs.map((l) => [l.id, l]));
		for (const d of dialects) {
			if (!d.name.toLowerCase().includes(q) || favorites.has('lang', d.language_id)) continue;
			const parent = byId.get(d.language_id);
			if (!parent) continue;
			out.push({
				key: `dialect:${d.token}`,
				token: { kind: 'lang', id: parent.id, label: parent.name, clade: parent.clade },
				sub: `${d.name} dialect`,
				swatch: cladeColor(parent.clade)
			});
		}
		return out.slice(0, 40);
	});
</script>

<button class="fav-btn" onclick={show} aria-label="Favorite languages and clades" title="Favorites">
	<span class="star">★</span>
	{#if favorites.count}<span class="badge">{favorites.count}</span>{/if}
</button>

{#if open}
	<div
		class="overlay"
		role="button"
		tabindex="-1"
		aria-label="Close"
		onclick={() => (open = false)}
		onkeydown={(e) => e.key === 'Escape' && (open = false)}
	></div>
	<div class="modal" role="dialog" aria-modal="true" aria-label="Favorites">
		<div class="m-head">
			<h2>Favorites</h2>
			<button class="close" onclick={() => (open = false)} aria-label="Close">✕</button>
		</div>

		{#if favorites.list.length}
			<ul class="pinned">
				{#each favorites.list as t, i (t.kind + t.id)}
					<li>
						<span class="rank">{i + 1}</span>
						<span class="sw" style="background:{cladeColor(t.kind === 'clade' ? t.id : t.clade)}"
						></span>
						<span class="lbl">{t.label}</span>
						<span class="kind">{t.kind}</span>
						<span class="ctrls">
							<button
								onclick={() => favorites.move(i, -1)}
								disabled={i === 0}
								aria-label="Move up">↑</button
							>
							<button
								onclick={() => favorites.move(i, 1)}
								disabled={i === favorites.list.length - 1}
								aria-label="Move down">↓</button
							>
							<button class="rm" onclick={() => favorites.remove(t.kind, t.id)} aria-label="Remove"
								>✕</button
							>
						</span>
					</li>
				{/each}
			</ul>
		{:else}
			<p class="empty">No favourites yet — search below to add some.</p>
		{/if}

		<input
			class="search"
			placeholder="Add a language or clade…"
			bind:value={query}
			autocomplete="off"
		/>
		{#if query.trim()}
			<ul class="results">
				{#each results as r (r.key)}
					<li>
						<button
							onclick={() => {
								favorites.add(r.token);
								query = '';
							}}
						>
							<span class="sw" style="background:{r.swatch}"></span>
							<span class="lbl">{r.token.label}</span>
							<span class="sub">{r.sub}</span>
							<span class="add">+</span>
						</button>
					</li>
				{/each}
				{#if results.length === 0}<li class="none">no match</li>{/if}
			</ul>
		{/if}
	</div>
{/if}

<style>
	.fav-btn {
		display: inline-flex;
		align-items: center;
		gap: 3px;
		background: none;
		border: none;
		cursor: pointer;
		color: var(--nav-fg-dim);
		font-size: 1rem;
		padding: 2px 4px;
	}
	.fav-btn:hover {
		color: var(--nav-fg);
	}
	.fav-btn .star {
		font-size: 1.1rem;
		line-height: 1;
	}
	.badge {
		font-size: 0.62rem;
		font-weight: 700;
		background: var(--plum);
		color: #fbeefb;
		border-radius: 999px;
		padding: 0 5px;
		line-height: 1.4;
	}

	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(20, 8, 22, 0.42);
		z-index: 90;
	}
	.modal {
		position: fixed;
		z-index: 91;
		top: 62px;
		left: 16px;
		width: min(360px, calc(100vw - 32px));
		max-height: calc(100vh - 84px);
		overflow-y: auto;
		background: var(--surface);
		/* the button lives in the dark nav header; reset text colour to the page ink so the panel
		   doesn't inherit the header's light-on-dark colour (unreadable on the light surface). */
		color: var(--ink);
		border: 1px solid var(--border-strong);
		border-radius: 14px;
		box-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
		padding: 14px 16px 16px;
	}
	.m-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 12px;
	}
	.m-head h2 {
		margin: 0;
		font-size: 1.15rem;
	}
	.close {
		background: none;
		border: none;
		color: var(--muted);
		cursor: pointer;
		font-size: 0.95rem;
	}
	.close:hover {
		color: var(--ink);
	}
	.pinned,
	.results {
		list-style: none;
		margin: 0 0 12px;
		padding: 0;
	}
	.pinned li {
		display: flex;
		align-items: center;
		gap: 7px;
		padding: 4px 0;
	}
	.rank {
		font-size: 0.7rem;
		color: var(--muted);
		width: 1.1em;
		text-align: right;
	}
	.sw {
		width: 11px;
		height: 11px;
		border-radius: 3px;
		flex: none;
		border: 1px solid rgba(0, 0, 0, 0.2);
	}
	.pinned .lbl {
		flex: 1;
		font-size: 0.9rem;
	}
	.kind {
		font-size: 0.6rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--muted);
		border: 1px solid var(--border);
		border-radius: 999px;
		padding: 0 5px;
	}
	.ctrls {
		display: inline-flex;
		gap: 2px;
	}
	.ctrls button {
		background: none;
		border: 1px solid var(--border);
		border-radius: 6px;
		width: 22px;
		height: 22px;
		cursor: pointer;
		color: var(--ink);
		font-size: 0.75rem;
		line-height: 1;
	}
	.ctrls button:hover:not(:disabled) {
		border-color: var(--berry);
	}
	.ctrls button:disabled {
		opacity: 0.3;
		cursor: default;
	}
	.ctrls .rm:hover {
		border-color: var(--bad);
		color: var(--bad);
	}
	.empty {
		font-size: 0.82rem;
		color: var(--muted);
		margin: 4px 0 12px;
	}

	.search {
		width: 100%;
		box-sizing: border-box;
		font-size: 0.9rem;
		padding: 7px 10px;
		border: 1px solid var(--border-strong);
		border-radius: 8px;
		background: var(--bg);
		color: var(--ink);
	}
	.search:focus {
		outline: none;
		border-color: var(--berry);
	}
	.results {
		margin-top: 6px;
		max-height: 260px;
		overflow-y: auto;
	}
	.results li button {
		display: flex;
		align-items: center;
		gap: 7px;
		width: 100%;
		background: none;
		border: none;
		padding: 5px 4px;
		border-radius: 6px;
		cursor: pointer;
		color: var(--ink);
		text-align: left;
	}
	.results li button:hover {
		background: var(--surface-2, rgba(128, 128, 128, 0.1));
	}
	.results .lbl {
		flex: 1;
		font-size: 0.9rem;
	}
	.results .sub {
		font-size: 0.72rem;
		color: var(--muted);
	}
	.results .add {
		color: var(--berry);
		font-weight: 700;
	}
	.none {
		font-size: 0.8rem;
		color: var(--muted);
		padding: 6px 4px;
	}
</style>
