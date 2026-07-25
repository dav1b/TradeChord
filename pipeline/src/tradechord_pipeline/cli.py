"""Command-line entry point for the TradeChord data pipeline.

    collect   -> gather a staging run from the WITS API      (data/staging/<run>)
    validate  -> check a staging run against the contract     [stub: M3]
    release   -> normalize, project, and publish a release    [stub: M3]

Staging output holds raw source values (thousands USD, one CSV per
reporter-year-flow). Normalization to integer USD happens at release time.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import UTC, datetime

from . import config as _config
from .collection.flows import CollectionConfig, build_client, collect_reporter_flow
from .models import Flow

_STAGING_FIELDS = ["year", "reporter", "partner", "product", "flow", "value_thousands"]


def _parse_years(expr: str) -> list[int]:
    years: set[int] = set()
    for token in expr.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            a, b = token.split("-", 1)
            years.update(range(int(a), int(b) + 1))
        else:
            years.add(int(token))
    return sorted(years)


def _resolve_reporters(spec: str) -> list[str]:
    upper = spec.upper()
    if upper == "ONE":
        return [_config.REPORTER]
    if upper == "TOP50":
        return list(_config.TOP_50_EXPORTERS)
    return [r.strip().upper() for r in spec.split(",") if r.strip()]


def _resolve_flows(spec: str) -> list[Flow]:
    spec = spec.lower()
    if spec in ("both", "all"):
        return [Flow.EXPORT, Flow.IMPORT]
    return [Flow(s.strip()) for s in spec.split(",") if s.strip()]


def _write_staging(run_dir: str, result) -> str:
    os.makedirs(run_dir, exist_ok=True)
    stem = f"{result.reporter}_{result.flow.value}_{result.year}"
    csv_path = os.path.join(run_dir, f"{stem}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_STAGING_FIELDS)
        writer.writeheader()
        for obs in result.observations:
            writer.writerow(
                {
                    "year": obs.year,
                    "reporter": obs.reporter,
                    "partner": obs.partner,
                    "product": obs.product,
                    "flow": obs.flow.value,
                    "value_thousands": obs.value_thousands,
                }
            )
    with open(os.path.join(run_dir, f"{stem}.manifest.json"), "w", encoding="utf-8") as f:
        json.dump(result.manifest, f, indent=2, sort_keys=True)
    return csv_path


def _cmd_collect(args: argparse.Namespace) -> int:
    reporters = _resolve_reporters(args.reporters)
    years = _parse_years(args.years)
    flows = _resolve_flows(args.flows)

    cc = CollectionConfig.from_module()
    cc.coverage_target = args.coverage_target
    cc.concurrency = args.concurrency
    cc.max_reqs_per_sec = args.max_rps
    if args.top_k is not None:
        cc.top_k_partners = args.top_k

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join(args.out, run_id)
    client = build_client(cc)  # one client => one global rate limiter for the run

    print(f"[collect] run={run_id} reporters={len(reporters)} years={years} "
          f"flows={[f.value for f in flows]}", file=sys.stderr)

    started = time.time()
    total_obs = 0
    unresolved = 0
    for reporter in reporters:
        for year in years:
            for flow in flows:
                result = collect_reporter_flow(
                    reporter, year, flow, cc=cc, client=client, exhaustive=args.exhaustive
                )
                _write_staging(run_dir, result)
                total_obs += len(result.observations)
                if result.statuses.had_unresolved_failures:
                    unresolved += 1
                print(
                    f"  {reporter} {year} {flow.value}: "
                    f"{len(result.observations)} obs  statuses={result.statuses.as_dict()}",
                    file=sys.stderr,
                )

    # Run-level manifest
    run_manifest = {
        "run_id": run_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "reporters": reporters,
        "years": years,
        "flows": [f.value for f in flows],
        "coverage_target": cc.coverage_target,
        "observations": total_obs,
        "reporter_year_flows_with_unresolved_failures": unresolved,
    }
    with open(os.path.join(run_dir, "run.manifest.json"), "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2, sort_keys=True)

    elapsed = time.time() - started
    print(f"[collect] done: {total_obs} observations in {elapsed:.1f}s -> {run_dir}", file=sys.stderr)
    if unresolved:
        print(f"[collect] WARNING: {unresolved} reporter-year-flows had unresolved failures "
              f"(a release will reject these).", file=sys.stderr)
    return 0


def _not_implemented(args: argparse.Namespace) -> int:
    print(f"[tradechord-data] '{args.command}' is not yet implemented (release exporter: M3).",
          file=sys.stderr)
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tradechord-data",
        description="Collect WITS trade data and publish versioned dashboard releases.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("collect", help="Collect a staging run from the WITS API")
    c.add_argument("--reporters", default="ONE", help="ONE | TOP50 | ISO3,ISO3,...")
    c.add_argument("--years", default=str(_config.END_YEAR), help="e.g. 2002-2005,2010")
    c.add_argument("--flows", default="both", help="export | import | both")
    c.add_argument("--out", default="data/staging", help="Staging root directory")
    c.add_argument("--coverage-target", dest="coverage_target", type=float,
                   default=getattr(_config, "COVERAGE_TARGET", 0.9))
    c.add_argument("--concurrency", type=int, default=_config.CONCURRENCY)
    c.add_argument("--max-rps", dest="max_rps", type=float, default=_config.MAX_REQS_PER_SEC)
    c.add_argument("--top-k", dest="top_k", type=int, default=None,
                   help="Cap ranked partners per product (default: config)")
    c.add_argument("--exhaustive", action="store_true",
                   help="Fetch all partners (ignore coverage short-circuit)")
    c.set_defaults(func=_cmd_collect)

    v = sub.add_parser("validate", help="Validate a staging run against the contract")
    v.set_defaults(func=_not_implemented)

    r = sub.add_parser("release", help="Publish a validated release")
    r.add_argument("--input", help="Path to the staging run to publish")
    r.add_argument("--version", help="Release version, e.g. 2026-01")
    r.set_defaults(func=_not_implemented)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
