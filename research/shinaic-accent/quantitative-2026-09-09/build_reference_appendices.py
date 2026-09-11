"""Readable quantitative, bibliographic and proposal appendices; no final narrative."""
import html,json,re
from analysis_data import HERE,tsv,jsonlines
from build_appendices import DEST,page,embedded,NAMES

TABLES=[
('exception-ledger.tsv','Consolidated model exception ledger','Every tested residual and documented special case, with its source table and full evidence. Repeated membership in different tests is retained, not counted as independent exceptions.'),
('editorial-and-source-decisions.tsv','Editorial, formation and source decisions','Every research-only correction or explicit source observation, preserving its original locator and rationale.'),
('all-family-open-issues.tsv','All family-level open questions','The complete first-pass unresolved-issue register. An open verification question is not automatically a counterexample to a sound law.'),
('class-definitions.tsv','Lexical class definitions and selection tables','All 27 class domains represented in the counterpart panels, with the frozen source inventory defining each. Overlapping subsets are not independent innovations.'),
('class-counterpart-outcome-summary.tsv','Every tested class: all-language outcome ranges','Complete counterpart outcome sets in all seven languages. Broad family counterparts can have different formations; these counts are not cross-language prediction accuracies.'),
('class-counterparts-all-languages.tsv','Every tested class: individual counterpart families','Exact selected class tokens are distinguished from every other record in the same research family. Unlinked members remain visible without invented cognates.'),
('class-memberships.tsv','Every tested class: exact member tokens','The records that define each tested class; source constraints and split-token identity are retained.'),
('old-long-screen.tsv','Broad old-long falsification screen','All eligible old-long two-nucleus inputs with modern monosyllabic E/L readings. Family-level source and dialect conflicts remain conflicts.'),
('old-long-screen-residuals.tsv','Every broad old-long residual','Opposite or conflicting family/language cells, with individual explanations and unresolved issues.'),
('old-long-nominal-sensitivity.tsv','Restricted nominal class: source and input sensitivity','29 explicitly selected old nominal a-stem families; twelve input/source/lect scopes. This subset is not a claim of exhaustive nominal reconstruction.'),
('old-long-nominal-formation-audit.tsv','Restricted nominal class: selection rationale','Every selected family, its independent nominal formation basis, and documented alternatives.'),
('old-long-nominal-language-panel.tsv','Restricted nominal class: all seven languages','Every selected family/language cell, including unmarked and excluded evidence.'),
('old-long-nominal-residuals.tsv','Restricted nominal class: all residuals','Smell, village and source/lect/sense conflicts retained.'),
('short-root-cluster-screen.tsv','Short-root cluster comparisons','Old input and Shina lect outcomes. A descriptive structural screen, not a universal cluster-lengthening law.'),
('short-root-cluster-summary.tsv','Short-root cluster summary','Family outcome sets by old root vowel and Shina lect; vowels are not pooled.'),
('palula-short-a-pairs.tsv','Palula new short-a length: every pair','Biori short-a versus Ashret long-a; aspiration/h, forms, predictions and all residuals.'),
('palula-short-a-sensitivity.tsv','Palula short-a: units and scope','All forms, closed syllables, and closed lexemes with article/numeral identity collapsed.'),
('palula-u-adjectives.tsv','Palula grammatical short-u class','Gender-inflecting regular/umlaut types, including accented ú and participles. Source metadata is not assumed to prove an exact dialect paradigm.'),
('palula-tagged-u-adjectives.tsv','Palula POS-tagged short-u adjectives','Separate lexical-POS selection; all final-accented exceptions retained.'),
('gilgit-o-adjectives.tsv','Gilgit short-o adjectives','Independent adjective tags and final short-o selection, with all unscorable records.'),
('adjective-cognate-panel.tsv','Adjective counterparts in all languages','Whole-family panel associated with source-tagged adjectives; includes other formations and senses, not one pooled adjective statistic.'),
('property-location-screen.tsv','Core property comparison: records','Predeclared property families, retained short endings and source-specific stress/accent position.'),
('property-location-summary.tsv','Core property comparison: seven-language counts','Penultimate, other, mixed and unscorable family outcomes. Restricted lexical comparison, not a fitted law.'),
('palula-umlaut-i-nouns.tsv','Palula aa/ee+i noun paradigms','All74 candidates,73 comparable full-form cells/66 lexemes, and the excluded mismatched rainbow paradigm. Selection ignores accent.'),
('palula-i-decl-extension.tsv','Palula i-declension: extension beyond umlaut','All43 further candidates,42 comparable cells/30 lexemes. Final-i accent persists while citation E/L varies; the unverified gun variant paradigm is excluded.'),
('vowel-raising-reviewed.tsv','Biori–Ashret raising: all78 pairs','Quality, accent and syllable domain, including six aa-to-uu residuals and independently supported versus speculative proto-au analyses.'),
('vowel-raising-summary.tsv','Vowel-raising outcome summary','Form-pair counts; two late-aa forms instantiate one accusative suffix, and five genitive forms instantiate one ending.'),
('kalkoti-palula-adjudicated.tsv','Kalkoti–Palula: every comparison','Source-specific tone/contour observations with formation exclusions, uncertainties and residual analysis.'),
('kalkoti-palula-summary.tsv','Kalkoti–Palula: source-specific counts','2013 phonetic contours and2023 High/Low analysis kept separate.'),
('kalkoti-palula-combined.tsv','Kalkoti–Palula: consolidated lexical cells','Cell consolidation by broad family and Palula citation; missing tone remains unknown.'),
('kalkoti-palula-combined-summary.tsv','Kalkoti–Palula: class counts','Known outcomes, Low interactions, unknown and excluded cells; not an unbiased sample of all tone categories.'),
('numeral-series-records.tsv','Numerals11–20: complete records','381 source tokens across all seven languages, including different formations and misglossed twenty-plus-five expressions.'),
('numeral-series-language-panel.tsv','Numerals11–20: seven-language panel','Ten-compound series11–18; nineteen and twenty compared separately. Not eight independent innovations.'),
('numeral-series-tests.tsv','Palula–Kalkoti numeral correspondence','Eight ten compounds plus two twenty-element controls, with predictions and all source outcomes.'),
('dras-paradigm-review.tsv','Dras: every reviewed plural citation','287 plural citations with singular candidates and individual or paradigm-class assessments. Exact-gloss matches are not automatically valid paradigms.'),
('dras-suffix-accent-review.tsv','Dras: final-suffix accent readings','Every plural, including dual stem/final marks and source contradictions.'),
('dras-suffix-accent-summary.tsv','Dras: plural suffix counts','Final-only, dual, stem-only and unmarked citations. Counts are citations, not independent etyma.'),
('kundal-primary-paradigms.tsv','Kundal Shahi: all21 primary paradigms','Fixed, mobile rising, truncated feminine and unexplained postaccenting paradigms from the2004 draft.'),
('sauji-source-review.tsv','Sauji: all573 Knobloch records','335 manually reviewed gloss groups; linked, provisional, component-only and unknown analyses. Accent was not investigated by this source.'),
('input-class-summary.tsv','Full nearest-input class inventory','Seven-language outcome sets for every automatically described historical input class; overlapping family counts are explicit.'),
('input-class-family-outcomes.tsv','Full input classes: family/language cells','Complete eligible and excluded outcomes, with all forms and sources.'),
('coverage-by-source.tsv','Frozen raw source coverage','Counts overlap for merged citations; accent-mark presence is not a phonological interpretation.'),
('coverage-research-by-source.tsv','Research source coverage','Tokens, linked ancestry, unknown ancestry and explicit review counts after research-only corrections.'),
]
SCRIPT=r'''
const D=JSON.parse(document.getElementById('data').textContent),$=s=>document.querySelector(s);let page=0,filtered=[];const size=40;
const val=x=>String(x??''),norm=x=>val(x).normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
function e(t,s){let x=document.createElement(t);if(s!==undefined)x.textContent=s;return x}
const CORE={
'exception-ledger.tsv':['ledger_id','family_id','language','status','explanation'],
'editorial-and-source-decisions.tsv':['locator','family_id','kind','decision'],
'class-counterparts-all-languages.tsv':['class_id','family_or_unlinked_member','language','outcomes','selected_class_tokens'],
'class-counterpart-outcome-summary.tsv':['class_id','language','families_or_members_with_counterpart_records','families_or_members_without_counterpart_records','observed_counterpart_outcome_counts'],
'old-long-nominal-language-panel.tsv':['family_id','language','all_forms','outcomes'],
'short-root-cluster-screen.tsv':['family_id','input','form','dialect','observed','analysis'],
'palula-short-a-pairs.tsv':['biori','ashret_forms','gloss','input_class','status'],
'palula-u-adjectives.tsv':['masculine','feminine','gloss','input','status'],
'palula-tagged-u-adjectives.tsv':['form','gloss','observed_from_right','observed_mora','status','exclusion'],
'gilgit-o-adjectives.tsv':['form','gloss','observed_from_right','observed_mora','status','exclusion'],
'property-location-screen.tsv':['family_id','language','form','outcome','status','analysis'],
'palula-umlaut-i-nouns.tsv':['citation','gloss','inflected','citation_outcome','status','analysis'],
'palula-i-decl-extension.tsv':['citation','gloss','inflected','citation_outcome','status','analysis'],
'vowel-raising-reviewed.tsv':['biori','ashret','gloss','input_class','status','analysis'],
'kalkoti-palula-combined.tsv':['family_id','palula','glosses','kalkoti_forms','status','adjudication'],
'numeral-series-records.tsv':['numeral','language','form','outcome','source'],
'dras-suffix-accent-review.tsv':['gloss','plural','suffix','suffix_accent_status','manual_lexical_note'],
'kundal-primary-paradigms.tsv':['gloss','nom_singular','nom_plural','obl_singular','obl_plural','observed_pattern'],
};
const label=k=>k.replaceAll('_',' ').replace(/^./,c=>c.toUpperCase());
function valueCell(v){let td=e('td');v=val(v);if(v.length>300){let d=e('details');d.append(e('summary',v.slice(0,150)+'…'),e('p',v));td.append(d)}else td.textContent=v;return td}
for(let t of D){let o=e('option',t.title);o.value=t.file;$('#table').append(o)}
function update(reset=true){
 if(reset)page=0;let t=D.find(x=>x.file===$('#table').value);
 $('#description').textContent=t.description;$('#download').href='../'+t.file;$('#download').textContent='Download complete TSV ('+t.rows.length+' rows)';
 let q=norm($('#search').value);filtered=t.rows.filter(r=>!q||norm(Object.values(r).join(' ')).includes(q));
 $('#count').textContent=filtered.length+(filtered.length===1?' row':' rows')+' · page '+(page+1)+' / '+Math.max(1,Math.ceil(filtered.length/size));
 let fields=(CORE[t.file]||t.fields.slice(0,t.fields.length<=8?t.fields.length:6)).filter(k=>t.fields.includes(k));
 if(fields.length<3)fields=t.fields.slice(0,6);
 let tab=e('table'),head=e('thead'),tr=e('tr');tab.className='quant-table';let cg=e('colgroup'),weights=fields.map(k=>['analysis','explanation','adjudication','decision','forms','all_forms'].includes(k)?3:['status','input_class','class_id','outcomes'].includes(k)?2:1),total=weights.reduce((a,b)=>a+b,0);for(let w of weights){let c=e('col');c.style.width=(100*w/total)+'%';cg.append(c)}tab.append(cg);for(let k of fields)tr.append(e('th',label(k)));head.append(tr);tab.append(head);let body=e('tbody');
 for(let r of filtered.slice(page*size,(page+1)*size)){
  let tr=e('tr');for(let k of fields)tr.append(valueCell(r[k]));body.append(tr);
  if(fields.length<t.fields.length){
   let full=e('tr'),cell=e('td'),d=e('details'),dl=e('dl');cell.colSpan=fields.length;dl.className='kv';d.append(e('summary','Complete row · all '+t.fields.length+' fields'));
   for(let k of t.fields){let dd=e('dd'),v=val(r[k]);if(v.startsWith('{')||v.startsWith('[')){try{v=JSON.stringify(JSON.parse(v),null,2)}catch{}}if(v.length>500||v.includes('\n'))dd.append(e('pre',v));else dd.textContent=v;dl.append(e('dt',label(k)),dd)}
   d.append(dl);cell.append(d);full.append(cell);body.append(full);
  }
 }
 tab.append(body);$('#results').replaceChildren(tab);$('#prev').disabled=page===0;$('#next').disabled=(page+1)*size>=filtered.length;
}
$('#table').onchange=()=>{history.replaceState(null,'','#'+$('#table').value);update()};$('#search').oninput=()=>update();$('#prev').onclick=()=>{page--;update(false)};$('#next').onclick=()=>{page++;update(false)};let h=decodeURIComponent(location.hash.slice(1));if(D.some(x=>x.file===h))$('#table').value=h;update();
'''
def esc(v):return html.escape(str(v))
def display_copy(s):
    s=re.sub(r'\b(All|all|and|the|The|Numerals|Table|Tables|including|representing)(?=\d)',r'\1 ',s)
    return re.sub(r',(?=\S)',', ',s)
