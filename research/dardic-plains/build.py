"""Freeze the exploratory analysis, reconcile language votes, and draw blog figures.

Run with --refresh-snapshot once to copy the current analysis; otherwise uses frozen data.
Requires matplotlib. Does not edit or rebuild the lexical database.
"""
import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'static/research/dardic-plains'
ANALYSIS = ROOT.parent / 'data/stats/dardic-plains'
SOURCE_BASE = '/research/dardic-plains'
FEATURED = ['RAW', 'WOOL', 'MOUSTACHE', 'LONG', 'WATER', 'IRON']
INCLUDED = FEATURED + ['RIVER', 'UNRIPE', 'SOUR']


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    global OUT, ANALYSIS, SOURCE_BASE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-snapshot', action='store_true')
    parser.add_argument('--refresh-coordinates', action='store_true', help='Freeze current language representative coordinates separately from lexical evidence')
    parser.add_argument('--family-level', choices=['head', 'entry'], default='entry')
    args = parser.parse_args()
    if args.family_level == 'head':
        OUT = OUT / 'head'
        ANALYSIS = ANALYSIS.with_name('dardic-plains-head')
        SOURCE_BASE += '/head'
    OUT.mkdir(parents=True, exist_ok=True)
    if args.refresh_snapshot:
        payload = json.loads((ANALYSIS / 'results.json').read_text())
        payload['total_positive_contrasts'] = len(payload['results'])
        payload['results'] = [r for r in payload['results'] if r['concept'] in INCLUDED]
        (OUT / 'snapshot.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        write_csv(OUT / 'evidence.csv', [r for r in read(ANALYSIS / 'evidence.csv') if r['concept'] in INCLUDED])
        (OUT / 'all-concept-ranking.csv').write_bytes((ANALYSIS / 'ranking.csv').read_bytes())
        for name in ['analyze_concept_isoglosses.py']:
            (OUT / name).write_bytes((ROOT.parent / 'data' / name).read_bytes())
        (OUT / 'edges_util.py').write_bytes((ROOT.parent / 'data/edges_util.py').read_bytes())
    payload = json.loads((OUT / 'snapshot.json').read_text())
    if args.refresh_coordinates:
        language_path = Path(payload['settings']['cldf']) / 'languages.csv'
        write_csv(OUT / 'map-languages.csv', [r for r in read(language_path) if r['ID'] in payload['selected_languages']])
        (OUT / 'coordinate-provenance.json').write_text(json.dumps(dict(
            source='data/cldf/languages.csv', sha256=hashlib.sha256(language_path.read_bytes()).hexdigest(),
            matches_lexical_snapshot=hashlib.sha256(language_path.read_bytes()).hexdigest() == payload['inputs']['languages.csv'],
            note='Representative base-language coordinates, not elicitation localities. A shared-Glottocode unit uses the first located contributing language in catalogue order.'), indent=2) + '\n')
    results = {r['concept']: r for r in payload['results']}
    evidence = read(OUT / 'evidence.csv')
    buckets = defaultdict(lambda: defaultdict(set))
    names = defaultdict(set)
    for row in evidence:
        key = row['concept'], row['group']
        families = buckets[key][row['unit']]
        if row['family_id']:
            families.add(row['family_id'])
        names[row['unit']].add(row['language'])
    memberships, shares, chart_views, family_rows = [], [], [], []
    family_names = {r['family_id']: r['family'] or r['family_id'] for r in evidence if r['family_id']}
    categories = ['Dardic-associated family only', 'Plains-associated family only',
                  'Both focal families', 'One focal + other families',
                  'Other families only', 'No resolved family']
    for concept in INCLUDED:
        result = results[concept]
        a, b = result['dardic_family_id'], result['plains_family_id']
        chart_rows = []
        for group in ['dardic', 'plains']:
            units = buckets[concept, group]
            linked = sum(bool(f) for f in units.values())
            assert len(units) == result[group + '_observed']
            assert linked == result[group + '_linked']
            votes = defaultdict(float)
            counts = [0] * 6
            for unit, families in sorted(units.items()):
                for family in families:
                    votes[family] += 1 / len(families)
                category = (5 if not families else 0 if families == {a} else 1 if families == {b}
                            else 2 if {a, b} <= families else 3 if {a, b} & families else 4)
                counts[category] += 1
                memberships.append(dict(concept=concept, group=group, unit=unit,
                    languages='; '.join(sorted({e['language'] for e in evidence if e['concept'] == concept and e['group'] == group and e['unit'] == unit})), families=';'.join(sorted(families)),
                    category=categories[category],
                    unresolved_records=sum(e['concept'] == concept and e['group'] == group and e['unit'] == unit and e['status'] == 'unlinked' for e in evidence),
                    excluded_loan_records=sum(e['concept'] == concept and e['group'] == group and e['unit'] == unit and e['status'] == 'borrowed' for e in evidence)))
            expected = result[group + '_distribution']
            assert set(votes) == set(expected)
            for family, vote in votes.items():
                assert math.isclose(vote / linked, expected[family], abs_tol=1e-12)
                family_rows.append(dict(concept=concept, group=group, family_id=family,
                    family=family_names[family], fractional_votes=vote, share=vote/linked,
                    languages='; '.join(sorted({e['language'] for e in evidence if e['concept'] == concept and e['group'] == group and e['family_id'] == family}))))
            shares.append(dict(concept=concept, group=group, linked=linked, observed=len(units),
                dardic_family=result['dardic_family'], plains_family=result['plains_family'],
                dardic_family_share=votes[a] / linked, plains_family_share=votes[b] / linked,
                other_share=1 - (votes[a] + votes[b]) / linked))
            chart_rows.append(dict(label=group.title(), values=counts))
        chart_views.append(dict(label=concept, unit='Language units (one Glottocode = one unit)',
            note=f"Focal families: {result['dardic_family']} / {result['plains_family']}. These are integer language counts, not fractional family votes. ‘Only’ refers to resolved families; unlinked synonyms can coexist. ‘No resolved family’ includes units with only excluded loan paths. No attestation at all is outside this denominator.",
            categories=categories, rows=chart_rows))
    write_csv(OUT / 'language-memberships.csv', memberships)
    write_csv(OUT / 'weighted-shares.csv', shares)
    write_csv(OUT / 'family-distributions.csv', family_rows)
    write_csv(OUT / 'metric-comparison.csv', [dict(concept=c, rank=results[c]['rank'],
        old_rank=results[c]['legacy_rank'], score=results[c]['score'],
        old_score=results[c]['legacy_coverage_score'],
        dardic_positive_votes=results[c]['dardic_positive_votes'],
        plains_positive_votes=results[c]['plains_positive_votes']) for c in INCLUDED])
    # Full distributions in the essay keep named alternatives inspectable, not hidden in 'other'.
    details = ['<!-- family-distributions:start -->']
    for concept in INCLUDED:
        details += ['', '<details>', f'<summary>{concept.title()}: every resolved family</summary>', '',
                    '| Family | Dardic share | Plains share | Languages with linked evidence |',
                    '| --- | --- | --- | --- |']
        for family in sorted({r['family_id'] for r in family_rows if r['concept'] == concept}):
            rows = [r for r in family_rows if r['concept'] == concept and r['family_id'] == family]
            by_group = {r['group']: r for r in rows}
            label = family_names[family].replace('*', '\\*').replace('|', '\\|')
            shares_text = [f"{by_group[g]['share']:.1%}" if g in by_group else '0%' for g in ['dardic', 'plains']]
            langs = ' · '.join(f"{g.title()}: {by_group[g]['languages']}" for g in ['dardic', 'plains'] if g in by_group)
            details.append(f"| [{label}](entry:{family}) | {' | '.join(shares_text)} | {langs} |")
        details += ['', '</details>']
    details += ['', '<!-- family-distributions:end -->']
    post_path = ROOT / 'src/lib/blog/posts/dardic-plains-isoglosses.md'
    if post_path.exists() and args.family_level == 'entry':
        post = post_path.read_text()
        post = re.sub(r'<!-- family-distributions:start -->.*?<!-- family-distributions:end -->',
                      lambda _: '\n'.join(details), post, flags=re.S)
        post_path.write_text(post)
    chart = {'dardic-language-evidence': dict(id='dardic-language-evidence',
        title='What does each language actually contribute?', sourceBase=SOURCE_BASE,
        sources=['language-memberships.csv', 'family-distributions.csv', 'weighted-shares.csv', 'evidence.csv'], views=chart_views)}
    river = []
    for scope in ['Original concept mapping', 'Gloss begins with river / a river']:
        for group in ['dardic', 'plains']:
            units = defaultdict(set)
            for row in evidence:
                if row['concept'] != 'RIVER' or row['group'] != group:
                    continue
                if scope != 'Original concept mapping' and not re.match(r'^(?:a\s+)?river\b', row['gloss'].strip(), re.I):
                    continue
                families = units[row['unit']]
                if row['family_id']:
                    families.add(row['family_id'])
            linked = sum(bool(f) for f in units.values())
            votes = defaultdict(float)
            for families in units.values():
                for family in families:
                    votes[family] += 1 / len(families)
            river.append(dict(scope=scope, group=group, linked=linked, observed=len(units),
                              sindhu=votes['13415']/linked, nadi=votes['6943']/linked,
                              other=1-(votes['13415']+votes['6943'])/linked))
    write_csv(OUT / 'river-sensitivity.csv', river)
    def add_chart(cid, title, views, sources):
        chart[cid] = dict(id=cid, title=title, sourceBase=SOURCE_BASE, sources=sources, views=views)

    family_views, coverage_views = [], []
    for concept in INCLUDED:
        r = results[concept]
        rows = [row for row in shares if row['concept'] == concept]
        family_views.append(dict(label=concept, unit='Fractional language votes', fractionalVotes=True,
            note=f"Rank {r['rank']}; score {r['score']:.3f}. Positive focal-family votes: Dardic {r['dardic_positive_votes']:.2f}, Plains {r['plains_positive_votes']:.2f}. Unknowns do not reduce the score. Bars describe linked language units only; switch to Votes to see support, and use the coverage chart below for unknowns.",
            categories=[r['dardic_family'], r['plains_family'], 'Other resolved families'],
            rows=[dict(label=row['group'].title(), values=[row['dardic_family_share']*row['linked'],
                row['plains_family_share']*row['linked'], max(0, row['other_share']*row['linked'])]) for row in rows]))
        coverage_views.append(dict(label=concept, unit='Attested language units',
            note='A linked language has at least one included resolved family; it can still have unresolved synonyms. No included family also covers excluded loan paths. Languages without concept attestations are outside these totals. Unknowns are descriptive, not a score penalty.',
            categories=['At least one included family', 'No included family'],
            rows=[dict(label=row['group'].title(), values=[row['linked'], row['observed']-row['linked']]) for row in rows]))
    add_chart('dardic-family-shares', 'Which families occur on each side?', family_views,
              ['weighted-shares.csv', 'family-distributions.csv', 'metric-comparison.csv'])
    add_chart('dardic-coverage', 'Known and unknown evidence', coverage_views,
              ['language-memberships.csv', 'evidence.csv'])
    long_views = []
    for unknown in [False, True]:
        rows = [row for row in shares if row['concept'] == 'LONG']
        long_views.append(dict(label='All attested languages' if unknown else 'Linked languages only',
            unit='Fractional language votes' + (' plus unresolved-only language units' if unknown else ''), fractionalVotes=True,
            note='The family votes are identical in both views. All attested languages restores units with no included family to the denominator; it does not guess their etymology. Linked / attested: Dardic 20/22, Plains 41/71.',
            categories=['dīrgha family', 'lamba family', 'Other resolved families', 'No included family'],
            rows=[dict(label=row['group'].title(), values=[row['dardic_family_share']*row['linked'], row['plains_family_share']*row['linked'],
                  max(0, row['other_share']*row['linked']), row['observed']-row['linked'] if unknown else 0]) for row in rows]))
    add_chart('dardic-long-denominators', 'LONG: the split and the missing evidence', long_views, ['weighted-shares.csv'])
    river_views = []
    for scope in ['Original concept mapping', 'Gloss begins with river / a river']:
        rows = [row for row in river if row['scope'] == scope]
        river_views.append(dict(label=scope, unit='Fractional language votes', fractionalVotes=True,
            note='Linked / attested: ' + '; '.join(f"{row['group'].title()} {row['linked']}/{row['observed']}" for row in rows) + '. The case-insensitive gloss-start filter is a narrow diagnostic, not a completed semantic review or a reranking. Unknowns do not penalize the revised score.',
            categories=['sindhu family', 'nadī family', 'Other resolved families'],
            rows=[dict(label=row['group'].title(), values=[row['sindhu']*row['linked'], row['nadi']*row['linked'], max(0, row['other']*row['linked'])]) for row in rows]))
    add_chart('dardic-river-sensitivity', 'RIVER: a contrast obscured by the glosses', river_views, ['river-sensitivity.csv', 'evidence.csv'])
    attach_maps(chart, evidence, results)
    for item in chart.values():
        for view in item['views']:
            view['familyMode'] = args.family_level
    (OUT / 'charts.json').write_text(json.dumps(chart, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'src/lib/blog/data/dardic-plains-charts.json').write_text(json.dumps(chart, ensure_ascii=False, indent=2) + '\n')
    draw(results, shares, river)
    manifest = dict(input_hashes=payload['inputs'], evidence_rows=len(evidence),
        language_concept_units=len(memberships), featured_concepts=FEATURED,
        verified='All nine concepts independently recomputed from evidence; every family share and denominator matches the frozen analysis.',
        outputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'manifest.json'})
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'outputs'}, indent=2))


