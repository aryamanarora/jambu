# AGENTS.md — jambu-static

Agent-facing notes for the static Jambu site. Read `README.md` first for the architecture
overview; this file is the operational stuff — how the DB flows, dev gotchas, and invariants that
aren't obvious from the tree.

## Stack

SvelteKit 2 + **Svelte 5 runes** (`$state`/`$derived`/`$effect`/`$props`, `{#snippet}`/`{@render}`)
+ `adapter-static`. No server at runtime. Two totally different SQLite paths:

- **Build/prerender + dev SSR**: `src/lib/server/db.ts` opens `jambu.db` with `better-sqlite3`.
- **Client (browser)**: `src/lib/sqlite.worker.ts` runs sqlite-wasm in a Worker, single-file
  "full" mode (fetches byte ranges over HTTP; **not** split/chunked mode — see README note).

`src/lib/query.ts` is the **single source of query truth** for both paths — a port of the old
Flask `search.py` plus the entry/cognate grouping. Change query semantics there, once.

## The DB, end to end

```
../data/cldf/*   --(scripts/build_static_db.py)-->  .dbwork/jambu.db  --(db:stage)-->  static/db/jambu.db
                       npm run db:transform                                 npm run db:stage
```

- `npm run db:transform` = `python3 scripts/build_static_db.py .dbwork/jambu.db --cldf ../data/cldf`.
  It reads the sibling data repo's `cldf/` **directly** (the README's mention of a `.dbwork/data.db`
  input is stale — the current script takes `--cldf`). It drops unused tables, adds indexes + the
  **FTS5 trigram** index (substring search), remaps `alignment.parameter_id` onto each reflex's
  current `origin_lemma_id`, precomputes `meta` counts, and `VACUUM`s.
- `npm run db:stage` copies it to `static/db/jambu.db`, served at `/db/jambu.db`.
- In **CI** the DB is NOT built — it's downloaded from a release asset (`STATIC_DB_URL` in
  `.github/workflows/deploy.yml`). So a data change only reaches prod after you rebuild `jambu.db`
  and re-upload it to the release. See "Shipping" below.

### Dev DB gotcha: stale connection after a rebuild
The Vite dev server pins a `better-sqlite3` handle to the DB's inode. `db:stage` replaces the file
(new inode), so a long-lived dev server keeps serving the **old** data (e.g. stale headwords).
`server/db.ts` reopens when the DB mtime changes — but if you see stale data after a transform,
restart `npm run dev`.

## Prerender

Canonical pages are prerendered (`prerender = true` in the route). This is the slow part of a full
build (23k entry pages). While iterating:

```bash
JAMBU_DB=.dbwork/jambu.db PRERENDER_LIMIT=50 npm run build && npm run preview
```

`fallback` is **`404.html`**, not `200.html` — GitHub Pages ignores a 200 fallback and serves its
own 404 for unknown paths, so 404.html is the only shell it returns for client-rendered deep links.

## Page model invariants

- **Unified entry page.** `/entries/[id]` renders **any node** in the etymon graph — an etymon, a
  section form, a reflex, or a borrowed form (ancestry chain + its own alignment + its children).
  `/reflexes/[id]` is a **308 redirect** to `/entries/[id]`; don't add logic to the reflex route.
- Children of a node = `origin_lemma_id = ? AND relation IN ('reflex','borrowed')`.
- Ancestry recurses via `COALESCE(variant_of, origin_lemma_id)`. Borrowed forms have
  `origin_lemma_id` = their **source reflex** (a real node), so the same recursion works for loans.
- **Known prod caveat**: the unified entry page relies on dev/build SSR for arbitrary reflex IDs.
  Non-prerendered reflex IDs need a **client-fetch fallback** wired up before deploy — verify this
  is in place if you touch that route or ship.

## Files that MUST stay in sync with `../data`

These mirror data-side categories; if the pipeline adds/renames one, update here too:

- `src/lib/clades.ts` (`CLADE_COLORS`, `CLADE_ORDER`) + `src/lib/cladeTree.ts` (GROUP/SUPER
  hierarchy) ↔ `../data/cldf/languages.csv` Clade column.
- `src/lib/tags.ts` (`ERA_TAGS`, tag categories/names) ↔ `../data/tags.py` + `sanskrit_works.tsv`.

## Conventions

- Run `npm run check` (svelte-check) before considering a change done; keep it at **0 errors**
  (there are ~3 pre-existing warnings).
- Text fields (`word`, `gloss`, `notes`, etymology) may contain **hand-authored HTML** and are
  rendered as such — this is intentional (trusted, curated content), matches the original site.
- `FilterCell.svelte` supports an optional picker (pickerKey/pickerOptions/…) rendered first in a
  50/50 split header — used for the split Origin-lang/Origin column.

## Shipping to prod (only when the user asks)

1. Rebuild data in `../data` (see its AGENTS.md), then `npm run db:transform` here.
2. Upload `.dbwork/jambu.db` as `jambu.db` on a new release of the `jambu` repo
   (deploy workflow pulls `releases/latest/download/jambu.db`).
3. Push `main` — `deploy.yml` downloads that DB, runs the full build, deploys to Pages.
4. Verify the client-fetch fallback for non-prerendered reflex IDs is wired first.
