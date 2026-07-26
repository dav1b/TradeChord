"""Publish a validated data release from a staging run.

Pipeline: load staging -> validate (acceptance gate) -> normalize -> write a
deterministic release directory (canonical gzipped matrix + manifest + checksums).

Browser projections (overview/per-country) are added in a later milestone; this
module produces the canonical archival artifact under data/releases/<version>/.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from glob import glob

from . import projections
from .models import INDICATOR_BY_FLOW, Flow, Observation
from .normalize import CANONICAL_FIELDS, CanonicalRecord, normalize
from .validation import completeness, reconciliation

SCHEMA_VERSION = 1
DEFAULT_TOLERANCE = 0.02

_VALUATION = {
    Flow.EXPORT: "reported export value",
    Flow.IMPORT: "reported import value",
}


# --------------------------------------------------------------------------- #
# Load staging
# --------------------------------------------------------------------------- #

@dataclass
class Staging:
    run_dir: str
    observations: list[Observation]
    per_file_manifests: dict[str, dict]
    run_manifest: dict
    wld_totals: dict[reconciliation.ReconKey, float]


def load_staging(run_dir: str) -> Staging:
    observations: list[Observation] = []
    per_file: dict[str, dict] = {}
    wld_totals: dict[reconciliation.ReconKey, float] = {}

    for csv_path in sorted(glob(os.path.join(run_dir, "*.csv"))):
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                observations.append(
                    Observation(
                        year=int(row["year"]),
                        reporter=row["reporter"],
                        partner=row["partner"],
                        product=row["product"],
                        flow=Flow(row["flow"]),
                        value_thousands=float(row["value_thousands"]),
                    )
                )

    for man_path in sorted(glob(os.path.join(run_dir, "*.manifest.json"))):
        name = os.path.basename(man_path)
        if name == "run.manifest.json":
            continue
        with open(man_path, encoding="utf-8") as f:
            manifest = json.load(f)
        per_file[name] = manifest
        reporter = manifest.get("reporter")
        year = manifest.get("year")
        flow = manifest.get("flow")
        for product, total in (manifest.get("wld_totals") or {}).items():
            wld_totals[(reporter, int(year), flow, product)] = float(total)

    run_manifest = {}
    run_path = os.path.join(run_dir, "run.manifest.json")
    if os.path.isfile(run_path):
        with open(run_path, encoding="utf-8") as f:
            run_manifest = json.load(f)

    return Staging(run_dir, observations, per_file, run_manifest, wld_totals)


# --------------------------------------------------------------------------- #
# Validate
# --------------------------------------------------------------------------- #

@dataclass
class ValidationReport:
    unresolved: list = field(default_factory=list)
    duplicates: list = field(default_factory=list)
    recon_failures: list = field(default_factory=list)
    invalid: list = field(default_factory=list)
    missing_flows: set = field(default_factory=set)

    @property
    def ok(self) -> bool:
        return not (
            self.unresolved
            or self.duplicates
            or self.recon_failures
            or self.invalid
            or self.missing_flows
        )

    def summary(self) -> str:
        return (
            f"unresolved_failures={len(self.unresolved)} "
            f"duplicate_keys={len(self.duplicates)} "
            f"reconciliation_failures={len(self.recon_failures)} "
            f"invalid_values={len(self.invalid)} "
            f"missing_flows={sorted(self.missing_flows)}"
        )


def validate(
    staging: Staging,
    records: list[CanonicalRecord],
    tolerance: float = DEFAULT_TOLERANCE,
    expected_flows: set[str] | None = None,
) -> ValidationReport:
    _, recon_failures = reconciliation.reconcile(
        staging.observations, staging.wld_totals, tolerance=tolerance
    )
    return ValidationReport(
        unresolved=completeness.unresolved_failures(staging.per_file_manifests),
        duplicates=completeness.duplicate_keys(staging.observations),
        recon_failures=recon_failures,
        invalid=completeness.invalid_values(records),
        missing_flows=completeness.missing_flows(
            staging.per_file_manifests, expected_flows or set()
        ),
    )


# --------------------------------------------------------------------------- #
# Manifest + write
# --------------------------------------------------------------------------- #

def _coverage_summary(staging: Staging, flows: list[str]) -> dict:
    summary: dict[str, dict] = {}
    for flow in flows:
        achieved: list[float] = []
        method = "unknown"
        for m in staging.per_file_manifests.values():
            if m.get("flow") != flow:
                continue
            cov = m.get("coverage")
            if cov:
                method = "coverage_target"
                achieved.extend(c["achieved"] for c in cov.values())
            elif m.get("probe", {}).get("product_all"):
                method = "product_all_batch"
        summary[flow] = {
            "method": method,
            "min_achieved": min(achieved) if achieved else None,
            "reconciled": True,
        }
    return summary


def build_manifest(version: str, staging: Staging, records: list[CanonicalRecord]) -> dict:
    reporters = sorted({r.reporter for r in records})
    products = sorted({r.product for r in records if r.product != "Total"})
    flows = sorted({r.flow.value for r in records})
    years = sorted({r.year for r in records})

    return {
        "schemaVersion": SCHEMA_VERSION,
        "datasetVersion": version,
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source": {
            "provider": "World Bank WITS",
            "sourceUnit": "thousands_current_usd",
            "flows": {
                flow.value: {
                    "sourceIndicator": INDICATOR_BY_FLOW[flow],
                    "valuation": _VALUATION[flow],
                }
                for flow in Flow
                if flow.value in flows
            },
        },
        "artifactUnit": "current_usd",
        "years": {"start": years[0], "end": years[-1]} if years else {},
        "reporters": reporters,
        "products": products,
        "flows": flows,
        "coverage": _coverage_summary(staging, flows),
        "row": {
            "synthetic": True,
            "definition": "Reporter WLD total minus explicitly collected partners, per flow.",
        },
        "artifacts": {
            "matrix": {"path": "trade_matrix.csv.gz", "sha256": None, "records": len(records)},
        },
    }


def _write_matrix_gz(records: list[CanonicalRecord], path: str) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(CANONICAL_FIELDS)
    for r in records:
        writer.writerow([r.year, r.reporter, r.partner, r.product, r.flow.value, r.value_usd])
    data = buf.getvalue().encode("utf-8")
    with open(path, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        gz.write(data)
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_release(
    records: list[CanonicalRecord], manifest: dict, out_dir: str, force: bool = False
) -> tuple[str, str]:
    """Build the release in a temp dir, then promote atomically to ``out_dir``.

    Returns (out_dir, manifest_sha256).
    """
    if os.path.exists(out_dir):
        if not force:
            raise FileExistsError(f"release already exists: {out_dir} (use --force)")
        shutil.rmtree(out_dir)

    parent = os.path.dirname(os.path.abspath(out_dir))
    os.makedirs(parent, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix=".tmp-release-", dir=parent)
    try:
        matrix_sha = _write_matrix_gz(records, os.path.join(tmp, "trade_matrix.csv.gz"))
        manifest["artifacts"]["matrix"]["sha256"] = matrix_sha

        with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write("\n")
        with open(os.path.join(tmp, "manifest.json"), "rb") as f:
            manifest_sha = hashlib.sha256(f.read()).hexdigest()

        with open(os.path.join(tmp, "checksums.txt"), "w", encoding="utf-8") as f:
            f.write(f"{matrix_sha}  trade_matrix.csv.gz\n")
            f.write(f"{manifest_sha}  manifest.json\n")

        os.rename(tmp, out_dir)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return out_dir, manifest_sha


def write_web_projections(
    records: list[CanonicalRecord], version: str, web_root: str, manifest_sha: str, force: bool = False
) -> str:
    """Write committed browser projections under web_root/<version>/ + current.json."""
    version_dir = os.path.join(web_root, version)
    if os.path.exists(version_dir):
        if not force:
            raise FileExistsError(f"web projections already exist: {version_dir} (use --force)")
        shutil.rmtree(version_dir)
    os.makedirs(web_root, exist_ok=True)
    projections.write_projections(records, version, version_dir)

    with open(os.path.join(web_root, "current.json"), "w", encoding="utf-8") as f:
        json.dump(
            {"schemaVersion": SCHEMA_VERSION, "datasetVersion": version, "manifestSha256": manifest_sha},
            f,
            indent=2,
            sort_keys=True,
        )
        f.write("\n")
    return version_dir


# --------------------------------------------------------------------------- #
# Entry points used by the CLI
# --------------------------------------------------------------------------- #

def run_validate(run_dir: str, tolerance: float = DEFAULT_TOLERANCE) -> ValidationReport:
    staging = load_staging(run_dir)
    records = normalize(staging.observations)
    return validate(staging, records, tolerance=tolerance)


def run_release(
    run_dir: str,
    version: str,
    releases_root: str,
    web_root: str,
    tolerance: float = DEFAULT_TOLERANCE,
    strict: bool = True,
    force: bool = False,
) -> tuple[str | None, ValidationReport]:
    staging = load_staging(run_dir)
    records = normalize(staging.observations)
    report = validate(staging, records, tolerance=tolerance)
    if strict and not report.ok:
        return None, report

    manifest = build_manifest(version, staging, records)
    out_dir = os.path.join(releases_root, version)
    path, manifest_sha = write_release(records, manifest, out_dir, force=force)
    write_web_projections(records, version, web_root, manifest_sha, force=force)
    return path, report
