# Detail sidecar — session handoff

Last updated: 2026-07-29

This records a discrete, uncommitted unit of work: the **partner×product×year
detail sidecar** (Tier 1 of the frontend data-contract expansion). Read this
before continuing so you don't re-derive the context or accidentally ship the
outstanding action below.

## TL;DR

- We added **one new, additive artifact**: a per-country *detail* sidecar that
  surfaces year-by-year partner×product cells. Nothing existing was rewritten.
- The data was **already in the canonical matrix** — this is a pure offline
  reprojection, no WITS collection. Release `2026-07.2` was minted from
  `2026-07`/`2026-07.1` via `reproject`.
- **Nothing is committed or pushed.** It all lives in the working tree.

## ⚠️ Outstanding action before any commit

`web/static/data/current.json` is currently flipped to **`2026-07.2`** (a side
effect of `reproject`). The decision on record is to **keep production on
`2026-07.1` until the frontend actually consumes the detail sidecar.**

Before committing, revert the pointer:

```bash
git checkout -- web/static/data/current.json   # back to 2026-07.1
```

Do NOT commit `current.json` pointing at `2026-07.2` unless the frontend
detail-consuming journeys have shipped in the same change. The `2026-07.2`
release directory itself is safe to commit at any time (it's immutable and
additive); only the active-pointer flip is being deferred.

## Why we did this

The frontend "continuous scene" roadmap is blocked in several places on data the
projections didn't expose: product sparklines, product composition over time,
and relationship history with product identity (Journeys A and C). The key
finding: the canonical matrix **already stores partner × product × year × flow**
at full granularity (301k bilateral rows, 2002–2022). The projection step
deliberately discarded everything except the headline year (`crossYear`). So the
#1 blocker needed **zero new collection** — only a reprojection.

We deliberately scoped this pass to **Tier 1 only**. The expensive tiers
(larger partner universe for ROW top-N, mirror flows for the quality lens,
product sub-hierarchy) require the big coordinated WITS recollection and are out
of scope here.

## What changed (files)

Pipeline:
- `pipeline/src/tradechord_pipeline/projections.py`
  - `build_country_detail()` — emits `crossCellsByYear: { year: CrossCell[] }`,
    reusing `_cross_cells()` per year.
  - `_dump_compact()` — deterministic **minified** writer (the detail files are
    large and lazily fetched, so they are not pretty-printed).
  - `write_projections()` — now also writes `detail/<CODE>.json` per reporter.
  - `_cross_cells()` docstring updated (no longer "headline year only").
- `pipeline/tests/test_projections.py` — added `test_country_detail_keys_cells_by_year`,
  `test_generated_detail_matches_schema`, and a `detail/USA.json` assertion.

Contract:
- `data/contracts/detail.schema.json` — new schema, reuses the existing
  `crossCell` definition. Shares **schemaVersion 2** (see decision below).

Frontend contract (types only — no UI consumes it yet):
- `web/src/lib/data/types.ts` — `CountryDetail` interface.
- `web/src/lib/data/load.ts` — `loadCountryDetail()` lazy loader.

Generated data (from `reproject`, deterministic):
- `data/releases/2026-07.2/` — canonical matrix (byte-identical to source) +
  manifest + checksums.
- `web/static/data/2026-07.2/` — full projection set **plus** the new `detail/`
  directory (30 files).

## The artifact shape

`web/static/data/<version>/detail/<CODE>.json`:

```jsonc
{
  "schemaVersion": 2,
  "datasetVersion": "2026-07.2",
  "country": "IRL",
  "years": [2002, ..., 2022],
  "crossCellsByYear": {
    "2022": [ { "partner": "AUS", "product": "01-05_Animal",
                "exportsUsd": 78697781, "importsUsd": 0,
                "balanceUsd": null,
                "exportAvailable": true, "importAvailable": false }, ... ]
  }
}
```

Each cell is **identical to the existing `CrossCell`** (same seven fields), so
the frontend reuses its existing type and rendering. Honest availability
semantics are preserved per year: `balanceUsd` is `null` when a flow was not
explicitly collected (never a fabricated zero).

## Decisions made (and why)

1. **Additive at schema v2, NOT a v3 bump.** Bumping would make the current app
   (which enforces `SUPPORTED_SCHEMA_VERSION = 2`) reject the whole release
   before the frontend is ready. Additive files that old clients ignore are
   backward-compatible. Keep it v2.
2. **Separate sidecar file, not inlined** into the country projection. Inlining
   would ~3× the initial per-country payload for data most sessions never open.
   The sidecar is fetched only on drill-in.
3. **Dense-consistent encoding** (`crossCellsByYear` = existing `_cross_cells`
   per year, including materialized zeros and ROW). Chosen over a bespoke lean
   encoding for simplicity and exact `CrossCell` reuse. See size trade-off below.

## Size

- Detail dir: **~36 MB** across 30 countries. Largest file USA **1.1 MB** (well
  under the 20 MB/file CI guard). Git compresses blobs to a few MB in-repo.
  Vercel serves each gzipped (~86 KB for USA) and only on drill-in.
- A **lean encoding** (drop zero cells, factor availability per partner/flow)
  was measured at ~16.8 MB (−35%) but adds frontend contract complexity. Only
  adopt it if repo footprint becomes a real concern; not recommended otherwise.

## Verification (all green at handoff)

- Pipeline: `37 passed`, ruff clean. Run: `cd pipeline && .venv/bin/python -m pytest -q`
- Release integrity: `verify --release data/releases/2026-07.2` → OK.
- Web: `svelte-check` 0 errors / 0 warnings; `vite build` succeeds.
  - Note: run `svelte-kit sync` before `svelte-check` after a build — a stale
    `./$types` otherwise produces spurious cascade errors.

## Also done this session (cleanup)

- Deleted `web/src/lib/ui/selection.svelte.ts` — genuinely dead (no importers;
  `motion-lab` defines its own same-named local functions).
- **`explorer/scene.ts` and `explorer/scene-viewport.svelte.ts` are NOT dead** —
  an earlier grep missed relative `./scene` and `.svelte`-suffixed imports.
  They were briefly deleted and restored. Leave them.

## Recommended next steps

1. **Wire the frontend journeys to `loadCountryDetail()`** — this is the whole
   point of the sidecar:
   - product sparklines / product composition over time (Journey A);
   - relationship history with product identity (Journey C);
   - keep the "never infer product history from national totals" rule — read the
     sidecar or show an explicit unavailable state.
2. **Then, in the same change, flip `current.json` to `2026-07.2`** and update
   the Playwright coverage + methodology notes.
3. Only after that, consider the expensive Tier 3 data work (larger partner
   universe, mirror flows, product hierarchy) — each needs the big coordinated
   WITS recollection, which has still never been run (see
   `docs/refactor-roadmap.md` §6.2–6.4).

## Related

- `docs/refactor-roadmap.md` — living record; the "Current data boundary" note
  in §7.14 and Phase D are the parts this work starts to resolve.
- `plan.md` — original architecture/decision record.
