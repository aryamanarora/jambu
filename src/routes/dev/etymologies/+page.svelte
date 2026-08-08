<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';

	type QueueForm = {
		id: string;
		word: string;
		gloss: string;
		phonemic: string;
		notes: string;
		language_id: string;
		language: string;
		sources: string | null;
	};
	type Candidate = {
		id: string;
		word: string;
		gloss: string;
		language: string;
		reflex_count: number;
		lang_count: number;
		sources: string | null;
		confidence?: number;
		concept_score?: number;
		sound_score?: number;
		cognate_score?: number;
		best_cognate?: string | null;
	};
	type Option = { id: string; name?: string; short?: string };
	type Assignment = { Form_ID: string; Etymon_ID: string; Relation: string; Notes: string };

	let queue = $state<QueueForm[]>([]);
	let candidates = $state<Candidate[]>([]);
	let languages = $state<Option[]>([]);
	let sources = $state<Option[]>([]);
	let assignments = $state<Record<string, Assignment>>({});
	let selected = $state<QueueForm | null>(null);
	let selectedCandidate = $state<Candidate | null>(null);
	let queueQuery = $state('');
	let candidateQuery = $state('');
	let language = $state('');
	let source = $state('');
	let relation = $state<'reflex' | 'borrowed'>('reflex');
	let notes = $state('');
	let count = $state(0);
	let page = $state(1);
	let busy = $state(false);
	let candidateBusy = $state(false);
	let candidateError = $state('');
	let saving = $state(false);
	let message = $state('');
	let loadError = $state('');

	const api = `${base}/dev/etymologies/api`;
	let candidateRequest = 0;

	// ---- edge-model review queue (auto-classified alternate-etymology hypotheses) ----
	type ReviewRow = {
		form_id: string;
		form_word: string;
		form_gloss: string;
		form_lang: string | null;
		etymon_id: string;
		etymon_word: string;
		etymon_gloss: string;
		etymon_lang: string | null;
		etymon_is_entry: boolean;
		kind: string;
		rank: number;
		note: string;
	};
	let reviewRows = $state<ReviewRow[]>([]);
	let reviewTotal = $state(0);
	let showReview = $state(false);
	async function loadReview() {
		const response = await fetch(`${api}?mode=review`);
		if (!response.ok) return;
		const data = await response.json();
		reviewRows = data.rows;
		reviewTotal = data.total;
	}
	async function resolveReview(row: ReviewRow, accept: boolean) {
		await fetch(api, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({
				Form_ID: row.form_id,
				Etymon_ID: row.etymon_id,
				Kind: row.kind === 'borrowed' ? 'borrowed' : 'reflex',
				Rank: String(Math.max(2, row.rank)),
				reject: !accept
			})
		});
		reviewRows = reviewRows.filter((r) => r !== row);
		message = accept
			? `Accepted alternate ${row.form_word} < ${row.etymon_word}`
			: `Rejected alternate ${row.form_word} < ${row.etymon_word}`;
	}

	async function loadQueue(nextPage = 1) {
		busy = true;
		loadError = '';
		const params = new URLSearchParams({ q: queueQuery, language, source, page: String(nextPage) });
		try {
			const response = await fetch(`${api}?${params}`);
			if (!response.ok) throw new Error(await response.text());
			const data = await response.json();
			queue = data.rows;
			count = data.count;
			page = data.page;
			languages = data.languages;
			sources = data.sources;
			assignments = Object.fromEntries(data.assignments.map((a: Assignment) => [a.Form_ID, a]));
			if (selected && !queue.some((row) => row.id === selected?.id)) selectForm(queue[0] ?? null);
		} catch (cause) {
			loadError = cause instanceof Error ? cause.message : String(cause);
		} finally {
			busy = false;
		}
	}

	async function searchCandidates(): Promise<Candidate[] | null> {
		const request = ++candidateRequest;
		candidateBusy = true;
		candidateError = '';
		candidates = [];
		const params = new URLSearchParams({
			mode: 'candidates',
			q: candidateQuery,
			form: selected?.id ?? ''
		});
		try {
			const response = await fetch(`${api}?${params}`);
			if (!response.ok) throw new Error(await response.text());
			const rows = (await response.json()).rows as Candidate[];
			if (request !== candidateRequest) return null;
			candidates = rows;
			return rows;
		} catch (cause) {
			if (request === candidateRequest)
				candidateError = cause instanceof Error ? cause.message : String(cause);
			return null;
		} finally {
			if (request === candidateRequest) candidateBusy = false;
		}
	}

	function selectForm(form: QueueForm | null) {
		selected = form;
		selectedCandidate = null;
		message = '';
		const saved = form ? assignments[form.id] : undefined;
		relation = saved?.Relation === 'borrowed' ? 'borrowed' : 'reflex';
		notes = saved?.Notes ?? '';
		candidateQuery = saved?.Etymon_ID ?? form?.gloss ?? '';
		void searchCandidates().then((rows) => {
			if (saved && rows && selected?.id === form?.id)
				selectedCandidate = rows.find((candidate) => candidate.id === saved.Etymon_ID) ?? null;
		});
	}

	async function saveAndNext() {
		if (!selected || !selectedCandidate) return;
		saving = true;
		message = '';
		try {
			const response = await fetch(api, {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({
					Form_ID: selected.id,
					Etymon_ID: selectedCandidate.id,
					Relation: relation,
					Notes: notes
				})
			});
			if (!response.ok) throw new Error(await response.text());
			assignments[selected.id] = {
				Form_ID: selected.id,
				Etymon_ID: selectedCandidate.id,
				Relation: relation,
				Notes: notes
			};
			const index = queue.findIndex((row) => row.id === selected?.id);
			message = `Saved ${selected.id} → ${selectedCandidate.id}`;
			selectForm(queue[index + 1] ?? queue[index] ?? null);
		} catch (cause) {
			message = cause instanceof Error ? cause.message : String(cause);
		} finally {
			saving = false;
		}
	}

	async function removeAssignment() {
		if (!selected || !assignments[selected.id]) return;
		const response = await fetch(api, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ Form_ID: selected.id, remove: true })
		});
		if (!response.ok) {
			message = await response.text();
			return;
		}
		delete assignments[selected.id];
		selectForm(selected);
		message = 'Removed saved assignment';
	}

	onMount(() => void loadQueue());
