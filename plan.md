# TradeChord Monorepo & Data-Product Plan

Status: architecture implemented. This remains the decision record; active
follow-up work, optional improvements, and new decisions are tracked in
[`docs/refactor-roadmap.md`](./docs/refactor-roadmap.md).
Vercel production architecture and performance budgets are tracked in
[`docs/deployment-performance.md`](./docs/deployment-performance.md).

## Implementation status (2026-07-27)

Completed:

- Monorepo layout and independent Node/Python toolchains.
- Directly reported export and import flows.
- Versioned canonical releases and committed browser projections.
- Deterministic gzip, schemas, checksums, and offline pipeline tests.
- Per-country projections for `/` and `overview.json` for `/all`.
- Removal of the legacy 14 MB browser CSV and browser-side aggregation.
- Explicit request statuses, strict validation, and Vercel deployment adapter.
- Compatibility release semantics for unavailable bilateral flows.
- Coordinated export/import partner unions, validated against a live USA/DEU
  pilot with no unresolved, duplicate, reconciliation, value, flow, or shape
  failures.
- Atomic browser projection promotion, per-file hashes, release verification,
  coverage summaries, country names, browser loading/error states, and
  Playwright route/interaction coverage.
- The first continuous-scene interactions: network ↔ ranked partners and
  network → bilateral reported export/import relationship, with stable
  semantic keys, URL restoration, keyboard activation, and reversible
  selection.
- Vercel cache policy configuration for immutable versioned projections and a
  separately revalidated active-release pointer, verified in production.
- Persistent Vercel project configuration with `web/` as the root and Node 22;
  the production bilateral journey passes in Chromium.

Operational follow-up:

- Run and review the full 30-reporter recollection before publishing the next
  historical-data release. The active `2026-07.1` release is intentionally a
  schema-v2 compatibility projection of the existing canonical matrix.
- Complete visual, interruption, focus-restoration, and screen-reader QA for
  the first continuous-scene prototype.

This document merges the pipeline repo (`TradeChord_datapipeline`) and the dashboard repo
(`TradeChord`) into one repository with a clean data contract, and sets the path to a more
efficient, correct, and modular dashboard.

---

## 1. North star

**A fresh clone runs the dashboard with Node alone. Python and WITS access are required only when
deliberately publishing a new data release.**

The pipeline is an offline *release tool*, not a dependency of normal web development or deployment.

---

## 2. Non-negotiable architectural decisions

1. The **frontend repository is the Git-history base**; the pipeline (no existing history) is copied in.
2. **Normal web development requires Node only.**
3. **Pipeline execution is offline/manual** and never part of a web build or deploy.
4. **Published releases are committed** to the repo (not built in CI, not fetched as external assets).
5. **Exports and imports are collected directly as separate flows** (WITS-reported), not inferred.
6. **Mirror flows are validation data, not the primary import source.**
7. The **canonical schema includes `flow`**.
8. **ROW is computed and reconciled separately for each flow.**
9. The **canonical gzip is deterministic** (`mtime=0`, stable sort, fixed column order).
10. **Browser projections are committed directly under `web/static/data/<version>/`.**
11. `/` gets **per-country projections**; `/all` gets a **purpose-built `overview.json`**.
12. **`current.json` selects the active release.**
13. **No symlinks, copy hooks, or Python steps** in normal web setup.
14. **Staging is ephemeral and Git-ignored.**
15. The **first move is behavior-preserving**; existing diagnostics are recorded, then fixed separately.
16. **Initial CI and testing remain deliberately small.**

---

## 3. End-state layout

