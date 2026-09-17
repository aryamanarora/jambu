<script lang="ts">
	import chart from '$lib/transcriptionChart.json';
	import {
		CONSONANT_PLACES,
		CONSONANT_ROWS,
		CLUSTER_GROUPS,
		VOWEL_BACKNESS,
		VOWEL_ROWS,
		VOWEL_EXTRAS
	} from '$lib/ipaChart';

	type Entry = {
		house: string;
		profiles: number;
		agreement: number;
		variants: { house: string; profiles: number; examples: string[] }[];
	};

	const map = chart.map as Record<string, Entry>;

	function lookup(ipa: string): Entry | null {
		return ipa ? (map[ipa] ?? null) : null;
	}

	/** A symbol the profiles render as something other than itself is the interesting case. */
	function isRespelt(ipa: string, entry: Entry | null): boolean {
		return !!entry && entry.house !== ipa;
	}

	function isContested(entry: Entry | null): boolean {
		return !!entry && entry.variants.length > 0;
	}

	function title(ipa: string, entry: Entry | null): string {
		if (!entry) return `${ipa} — no profile maps this symbol`;
		const parts = [
			`${ipa} → ${entry.house} in ${entry.agreement} of ${entry.profiles} profiles`
		];
		for (const variant of entry.variants) {
			parts.push(
				`${variant.house} in ${variant.profiles} (${variant.examples.join(', ')})`
			);
		}
		return parts.join('; ');
	}

	// Every disagreement in one place, so the tables stay readable and nothing is hidden. The
	// space grapheme is excluded: profiles map it to the word-boundary marker rather than to a
	// sound, and it renders as a blank row that reads like a bug.
	const contested = Object.entries(map)
		.filter(
			([ipa, entry]) => ipa.trim() !== '' && entry.variants.length > 0 && entry.profiles >= 5
		)
		.sort((a, b) => b[1].profiles - a[1].profiles);

	let showAllContested = $state(false);
	const shownContested = $derived(showAllContested ? contested : contested.slice(0, 12));
</script>

