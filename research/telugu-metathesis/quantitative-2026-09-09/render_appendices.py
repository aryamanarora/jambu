#!/usr/bin/env python3
"""Render complete reviewed case annotations and concise count tables, not the report.

No linguistic inference is made here. Form and source strings are copied from the
validated annotation exports. The raw-record appendix remains a separate TSV.
"""
import csv,json,html,re
from collections import defaultdict
from pathlib import Path
from annotations import CASES
from quantify_families import read,write,classify_input
P=Path(__file__).resolve().parent
def esc(s):return html.escape(str(s))
def md(s):return str(s).replace('|','\\|').replace('\n','<br>')
def render_md(txt):
 out=[];intable=False
 def inline(s):
  s=esc(s).replace('&lt;br&gt;','<br>');s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
  return s
 for line in txt.splitlines():
  if line.startswith('| '):
   parts=re.split(r'(?<!\\)\|',line)[1:-1]
   if all(re.fullmatch(r'[ :\-]+',x) for x in parts):continue
   if not intable:out.append('<div class="scroll"><table>');intable=True
   out.append('<tr>'+''.join('<td>'+inline(x.strip().replace('\\|','|'))+'</td>' for x in parts)+'</tr>');continue
  if intable:out.append('</table></div>');intable=False
  if not line.strip() or line.startswith('<a id='):continue
  if m:=re.match(r'^(#{1,6}) (.*)',line):out.append(f'<h{len(m[1])}>{inline(m[2])}</h{len(m[1])}>')
  else:out.append('<p>'+inline(line)+'</p>')
 if intable:out.append('</table></div>')
 return ''.join(out)
def table(rows,fields):
 return '\n'.join(['| '+' | '.join(fields)+' |','| '+' | '.join('---' for f in fields)+' |',*['| '+' | '.join(md(r.get(f,'')) for f in fields)+' |' for r in rows]])+'\n'
