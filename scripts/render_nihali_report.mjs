import { readFile, writeFile } from 'node:fs/promises';
import { marked } from 'marked';

const reportDir = new URL('../../data/data/other/analysis/nihali-provisional/', import.meta.url);
const sourceUrl = new URL('REPORT.md', reportDir);
const outputUrl = new URL('REPORT.html', reportDir);

const source = await readFile(sourceUrl, 'utf8');
const titleMatch = source.match(/^#\s+(.+)$/m);
const title = titleMatch?.[1] ?? 'Provisional etymology of the Jambu Nihali lexicon';
const markdownBody = source.replace(/^#\s+.+\n+/, '');

marked.setOptions({
  gfm: true,
  breaks: false,
});

const escapeHtml = (value) => value
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

const stripHtml = (value) => value
  .replace(/<[^>]+>/g, '')
  .replaceAll('&amp;', '&')
  .replaceAll('&quot;', '"')
  .replaceAll('&#39;', "'");

const seenSlugs = new Map();
const headings = [];
const slugify = (label) => {
  const base = label
    .normalize('NFKD')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'section';
  const count = seenSlugs.get(base) ?? 0;
  seenSlugs.set(base, count + 1);
  return count ? `${base}-${count + 1}` : base;
};

let article = marked.parse(markdownBody);
article = article.replace(/<h([23])>([\s\S]*?)<\/h\1>/g, (_match, level, inner) => {
  const label = stripHtml(inner);
  const id = slugify(label);
  headings.push({ level: Number(level), label, id });
  return `<h${level} id="${id}"><a class="heading-anchor" href="#${id}" aria-label="Link to ${escapeHtml(label)}">#</a>${inner}</h${level}>`;
});

article = article.replace(
  /<code>(nihali-[a-z0-9-]+\.csv)<\/code>/g,
  '<a class="audit-link" href="./$1"><code>$1</code></a>',
);

const toc = headings.map(({ level, label, id }) => (
  `<a class="toc-link level-${level}" href="#${id}">${escapeHtml(label)}</a>`
)).join('\n');

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A complete provisional etymological audit of 4,299 Nihali records in Jambu and an evidence-weighted hypothesis of Nihali's linguistic origin.">
  <meta name="color-scheme" content="light dark">
  <title>${escapeHtml(title)} · Jambu Research Report</title>
  <style>
    :root {
      --paper: #f4efe4;
      --paper-raised: #fffaf0;
      --paper-muted: #e9e1d2;
      --ink: #20241f;
      --ink-soft: #5e6259;
      --rule: #d1c5b3;
      --accent: #9a3e25;
      --accent-2: #42604b;
      --accent-3: #d49a2f;
      --indigo: #4c536f;
      --shadow: 0 18px 45px rgb(48 38 24 / 10%);
      --serif: Iowan Old Style, Palatino Linotype, Book Antiqua, Palatino, Georgia, serif;
      --sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color-scheme: light;
    }

    html[data-theme="dark"] {
      --paper: #1d211d;
      --paper-raised: #252a24;
      --paper-muted: #30362e;
      --ink: #eee8db;
      --ink-soft: #b8b7ad;
      --rule: #454a41;
      --accent: #ef9274;
      --accent-2: #9bbda3;
      --accent-3: #edbd63;
      --indigo: #aeb5d6;
      --shadow: 0 18px 45px rgb(0 0 0 / 24%);
      color-scheme: dark;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; scroll-padding-top: 5rem; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(90deg, transparent 0 49.9%, rgb(154 62 37 / 3%) 50%, transparent 50.1%),
        var(--paper);
      font-family: var(--serif);
      font-size: 17px;
      line-height: 1.72;
      transition: color 180ms ease, background-color 180ms ease;
    }
    a { color: var(--accent); text-underline-offset: .16em; }
    a:hover { text-decoration-thickness: 2px; }
    button, select { font: inherit; }

    .progress {
      position: fixed;
      inset: 0 auto auto 0;
      z-index: 20;
      width: 0;
      height: 3px;
      background: var(--accent);
    }

    .masthead {
      color: #fffaf0;
      background: #26352b;
      border-bottom: 5px solid #d49a2f;
    }
    .masthead-inner {
      width: min(1180px, calc(100% - 2rem));
      margin: 0 auto;
      padding: 4.5rem 0 3.8rem;
    }
    .eyebrow {
      margin: 0 0 1.1rem;
      color: #edbd63;
      font: 700 .76rem/1.2 var(--sans);
      letter-spacing: .15em;
      text-transform: uppercase;
    }
    h1 {
      max-width: 880px;
      margin: 0;
      font: 500 clamp(2.55rem, 6vw, 5.3rem)/.98 var(--serif);
      letter-spacing: -.045em;
    }
    .dek {
      max-width: 760px;
      margin: 1.55rem 0 0;
      color: #d9ddcf;
      font-size: clamp(1.05rem, 2vw, 1.3rem);
      line-height: 1.5;
    }
    .meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: .6rem 1.6rem;
      margin-top: 2rem;
      color: #bfc8ba;
      font: 600 .78rem/1.5 var(--sans);
      letter-spacing: .04em;
    }

    .toolbar {
      position: sticky;
      top: 0;
      z-index: 15;
      border-bottom: 1px solid var(--rule);
      background: color-mix(in srgb, var(--paper) 92%, transparent);
      backdrop-filter: blur(14px);
    }
    .toolbar-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: min(1180px, calc(100% - 2rem));
      min-height: 3.45rem;
      margin: 0 auto;
      gap: 1rem;
    }
    .toolbar-title {
      overflow: hidden;
      color: var(--ink-soft);
      font: 700 .72rem/1 var(--sans);
      letter-spacing: .12em;
      text-overflow: ellipsis;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .toolbar-actions { display: flex; gap: .45rem; }
    .button {
      min-height: 2.15rem;
      padding: .35rem .7rem;
      color: var(--ink);
      background: var(--paper-raised);
      border: 1px solid var(--rule);
      border-radius: 999px;
      cursor: pointer;
      font: 700 .74rem/1 var(--sans);
      text-decoration: none;
    }
    .button:hover { border-color: var(--accent); }

    .overview {
      width: min(1180px, calc(100% - 2rem));
      margin: 2.2rem auto 2.8rem;
    }
    .thesis {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(240px, .65fr);
      gap: 2rem;
      padding: clamp(1.5rem, 4vw, 2.8rem);
      background: var(--paper-raised);
      border: 1px solid var(--rule);
      border-top: 5px solid var(--accent);
      box-shadow: var(--shadow);
    }
    .thesis-label {
      margin: 0 0 .65rem;
      color: var(--accent);
      font: 800 .73rem/1.2 var(--sans);
      letter-spacing: .14em;
      text-transform: uppercase;
    }
    .thesis h2 {
      margin: 0;
      font: 500 clamp(1.55rem, 3vw, 2.35rem)/1.18 var(--serif);
      letter-spacing: -.025em;
    }
    .thesis p { margin: .85rem 0 0; color: var(--ink-soft); }
    .verdict {
      align-self: stretch;
      padding: 1.2rem 1.3rem;
      background: var(--paper-muted);
      border-left: 3px solid var(--accent-3);
    }
    .verdict strong {
      display: block;
      margin-bottom: .4rem;
      color: var(--accent-2);
      font: 800 .78rem/1.2 var(--sans);
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .verdict p { margin: 0; font-size: .96rem; line-height: 1.55; }

    .metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      margin-top: 1px;
      background: var(--rule);
      border: 1px solid var(--rule);
    }
    .metric { padding: 1.25rem 1.35rem; background: var(--paper-raised); }
    .metric-value { display: block; font: 600 2rem/1 var(--serif); letter-spacing: -.03em; }
    .metric-label { display: block; margin-top: .45rem; color: var(--ink-soft); font: 650 .72rem/1.35 var(--sans); text-transform: uppercase; letter-spacing: .08em; }

    .composition { padding: 1.35rem; background: var(--paper-raised); border: 1px solid var(--rule); border-top: 0; }
    .composition h2 { margin: 0 0 .8rem; font: 750 .78rem/1.2 var(--sans); letter-spacing: .1em; text-transform: uppercase; }
    .bar { display: flex; height: 1.15rem; overflow: hidden; border-radius: 2px; background: var(--paper-muted); }
    .bar span { min-width: 2px; }
    .bar .residue { width: 34.6%; background: var(--accent); }
    .bar .ia { width: 28.5%; background: var(--accent-3); }
    .bar .korku { width: 17.9%; background: var(--accent-2); }
    .bar .mixed { width: 9.6%; background: var(--indigo); }
    .bar .other { width: 9.4%; background: var(--rule); }
    .legend { display: flex; flex-wrap: wrap; gap: .45rem 1.15rem; margin-top: .85rem; color: var(--ink-soft); font: 600 .76rem/1.4 var(--sans); }
    .legend span::before { content: ''; display: inline-block; width: .65rem; height: .65rem; margin-right: .4rem; border-radius: 50%; background: var(--key); }

    .report-grid {
      display: grid;
      grid-template-columns: 245px minmax(0, 820px);
      gap: clamp(2rem, 6vw, 5.5rem);
      justify-content: center;
      width: min(1180px, calc(100% - 2rem));
      margin: 0 auto;
      padding-bottom: 7rem;
    }
    .toc { position: sticky; top: 5rem; align-self: start; max-height: calc(100vh - 7rem); overflow: auto; padding: 1rem 0 1.5rem; }
    .toc-title { margin: 0 0 .65rem; color: var(--ink-soft); font: 800 .7rem/1.2 var(--sans); letter-spacing: .14em; text-transform: uppercase; }
    .toc-link { display: block; padding: .34rem .65rem; color: var(--ink-soft); border-left: 2px solid var(--rule); font: 600 .78rem/1.35 var(--sans); text-decoration: none; }
    .toc-link.level-3 { padding-left: 1.25rem; font-size: .72rem; }
    .toc-link:hover, .toc-link.active { color: var(--accent); border-left-color: var(--accent); background: color-mix(in srgb, var(--accent) 7%, transparent); }

    article { min-width: 0; }
    article h2, article h3 { position: relative; scroll-margin-top: 5rem; color: var(--ink); }
    article h2 { margin: 4.1rem 0 1.2rem; padding-top: .6rem; border-top: 1px solid var(--rule); font: 600 clamp(1.8rem, 4vw, 2.55rem)/1.15 var(--serif); letter-spacing: -.035em; }
    article h2:first-child { margin-top: 0; }
    article h3 { margin: 2.8rem 0 .8rem; font: 700 1.25rem/1.25 var(--sans); letter-spacing: -.015em; }
    .heading-anchor { position: absolute; right: 100%; padding-right: .5rem; color: var(--rule); text-decoration: none; opacity: 0; }
    article h2:hover .heading-anchor, article h3:hover .heading-anchor { opacity: 1; }
    article p { margin: 0 0 1.2rem; }
    article strong { color: color-mix(in srgb, var(--ink) 82%, var(--accent)); }
    article ul, article ol { padding-left: 1.3rem; }
    article li { margin: .4rem 0; }
    article blockquote { margin: 1.8rem 0; padding: .9rem 1.3rem; color: var(--ink-soft); background: var(--paper-raised); border-left: 4px solid var(--accent-3); }
    article code { padding: .12em .32em; font: 600 .78em/1.35 ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--paper-muted); border-radius: 3px; }
    .audit-link { text-decoration-color: color-mix(in srgb, var(--accent) 45%, transparent); }

    .table-wrap { width: 100%; margin: 1.35rem 0 2rem; overflow-x: auto; border: 1px solid var(--rule); background: var(--paper-raised); box-shadow: 0 7px 18px rgb(48 38 24 / 5%); }
    table { width: 100%; min-width: 560px; border-collapse: collapse; font: 500 .79rem/1.38 var(--sans); font-variant-numeric: tabular-nums; }
    th { padding: .75rem .8rem; color: var(--ink); background: var(--paper-muted); border-bottom: 1px solid var(--rule); text-align: left; vertical-align: bottom; }
    td { padding: .66rem .8rem; border-bottom: 1px solid color-mix(in srgb, var(--rule) 65%, transparent); vertical-align: top; }
    tbody tr:last-child td { border-bottom: 0; }
    tbody tr:hover td { background: color-mix(in srgb, var(--accent-3) 7%, transparent); }
    th[align="right"], td[align="right"] { text-align: right; }

    .report-footer { padding: 2rem 1rem 3rem; color: var(--ink-soft); background: var(--paper-muted); border-top: 1px solid var(--rule); text-align: center; font: 600 .76rem/1.6 var(--sans); }
    .report-footer a { margin: 0 .45rem; }

    @media (max-width: 860px) {
      .thesis { grid-template-columns: 1fr; }
      .metrics { grid-template-columns: repeat(2, 1fr); }
      .report-grid { grid-template-columns: 1fr; }
      .toc { position: static; max-height: 17rem; padding: 1rem; background: var(--paper-raised); border: 1px solid var(--rule); }
      .toc-links { columns: 2; }
      .toc-link { break-inside: avoid; }
    }
    @media (max-width: 560px) {
      body { font-size: 16px; }
      .masthead-inner { padding: 3rem 0 2.8rem; }
      .toolbar-title { display: none; }
      .toolbar-inner { justify-content: flex-end; }
      .metrics { grid-template-columns: 1fr 1fr; }
      .toc-links { columns: 1; }
      .heading-anchor { display: none; }
    }
    @media print {
      :root { --paper: #fff; --paper-raised: #fff; --paper-muted: #f3f0e9; --ink: #111; --ink-soft: #444; --rule: #bbb; }
      body { font-size: 10.5pt; background: #fff; }
      .toolbar, .toc, .progress { display: none !important; }
      .masthead { color: #111; background: #fff; border-bottom: 2px solid #111; }
      .masthead-inner { padding: 1cm 0; }
      .eyebrow, .dek, .meta-row { color: #333; }
      .overview { margin-top: 1cm; }
      .thesis { box-shadow: none; }
      .report-grid { display: block; width: 100%; padding: 0; }
      article h2 { break-after: avoid; }
      table { font-size: 8pt; }
      .table-wrap { overflow: visible; box-shadow: none; break-inside: avoid; }
      a { color: inherit; text-decoration: none; }
      .report-footer { display: none; }
    }
  </style>
</head>
<body>
  <div class="progress" aria-hidden="true"></div>
  <header class="masthead">
    <div class="masthead-inner">
      <p class="eyebrow">Jambu · Historical linguistics research report</p>
      <h1>${escapeHtml(title)}</h1>
      <p class="dek">A complete, evidence-tiered audit of the database lexicon—and a deliberately provisional account of what its contact layers imply about Nihali’s origin.</p>
      <div class="meta-row"><span>4,299 records</span><span>3,277 lexeme clusters</span><span>Five lexical sources</span><span>1 September 2026</span></div>
    </div>
  </header>

  <nav class="toolbar" aria-label="Report tools">
    <div class="toolbar-inner">
      <span class="toolbar-title">Nihali provisional etymology</span>
      <div class="toolbar-actions">
        <a class="button" href="./REPORT.md" download>Markdown</a>
        <button class="button" type="button" data-print>Print / PDF</button>
        <button class="button" type="button" data-theme-toggle aria-label="Switch color theme">Dark mode</button>
      </div>
    </div>
  </nav>

  <section class="overview" aria-labelledby="headline-finding">
    <div class="thesis">
      <div>
        <p class="thesis-label">Headline finding</p>
        <h2 id="headline-finding">An independent Central Indian lineage, transformed by layered relexification</h2>
        <p>Indo-Aryan is the widest attribution; Korku/Munda is the most historically diagnostic contact route; Dravidian is smaller but real. The independent residue is stable, but remains a diagnosis by exclusion rather than a reconstructed family.</p>
      </div>
      <aside class="verdict">
        <strong>Confidence: moderate</strong>
        <p>Munda descent remains the strongest competing account. It requires regular inherited correspondences and morphological reconstruction that the present lexical database cannot yet supply.</p>
      </aside>
    </div>
    <div class="metrics" aria-label="Key report figures">
      <div class="metric"><span class="metric-value">65.4%</span><span class="metric-label">Clusters with external attribution</span></div>
      <div class="metric"><span class="metric-value">34.6%</span><span class="metric-label">Strict Nihali residue</span></div>
      <div class="metric"><span class="metric-value">56</span><span class="metric-label">Effective core residue roots</span></div>
      <div class="metric"><span class="metric-value">39 / 91</span><span class="metric-label">Core concepts retaining residue</span></div>
    </div>
    <div class="composition">
      <h2>Lexeme-cluster composition</h2>
      <div class="bar" role="img" aria-label="Nihali residue 34.6 percent, Indo-Aryan 28.5 percent, Korku 17.9 percent, Korku plus Indo-Aryan 9.6 percent, other strata 9.4 percent">
        <span class="residue"></span><span class="ia"></span><span class="korku"></span><span class="mixed"></span><span class="other"></span>
      </div>
      <div class="legend">
        <span style="--key: var(--accent)">Residue 34.6%</span>
        <span style="--key: var(--accent-3)">Indo-Aryan 28.5%</span>
        <span style="--key: var(--accent-2)">Korku 17.9%</span>
        <span style="--key: var(--indigo)">Korku + Indo-Aryan 9.6%</span>
        <span style="--key: var(--rule)">Other strata 9.4%</span>
      </div>
    </div>
  </section>

  <main class="report-grid">
    <aside class="toc" aria-label="Report contents">
      <p class="toc-title">Contents</p>
      <div class="toc-links">${toc}</div>
    </aside>
    <article>${article}</article>
  </main>

  <footer class="report-footer">
    Generated from the reproducible Jambu Nihali audit.
    <a href="./REPORT.md">Source Markdown</a>
    <a href="../../../../tmp/pdfs/nihali/kuiper-nahali-1962.pdf">Kuiper 1962 source PDF</a>
  </footer>

  <script>
    document.querySelectorAll('table').forEach((table) => {
      const wrapper = document.createElement('div');
      wrapper.className = 'table-wrap';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    });

    const root = document.documentElement;
    const themeButton = document.querySelector('[data-theme-toggle]');
    const savedTheme = localStorage.getItem('nihali-report-theme');
    const preferredDark = matchMedia('(prefers-color-scheme: dark)').matches;
    if (savedTheme === 'dark' || (!savedTheme && preferredDark)) root.dataset.theme = 'dark';
    const updateThemeLabel = () => { themeButton.textContent = root.dataset.theme === 'dark' ? 'Light mode' : 'Dark mode'; };
    updateThemeLabel();
    themeButton.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('nihali-report-theme', root.dataset.theme);
      updateThemeLabel();
    });
    document.querySelector('[data-print]').addEventListener('click', () => window.print());

    const progress = document.querySelector('.progress');
    const updateProgress = () => {
      const available = document.documentElement.scrollHeight - innerHeight;
      progress.style.width = (available > 0 ? scrollY / available * 100 : 0) + '%';
    };
    addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();

    const links = [...document.querySelectorAll('.toc-link')];
    const byId = new Map(links.map((link) => [link.hash.slice(1), link]));
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach((link) => link.classList.remove('active'));
        byId.get(entry.target.id)?.classList.add('active');
      }
    }, { rootMargin: '-18% 0px -70% 0px' });
    document.querySelectorAll('article h2, article h3').forEach((heading) => observer.observe(heading));
  </script>
</body>
</html>`;

await writeFile(outputUrl, html);
console.log(`Rendered ${outputUrl.pathname} (${html.length.toLocaleString()} characters)`);
