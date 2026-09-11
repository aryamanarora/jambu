"""Audit the final report and complete HTML appendices against frozen tables.

This does not make new linguistic judgments or verify remote availability.
Browser layout and interaction checks are recorded in presentation-qa.json.
"""
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import csv, json, os, re, shutil, subprocess, tempfile

HERE = Path(__file__).resolve().parent

def tsv(name):
    with (HERE / name).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def jsn(name):
    return json.loads((HERE / name).read_text())

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = []; self.links = []; self.scripts = []
        self.active_script = None; self.path = path
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag == 'script': self.active_script = [a, '']

    def handle_data(self, data):
        if self.active_script is not None: self.active_script[1] += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.active_script is not None:
            self.scripts.append(self.active_script); self.active_script = None

    def embedded(self):
        return next(json.loads(text) for attrs, text in self.scripts
                    if attrs.get('type') == 'application/json')

def main():
    pages = {p.resolve(): Page(p) for p in [HERE/'REPORT.html', *sorted((HERE/'appendices').glob('*.html'))]}
    checks = []; external = set(); local_links = 0
    def check(name, condition, evidence=None):
        assert condition, (name, evidence)
        checks.append(dict(check=name, status='passed', evidence=evidence))

    catalog = jsn('appendices/table-catalog.json')
    table_files = {x['file'] for x in catalog}
    families = {r['family_id'] for r in tsv('families.tsv')}
    for path, page in pages.items():
        check('unique HTML IDs: '+str(path.relative_to(HERE)), len(page.ids)==len(set(page.ids)))
        for href in page.links:
            u = urlsplit(href)
            if u.scheme or u.netloc:
                external.add(href); continue
            dest = (path.parent / unquote(u.path)).resolve() if u.path else path
            check('local link: '+str(path.relative_to(HERE))+' → '+href, dest.is_file())
            local_links += 1
            if u.fragment:
                fragment = unquote(u.fragment)
                valid = dest in pages and fragment in pages[dest].ids
                if dest == (HERE/'appendices/tables.html').resolve(): valid |= fragment in table_files
                if dest == (HERE/'appendices/index.html').resolve(): valid |= fragment.removeprefix('family-') in families
                check('local fragment: '+href, valid)

    explorer = pages[(HERE/'appendices/index.html').resolve()].embedded()
    check('embedded family inventory', len(explorer['families'])==1686)
    check('embedded token inventory', len(explorer['records'])==25593)
    check('embedded original record coverage', len({r['id'] for r in explorer['records']})==25505)
    check('embedded complete family identities', {r['family_id'] for r in explorer['families']}==families)
    check('embedded complete token identities', {r['analysis_token_id'] for r in explorer['records']}=={r['analysis_token_id'] for r in tsv('analysis-tokens.tsv')})
    tables = pages[(HERE/'appendices/tables.html').resolve()].embedded()
    check('table catalog complete', {t['file'] for t in tables}==table_files)
    for table in tables:
        check('embedded TSV equals export: '+table['file'], table['rows']==tsv(table['file']), len(table['rows']))
    definitions=tsv('class-definitions.tsv'); counterparts=tsv('class-counterparts-all-languages.tsv')
    class_summary=tsv('class-counterpart-outcome-summary.tsv')
    check('all 27 class definitions exported',len(definitions)==27)
    check('all seven languages in each class summary',len(class_summary)==189 and all({r['language'] for r in class_summary if r['class_id']==d['class_id']}==set(explorer['languages']) for d in definitions))
    for r in class_summary:
        rows=[x for x in counterparts if x['class_id']==r['class_id'] and x['language']==r['language']]
        has_records=sum(bool(json.loads(x['all_counterpart_tokens'])) for x in rows)
        check('counterpart availability: '+r['class_id']+' '+r['language'],has_records==int(r['families_or_members_with_counterpart_records']) and len(rows)-has_records==int(r['families_or_members_without_counterpart_records']))
        observed=Counter(o for x in rows for o in json.loads(x['outcomes']))
        check('counterpart outcome counts: '+r['class_id']+' '+r['language'],dict(observed)==json.loads(r['observed_counterpart_outcome_counts']))

    # Central report denominators must agree with the independent output tables.
    md = (HERE/'REPORT.md').read_text()
    n = lambda x: f'{int(x):,}'
    names = dict(Sh='Shina',Phal='Palula',Sv='Sauji',Kalk='Kalkoti',Kund='Kundal Shahi',bro='Brokskat',Ush='Ushojo')
    coverage = jsn('integrity-audit.json')['coverage']
    for r in coverage:
        row='| '+' | '.join([names[r['language']],n(r['raw_records']),n(r['research_linked']),n(r['research_families']),n(r['unlinked'])])+' |'
        check('report language census: '+r['language'], row in md, row)
    for r in tsv('old-long-screen.tsv'):
        if r['language'] not in ('Sh','Phal'): continue
        kind='barytone' if r['prediction']=='E' else 'oxytone'
        opposite='L' if r['prediction']=='E' else 'E'
        row=f"| Old long-root {kind} | {names[r['language']]} | {r['consistent']} {r['prediction']} | {r['conflicting']} | {r['opposite']} {opposite} | {r['scorable_families']} |"
        check('report broad old-long row: '+kind+' '+r['language'], row in md, row)
    restricted=tsv('old-long-nominal-sensitivity.tsv')
    degener=[r for r in restricted if r['scope']=='Degener-Gilgit-only']
    if not degener:
        degener=[r for r in restricted if 'degener' in r['scope'].lower() and 'alternative' not in r['scope'] and r['language']=='Sh']
    check('restricted Degener source result retained',any(r['consistent']=='7' for r in degener) and any(r['consistent']=='10' for r in degener))
    a=jsn('palula-tagged-u-summary.json'); g=jsn('gilgit-o-adjectives-summary.json'); u=jsn('palula-u-adjectives-summary.json')
    for name,row in [
      ('Palula POS adjectives',f"| Palula source-tagged short-*u* adjectives | {a['counts']['consistent']} | {a['counts']['exception']} | {a['counts']['unscorable']} unscorable | {a['unique_form_gloss_types']} unique form/gloss types |"),
      ('Gilgit adjectives',f"| Gilgit source-tagged short-*o* adjectives | {g['counts']['consistent']} | 0 | {g['counts']['unscorable']} unscorable | {g['unique_form_gloss_types']} unique form/gloss types |"),
      ('Palula grammatical adjectives',f"| Palula regular/umlaut *u : i* gender-inflecting types, including participles | {u['consistent']} | {u['exception']} | {u['unscorable']} unscorable | {u['unique_citation_types']} unique citation types |")]:
        check('report '+name,row in md,row)
    uml=[r for r in tsv('palula-umlaut-i-nouns.tsv') if r['status']=='consistent']
    ext=[r for r in tsv('palula-i-decl-extension.tsv') if r['status']=='consistent']
    lexemes={(r['gloss'],r['inflected']) for r in uml+ext}
    check('combined i-declension cells',len(uml)==73 and len(ext)==42 and len(uml+ext)==115)
    check('combined i-declension lexemes',len(lexemes)==95)
    check('all 115 inflections explicitly final-accented', all(r.get('inflected_position',r.get('inflected_accent_from_right'))=='1' for r in uml+ext))
    check('report combined i-declension result','**115/115 comparable inflected forms have final -í**' in md and '**95**, with one overlapping lexeme' in md)
    for r in tsv('dras-suffix-accent-summary.tsv'):
        s=json.loads(r['statuses']); label='Other formations' if r['suffix']=='other' else '*'+r['suffix']+'*'
        row='| '+' | '.join([label,*[str(s.get(k,0)) for k in ('final-accent-only','final-plus-other-accent','stem-accent-only','unmarked')],r['plural_citations']])+' |'
        check('report Dras suffix: '+r['suffix'],row in md,row)
    nr=tsv('numeral-series-tests.tsv')
    check('all numeral-series outcomes',len(nr)==20 and all(r['consistent']=='1' for r in nr))
    for r in tsv('kalkoti-palula-combined-summary.tsv'):
        st=json.loads(r['statuses'])
        if r['input_class']=='Palula-prefinal-accent-plus-short-final-vowel':
            row=f"| Prefinal accent + short unaccented final vowel | Final High / rising | {st['consistent']} | 0 | {st['unscorable']} | {st['excluded']} |"
        elif r['input_class']=='Palula-E-without-short-final-vowel':
            row=f"| Monosyllabic E without that ending | Zero High / default | {st['consistent']} | {st['residual']} final-High residuals | {st['unscorable']} | {st['excluded']} |"
        elif r['input_class']=='Palula-L-without-short-final-vowel':
            row=f"| Monosyllabic L without that ending | H1 / falling | {st['consistent']} | {st['Low-interaction']} Low interactions | {st['unscorable']} | {st['excluded']} |"
        else: continue
        check('report Kalkoti class: '+r['input_class'],row in md,row)
    check('consolidated residual explanations are nonempty',all(r['explanation'] for r in tsv('exception-ledger.tsv')))
    check('report preserves source-version caveat','9 January 2004 draft' in md and 'unretrieved final 2005' in md)
    check('report preserves review-level limits','11,851 remain at the unlinked-inventory' in md and '10,311 at family-context' in md)
    check('narrative has twelve sections',len(re.findall(r'^## ',md,re.M))==12)

    # Syntax-check only; no browser interaction or execution through Node.
    bundled=Path('/Users/aryamanarora/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
    node=os.environ.get('SHINAIC_NODE') or shutil.which('node') or (str(bundled) if bundled.exists() else None)
    check('Node available for script syntax check',bool(node))
    for path,page in pages.items():
        for attrs,script in page.scripts:
            if attrs.get('type')=='application/json':continue
            with tempfile.NamedTemporaryFile('w',suffix='.js') as f:
                f.write(script);f.flush()
                result=subprocess.run([node,'--check',f.name],capture_output=True,text=True)
                check('JavaScript syntax: '+str(path.relative_to(HERE)),result.returncode==0,result.stderr or None)
    result=dict(status='passed',checked_at=datetime.now(timezone.utc).isoformat(),html_files=len(pages),local_links=local_links,
                quantitative_tables=len(tables),checks=checks,external_source_links=sorted(external),
                limitation='External links are a provenance inventory, not a claim that every remote server was rechecked during presentation QA. Browser behavior is recorded separately.')
    (HERE/'presentation-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','html_files','local_links','quantitative_tables')}))
    print(len(checks),'presentation checks passed')

if __name__=='__main__':main()
