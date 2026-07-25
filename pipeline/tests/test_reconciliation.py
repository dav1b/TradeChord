"""Flow-specific WLD/ROW reconciliation."""

from tradechord_pipeline.models import Flow, Observation
from tradechord_pipeline.validation.reconciliation import reconcile


def _obs(partner, flow, value, product="Total", reporter="USA", year=2020):
    return Observation(year, reporter, partner, product, flow, value)


def test_explicit_plus_row_equals_wld_passes():
    observations = [_obs("CAN", Flow.EXPORT, 90.0), _obs("ROW", Flow.EXPORT, 10.0)]
    wld = {("USA", 2020, "export", "Total"): 100.0}
    _, failures = reconcile(observations, wld, tolerance=0.02)
    assert failures == []


def test_short_coverage_fails():
    observations = [_obs("CAN", Flow.EXPORT, 50.0)]  # only 50 of 100, no ROW
    wld = {("USA", 2020, "export", "Total"): 100.0}
    _, failures = reconcile(observations, wld, tolerance=0.02)
    assert len(failures) == 1
    assert failures[0].rel_diff == 0.5


def test_within_tolerance_passes():
    observations = [_obs("CAN", Flow.EXPORT, 99.0)]  # 1% short, tolerance 2%
    wld = {("USA", 2020, "export", "Total"): 100.0}
    _, failures = reconcile(observations, wld, tolerance=0.02)
    assert failures == []


def test_flows_reconciled_separately():
    # export balances; import is short -> only import fails
    observations = [
        _obs("CAN", Flow.EXPORT, 100.0),
        _obs("CAN", Flow.IMPORT, 50.0),
    ]
    wld = {
        ("USA", 2020, "export", "Total"): 100.0,
        ("USA", 2020, "import", "Total"): 100.0,
    }
    _, failures = reconcile(observations, wld, tolerance=0.02)
    assert [f.flow for f in failures] == ["import"]
