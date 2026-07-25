"""Contract smoke: generated manifest and canonical record validate against the
data/contracts schemas. This is the web/pipeline boundary, so it is worth a test."""

import json
from pathlib import Path

import jsonschema
import pytest

from tradechord_pipeline.models import Flow, Observation
from tradechord_pipeline.normalize import normalize
from tradechord_pipeline.release import Staging, build_manifest

CONTRACTS = Path(__file__).resolve().parents[2] / "data" / "contracts"


def _staging(observations):
    return Staging(
        run_dir="",
        observations=observations,
        per_file_manifests={},
        run_manifest={},
        wld_totals={},
    )


def test_generated_manifest_matches_schema():
    schema = json.loads((CONTRACTS / "manifest.schema.json").read_text())
    obs = [
        Observation(2020, "USA", "CAN", "84-85_MachElec", Flow.EXPORT, 1.0),
        Observation(2020, "USA", "CAN", "84-85_MachElec", Flow.IMPORT, 2.0),
    ]
    manifest = build_manifest("2026-01", _staging(obs), normalize(obs))
    manifest["artifacts"]["matrix"]["sha256"] = "0" * 64  # populated at write time
    jsonschema.validate(manifest, schema)


def test_canonical_record_matches_schema():
    schema = json.loads((CONTRACTS / "records.schema.json").read_text())
    record = {
        "year": 2020,
        "reporter": "USA",
        "partner": "CAN",
        "product": "Total",
        "flow": "export",
        "value_usd": 1000,
    }
    jsonschema.validate(record, schema)


def test_negative_value_rejected_by_schema():
    schema = json.loads((CONTRACTS / "records.schema.json").read_text())
    bad = {
        "year": 2020,
        "reporter": "USA",
        "partner": "CAN",
        "product": "Total",
        "flow": "export",
        "value_usd": -5,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)