def bibliography_html(s):
    s=esc(s).replace('\n',' ')
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2">\1</a>',s)
    return re.sub(r'\*([^*]+)\*',r'<em>\1</em>',s)
def main():
    DEST.mkdir(exist_ok=True);data=[]
    for file,title,description in TABLES:
        rows=tsv(file);data.append(dict(file=file,title=display_copy(title),description=display_copy(description),fields=list(rows[0]) if rows else [],rows=rows))
    body='''<header><div class="eyebrow">Shinaic accent · Quantitative appendices</div><h1>Classes, outcomes and exceptions</h1><p>Every reported model retains its candidate inventory, exclusions and source disagreements. Select a table, search its complete contents, or download the unabridged TSV.</p><div class="downloads"><a href="index.html">Complete family and record appendices</a><a href="../REPORT.html">Narrative report</a><a href="sources.html">Sources and notation</a></div></header><main><div class="toolbar"><label>Table<select id="table"></select></label><label>Search<input id="search" type="search" placeholder="Form, meaning, family, outcome…"></label></div><p id="description"></p><p><a id="download"></a></p><p id="count" class="count"></p><div id="results" class="scroll"></div><div class="pager"><button id="prev">Previous</button><button id="next">Next</button></div></main><footer>Counts are descriptive census/subset counts. Source tokens, lexical cells, paradigms and broad families are different units; consult each table's scope.</footer>'''
    (DEST/'tables.html').write_text(page('Shinaic accent — quantitative appendices',body,data,SCRIPT))
    entries=[]
    for r in tsv('source-register.tsv'):
        languages=', '.join(NAMES.get(l,l) for l in json.loads(r['languages'])) or 'Supplementary authority'
        entries.append('<article id="'+esc(r['source_key'])+'"><h2>'+esc(r['source_key'])+'</h2><p>'+bibliography_html(r['bibliography'])+'</p><p><strong>Notation. </strong>'+esc(display_copy(r['notation']))+'</p><p><strong>Access and review. </strong>'+esc(display_copy(r['access_and_review']))+'</p><p class="muted">'+format(int(r['raw_records']),',')+' raw source citations · '+esc(languages)+'</p>'+('<p><a href="'+esc(r['url'])+'">Primary source / bibliographic location</a></p>' if r['url'] else '')+'</article>')
    (DEST/'sources.html').write_text(page('Shinaic accent — sources and notation','<header><div class="eyebrow">Shinaic accent · Source register</div><h1>What each source can tell us</h1><p>Access level is part of the evidence. A checked database transcription, a primary printed reading and an author’s phonological analysis are recorded separately.</p><div class="downloads"><a href="index.html">Appendices</a><a href="../source-register.tsv">Download source register</a><a href="../PRIMARY_READINGS.md">Detailed primary-reading log</a></div></header><main>'+''.join(entries)+'</main>'))
    proposals=[]
    for r,loc in jsonlines('etymology_proposals.jsonl'):
        proposals.append('<article id="'+esc(r['proposal_id'])+'"><h2>'+esc(r['proposal_id']+' · '+r['forms']+' “'+r['meaning']+'”')+'</h2><p class="phon">'+esc(r['language']+' ← '+r['proposed_input']+' (Turner '+r['proposed_family']+')')+'</p><p><strong>'+esc(r['confidence'])+'</strong></p>'+''.join('<p><strong>'+esc(label)+'. </strong>'+esc(r[key])+'</p>' for key,label in [('analysis','Analysis'),('accent_consequence','Accentual consequence'),('further_test','Discriminating evidence still needed'),('source','Evidence'),('disposition','Status')])+'<p class="muted">Records: '+esc(', '.join(r['record_ids']))+'</p></article>')
    (DEST/'proposals.html').write_text(page('Shinaic accent — etymological proposals','<header><div class="eyebrow">Shinaic accent · Supplementary etymologies</div><h1>Five proposals for further testing</h1><p>These proposals are separate from the frozen 1,686-family registry. A plausible lexical identification does not establish an inherited accent history or rule out borrowing.</p><div class="downloads"><a href="index.html">Appendices</a><a href="../etymology_proposals.jsonl">Download complete proposal data</a></div></header><main>'+''.join(proposals)+'</main>'))
    (DEST/'data-dictionary.md').write_text('''# Data dictionary and appendix guide

The appendices contain all 25,505 frozen Shinaic raw records, all 25,593 analysis tokens after 88 additional source/lexeme branches, and all 1,686 original anchored family dossiers. Old Shina has zero records. New-family proposals remain supplementary. Raw-record and branch-level research associations can differ: 13,270 raw records and 13,272 analysis tokens lack a research family.

- `../corpus.tsv`: every original database field, language/source tags, nearest non-Shinaic ancestor, broad family and full accepted ancestry path. This frozen input is never silently corrected.
- `../annotated-records.tsv` / `complete-records.jsonl`: the same 25,505 IDs with research-only decisions, source readings, parser features, review level and annotations. Every raw field remains available.
- `../analysis-tokens.tsv` / `analysis-tokens.jsonl`: all raw records, with 88 additional branches where one source record merged distinct words or independently transcribed sources. `analysis_token_id` adds `#1`, `#2` where necessary; `id` remains the original database ID.
- `family-dossiers.jsonl`: 1,686 dossiers, applying every later annotation revision, with all seven language panels, every linked record ID, source outcomes and ancestor metadata. Original raw members reassigned during research remain visible in the browser dossier.
- `../historical-observations.tsv`: every research-linked token, its immediate input or explicitly labelled broad-head proxy, independently calculated input features, outcome, exclusions and family analysis.
- `../record-edges.tsv`, `../ancestral-records.tsv`, `../families.tsv`, `../languages.tsv`, `../references.tsv`: frozen graph, ancestral and bibliographic evidence.
- `../supplementary-ancestors.tsv`: the existing database subentry 10310-2, needed by a documented reference correction but absent from the original ancestry walk. Its extraction was permitted only after verifying that the live forms file still matched the starting hash; `../supplementary-ancestor-provenance.json` records that check. The original ancestral extract is unchanged.
- `tables.html`: all quantitative model tables and their full downloadable TSVs. `sources.html` records notation and the actual level of source access. `proposals.html` preserves new etymological hypotheses separately.

## Fields that must not be conflated

`family_id` and `ancestor_id` are original database associations. `research_family_id` and `research_ancestor_id` apply the explicitly recorded research decisions. A broad family can contain several distinct historical formations and lexical senses. An empty research ancestor means the headword is a proxy, not a verified immediate input.

`original` is the raw citation; `reading_form` is the source-aware reading used for analysis. `research_original`, when present, records a documented correction or split. `record_decisions`, `formation_decisions`, `source_observations`, `primary_table_readings`, `additional_record_annotations` and their locator fields preserve the reasons and audit trail. No lexical database was changed.

`individual_review` distinguishes a family-context first pass, an unlinked inventory entry, a manual lexical/source-group assessment, a research link, a structural/paradigm review and an explicit primary reading. These levels are not interchangeable. In particular, the complete appendix does not claim that every raw citation received an independent printed-page check.

`strict_exclusion` identifies record-level obstacles to strict historical predictions. Model-specific exclusions additionally include multiword expressions, fragments, uncertain vowel-sequence syllabification, provisional etymologies and unmatched grammatical formations. Excluded records are retained and searchable.

## Accent and tone labels

- E/L: first/second-mora accent only in explicitly compatible Gilgit/Shina, Palula or Strand notation.
- S: one marked short vowel; its syllable location is recorded separately.
- H1/H2/Hshort: Kalkoti High on first mora, second mora or a short vowel, in the 2023 analysis. Low can coexist with High. `0-explicit` is reserved for explicitly analyzed toneless examples.
- P-high-level, P-low-level, P-high-rising, P-low-rising, P-high-falling: 2013 primary phonetic contour observations. These are not automatically identical to the 2023 phonological categories.
- F/R/LR: a source-specific falling, rising or low-rising contour; consult the notation field. Kundal and survey conventions are not assumed identical to Shina E/L.
- stress-marked and its position: syllable stress in Brokskat, Dras or survey notation. It is not relabelled E/L.
- unmarked: the source citation does not supply usable accent information. It does not mean toneless.
- `@-1`, `@-2`, etc.: final, penultimate, etc., where the source notation and conservative syllabification permit a location. `position-unresolved` retains a mark while withholding an uncertain syllable analysis.

`modern_nuclei` is a conservative orthographic nucleus count. Unequal or interrupted vowel sequences remain flagged. Dras repeated vowels may be distinct nuclei; colon marks length. Sanskrit grave/svarita inputs are not silently treated as historically accentless merely because the acute counter is zero.

## Units and reproducibility

Raw citations, split analysis tokens, unique form/gloss types, morphological cells, paradigms, lexemes and broad etymological families are different units. Family tables use outcome sets rather than majority voting. Multiple outcomes can contribute overlapping counts; table notes state this explicitly. Eight teen numerals or several forms of one suffix are not eight independent historical changes.

In the two Palula i-declension tests, the operational lexeme grouping uses the dictionary gloss together with the full inflected form, merging citation variants. The happiness variants occur in both structural subsets and share one inflected form: 66 plus 30 therefore yields 95 combined lexemes, not 96. The complete candidate tables preserve each source record, citation and inflection.

`../reproduce.py` rebuilds quantitative outputs from the frozen corpus and reviewed analytical inputs. It does not re-extract a changed live database. JSONL review/decision files and reviewed paradigm tables are human analytical inputs; their generation scripts preserve retrieval and selection procedures. `../input-manifest.json` records the original database hashes; `../integrity-audit.json` and `../artifact-manifest.json` document final checks and output hashes.
''')
    (DEST/'table-catalog.json').write_text(json.dumps([dict(file=f,title=display_copy(t),description=display_copy(d)) for f,t,d in TABLES],ensure_ascii=False,indent=2)+'\n')
    print(len(TABLES),'quantitative tables; source and proposal appendices built')
if __name__=='__main__':main()
