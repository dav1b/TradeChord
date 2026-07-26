"""Core types shared across the pipeline.

Values here are in the WITS *source* unit (thousands of current USD). Conversion
to integer USD happens once, at release time — never during collection.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum


class Flow(str, Enum):
    """A directly reported trade flow."""

    EXPORT = "export"
    IMPORT = "import"


#: Authoritative flow -> WITS indicator mapping. Verified against the live API:
#: XPRT-TRD-VL and MPRT-TRD-VL return data; IMPT-TRD-VL does not. See
#: docs/data-methodology.md.
INDICATOR_BY_FLOW: dict[Flow, str] = {
    Flow.EXPORT: "XPRT-TRD-VL",
    Flow.IMPORT: "MPRT-TRD-VL",
}


def indicator_for(flow: Flow) -> str:
    return INDICATOR_BY_FLOW[flow]


class RequestStatus(str, Enum):
    """Outcome of a single WITS request+parse.

    Replaces the previous silent ``except: pass`` handling so that an incomplete
    collection is visible rather than indistinguishable from genuine "no trade".
    """

    SUCCESS = "success"                       # 200 with parsed observations
    AUTHORITATIVE_EMPTY = "authoritative_empty"  # 200, valid, no observations
    NOT_FOUND = "not_found"                    # 404: no series for this key (data absent)
    HTTP_ERROR = "http_error"                 # other non-retryable HTTP status
    RETRY_EXHAUSTED = "retry_exhausted"       # retryable errors/network gave up
    PARSE_ERROR = "parse_error"               # 200 but response did not parse


@dataclass
class FetchResult:
    """Result of an HTTP GET, before parsing."""

    status: RequestStatus
    content: bytes | None = None
    http_status: int | None = None


@dataclass(frozen=True)
class Observation:
    """One (reporter, partner, product, flow, year) trade value in thousands USD."""

    year: int
    reporter: str
    partner: str
    product: str
    flow: Flow
    value_thousands: float


@dataclass
class StatusRecorder:
    """Accumulates request outcomes for a collection run."""

    counts: Counter[RequestStatus] = field(default_factory=Counter)

    def record(self, status: RequestStatus) -> None:
        self.counts[status] += 1

    @property
    def had_unresolved_failures(self) -> bool:
        return bool(
            self.counts[RequestStatus.HTTP_ERROR]
            or self.counts[RequestStatus.RETRY_EXHAUSTED]
            or self.counts[RequestStatus.PARSE_ERROR]
        )

    def as_dict(self) -> dict[str, int]:
        return {status.value: count for status, count in sorted(self.counts.items())}
