---
name: jambu-release
description: Prepare, publish, and verify Jambu production releases across the data and jambu-static repositories. Use when asked to ship Jambu, push it to production, publish a database release, or deploy the site; includes complete source/changelog reconciliation. Local serving or source discovery alone does not trigger publication.
---

# Jambu production release

Use an evidence-backed checklist for the entire requested release, not just the most
recently discussed source. Announce this skill when applying it. Keep a release audit
with each applicable item marked **passed**, **blocked**, or **not applicable** and
supporting paths, commit IDs, counts, hashes, and URLs. Preparation is not deployment;
a successful push is not a successful deployment.

## Scope and workspace

- [ ] Locate the sibling `data` and `jambu-static` repositories (normally under
  `~/Documents/Code/jambu-all`). Read their `AGENTS.md` and current release/build
  documentation. For lexical changes also read `data/SOURCE_INGESTION_CHECKLIST.md`.
  Use the actual Makefile/scripts when prose describes an older pipeline.
- [ ] Identify the requested destinations and existing authorization, including any
  requested data-repository push. Use authorization already provided; this checklist
  does not require another confirmation. It also does not authorize a new repository,
  unrelated edits, source PDFs, or a broader publication scope.
- [ ] Inspect both working trees, current branches, remotes, and previous deployment.
  Record the last successfully **deployed** frontend commit, database release, and
  corresponding data commit/snapshot. Do not assume HEAD or the latest draft release
  is the production baseline.
- [ ] Select the intended source, data, and frontend changes. Preserve unrelated work.
  If isolation is useful, prepare a release checkout and inspect its diff. Explicitly
  account for any necessary dependency from otherwise unrelated edits.
- [ ] Check local free space and existing jobs/servers before starting large builds.
  Allow space for CLDF, expanded/compact DBs, compressed assets and prerender output.
  Use one writer per generated output. Stop an old job before retrying its output;
  never launch overlapping pipelines or delete/rebuild `data/form-identities.csv`.

## Local resource budget (8 GB RAM laptop)

- Default to focused tests and small smoke checks locally. Run required full data builds,
  full test suites, production prerendering, and maximum-compression packaging in existing
  CI or an authorized remote environment. Relocate required gates; do not silently skip them.
- Before starting expensive work, inspect existing jobs and reuse verified artifacts/checks
  when their inputs are unchanged. Batch source changes into one full rebuild.
- Run at most one heavy local job at a time across this workspace. Do not overlap database
  generation, full tests, compression, and production builds. Do not stop another task's jobs
  without establishing ownership or authorization.
- If a heavy local run is necessary, explain why and run it sequentially with one worker/thread
  where supported. Avoid automatic all-core compression and high-memory compression settings
  locally. If required asset size/codec gates need those settings, package remotely instead.
- Prefer streaming reads, scoped SQL queries and bounded samples over loading multiple complete
  datasets into memory. Reuse one dev server and browser tab; avoid duplicate database loads.
- CPU priority (`nice`) does not limit RAM, and Node heap limits do not cap total process memory.
  Do not promise a memory ceiling without measuring and enforcing it.
- Use existing authorized CI for remote work; do not invent a cluster destination, incur new
  paid infrastructure, or publish unfinished changes merely to offload a check. If no suitable
  runner is available, report the deferred full gate and continue lightweight work.

## Complete release inventory and changelog

- [ ] Compare the selected data snapshot with the **previous deployed data snapshot**:
  new and expanded source ingests, supporting citations, language/dialect changes,
  transcription fixes, graph/curation changes, and relevant UI/research changes.
- [ ] Run `scripts/source_inventory.py DATA_REPO --base DATA_REF` from this skill to
  help reconcile reference additions and edits. Its primary-source suggestions are
  based on provenance paths and need review; bibliography additions are not all new
  dictionaries. Inspect raw-source and compiled-form deltas for expanded existing
  sources, which a new-reference-only comparison misses.
