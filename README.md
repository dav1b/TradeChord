# TradeChord

Monorepo for the TradeChord trade-flows dashboard.

- **`web/`** — SvelteKit + D3 dashboard (Node).
- **`pipeline/`** — Python tool that collects World Bank WITS data and publishes a versioned release.
- **`data/releases/<version>/`** — canonical, committed data releases (archival matrix + manifest).
- **`web/static/data/<version>/`** — committed browser projections the dashboard reads.

## Core principle

A fresh clone runs the dashboard with **Node alone**. Python and WITS access are required **only** when
deliberately publishing a new data release. The pipeline is an offline release tool, never part of a web
build or deploy.

See [`plan.md`](./plan.md) for the full architecture and refactor plan of record.

## Web development (Node only)

```bash
cd web
npm install      # Node 22 (see .nvmrc)
npm run dev
```

The dashboard loads the committed release named by `web/static/data/current.json`.

## Publishing a data release (offline, manual)

Requires Python and hits the WITS API. Only run when refreshing data.

```bash
make pipeline-install
make data-collect      # -> data/staging/<run>
make data-validate
make data-release      # -> data/releases/<version>/ + web/static/data/<version>/
```

See [`docs/data-release.md`](./docs/data-release.md) and [`docs/data-methodology.md`](./docs/data-methodology.md).

## Layout

```
web/        SvelteKit dashboard (Node)
pipeline/   WITS collection + release tool (Python)
data/       contracts/ (schemas) and releases/ (committed canonical artifacts)
docs/       architecture, methodology, release process
plan.md     refactor plan of record
```
