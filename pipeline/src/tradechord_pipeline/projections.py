"""Browser-ready projections generated from the canonical release.

The web app consumes these, never the full matrix:

    <web_root>/<version>/overview.json          -> /all route
    <web_root>/<version>/countries.json         -> country picker
    <web_root>/<version>/countries/<CODE>.json  -> / route (per country)

Projections are derived from the dual-flow canonical records, so exports,
imports, and balance are all real (not mirror-derived). Output is deterministic
(sorted keys, no embedded timestamps).
"""

from __future__ import annotations

import json
import os
from collections import defaultdict

from .models import Flow
from .normalize import CanonicalRecord

SCHEMA_VERSION = 1


def _bucket_by_reporter(records: list[CanonicalRecord]) -> dict[str, list[CanonicalRecord]]:
    buckets: dict[str, list[CanonicalRecord]] = defaultdict(list)
    for r in records:
        buckets[r.reporter].append(r)
    return buckets


def _totals_by_year(recs: list[CanonicalRecord]) -> dict[int, dict[str, int]]:
    exp: dict[int, int] = defaultdict(int)
    imp: dict[int, int] = defaultdict(int)
    for r in recs:
        if r.flow is Flow.EXPORT:
            exp[r.year] += r.value_usd
        else:
            imp[r.year] += r.value_usd
    years = sorted(set(exp) | set(imp))
    return {
        y: {"exportsUsd": exp.get(y, 0), "importsUsd": imp.get(y, 0),
            "balanceUsd": exp.get(y, 0) - imp.get(y, 0)}
        for y in years
    }


def _breakdown(recs: list[CanonicalRecord], year: int, name: str) -> list[dict]:
    """Per-partner or per-product export/import/balance for one year."""
    attr = "partner" if name == "partner" else "product"
    exp: dict[str, int] = defaultdict(int)
    imp: dict[str, int] = defaultdict(int)
    for r in recs:
        if r.year != year:
            continue
        key = getattr(r, attr)
        if r.flow is Flow.EXPORT:
            exp[key] += r.value_usd
        else:
            imp[key] += r.value_usd
    total_exp = sum(exp.values())
    rows = []
    for key in set(exp) | set(imp):
        e, i = exp.get(key, 0), imp.get(key, 0)
        rows.append({
            name: key,
            "exportsUsd": e,
            "importsUsd": i,
            "balanceUsd": e - i,
            "exportShare": (e / total_exp) if total_exp else 0.0,
        })
    rows.sort(key=lambda d: (-d["exportsUsd"], d[name]))
    return rows


def build_country_projection(country: str, recs: list[CanonicalRecord], dataset_version: str) -> dict:
    years = sorted({r.year for r in recs})
    totals = _totals_by_year(recs)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "datasetVersion": dataset_version,
        "country": country,
        "years": years,
        "summaryByYear": {str(y): totals[y] for y in years},
        "partnersByYear": {str(y): _breakdown(recs, y, "partner") for y in years},
        "productsByYear": {str(y): _breakdown(recs, y, "product") for y in years},
    }


def build_overview(records: list[CanonicalRecord], dataset_version: str) -> dict:
    buckets = _bucket_by_reporter(records)
    years_all = sorted({r.year for r in records})
    reporters = []
    for code in sorted(buckets):
        totals = _totals_by_year(buckets[code])
        reporters.append({
            "code": code,
            "totalsByYear": [{"year": y, **totals[y]} for y in sorted(totals)],
        })
    return {
        "schemaVersion": SCHEMA_VERSION,
        "datasetVersion": dataset_version,
        "defaultYear": years_all[-1] if years_all else None,
        "reporters": reporters,
    }


def _dump(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_projections(records: list[CanonicalRecord], dataset_version: str, version_dir: str) -> int:
    """Write overview + per-country projections into ``version_dir``. Returns count."""
    os.makedirs(os.path.join(version_dir, "countries"), exist_ok=True)
    buckets = _bucket_by_reporter(records)

    _dump(os.path.join(version_dir, "overview.json"), build_overview(records, dataset_version))
    _dump(os.path.join(version_dir, "countries.json"), {
        "schemaVersion": SCHEMA_VERSION,
        "datasetVersion": dataset_version,
        "countries": sorted(buckets),
    })
    for code in sorted(buckets):
        _dump(
            os.path.join(version_dir, "countries", f"{code}.json"),
            build_country_projection(code, buckets[code], dataset_version),
        )
    return len(buckets)