- [ ] Update `jambu-static/src/lib/changelog.ts`: extend the existing date entry when
  present, keep dates newest first, and preserve other intended updates. Name all
  significant new/expanded primary sources, with compact grouping where appropriate.
  Do not describe a multi-source refresh as only the last source ingested.
- [ ] Link each new primary source in `ingested.sources`; use meaningful labels.
  Include real affected language IDs in `ingested.languages`, grouping dialect-heavy
  surveys sensibly. Supporting works can be summarized under their parent ingestion;
  do not imply they were separately ingested in full.
- [ ] Verify every changelog source/language ID against the selected compiled dataset
  and final browser DB. Reconcile stated counts and coverage with those data. Distinguish
  raw attestations, merged browser nodes, headwords, displayed forms and references.
  Recheck coverage after changing release scope.

## Data, identity, and metadata gates

- [ ] Complete applicable ingestion-checklist audits before shipping data changes.
  Verify source spelling, locators, source-specific profile routing (declared in each source's
  `data/data/other/forms/<stem>.yaml`, validated by `make check-sources` in `data/`),
  bibliography, language/dialect parents and clades, and explicit graph claims. Confirm
  every new source has its YAML settings file and, where regenerated by an importer,
  `defaults.importer.commands` so `make ingest SOURCE=<stem>` reproduces it. Apply the user's
  editorial decisions without silently overriding them with a default classification.
- [ ] Record pre-build IDs, source keys, aliases and graph counts (sha256 of
  `cldf/edges.csv`, `cldf/forms.csv`, `data/form-identities.csv` and the etymology
  sidecars; do not copy them into task directories). Run focused tests first, then the
  full data pipeline with `make all` in `data/` (it runs every stage in order with the
  single-thread environment; do not hand-write a wrapper script). Confirm unsaved
  etymology-lab passes are either saved via `make save-pass` or explicitly excluded.
  Run the relevant full suite after the pipeline; isolate tests that mutate fixtures.
- [ ] Investigate lost IDs, new conversion errors, unexpected unrelated changes or
  graph differences. For language/metadata-only changes, prove spelling, source keys,
  citations, persistent IDs and relationships survive. Reconcile expected merges.
- [ ] Record test results honestly. Existing failures require an actual baseline and
  a no-new-regressions comparison; never call a failing suite clean or expand the task
  into unrelated fixes. Follow any applicable repository rule that blocks shipping.
- [ ] Prepare and commit the intended data inputs, source importers, registries and
  audits as required by the requested scope. If publishing a compiled-only snapshot,
  label it explicitly and record what provenance remains unpublished. Do not claim
  that pushing a release branch updates data `main`.
- [ ] Verify public provenance links point to committed, published paths at the
  intended data ref. Raw source/audit paths on `main` must actually exist there;
  a separate CLDF-only branch does not make those links work. Report unresolved
  publication scope explicitly rather than silently leaving broken evidence links.

## Browser database and exact assets

- [ ] Build the browser DB from the final committed CLDF snapshot with the current
  `scripts/build_static_db.py` workflow. A previously verified DB may be reused only
  if rebuilding the selected committed input gives the identical hash, or equivalent
  recorded provenance proves that exact input was used.
- [ ] Verify SQLite integrity, expected source/language counts, representative IDs,
  aliases, citations and graph relations. Run codec/parity tests if schema semantics
  changed. Separate advisory raw-size warnings from hard deployment limits.
- [ ] Stage with `npm run db:stage`. The current packer uses the vendored browser
  decoder to prove a full lossless roundtrip and enforces a packed asset below
  60,000,000 bytes (raised from 50 MB at db-v37). Keep the verified raw and packed files until live checks finish.
  Never publish an oversized or corrupted artifact or work around the guard silently.
