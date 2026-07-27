"""Projection builders + contract validation."""

import json
from pathlib import Path

import jsonschema

from tradechord_pipeline.models import Flow, Observation
from tradechord_pipeline.normalize import normalize
from tradechord_pipeline.projections import (
    build_country_projection,
    build_overview,
    write_projections,
)

CONTRACTS = Path(__file__).resolve().parents[2] / "data" / "contracts"


def _records():
    # values in thousands; normalize -> integer USD (x1000)
    obs = [
        Observation(2022, "USA", "CAN", "84-85_MachElec", Flow.EXPORT, 100.0),
        Observation(2022, "USA", "CAN", "84-85_MachElec", Flow.IMPORT, 40.0),
        Observation(2022, "USA", "CHN", "84-85_MachElec", Flow.EXPORT, 50.0),
        Observation(2022, "USA", "CHN", "84-85_MachElec", Flow.IMPORT, 200.0),
        Observation(2022, "USA", "ROW", "84-85_MachElec", Flow.EXPORT, 10.0),
    ]
    return normalize(obs)


def test_country_summary_is_dual_flow():
    d = build_country_projection("USA", _records(), "v1")
    s = d["summaryByYear"]["2022"]
    # exports 160k, imports 240k -> USD x1000
    assert (s["exportsUsd"], s["importsUsd"], s["balanceUsd"]) == (160_000, 240_000, -80_000)


def test_partners_ranked_with_real_imports_and_share():
    d = build_country_projection("USA", _records(), "v1")
    partners = d["partnersByYear"]["2022"]
    assert [p["partner"] for p in partners] == ["CAN", "CHN", "ROW"]
    can = partners[0]
    assert can["importsUsd"] == 40_000 and can["balanceUsd"] == 60_000
    assert can["exportAvailable"] and can["importAvailable"]
    assert abs(can["exportShare"] - 0.625) < 1e-9  # 100 / 160


def test_overview_reports_reporter_totals():
    ov = build_overview(_records(), "v1")
    assert ov["defaultYear"] == 2022
    assert [r["code"] for r in ov["reporters"]] == ["USA"]
    assert ov["reporters"][0]["totalsByYear"][0]["balanceUsd"] == -80_000


def test_cross_cells_are_partner_product_dual_flow():
    d = build_country_projection("USA", _records(), "v1")
    assert d["crossYear"] == 2022
    can = next(c for c in d["crossCells"] if c["partner"] == "CAN")
    assert (can["product"], can["exportsUsd"], can["importsUsd"], can["balanceUsd"]) == (
        "84-85_MachElec",
        100_000,
        40_000,
        60_000,
    )
    assert can["exportAvailable"] and can["importAvailable"]


def test_uncollected_bilateral_flow_is_not_reported_as_zero_balance():
    records = normalize(
        [Observation(2022, "USA", "NLD", "84-85_MachElec", Flow.EXPORT, 10.0)]
    )
    projection = build_country_projection("USA", records, "v1")
    partner = projection["partnersByYear"]["2022"][0]
    assert partner["exportsUsd"] == 10_000
    assert partner["importsUsd"] == 0
    assert partner["exportAvailable"] is True
    assert partner["importAvailable"] is False
    assert partner["balanceUsd"] is None


def test_generated_projection_matches_schema():
    schema = json.loads((CONTRACTS / "projection.schema.json").read_text())
    jsonschema.validate(build_country_projection("USA", _records(), "v1"), schema)


def test_write_projections_emits_expected_files(tmp_path):
    count = write_projections(_records(), "v1", str(tmp_path))
    assert count == 1
    assert (tmp_path / "overview.json").exists()
    assert (tmp_path / "countries.json").exists()
    assert (tmp_path / "countries" / "USA.json").exists()
