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

The production target is Vercel with `web/` configured as the project root.
The primary experience should be prerendered and served through Vercel's CDN;
runtime server functions are reserved for future requirements that cannot be
served statically. Python, WITS access, and data publication never run during
the Vercel build.

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

## Planned frontend evolution

The next frontend is planned as one continuous visual scene rather than a set
of independent dashboard drill-downs. Country, partner, flow, product, year,
value, share, and balance objects will keep stable semantic identities while
their visual representations transform between overview, bilateral,
composition, history, and contribution states.

This direction does not change the ownership boundary above. The pipeline
continues to produce validated analytical projections; the scene layer owns
state, geometry, visual continuity, URL navigation, motion, and accessible
alternatives. See the frontend direction in the
[refactor roadmap](./refactor-roadmap.md#7-revised-frontend-direction-one-continuous-visual-scene).

See [data-methodology.md](./data-methodology.md) for analytical semantics and
[data-release.md](./data-release.md) for operating instructions. The
[refactor roadmap](./refactor-roadmap.md) records completed work, immediate
next steps, possible improvements, and open decisions.
See [deployment-performance.md](./deployment-performance.md) for Vercel
configuration, caching, payload strategy, performance budgets, build gates,
and production measurement.
