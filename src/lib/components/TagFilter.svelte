<script lang="ts">
	// Header cell for the Reflexes table: a dropdown that filters by structured tags. Multi-select
	// with AND semantics (a row must carry every picked tag). Renders a <th> so it drops into the
	// header row alongside the FilterCell columns.
	let {
		value = '',
		onFilter
	}: { value?: string; onFilter: (key: string, value: string) => void } = $props();

	const GENDER = ['m', 'f', 'n'];
	const GRAMMATICAL = [
		'sg', 'pl', 'du',
		'adj', 'adv', 'pron', 'num', 'postp', 'prep', 'conj', 'interj', 'part', 'indecl', 'ord',
		'nom', 'acc', 'dat', 'gen', 'loc', 'abl', 'instr', 'voc', 'obl',
		'tr', 'intr', 'caus', 'pass', 'pp', 'ppp', 'pres', 'fut', 'inf', 'ger'
	];
	const NAMES: Record<string, string> = {
		m: 'masculine', f: 'feminine', n: 'neuter',
		sg: 'singular', pl: 'plural', du: 'dual',
		adj: 'adjective', adv: 'adverb', pron: 'pronoun', num: 'numeral', postp: 'postposition',
		prep: 'preposition', conj: 'conjunction', interj: 'interjection', part: 'particle',
		indecl: 'indeclinable', ord: 'ordinal',
		nom: 'nominative', acc: 'accusative', dat: 'dative', gen: 'genitive', loc: 'locative',
		abl: 'ablative', instr: 'instrumental', voc: 'vocative', obl: 'oblique',
		tr: 'transitive', intr: 'intransitive', caus: 'causative', pass: 'passive',
		pp: 'past participle', ppp: 'past passive participle', pres: 'present', fut: 'future',
		inf: 'infinitive', ger: 'gerund'
	};

	const selected = $derived(new Set(value.split(/\s+/).filter(Boolean)));
	let open = $state(false);
	let root: HTMLElement;

	function toggle(t: string) {
		const next = new Set(selected);
		if (next.has(t)) next.delete(t);
		else next.add(t);
		onFilter('tags', [...next].join(' '));
	}
	function clear() {
		onFilter('tags', '');
	}

	$effect(() => {
		if (!open) return;
		const onDown = (e: MouseEvent) => {
			if (root && !root.contains(e.target as Node)) open = false;
		};
		const onKey = (e: KeyboardEvent) => e.key === 'Escape' && (open = false);
		window.addEventListener('mousedown', onDown);
		window.addEventListener('keydown', onKey);
		return () => {
			window.removeEventListener('mousedown', onDown);
			window.removeEventListener('keydown', onKey);
		};
	});
</script>

<th bind:this={root}>
	<div class="field">
		<button
			class="trigger"
			class:active={selected.size > 0}
			aria-expanded={open}
			onclick={() => (open = !open)}
		>
			Tags{#if selected.size}<span class="count">{selected.size}</span>{/if}
			<span class="caret" class:up={open}>▾</span>
		</button>
	</div>
	{#if open}
		<div class="panel">
			<div class="grp">
				<div class="grp-lbl">
					gender
					{#if selected.size}<button class="clear" onclick={clear}>clear all</button>{/if}
				</div>
				<div class="chips">
					{#each GENDER as t (t)}
						<button
							class="chip gender"
							class:on={selected.has(t)}
							title={NAMES[t]}
							onclick={() => toggle(t)}>{t}</button
						>
					{/each}
				</div>
			</div>
			<div class="grp">
				<div class="grp-lbl">grammatical</div>
				<div class="chips">
					{#each GRAMMATICAL as t (t)}
						<button
							class="chip"
							class:on={selected.has(t)}
							title={NAMES[t] ?? t}
							onclick={() => toggle(t)}>{t}</button
						>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</th>

<style>
	th {
		position: relative;
	}
	.trigger {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		font: inherit;
		font-size: 0.82rem;
		padding: 3px 9px;
		border: 1px solid var(--border-strong);
		border-radius: 7px;
		background: var(--bg);
		color: var(--ink);
		cursor: pointer;
		white-space: nowrap;
	}
	.trigger:hover {
		border-color: var(--berry);
	}
	.trigger.active {
		background: var(--plum);
		color: #fbeefb;
		border-color: var(--plum);
	}
	.count {
		font-size: 0.62rem;
		font-weight: 700;
		background: color-mix(in srgb, currentColor 22%, transparent);
		border-radius: 999px;
		padding: 0 5px;
	}
	.caret {
		font-size: 0.6rem;
		transition: transform 0.12s ease;
	}
	.caret.up {
		transform: rotate(180deg);
	}
	.panel {
		position: absolute;
		z-index: 40;
		top: calc(100% + 4px);
		left: 0;
		width: 250px;
		background: var(--surface);
		color: var(--ink);
		border: 1px solid var(--border-strong);
		border-radius: 10px;
		box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
		padding: 9px 11px 11px;
		text-align: left;
		font-weight: 400;
	}
	.grp + .grp {
		margin-top: 9px;
	}
	.grp-lbl {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		font-size: 0.65rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
		margin-bottom: 5px;
	}
	.clear {
		border: none;
		background: none;
		color: var(--berry);
		cursor: pointer;
		font-size: 0.68rem;
		text-transform: none;
		letter-spacing: 0;
		padding: 0;
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}
	.chip {
		font-size: 0.72rem;
		padding: 1px 8px;
		border-radius: 999px;
		border: 1px solid var(--border-strong);
		background: var(--surface);
		color: var(--ink);
		cursor: pointer;
		font-variant: small-caps;
	}
	.chip:hover {
		border-color: var(--berry);
	}
	.chip.on {
		background: var(--plum);
		color: #fbeefb;
		border-color: var(--plum);
	}
	.chip.gender.on {
		background: var(--berry);
		border-color: var(--berry);
	}
</style>
