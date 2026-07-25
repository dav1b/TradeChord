"""Normalize collected observations into the canonical release record.

The single place where the WITS source unit (thousands USD) becomes integer USD.
Downstream (the web app) never multiplies by 1000.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Flow, Observation

CANONICAL_FIELDS = ["year", "reporter", "partner", "product", "flow", "value_usd"]


@dataclass(frozen=True)
class CanonicalRecord:
    year: int
    reporter: str
    partner: str
    product: str
    flow: Flow
    value_usd: int

    @property
    def key(self) -> tuple[int, str, str, str, str]:
        return (self.year, self.reporter, self.partner, self.product, self.flow.value)


def to_usd(value_thousands: float) -> int:
    """WITS thousands-USD -> integer current USD."""
    return round(value_thousands * 1000)


def normalize(observations: list[Observation]) -> list[CanonicalRecord]:
    """Convert to integer USD and sort deterministically by compound key."""
    records = [
        CanonicalRecord(
            year=o.year,
            reporter=o.reporter,
            partner=o.partner,
            product=o.product,
            flow=o.flow,
            value_usd=to_usd(o.value_thousands),
        )
        for o in observations
    ]
    records.sort(key=lambda r: r.key)
    return records
