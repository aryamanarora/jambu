# Jambu (static)

A static, **GitHub Pages–hostable** rebuild of the [Jambu](https://arxiv.org/abs/2306.02514)
etymological dictionary of South Asian languages (23,131 entries / 290,071 reflexes / 615
languages / 194 references). No server, no Heroku — the browser queries the SQLite database
directly over HTTP Range requests.

## How it works

- **Data**: the raw `data.db` is published as a GitHub **release asset** on
  [`moli-mandala/data`](https://github.com/moli-mandala/data) (the source of truth; not
  git-tracked). CI downloads it, transforms it, and serves the result **same-origin** from the
  Pages deploy.
- **In-browser SQLite**: [`sql.js-httpvfs`](https://github.com/phiresky/sql.js-httpvfs) runs
  SQLite (WASM) in a Web Worker and fetches only the byte ranges each query touches, so the
  ~117 MB DB is never fully downloaded. Substring search uses an **FTS5 trigram** index.
- **Hybrid rendering** (SvelteKit + `adapter-static`):
  - **Prerendered** to static HTML for SEO/citability: home, the list pages, and every
    `/entries/[id]` (23k), `/languages/[id]` (615), `/references/[id]` (194) — each carries its
    headword, gloss, `<title>`, and meta so crawlers see content without JS.
  - **Client-rendered** from SQLite: the 290k `/reflexes/[id]`, language comparisons, and all
    filtered/sorted list views (served the `200.html` SPA fallback).

## Develop

```bash
npm install
npm run db:transform   # .dbwork/data.db  → .dbwork/jambu.db  (needs a raw data.db there)
npm run db:stage       # copy jambu.db → static/db/ (served at /db/jambu.db)
npm run dev
```

Get a raw `data.db` from the release (`curl -L <release-url> -o .dbwork/data.db`) before the
first `db:transform`.

For a fast production build while iterating, cap prerendering:

```bash
JAMBU_DB=.dbwork/jambu.db PRERENDER_LIMIT=50 npm run build && npm run preview
```

## Deploy

Push to `main` — `.github/workflows/deploy.yml` downloads the release DB, transforms + stages it,
runs the full build (all 23k entry pages), and deploys to Pages. **Before first deploy**, set the
two env vars at the top of that workflow:

- `BASE_PATH` — `''` for a custom domain / `<user>.github.io` root, or `/<repo>` for a project page.
- `SITE_URL` — your absolute origin (used for `sitemap.xml`).

Also enable **Settings → Pages → Source: GitHub Actions**.

## Scripts / layout

- `scripts/build_static_db.py` — drops unused tables, adds indexes + the FTS5 trigram index,
  writes precomputed `meta` counts, `VACUUM`s.
- `src/lib/db.ts` — sql.js-httpvfs worker (single-file "full" mode).
- `src/lib/query.ts` — the query layer (port of the old Flask `search.py` + entry grouping).
- `src/lib/server/db.ts` — build-time `better-sqlite3` access for prerendering.
- `src/routes/**` — the pages.

## Notes

- Single-file "full" mode is used deliberately: chunked/split mode's read-ahead can straddle a
  chunk boundary and fail on large scans, and its `maxReadSpeed` isn't configurable via the public
  API. One file sidesteps that; the 1 GB Pages site limit comfortably fits the ~117 MB DB.
- Text fields (`word`, `gloss`, `notes`) may contain hand-authored HTML and are rendered as such,
  matching the original site (trusted, curated content).
