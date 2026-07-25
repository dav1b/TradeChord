# TradeChord Monorepo & Data-Product Plan

Status: agreed plan of record. Supersedes ad-hoc scripts and the manual CSV hand-off.

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
{ "schemaVersion": 1, "datasetVersion": "2026-01", "manifestSha256": "..." }
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

**M1 — monorepo mechanics.** Checkpoint frontend; final ignore rules; move frontend to `web/`; record
existing check failures; import curated pipeline to `pipeline/`; root README + Makefile; pin Python & Node;
confirm no cache/shards/secrets entered Git.

**M2 — minimal reliable pipeline.** `pyproject.toml`; extract WITS client, SDMX parser, collector, release
exporter; verify import indicator via pilot request; add `flow` to canonical schema; add the five focused
tests; replace silent failures with explicit request statuses in touched paths; deterministic gzip; stop
glob-unioning; minimal CI.

**M3 — first honest dual-flow release.** Export/import pilot; validate flow-specific WLD/ROW; full XPRT +
MPRT collection; reject incomplete reporters; canonical normalized matrix; manifest + checksums; generate
`overview.json` + per-country projections; commit both representations; update `current.json`.

**M4 — web migration.** `/all` loads `overview.json`; `/` loads one country projection; remove full-CSV
download, `createTotalRecords`, browser-side ×1000, mirror-derived imports, and browser-side canonical
aggregation; pass prepared datasets into charts; surface dataset version and coverage.

**M5 — application cleanup.** Move AI calls server-side; remove `{@html}` of model output; consolidate
duplicate slope/treemap chart components; improve responsiveness/accessibility; add tests around
stabilized behavior; set an explicit deployment adapter.

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
