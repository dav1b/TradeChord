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
