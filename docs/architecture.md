# Architecture

TradeChord is one repository with two independent toolchains joined by an
immutable, versioned data release.

## Runtime

The SvelteKit application under `web/` requires Node only. It reads
`web/static/data/current.json`, then fetches either:

- `<version>/overview.json` for `/all`, or
- `<version>/countries/<ISO3>.json` for `/`.

The browser never downloads the canonical matrix and never performs canonical
trade aggregation.

## Offline data production

The Python package under `pipeline/` is an offline release tool:

```
WITS API
  → explicit request outcomes
  → data/staging/<run>          (ignored, ephemeral)
  → validation gate
  → normalized canonical matrix
  → canonical + browser artifacts
```

The collector ranks export and import partners independently, takes their
union, and fetches both reported flows for every named partner. Flow-specific
ROW values reconcile explicit partners to WITS world totals.

## Published release

`data/releases/<version>/` contains the deterministic canonical matrix,
manifest, and checksums. `web/static/data/<version>/` contains browser
projections. The manifest hashes both representations; `current.json` is
updated last and selects the active version.

## Ownership

The pipeline owns units, flows, reconciliation, totals, shares, availability,
and projection generation. The web app owns selection, top-N presentation,
layout, formatting, interaction, and accessibility.

See [data-methodology.md](./data-methodology.md) for analytical semantics and
[data-release.md](./data-release.md) for operating instructions.
