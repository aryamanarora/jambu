#!/usr/bin/env python3
"""Public research-source retrieval only; no Jambu lexical ingestion or installation.

Cache downloaded reading material outside the report directory. Record URLs and hashes.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[3]/'tmp'/'telugu-metathesis'
CACHE.mkdir(parents=True,exist_ok=True)

def fetch(url,name):
    path=CACHE/name
    result=subprocess.run(['curl','-L','--retry','1','--max-time','55','-o',str(path),url],capture_output=True,text=True)
    record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'file':str(path),'returncode':result.returncode}
    if path.exists():
        b=path.read_bytes()
        record.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),signature=b[:15].decode('ascii','replace'))
    if result.returncode:record['error']=result.stderr[-1000:]
    with (HERE/'retrieval-ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    print(json.dumps(record,ensure_ascii=False),flush=True)
    return path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['metadata','dharma','sastri','sastri-pdf','hume-final'])
    args=p.parse_args()
    if args.mode=='hume-final':
        fetch('https://citeseerx.ist.psu.edu/document?doi=ef8fae4444af92ba3f819aad93f3eb118a8f832b&repid=rep1&type=pdf','hume-2004-citeseer.pdf')
    elif args.mode=='metadata':
        items=[('https://archive.org/metadata/in.ernet.dli.2015.169957','sastri1969-ia-metadata.json'),
               ('https://api.github.com/repos/erc-dharma/tfb-telugu-epigraphy/git/trees/master?recursive=1','dharma-telugu-tree.json')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for result in pool.map(lambda x:fetch(*x),items):pass
    elif args.mode=='dharma':
        meta=json.loads((CACHE/'dharma-telugu-tree.json').read_text())
        commit=meta['sha']
        paths=[x['path'] for x in meta['tree'] if x['type']=='blob' and x['path'].startswith('texts/') and x['path'].endswith('.xml')]
        folder=CACHE/'dharma-telugu'
        folder.mkdir(exist_ok=True)
        jobs=[(f'https://raw.githubusercontent.com/erc-dharma/tfb-telugu-epigraphy/{commit}/{p}',f'dharma-telugu/{Path(p).name}') for p in paths]
        jobs.append((f'https://raw.githubusercontent.com/erc-dharma/tfb-telugu-epigraphy/{commit}/LICENCE.txt','dharma-telugu/LICENCE.txt'))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for result in pool.map(lambda x:fetch(*x),jobs):pass
        print('DHARMA source snapshot',commit,len(paths),'XML documents; research cache only',flush=True)
    elif args.mode=='sastri':
        meta=json.loads((CACHE/'sastri1969-ia-metadata.json').read_text())
        print('Archive metadata',meta.get('metadata',{}),flush=True)
        eligible=[f for f in meta.get('files',[]) if f['name'].endswith('_djvu.txt')]
        for f in eligible:fetch('https://archive.org/download/in.ernet.dli.2015.169957/'+f['name'],'sastri1969-djvu.txt')
    elif args.mode=='sastri-pdf':
        meta=json.loads((CACHE/'sastri1969-ia-metadata.json').read_text())
        eligible=[f for f in meta.get('files',[]) if f.get('format')=='Image Container PDF' or f['name'].endswith('_scandata.xml')]
        for f in eligible:
            name='sastri1969.pdf' if f['name'].endswith('.pdf') else 'sastri1969-scandata.xml'
            fetch('https://archive.org/download/in.ernet.dli.2015.169957/'+f['name'],name)

if __name__=='__main__':main()