{#snippet symbol(ipa: string, boxed = false)}
	{@const entry = lookup(ipa)}
	{#if ipa}
		<span class="sym" class:boxed class:respelt={isRespelt(ipa, entry)} class:unmapped={!entry} title={title(ipa, entry)}>
			<span class="ipa">{ipa}</span>
			{#if entry}<span class="house">{entry.house}{#if isContested(entry)}<span class="dagger">†</span>{/if}</span>{/if}
		</span>
	{:else}<span class="sym empty"></span>{/if}
{/snippet}

<svelte:head>
	<title>Transcription — Jambu</title>
	<meta
		name="description"
		content="The IPA consonant and vowel charts with Jambu's house transcription overlaid on each symbol, generated from the sound profiles of every ingested source."
	/>
</svelte:head>

<h1>Transcription</h1>
<p class="lead">
	The IPA charts, with the glyph <em>Jambu</em> writes for each sound laid over the symbol itself.
</p>

<p>
	Every source in the dictionary carries a <strong>sound profile</strong> — a mapping from that
	source's own notation onto a shared house transcription, so that a Halbi form and a Kashmiri one
	can be read side by side. This page is those profiles turned inside out: for each IPA symbol, the
	house glyph that
	{chart.profileCount} profiles agree on, drawn from {chart.graphemeCount.toLocaleString()} mapped
	graphemes.
</p>

<div class="legend">
	<span class="key"><span class="swatch respelt"></span> respelt in the house transcription</span>
	<span class="key"><span class="swatch same"></span> written as the IPA symbol itself</span>
	<span class="key"><span class="swatch none"></span> not mapped by any profile</span>
	<span class="key"><span class="dagger">†</span> profiles disagree — hover for the split</span>
</div>

<h2>Pulmonic consonants</h2>
<div class="scroller">
	<table class="ipa">
		<thead>
			<tr>
				<th scope="col" class="manner-col"></th>
				{#each CONSONANT_PLACES as place}
					<th scope="col"><span class="place">{place}</span></th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{#each CONSONANT_ROWS as row}
				<tr>
					<th scope="row" class="manner-col">{row.manner}</th>
					{#each row.cells as cell}
						{#if cell === null}
							<td class="impossible" aria-label="impossible articulation"></td>
						{:else}
							<td>
								<div class="pair">
									{#each cell as ipa}
										{@render symbol(ipa)}
									{/each}
								</div>
							</td>
						{/if}
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>
<p class="caption">
	Each cell pairs the voiceless symbol with the voiced one. Shaded cells are articulations the IPA
	judges impossible.
</p>

<h2>Vowels</h2>
<div class="scroller">
	<table class="ipa vowels">
		<thead>
			<tr>
				<th scope="col" class="manner-col"></th>
				{#each VOWEL_BACKNESS as backness}
					<th scope="col"><span class="place">{backness}</span></th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{#each VOWEL_ROWS as row}
				<tr>
					<th scope="row" class="manner-col">{row.height}</th>
					{#each row.cells as cell}
						<td>
							<div class="pair">
								{#each cell as ipa}
									{@render symbol(ipa)}
								{/each}
							</div>
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>
<p class="caption">Each cell pairs the unrounded vowel with the rounded one.</p>

<h2>Beyond the chart</h2>
<p>
	South Asian sources write affricates, aspirates and nasal vowels as units, and the profiles map
	them as units too rather than composing them from their parts.
</p>

{#each [...CLUSTER_GROUPS, ...VOWEL_EXTRAS] as group}
	<section class="group">
		<h3>{group.label}</h3>
		<p class="caption">{group.note}</p>
		<div class="strip">
			{#each group.symbols as ipa}
				{@render symbol(ipa, true)}
			{/each}
		</div>
	</section>
{/each}

<h2>Where the profiles disagree</h2>
<p>
	A minority reading is usually not an error but a property of the source: a transcription that
	marks vowel length by quality rather than by a macron will send <span class="phon">a</span> to
	<span class="phon">ā</span>, while one that marks it explicitly will not. These are the symbols
	whose treatment is genuinely split.
</p>
<div class="scroller">
	<table class="contested">
		<thead>
			<tr>
				<th scope="col">IPA</th>
				<th scope="col">Majority</th>
				<th scope="col">Also written</th>
			</tr>
		</thead>
		<tbody>
			{#each shownContested as [ipa, entry]}
				<tr>
					<td class="phon big">{ipa}</td>
					<td>
						<span class="phon big">{entry.house}</span>
						<span class="count">{entry.agreement}/{entry.profiles}</span>
					</td>
					<td>
						{#each entry.variants as variant, index}
							{#if index > 0}<span class="sep">·</span>{/if}
							<span class="phon">{variant.house || '∅'}</span>
							<span class="count">{variant.profiles}</span>
							<span class="examples">{variant.examples.join(', ')}</span>
						{/each}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
{#if contested.length > shownContested.length || showAllContested}
	<button class="more" onclick={() => (showAllContested = !showAllContested)}>
		{showAllContested ? 'Show fewer' : `Show all ${contested.length}`}
	</button>
{/if}

<p class="provenance">
	Generated from <code>data/conversion/*.txt</code> by
	<code>scripts/build_transcription_chart.py</code>. A symbol mapped by only one or two profiles is
	still shown, but says less about the house convention than one mapped by fifty.
</p>

<style>
	.lead {
		font-size: 1.15rem;
		color: var(--muted);
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem 1.1rem;
		margin: 1.4rem 0 0.6rem;
		padding: 0.7rem 0.9rem;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background: var(--surface-2);
		font-size: 0.82rem;
		color: var(--muted);
	}
	.key {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
	}
	.swatch {
		width: 0.85rem;
		height: 0.85rem;
		border-radius: 3px;
		border: 1px solid var(--border-strong);
	}
	.swatch.respelt {
		background: color-mix(in srgb, var(--berry) 18%, var(--surface));
		border-color: color-mix(in srgb, var(--berry) 45%, transparent);
	}
	.swatch.same {
		background: var(--surface);
	}
	.swatch.none {
		background: var(--clade-empty);
	}

	.scroller {
		overflow-x: auto;
		margin: 0.8rem 0;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background: var(--surface);
	}
	table.ipa {
		border-collapse: collapse;
		width: 100%;
		min-width: 54rem;
	}
	table.ipa.vowels {
		min-width: 26rem;
	}
	table.ipa th,
	table.ipa td {
		border: 1px solid var(--border);
		padding: 0;
		text-align: center;
		vertical-align: middle;
	}
	table.ipa thead th {
		padding: 0.45rem 0.3rem;
		background: var(--surface-2);
		font-size: 0.72rem;
		font-weight: 600;
		color: var(--muted);
		letter-spacing: 0.02em;
	}
	.place {
		display: inline-block;
		line-height: 1.15;
	}
	.manner-col {
		width: 9.5rem;
		text-align: left !important;
		padding: 0.4rem 0.6rem !important;
		background: var(--surface-2);
		font-size: 0.76rem;
		font-weight: 600;
		color: var(--muted);
		white-space: nowrap;
	}
	td.impossible {
		background: repeating-linear-gradient(
			45deg,
			var(--clade-empty),
			var(--clade-empty) 4px,
			var(--surface-2) 4px,
			var(--surface-2) 8px
		);
	}
	.pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
	}
	.pair > .sym + .sym {
		border-left: 1px dotted var(--border);
	}

	.sym {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.05rem;
		min-height: 3.1rem;
		padding: 0.3rem 0.15rem;
	}
	.sym.empty {
		min-height: 3.1rem;
	}
	.sym .ipa {
		font-family: var(--font-phon);
		font-size: 1.15rem;
		line-height: 1;
		color: var(--ink);
	}
	.sym .house {
		font-family: var(--font-phon);
		font-size: 0.9rem;
		line-height: 1;
		color: var(--muted);
	}
	.sym.respelt {
		background: color-mix(in srgb, var(--berry) 12%, var(--surface));
	}
	.sym.respelt .house {
		color: var(--berry);
		font-weight: 600;
	}
	.sym.unmapped .ipa {
		color: var(--faint);
	}
	.sym.boxed {
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		min-width: 3.2rem;
		min-height: 3rem;
	}
	.dagger {
		color: var(--warn);
		font-weight: 700;
	}

	.group {
		margin: 1.2rem 0;
	}
	.group h3 {
		margin: 0 0 0.15rem;
		font-size: 0.95rem;
	}
	.strip {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-top: 0.5rem;
	}
	.caption {
		font-size: 0.8rem;
		color: var(--muted);
		margin: 0.3rem 0 0;
	}

	table.contested {
		border-collapse: collapse;
		width: 100%;
		min-width: 34rem;
	}
	table.contested th,
	table.contested td {
		border-bottom: 1px solid var(--border);
		padding: 0.4rem 0.7rem;
		text-align: left;
		vertical-align: baseline;
	}
	table.contested thead th {
		background: var(--surface-2);
		font-size: 0.74rem;
		color: var(--muted);
	}
	.phon {
		font-family: var(--font-phon);
	}
	.phon.big {
		font-size: 1.05rem;
	}
	.count {
		font-size: 0.72rem;
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.examples {
		font-size: 0.72rem;
		color: var(--faint);
	}
	.sep {
		color: var(--faint);
		margin: 0 0.3rem;
	}
	.more {
		margin-top: 0.6rem;
		padding: 0.35rem 0.8rem;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface);
		color: var(--plum-2);
		font: inherit;
		font-size: 0.82rem;
		cursor: pointer;
	}
	.more:hover {
		border-color: var(--plum-hover);
		color: var(--plum-hover);
	}
	.provenance {
		margin-top: 1.6rem;
		font-size: 0.8rem;
		color: var(--muted);
	}
</style>
