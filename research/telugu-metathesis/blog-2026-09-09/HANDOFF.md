# Completed blog preparation — 9 September 2026

The approved six claims are implemented at `/blogs/telugu-metathesis`, with six
interactive stacked-bar charts, six ten-family annotated example tables, precise
citations, linked dictionary records, explicit exceptions and public data downloads.
The site identifies Codex as the author; outline approval was not treated as a named
human review of the finished prose. No deployment or database ingestion was performed.

Source: `src/lib/blog/posts/telugu-metathesis.md` (generated from `post.md.in` here).
Metadata: `src/lib/blog/index.ts`. Chart JSON: `src/lib/blog/data/telugu-metathesis-charts.json`.
Public evidence: `static/research/telugu-metathesis/`.

Checks completed:

- `verify.py`: six charts, 4,454 family memberships, sixty examples, ten distinct
  primary families per section; every chart aggregate independently recounted.
- `node --test tests/blog.test.mjs`: six tests passed.
- `npm run check`: zero errors; seven existing warnings in five unrelated files.
- Frozen research manifest: all 199 files unchanged.
- Development browser checks: all 155 distinct record destinations resolved in
  SSR; three representative destination pages fetched successfully; live dictionary
  hover preview worked; all four prose download destinations returned valid files.
- Compiled static preview: six claim headings, six interactive charts, exactly ten
  example rows per claim, working controls and hover preview, accessible sideways
  table scrolling, no document overflow at 390px, light/dark display, and full
  article/table/chart readability without JavaScript. No page errors.
- `git diff --check`: passed.

Static-build scope: the full application compiled successfully with `BASE_PATH=/jambu`.
Prerender was focused on the blog section in a disposable copy at
`/private/tmp/jambu-telugu-blog-build-20260909`; four blog pages and fifty baseline
entry pages were emitted. `prepare-build.py` documents the temporary configuration.
An earlier full crawl was intentionally interrupted after it began traversing
unrelated dictionary pages. The repository's deployment configuration was not changed.

The compiled preview is served from tmux window `telugu-blog-build` at
`http://127.0.0.1:5188/jambu/blogs/telugu-metathesis`. The development preview remains
at port 5187. Both use the existing Telugu research tmux socket.

Research qualifications are part of the article: selected denominators are not
language-wide frequencies; 41/117 paired witnesses measure evidence availability,
not consonant-loss incidence; mixed forms and morphological differences are retained;
the eight quantity exceptions receive individual attempted explanations; shared
outcomes do not alone establish inheritance or contact; uncertainty is not silently
recoded as retention. Source-only observations remain distinguishable in the archive.