def attach_maps(charts, evidence, results, audit_name="map-points.csv"):
    languages = read(OUT / 'map-languages.csv')
    map_audit = []
    for cid, chart in charts.items():
        chart['sources'] += ['map-languages.csv', audit_name]
        for view in chart['views']:
            concept = 'LONG' if cid == 'dardic-long-denominators' else 'RIVER' if cid == 'dardic-river-sensitivity' else view['label']
            r = results[concept]
            a, b = r['dardic_family_id'], r['plains_family_id']
            scope = [e for e in evidence if e['concept'] == concept]
            if cid == 'dardic-river-sensitivity' and view['label'].startswith('Gloss'):
                scope = [e for e in scope if re.match(r'^(?:a\s+)?river\b', e['gloss'].strip(), re.I)]
            by_unit = defaultdict(list)
            for e in scope:
                by_unit[e['group'], e['unit']].append(e)
            categories = list(view['categories'])
            family_view = cid in {'dardic-family-shares', 'dardic-river-sensitivity', 'dardic-long-denominators'}
            asymmetric = cid == 'dardic-asymmetric'
            if asymmetric:
                family_view = True
            if (family_view and len(categories) == 3) or asymmetric:
                categories.append('No included family')
            points = []
            for (group, unit), records in sorted(by_unit.items()):
                families = {e['family_id']: e['family'] or e['family_id'] for e in records if e['family_id']}
                values = [0.] * len(categories)
                if family_view:
                    if families:
                        for family in families:
                            values[(0 if family == a else 1) if asymmetric else (0 if family == a else 1 if family == b else 2)] += 1 / len(families)
                    else:
                        values[-1] = 1
                elif cid == 'dardic-coverage':
                    values[0 if families else 1] = 1
                else:
                    fs = set(families)
                    category = (5 if not fs else 0 if fs == {a} else 1 if fs == {b}
                                else 2 if {a, b} <= fs else 3 if {a, b} & fs else 4)
                    values[category] = 1
                lids = {e['language_id'] for e in records}
                located = []
                for lang in languages:
                    if lang['ID'] not in lids:
                        continue
                    try:
                        lat, lon = float(lang['Latitude']), float(lang['Longitude'])
                        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                            continue
                    except ValueError:
                        continue
                    located.append((lang, lat, lon))
                location, lat, lon = located[0] if located else (None, None, None)
                examples, seen = [], set()
                for e in sorted(records, key=lambda e: (not bool(e['family_id']), e['language'], e['form_id'])):
                    key = (e['family_id'], e['status'])
                    if key in seen:
                        continue
                    seen.add(key)
                    examples.append(dict(id=e['form_id'], language=e['language'], form=e['form'], gloss=e['gloss'], status=e['status']))
                point = dict(id=unit, label=' / '.join(sorted({e['language'] for e in records})),
                    group=group.title(), latitude=lat, longitude=lon,
                    locationLabel=f"Representative location: {location['Name']} ({lat:.2f}, {lon:.2f}); shared-Glottocode unit." if location else 'No representative coordinates available; still included in the evidence.',
                    values=values, families=[dict(id=fid, label=name) for fid, name in sorted(families.items())],
                    unresolved=sum(e['status'] == 'unlinked' for e in records), loans=sum(e['status'] == 'borrowed' for e in records),
                    examples=examples[:6])
                points.append(point)
                map_audit.append(dict(chart=cid, view=view['label'], concept=concept, unit=unit,
                    group=group, latitude=lat, longitude=lon, representative_language=location['ID'] if location else '',
                    categories=json.dumps(categories, ensure_ascii=False), values=json.dumps(values),
                    families=';'.join(sorted(families))))
            # Reconcile located AND unlocated map units with bar denominators and votes.
            for row in view['rows']:
                ps = [p for p in points if p['group'] == row['label']]
                sums = [sum(p['values'][i] for p in ps) for i in range(len(categories))]
                if family_view and (cid != 'dardic-long-denominators' or view['label'] == 'Linked languages only'):
                    sums[-1] = 0  # Unknowns shown on map, explicitly excluded from these bars.
                assert all(math.isclose(x, y, abs_tol=1e-9) for x, y in zip(sums, row['values'])), (cid, view['label'], row['label'])
            view['map'] = dict(categories=categories, points=points,
                note='One point per attested language unit, including unknowns even when the bars use only linked units. Locations are language representatives, not survey sites or boundary claims. Shared-Glottocode varieties are combined; overlapping points can be inspected with the language selector.')
            if 'Other resolved families' in view['categories']:
                others = sorted({f['id']: f['label'] for p in points for f in p['families'] if f['id'] not in {a, b}}.items())
                view['otherFamilies'] = []
                for fid, name in others:
                    values, lang_labels = [], []
                    for row in view['rows']:
                        values.append(sum(1 / len(p['families']) for p in points
                                          if p['group'] == row['label'] and any(f['id'] == fid for f in p['families'])))
                        lang_labels.append('; '.join(sorted({e['language'] for e in scope if e['group'].title() == row['label'] and e['family_id'] == fid})))
                    view['otherFamilies'].append(dict(id=fid, label=name, values=values, languages=lang_labels))
                index = view['categories'].index('Other resolved families')
                for i, row in enumerate(view['rows']):
                    assert math.isclose(sum(f['values'][i] for f in view['otherFamilies']), row['values'][index], abs_tol=1e-9)
    write_csv(OUT / audit_name, map_audit)


