#!/usr/bin/env python3
"""Render the final report as a standalone local HTML artifact (requires Markdown)."""
from pathlib import Path
import markdown
P=Path(__file__).resolve().parent
text=(P/'report.md').read_text();body=markdown.markdown(text,extensions=['tables','toc','fenced_code'])
style='''body{font:18px/1.72 Georgia,"Times New Roman",serif;color:#22312e;background:#faf9f5;margin:0}main{max-width:1050px;margin:55px auto;padding:0 35px 70px}h1,h2,h3,nav{font-family:system-ui,sans-serif}h1{font-size:40px;line-height:1.2;max-width:850px}h2{font-size:26px;line-height:1.35;margin-top:2.4em;border-top:1px solid #d3dbd5;padding-top:24px}p{max-width:94ch}a{color:#1b6753;text-underline-offset:3px}img{max-width:100%;height:auto}table{border-collapse:collapse;display:block;overflow:auto;font:13px/1.5 system-ui,sans-serif;max-width:100%;margin:25px 0}td,th{padding:9px;border:1px solid #d3dbd5;vertical-align:top;min-width:68px}th{background:#e6ede7;text-align:left}nav{font-size:14px;background:#e6ede7;padding:18px 35px;position:sticky;top:0;z-index:2}code{font-size:.88em}strong{font-weight:700}@media print{body{font-size:11pt;background:white}nav{display:none}main{margin:0;max-width:none;padding:0}h2{break-after:avoid}table{font-size:8pt}tr{break-inside:avoid}a{color:inherit}img{max-height:190mm;object-fit:contain}}'''
style+='h2,h3{scroll-margin-top:90px}'
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Telugu metathesis in comparative Dravidian perspective</title><style>'+style+'</style></head><body><nav>Research report · <a href="casebook.html">Complete casebook</a> · <a href="report.md">Markdown</a> · <a href="README.md">Reproduce</a> · <a href="SOURCE_ACCESS.md">Sources</a></nav><main>'+body+'</main></body></html>'
(P/'report.html').write_text(html)
print('Report HTML bytes',len(html.encode()))
