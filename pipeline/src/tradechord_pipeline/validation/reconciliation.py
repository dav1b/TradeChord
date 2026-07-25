"""Flow-specific WLD/ROW reconciliation.

For each (reporter, year, flow, product):

    sum(explicit partners) + ROW  ≈  WLD total       (within tolerance)

Reconciliation is per flow — import ROW is never inferred from exports. Compared
in the source unit (thousands USD), before normalization.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ..models import Observation

#: Reporter/year/flow/product key.
ReconKey = tuple[str, int, str, str]


@dataclass
class ReconItem:
    reporter: str
    year: int
    flow: str
    product: str
    wld_total: float
    accumulated: float

    @property
    def rel_diff(self) -> float:
        if self.wld_total == 0:
            return 0.0
        return abs(self.accumulated - self.wld_total) / self.wld_total


def reconcile(
    observations: list[Observation],
    wld_totals: dict[ReconKey, float],
    tolerance: float = 0.02,
) -> tuple[list[ReconItem], list[ReconItem]]:
    """Return (all items, failing items) for the given WLD totals.

    ``observations`` should include the synthetic ROW rows so explicit + ROW is
    the accumulated sum. ``tolerance`` is a relative fraction (0.02 = 2%).
    """
    sums: dict[ReconKey, float] = defaultdict(float)
    for o in observations:
        sums[(o.reporter, o.year, o.flow.value, o.product)] += o.value_thousands

    items: list[ReconItem] = []
    failures: list[ReconItem] = []
    for (reporter, year, flow, product), total in wld_totals.items():
        item = ReconItem(
            reporter=reporter,
            year=year,
            flow=flow,
            product=product,
            wld_total=total,
            accumulated=sums.get((reporter, year, flow, product), 0.0),
        )
        items.append(item)
        if total > 0 and item.rel_diff > tolerance:
            failures.append(item)
    return items, failures