def draw(results, shares, river):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    from matplotlib.lines import Line2D

    bg, ink, muted, teal, orange = '#fbf8f2', '#242b32', '#657078', '#137c80', '#c8653b'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
        'figure.facecolor': bg, 'axes.facecolor': bg, 'text.color': ink,
        'axes.labelcolor': muted, 'xtick.color': muted, 'ytick.color': ink,
        'svg.fonttype': 'none', 'savefig.facecolor': bg})

    def save(fig, name):
        fig.savefig(OUT / (name + '.svg'), bbox_inches='tight')
        fig.savefig(OUT / (name + '.png'), dpi=180, bbox_inches='tight')
        plt.close(fig)

    def clean(ax):
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(length=0)
        ax.set_axisbelow(True)

    fig, axes = plt.subplots(6, 1, figsize=(9, 12.5))
    fig.subplots_adjust(left=.26, right=.91, top=.82, bottom=.08, hspace=1.15)
    fig.text(.06, .97, 'Different words for the same idea', fontsize=23, weight='bold', va='top')
    fig.text(.06, .928, 'Family shares among languages with a resolved etymology', fontsize=12, color=muted)
    fig.legend(handles=[Line2D([], [], marker='o', color=teal, linestyle='', label='Dardic'),
                        Line2D([], [], marker='D', color=orange, linestyle='', label='Plains')],
               loc='upper left', bbox_to_anchor=(.05, .909), frameon=False, ncol=2)
    for ax, concept in zip(axes, FEATURED):
        r = results[concept]
        a, b = r['dardic_family_id'], r['plains_family_id']
        ax.set_title(concept.title(), loc='left', fontsize=14, weight='bold', pad=15)
        for y, family in [(1, a), (0, b)]:
            d, p = r['dardic_distribution'].get(family, 0), r['plains_distribution'].get(family, 0)
            ax.plot([d, p], [y, y], color='#c9c9c1', lw=3, zorder=1)
            for x, color, marker in [(d, teal, 'o'), (p, orange, 'D')]:
                ax.scatter(x, y, s=65, c=color, marker=marker, zorder=3)
                ax.annotate(f'{x:.0%}', (x, y), xytext=(0, 10), textcoords='offset points',
                            ha='center', fontsize=10, color=color, weight='bold')
        ax.set_yticks([1, 0], [r['dardic_family'], r['plains_family']])
        ax.set_xlim(-.03, 1.04)
        ax.set_ylim(-.45, 1.6)
        ax.set_xticks([0, .25, .5, .75, 1])
        ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        ax.grid(axis='x', color='#e3e1da')
        clean(ax)
    fig.text(.06, .023, 'One vote per language, split among its distinct families. Unresolved-only languages excluded here.\nJambu compiled snapshot · 11 September 2026 · Dardic and Plains are operational comparison groups.',
             fontsize=9, color=muted, linespacing=1.7)
    save(fig, 'family-contrasts')

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(left=.24, right=.87, top=.77, bottom=.17)
    fig.text(.06, .95, 'How much of the evidence is linked?', fontsize=21, weight='bold')
    fig.text(.06, .895, 'Languages with ≥1 resolved family / languages attested for the concept', fontsize=11, color=muted)
    for i, concept in enumerate(FEATURED):
        r = results[concept]
        for offset, group, color in [(.16, 'dardic', teal), (-.16, 'plains', orange)]:
            n, total = r[group + '_linked'], r[group + '_observed']
            ax.barh(5-i+offset, n/total, height=.26, color=color)
            ax.text(n/total+.02, 5-i+offset, f'{n}/{total}', va='center', fontsize=10, color=color)
    ax.set_yticks(range(6), [c.title() for c in FEATURED[::-1]])
    ax.set_xlim(0, 1.16)
    ax.set_xticks([0, .25, .5, .75, 1])
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.grid(axis='x', color='#e3e1da')
    clean(ax)
    fig.legend(handles=[Line2D([], [], lw=8, color=teal, label='Dardic'), Line2D([], [], lw=8, color=orange, label='Plains')],
               loc='upper left', bbox_to_anchor=(.05, .866), frameon=False, ncol=2)
    fig.text(.06, .04, 'Missing etymologies are unknown, not evidence for a different word.\nA language with one linked word can still have unresolved synonyms.', fontsize=10, color=muted)
    save(fig, 'coverage')

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5))
    fig.subplots_adjust(left=.17, right=.96, top=.77, bottom=.2, hspace=.85)
    fig.text(.06, .95, 'LONG: the split and the missing evidence', fontsize=20, weight='bold')
    fig.text(.06, .899, 'The same family votes, shown with two different denominators', fontsize=12, color=muted)
    colors = [teal, orange, '#788396', '#dedbd3']
    labels = ['dīrgha family', 'lamba family', 'Other linked families', 'No resolved family']
    for ax, include_unknown, title in zip(axes, [False, True], ['Among linked languages', 'Among all attested languages']):
        for y, group in [(1, 'dardic'), (0, 'plains')]:
            row = next(r for r in shares if r['concept'] == 'LONG' and r['group'] == group)
            scale = row['linked']/row['observed'] if include_unknown else 1
            vals = [row['dardic_family_share']*scale, row['plains_family_share']*scale,
                    row['other_share']*scale, 1-scale]
            left = 0
            for value, color in zip(vals, colors):
                ax.barh(y, value, left=left, height=.52, color=color)
                if value > .09:
                    ax.text(left+value/2, y, f'{value:.0%}', ha='center', va='center',
                            color=ink if color == colors[3] else 'white', fontsize=11, weight='bold')
                left += value
        ax.set_title(title, loc='left', fontsize=13, weight='bold', pad=12)
        ax.set_yticks([1, 0], ['Dardic', 'Plains'])
        ax.set_xlim(0, 1)
        ax.set_xticks([0, .25, .5, .75, 1])
        ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        clean(ax)
    fig.legend(handles=[Line2D([], [], lw=9, color=c, label=l) for c, l in zip(colors, labels)],
               loc='lower left', bbox_to_anchor=(.05, .055), frameon=False, ncol=2, fontsize=10)
    fig.text(.06, .023, 'Linked / attested: Dardic 20/22 · Plains 41/71. Family shares use fractional language votes.', fontsize=9, color=muted)
    save(fig, 'long-denominators')

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.8))
    fig.subplots_adjust(left=.18, right=.9, top=.75, bottom=.23, hspace=.95)
    fig.text(.06, .95, 'RIVER was there—below the shortlist', fontsize=21, weight='bold')
    fig.text(.06, .892, f"sindhu / nadī · Rank {results['RIVER']['rank']} with unknowns neutral · Previously {results['RIVER']['legacy_rank']}", fontsize=11, color=muted)
    for ax, scope in zip(axes, ['Original concept mapping', 'Gloss begins with river / a river']):
        for y, group in [(1, 'dardic'), (0, 'plains')]:
            row = next(r for r in river if r['scope'] == scope and r['group'] == group)
            left = 0
            for key, color in zip(['sindhu', 'nadi', 'other'], colors):
                value = row[key]
                ax.barh(y, value, left=left, height=.52, color=color)
                if value > .08:
                    ax.text(left+value/2, y, f'{value:.0%}', ha='center', va='center', color='white', weight='bold')
                left += value
            ax.text(1.02, y, f"{row['linked']}/{row['observed']}", va='center', fontsize=10, color=muted)
        ax.set_title(scope, loc='left', fontsize=13, weight='bold', pad=13)
        ax.set_yticks([1, 0], ['Dardic', 'Plains'])
        ax.set_xlim(0, 1)
        ax.set_xticks([0, .25, .5, .75, 1])
        ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        clean(ax)
    fig.legend(handles=[Line2D([], [], lw=9, color=c, label=l) for c, l in zip(colors, ['sindhu family', 'nadī family', 'Other linked families'])],
               loc='lower left', bbox_to_anchor=(.05, .09), frameon=False, ncol=3, fontsize=10)
    fig.text(.06, .027, 'Shares among linked languages; right labels show linked/attested units.\nThe gloss filter is deliberately narrow. It is a diagnostic, not a completed semantic reannotation.', fontsize=9, color=muted, linespacing=1.7)
    save(fig, 'river-sensitivity')


if __name__ == '__main__':
    main()