```
tradechord/
├── README.md
├── Makefile
├── package.json                     # optional root convenience scripts
├── .gitignore
├── .python-version                  # e.g. 3.11.9
├── .nvmrc                           # e.g. 22.14.0 (confirm vs SvelteKit/Vite first)
│
├── .github/workflows/
│   ├── pipeline.yml
│   ├── web.yml
│   └── release-data.yml             # workflow_dispatch only
│
├── pipeline/
│   ├── pyproject.toml
│   ├── src/tradechord_pipeline/
│   │   ├── cli.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── clients/wits.py
│   │   ├── parsing/sdmx.py
│   │   ├── collection/flows.py       # exports + imports, one code path
│   │   ├── validation/
│   │   │   ├── completeness.py
│   │   │   └── reconciliation.py
│   │   └── release.py
│   └── tests/fixtures/
│
├── web/                              # the SvelteKit app (git mv'd here)
│   ├── package.json
│   ├── src/
│   └── static/data/
│       ├── current.json              # points to active release
│       └── <version>/                # committed browser projections
│           ├── overview.json
│           ├── countries.json
│           └── countries/{USA,DEU,...}.json
│
├── data/
│   ├── contracts/
│   │   ├── manifest.schema.json
│   │   ├── records.schema.json
│   │   └── projection.schema.json
│   └── releases/<version>/           # canonical archival artifact
│       ├── manifest.json
│       ├── trade_matrix.csv.gz
│       └── checksums.txt
│
└── docs/
    ├── architecture.md
    ├── data-methodology.md
    └── data-release.md
```

`data/staging/`, `**/.cache/`, and all raw shards are **git-ignored** and never committed.

---

## 4. Decision 1 — direct exports and imports (dual flow)

Primary data is WITS-reported flows:

- `XPRT-TRD-VL` → `flow=export`
- `MPRT-TRD-VL` → `flow=import`

For country X:

```
Exports = records where reporter=X and flow=export
Imports = records where reporter=X and flow=import
Balance = reported exports − reported imports
```

National imports are **never** derived from other reporters' exports. Mirror flows (e.g. USA-reported
imports from DEU vs DEU-reported exports to USA) are retained only as **validation** — discrepancies are
expected (valuation, timing, re-exports, CIF/FOB) and are not automatically pipeline errors.

### Pre-implementation check (blocking)

The repo is inconsistent about the import indicator (`config.py` → `MPRT-TRD-VL`; an older script →
`IMPT-TRD-VL`). Before any full import run, **verify the live WITS endpoint** with one
reporter/partner/product/year fixture, then encode the authoritative indicator mapping in **one place**
and test it. Historical scripts do not get a vote.

### Canonical record

```
year,reporter,partner,product,flow,value_usd
2022,USA,CAN,84-85_MachElec,export,123456789
2022,USA,CAN,84-85_MachElec,import,987654321
```

- `reporter` — the reporting country (both flows).
- `partner` — destination for exports, origin for imports.
- `flow` — `export | import`.
- `value_usd` — integer current USD, `round(value_thousands * 1000)`.
- Source-indicator mappings live in the **manifest**, not the records.
- Compound key: `year + reporter + partner + product + flow`.

Manifest declares the flow provenance:

```json
{
  "flows": {
    "export": { "sourceIndicator": "XPRT-TRD-VL", "valuation": "reported export value" },
    "import": { "sourceIndicator": "MPRT-TRD-VL", "valuation": "reported import value" }
  }
}
```

### Flow-specific ROW

```
export ROW = reporter world export total − explicit export destinations
import ROW = reporter world import total − explicit import origins
```

Import ROW is **never** inferred by reversing export records. Validation reconciles each flow separately,
with a documented numeric tolerance (not exact float equality):

```
sum(explicit export partners) + export ROW ≈ export WLD
sum(explicit import partners) + import ROW ≈ import WLD
```

### Cost

Architecturally free (same client, parser, cache, coverage, release machinery). Operationally it roughly
doubles collection work and may expose indicator-specific API behavior — acceptable for an infrequent
offline release, but gated behind a pilot.

**Pilot before full run:** reporters `USA, DEU`; years `2002, 2012, 2022`; 2–3 products; both flows.
Validate endpoint structure, correct source indicator, partner-dimension semantics, WLD reconciliation,
empty/missing behavior, and magnitude/unit plausibility. Only then run full history.

