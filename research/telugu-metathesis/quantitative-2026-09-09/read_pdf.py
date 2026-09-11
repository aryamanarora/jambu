#!/usr/bin/env python3
"""Extract research reading text with PDF page markers; never ingest into Jambu.

Requires pypdf. The text is a finding aid: check page images for phonetic symbols.
"""
import argparse
import subprocess
from pathlib import Path
from pypdf import PdfReader

p=argparse.ArgumentParser()
p.add_argument('pdf',type=Path)
p.add_argument('output',type=Path)
p.add_argument('--render-pages',default='')
p.add_argument('--pdftoppm',default='pdftoppm')
a=p.parse_args()
r=PdfReader(a.pdf)
with a.output.open('w',encoding='utf-8') as f:
    for n,page in enumerate(r.pages,1):
        f.write(f'\n===== PDF PAGE {n} =====\n')
        f.write(page.extract_text() or '')
        f.write('\n')
print(f'{len(r.pages)} pages: {a.pdf} -> {a.output}')
for page in a.render_pages.split(','):
    if not page:continue
    number=int(page)
    assert 1<=number<=len(r.pages)
    prefix=a.output.with_suffix('').with_name(a.output.stem+f'-page-{number:03d}')
    subprocess.run([a.pdftoppm,'-f',page,'-l',page,'-r','170','-png','-singlefile',str(a.pdf),str(prefix)],check=True)
