"""Candidate retrieval for manual cross-language review; never assigns cognacy."""
from analysis_data import load_records,tsv
from phonology import segment_key
from collections import defaultdict
from difflib import SequenceMatcher
import re,sys

rows=load_records();families={r['family_id']:r for r in tsv('families.tsv')}
def glosskey(s):
    s=re.sub(r'^to ','',s.lower().strip()).replace('!','')
    return s
def words(s):
    return set(re.findall(r'[a-z]+',s.lower()))-{'to','a','the','of','is','be','one','s','and','or','in','it','he','she'}
bygloss=defaultdict(list)
for r in rows:
    if r['research_family_id'] and not r['strict_exclusion']:
        bygloss[glosskey(r['research_gloss'])].append(r)
langs=set(sys.argv[1].split(','));start=int(sys.argv[2]);count=int(sys.argv[3])
sources=set(sys.argv[4].split(',')) if len(sys.argv)>4 else None
groups=defaultdict(list)
for r in rows:
    if r['language_id'] in langs and not r['family_id'] and (sources is None or sources.intersection(r['source_keys'].split(';'))):
        groups[glosskey(r['gloss'])].append(r)
gs=sorted(groups)
print('UNLINKED GLOSS GROUPS',len(gs),'PACKET',start,min(start+count,len(gs)))
for i,g in enumerate(gs[start:start+count],start):
    rs=groups[g]
    print('\nGROUP',i,repr(g))
    for r in rs:
        print(' ',r['id'],r['language_id'],r['original'],'['+r['source_keys']+']',r['description'][:100],('LINKED:'+r['research_family_id']) if r['research_link_evidence'] else '')
    candidates=list(bygloss.get(g,[]))
    if not candidates and words(g):
        for h,rr in bygloss.items():
            if words(g)<=words(h) or words(h) and words(h)<=words(g):candidates.extend(rr)
    rank={}
    for r in candidates:
        score=max(SequenceMatcher(None,segment_key(x['original']),segment_key(r['original'])).ratio() for x in rs)
        fid=r['research_family_id']
        if fid not in rank or score>rank[fid][0]:rank[fid]=(score,r)
    for fid,(score,r) in sorted(rank.items(),key=lambda x:-x[1][0])[:6]:
        f=families.get(fid,{})
        print(' CAND',fid,f.get('headword',''),f.get('gloss',''),':',r['language_id'],r['original'],r['research_gloss'],round(score,2))
