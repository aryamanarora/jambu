# Jambu (static)

A static, **GitHub Pages–hostable** rebuild of the [Jambu](https://arxiv.org/abs/2306.02514)
etymological dictionary of South Asian languages (29,362 entries / 290,267 reflexes / 409 base
languages / 523 references in the 2026-09-08 build). No server, no Heroku — the browser queries
a local SQLite database restored from a compact release artifact.

## How it works

- **Data**: the source CLDF lives in [`moli-mandala/data`](https://github.com/moli-mandala/data).
  The compiled `jambu.db` is published as a GitHub release asset on
  [`aryamanarora/jambu`](https://github.com/aryamanarora/jambu). CI downloads it for prerendering
  and serves a compressed copy from the Pages deploy.
- **In-browser SQLite**: SQLite (WASM) runs in a Web Worker. A 43.00 MB Zstandard artifact is
  downloaded once, restored losslessly to the 97.04 MB query-optimized SQLite image, and cached
  privately in OPFS. Substring search scans its compact lemma table directly.
- **Hybrid rendering** (SvelteKit + `adapter-static`):
  - **Prerendered** to static HTML for SEO/citability: home, the list pages, and every
    `/entries/[id]` (26k), `/languages/[id]` (344), `/references/[id]` (392) — each carries its
    headword, gloss, `<title>`, and meta so crawlers see content without JS.
  - **Client-rendered** from SQLite: the 275k `/reflexes/[id]`, language comparisons, and all
    filtered/sorted list views (served the `404.html` SPA fallback).

## Develop

```bash
npm install
npm run db:transform   # ../data/cldf → .dbwork/jambu.db
npm run db:stage       # zstd → static/db/jambu.db.zst (must remain below 50 MB)
npm run dev
```

`db:stage` requires the `zstd` command (`brew install zstd` or `apt install zstd`).

For a fast production build while iterating, cap prerendering:

```bash
JAMBU_DB=.dbwork/jambu.db PRERENDER_LIMIT=50 npm run build && npm run preview
```

## Deploy

Push to `main` — `.github/workflows/deploy.yml` downloads the release DB as a temporary prerender
input, packs it, runs the full build, and deploys only the packed artifact to Pages.
**Before first deploy**, set the two env vars at the top of that workflow:

- `BASE_PATH` — `''` for a custom domain / `<user>.github.io` root, or `/<repo>` for a project page.
- `SITE_URL` — your absolute origin (used for `sitemap.xml`).

Also enable **Settings → Pages → Source: GitHub Actions**.

### Google Analytics

The deployed site uses the existing Jambu/Home Google Analytics 4 property and tracks page views,
including client-side navigation. The public Measurement ID is configured in the deploy workflow.
For local development, copy `.env.example` to `.env` and set `PUBLIC_GA_MEASUREMENT_ID`; tracking
is disabled when the variable is absent or invalid.

## Scripts / layout

- `scripts/build_static_db.py` — dictionary-codes citations, tags, article prose,
  alignments/correspondences, compacts indexes, writes precomputed `meta` counts, and `VACUUM`s.
- `scripts/pack_db.mjs` / `unpack_db.mjs` — enforce the sub-50 MB artifact and restore it for CI.
- `src/lib/sqliteCore.ts` — downloads, restores, caches, and opens SQLite in a worker.
- `src/lib/query.ts` — the query layer (port of the old Flask `search.py` + entry grouping).
- `src/lib/server/db.ts` — build-time `better-sqlite3` access for prerendering.
- `src/routes/**` — the pages.

## Notes

- The deployed database is 43.00 MB. Its 97.04 MB expanded form remains tuned for fast SQLite
  scans and is stored only in the visitor's private browser cache and CI's temporary workspace.
- Text fields (`word`, `gloss`, `notes`) may contain hand-authored HTML and are rendered as such,
  matching the original site (trusted, curated content).
