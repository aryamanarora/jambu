<script lang="ts">
	import Pager from './Pager.svelte';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { base } from '$app/paths';
	import { browser } from '$app/environment';
	import { getProtoFamilies, getSoundLanguages, getSoundObservations, type ProtoFamily } from '$lib/query';
	import { DEFAULT_STUDY, CONDITIONS, INPUT_FACET_GROUPS, inputFacetLabel, OUTCOME_GROUPS, readStudy, studySearch, queryKey, loadKey, queryFilters, selectedLanguages, conditionLabel, categoryLabel, groupStudy, inputColumns, buildMatrix, languageOutcomeCounts, matchesLanguageCounts, languageCountError, type StudyState } from '$lib/soundStudy';
	import { summarizeSounds, type SoundObservation, type SoundFilters, type SoundSummary } from '$lib/soundExplorer';
	import { parseSoundPattern } from '$lib/soundPattern';
	import { pieMarker } from '$lib/atlas';
	import type { Language, MapMarker } from '$lib/types';
	import GeoMap from './Map.svelte';
	import SoundEvidence from './SoundEvidence.svelte';
	import SoundPatternEditor from './SoundPatternEditor.svelte';
	import AncestorEntrySearch from './AncestorEntrySearch.svelte';
	import SoundLanguagePicker from './SoundLanguagePicker.svelte';
	import { paramsFromUrl } from '$lib/urlParams';

	const f = $derived(readStudy(browser ? page.url.searchParams : new URLSearchParams()));
	const inputKey = $derived(queryKey(f)), dataKey = $derived(loadKey(f));
	let draft = $state<StudyState>({...DEFAULT_STUDY});
	let mounted = $state(false), loading = $state(true), error = $state(''), copied = $state(false);
	let all = $state.raw<SoundObservation[]>([]), families = $state<ProtoFamily[]>([]);
	let languages = $state.raw<Language[]>([]), pickerLanguages = $state.raw<Language[]>([]);
	let property = $state(''), value = $state('');
	let rowPage = $state(0), colPage = $state(0), showLegend = $state(false);
	let dialog: HTMLDialogElement;
	let request = 0, pickerRequest = 0;
	const ROWS=25, COLS=6;
	const units = {forms:'forms',occurrences:'matched sequences',families:'families within languages'};
	const parsed = $derived(parseSoundPattern(draft.s,['Indo-Aryan','OIA','PIA'].includes(draft.p)));
	const dirty = $derived(queryKey(draft)!==inputKey);
	const selected = $derived(selectedLanguages(draft));
	const condition = $derived(CONDITIONS.find(c=>c.key===property));
	$effect(()=>{draft={...DEFAULT_STUDY,...JSON.parse(inputKey)};rowPage=0;colPage=0;});
	onMount(()=>{mounted=true;getProtoFamilies().then(fs=>families=fs).catch(e=>error=String(e));});
	$effect(()=>{
		const state:StudyState={...DEFAULT_STUDY,...JSON.parse(dataKey)};
		if(!mounted)return;
		const n=++request;loading=true;error='';all=[];
		Promise.all([getSoundLanguages(state.p),getSoundObservations(state.p,state.s,{filters:queryFilters(state),entrySearch:state.entry?paramsFromUrl(new URLSearchParams(state.entry)):undefined})]).then(([ls,rows])=>{if(n===request){languages=ls;all=rows;loading=false;}}).catch(e=>{if(n===request){error=String(e);loading=false;}});
	});
	$effect(()=>{const p=draft.p;if(!mounted)return;const n=++pickerRequest;getSoundLanguages(p).then(ls=>{if(n===pickerRequest)pickerLanguages=ls;});});
	$effect(()=>{if(!mounted||!dialog)return;if(f.detail&&!dialog.open)dialog.showModal();else if(!f.detail&&dialog.open)dialog.close();});
	function href(patch:Partial<StudyState>={}){const s=studySearch({...f,...patch});return `${base}/correspondences${s?'?'+s:''}`;}
	async function set(patch:Partial<StudyState>){await goto(href(patch),{noScroll:true,keepFocus:true});}
	async function apply(){if(!parsed.error&&!languageCountError(draft))await set({...draft,s:draft.s.trim()||'*',view:f.view,unit:f.unit,detail:'',cellInput:'',mapGroup:'',r:'',text:''});}
	function addProperty(){if(property&&value){draft={...draft,[property]:value};property='';value='';}}
	function toggleLanguage(id:string,on:boolean){const ids=new Set(selected);if(on)ids.add(id);else ids.delete(id);draft.langs=[...ids].sort().join('|');}

	const name=(id:string)=>languages.find(l=>l.id===id)?.name??pickerLanguages.find(l=>l.id===id)?.name??id;
	const inputLabel=(group:string)=>group==='all'?(f.s==='*'||!f.s?'Whole form':f.s):categoryLabel(group);
	const outcomeCounts=$derived(languageOutcomeCounts(all));
	const eligibleLanguages=$derived(languages.filter(l=>matchesLanguageCounts(l,outcomeCounts.get(l.id)??0,f)&&(!selectedLanguages(f).length||selectedLanguages(f).includes(l.id))));
	const eligibleIds=$derived(new Set(eligibleLanguages.map(l=>l.id)));
	const grouped=$derived(groupStudy(all.filter(o=>eligibleIds.has(o.form.language)),f));
	const columns=$derived(inputColumns(grouped));
	const visibleColumns=$derived(columns.slice(colPage*COLS,(colPage+1)*COLS));
	const matrix=$derived(buildMatrix(grouped,f.unit));
	const rowLanguages=$derived(eligibleLanguages.filter(l=>selectedLanguages(f).length||matrix.has(l.id)));
	const summary=$derived(summarizeSounds(grouped,f.unit));
	const mapColumn=$derived(columns.includes(f.mapGroup)?f.mapGroup:columns[0]??'all');
	const colors=$derived(new Map(summary.outcomes.map((o,i)=>[o.sound,['unknown','unmarked','?','∅'].includes(o.sound)?'#97908a':`hsl(${(i*137.508+320)%360} 43% 48%)`])));
	const color=(s:string)=>colors.get(s)??'#97908a';
	const pie=(s:SoundSummary,outline=true)=>pieMarker(s.outcomes.map(o=>({color:color(o.sound),n:o.weight})),64,outline);
	const cellLabel=(lang:string,group:string,cell:SoundSummary)=>`${name(lang)}, ${inputLabel(group)}: ${cell.total} ${units[f.unit]}. ${cell.outcomes.slice(0,3).map(o=>`${categoryLabel(o.sound)} ${o.percent.toFixed(0)}%`).join(', ')}. Open evidence`;
	function escape(s:string){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));}
	const markers=$derived.by(():MapMarker[]=>rowLanguages.flatMap(l=>{
		const cell=matrix.get(l.id)?.get(mapColumn);if(!cell||l.lat==null||l.long==null)return [];
		return [{lat:l.lat,long:l.long,svg:pie(cell),size:32,label:cellLabel(l.id,mapColumn,cell),tooltip:`<strong>${escape(l.name)}</strong><br>${cell.total} ${units[f.unit]}`,popupHtml:`<strong>${escape(l.name)} · ${escape(inputLabel(mapColumn))}</strong><br>${cell.outcomes.slice(0,5).map(o=>`${escape(categoryLabel(o.sound))}: ${o.percent.toFixed(1)}%`).join('<br>')}<br><a href="${escape(href({detail:l.id,cellInput:mapColumn,r:''}))}">Inspect evidence</a>`}];
	}));
	const evidenceRows=$derived(grouped.filter(o=>(f.detail==='*'||o.form.language===f.detail)&&(!f.cellInput||o.input===f.cellInput)));
	const evidenceSummary=$derived(summarizeSounds(evidenceRows,f.unit));
	const evidenceFiltered=$derived(evidenceRows.filter(o=>(!f.r||o.outcome===f.r)&&(!f.text||[o.form.word,o.form.parentWord,o.form.gloss,o.form.id].some(s=>s.toLowerCase().includes(f.text.toLowerCase())))));
	const closeEvidence=()=>set({detail:'',cellInput:'',r:'',text:''});
	async function copyLink(){try{await navigator.clipboard.writeText(page.url.href);copied=true;setTimeout(()=>copied=false,1800);}catch{copied=false;}}
