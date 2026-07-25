"""Command-line entry point for the TradeChord data pipeline.

Subcommands mirror the release lifecycle:

    collect   -> gather a staging run from the WITS API      (data/staging/<run>)
    validate  -> check a staging run against the contract
    release   -> normalize, project, and publish a release   (data/releases/<version>)

The subcommands are stubs until the collector (M2) and release exporter (M3)
land. They are wired now so the entry point and Makefile targets resolve.
"""

from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tradechord-data",
        description="Collect WITS trade data and publish versioned dashboard releases.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("collect", help="Collect a staging run from the WITS API")
    sub.add_parser("validate", help="Validate a staging run against the contract")

    p_release = sub.add_parser("release", help="Publish a validated release")
    p_release.add_argument("--input", help="Path to the staging run to publish")
    p_release.add_argument("--version", help="Release version, e.g. 2026-01")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    print(
        f"[tradechord-data] '{args.command}' is not yet implemented "
        f"(collector: M2, release exporter: M3).",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
