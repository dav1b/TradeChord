"""Unit conversion (thousands -> integer USD) and deterministic ordering."""

from tradechord_pipeline.models import Flow, Observation
from tradechord_pipeline.normalize import normalize, to_usd


def test_to_usd_multiplies_by_1000_and_rounds():
    assert to_usd(255021619.206) == 255021619206
    assert to_usd(3047853.409) == 3047853409
    assert to_usd(0.0) == 0


def test_to_usd_returns_int():
    assert isinstance(to_usd(1.2345), int)


def test_normalize_sorts_by_compound_key():
    obs = [
        Observation(2020, "USA", "JPN", "Total", Flow.EXPORT, 5.0),
        Observation(2020, "USA", "CAN", "Total", Flow.IMPORT, 5.0),
        Observation(2020, "USA", "CAN", "Total", Flow.EXPORT, 5.0),
    ]
    recs = normalize(obs)
    keys = [r.key for r in recs]
    assert keys == sorted(keys)
    # export sorts before import for the same partner
    assert (recs[0].partner, recs[0].flow) == ("CAN", Flow.EXPORT)
    assert recs[1].flow is Flow.IMPORT


def test_normalize_converts_values():
    obs = [Observation(2020, "USA", "CAN", "Total", Flow.EXPORT, 255021619.206)]
    assert normalize(obs)[0].value_usd == 255021619206
