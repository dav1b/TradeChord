# Data methodology

How TradeChord's trade data is sourced, normalized, and reconciled. This governs
what the dashboard may honestly claim.

## Source

- **Provider:** World Bank WITS (World Integrated Trade Solution), SDMX 2.1 REST API.
- **Base:** `https://wits.worldbank.org/API/V1`
- **Endpoint pattern:**
  `SDMX/V21/rest/data/df_wits_tradestats_trade/A.{reporter}.{partner}.{product}.{indicator}?startPeriod={y}&endPeriod={y}`
- See `WITSAPI_UserGuide.pdf` in this directory.

## Indicators and flows

Data is collected as two **directly reported flows**, not inferred from mirrors:

| Flow     | Indicator      | Meaning                          |
|----------|----------------|----------------------------------|
| `export` | `XPRT-TRD-VL`  | Reporter's reported export value |
| `import` | `MPRT-TRD-VL`  | Reporter's reported import value |

**Verified against the live API (2026-07), USA / WLD / Total / 2020:**

- `XPRT-TRD-VL` → `1,430,253,623` (thousand USD) = **$1.43 T** exports ✓
- `MPRT-TRD-VL` → `2,405,381,557` (thousand USD) = **$2.4 T** imports ✓
- `IMPT-TRD-VL` → empty (27-byte response) — **not a valid indicator.**

A stray legacy script used `IMPT-TRD-VL`; it is wrong. `MPRT-TRD-VL` is authoritative.
The one authoritative flow→indicator mapping lives in code (and is echoed into each
release manifest); historical scripts do not get a vote.

## Units

The API returns values in **thousands of current USD**. The pipeline normalizes to
**integer current USD** at release time: `value_usd = round(value_thousands * 1000)`.
Downstream code (web) never multiplies by 1000; it consumes `value_usd` directly.

## Balance

For a country X in a given year:

```
exports = records where reporter=X and flow=export
imports = records where reporter=X and flow=import
balance = exports − imports        (both reported directly)
```

National imports are **never** derived from other reporters' exports.

## Mirror flows (validation only)

X-reported imports from Y vs Y-reported exports to X are expected to differ
(valuation, timing, re-exports, CIF vs FOB). Discrepancy is a data-quality signal
for validation, **not** automatically a pipeline error.

## ROW (Rest of World) — computed per flow

```
export ROW = reporter's world export total (WLD) − sum(explicit export destinations)
import ROW = reporter's world import total (WLD) − sum(explicit import origins)
```

Import ROW is never inferred by reversing export records. Validation reconciles each
flow separately, within a documented numeric tolerance:

```
sum(explicit export partners) + export ROW ≈ export WLD
sum(explicit import partners) + import ROW ≈ import WLD
```

## Coverage status

Release `2026-07` is the first directly reported dual-flow release. National
totals and product totals reconcile to WITS world totals through flow-specific
ROW records.

Its named export and import partners were selected independently. Compatibility
release `2026-07.1` therefore marks a bilateral balance unavailable when one
side was not explicitly collected instead of treating the missing side as zero.
The next full collection uses the union of export and import rankings and
requests both flows for every named partner.

Named partners are a top-partner view, not exhaustive bilateral coverage.
Trade outside the explicit set is included in synthetic ROW. Release manifests
report coverage distributions and the worst reporter/product/year observations.
