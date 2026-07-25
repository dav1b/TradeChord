"""Parse WITS SDMX 2.1 generic-data XML into :class:`Observation` rows."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ..models import Flow, Observation

_NS = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "gen": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic",
}


class SdmxParseError(Exception):
    """Raised when a 200 response is not parseable SDMX (distinct from empty)."""


def parse_sdmx(content: bytes | None, flow: Flow) -> list[Observation]:
    """Parse SDMX XML into observations for ``flow``.

    Returns ``[]`` for a valid response with no series (authoritative empty).
    Raises :class:`SdmxParseError` if the payload is not parseable XML.
    """
    if not content:
        return []
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise SdmxParseError(str(exc)) from exc

    rows: list[Observation] = []
    for series in root.findall(".//gen:Series", _NS):
        dim: dict[str, str | None] = {}
        for elem in series.findall("gen:SeriesKey/gen:Value", _NS):
            key = (elem.attrib.get("id") or "").lower()
            dim[key] = elem.attrib.get("value")

        reporter = dim.get("reporter") or dim.get("ref_area") or dim.get("reporter_code")
        partner = dim.get("partner") or dim.get("counterpart_area") or dim.get("partner_code")
        product = dim.get("product") or dim.get("product_code") or dim.get("productcode")

        for obs in series.findall("gen:Obs", _NS):
            period = obs.find("gen:ObsDimension", _NS)
            value = obs.find("gen:ObsValue", _NS)
            if period is None or value is None:
                continue
            raw_year = period.attrib.get("value")
            raw_value = value.attrib.get("value")
            if raw_year is None or raw_value is None:
                continue
            try:
                year = int(raw_year)
                value_thousands = float(raw_value)
            except ValueError:
                continue
            rows.append(
                Observation(
                    year=year,
                    reporter=reporter or "",
                    partner=partner or "",
                    product=product or "",
                    flow=flow,
                    value_thousands=value_thousands,
                )
            )
    return rows