---

## 5. Decision 2 — committed static projections (no symlink)

The release writes **two representations** in one atomic commit:

```
data/releases/<version>/            web/static/data/<version>/
  manifest.json                       overview.json
  trade_matrix.csv.gz                 countries.json
  checksums.txt                       countries/USA.json, DEU.json, ...
                                    web/static/data/current.json
```

- `data/releases/<version>/trade_matrix.csv.gz` — canonical analytical/archive artifact.
- `web/static/data/<version>/…` — browser projections generated from that matrix.
- These are **not redundant copies** (different representations); the manifest records hashes for both.

No symlink, no runtime copy, no `prepare:data`, no Python in normal web work. The dashboard loads:

```
/data/current.json
/data/<version>/overview.json
/data/<version>/countries/USA.json
```

`current.json` is minimal:

```json
{ "schemaVersion": 2, "datasetVersion": "2026-01", "manifestSha256": "..." }
```

The web app must **reject unsupported `schemaVersion`** values.

### Atomicity

The release program generates everything into a temporary workspace, validates, then promotes to both
final trees. A half-failed promotion leaves a visibly dirty working tree but commits no release. No
cross-directory transactional filesystem machinery — unnecessary ceremony for this project.

---

## 6. Route-driven projections

Projection schemas are derived from **actual component input requirements**, inventoried before design:

| Route | Component        | Required data                                          |
|-------|------------------|--------------------------------------------------------|
| `/`   | headline equation| exports, imports, balance by year                      |
| `/`   | mini lines       | export/import/balance time series                      |
| `/`   | chord            | selected-year bilateral export + import flows          |
| `/`   | product treemap  | product exports, imports, balance, share, history      |
| `/`   | partner treemap  | partner exports, imports, balance, share, history      |
| `/`   | partner slope    | partner shares for comparison years                    |
| `/`   | product slope    | product shares for comparison years                    |
| `/all`| reporter ranking | reporter totals and ranks by year                      |
| `/all`| balance trend    | reporter export/import/balance series                  |
| `/all`| compact chord    | compact selected-year bilateral flows                  |

Generate only those projections.

### Division of responsibility

Pipeline owns (correctness): totals, flow direction, product/partner aggregation, coverage, ROW,
canonical shares, bilateral flows, time series.

Web owns (presentation): top-N displayed, label placement, color, layout sorting, tooltip formatting,
selected comparison years. **The pipeline is not a chart-layout engine.**

### `overview.json` (starting shape)

```json
{
  "schemaVersion": 1,
  "datasetVersion": "2026-01",
  "defaultYear": 2022,
  "reporters": [
    {
      "code": "USA",
      "name": "United States",
      "totalsByYear": [
        { "year": 2002, "exportsUsd": 0, "importsUsd": 0, "balanceUsd": 0, "exportRank": 1 }
      ],
      "topPartnerRanks": [
        { "partner": "CAN", "series": [ { "year": 2002, "rank": 1, "valueUsd": 0 } ] }
      ],
      "compactChord": { "year": 2022, "countries": ["USA","CAN","ROW"], "matrix": [] }
    }
  ]
}
```

Start as one file. Split (`overview/totals.json`, `overview/ranks.json`, `overview/chords-2022.json`)
only after measuring size.

---

## 7. Determinism & runtime pins

### Deterministic gzip

```python
import gzip
from pathlib import Path

with Path(output_path).open("wb") as raw:
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        gz.write(csv_bytes)
```

Also required: stable record sort order, UTF-8, `\n` line endings, fixed CSV column order, stable JSON key
order + separators/indentation, integer USD values, and **no generation timestamp inside
content-addressed files**. Operational timestamps (e.g. `generatedAt`) live in the manifest, which is
expected to change between builds; the matrix and projections stay byte-identical for identical
normalized inputs.

### Pins