</script>

<svelte:head>
	<title>Etymology workbench — Jambu</title>
</svelte:head>

<header class="workbench-head">
	<div>
		<p class="eyebrow">Local development tool</p>
		<h1>Etymology workbench</h1>
		<p>Link unetymologised forms to existing etyma. Saves to the curated assignment overlay.</p>
	</div>
	<div class="counter"><strong>{count.toLocaleString()}</strong><span>matching forms</span></div>
</header>

{#if loadError}
	<div class="error">
		<strong>Workbench unavailable.</strong> {loadError}
		<p>Run the stable-ID data pass and rebuild the development database, then restart Vite.</p>
	</div>
{:else}
	<section class="filters" aria-label="Queue filters">
		<form onsubmit={(event) => { event.preventDefault(); void loadQueue(1); }}>
			<label>Search<input bind:value={queueQuery} placeholder="form, gloss, notes, or language" /></label>
			<label>Language<select bind:value={language}><option value="">All languages</option>{#each languages as option}<option value={option.id}>{option.name}</option>{/each}</select></label>
			<label>Source<select bind:value={source}><option value="">All sources</option>{#each sources as option}<option value={option.id}>{option.short}</option>{/each}</select></label>
			<button type="submit" disabled={busy}>{busy ? 'Searching…' : 'Search queue'}</button>
		</form>
	</section>

	<section class="filters" aria-label="Migration review queue">
		<button
			type="button"
			onclick={() => {
				showReview = !showReview;
				if (showReview && !reviewRows.length) void loadReview();
			}}>{showReview ? 'Hide' : 'Show'} hypothesis review queue</button
		>
		{#if showReview}
			<p class="muted">
				{reviewRows.length} auto-classified alternate-etymology edges awaiting curation
				(accept keeps the hypothesis, reject removes it on the next data build).
			</p>
			<ul class="review-list">
				{#each reviewRows.slice(0, 50) as row (row.form_id + row.etymon_id)}
					<li>
						<a href="{base}/reflexes/{row.form_id}" target="_blank">{row.form_word}</a>
						<span class="muted">({row.form_lang ?? '—'})</span>
						&lt; proposed
						<a href="{base}/{row.etymon_is_entry ? 'entries' : 'reflexes'}/{row.etymon_id}" target="_blank"
							>{row.etymon_word}</a
						>
						<span class="muted">({row.etymon_lang ?? '—'}) · {row.note.replace('review:', '')}</span>
						<button type="button" onclick={() => void resolveReview(row, true)}>accept</button>
						<button type="button" onclick={() => void resolveReview(row, false)}>reject</button>
					</li>
				{/each}
			</ul>
		{/if}
	</section>

	<div class="workspace">
		<section class="queue" aria-label="Unetymologised forms">
			<div class="panel-title"><h2>Queue</h2><span>Page {page} of {Math.max(1, Math.ceil(count / 50))}</span></div>
			<div class="rows">
				{#each queue as form (form.id)}
					<button class:active={selected?.id === form.id} onclick={() => selectForm(form)}>
						<span class="word">{form.word || '—'}</span>
						<span class="language">{form.language}</span>
						<span class="gloss">{form.gloss || 'No gloss'}</span>
						{#if assignments[form.id]}<span class="saved">✓ {assignments[form.id].Etymon_ID}</span>{/if}
					</button>
				{/each}
				{#if !busy && !queue.length}<p class="empty">No forms match these filters.</p>{/if}
			</div>
			<div class="pager"><button disabled={page <= 1} onclick={() => void loadQueue(page - 1)}>Previous</button><button disabled={page * 50 >= count} onclick={() => void loadQueue(page + 1)}>Next</button></div>
		</section>

		<section class="editor" aria-label="Etymology editor">
			{#if selected}
				<div class="selected-form">
					<div><span class="language">{selected.language}</span><h2>{selected.word}</h2><p class="gloss">{selected.gloss}</p></div>
					<a href={`${base}/entries/${selected.id}`} target="_blank">Open form ↗</a>
				</div>
				<dl>
					{#if selected.phonemic}<div><dt>Phonemic</dt><dd>{selected.phonemic}</dd></div>{/if}
					{#if selected.sources}<div><dt>Source</dt><dd>{selected.sources}</dd></div>{/if}
					{#if selected.notes}<div><dt>Notes</dt><dd>{selected.notes}</dd></div>{/if}
					<div><dt>Persistent ID</dt><dd><code>{selected.id}</code></dd></div>
				</dl>

				<form class="candidate-search" onsubmit={(event) => { event.preventDefault(); void searchCandidates(); }}>
					<label>Find an etymon<input bind:value={candidateQuery} placeholder="headword, gloss, language, or ID" /></label>
					<button type="submit" disabled={candidateBusy}>{candidateBusy ? 'Searching…' : 'Search'}</button>
				</form>
				{#if candidateError}<p class="candidate-error">Could not load suggestions: {candidateError}</p>{/if}
				<div class="table-wrap candidate-table-wrap" aria-busy={candidateBusy}>
					<table class="data candidate-table">
						<thead>
							<tr>
								<th><span class="sr-only">Select</span></th><th>Etymon</th><th>Language</th><th>Gloss</th><th>Confidence</th>
								<th>Closest reflex</th><th>Reference</th>
							</tr>
						</thead>
						<tbody>
							{#if candidateBusy}
								{#each Array(6) as _, index}
									<tr class="skeleton-row" aria-hidden="true">
										<td><span class="skeleton select-skeleton"></span></td>
										<td><span class="skeleton wide"></span></td>
										<td><span class="skeleton medium"></span></td>
										<td><span class="skeleton wide"></span></td>
										<td><span class="skeleton meter" style={`animation-delay:${index * 55}ms`}></span></td>
										<td><span class="skeleton medium"></span></td>
										<td><span class="skeleton medium"></span></td>
									</tr>
								{/each}
							{:else}
								{#each candidates as candidate (candidate.id)}
									<tr class:selected-row={selectedCandidate?.id === candidate.id}>
										<td class="select-cell"><button class="choose" class:chosen={selectedCandidate?.id === candidate.id} onclick={() => selectedCandidate = candidate} aria-label={`${selectedCandidate?.id === candidate.id ? 'Selected' : 'Select'} ${candidate.word || candidate.id}`} title={selectedCandidate?.id === candidate.id ? 'Selected etymon' : 'Select this etymon'}>{selectedCandidate?.id === candidate.id ? '✓' : '+'}</button></td>
										<td>
											<a class="candidate-word" href={`${base}/entries/${candidate.id}`} target="_blank">{candidate.word || candidate.id}</a>
											<div class="family">[{candidate.id}] · {candidate.reflex_count ?? 0} forms / {candidate.lang_count ?? 0} languages</div>
										</td>
										<td>{candidate.language}</td>
										<td class="candidate-gloss">{candidate.gloss || '—'}</td>
										<td>
											{#if candidate.confidence !== undefined}
												<div class="confidence-viz" title="45% concept match + 20% headword sound match + 35% cognate similarity">
													<div class="confidence-heading"><strong>{candidate.confidence}%</strong><span>{candidate.confidence >= 70 ? 'strong' : candidate.confidence >= 45 ? 'possible' : 'weak'}</span></div>
													<div class="confidence-track"><span style={`width:${candidate.confidence}%`}></span></div>
													<div class="evidence-pips">
														<span class="concept">C {candidate.concept_score}%</span><span class="sound">S {candidate.sound_score}%</span><span class="cognate">R {candidate.cognate_score}%</span>
													</div>
												</div>
											{:else}—{/if}
										</td>
										<td class="best-cognate">{candidate.best_cognate || '—'}</td>
										<td class="candidate-source">{candidate.sources || '—'}</td>
									</tr>
								{:else}
									<tr><td colspan="7" class="empty-table">No candidate etyma found.</td></tr>
								{/each}
							{/if}
						</tbody>
					</table>
				</div>

				<div class="decision">
					<label>Relationship<select bind:value={relation}><option value="reflex">Inherited/reflex</option><option value="borrowed">Borrowed</option></select></label>
					<label>Evidence notes<textarea bind:value={notes} rows="3" placeholder="Why this analysis is credible; citations or uncertainty"></textarea></label>
					<div class="actions">
						<button class="primary" disabled={!selectedCandidate || saving || !selected.id.startsWith('f_')} onclick={saveAndNext}>{saving ? 'Saving…' : 'Save and next'}</button>
						{#if assignments[selected.id]}<button onclick={removeAssignment}>Remove saved link</button>{/if}
						{#if message}<span class="message">{message}</span>{/if}
					</div>
					{#if !selected.id.startsWith('f_')}<p class="warning">This database predates persistent form IDs. Run <code>assign_form_ids.py</code>, rebuild the DB, and restart the dev server before saving.</p>{/if}
				</div>
			{:else}
				<p class="empty large">Select a form from the queue to begin.</p>
			{/if}
		</section>
	</div>
{/if}

<style>
	.workbench-head { display:flex; justify-content:space-between; gap:2rem; align-items:flex-end; margin-bottom:1.5rem; }
	.workbench-head h1 { margin:.15rem 0 .35rem; }
	.workbench-head p { margin:0; color:var(--muted); }
	.eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; }
	.counter { border:1px solid var(--border); border-radius:.7rem; padding:.7rem 1rem; display:flex; flex-direction:column; text-align:right; background:var(--surface); }
	.counter strong { font-size:1.35rem; }
	.counter span,.panel-title span { color:var(--muted); font-size:.78rem; }
	.filters { border:1px solid var(--border); background:var(--surface); padding:.8rem; border-radius:.7rem; margin-bottom:1rem; }
	.filters form { display:grid; grid-template-columns:minmax(15rem,2fr) 1fr 1fr auto; gap:.7rem; align-items:end; }
	label { display:flex; flex-direction:column; gap:.28rem; color:var(--muted); font-size:.78rem; font-weight:650; }
	input,select,textarea { width:100%; box-sizing:border-box; border:1px solid var(--border); border-radius:.42rem; padding:.55rem .65rem; background:var(--paper); color:var(--ink); font:inherit; }
	button { border:1px solid var(--border); background:var(--surface); color:var(--ink); border-radius:.42rem; padding:.58rem .75rem; cursor:pointer; }
	button:disabled { opacity:.5; cursor:not-allowed; }
	button.primary { background:var(--plum); border-color:var(--plum); color:white; font-weight:700; }
	.workspace { display:grid; grid-template-columns:minmax(17rem,28%) 1fr; border:1px solid var(--border); border-radius:.75rem; min-height:68vh; overflow:hidden; }
	.queue { border-right:1px solid var(--border); display:flex; flex-direction:column; min-height:0; background:var(--surface); }
	.panel-title,.pager { display:flex; align-items:center; justify-content:space-between; gap:.5rem; padding:.7rem .8rem; border-bottom:1px solid var(--border); }
	.panel-title h2 { font-size:.95rem; margin:0; }
	.rows { flex:1; overflow:auto; max-height:62vh; }
	.rows > button { width:100%; border:0; border-bottom:1px solid var(--border); border-radius:0; text-align:left; display:grid; grid-template-columns:1fr auto; gap:.16rem .55rem; padding:.7rem .8rem; }
	.rows > button:hover,.rows > button.active { background:color-mix(in srgb,var(--plum) 10%,var(--surface)); }
	.word,.candidate-word { font-family:var(--font-serif); font-size:1.08rem; font-weight:700; }
	.language,.family { color:var(--muted); font-size:.76rem; }
	.gloss { grid-column:1/-1; color:var(--muted); font-size:.83rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
	.saved { color:var(--plum-2); font-size:.72rem; }
	.pager { border-top:1px solid var(--border); border-bottom:0; justify-content:flex-end; }
	.editor { padding:1.15rem; min-width:0; }
	.selected-form { display:flex; justify-content:space-between; gap:1rem; align-items:start; }
	.selected-form h2 { font-family:var(--font-serif); font-size:2rem; margin:.1rem 0; }
	.selected-form a { font-size:.8rem; }
	dl { display:grid; gap:.35rem; margin:1rem 0; }
	dl div { display:grid; grid-template-columns:6rem 1fr; gap:.6rem; }
	dt { color:var(--muted); font-size:.78rem; } dd { margin:0; font-size:.88rem; }
	.candidate-search { display:grid; grid-template-columns:1fr auto; align-items:end; gap:.6rem; margin-top:1.2rem; }
	.candidate-table-wrap { max-height:34vh; overflow:auto; margin-top:.55rem; }
	.candidate-table { min-width:68rem; font-size:.82rem; }
	.candidate-table th { padding:.5rem .6rem; }
	.candidate-table td { vertical-align:middle; }
	.candidate-table tr.selected-row td { background:color-mix(in srgb,var(--plum) 12%,var(--surface)); }
	.candidate-word { white-space:nowrap; }
	.candidate-gloss { max-width:18rem; }
	.candidate-source,.best-cognate { color:var(--muted); font-size:.75rem; max-width:13rem; }
	.select-cell { width:2.2rem; padding-right:.15rem !important; }
	.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
	.choose { width:1.75rem; height:1.75rem; display:grid; place-items:center; padding:0; border-radius:50%; font-size:1rem; line-height:1; font-weight:700; }
	.choose.chosen { color:white; background:var(--plum); border-color:var(--plum); }
	.confidence-viz { width:10.5rem; }
	.confidence-heading { display:flex; justify-content:space-between; align-items:baseline; font-variant-numeric:tabular-nums; }
	.confidence-heading strong { color:var(--plum-2); font-size:.9rem; }
	.confidence-heading span { color:var(--muted); font-size:.68rem; text-transform:uppercase; letter-spacing:.06em; }
	.confidence-track { height:.42rem; margin:.22rem 0 .3rem; overflow:hidden; background:var(--surface-2); border:1px solid var(--border); border-radius:999px; }
	.confidence-track span { display:block; height:100%; border-radius:inherit; background:linear-gradient(90deg,#b96b75,var(--plum-2)); }
	.evidence-pips { display:flex; gap:.28rem; font-size:.64rem; font-variant-numeric:tabular-nums; }
	.evidence-pips span { padding:.08rem .25rem; border-radius:999px; white-space:nowrap; }
	.evidence-pips .concept { color:#775913; background:#d8a72a24; }
	.evidence-pips .sound { color:#316078; background:#4d9bc124; }
	.evidence-pips .cognate { color:#68508a; background:#8e6ab924; }
	.candidate-error { color:var(--bad); font-size:.8rem; margin:.55rem 0 0; }
	.empty-table { padding:1.25rem !important; text-align:center; color:var(--muted); }
	.skeleton { display:block; height:.72rem; border-radius:.25rem; background:linear-gradient(90deg,var(--surface-2) 20%,color-mix(in srgb,var(--plum) 10%,var(--surface)) 50%,var(--surface-2) 80%); background-size:220% 100%; animation:shimmer 1.15s ease-in-out infinite; }
	.skeleton.wide { width:8rem; }.skeleton.medium { width:5.5rem; }.skeleton.meter { width:9rem; height:1.25rem; }.skeleton.select-skeleton { width:1.75rem; height:1.75rem; border-radius:50%; }
	@keyframes shimmer { from { background-position:200% 0; } to { background-position:-20% 0; } }
	@media (prefers-reduced-motion:reduce) { .skeleton { animation:none; } }
	.decision { border-top:1px solid var(--border); margin-top:.5rem; padding-top:1rem; display:grid; gap:.75rem; }
	.actions { display:flex; align-items:center; gap:.6rem; flex-wrap:wrap; }
	.message { font-size:.8rem; color:var(--muted); }
	.warning,.error { border:1px solid #b87922; background:#b8792215; border-radius:.6rem; padding:.75rem; }
	.error p { margin:.4rem 0 0; }
	.empty { color:var(--muted); padding:1rem; } .empty.large { text-align:center; margin-top:20vh; }
	@media (max-width:850px) { .filters form { grid-template-columns:1fr 1fr; } .workspace { grid-template-columns:1fr; } .queue { border-right:0; border-bottom:1px solid var(--border); } .rows { max-height:35vh; } }
	.review-list {
		list-style: none;
		margin: 0.5rem 0 0;
		padding: 0;
		display: grid;
		gap: 0.3rem;
		font-size: 0.9rem;
	}
	.review-list button {
		margin-left: 0.35rem;
		padding: 0.05rem 0.5rem;
	}
</style>
