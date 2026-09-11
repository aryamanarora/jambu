"""Same-language lexical-identity candidates, for manual acceptance only."""
import unicodedata as ud,re,json,sys
from collections import defaultdict
from analysis_data import load_records,HERE,write_tsv
def spelling(s):
    # Coarse retrieval removes accent/quantity and also caron (including č/ǰ).
    # Every accepted candidate was manually inspected; this is not equivalence.
    s=''.join(c for c in ud.normalize('NFD',s.lower()) if c not in '\u0301\u0300\u0302\u0304\u030cː:ʹˈˊ\'')
    s=re.sub(r'([aeiou])\1+',r'\1',s)
    return ud.normalize('NFC',s).strip()
def meaning(s):return re.sub(r'^to ','',s.lower().strip()).rstrip('!')
def candidates():
    rows=load_records();anchors=defaultdict(list);targets=defaultdict(list)
    for r in rows:
        k=(r['language_id'],meaning(r['research_gloss']),spelling(r.get('research_original',r['original'])))
        if r['research_family_id'] and not r['strict_exclusion'] and r['research_link_confidence'] not in ['provisional']:
            anchors[k].append(r)
        elif not r['research_family_id'] and 'etymological_assessment' not in r:targets[k].append(r)
    out=[]
    for k,rs in sorted(targets.items()):
        aa=anchors.get(k,[]);fids={r['research_family_id'] for r in aa}
        if len(fids)!=1:continue
        fid=next(iter(fids));out.append(dict(candidate=len(out),language=k[0],gloss=k[1],spelling=k[2],family_id=fid,
          record_ids=[r['id'] for r in rs],target_forms=sorted({r['original']+' ['+r['source_keys']+']' for r in rs}),
          anchor_ids=[r['id'] for r in aa],anchor_forms=sorted({r.get('research_original',r['original'])+' ['+r['source_keys']+']' for r in aa})))
    return out
if __name__=='__main__':
    cs=candidates();start=int(sys.argv[1]) if len(sys.argv)>1 else 0;count=int(sys.argv[2]) if len(sys.argv)>2 else 100
    print('CANDIDATES',len(cs))
    for c in cs[start:start+count]:print(c['candidate'],c['language'],c['gloss'],'→',c['family_id'],'TARGET',','.join(c['target_forms']),'ANCHOR',','.join(c['anchor_forms']))