```
.python-version   3.11.9
.nvmrc            22.14.0   # confirm against current SvelteKit/Vite before locking
```

```json
{ "engines": { "node": ">=22 <23", "npm": ">=10 <11" } }
```

```toml
[project]
requires-python = ">=3.11,<3.12"
```

Exact patch versions for reproducible local setup; compatible ranges in package metadata to avoid install
friction.

---

## 8. Release acceptance gate

`release --input data/staging/<run> --version <version>` must, before writing anything:

1. Load the run configuration.
2. Validate expected reporters, years, products, and **both flows**.
3. Reject unresolved request failures (no silent partials).
4. Reject duplicate compound keys.
5. Reconcile per flow: `explicit partners + ROW ≈ WLD` within tolerance.
6. Validate units and numeric validity (integer USD, non-negative).
7. Write normalized matrix (deterministic).
8. Generate web projections (overview + per-country).
9. Write manifest + `checksums.txt`.
10. Promote atomically to both trees; update `current.json`.

It must never glob arbitrary historical shards from a shared directory.

---

## 9. Right-sized tests (initial)

Pipeline:

1. SDMX parser against saved XML fixtures.
2. Unit conversion (WITS thousands → integer USD).
3. Flow-specific ROW/WLD reconciliation.
4. Duplicate compound-key detection.

Cross-boundary:

5. Contract smoke test — a generated manifest and one country projection validate against their schemas.

Offline by default. A separately marked integration test (`pytest -m integration`) may contact WITS; CI
runs only the offline suite. Add further tests only when their code is refactored or a bug warrants them.

---

## 10. Right-sized CI

**pipeline.yml:** install pinned Python → install with dev deps → `ruff check` → offline `pytest` →
large-file guard → validate committed manifest/checksums.

**web.yml:** install pinned Node → `npm ci` → `svelte-check` → `vite build` → large-file guard.

**release-data.yml:** `workflow_dispatch` only. Initially may validate/build a prepared staging run. No
automated PR creation and no WITS calls on push. (A PR-opening release bot with coverage-diff is a
deliberate *later* enhancement, not part of the initial build.)

The initial mechanical-move commit is allowed to reproduce the known `svelte-check` failures; the Node job
becomes required only after the quality-baseline commit makes it green.

---

## 11. Sequencing — commits (mechanical stays mechanical)

1. **`chore: checkpoint current dashboard work`** — capture the current dirty frontend exactly.
2. **`chore: establish monorepo ignore rules and structure`** — root `.gitignore` + empty structural dirs.
3. **`chore: move web application under web`** — `git mv` tracked files; only path/config changes needed to
   run from `web/`. Record baseline (e.g. `vite build: passes; svelte-check: N errors, M warnings`). **Do
   not fix errors here.**
4. **`chore: import active pipeline source`** — curated source only; no data dir, cache, shards, or
   experiments.
5. **`fix: restore clean web type check`** — first behavior/quality change, separate from the move.

---

## 12. Milestones

**M1 — monorepo mechanics. ✅ Done.** Checkpoint frontend; final ignore rules; move frontend to `web/`;
record existing check failures; import curated pipeline to `pipeline/`; root README + Makefile; pin Python &
Node; confirm no cache/shards/secrets entered Git.

**M2 — minimal reliable pipeline. ✅ Done.** `pyproject.toml`; extract WITS client, SDMX parser, collector,
release exporter; verify import indicator via pilot request; add `flow` to canonical schema; the five
focused tests; explicit request statuses; deterministic gzip; stop glob-unioning; minimal CI.

**M3 — first honest dual-flow release. 🔄 In progress.** Export/import pilot; validate flow-specific
WLD/ROW; full XPRT + MPRT collection; canonical normalized matrix; manifest + checksums; generate
`overview.json` + per-country projections; commit both representations; update `current.json`. *Added during
build:* multi-year + top-K collection (year-range requests, consistent partners across years), WITS 404→
not-found + `ROU→ROM`/`TWN→OAS` partner-code fixes, projection layer + `load.ts` typed loader.