ev=read('cited-evidence.tsv');byentry=defaultdict(list)
for r in ev:byentry[r['Entry_ID']].append(r)
forms=defaultdict(list)
for r in read('formation-tests.tsv'):forms[r['Entry_ID']].append(r)
others=defaultdict(list)
for r in read('other-process-observations.tsv'):others[r['Entry_ID']].append(r)
intro='''# Complete annotated casebook

All 409 reviewed DEDR entries are included below, including negative and ambiguous
cases. The primary counting unit merges these into 403 root families; sensitivity
partitions are in family-partitions.tsv. D = supported displacement-family history,
R = retained target initial order, O = other development, A = unresolved analysis,
B = borrowing. D does not by itself establish a literal historical segment swap.
R refers to the target initial-order comparison, not the absence of all other changes.
Unattested and attested-but-unreviewed cells are in language-outcomes.tsv.

Source forms, spelling, glosses, source keys, dialect tags and stable IDs are preserved
in cited-evidence.tsv. The 17,558 raw records in reviewed groups are separately preserved
in complete-reviewed-records.tsv; an explicit field distinguishes individually cited
evidence from records not individually adjudicated. A selected source form can occur
in several duplicate records; those records are listed together and are not extra votes.

Reconstructions and intermediate stages marked * are hypotheses. Source-specific
reconstructions are evaluated in the input-support paragraph, not accepted as database
ground truth. DEDR ṛ̆ is usually written ẓ in the analysis; attested strings are unchanged.
Exact historical level is given when independently supportable; unspecified * forms
are comparative inputs, not automatically Proto-Dravidian.

The independently defined input classes are computed without inspecting outcomes.
Their construction is not a blinded or preregistered experiment: the review is targeted
and includes an outcome-enriched cluster sweep. The broad application prediction is a
deliberately falsifiable Telugu hypothesis, not a prediction imposed on every language.

'''
out=[intro];sections=[]
for c in sorted(CASES,key=lambda c:int(c['entry_id'][1:])):
 e=c['entry_id'];ci=classify_input(c);lines=[f'<a id="{e}"></a>\n## {e}: {c["concept"]}\n']
 fields=[('Primary family',c['family_id']),('Comparative input',c['reconstruction']),('Initial consonant',c['c1']),('V1 quality / quantity',c['v1']+' / '+c['v1_quantity']),('C2 identity / structure',c['c2']+' / '+c['c2_structure']),('Following vowel',c['v2']),('Root/formation shape',c['structure']),('Grammatical category',c['grammatical_category']),('Boundary evidence',c['boundary_evidence']),('Input class',ci['Domain']),('Telugu hypothesis',ci['Telugu_Broad_Obligatory_Hypothesis']),('Input confidence',c['input_confidence']),('Overall confidence',c['confidence']),('Eligibility / caveat',c['eligibility'])]
 lines.append(table([{'Property':k,'Annotation':v} for k,v in fields],['Property','Annotation']))
 for label,key in [('Independent input evidence','input_support'),('Direction','direction_argument'),('Derivation and relative chronology','derivation'),('Exceptions and discriminating evidence','exception_notes'),('Mechanism scope','mechanism'),('Scholarly references','references')]:lines.append(f'**{label}.** {c[key]}\n')
 for lang,(status,words,note) in sorted(c['outcomes'].items()):
  lines.append(f'### {lang} — {status}\n\n{note}\n')
  grouped=defaultdict(list)
  for r in byentry[e]:
   if r['Language_ID']==lang:grouped[(r['Evidence_Form'],r['Observed_Outcome'])].append(r)
  rows=[]
  for (word,code),rr in grouped.items():
   rows.append({'Form':word,'Outcome':code,'Gloss / dialect':'; '.join(sorted({x['Gloss']+(' ['+x['Tags']+']' if x['Tags'] else '') for x in rr})),'Source / stable IDs':'; '.join(sorted({x['Source']+' — '+x['Form_ID'] for x in rr}))})
  lines.append(table(rows,['Form','Outcome','Gloss / dialect','Source / stable IDs']))
 if forms[e]:
  lines.append('### Formation-level predictions and observations\n')
  lines.append(table(forms[e],['Formation_ID','Language_ID','Reconstructed_Input','Input_Tier','Prediction','Evidence_Forms','Observed_Quantity','Quantity_Test_Result','Formation_Explanation']))
 if others[e]:
  lines.append('### Separately classified processes\n')
  lines.append(table(others[e],['Language_ID','Process','Reconstructed_Input','Observed_Form','Process_Outcome','Direction_Evidence','Relative_Chronology','References']))
 text='\n'.join(lines);out.append(text)
 # Plain-text sections preserve the complete Markdown content without an external renderer.
 # Searchable HTML uses textContent, never executes lexical HTML imported from sources.
 sections.append((e,c['concept'],text))
