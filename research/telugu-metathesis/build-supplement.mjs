#!/usr/bin/env node
/** Render the research supplement; no lexical data or graph edges are changed. */
import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
import { Marked } from 'marked';

const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(here, '../../static/research/telugu-metathesis');
mkdirSync(output, { recursive: true });
const read = (name) => readFileSync(resolve(here, name), 'utf8');
const esc = (s) => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const parser = new Marked();
const markdown = (name) => parser.parse(read(name).replace(/^# .*\n/, '')
  .replace(/`(f_[a-z0-9]+|d\d+[a-z]?)`/g, (_, id) => `[${id.startsWith('d') ? 'DEDR ' + id.slice(1) : id}](../../entries/${id})`))
  .replaceAll('<table>', '<div class="table-scroll" tabindex="0"><table>')
  .replaceAll('</table>', '</table></div>');
function table(name, id, labels) {
  const [fields, ...rows] = read(name).trim().split(/\r?\n/).map((line) => line.split('\t'));
  if (rows.some((row) => row.length !== fields.length)) throw new Error(`Malformed table ${name}`);
  const first = (value) => /^d\d+[a-z]?$/.test(value)
    ? `<a href="../../entries/${value}">DEDR ${value.slice(1)}</a>` : esc(value);
  return { count: rows.length, html: `<div class="table-scroll" tabindex="0"><table id="${id}">
    <thead><tr>${fields.map((field) => `<th scope="col">${esc(labels[field] || field.replaceAll('_', ' '))}</th>`).join('')}</tr></thead>
    <tbody>${rows.map((row) => `<tr>${row.map((value, i) => i === 0
      ? `<th scope="row">${first(value)}</th>`
      : `<td>${/^f_[a-z0-9]+$/.test(value) ? `<a href="../../entries/${value}">${value}</a>` : esc(value)}</td>`).join('')}</tr>`).join('\n')}</tbody>
  </table></div>` };
}
const triage = table('cluster-triage.tsv', 'triage-table', {});
const audit = table('reconstruction-audit.tsv', 'audit-table', {
  Observed_record: 'Current record', Source_check: 'Documentary check', Proposed_action: 'Proposed repair'
});
if (triage.count !== 116) throw new Error('The documented triage count has changed; review the essay.');
const downloads = ['casebook.md', 'vowel-lowering-audit.md', 'bibliography.md', 'cluster-triage.tsv',
  'reconstruction-audit.tsv', 'candidate-records.tsv', 'legacy-level-flags.tsv',
  'inventory-summary.json'];
for (const name of downloads) copyFileSync(resolve(here, name), resolve(output, name));

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Telugu metathesis: evidence and audit — Jambu</title>
<meta name="description" content="Comparative casebook, 116-group cluster triage, reconstruction audit, and primary sources for Jambu's investigation of Telugu metathesis.">
<style>
:root{color-scheme:light dark;--paper:#fbf7f0;--ink:#241c24;--muted:#6d606b;--link:#6b2d6b;--border:#d8cdbb;--surface:#fffdf9}
@media(prefers-color-scheme:dark){:root{--paper:#17111a;--ink:#efe7ee;--muted:#baaaba;--link:#d9aede;--border:#47374c;--surface:#1f1723}}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:1.05rem/1.75 'Charis SIL','Iowan Old Style',Georgia,serif}
main{max-width:1100px;margin:auto;padding:32px 24px 90px}header{max-width:780px;margin:0 0 40px}h1{font-size:clamp(2rem,6vw,3.2rem);font-weight:400;line-height:1.15;margin:24px 0}h2{font-size:1.8rem;font-weight:400;line-height:1.3;margin:0 0 24px}h3{font-size:1.25rem;line-height:1.35;margin-top:2em}
a{color:var(--link);text-underline-offset:.16em}p{margin:0 0 1.25em}section{border-top:1px solid var(--border);padding-top:34px;margin-top:42px;scroll-margin-top:20px}.prose p,.prose li{max-width:790px}.prose li{margin-bottom:.5em}nav,.label,.tools,.downloads,.count{font-family:system-ui,sans-serif;font-size:.9rem}nav{display:flex;flex-wrap:wrap;gap:12px 24px;margin:24px 0}.label{color:var(--muted);letter-spacing:.08em;text-transform:uppercase}.note{padding:16px 20px;border-left:3px solid var(--link);background:var(--surface);max-width:790px}.table-scroll{overflow-x:auto;margin:22px 0;max-width:100%;border:1px solid var(--border);border-radius:5px}table{width:100%;border-collapse:collapse;font-size:.96rem;line-height:1.65}th,td{padding:13px 16px;text-align:left;vertical-align:top;border-bottom:1px solid var(--border);min-width:190px}th{font-weight:600}th:first-child{min-width:120px}thead{background:var(--surface)}tbody tr:last-child>*{border-bottom:0}#audit-table td{min-width:225px}#audit-table td:nth-child(2){min-width:175px;overflow-wrap:anywhere}code{font-family:inherit;background:var(--surface);padding:.05em .15em}input{display:block;width:min(100%,560px);margin:8px 0 10px;padding:12px;border:1px solid var(--border);border-radius:5px;font:inherit;background:var(--surface);color:var(--ink)}.count{color:var(--muted)}details{margin:22px 0}summary{cursor:pointer;font-family:system-ui,sans-serif;font-weight:600}a:focus-visible,input:focus-visible,summary:focus-visible,.table-scroll:focus-visible{outline:3px solid var(--link);outline-offset:4px}.downloads{display:flex;gap:10px 22px;flex-wrap:wrap;line-height:1.8}.back{font-family:system-ui,sans-serif;font-size:.9rem}@media(max-width:600px){main{padding:22px 16px 60px}body{font-size:1rem}th,td{min-width:210px;padding:10px 12px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{body{background:#fff;color:#111}nav,.tools,.downloads{display:none}main{max-width:none;padding:0}.table-scroll{overflow:visible}th,td{min-width:0!important;font-size:9pt;padding:5px}a{color:inherit}}
</style></head><body><main>
<a class="back" href="../../blogs/telugu-metathesis">← What moved in Telugu metathesis?</a>
<header><p class="label">Jambu research supplement · 8 September 2026</p>
<h1>Telugu metathesis: evidence and audit</h1>
<p>Derivations, controls, unresolved comparisons, and proposed database repairs accompanying the essay.</p>
<p class="note">Written by Codex, an AI agent. Source judgments and reconstructed intermediates are identified as such. These are audit findings and proposed repairs; this investigation has not changed the lexical graph.</p>
<nav aria-label="Supplement sections"><a href="#casebook">Casebook</a><a href="#lowering">Kui–Kuvi audit</a><a href="#triage">116-group triage</a><a href="#audit">Reconstruction audit</a><a href="#sources">Sources</a><a href="#downloads">Downloads</a></nav></header>
<section id="casebook"><h2>Analytical casebook</h2><div class="prose">${markdown('casebook.md')}</div></section>
<section id="lowering"><h2>Kui–Kuvi vowel lowering</h2><div class="prose">${markdown('vowel-lowering-audit.md')}</div></section>
<section id="triage"><h2>All 116 initial-cluster groups</h2>
<p>Every spelling candidate received an initial comparative assessment. “Apical comparison” means the earlier consonant has support; it does not mean every vowel, formative, or loan relationship is solved. These are inspection groups, not 116 independent metatheses.</p>
<div class="tools"><label for="triage-search">Find a group, form, or issue</label><input id="triage-search" type="search" placeholder="For example: 1787, nasal, or secondary" autocomplete="off"><p id="triage-count" class="count" role="status">116 of 116 groups shown</p></div>${triage.html}</section>
<section id="audit"><h2>Reconstruction and source audit</h2><p>${audit.count} records or issues, including confirmed reference errors, lost qualifications, controls, and competing hypotheses. The final column distinguishes their evidential status.</p>${audit.html}</section>
<section id="sources"><h2>Sources and access record</h2><div class="prose">${markdown('bibliography.md')}</div></section>
<section id="downloads"><h2>Download the evidence</h2><p>UTF-8 files preserve source IDs and diacritics. The inventory summary pins the input data by SHA-256 checksums. Candidate and level-note flags are search aids, not error or borrowing labels.</p><div class="downloads">${downloads.map((name) => `<a href="${name}" download>${name}</a>`).join('')}</div></section>
</main><script>
const input=document.getElementById('triage-search');
const rows=Array.from(document.querySelectorAll('#triage-table tbody tr'));
input.addEventListener('input',()=>{const query=input.value.normalize('NFC').toLocaleLowerCase().trim();let visible=0;for(const row of rows){row.hidden=!row.textContent.normalize('NFC').toLocaleLowerCase().includes(query);if(!row.hidden)visible++;}document.getElementById('triage-count').textContent=visible+' of '+rows.length+' groups shown';});
</script></body></html>`;
writeFileSync(resolve(output, 'evidence.html'), html);
console.log(`Rendered ${triage.count} triage groups and ${audit.count} audit items to ${output}/evidence.html`);
