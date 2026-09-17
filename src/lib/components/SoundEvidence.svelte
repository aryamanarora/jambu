<script lang="ts">
	import Pager from './Pager.svelte';
	import { base } from '$app/paths';
	import { safe } from '$lib/render';
	import { alignmentEvents } from '$lib/phonology';
	import { changeInfo } from '$lib/soundChange';
	import { categoryLabel, type StudyObservation } from '$lib/soundStudy';
	import FormWord from './FormWord.svelte';
	let { rows }: { rows: StudyObservation[] } = $props();
	let page = $state(0);
	const size = 30;
	$effect(() => { rows; page = 0; });
	const forms = $derived.by(() => {
		const grouped = new Map<string,StudyObservation[]>();
		for (const o of rows) { if (!grouped.has(o.form.id)) grouped.set(o.form.id,[]); grouped.get(o.form.id)!.push(o); }
		return [...grouped.values()];
	});
	function download() {
		const values = [['form_id','ancestor_id','family_id','language','ancestor','descendant','start','end','context_start','context_end','input_group','aligned_outcome','outcome_group','ancestor_accent','ancestor_syllables','descendant_accent','descendant_syllables','reading_flags','sources'],
			...rows.map(o=>[o.form.id,o.form.parentId,o.form.familyId,o.form.language,o.form.parentWord,o.form.word,o.pos+1,(o.endPos ?? o.pos)+1,(o.contextStart??o.pos)+1,(o.contextEnd??o.endPos??o.pos)+1,o.input,o.alignedOutcome,o.outcome,o.form.ancestor.accentClass,o.form.ancestor.count ?? '',o.form.modern.accentType,o.form.modern.count ?? '',[...new Set([...o.form.ancestor.issues,...o.form.modern.issues])].join(';'),o.form.sources.map(s=>`${s.id}[${s.locator}]`).join(';')])];
		const csv = values.map(row=>row.map(v=>'"'+String(v).replace(/^[=+@\-\t\r]/,c=>"'"+c).replace(/"/g,'""')+'"').join(',')).join('\n');
		const url = URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
		const a = document.createElement('a'); a.href=url; a.download='jambu-sound-evidence.csv'; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
	}
</script>

<div class="toolbar"><p>{forms.length.toLocaleString()} forms · {rows.length.toLocaleString()} matched sequences</p><button onclick={download}>Download CSV</button></div>
{#each forms.slice(page*size,(page+1)*size) as observations (observations[0].form.id)}
	{@const form = observations[0].form}
	{@const positions = new Set(form.columns.filter(c=>observations.some(o=>c.pos>=o.pos&&c.pos<=(o.endPos??o.pos))).map(c=>c.pos))}
	{@const context = new Set(form.columns.filter(c=>observations.some(o=>c.pos>=(o.contextStart??o.pos)&&c.pos<=(o.contextEnd??o.endPos??o.pos))).map(c=>c.pos))}
	<details class="form">
		<summary><span class="language">{form.languageName}</span><span class="words">{form.parentWord} → <FormWord word={form.word} ocr={form.ocr} /></span><span class="gloss">{@html safe(form.gloss)}</span></summary>
		<div class="body">
			<div class="links"><a href="{base}/entries/{form.parentId}">Ancestor ↗</a><a href="{base}/entries/{form.id}">Descendant ↗</a><span>{form.relation}</span></div>
			<div class="alignment"><table><tbody>
				<tr><th>Ancestor</th>{#each form.columns as c}<td class:selected={positions.has(c.pos)} class:context={context.has(c.pos)}>{c.etymonSeg || '∅'}</td>{/each}</tr>
				<tr><th>Descendant</th>{#each form.columns as c}<td class:selected={positions.has(c.pos)} class:context={context.has(c.pos)}>{c.reflexSeg || '∅'}</td>{/each}</tr>
			</tbody></table></div>
			<p>Ancestor: {form.ancestor.count ?? '?'} syllables · {categoryLabel(form.ancestor.accentClass)}.<br>Descendant: {form.modern.count ?? '?'} syllables · {form.modern.accentType} · {form.modern.notation}.</p>
			{#if context.size>positions.size}<p class="muted">Purple cells are the aligned target; shaded cells show its matching context.</p>{/if}
			<p>Matched outcome: {observations.map(o=>`${o.alignedOutcome} (${categoryLabel(o.outcome)})`).join('; ')}</p>
			{#each alignmentEvents(form.columns) as event}<p class="event">{event.from || '∅'} → {event.to || '∅'} · {event.labels.map(c=>changeInfo(c).name).join(', ')}</p>{/each}
			{#if form.ancestor.issues.length || form.modern.issues.length}<p class="muted">Reading flags: {[...new Set([...form.ancestor.issues,...form.modern.issues])].join(', ')}</p>{/if}
			<div class="links">{#each form.sources as s}<a href="{base}/references/{s.id}">{s.label}{s.locator ? ` · ${s.locator}` : ''}</a>{/each}</div>
		</div>
	</details>
{/each}
<Pager count={forms.length} page={page + 1} pageSize={size} label="Evidence pages" onpage={(next) => page = next - 1} />

<style>
	.toolbar,.links { display:flex; flex-wrap:wrap; gap:.7rem; align-items:center; justify-content:space-between; font-size:.78rem; }
	button { font:inherit; cursor:pointer; padding:.4rem .7rem; border:1px solid var(--border); border-radius:.3rem; background:var(--surface); color:var(--ink); }
	.form { border-top:1px solid var(--border); padding:.8rem 0; } summary { display:grid; gap:.3rem; cursor:pointer; } .language { color:var(--plum-2); font-size:.72rem; } .words { font-family:var(--font-phon); font-size:1.25rem; overflow-wrap:anywhere; } .gloss,.body { font-size:.8rem; line-height:1.55; } .gloss,.muted { color:var(--muted); }
	.body { padding-top:.8rem; } .links { justify-content:flex-start; } .alignment { overflow:auto; padding:1rem 0; } table { border-collapse:collapse; } th { text-align:left; font-weight:400; padding-right:.6rem; font-size:.7rem; } td { border:1px solid var(--border); padding:.3rem; min-width:1.6rem; text-align:center; font-family:var(--font-phon); } td.context { background:var(--surface-2); } td.selected { background:color-mix(in srgb,var(--plum-2) 13%,transparent); } .event { margin:.3rem 0; } 
</style>
