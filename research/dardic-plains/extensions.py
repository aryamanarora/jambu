"""Four corpus analyses, frozen inputs, and variant-counting sensitivity (stdlib).

Run --freeze after generating both data-side head and entry analyses, then rerun
without flags to reproduce the extensions from their frozen input package.
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT.parent / 'data'
OUT = ROOT / 'static/research/dardic-plains'
FROZEN = ROOT / 'research/dardic-plains/inputs'
FEATURED = ['RAW', 'WOOL', 'MOUSTACHE', 'LONG', 'WATER', 'IRON', 'RIVER']
ERAS = ['Early-Vedic', 'Late-Vedic', 'Epic', 'Classical', 'Medieval']
AGE_LABELS = ERAS + ['Reconstructed only', 'Undated OIA', 'Other origin']
BANDS = ['Low: <0.2', 'Middle: 0.2–<0.4', 'Middle: 0.4–<0.6', 'High: ≥0.6']


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def save_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def band(score):
    return BANDS[0 if score < .2 else 1 if score < .4 else 2 if score < .6 else 3]


def dist(units):
    linked = [fs for fs in units.values() if fs]
    votes = defaultdict(float)
    for fs in linked:
        for fid in fs:
            votes[fid] += 1 / len(fs)
    return {fid: n / len(linked) for fid, n in votes.items()} if linked else {}, len(linked)


def pair(d, p):
    return max(((.5 * (d[a] - p.get(a, 0) + p[b] - d.get(b, 0)), a, b)
                for a in d for b in p if a != b), default=(0, '', ''), key=lambda x: (x[0], x[1], x[2]))


def unilateral(d, p, nd, target=5):
    return max(((max(0, share-p.get(a, 0)) * min(1, share*nd/target), a)
                for a, share in d.items()), default=(0, ''), key=lambda x: (x[0], x[1]))


def age(fid, mode, heads, family_map):
    ids = [fid] if mode == 'head' else [k for k in heads if family_map.get(k, k) == fid]
    rows = [heads[k] for k in ids if k in heads]
    oia = [r for r in rows if r['Language_ID'] in {'Indo-Aryan', 'Sk', 'IA', 'OIA', 'PIA'}]
    if not oia:
        return 'Other origin'
    attested = [r for r in oia if not r['Form'].startswith('*')]
    if not attested:
        return 'Reconstructed only'
    tags = {t for r in attested for t in r['Tags'].split()}
    return next((era for era in ERAS if era in tags), 'Undated OIA')


def freeze():
    FROZEN.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(DATA))
    from analyze_concept_isoglosses import entry_family_map
    from edges_util import load_edges
    cldf = Path(json.loads((DATA / 'stats/dardic-plains/results.json').read_text())['settings']['cldf'])
    forms = {r['ID']: r for r in read_csv(cldf / 'forms.csv')}
    family_map = entry_family_map(forms, load_edges(str(cldf / 'edges.csv')))
    needed = {k for k, v in family_map.items() if k != v} | {v for k, v in family_map.items() if k != v}
    for mode, folder in [('head', 'dardic-plains-head'), ('entry', 'dardic-plains')]:
        src = DATA / 'stats' / folder
        payload = json.loads((src / 'results.json').read_text())
        for name, digest in payload['inputs'].items():
            assert hashlib.sha256((cldf / name).read_bytes()).hexdigest() == digest, name
        (FROZEN / f'{mode}-results.json').write_text(json.dumps(payload, ensure_ascii=False))
        raw = (src / 'evidence.csv').read_bytes()
        (FROZEN / f'{mode}-evidence.csv.gz').write_bytes(gzip.compress(raw, mtime=0))
        needed |= {e['head_id'] for e in csv.DictReader(io.StringIO(raw.decode())) if e['head_id']}
    meta = {fid: {k: forms[fid][k] for k in ['ID', 'Language_ID', 'Form', 'Gloss', 'Tags']} for fid in needed}
    (FROZEN / 'head-metadata.json.gz').write_bytes(gzip.compress(json.dumps(meta, ensure_ascii=False).encode(), mtime=0))
    (FROZEN / 'entry-family-map.json').write_text(json.dumps({k: v for k, v in family_map.items() if k != v}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    for mode in ['entry', 'head']:
        (OUT / f'{mode}-full-evidence.csv.gz').write_bytes((FROZEN / f'{mode}-evidence.csv.gz').read_bytes())
    heads = json.loads(gzip.decompress((FROZEN / 'head-metadata.json.gz').read_bytes()))
    family_map = json.loads((FROZEN / 'entry-family-map.json').read_text())
    charts = json.loads((OUT / 'charts.json').read_text())
    head_charts = json.loads((OUT / 'head/charts.json').read_text())
    for cid in charts:
        charts[cid]['views'] += head_charts[cid]['views']
        charts[cid]['sources'] += ['head/' + f for f in head_charts[cid]['sources']]
        # Downloads explicitly identify each counting mode.
    for cid, title, sources in [
        ('dardic-age', 'When are the contrasted families first tagged?', ['age-pairs.csv']),
        ('dardic-age-order', 'Which side has the earlier tagged family?', ['age-pairs.csv']),
        ('dardic-score-bands', 'What makes a contrast weaker?', ['extension-concepts.csv', 'score-bands.csv']),
        ('dardic-northwest', 'Where do Sindhi and Lahnda line up?', ['northwest-alignment.csv']),
        ('dardic-asymmetric', 'Dardic unity without requiring Plains unity', ['asymmetric-ranking.csv', 'asymmetric-map-points.csv', 'head/asymmetric-map-points.csv', 'entry-full-evidence.csv.gz', 'head-full-evidence.csv.gz'])]:
        charts[cid] = dict(id=cid, title=title, sourceBase='/research/dardic-plains', sources=sources, views=[])
    age_rows, band_rows, nw_rows, asym_rows, concept_rows = [], [], [], [], []
    summaries = {}
    mode_results = {}
    for mode in ['entry', 'head']:
        payload = json.loads((FROZEN / f'{mode}-results.json').read_text())
        results = [r for r in payload['results'] if r['eligible']]
        mode_results[mode] = {r['concept']: r for r in results}
        evidence = list(csv.DictReader(io.StringIO(gzip.decompress((FROZEN / f'{mode}-evidence.csv.gz').read_bytes()).decode())))
        units = defaultdict(lambda: {'dardic': defaultdict(set), 'plains': defaultdict(set)})
        targets = defaultdict(lambda: defaultdict(set))
        for e in evidence:
            fs = units[e['concept']][e['group']][e['unit']]
            target_fs = targets[e['concept']][e['language_id']]
            if e['family_id']:
                fs.add(e['family_id'])
                target_fs.add(e['family_id'])
        for r in results:
            for group in ['dardic', 'plains']:
                d, n = dist(units[r['concept']][group])
                assert n == r[group + '_linked']
                assert all(math.isclose(v, r[group + '_distribution'][k], abs_tol=1e-10) for k, v in d.items())
        # One row per unique oriented family pair, assigned to its highest-scoring concept.
        unique = {}
        for r in results:
            unique.setdefault((r['dardic_family_id'], r['plains_family_id']), r)
        for (a, b), r in unique.items():
            da, pa = age(a, mode, heads, family_map), age(b, mode, heads, family_map)
            order = ('At least one undated' if da not in ERAS or pa not in ERAS else
                     'Dardic earlier' if ERAS.index(da) < ERAS.index(pa) else
                     'Plains earlier' if ERAS.index(pa) < ERAS.index(da) else 'Same tagged era')
            age_rows.append(dict(mode=mode, concept=r['concept'], score=r['score'], band=band(r['score']),
                dardic_family_id=a, plains_family_id=b, dardic_age=da, plains_age=pa, age_order=order))
        for label, subset in [('All eligible pairs', list(unique.values())), ('Score ≥0.4', [r for r in unique.values() if r['score'] >= .4])]:
            ids = {(r['dardic_family_id'], r['plains_family_id']) for r in subset}
            rows = [r for r in age_rows if r['mode'] == mode and (r['dardic_family_id'], r['plains_family_id']) in ids]
            charts['dardic-age']['views'].append(dict(label=label, familyMode=mode, unit='Distinct oriented family pairs',
                note='One observation per family pair, assigned to its highest-scoring concept; repeated concepts do not duplicate pairs. Earliest era among non-starred OIA member heads with tags. These are textual-attestation metadata, not dates of origin, transmission or the exact modern sense. Undated and reconstructed cases stay visible.',
                categories=AGE_LABELS, rows=[dict(label=g.title(), values=[sum(r[g+'_age']==era for r in rows) for era in AGE_LABELS]) for g in ['dardic','plains']]))
        categories = ['Dardic earlier', 'Same tagged era', 'Plains earlier', 'At least one undated']
        charts['dardic-age-order']['views'].append(dict(label='By score band', familyMode=mode, unit='Distinct oriented family pairs',
            note='Pairs are deduplicated across concepts, but different pairs can share a head. Differences are descriptive, not independent observations proving a causal effect of age. Bands use each pair’s highest concept score.',
            categories=categories, rows=[dict(label=b, values=[sum(r['mode']==mode and r['band']==b and r['age_order']==c for r in age_rows) for c in categories]) for b in BANDS]))
        # Exclusive diagnostic classes; support takes precedence over structure.
        diagnostics = ['Focal support below five votes', 'Supported, crossover >10 points', 'Supported, low crossover, weaker-side share <50%', 'Supported, low crossover, both shares ≥50%']
        for r in results:
            cross = r['dardic_cross'] + r['plains_cross']
            diag = diagnostics[0 if r['support_factor'] < 1-1e-10 else 1 if cross > .1+1e-10 else 2 if min(r['dardic_own'], r['plains_own']) < .5 else 3]
            concept_rows.append(dict(mode=mode, concept=r['concept'], score=r['score'], band=band(r['score']), diagnostic=diag,
                separation=r['separation'], support_factor=r['support_factor'], dardic_own=r['dardic_own'], plains_own=r['plains_own'],
                crossover=cross, dardic_family=r['dardic_family'], plains_family=r['plains_family']))
        for b in BANDS:
            rows = [r for r in concept_rows if r['mode']==mode and r['band']==b]
            band_rows.append(dict(mode=mode, band=b, concepts=len(rows), median_support=median(r['support_factor'] for r in rows),
                median_crossover=median(r['crossover'] for r in rows), median_dardic_share=median(r['dardic_own'] for r in rows),
                median_plains_share=median(r['plains_own'] for r in rows)))
        charts['dardic-score-bands']['views'].append(dict(label='All eligible concepts', familyMode=mode, unit='Concepts (related labels may reuse evidence)',
            note='Low <0.2; middle 0.2–<0.6; high ≥0.6. “Crossover” adds the opposite-side shares of the focal families, not a percentage of all languages. Support-limited cases are assigned first, making the four diagnostic classes mutually exclusive.', categories=diagnostics,
            rows=[dict(label=b, values=[sum(r['mode']==mode and r['band']==b and r['diagnostic']==c for r in concept_rows) for c in diagnostics]) for b in BANDS]))
        # Exact S and L, not all Sindhic and Lahndic; held-out sensitivity avoids target leakage.
        held_units = {payload['selected_languages'][lid]['unit'] for lid in ['S','L']}
        cohorts = [('Featured seven', [r for r in results if r['concept'] in FEATURED]),
                   ('Score ≥0.4', [r for r in results if r['score'] >= .4]),
                   ('Middle: 0.2–<0.6', [r for r in results if .2 <= r['score'] < .6]), ('All eligible', results)]
        cats = ['Dardic family, not Plains family', 'Plains family, not Dardic family', 'Both focal families', 'Other resolved families only', 'No included etymology', 'No attestation']
        for cohort, rs in cohorts:
            for held_out in [False, True]:
                case_rows, skipped = [], 0
                for r in rs:
                    a,b = r['dardic_family_id'],r['plains_family_id']
                    if held_out:
                        p,n = dist({u:fs for u,fs in units[r['concept']]['plains'].items() if u not in held_units})
                        sep,a,b = pair(r['dardic_distribution'],p)
                        if n < 5 or sep <= 0:
                            skipped += 1
                            continue
                    for target,lids in [('Sindhi',['S']),('Lahnda',['L']),('Either language',['S','L'])]:
                        observed = any(lid in targets[r['concept']] for lid in lids)
                        fs = set().union(*(targets[r['concept']].get(lid,set()) for lid in lids))
                        category = (5 if not observed else 4 if not fs else 2 if {a,b} <= fs else 0 if a in fs else 1 if b in fs else 3)
                        item = dict(mode=mode,cohort=cohort,held_out=held_out,concept=r['concept'],target=target,
                            dardic_family_id=a,plains_family_id=b,category=cats[category],families=';'.join(sorted(fs)))
                        nw_rows.append(item);case_rows.append(item)
                charts['dardic-northwest']['views'].append(dict(label=cohort+(' · held out' if held_out else ' · original pair'),familyMode=mode,
                    unit='Concepts per target (rows overlap)',note=f'Canonical Sindhi (S) and Lahnda (L) only. “Either language” pools presence, not independent observations. Unknowns and nonattestation stay separate. Focal pairs '+('reselected after removing both targets from Plains' if held_out else 'come from the main analysis, which includes the targets in Plains')+f'. {skipped} concepts lack a usable comparison after exclusions. A focal family can coexist with additional etyma.',categories=cats,
                    rows=[dict(label=t,values=[sum(r['target']==t and r['category']==c for r in case_rows) for c in cats]) for t in ['Sindhi','Lahnda','Either language']]))
        # Dardic-only support; no required dominant Plains B.
        asym = []
        for symmetric_rank, r in enumerate(results,1):
            d,p = r['dardic_distribution'],r['plains_distribution']
            score,a = unilateral(d,p,r['dardic_linked'])
            if score <= 0:
                continue
            asym.append(dict(mode=mode,concept=r['concept'],family_id=a,family=heads.get(a,{}).get('Form',a),score=score,
                symmetric_score=r['score'],symmetric_rank=symmetric_rank,dardic_share=d[a],plains_share=p.get(a,0),
                dardic_positive_votes=d[a]*r['dardic_linked'],plains_max_share=max(p.values()),
                plains_effective_families=1/sum(v*v for v in p.values())))
        asym.sort(key=lambda r:(-r['score'],r['concept']))
        for rank,r in enumerate(asym,1):
            r['rank']=rank;r['rank_gain']=r['symmetric_rank']-rank
        asym_rows += asym
        selected = asym[:12] + [r for r in sorted(asym,key=lambda r:-r['rank_gain']) if r['dardic_share']>=.7 and r['score']>=.4][:8]
        chosen = list({r['concept']:r for r in selected}.values())
        for r in chosen:
            source = next(s for s in results if s['concept']==r['concept'])
            charts['dardic-asymmetric']['views'].append(dict(label=r['concept'],familyMode=mode,unit='Fractional language votes',fractionalVotes=True,
                note=f"Family {r['family']}. One-sided rank {r['rank']} of {len(asym)} positive eligible cases; score {r['score']:.3f}. Symmetric rank {r['symmetric_rank']} among eligible cases. Dardic support {r['dardic_positive_votes']:.2f} votes. Plains has {r['plains_effective_families']:.2f} effective families (inverse concentration). No single opposing Plains etymon is required.",
                categories=[r['family'],'Other resolved families'],rows=[dict(label=g.title(),values=[source[g+'_distribution'].get(r['family_id'],0)*source[g+'_linked'],(1-source[g+'_distribution'].get(r['family_id'],0))*source[g+'_linked']]) for g in ['dardic','plains']]))
        import build
        build.OUT = OUT if mode == 'entry' else OUT / 'head'
        asym_chart = dict(charts['dardic-asymmetric'], views=[v for v in charts['dardic-asymmetric']['views'] if v['familyMode'] == mode], sources=[])
        map_results = {r['concept']: dict(mode_results[mode][r['concept']], dardic_family_id=r['family_id'], plains_family_id='') for r in chosen}
        build.attach_maps({'dardic-asymmetric': asym_chart}, evidence, map_results, 'asymmetric-map-points.csv')
        summaries[mode]=dict(eligible=len(results),unique_pairs=len(unique),age_order=dict(Counter(r['age_order'] for r in age_rows if r['mode']==mode)),
            high_age_order=dict(Counter(r['age_order'] for r in age_rows if r['mode']==mode and r['score']>=.4)),
            asym_top=asym[:20],asym_gainers=sorted(asym,key=lambda r:-r['rank_gain'])[:25],
            mid_examples=[r for r in concept_rows if r['mode']==mode and .2<=r['score']<.6][:50])
    for name,rows in [('age-pairs.csv',age_rows),('score-bands.csv',band_rows),('northwest-alignment.csv',nw_rows),('asymmetric-ranking.csv',asym_rows),('extension-concepts.csv',concept_rows)]:save_csv(name,rows)
    save_csv('family-collapse-audit.csv',[dict(head_id=k,family_id=v,head=heads.get(k,{}).get('Form',''),family=heads.get(v,{}).get('Form',''),rule='explicitly linked numbered CDIAL subhead') for k,v in sorted(family_map.items())])
    save_csv('head-age-metadata.csv',[dict(**r,entry_family_id=family_map.get(fid,fid)) for fid,r in sorted(heads.items())])
    (OUT/'extension-summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'src/lib/blog/data/dardic-plains-charts.json').write_text(json.dumps(charts,ensure_ascii=False,indent=2)+'\n')
    post_path = ROOT / 'src/lib/blog/posts/dardic-plains-isoglosses.md'
    post = post_path.read_text()
    intro = ['<!-- intro-comparisons:start -->', '', 'The seven comparisons discussed here, in descending score order. **Scores use collapsed entry families by default**; the last column shows the separate-headword sensitivity. These are selected examples, not the entire top-ranked list.', '', '| Concept | Dardic comparandum | Plains comparandum | Score | Separate heads |', '| --- | --- | --- | ---: | ---: |']
    for r in sorted((mode_results['entry'][c] for c in FEATURED), key=lambda r: -r['score']):
        a = r['dardic_family'].replace('*', r'\*')
        b = r['plains_family'].replace('*', r'\*')
        intro.append(f"| {r['concept']} | [{a}](entry:{r['dardic_family_id']}) | [{b}](entry:{r['plains_family_id']}) | {r['score']:.3f} | {mode_results['head'][r['concept']]['score']:.3f} |")
    intro += ['', 'Higher scores mean stronger supported separation among resolved language units. Unknown etymologies remain visible in the charts and do not count against a contrast. All viewers below offer both counting modes.', '', '<!-- intro-comparisons:end -->']
    block = '\n'.join(intro)
    if '<!-- intro-comparisons:start -->' in post:
        post = re.sub(r'<!-- intro-comparisons:start -->.*?<!-- intro-comparisons:end -->', lambda m: block, post, flags=re.S)
    else:
        first, rest = post.split('\n\n', 1)
        post = first + '\n\n' + block + '\n\n' + rest
    post_path.write_text(post)
    manifest = dict(inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FROZEN.iterdir()) if p.is_file()}, outputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name in ['age-pairs.csv','score-bands.csv','northwest-alignment.csv','asymmetric-ranking.csv','extension-concepts.csv','family-collapse-audit.csv','head-age-metadata.csv','extension-summary.json','asymmetric-map-points.csv']}, checks=['All eligible distributions reconstructed from evidence in both counting modes', 'Asymmetric map weights and other-family details reconcile to bars'], eligible={m: summaries[m]['eligible'] for m in summaries})
    (OUT / 'extension-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(summaries,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