**M4–M5 — superseded by the Frontend Rebuild (§16).** Rather than rewire the legacy components onto the
projections (only to discard them), the presentation layer is **rebuilt** on the clean data layer with the
DataJockey brand kit, mobile-responsive layout, reactive charts, and motion. The security/cleanup items
formerly in M5 (server-side AI, remove `{@html}`, explicit deploy adapter) are absorbed into §16.

---

## 13. Guardrails

### Against committing 1.2 GB

Before the pipeline's first import, and before each initial commit:

```bash
git status --short
git add -n pipeline data
git check-ignore -v <suspicious/path>
git diff --cached --stat
git diff --cached --name-only
```

Never `git add .` during the first pipeline import — add curated paths explicitly. Verify the import
directory is kilobytes/low-MB, not 1.2 GB:

```bash
du -sh <pipeline-import-dir>
find <pipeline-import-dir> -type f | wc -l
```

CI large-file guard (fails on unexpected big files outside releases):

```bash
find . -type f -size +20M -not -path './.git/*' -not -path './data/releases/*'
```

### Ignore rules (essentials)

```
# working data / cache / shards
data/staging/
**/.cache/
*.bin
*.checkpoint*.jsonl
optimized_exports_*.csv
optimized_exports_*.manifest.json
*_matrix_*.csv
*_matrix_*.json

# toolchains
__pycache__/
*.py[cod]
.venv/ .pytest_cache/ .mypy_cache/ .ruff_cache/
node_modules/ .svelte-kit/ build/ dist/

# secrets / OS
.env
.env.*
!.env.example
.DS_Store

# explicit release exception
!data/releases/
!data/releases/**
```

### Secrets check before import

```bash
find <pipeline-import> -name '.env*' -o -name '*secret*' -o -name '*credential*'
rg -n 'API_KEY|SECRET|TOKEN|PASSWORD|BEGIN .*PRIVATE KEY' <pipeline-import>
```

WITS may need no secret, but cached responses, shell fragments, and unrelated `.env` files must still be
excluded.

---

## 14. Open / deferred (recorded, not blocking)

- Exact `.nvmrc` pin pending SvelteKit/Vite compatibility confirmation.
- Import-flow coverage target (may differ from the export `COVERAGE_TARGET`); confirm during pilot.
- Whether `overview.json` splits by visualization — decide after measuring real size.
- PR-opening release workflow with coverage-diff report — deliberate later enhancement.
- Methodology doc (`docs/data-methodology.md`) must label the current single-flow CSV as
  **legacy/incomplete** until the first dual-flow release lands.

---

## 15. Recommended first action

1. Prepare the curated pipeline import **outside** Git.
2. Write the final root `.gitignore` before copying anything.
3. Verify the import contains no cache, shards, secrets, or timestamped outputs.
4. Checkpoint the current frontend (Commit 1).
5. Move the frontend with `git mv` (Commit 3).
6. Only then copy curated pipeline source into `pipeline/` (Commit 4).

---

## 16. Frontend Rebuild (DataJockey) — revises M4–M5

The data layer is now the stable contract (typed projections + `web/src/lib/data/load.ts`). The presentation
layer is **rebuilt on top of it**, not incrementally refactored — a full brand rebuild replaces those
components anyway, so refactoring the legacy imperative-D3 layer first would be wasted work.

### Guiding principles

1. **Rebuild on the data layer, not the CSV.** Components receive typed projection props
   (`summaryByYear`, `partnersByYear`, `productsByYear`, `overview`); no component parses the matrix,
   multiplies by 1000, derives mirror imports, or aggregates in-browser.
2. **Brand-kit-first.** All color, type, spacing, radii, and motion come from the **DataJockey brand kit** as
   a `web/src/lib/theme/` tokens module (CSS custom properties + typed TS export). No ad-hoc hex values.
