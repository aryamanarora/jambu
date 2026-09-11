"""Apply the 335 manually read Sauji gloss-group adjudications.

Selections are frozen database gloss/form groups, never accent-based retrieval.
Lexical membership is not an assertion of an exact historical formation. The
source explicitly did not analyze stress/pitch; no accent is supplied here.
"""
import json,re
from collections import defaultdict,Counter
from analysis_data import load_records,tsv,HERE,write_tsv

def glosskey(s):return re.sub(r'^to ','',s.lower().strip()).replace('!','')

def family_for(i,form,default):
    if i==24:return '9552' if form.startswith('bil') else '9416'
    if i==25:return '' # Source gloss combines go and become; homonymous stems.
    if i==37:return '8399' if form.startswith(('pu','pi')) else ''
    if i==53:return '' if form.startswith('wol') else '10452'
    if i==107:return '6140' if form.startswith('dit') else '6141'
    if i==109:return '12225' if form.startswith('baan') else '4008'
    if i in [122,248,249,254]:return '12815' if form=='se' else ''
    if i==133:return '12278' if form=='sawa' else ''
    if i==181:return '6906' if form=='na' else ''
    if i==210:return '8012' if form.startswith('paš') else '6518'
    if i==228:return '13479' if form.startswith('sot') else '13902'
    if i==306:return '11302' if form=='be' else '986'
    if i==309:return '2910' if form.startswith('ka') else ''
    if i==330 and form=='tu':return ''
    return default

def main():
    rows=load_records();groups=defaultdict(list)
    for r in rows:
        if r['language_id']=='Sv' and not r['family_id'] and 'knobloch2020sauji' in r['source_keys'].split(';'):
            groups[glosskey(r['gloss'])].append(r)
    gs=sorted(groups);assert len(gs)==335
    decisions=tsv('sauji_adjudications.tsv');assert [int(d['group']) for d in decisions]==list(range(335))
    fams={r['family_id'] for r in tsv('families.tsv')}
    out=[];annotations=[];links=[];summary=Counter()
    provisional={80,136,165,176,179,188,206,209,237,284,305,323}
    verbgroups={24,25,26,43,46,53,54,55,59,60,61,64,65,69,105,107,108,109,110,112,147,148,152,207,208,210,218,223,228,271,302,303,307,316,317,318,319}
    compoundgroups={104,167,191,206}
    for i,d in enumerate(decisions):
        g=gs[i];rs=groups[g];notes=d['note']
        annotations.append(dict(record_ids=[r['id'] for r in rs],analysis=notes,
          scope='Manual reading of all frozen Knobloch source-extract forms in this gloss group; not a claim of individual PDF collation.',
          source_qualification='Knobloch2020p16 leaves stress and pitch accent unanalyzed; unmarked forms have unknown accent. Secondary Buddruss citations retain their source labels.',
          review_group=i,review_gloss=g))
        for r in rs:
            form=r['original'];fid=family_for(i,form,d['family'])
            assert not fid or fid in fams,(i,fid)
            previous=r.get('research_link_locator','')
            exists=bool(r['research_link_evidence']) and not previous.startswith('research_links_13.jsonl:')
            status='previous-research-link' if exists else 'new-family-association' if fid else 'assessed-no-secure-input'
            confidence='provisional' if i in provisional else 'high'
            relation='root-family-only' if i in verbgroups else 'compound-component-only' if i in compoundgroups else 'manually-reviewed-lexical-family'
            if fid and not exists:
                link=dict(record_id=r['id'],family_id=fid,confidence=confidence,relation=relation,basis=notes+' Knobloch2020 source-extract group '+str(i)+'. No accent copied or reconstructed from the modern unmarked citation.')
                if i in verbgroups or i in compoundgroups:link['strict_exclusion']='root-or-component-association-not-exact-formation'
                links.append(link)
            summary[status]+=1
            out.append(dict(group=i,gloss=g,record_id=r['id'],form=form,source=r['source_keys'],
              proposed_family=fid,retained_previous_family=r['research_family_id'] if exists else '',
              status=status,confidence=confidence if fid else '',relation=relation if fid else '',analysis=notes,
              source_locator=r.get('source_refs',''),description=r['description']))
    write_tsv('sauji-source-review.tsv',out)
    for name,data in [('lexical_annotations_01.jsonl',annotations),('research_links_13.jsonl',links)]:
        (HERE/name).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in data))
    print('groups',len(gs),'records',len(out),'links',len(links),dict(summary))
if __name__=='__main__':main()
