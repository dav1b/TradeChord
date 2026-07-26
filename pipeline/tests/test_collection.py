"""Collection config: partner universe and WITS code corrections."""

from tradechord_pipeline.collection.flows import CollectionConfig
from tradechord_pipeline.models import Flow


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