3. **Mobile-first responsive.** Fluid layout with container queries; the fixed `820px 920px` grid and
   hardcoded chart widths are gone. Charts are size-aware (`ResizeObserver`/`bind:clientWidth`).
4. **Reactive charts: D3 for the math, Svelte for the DOM.** D3 computes scales/layouts
   (`d3.chord`, `d3.treemap`, scales); Svelte renders the SVG and owns reactivity and transitions
   (`tweened`/`crossfade`). Replaces the `onMount`/`afterUpdate` + `d3.select` pattern, which fights
   responsiveness and animation.
5. **Svelte 5 runes** baseline for new components (`$state`/`$derived`/`$props`).
6. **Accessibility & touch as first-class**: keyboard/ARIA, balance encoded by more than red/green, tap
   interactions (no hover-only affordances).

### Prerequisites (blocking)

- **The DataJockey brand kit** (private repo `dj-brand-kit`) — tokens, and any component/motion specs. The
  agent cannot pull it from the sandbox (no `gh`, no SSH key, no token handling); provide via a local clone
  path, `gh` install + auth, or pasted token values. First deliverable once available: the `theme/` module.
- **M3 complete** — committed release + projections; the loader wired.

### Phases (each shippable)

**F0 — Foundations.** Finish M3 (release + projections). Wire `load.ts` (replaces the 14 MB CSV parse).
Brand kit → `theme/` tokens. Adopt Svelte 5 runes; set the explicit deploy adapter.

**F1 — Design system primitives.** Token-driven `Card`, `Stat`, `Grid`, `Tooltip`, `Legend`, `Controls`
(country picker, year control), `Skeleton`. Mobile-first responsive shell (stacked → multi-column).

**F2 — Reactive chart architecture.** Establish the "D3 math + Svelte DOM" pattern with a size-aware
container and transition/tween utilities. Build **one reference chart** (slope) end-to-end to lock the
pattern before scaling out.

**F3 — Rebuild the charts** (on F2, fed by projection props):
- **Chord** — animated ribbons, responsive radius, hover to isolate a partner's flows.
- **Treemap** (partners + products) — tween on year/country change; dual-flow tiles (exports / imports /
  balance) with mini-charts.
- **Slopes** (partners + products) — animated line-draw; share change over the year range.
- **Equation + mini-trends** — the exports − imports = balance hero, now with *real* balance.

**F4 — Layout, screens & interactions.** Responsive `/` and `/all` compositions. Cross-chart interaction
(selecting a partner highlights it across chord + treemap + slope); a synced year control; smooth country-
change transitions; mobile tap tooltips.

**F5 — Motion, a11y, polish.** Motion choreography (enter/update/exit, stagger), empty/error/loading states,
keyboard + ARIA, color-independent balance encoding, performance pass.

**F6 — Security & deploy.** Finalize the Vercel adapter and CI. The earlier
AI-commentary proposal was removed; do not retain runtime SSR solely for a
feature that no longer exists.

### Decisions (resolved)

- **Brand kit** — full DataJockey kit (tokens + guidance: color, typography, components, dashboard) added as
  a **git subtree** at `dj-brand-kit/`; web copies under `web/src/lib/theme/` + `web/static/{fonts,brand}/`.
- **Deploy target** — **Vercel** (`@sveltejs/adapter-vercel`; Kit upgraded to
  2.70.x). This original SSR decision is superseded by the static-first plan in
  `docs/deployment-performance.md`; isolate runtime SSR only if a future
  feature demonstrates a real need.
- **Cross-chart highlighting** — **in scope for v1** (F4), using the kit's lit/recessed pattern.
- **Year scrubber** — **deferred**; v1 uses the fixed range with the headline year.
- **Charts to rebuild** — chord, treemap (partner + product), slopes (partner + product), equation +
  mini-trends.

Still open:
- Whether `/all` (overview small-multiples) is v1 or follows the single-country view.
