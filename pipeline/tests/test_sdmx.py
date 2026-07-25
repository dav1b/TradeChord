"""SDMX parser: real fixture, empty vs malformed distinction, flow tagging."""

from pathlib import Path

import pytest

from tradechord_pipeline.models import Flow
from tradechord_pipeline.parsing.sdmx import SdmxParseError, parse_sdmx

FIXTURE = Path(__file__).parent / "fixtures" / "wits_usa_can_total_2020.xml"


def test_parses_real_fixture():
    rows = parse_sdmx(FIXTURE.read_bytes(), Flow.EXPORT)
    assert len(rows) == 1
    o = rows[0]
    assert (o.year, o.reporter, o.partner, o.product) == (2020, "USA", "CAN", "Total")
    assert o.flow is Flow.EXPORT
    assert o.value_thousands == pytest.approx(255021619.206)


def test_flow_is_applied_from_argument():
    rows = parse_sdmx(FIXTURE.read_bytes(), Flow.IMPORT)
    assert rows[0].flow is Flow.IMPORT


def test_empty_content_returns_empty():
    assert parse_sdmx(b"", Flow.EXPORT) == []
    assert parse_sdmx(None, Flow.EXPORT) == []


def test_valid_but_no_series_returns_empty():
    xml = (
        b'<?xml version="1.0"?>'
        b'<message:GenericData '
        b'xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">'
        b"</message:GenericData>"
    )
    assert parse_sdmx(xml, Flow.EXPORT) == []


def test_malformed_raises_parse_error():
    with pytest.raises(SdmxParseError):
        parse_sdmx(b"<not-xml <<<", Flow.EXPORT)
