"""Rebuild the Telugu blog's examples, interactive aggregates and downloadable audit.
Run from any directory with Python 3. No third-party dependencies; no DB mutation.
The frozen investigation is the input. Counts are recomputed from memberships.
"""
import csv, io, json, re, hashlib, zipfile, unicodedata
from pathlib import Path
from collections import Counter, defaultdict
from examples import EXAMPLES
P=Path(__file__).resolve().parent; S=P.parent/'quantitative-2026-09-09'; ROOT=P.parents[2]
PUBLIC=ROOT/'static/research/telugu-metathesis'; PUBLIC.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'src/lib/blog/data'; DATA.mkdir(parents=True,exist_ok=True)
def read(n):
 with (S/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def tsv(rows):
 out=io.StringIO(); w=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return out.getvalue()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
A={r['entry_id']:r for r in read('etymon-annotations.tsv')}
I={r['Family_ID']:r for r in read('family-input-classes.tsv') if r['Partition']=='primary'}
L={(r['Family_ID'],r['Language_ID']):r for r in read('family-language-outcomes.tsv') if r['Partition']=='primary'}
E=read('cited-evidence.tsv');F=read('formation-tests.tsv');FM=read('formation-count-membership.tsv');T=read('stop-cluster-annotations.tsv')
assert len(I)==403
M=[];charts={}
def row(chart,view,label,categories,items):
 counts=Counter()
 for fam,cat,ids in items:
  assert cat in categories,(chart,cat);counts[cat]+=1
  M.append(dict(Chart=chart,View=view,Row=label,Category=cat,Family_ID=fam,Evidence_or_Formation_IDs=ids))
 return {'label':label,'values':[counts[c] for c in categories]}
def chart(id,title,views):
 charts[id]={'id':id,'title':title,'sourceBase':'/research/telugu-metathesis','sources':['chart-membership.tsv','study-data.zip'],'views':views}
def view(label,cats,rows,note,unit='Primary root families'):return dict(label=label,unit=unit,categories=cats,rows=rows,note=note)
CATS=['Displaced, no retention','Displaced and retained','Retained, no displacement','Other only','Uncertain (with or without other)','Borrowed only','Missing','Not reviewed']
def state(r):
 if r['Has_D']=='1':return CATS[1] if r['Has_R']=='1' else CATS[0]
 if r['Has_R']=='1':return CATS[2]
 if r['Has_A']=='1':return CATS[4]
 if r['Has_O']=='1':return CATS[3]
 if r['Has_B']=='1':return CATS[5]
 return CATS[6] if r['Attested']=='0' else CATS[7]
def state_items(families,lang='Telugu'):
 return [(f,state(L[(f,lang)]),L[(f,lang)]['Evidence_IDs']) for f in sorted(families)]
domains=['short-vowel-initial-singleton-apical','short-C-initial-singleton-r-ẓ']
# Discover the literal second domain name from the frozen controlled vocabulary.
domains[1]=next(x['Domain'] for x in I.values() if x['Domain'].startswith('short-C') or x['Domain'].startswith('short-consonant'))
views=[]
for scope,low in [('All following-vowel classes',False),('Independently classified low-a formations',True)]:
 rows=[]
 for domain,label in zip(domains,['Vowel-initial, short vowel + single apical','Consonant-initial, short vowel + single r/ẓ']):
  fs=[f for f,r in I.items() if r['Domain']==domain and (not low or r['Following_Vowel']=='low-a')]
  rows.append(row('inputs',scope,label,CATS,state_items(fs)))
 views.append(view(scope,CATS,rows,'These input groups were reviewed through different discovery screens. Their proportions describe this sample, not unbiased language-wide change rates. Mixed families occur once; missing and unresolved evidence are separate.'))
chart('inputs','Similar-looking inputs have more than one Telugu outcome',views)
qcats=['Matches predicted quantity','Contradicts predicted quantity','Not strictly testable']
qrows=[]
for tier,pred,label in [('full','long-if-displaced','Full input: low or equal following vowel → long'),('full','short-if-displaced','Full input: different high following vowel → short'),('cluster','short-from-consonantal-input','Independent consonantal input → short')]:
 rs=[r for r in FM if r['Language_ID']=='Telugu' and r['Input_Tier']==tier and r['Prediction']==pred]
 qrows.append(row('quantity','Matched formations',label,qcats,[(r['Family_ID'],{'match':qcats[0],'counterexample':qcats[1],'not-strictly-testable':qcats[2]}[r['Category']],r['Formation_IDs']) for r in rs]))
chart('quantity','Vowel quantity is a conditional prediction about the immediate formation',[view('Matched formations',qcats,qrows,'Strict displaced-output denominators: 25/33 long, 8/8 short with different high V₂, and 21/21 short from consonantal inputs. Grey/non-testable families stay visible. Families can enter more than one formation class: do not sum rows.')])
# Exact paired-form screen: descriptive evidence availability, not inferred causation.
RED=json.loads((P/'reduction-screen.json').read_text()); paired={r['family'] for r in RED}
ds={f for f in I if L[(f,'Telugu')]['Has_D']=='1'};assert len(ds)==117 and len(paired)==41 and len(RED)==56
for r in RED:
 r['screen_interpretation']='Exact paired forms within a family with independently supported displacement. A pair supports a possible reduction route, not the exclusive origin or age of the reduced form. See inherited derivation and exception notes.'
 r['competing_analysis']= 'Reduced form already marked uncertain in frozen analysis.' if 'A' in r['reduced_flags'] else 'A supported pathway; alternatives and morphology must still be checked in the family notes.'
 if r['entry'] in ['d4750','d4559','d5007']:r['competing_analysis']+=' Direct assimilation or medial loss is demonstrably available elsewhere in this family.'
dump(PUBLIC/'reduction-audit.json',RED)
rc=['An exact cluster/reduced pair is cited','No exact pair in the cited evidence']
rr=row('reduction','Evidence availability','All Telugu displacement-bearing families',rc,[(f,rc[0] if f in paired else rc[1],L[(f,'Telugu')]['Evidence_IDs']) for f in sorted(ds)])
chart('reduction','Forty-one families preserve a cluster/reduced-form bridge',[view('Evidence availability',rc,[rr],'41/117 (35.0%) is the availability of exact paired witnesses, not a rate of consonant loss. The remaining 76 are not negative cases: many lack the relevant initial cluster or an exact cited variant. The 56 pairs are subobservations, not 56 independent etyma.')])
partners=['Gondi','Konda','Kui','Kuwi','Pengo','Manda','Brahui']
pc=['Both have displacement','Telugu displacement; partner retention only','Telugu retention only; partner displacement','Both retention only']
prows=[]
for lang in partners:
 items=[]
 for f in sorted(I):
  a=L[(f,'Telugu')];b=L[(f,lang)]
  if (a['Has_D']=='1' or a['Has_R']=='1') and (b['Has_D']=='1' or b['Has_R']=='1'):
   cat=pc[0] if a['Has_D']==b['Has_D']=='1' else pc[1] if a['Has_D']=='1' else pc[2] if b['Has_D']=='1' else pc[3]
   items.append((f,cat,a['Evidence_IDs']+';'+b['Evidence_IDs']))
 prows.append(row('languages','Common informative families','Kuvi' if lang=='Kuwi' else lang,pc,items))
allrows=[row('languages','All 403 reviewed input families','Kuvi' if lang=='Kuwi' else lang,CATS,state_items(I,lang)) for lang in ['Telugu']+partners]
chart('languages','A shared process does not give every language the same lexical distribution',[
 view('Common informative families',pc,prows,'Each bar contains only families with displacement or retention evidence in both languages. A “both displacement” cell may also contain retained formations. Telugu–Kui has 26 mixed-family comparisons among its 91 common families. Shared outcomes do not establish a single inherited event.'),
 view('All 403 reviewed input families',CATS,allrows,'This view restores missing, other, uncertain, borrowed and unreviewed cells. Modern language labels aggregate historical and dialectal records; those remain separate in the evidence download. These are selected-sample proportions, not rates across each language’s whole lexicon.')])
sc=['Source-supported reversal','Possible retained counterexample']
srows=[]
for lang in ['Kui','Kuwi','Pengo','Manda']:
 rs=[r for r in T if r['Language_ID']==lang and r['Disposition'] in ['source-supported-verbal-input','possible-retained-counterexample']]
 # Kuvi and Manda also have comparative (rather than explicit-parenthetical) inputs.
 supported=next(r for r in read('stop-rule-counts.tsv') if r['Language_ID']==lang)
 groups=defaultdict(list)
 for r in T:
  if r['Language_ID']==lang and r['Input_Class']=='verbal-velar+labial-formative' and r['Observed_Outcome'] in ['D','R?']:groups[r['Family_ID']].append(r)
 for r in rs:groups[r['Family_ID']].append(r)
 items=[]
 for fam,records in groups.items():
  cat=sc[0] if any(r['Observed_Outcome']=='D' for r in records) else sc[1]
  items.append((fam,cat,';'.join(sorted({r['Record_ID'] for r in records}))))
 counts=Counter(x[1] for x in items)
 assert counts[sc[0]]==int(supported['N_D']) and len(items)==int(supported['N_Input_Supported_Families']),(lang,counts,dict(Counter(r['Disposition'] for r in T if r['Language_ID']==lang)))
 srows.append(row('kui','Input-supported stem–suffix formations','Kuvi' if lang=='Kuwi' else lang,sc,items))
chart('kui','The clearest local regularity is velar + labial at a morphological boundary',[view('Input-supported stem–suffix formations',sc,srows,'Kui: 61/61 input-supported families in the selected literal cluster screen. This is not a random sample of verbs, nor proof that all velar–labial sequences reverse. The wider screen adjudicated 152 records in 123 groups, including duplicates, controls and spurious matches.')])
with (S.parent/'cluster-triage.tsv').open() as f:prior={r['Entry_ID'] for r in csv.DictReader(f,delimiter='\t')}
prior={A[e]['family_id'] for e in prior};assert len(prior)==116
chart('clusters','Only 74 of 116 cluster-candidate families establish displacement',[view('All previously screened cluster candidates',CATS,[row('clusters','All previously screened cluster candidates','Previously collected Telugu cluster candidates',CATS,state_items(prior))],'48 displaced without retention + 26 mixed = 74/116 (63.8%). The remaining 42 include retained relatives, other developments and unresolved analyses; they are not all proven false positives. Every candidate family was reviewed.')])
# Readable tables with stable entry and form links, plus complete source-backed annotations.
example_rows=[]; tables={};norm=lambda s:unicodedata.normalize('NFC',s)
def match(e,lang,form):
 rs=[r for r in E if r['Entry_ID']==e and r['Language_ID']==lang and (norm(r['Evidence_Form'])==norm(form) or norm(r['Evidence_Form']).startswith(norm(form)+' ('))]
 if not rs:raise ValueError(('Unattested example',e,lang,form))
 # Exact displayed form is a shortened label only when source carries a paradigm in parentheses.
 r=sorted(rs,key=lambda r:(r['Record_Origin']!='database',r['Form_ID']))[0]
 fid=r['Form_ID'] if r['Record_Origin']=='database' else r['Linked_Database_IDs'].split(';')[0]
 if not fid:raise ValueError(('No stable database link',e,form))
 return f'{"Kuvi" if lang=="Kuwi" else lang} [{form}](form:{fid})',r
for section,items in EXAMPLES.items():
 assert len(items)==10
 seen=set();lines=['| Etymon | Earlier input / formation | Attested evidence | What the comparison shows |','| --- | --- | --- | --- |']
 for item in items:
  e='d'+str(item[0]);a=A.get(e,{});fam=a.get('family_id',e);assert fam not in seen;seen.add(fam)
  evidence=[]
  if section=='kui':
   _,word,concept,inp,past,note=item
   t=next(r for r in T if r['Entry_ID']==e and r['Language_ID']=='Kui' and (r['Source_Form']==word or r['Source_Form'].startswith(word+' (')))
   assert inp in t['Proposed_Immediate_Input'] and past in (t['Supporting_Past_Stem']+' '+t['Source_Gloss'])
   forms=f'Kui [{word}](form:{t["Record_ID"]}); past stem {past}'
   source_ids=t['Record_ID'];source_rows=[t];refs='DEDR '+e[1:]+'; Winfield 1928 pp.72–75 (formation comparison)';derivation=inp+' → '+word;confidence=t['Confidence'];exceptions=t['Exception_Notes']
  else:
   _,inp,panel,note=item
   if section=='quantity':
    f=next(r for r in F if r['Formation_ID']==inp and r['Language_ID']=='Telugu');inp=f['Reconstructed_Input']
   inp=inp or a['reconstruction'];concept=a['concept'];refs=a['references'];derivation=a['derivation'];confidence=a['confidence'];exceptions=a['exception_notes']
   links=[]
   for lang,word in panel:
    label,r=match(e,lang,word);links.append(label);evidence.append(r)
   forms='; '.join(links);source_ids=';'.join(r['Form_ID'] for r in evidence);source_rows=evidence
  # Escape asterisks to preserve starred reconstructions as text in Markdown tables.
  cell=lambda s:str(s).replace('|',' / ').replace('*','\\*').replace('\n',' ')
  lines.append(f'| [{e}: {cell(concept)}](entry:{e}) | {cell(inp)} | {forms} | {cell(note)} |')
  example_rows.append(dict(Section=section,Entry_ID=e,Family_ID=fam,Concept=concept,Displayed_Input=inp,Displayed_Evidence=forms,Annotation=note,Source_Record_IDs=source_ids,References=refs,Full_Derivation=derivation,Confidence=confidence,Exception_Notes=exceptions,Source_Rows_JSON=json.dumps(source_rows,ensure_ascii=False)))
 tables[section]='\n'.join(lines)
template=(P/'post.md.in').read_text()
for section,table in tables.items():
 assert template.count('{{table:'+section+'}}')==1
 template=template.replace('{{table:'+section+'}}',table)
assert '{{table:' not in template
(ROOT/'src/lib/blog/posts/telugu-metathesis.md').write_text(template)
(PUBLIC/'annotated-examples.tsv').write_text(tsv(example_rows))
(PUBLIC/'chart-membership.tsv').write_text(tsv(M))
dump(DATA/'telugu-metathesis-charts.json',charts);dump(PUBLIC/'charts.json',charts)
# A compact self-contained audit archive includes the scripts and unchanged study tables.
files=['etymon-annotations.tsv','family-input-classes.tsv','family-language-outcomes.tsv','cited-evidence.tsv','formation-tests.tsv','formation-count-membership.tsv','formation-class-counts.tsv','stop-cluster-annotations.tsv','stop-rule-counts.tsv','stop-cluster-count-membership.tsv','pairwise-language-counts.tsv','references.tsv','SOURCE_ACCESS.md']
with zipfile.ZipFile(PUBLIC/'study-data.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(S/name,'quantitative-2026-09-09/'+name)
 z.write(S.parent/'cluster-triage.tsv','cluster-triage.tsv')
 for name in ['build.py','examples.py','prepare.py','post.md.in','reduction-screen.json','README.md']:
  z.write(P/name,'blog-2026-09-09/'+name)
 for name in ['chart-membership.tsv','annotated-examples.tsv','reduction-audit.json','charts.json']:z.write(PUBLIC/name,'blog-output/'+name)
manifest={n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in files}
dump(P/'input-hashes.json',manifest)
print('Generated six charts,',len(example_rows),'annotated examples,',len(M),'chart memberships.')
for id,c in charts.items():
 for v in c['views']:
  print(id,v['label'],[(r['label'],r['values']) for r in v['rows']])
