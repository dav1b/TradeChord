"""Structural completeness checks."""

from tradechord_pipeline.models import Flow, Observation
from tradechord_pipeline.normalize import CanonicalRecord
from tradechord_pipeline.validation import completeness


def test_duplicate_keys_detected():
    o = Observation(2020, "USA", "CAN", "Total", Flow.EXPORT, 1.0)
    assert (2020, "USA", "CAN", "Total", "export") in completeness.duplicate_keys([o, o])


def test_no_duplicates_across_flows():
    obs = [
        Observation(2020, "USA", "CAN", "Total", Flow.EXPORT, 1.0),
        Observation(2020, "USA", "CAN", "Total", Flow.IMPORT, 1.0),
    ]
    assert completeness.duplicate_keys(obs) == []


def test_unresolved_failures_flagged():
    manifests = {
        "a.json": {"flow": "export", "statuses": {"success": 10, "http_error": 2}},
        "b.json": {"flow": "import", "statuses": {"success": 10}},
    }
    bad = completeness.unresolved_failures(manifests)
    assert len(bad) == 1 and bad[0][0] == "a.json"


def test_not_found_is_not_a_failure():
    # 404 (no series for the key) is data absence, not a collection failure.
    manifests = {"a.json": {"flow": "export", "statuses": {"success": 10, "not_found": 3}}}
    assert completeness.unresolved_failures(manifests) == []


def test_invalid_values_flagged():
    good = CanonicalRecord(2020, "USA", "CAN", "Total", Flow.EXPORT, 100)
    negative = CanonicalRecord(2020, "USA", "CAN", "Total", Flow.EXPORT, -1)
    assert completeness.invalid_values([good, negative]) == [negative]


def test_missing_flows():
    manifests = {"a.json": {"flow": "export"}}
    assert completeness.missing_flows(manifests, {"export", "import"}) == {"import"}