</script>

<svelte:head><title>Sound correspondences — Jambu</title><meta name="description" content="Compare ancestor patterns and descendant outcomes across languages, in a table or on a map." /></svelte:head>

<div class="study">
	<header><div><h1>Sound correspondences</h1><p>Choose the input, the languages, and what to compare.</p></div><button class="quiet" onclick={copyLink}>{copied?'Copied':'Copy link'}</button></header>
	<div class="query">
		<div class="query-parts">
			<section aria-labelledby="ancestor-heading">
				<div class="ancestor-heading"><h2 id="ancestor-heading"><span>1</span> Ancestor input</h2><select aria-label="Ancestor language" bind:value={draft.p} onchange={()=>draft.langs=''}>{#if !families.length}<option value={draft.p}>{draft.p}</option>{/if}{#each families as family}<option value={family.id}>{family.name}</option>{/each}</select></div>
				<AncestorEntrySearch value={draft.entry} onChange={entry=>draft.entry=entry} onSubmit={apply} language={draft.p} />
				<SoundPatternEditor value={draft.s} old={['Indo-Aryan','OIA','PIA'].includes(draft.p)} onChange={value=>draft.s=value} onSubmit={apply} />
				<div class="examples"><span>Try</span><button type="button" onclick={()=>{draft.s='[retroflex]';draft.facet='sound';}}>retroflexes</button><button type="button" onclick={()=>draft.s='V (k) V'}>k between vowels</button><button type="button" onclick={()=>draft.s='*'}>whole form</button></div>
				<div class="chips">{#each Object.entries(queryFilters(draft)) as [key,val]}<button type="button" onclick={()=>draft={...draft,[key]:''}} aria-label="Remove {conditionLabel(key,String(val))}">{conditionLabel(key,String(val))} ×</button>{/each}</div>
				<div class="add-property"><select aria-label="Add ancestor property" bind:value={property} onchange={()=>value=''}><option value="">+ form property</option>{#each CONDITIONS as c}<option value={c.key}>{c.label}</option>{/each}</select>{#if condition}<select aria-label={condition.label} bind:value><option value="">Choose…</option>{#each condition.values as [id,label]}<option value={id}>{label}</option>{/each}</select><button type="button" disabled={!value} onclick={addProperty}>Add</button>{/if}</div>
				<div class="facet">
					<label><span>Group ancestor inputs by <small>Table columns</small></span>
						<select bind:value={draft.facet} aria-describedby="facet-help">
							<option value="none">Keep all inputs together</option>
							{#each INPUT_FACET_GROUPS as group}
								<optgroup label={group.label}>{#each group.options as [id,label]}<option value={id}>{label}</option>{/each}</optgroup>
							{/each}
						</select>
					</label>
					<p id="facet-help">{draft.facet==='none'?'One column for all matching ancestor inputs.':'One column for each ancestor group.'} The map uses these same groups.{#if draft.facet==='weightPattern'} H = heavy; L = light.{:else if draft.facet==='quantityPattern'} S = short; L = long.{/if}</p>
				</div>
			</section>
			<section aria-labelledby="languages-heading">
				<h2 id="languages-heading"><span>2</span> Descendant languages</h2>
				<SoundLanguagePicker languages={pickerLanguages} counts={!loading&&!error&&loadKey(draft)===dataKey?outcomeCounts:undefined} values={selected} filters={draft} onChange={ids=>draft.langs=ids.sort().join('|')} onCounts={patch=>draft={...draft,...patch}} />
				{#if selected.length}<div class="chips">{#each selected.slice(0,5) as id}<button type="button" aria-label="Remove {name(id)}" onclick={()=>toggleLanguage(id,false)}>{name(id)} ×</button>{/each}{#if selected.length>5}<span>+{selected.length-5} more</span>{/if}</div>{:else}<p class="hint">Keep the full distribution, or choose several languages or a branch.</p>{/if}
			</section>
			<section aria-labelledby="outcome-heading">
				<h2 id="outcome-heading"><span>3</span> Descendant outcomes</h2>
				<label>Group outcomes by<select bind:value={draft.groupBy}>{#each OUTCOME_GROUPS as [id,label]}<option value={id}>{label}</option>{/each}</select></label>
				<p class="hint">{draft.groupBy==='segments'?'Each slice is the descendant sequence aligned to the highlighted target.':draft.groupBy==='tone'?'Each slice is a recorded tone or accent type. Known mora classes stay specific to their source convention.':'Each slice is a class of the descendant '+(['place','manner'].includes(draft.groupBy)?'aligned sequence.':'form.')}</p>
			</section>
		</div>
		<div class="query-footer"><span>{languageCountError(draft)||(dirty?'Changes ready to apply.':'The same comparison works in either display.')}</span><button class="primary" disabled={!!parsed.error||!!languageCountError(draft)} onclick={apply}>{dirty?'Update comparison':'Run comparison'} →</button></div>
	</div>

	<section class="results" aria-label="Comparison results" aria-busy={loading}>
		<div class="display-bar"><div class="display-toggle" role="group" aria-label="Display"><button aria-pressed={f.view==='table'} onclick={()=>set({view:'table'})}>Table</button><button aria-pressed={f.view==='map'} onclick={()=>set({view:'map'})}>Map</button></div>
			{#if f.view==='map'&&columns.length>1}<label class="map-group">Input group<select value={mapColumn} onchange={e=>set({mapGroup:e.currentTarget.value})}>{#each columns as group}<option value={group}>{inputLabel(group)}</option>{/each}</select></label>{/if}
			<span class="result-count">{loading?'Reading aligned forms…':`${summary.forms.toLocaleString()} forms · ${rowLanguages.length} languages · ${columns.length} input group${columns.length===1?'':'s'}`}</span><button class="quiet" disabled={loading||!grouped.length} onclick={()=>set({detail:'*',cellInput:'',r:''})}>All evidence ↗</button>
		</div>
		{#if error}<div class="empty" role="alert"><h3>Could not read this comparison</h3><p>{error}</p><button onclick={()=>location.reload()}>Retry</button></div>
		{:else if loading}<div class="empty" role="status">Reading “{f.s||'whole form'}” and its descendant outcomes…</div>
		{:else if !grouped.length}<div class="empty"><h3>No matching forms</h3><p>Try a shorter sequence, remove a property, or broaden the languages and form-count limits.</p></div>
		{:else}
			<p class="column-key">Ancestor groups · {inputFacetLabel(f.facet)}</p>
			<div class="legend" aria-label="Outcome classes"><span class="muted">Slices · {OUTCOME_GROUPS.find(([key])=>key===f.groupBy)?.[1]}</span>{#each (showLegend?summary.outcomes:summary.outcomes.slice(0,8)) as o}<span><i style:background={color(o.sound)}></i>{categoryLabel(o.sound)}</span>{/each}{#if summary.outcomes.length>8}<button class="quiet" onclick={()=>showLegend=!showLegend}>{showLegend?'Fewer':`+${summary.outcomes.length-8} classes`}</button>{/if}</div>
			{#if f.view==='table'}
				<Pager count={columns.length} page={colPage + 1} pageSize={COLS} label="Input group pages" onpage={(next) => colPage = next - 1} />
				<!-- Keyboard users can scroll the table without changing their query. -->
				<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
				<div class="matrix-scroll" tabindex="0" role="region" aria-label="Language by ancestor input table"><table class="matrix">
					<caption>Languages × ancestor input. Pies show descendant outcomes; numbers count {units[f.unit]}. Click a cell for evidence.</caption><thead><tr><th scope="col">Language</th>{#each visibleColumns as group}<th scope="col">{inputLabel(group)}</th>{/each}</tr></thead><tbody>
					{#each rowLanguages.slice(rowPage*ROWS,(rowPage+1)*ROWS) as language}<tr><th scope="row">{language.name}<small>{language.clade}</small></th>{#each visibleColumns as group}{@const cell=matrix.get(language.id)?.get(group)}<td>{#if cell}<button class="pie-cell" aria-label={cellLabel(language.id,group,cell)} onclick={()=>set({detail:language.id,cellInput:group,r:'',text:''})}><span class="pie" aria-hidden="true">{@html pie(cell,false)}</span><span>{cell.total.toLocaleString()}</span></button>{:else}<span class="muted" title="No matched forms">—</span>{/if}</td>{/each}</tr>{/each}
					</tbody></table></div>
				<Pager count={rowLanguages.length} page={rowPage + 1} pageSize={ROWS} label="Language pages" onpage={(next) => rowPage = next - 1} />
			{:else}<GeoMap {markers} zoom={4} height="540px" scrollZoom /><p class="map-note">{markers.length} languages mapped for {inputLabel(mapColumn)}. Click a pie for its distribution and evidence. Languages without coordinates remain in the table.</p>{/if}
		{/if}
	</section>
	<details class="method"><summary>Reading this comparison & counting options</summary><div>
		<label>Count<select value={f.unit} onchange={e=>set({unit:e.currentTarget.value as SoundFilters['unit']})}><option value="forms">Distinct forms</option><option value="occurrences">Matched sequences</option><option value="families">Families within languages</option></select></label>
		<p>Table columns and the map selector show the same input groups; colors refer to descendant outcomes. Each cell has its own denominator. Forms or families with several outcomes split their vote equally among those outcomes.</p>
		<p>Use <code>kt</code> or <code>k t</code> for literal sequences, <code>V C V</code> for classes, and <code>[retroflex+stop]</code> for combined properties. <code>#</code> anchors a word edge. Parentheses select the aligned target: <code>V (k) V</code> counts the reflex of k between vowels. Sound facets and matched-syllable properties refer to that target; surrounding sounds only constrain the match. <code>*</code> selects the whole form, including for comparisons based only on accent or syllable count. Insertions inside a matched sequence belong to its outcome; those outside its edges do not. Overlapping matches are separate occurrences.</p>
		<p>Barytone and oxytone describe marked citation forms. Unmarked accent remains unknown. OIA ai/au and syllabic liquids count as nuclei; quantity and conventional V.CV / VC.CV weight remain separate. Ambiguous readings retain their flags. Matched-syllable properties refer to the sequence’s start.</p>
		<p>Tone / accent type preserves source conventions: known Palula and Gilgit Shina mora readings are separated from uninterpreted marks. Unmarked data is not a toneless class. Alignments remain descriptive; <code>?</code> flags notation needing review. <a href="https://dsal.uchicago.edu/dictionaries/soas/frontmatter/introduction.html">Turner’s notation</a> · <a href="https://langsci-press.org/catalog/view/82/85/399-1">Palula grammar</a>.</p>
	</div></details>
</div>

<dialog bind:this={dialog} oncancel={e=>{e.preventDefault();void closeEvidence();}} aria-labelledby="evidence-heading">
	<div class="dialog-head"><div><p>Lexical evidence</p><h2 id="evidence-heading">{f.detail==='*'?'All selected languages':name(f.detail)}{f.cellInput?` · ${inputLabel(f.cellInput)}`:''}</h2></div><button aria-label="Close evidence" onclick={closeEvidence}>×</button></div>
	{#if loading}<p>Reading evidence…</p>{:else}
		<div class="outcome-detail">{#each evidenceSummary.outcomes as o}<button class:chosen={f.r===o.sound} onclick={()=>set({r:f.r===o.sound?'':o.sound})}><span><i style:background={color(o.sound)}></i>{categoryLabel(o.sound)}</span><strong>{o.percent.toFixed(1)}%</strong><small>{o.support} supporting {units[f.unit]}</small></button>{/each}</div>
		{#if f.r}<p class="selected-outcome">Showing {categoryLabel(f.r)} <button onclick={()=>set({r:''})}>Show all outcomes</button></p>{/if}
		<label class="word-search">Find a word, gloss, or ID<input type="search" value={f.text} onchange={e=>set({text:e.currentTarget.value})} /></label><SoundEvidence rows={evidenceFiltered} />
	{/if}
</dialog>

<style>
	.study{width:100%;min-width:0;padding:.2rem 0 2rem}header{display:flex;justify-content:space-between;align-items:start;gap:1rem;margin-bottom:1.3rem}h1{font-size:1.8rem;margin:0 0 .4rem}header p{color:var(--muted);margin:0;font-size:.9rem}
	button,input,select{font:inherit;font-size:.82rem;color:var(--ink)}button{cursor:pointer;border:1px solid var(--border);border-radius:.35rem;background:var(--surface);padding:.45rem .7rem}button:disabled{opacity:.45;cursor:default}button:hover:not(:disabled){color:var(--plum-2);border-color:var(--plum-2)}input,select{border:1px solid var(--border);background:var(--surface);padding:.5rem .6rem;border-radius:.3rem;max-width:100%;min-width:0;width:100%}label{display:grid;gap:.4rem;min-width:0;font-size:.76rem;color:var(--muted)}button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible,.matrix-scroll:focus-visible{outline:2px solid var(--plum-2);outline-offset:3px}.quiet{border-color:transparent;background:transparent;color:var(--muted);font-size:.76rem}
	.query{border:1px solid var(--border);border-radius:.6rem;background:var(--surface)}.query-parts{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)}.query-parts>section:first-child{grid-row:span 2}.query-parts>section:last-child{border-top:1px solid var(--border)}.ancestor-heading{display:flex;align-items:center;justify-content:space-between;gap:.8rem}.ancestor-heading h2{margin:0;white-space:nowrap}.ancestor-heading select{width:auto;max-width:48%;font-size:.75rem}.query-parts>section{min-width:0;padding:1.2rem}.query-parts>section+section{border-left:1px solid var(--border)}h2{margin:0 0 1rem;font-size:.98rem;font-weight:600;display:flex;align-items:center;gap:.5rem}h2>span{display:grid;place-items:center;font-size:.65rem;border:1px solid var(--border);border-radius:50%;width:1.4rem;height:1.4rem;color:var(--muted)}
	.examples{display:flex;flex-wrap:wrap;align-items:center;gap:.25rem .5rem;color:var(--muted);margin:.5rem 0 .75rem;font-size:.7rem}.examples button{padding:0;border:0;text-decoration:underline;background:none;font-size:.7rem;color:var(--muted)}.add-property{display:flex;gap:.4rem;margin:.6rem 0}.add-property select{font-size:.72rem}.facet{border-top:1px solid var(--border);padding-top:.85rem;margin-top:.85rem}.facet label>span{display:flex;align-items:center;justify-content:space-between;gap:.5rem;color:var(--ink);font-weight:600}.facet small{color:var(--plum-2);font-size:.65rem;font-weight:400;white-space:nowrap}.facet p{font-size:.7rem;line-height:1.5;color:var(--muted);margin:.45rem 0 0}.column-key{color:var(--muted);font-size:.73rem;margin:.35rem 0 0}.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0}.chips:empty{display:none}.chips button{font-size:.7rem;padding:.3rem .5rem;border-radius:1rem}.chips>span{color:var(--muted);font-size:.7rem;align-self:center}
	.hint{color:var(--muted);font-size:.78rem;line-height:1.6;margin:.8rem 0 0}.query-footer{display:flex;justify-content:space-between;align-items:center;gap:1rem;border-top:1px solid var(--border);padding:.8rem 1.2rem;color:var(--muted);font-size:.74rem}button.primary{background:var(--plum-2);border-color:var(--plum-2);color:var(--surface);padding:.6rem .9rem;white-space:nowrap}.primary:hover{color:var(--surface)!important;opacity:.9}
	.display-bar{display:flex;align-items:center;flex-wrap:wrap;gap:.7rem;padding:1.4rem 0 .7rem}.display-toggle{display:flex}.display-toggle button{border-radius:0;padding:.45rem 1rem}.display-toggle button:first-child{border-radius:.35rem 0 0 .35rem}.display-toggle button:last-child{border-radius:0 .35rem .35rem 0;margin-left:-1px}.display-toggle button[aria-pressed=true]{background:var(--ink);color:var(--surface);border-color:var(--ink)}.result-count{flex:1;font-size:.75rem;color:var(--muted)}.map-group{display:flex;align-items:center;gap:.5rem}.map-group select{width:auto;max-width:14rem}.legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;align-items:center;padding:.8rem 0 1rem;font-size:.73rem}.legend>span{display:flex;align-items:center;gap:.35rem}i{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;flex-shrink:0}.muted{color:var(--muted)}
	.matrix-scroll{overflow:auto;max-height:640px;border:1px solid var(--border);border-radius:.4rem}.matrix{width:100%;border-collapse:separate;border-spacing:0;font-size:.85rem}caption{text-align:left;padding:.75rem;font-size:.73rem;line-height:1.5;color:var(--muted);caption-side:bottom}.matrix th,.matrix td{padding:.5rem .8rem;text-align:center;border-bottom:1px solid var(--border);border-right:1px solid var(--border)}.matrix thead th{position:sticky;top:0;z-index:3;background:var(--surface);font-weight:500;min-width:95px}.matrix tr>th:first-child{position:sticky;left:0;text-align:left;min-width:150px;background:var(--surface);z-index:2}.matrix thead tr>th:first-child{z-index:4}.matrix tbody th{font-weight:500}.matrix th small{display:block;color:var(--muted);font-weight:400;margin-top:.25rem;font-size:.65rem}.matrix td:last-child,.matrix th:last-child{border-right:0}.matrix tr:last-child td,.matrix tr:last-child th{border-bottom:0}.pie-cell{border:0;display:flex;align-items:center;justify-content:center;gap:.6rem;width:100%;padding:.1rem .3rem;font-size:.75rem;background:transparent}.pie-cell:hover{background:color-mix(in srgb,var(--plum-2) 8%,transparent)}.pie{display:block;width:48px;height:48px;flex-shrink:0}.pie :global(svg){width:100%;height:100%}.map-note,.empty{font-size:.84rem;line-height:1.6;color:var(--muted)}.empty{padding:3rem 1rem}
	.method{border-top:1px solid var(--border);margin-top:1.4rem;padding:1rem 0;max-width:58rem;font-size:.78rem;color:var(--muted)}.method summary{cursor:pointer}.method>div{line-height:1.7;padding-top:1rem}.method label{max-width:15rem}
	dialog{position:fixed;inset:0 0 0 auto;margin:0;height:100dvh;max-height:100dvh;width:min(640px,100vw);max-width:100vw;padding:1.3rem;border:0;border-left:1px solid var(--border);background:var(--surface);color:var(--ink);box-sizing:border-box}dialog::backdrop{background:#21132255}.dialog-head{display:flex;align-items:start;justify-content:space-between;gap:1rem}.dialog-head p{margin:0 0 .5rem;color:var(--muted);font-size:.72rem}.dialog-head h2{display:block;font-size:1.3rem}.dialog-head>button{font-size:1.3rem;padding:.1rem .6rem}.outcome-detail{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.5rem;margin:.7rem 0 1rem;max-height:260px;overflow:auto}.outcome-detail button{display:grid;grid-template-columns:1fr auto;gap:.4rem;text-align:left}.outcome-detail button>span{display:flex;align-items:center;gap:.4rem;overflow-wrap:anywhere;min-width:0}.outcome-detail small{grid-column:1/-1;color:var(--muted);font-size:.66rem}.outcome-detail .chosen{border-color:var(--plum-2);background:color-mix(in srgb,var(--plum-2) 8%,transparent)}.selected-outcome{font-size:.8rem}.word-search{border-top:1px solid var(--border);padding-top:.8rem}
	@media(max-width:600px){h1{font-size:1.5rem}header p{font-size:.8rem}.query-parts{display:block}.query-parts>section{padding:1rem}.query-parts>section+section{border-left:0;border-top:1px solid var(--border)}.query-parts>section:last-child{display:block}.query-parts>section:last-child .hint{margin-top:.7rem}.query-footer{padding:.8rem 1rem}.query-footer>span{display:none}.query-footer>button{width:100%}.result-count{flex-basis:100%;order:3}.matrix tr>th:first-child{min-width:115px;max-width:140px;font-size:.78rem}.pie-cell{flex-direction:column;gap:0}.map-group{max-width:100%}.outcome-detail{grid-template-columns:1fr}}
</style>
