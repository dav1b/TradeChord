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
from .collection.flows import (
    CollectionConfig,
    build_client,
    collect_reporter_flow,
    complete_partner_union,
)
from .models import Flow
from .release import DEFAULT_TOLERANCE, run_release, run_reproject, run_validate
from .verification import verify_release

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
    stem = f"{result.reporter}_{result.flow.value}"
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
    cc.concurrency = args.concurrency
    cc.max_reqs_per_sec = args.max_rps

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = os.path.join(args.out, run_id)
    client = build_client(cc)  # one client => one global rate limiter for the run

    print(f"[collect] run={run_id} reporters={len(reporters)} "
          f"years={min(years)}-{max(years)} flows={[f.value for f in flows]} "
          f"top_k={args.top_k}", file=sys.stderr)

    started = time.time()
    total_obs = 0
    unresolved = 0
    for reporter in reporters:
        provisional = [
            collect_reporter_flow(
                reporter, years, flow, cc=cc, client=client, top_k=args.top_k
            )
            for flow in flows
        ]
        if set(flows) == {Flow.EXPORT, Flow.IMPORT}:
            partner_union = sorted(
                {
                    partner
                    for result in provisional
                    for partner in result.manifest.get("ranked_partner_codes", [])
                }
            )
            results = [
                complete_partner_union(result, partner_union, cc=cc, client=client)
                for result in provisional
            ]
        else:
            results = provisional

        for result in results:
            _write_staging(run_dir, result)
            total_obs += len(result.observations)
            if result.statuses.had_unresolved_failures:
                unresolved += 1
            print(
                f"  {reporter} {result.flow.value}: {len(result.observations)} obs  "
                f"statuses={result.statuses.as_dict()}",
                file=sys.stderr,
            )

    run_manifest = {
        "run_id": run_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "reporters": reporters,
        "years": years,
        "flows": [f.value for f in flows],
        "top_k": args.top_k,
        "observations": total_obs,
        "reporter_flows_with_unresolved_failures": unresolved,
    }
    with open(os.path.join(run_dir, "run.manifest.json"), "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2, sort_keys=True)

    elapsed = time.time() - started
    print(f"[collect] done: {total_obs} observations in {elapsed:.1f}s -> {run_dir}", file=sys.stderr)
    if unresolved:
        print(f"[collect] WARNING: {unresolved} reporter-flows had unresolved failures "
              f"(a release will reject these).", file=sys.stderr)
    return 0


def _print_report(report) -> None:
    print(f"[validate] {report.summary()}", file=sys.stderr)
    for name, statuses in report.unresolved[:10]:
        print(f"    unresolved failure: {name} {statuses}", file=sys.stderr)
    for item in report.recon_failures[:10]:
        print(f"    reconcile: {item.reporter} {item.year} {item.flow} {item.product} "
              f"rel_diff={item.rel_diff:.3f}", file=sys.stderr)
    for key in report.duplicates[:10]:
        print(f"    duplicate key: {key}", file=sys.stderr)


def _cmd_validate(args: argparse.Namespace) -> int:
    report = run_validate(args.input, tolerance=args.tolerance)
    _print_report(report)
    if report.ok:
        print("[validate] OK", file=sys.stderr)
        return 0
    print("[validate] FAILED", file=sys.stderr)
    return 1


def _cmd_release(args: argparse.Namespace) -> int:
    path, report = run_release(
        args.input,
        args.version,
        args.releases_root,
        args.web_root,
        tolerance=args.tolerance,
        force=args.force,
    )
    _print_report(report)
    if path is None:
        print("[release] REJECTED: validation failed", file=sys.stderr)
        return 1
    print(f"[release] wrote {path}", file=sys.stderr)
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    errors = verify_release(args.release, args.repo_root)
    for error in errors:
        print(f"[verify] {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"[verify] OK: {args.release}", file=sys.stderr)
    return 0


def _cmd_reproject(args: argparse.Namespace) -> int:
    path = run_reproject(
        args.source,
        args.version,
        args.releases_root,
        args.web_root,
        force=args.force,
    )
    print(f"[reproject] wrote {path}", file=sys.stderr)
    return 0


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
    c.add_argument("--concurrency", type=int, default=_config.CONCURRENCY)
    c.add_argument("--max-rps", dest="max_rps", type=float, default=_config.MAX_REQS_PER_SEC)
    c.add_argument("--top-k", dest="top_k", type=int, default=15,
                   help="Number of top partners tracked across years (rest -> ROW)")
    c.set_defaults(func=_cmd_collect)

    v = sub.add_parser("validate", help="Validate a staging run against the contract")
    v.add_argument("--input", required=True, help="Path to the staging run")
    v.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE,
                   help="Reconciliation relative tolerance (default 0.02)")
    v.set_defaults(func=_cmd_validate)

    r = sub.add_parser("release", help="Publish a validated release")
    r.add_argument("--input", required=True, help="Path to the staging run to publish")
    r.add_argument("--version", required=True, help="Release version, e.g. 2026-01")
    r.add_argument("--releases-root", dest="releases_root", default="data/releases",
                   help="Root directory for committed releases")
    r.add_argument("--web-root", dest="web_root", default="web/static/data",
                   help="Root directory for committed browser projections")
    r.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    r.add_argument("--force", action="store_true", help="Overwrite an existing release version")
    r.set_defaults(func=_cmd_release)

    verify = sub.add_parser("verify", help="Verify committed canonical and web artifacts")
    verify.add_argument("--release", required=True, help="Path to data/releases/<version>")
    verify.add_argument("--repo-root", default=".", help="Repository root")
    verify.set_defaults(func=_cmd_verify)

    reproject = sub.add_parser(
        "reproject", help="Publish a new version from an existing canonical matrix"
    )
    reproject.add_argument("--source", required=True, help="Existing release directory")
    reproject.add_argument("--version", required=True)
    reproject.add_argument("--releases-root", default="data/releases")
    reproject.add_argument("--web-root", default="web/static/data")
    reproject.add_argument("--force", action="store_true")
    reproject.set_defaults(func=_cmd_reproject)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