- [ ] Bump `src/lib/dbMeta.ts` to an unused database cache version for changed DB bytes.
  Record exact compressed and expanded byte counts and SHA-256 hashes. Keep release
  manifest, metadata, decoder imports and staging/unpacking paths consistent.
- [ ] Ensure `.github/workflows/deploy.yml` consumes the intended version, not an old
  pinned asset. Prefer publishing both exact raw and packed assets and verifying them
  in CI: recompressing on a different zstd version may change packed byte length.
  If using `scripts/db-release.json` and `verify_db_artifact.mjs`, update and run them.
- [ ] Run `npm run check` with zero errors and relevant frontend/decoder tests. The
  **actual release checkout**, not just a dirty dev checkout, must be validated.

## Publish and deploy

- [ ] Determine an unused release/tag from GitHub and the cache version; do not
  hardcode a past version or overwrite an existing release to hide new DB bytes.
- [ ] Commit the selected frontend changes including changelog, metadata, workflow,
  and verification manifest. Check remote branch state before pushing; never force
  over concurrent work. Record the exact data and frontend commits.
- [ ] Publish the requested data commit(s), including needed Git LFS objects, to the
  intended branch; verify the remote SHA and distinguish LFS upload from Git ref
  success. Carry forward an existing approval. If review blocks a destination,
  explain the specific block and finish unaffected work without bypassing it.
- [ ] Publish the frontend commit to a release branch if needed to establish a
  valid target before releasing. Create the release against that full commit SHA
  or verified branch; a short SHA may be rejected. Upload `jambu.db`, the verified
  `jambu.db.zst`, and a hash/provenance manifest. Do not upload the source book/PDF
  unless it is explicitly within the authorized scope and redistributable.
- [ ] Publish the release before advancing the deployment branch when CI downloads
  its assets. Push the verified frontend commit to the intended deployment branch
  (normally `main`). The release/tag and deployed code must describe the same build.
- [ ] Monitor the **matching commit's** Actions run until the full production build
  and Pages deployment finish successfully. A limited local prerender is a smoke
  check, not the full build gate. Keep the unrestricted CI build; inspect failures
  and make targeted fixes. Reuse existing valid checks and assets when unchanged.

## Live verification and handoff

- [ ] Read GitHub Pages configuration/deployment output to establish the actual
  production URL; the github.io project URL may redirect to an inherited custom
  domain. Verify the configured domain instead of treating that redirect as unknown.
- [ ] Download the deployed packed database and compare its exact size and SHA-256
  with the release manifest. Verify release asset hashes as well.
- [ ] Use a real browser to check the live homepage changelog and corpus totals,
  the affected source page and filters, an affected language, a representative linked
  or variant entry, and an arbitrary **non-prerendered** form deep link. Direct
  navigation must load through the `404.html` SPA fallback and browser SQLite.
- [ ] Confirm returning visitors receive the new cache version and the new data;
  rendering a prerendered page alone does not prove the browser DB works. Inspect
  relevant console errors and visually check the result. If one browser profile has
  a local storage/disk error, distinguish it from a production defect and verify in
  another available browser context; do not erase user browser data.
- [ ] If local serving was requested, verify the intended local server and its current
  database. Avoid duplicate servers or stale database handles after replacement.
- [ ] Save release evidence and synchronize intended release changes back to the
  workspace without overwriting unrelated work. Report release URL, production URL,
  local URL when requested, validation outcome, and any concrete remaining blocker.
  Do not say deployment is complete while CI, asset verification, browser loading,
  or an explicitly requested data push remains unverified.
## Post-release hygiene

- [ ] Run `make prune-lfs` at the workspace root to drop superseded LFS blobs from `data/.git/lfs`
  (they regrow by roughly 300 MB per data commit).
- [ ] Run `make clean-scratch` (dry run) and, once the task scratch under `tmp/`, `data/tmp/` and the
  stale `.dbwork` builds are confirmed finished, `make clean-scratch FORCE=1`.
