"""Collection config, partner coordination, and WITS code corrections."""

from tradechord_pipeline.collection import flows
from tradechord_pipeline.collection.flows import CollectionConfig, CollectionResult
from tradechord_pipeline.models import Flow, Observation, StatusRecorder


def test_partner_code_fixes_applied():
    cc = CollectionConfig.from_module()
    universe = cc.partner_universe(Flow.EXPORT, "USA")
    # ROU/TWN 404 at WITS; corrected to ROM/OAS (see WITS_PARTNER_CODE_FIXES).
    assert "ROM" in universe and "OAS" in universe
    assert "ROU" not in universe and "TWN" not in universe


def test_reporter_excluded_from_its_own_partners():
    cc = CollectionConfig.from_module()
    assert "USA" not in cc.partner_universe(Flow.EXPORT, "USA")


def test_universes_are_iso3_and_nonempty():
    cc = CollectionConfig.from_module()
    exp = cc.partner_universe(Flow.EXPORT, "USA")
    imp = cc.partner_universe(Flow.IMPORT, "USA")
    assert exp and imp
    assert all(len(c) == 3 and c.isalpha() for c in exp + imp)


def test_partner_union_fetches_missing_flow_and_recomputes_row(monkeypatch):
    cc = CollectionConfig.from_module()
    cc.concurrency = 1
    result = CollectionResult(
        reporter="USA",
        years=[2022],
        flow=Flow.EXPORT,
        observations=[
            Observation(2022, "USA", "CAN", "01-05_Animal", Flow.EXPORT, 90.0),
            Observation(2022, "USA", "ROW", "01-05_Animal", Flow.EXPORT, 30.0),
        ],
        statuses=StatusRecorder(),
        manifest={
            "probe": {"product_all": True},
            "ranked_partner_codes": ["CAN"],
            "wld_totals": {"01-05_Animal": {"2022": 120.0}},
        },
    )

    def fake_fetch(*args, **kwargs):
        return [Observation(2022, "USA", "MEX", "01-05_Animal", Flow.EXPORT, 20.0)]

    monkeypatch.setattr(flows, "_fetch", fake_fetch)
    completed = flows.complete_partner_union(
        result, ["CAN", "MEX"], cc=cc, client=object()
    )

    values = {
        (row.partner, row.product, row.year): row.value_thousands
        for row in completed.observations
    }
    assert values[("MEX", "01-05_Animal", 2022)] == 20.0
    assert values[("ROW", "01-05_Animal", 2022)] == 10.0
    assert completed.manifest["partner_strategy"] == "union_of_export_import_top_k"
