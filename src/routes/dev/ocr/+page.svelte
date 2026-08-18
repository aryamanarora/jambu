<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';

	type SourceSummary = {
		id: string;
		label: string;
		available: boolean;
		inferred: boolean;
		total: number;
		pending: number;
		reviewed: number;
		stale: number;
		documents: Array<{ id: string; label: string; available: boolean; filename: string }>;
	};
	type DisplayField = { field: string; label: string; value: string };
	type DocumentRef = { id: string; label: string; available: boolean; page: number | null };
	type OcrRow = {
		key: string;
		status: string;
		auditStatus: string;
		form: string;
		pos: string;
		gloss: string;
		notes: string;
		fingerprint: string;
		stale: boolean;
		raw: DisplayField[];
		metadata: DisplayField[];
		documents: DocumentRef[];
	};

	const api = `${base}/dev/ocr/api`;
	const imageApi = `${base}/dev/ocr/image`;
	const specialCharacters = ['ā', 'ī', 'ū', 'ē', 'ō', 'ã', 'ĩ', 'ũ', 'ẽ', 'õ', 'ṭ', 'ḍ', 'ṇ', 'ṛ', 'ṝ', 'ḷ', 'ś', 'ṣ', 'ṅ', 'ñ', 'č', 'ǰ', 'ʔ', 'ː'];
	const statusOptions = [
		{ value: 'pending', label: 'Pending' },
		{ value: 'reviewed', label: 'Reviewed' },
		{ value: 'stale', label: 'Stale' },
		{ value: 'all', label: 'All' }
	];

	let sources = $state<SourceSummary[]>([]);
	let sourceId = $state('');
	let rows = $state<OcrRow[]>([]);
	let selected = $state<OcrRow | null>(null);
	let query = $state('');
	let status = $state('pending');
	let page = $state(1);
	let count = $state(0);
	let pageSize = $state(50);
	let counts = $state({ all: 0, pending: 0, reviewed: 0, stale: 0 });
	let loading = $state(false);
	let saving = $state(false);
	let loadError = $state('');
	let message = $state('');
	let imageView = $state<'crop' | 'page'>('crop');
	let form = $state('');
	let pos = $state('');
	let gloss = $state('');
	let notes = $state('');
	let formInput = $state<HTMLInputElement>();

	const source = $derived(sources.find((candidate) => candidate.id === sourceId) ?? null);
	const pageCount = $derived(Math.max(1, Math.ceil(count / pageSize)));
	const selectedIndex = $derived(selected ? rows.findIndex((row) => row.key === selected?.key) : -1);

	function choose(row: OcrRow | null) {
		selected = row;
		form = row?.form ?? '';
		pos = row?.pos ?? '';
		gloss = row?.gloss ?? '';
		notes = row?.notes ?? '';
		message = '';
	}

	async function loadSources() {
		loadError = '';
		try {
			const response = await fetch(api);
			if (!response.ok) throw new Error(await response.text());
			sources = (await response.json()).sources;
			const preferred = sources.find((candidate) => candidate.id === 'thari' && candidate.available) ?? sources.find((candidate) => candidate.available);
			if (preferred) {
				sourceId = preferred.id;
				await loadRows(1);
			}
		} catch (cause) {
			loadError = cause instanceof Error ? cause.message : String(cause);
		}
	}

	async function loadRows(nextPage = 1, preferredKey = '') {
		if (!sourceId) return;
		loading = true;
		loadError = '';
		try {
			const params = new URLSearchParams({ source: sourceId, q: query, status, page: String(nextPage) });
			const response = await fetch(`${api}?${params}`);
			if (!response.ok) throw new Error(await response.text());
			const data = await response.json();
			rows = data.rows;
			count = data.count;
			page = data.page;
			pageSize = data.pageSize;
			counts = data.counts;
			sources = sources.map((item) => item.id === sourceId ? { ...item, total: data.counts.all, pending: data.counts.pending, reviewed: data.counts.reviewed, stale: data.counts.stale } : item);
			choose(rows.find((row) => row.key === preferredKey) ?? rows[0] ?? null);
		} catch (cause) {
			loadError = cause instanceof Error ? cause.message : String(cause);
		} finally {
			loading = false;
		}
	}

	async function changeSource(value: string) {
		sourceId = value;
		query = '';
		status = 'pending';
		await loadRows(1);
	}

	async function save(reviewStatus: 'accepted' | 'corrected' | 'illegible' | 'skipped') {
		if (!selected || !sourceId) return;
		saving = true;
		message = '';
		const oldIndex = selectedIndex;
		try {
			const response = await fetch(api, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({
					source: sourceId,
					Entry_Key: selected.key,
					Status: reviewStatus,
					Form: form,
					POS: pos,
					Gloss: gloss,
					Notes: notes,
					Audit_Fingerprint: selected.fingerprint
				})
			});
			if (!response.ok) throw new Error(await response.text());
			const result = await response.json() as { status: string };
			const savedKey = selected.key;
			await loadRows(page);
			if (status === 'all' || status === 'reviewed') {
				choose(rows.find((row) => row.key === savedKey) ?? rows[Math.min(Math.max(0, oldIndex), rows.length - 1)] ?? null);
			}
			message = `${result.status === 'accepted' ? 'Accepted' : result.status === 'corrected' ? 'Saved correction for' : result.status === 'illegible' ? 'Marked illegible:' : 'Skipped'} ${savedKey}`;
		} catch (cause) {
			message = cause instanceof Error ? cause.message : String(cause);
		} finally {
			saving = false;
		}
	}

	async function removeDecision() {
		if (!selected) return;
		saving = true;
		try {
			const response = await fetch(api, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({ source: sourceId, Entry_Key: selected.key, remove: true })
			});
			if (!response.ok) throw new Error(await response.text());
			await loadRows(page, selected.key);
			message = 'Removed saved decision';
		} catch (cause) {
			message = cause instanceof Error ? cause.message : String(cause);
		} finally {
			saving = false;
		}
	}

	function insertCharacter(character: string) {
		const input = formInput;
		const start = input?.selectionStart ?? form.length;
		const end = input?.selectionEnd ?? start;
		form = `${form.slice(0, start)}${character}${form.slice(end)}`.normalize('NFC');
		requestAnimationFrame(() => {
			input?.focus();
			input?.setSelectionRange(start + character.length, start + character.length);
		});
	}

	function canUseAsForm(field: DisplayField): boolean {
		return /(form|head|gold|tesseract|kraken|abbyy)/i.test(field.field) && !/gloss|block|pos/i.test(field.field);
	}

	function imageUrl(document: DocumentRef): string {
		if (!selected) return '';
		const params = new URLSearchParams({ source: sourceId, document: document.id, entry: selected.key, view: imageView });
		return `${imageApi}?${params}`;
	}

	function moveSelection(direction: -1 | 1) {
		if (!rows.length) return;
		const next = Math.min(rows.length - 1, Math.max(0, selectedIndex + direction));
		choose(rows[next]);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return;
		const target = event.target as HTMLElement | null;
		const editing = target?.matches('input, textarea, select, [contenteditable="true"]');
		if (!editing && event.key.toLocaleLowerCase() === 'j') { event.preventDefault(); moveSelection(1); }
		else if (!editing && event.key.toLocaleLowerCase() === 'k') { event.preventDefault(); moveSelection(-1); }
		else if (!editing && event.key.toLocaleLowerCase() === 'a') { event.preventDefault(); void save('accepted'); }
		else if (!editing && event.key.toLocaleLowerCase() === 'e') { event.preventDefault(); formInput?.focus(); }
		else if (!editing && event.key.toLocaleLowerCase() === 'i') { event.preventDefault(); void save('illegible'); }
		else if (!editing && event.key.toLocaleLowerCase() === 's') { event.preventDefault(); void save('skipped'); }
	}

	onMount(() => void loadSources());