(P/'casebook.md').write_text('\n'.join(out))
css='''body{font:16px/1.55 system-ui,sans-serif;color:#202b33;background:#faf9f5;margin:0}header{position:sticky;top:0;background:#edf1ec;padding:18px 4%;border-bottom:1px solid #ccd3c9}h1{font-size:25px;margin:0 0 8px}input{font:inherit;width:min(600px,90%);padding:9px}main{max-width:1200px;margin:30px auto;padding:0 4%}details{background:white;border:1px solid #d9ddd6;border-radius:5px;margin:12px 0;padding:12px}summary{font-weight:650;cursor:pointer}a{color:#256048}.hint{font-size:14px}.scroll{overflow:auto}table{border-collapse:collapse;font-size:13px;width:100%;margin:12px 0}td{padding:8px;border:1px solid #d9ddd6;vertical-align:top;overflow-wrap:anywhere;min-width:80px}tr:first-child{background:#edf1ec;font-weight:600}h2{font-size:23px}h3{font-size:18px}p{max-width:95ch}'''
css+='details{scroll-margin-top:175px}header{z-index:2}'
markup='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Telugu metathesis: complete casebook</title><style>'+css+'</style><header><h1>Telugu metathesis: 409 annotated entries</h1><input id="q" placeholder="Search an ID, form, meaning, language or analysis"><span id="n">409 entries</span><div class="hint">D is displacement-family evidence; literal exchange and competing mechanisms are distinguished in each analysis. <a href="report.html">Report</a> · <a href="casebook.md">Markdown</a> · <a href="cited-evidence.tsv">Evidence TSV</a></div></header><main><p>Searches all annotations and cited evidence. Expand an entry to inspect its full analysis. Source keys resolve in <a href="source-index.md">the source index</a> and references.tsv. Raw uncited records and unreviewed cells are separate appendices.</p>'
for e,concept,txt in sections:markup+=f'<details id="{e}"><summary>{esc(e+" — "+concept)}</summary>{render_md(txt)}</details>'
markup+='''</main><script>const ds=[...document.querySelectorAll('details')];const q=document.getElementById('q');q.setAttribute('aria-label','Search annotated entries');q.addEventListener('input',()=>{const s=q.value.toLocaleLowerCase();let n=0;for(const d of ds){d.hidden=!d.textContent.toLocaleLowerCase().includes(s);if(!d.hidden)n++}document.getElementById('n').textContent=n+' entries';});function showHash(){if(!location.hash)return;const d=document.getElementById(location.hash.slice(1));if(d){q.value='';for(const entry of ds)entry.hidden=false;document.getElementById('n').textContent=ds.length+' entries';d.open=true;requestAnimationFrame(()=>d.scrollIntoView());}}addEventListener('hashchange',showHash);showHash();</script></html>'''
(P/'casebook.html').write_text(markup)
# Tables used for final report assembly; values remain traceable to membership TSVs.
counts=read('family-class-counts.tsv');ts=['# Generated quantitative tables\n\nAll rates describe the reviewed frame, not language-wide prevalence.\n']
selections=[('All-language primary frame',[r for r in counts if r['Partition']=='primary' and r['Axis']=='ALL']),('Telugu primary input domains',[r for r in counts if r['Partition']=='primary' and r['Axis']=='Domain' and r['Language_ID']=='Telugu']),('Telugu joint domain and following vowel',[r for r in counts if r['Partition']=='primary' and r['Axis']=='Domain_Following_Vowel' and r['Language_ID']=='Telugu']),('Telugu family-merger sensitivity',[r for r in counts if r['Partition']=='sensitivity' and r['Axis'] in {'ALL','Domain'} and r['Language_ID']=='Telugu'])]
fields=['Class','Language_ID','N_Reviewed_Frame_Families','N_Attested_Reviewed','N_Attested_Unreviewed','N_Missing','N_D_No_R','N_R_No_D','N_Mixed_DR','N_Other_No_DR','N_Uncertain_No_DR','N_Other_And_Uncertain_No_DR','N_Borrowed_Only','D_Over_DR','D_Over_Attested_Reviewed']
for title,rr in selections:ts.extend(['## '+title+'\n',table(rr,fields)])
ts.extend(['## Formation quantity tests\n',table(read('formation-class-counts.tsv'),['Language_ID','Input_Tier','Prediction','N_Families','N_D_Bearing','N_R_Bearing','N_Quantity_Match_Only','N_Quantity_Counterexample_Only','N_Strict_Quantity_Denominator','Match_Only_Over_Tested'])])
ts.extend(['## Telugu shared comparative evidence\n',table([r for r in read('pairwise-language-counts.tsv') if r['Partition']=='primary' and r['Input_Domain']=='all-reviewed-inputs' and 'Telugu' in {r['Language_A'],r['Language_B']}],['Language_A','Language_B','N_Common_DR_Informative','N_Both_D_Bearing','N_A_D_B_R','N_A_R_B_D','N_Both_R_No_D','N_Common_With_Mixed_Cell','Both_D_Over_Common'])])
(P/'generated-tables.md').write_text('\n'.join(ts))
print(json.dumps({'casebook_entries':len(sections),'evidence_links':len(ev),'casebook_markdown_bytes':(P/'casebook.md').stat().st_size,'casebook_html_bytes':(P/'casebook.html').stat().st_size},indent=2))
