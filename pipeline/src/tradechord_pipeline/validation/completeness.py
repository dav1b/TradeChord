"""Structural checks a release must pass (independent of reconciliation)."""

from __future__ import annotations

from ..models import Observation
from ..normalize import CanonicalRecord

_FAILURE_STATUSES = ("http_error", "retry_exhausted", "parse_error")


def duplicate_keys(observations: list[Observation]) -> list[tuple]:
    """Compound keys (year, reporter, partner, product, flow) that appear twice."""
    seen: set[tuple] = set()
    dups: set[tuple] = set()
    for o in observations:
        key = (o.year, o.reporter, o.partner, o.product, o.flow.value)
        if key in seen:
            dups.add(key)
        else:
            seen.add(key)
    return sorted(dups)


def unresolved_failures(per_file_manifests: dict[str, dict]) -> list[tuple[str, dict]]:
    """Staging files whose collection had non-empty failure statuses."""
    bad: list[tuple[str, dict]] = []
    for name, manifest in sorted(per_file_manifests.items()):
        statuses = manifest.get("statuses", {})
        if any(statuses.get(s) for s in _FAILURE_STATUSES):
            bad.append((name, {s: statuses.get(s, 0) for s in _FAILURE_STATUSES if statuses.get(s)}))
    return bad


def invalid_values(records: list[CanonicalRecord]) -> list[CanonicalRecord]:
    """Records whose value is non-integer or negative."""
    return [r for r in records if not isinstance(r.value_usd, int) or r.value_usd < 0]


def missing_flows(
    per_file_manifests: dict[str, dict], expected_flows: set[str]
) -> set[str]:
    """Expected flows that never appear in the staging run."""
    present = {m.get("flow") for m in per_file_manifests.values()}
    return expected_flows - present


def staging_shape_issues(
    per_file_manifests: dict[str, dict], run_manifest: dict
) -> list[str]:
    """Validate the requested reporter × flow × year shape of a staging run."""
    reporters = set(run_manifest.get("reporters") or [])
    flows = set(run_manifest.get("flows") or [])
    years = set(run_manifest.get("years") or [])
    if not reporters or not flows or not years:
        return ["run manifest must declare non-empty reporters, flows, and years"]

    by_pair: dict[tuple[str, str], dict] = {}
    issues: list[str] = []
    for name, manifest in sorted(per_file_manifests.items()):
        pair = (manifest.get("reporter"), manifest.get("flow"))
        if pair in by_pair:
            issues.append(f"duplicate reporter-flow manifest: {pair[0]} {pair[1]}")
        by_pair[pair] = manifest
        if pair[0] not in reporters or pair[1] not in flows:
            issues.append(f"unexpected reporter-flow manifest: {name}")
        manifest_years = set(manifest.get("years") or [])
        if manifest_years != years:
            issues.append(
                f"year mismatch for {name}: expected {sorted(years)}, "
                f"found {sorted(manifest_years)}"
            )
        for product, year_map in (manifest.get("wld_totals") or {}).items():
            product_years = {int(year) for year in year_map}
            if product_years != years:
                issues.append(
                    f"WLD year mismatch for {name} {product}: "
                    f"expected {sorted(years)}, found {sorted(product_years)}"
                )

    for reporter in sorted(reporters):
        for flow in sorted(flows):
            if (reporter, flow) not in by_pair:
                issues.append(f"missing reporter-flow manifest: {reporter} {flow}")
        if {"export", "import"} <= flows:
            export = by_pair.get((reporter, "export"))
            imported = by_pair.get((reporter, "import"))
            if export and imported:
                export_partners = set(export.get("ranked_partner_codes") or [])
                import_partners = set(imported.get("ranked_partner_codes") or [])
                if export_partners != import_partners:
                    issues.append(f"export/import partner union mismatch: {reporter}")
                for flow_name, manifest in (("export", export), ("import", imported)):
                    if manifest.get("partner_strategy") != "union_of_export_import_top_k":
                        issues.append(
                            f"uncoordinated partner strategy: {reporter} {flow_name}"
                        )
    return issues