</script>

<svelte:head><title>OCR post-corrector — Jambu</title></svelte:head>
<svelte:window onkeydown={handleKeydown} />

<header class="workbench-head">
	<div>
		<p class="eyebrow">Local development tool</p>
		<h1>OCR post-corrector</h1>
		<p>Review source images and OCR passes. Decisions save to curated overlays, never generated CLDF.</p>
	</div>
	{#if source}<div class="progress"><strong>{source.reviewed.toLocaleString()}</strong><span>of {source.total.toLocaleString()} reviewed</span></div>{/if}
</header>

{#if loadError}<div class="error"><strong>Workbench unavailable.</strong> {loadError}</div>{/if}

<section class="filters" aria-label="OCR queue filters">
	<label>Source
		<select value={sourceId} onchange={(event) => void changeSource(event.currentTarget.value)}>
			{#each sources as option (option.id)}
				<option value={option.id} disabled={!option.available}>{option.label} ({option.pending} pending){option.inferred ? ' · inferred adapter' : ''}</option>
			{/each}
		</select>
	</label>
	<label>State
		<select bind:value={status} onchange={() => void loadRows(1)}>
			{#each statusOptions as option}<option value={option.value}>{option.label}</option>{/each}
		</select>
	</label>
	<form onsubmit={(event) => { event.preventDefault(); void loadRows(1); }}>
		<label>Search<input bind:value={query} placeholder="Entry key, form, gloss, or raw OCR" /></label>
		<button type="submit" disabled={loading}>{loading ? 'Loading…' : 'Search'}</button>
	</form>
	<div class="counts"><span>{counts.pending} pending</span><span>{counts.reviewed} reviewed</span>{#if counts.stale}<span class="danger">{counts.stale} stale</span>{/if}</div>
</section>

<div class="workspace">
	<section class="queue" aria-label="OCR review queue">
		<div class="panel-title"><h2>Queue</h2><span>{count.toLocaleString()} matching</span></div>
		<div class="rows" aria-busy={loading}>
			{#each rows as row (row.key)}
				<button class:active={selected?.key === row.key} class:stale={row.stale} onclick={() => choose(row)}>
					<span class="row-head"><strong>{row.form || '—'}</strong><small class={`status status-${row.status}`}>{row.stale ? 'stale' : row.status}</small></span>
					<span class="gloss">{row.gloss || 'No gloss'}</span>
					<code>{row.key}</code>
				</button>
			{/each}
			{#if !loading && !rows.length}<p class="empty">No entries match this queue.</p>{/if}
		</div>
		<div class="pager">
			<button disabled={page <= 1 || loading} onclick={() => void loadRows(page - 1)}>Previous</button>
			<span>{page} / {pageCount}</span>
			<button disabled={page >= pageCount || loading} onclick={() => void loadRows(page + 1)}>Next</button>
		</div>
	</section>

	<main class="editor" aria-label="OCR correction editor">
		{#if selected}
			<header class="entry-head">
				<div><p class="section-kicker">{selected.auditStatus}</p><h2>{selected.key}</h2></div>
				<div class="entry-nav"><button onclick={() => moveSelection(-1)} disabled={selectedIndex <= 0}>↑ K</button><button onclick={() => moveSelection(1)} disabled={selectedIndex >= rows.length - 1}>↓ J</button></div>
			</header>
			{#if selected.stale}<div class="warning"><strong>Audit changed.</strong> This saved decision refers to an older OCR row. Review and save it again.</div>{/if}

			<section class="images" aria-label="Source scans">
				<div class="section-title"><div><p class="section-kicker">Source evidence</p><h3>Page images</h3></div><div class="view-switch"><button class:active={imageView === 'crop'} onclick={() => imageView = 'crop'}>Row crop</button><button class:active={imageView === 'page'} onclick={() => imageView = 'page'}>Full page</button></div></div>
				{#if selected.documents.length}
					<div class:page-view={imageView === 'page'} class="image-grid">
						{#each selected.documents as document (document.id)}
							<figure>
								<figcaption>{document.label} · PDF p. {document.page ?? '—'}</figcaption>
								{#if document.available && document.page}<img src={imageUrl(document)} alt={`${document.label}, entry ${selected.key}`} />{:else}<div class="missing-image">Source PDF unavailable{#if source?.documents.find((item) => item.id === document.id)}<small>Expected {source.documents.find((item) => item.id === document.id)?.filename}</small>{/if}</div>{/if}
							</figure>
						{/each}
					</div>
				{:else}<p class="empty compact">This inferred adapter has no page-image mapping yet. Raw evidence remains reviewable below.</p>{/if}
			</section>

			<section class="evidence" aria-label="OCR candidates">
				<div class="section-title"><div><p class="section-kicker">Model comparison</p><h3>OCR and prior readings</h3></div></div>
				<div class="evidence-grid">
					{#each selected.raw as field (field.field + field.value)}
						<article>
							<span>{field.label}</span><p>{field.value}</p>
							{#if canUseAsForm(field)}<button title="Use this reading as the corrected form" onclick={() => form = field.value}>Use form</button>{/if}
						</article>
					{/each}
					{#if !selected.raw.length}<p class="empty compact">No alternate OCR fields were identified.</p>{/if}
				</div>
			</section>

			<section class="correction" aria-label="Corrected transcription">
				<div class="section-title"><div><p class="section-kicker">Curated overlay</p><h3>Corrected entry</h3></div></div>
				<div class="form-fields">
					<label class="form-field">Form<input bind:this={formInput} bind:value={form} lang="und" spellcheck="false" /></label>
					<label>Part of speech<input bind:value={pos} /></label>
					<label class="gloss-field">Gloss<input bind:value={gloss} /></label>
				</div>
				<div class="character-pad" aria-label="Special characters">
					{#each specialCharacters as character}<button type="button" onclick={() => insertCharacter(character)}>{character}</button>{/each}
				</div>
				<label>Review notes<textarea bind:value={notes} rows="2" placeholder="Uncertainty, damaged glyph, source discrepancy, or editorial rationale"></textarea></label>
				{#if selected.metadata.length}<dl>{#each selected.metadata as field}<div><dt>{field.label}</dt><dd>{field.value}</dd></div>{/each}</dl>{/if}
				<div class="actions">
					<button class="primary" disabled={saving || !form.trim()} onclick={() => void save('accepted')}>Accept as shown <kbd>A</kbd></button>
					<button class="primary corrected" disabled={saving || !form.trim()} onclick={() => void save('corrected')}>Save correction</button>
					<button disabled={saving} onclick={() => void save('illegible')}>Illegible <kbd>I</kbd></button>
					<button disabled={saving} onclick={() => void save('skipped')}>Skip <kbd>S</kbd></button>
					{#if ['accepted', 'corrected', 'illegible', 'skipped'].includes(selected.status)}<button class="remove" disabled={saving} onclick={() => void removeDecision()}>Undo decision</button>{/if}
				</div>
				{#if message}<p class="message" aria-live="polite">{message}</p>{/if}
			</section>
		{:else}<div class="empty editor-empty"><h2>No entry selected</h2><p>Choose an OCR record from the queue.</p></div>{/if}
	</main>
</div>

<style>
	:global(main#main-content) { max-width: none; padding-inline: clamp(.75rem, 2vw, 2rem); }
	.workbench-head { display:flex; justify-content:space-between; gap:2rem; align-items:end; margin:1.5rem 0 1rem; }
	.workbench-head h1 { margin:.1rem 0 .25rem; }
	.workbench-head p { margin:0; color:var(--muted); }
	.eyebrow,.section-kicker { color:var(--accent) !important; font-size:.72rem; font-weight:750; letter-spacing:.1em; text-transform:uppercase; }
	.progress { min-width:9rem; border-left:3px solid var(--accent); padding-left:.8rem; }
	.progress strong { display:block; font-size:1.45rem; }.progress span { color:var(--muted); font-size:.8rem; }
	.error,.warning { border:1px solid #c66; background:color-mix(in srgb,#c66 12%,var(--surface)); border-radius:6px; padding:.75rem 1rem; margin:.8rem 0; }
	.filters { display:flex; align-items:end; gap:.75rem; flex-wrap:wrap; padding:.75rem; border:1px solid var(--border); background:var(--surface); border-radius:8px; margin-bottom:1rem; }
	.filters label { display:grid; gap:.25rem; color:var(--muted); font-size:.75rem; font-weight:650; }
	.filters select,.filters input { min-height:2.25rem; border:1px solid var(--border); border-radius:5px; background:var(--bg); color:var(--text); padding:.4rem .55rem; }
	.filters form { display:flex; align-items:end; gap:.4rem; flex:1; }.filters form label { flex:1; }.filters form input { min-width:14rem; width:100%; }
	.filters button,.pager button,.entry-nav button,.view-switch button,.evidence button,.actions button,.character-pad button { border:1px solid var(--border); background:var(--surface); color:var(--text); border-radius:5px; padding:.48rem .7rem; cursor:pointer; }
	button:disabled { opacity:.45; cursor:default; }.counts { display:flex; gap:.6rem; color:var(--muted); font-size:.75rem; }.danger { color:#b33; }
	.workspace { display:grid; grid-template-columns:minmax(250px,20vw) minmax(0,1fr); border:1px solid var(--border); border-radius:8px; min-height:70vh; overflow:hidden; }
	.queue { background:var(--surface); border-right:1px solid var(--border); display:flex; flex-direction:column; min-height:0; }
	.panel-title { display:flex; align-items:baseline; justify-content:space-between; padding:.75rem; border-bottom:1px solid var(--border); }.panel-title h2 { font-size:1rem; margin:0; }.panel-title span { color:var(--muted); font-size:.72rem; }
	.rows { overflow:auto; max-height:72vh; }.rows>button { display:grid; gap:.22rem; width:100%; text-align:left; border:0; border-bottom:1px solid var(--border); border-left:3px solid transparent; background:transparent; color:var(--text); padding:.65rem .7rem; cursor:pointer; }.rows>button:hover { background:color-mix(in srgb,var(--accent) 6%,transparent); }.rows>button.active { border-left-color:var(--accent); background:color-mix(in srgb,var(--accent) 10%,transparent); }.rows>button.stale { border-left-color:#c66; }
	.row-head { display:flex; justify-content:space-between; gap:.4rem; align-items:center; }.row-head strong { font-family:var(--serif); font-size:1rem; }.rows .gloss { color:var(--muted); font-size:.78rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.rows code { color:var(--muted); font-size:.62rem; }
	.status { border-radius:99px; padding:.12rem .38rem; background:var(--bg); color:var(--muted); font:600 .58rem/1 sans-serif; text-transform:uppercase; }.status-accepted,.status-corrected { color:#267348; background:color-mix(in srgb,#4a6 14%,transparent); }
	.pager { margin-top:auto; display:flex; justify-content:space-between; align-items:center; padding:.65rem; border-top:1px solid var(--border); font-size:.75rem; }
	.editor { min-width:0; padding:1rem clamp(.8rem,2vw,1.5rem) 2rem; background:var(--bg); }.entry-head,.section-title { display:flex; justify-content:space-between; align-items:center; gap:1rem; }.entry-head h2 { font:600 .9rem/1.2 monospace; margin:.15rem 0; }.entry-nav { display:flex; gap:.35rem; }
	.images,.evidence,.correction { margin-top:1.2rem; }.section-title h3 { margin:.1rem 0 .55rem; font-size:1.05rem; }.view-switch { display:flex; }.view-switch button { border-radius:0; }.view-switch button:first-child { border-radius:5px 0 0 5px; }.view-switch button:last-child { border-radius:0 5px 5px 0; }.view-switch button.active { background:var(--accent); color:white; border-color:var(--accent); }
	.image-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:.7rem; }.image-grid figure { margin:0; border:1px solid var(--border); border-radius:6px; overflow:hidden; background:white; }.image-grid figcaption { background:var(--surface); color:var(--muted); border-bottom:1px solid var(--border); padding:.35rem .55rem; font-size:.72rem; }.image-grid img { display:block; width:100%; min-height:110px; max-height:260px; object-fit:contain; }.image-grid.page-view img { max-height:70vh; }.missing-image { min-height:110px; display:grid; place-content:center; text-align:center; color:#755; background:#f8f2ed; }.missing-image small { display:block; margin-top:.25rem; }
	.evidence-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.55rem; }.evidence article { position:relative; border:1px solid var(--border); border-radius:6px; background:var(--surface); padding:.55rem; min-height:5rem; }.evidence article>span { display:block; color:var(--muted); font-size:.65rem; text-transform:uppercase; letter-spacing:.04em; }.evidence article p { white-space:pre-wrap; overflow-wrap:anywhere; margin:.45rem 0; font:1rem/1.35 var(--serif); }.evidence article button { position:absolute; top:.35rem; right:.35rem; padding:.2rem .35rem; font-size:.65rem; }
	.correction { border-top:2px solid var(--accent); padding-top:1rem; }.form-fields { display:grid; grid-template-columns:minmax(14rem,1fr) minmax(10rem,.7fr) minmax(16rem,1.4fr); gap:.7rem; }.correction label { display:grid; gap:.28rem; color:var(--muted); font-size:.72rem; font-weight:650; }.correction input,.correction textarea { border:1px solid var(--border); border-radius:5px; background:var(--surface); color:var(--text); padding:.55rem .65rem; font:inherit; }.correction .form-field input { font:1.2rem var(--serif); }.character-pad { display:flex; flex-wrap:wrap; gap:.25rem; margin:.55rem 0 .8rem; }.character-pad button { min-width:2rem; padding:.25rem .4rem; font-family:var(--serif); }
	dl { display:flex; flex-wrap:wrap; gap:.5rem 1.2rem; margin:.8rem 0; }dl div { display:grid; grid-template-columns:auto auto; gap:.3rem; font-size:.72rem; }dt { color:var(--muted); }dd { margin:0; }
	.actions { display:flex; gap:.45rem; flex-wrap:wrap; margin-top:.8rem; }.actions .primary { color:white; background:var(--accent); border-color:var(--accent); }.actions .corrected { background:#315f80; border-color:#315f80; }.actions .remove { margin-left:auto; color:#a33; }kbd { font:inherit; opacity:.7; border:1px solid currentColor; border-radius:3px; padding:0 .2rem; }.message { color:var(--accent); font-weight:650; font-size:.82rem; }
	.empty { color:var(--muted); padding:1rem; }.compact { padding:.5rem 0; }.editor-empty { text-align:center; padding-top:15vh; }
	@media (max-width:850px) { .workspace { grid-template-columns:1fr; }.queue { border-right:0; border-bottom:1px solid var(--border); }.rows { max-height:30vh; }.form-fields { grid-template-columns:1fr; }.workbench-head { align-items:start; }.progress { display:none; } }
</style>
