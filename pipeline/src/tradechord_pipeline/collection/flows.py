"""Collect one reporter for a single flow across a whole year range.

Strategy (multi-year, fixed top-K):

  Phase 1  rank partners once, by total across the range (partner=ALL if supported,
           else fan out over the universe) and keep the top K
  Phase 2  WLD per product across the range -> per-year world totals, drop empty sectors
  Phase 3  bilateral history for each top-K partner (one year-range request per
           partner, or per partner*product when product=ALL is unsupported)
  ROW      per (product, year): world total minus the explicit top-K partners

Using year *ranges* (startPeriod..endPeriod) collapses the year dimension into a
single request, and a fixed top-K keeps the *same* partners tracked across all
years (better for trend/slope charts than a per-year coverage walk).
"""

from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from .. import config as _config
from ..clients.wits import SimpleCache, TokenBucketLimiter, WitsClient
from ..models import (
    Flow,
    Observation,
    RequestStatus,
    StatusRecorder,
    indicator_for,
)
from ..parsing.sdmx import SdmxParseError, parse_sdmx

_DATASET = "df_wits_tradestats_trade"
_DEFAULT_TOP_K = 15


@dataclass
class CollectionConfig:
    base_url: str
    timeout: int
    max_reqs_per_sec: float
    concurrency: int
    use_cache: bool
    cache_dir: str
    include_row_remainder: bool
    allow_partner_all: bool
    allow_product_all: bool
    top_k_partners: int | None
    sector_products: list[str]
    partners_export: list[str]
    partners_import: list[str]
    partner_code_fixes: dict[str, str]

    @classmethod
    def from_module(cls, cfg=_config) -> CollectionConfig:
        return cls(
            base_url=cfg.WITS_BASE_URL,
            timeout=cfg.REQUEST_TIMEOUT,
            max_reqs_per_sec=cfg.MAX_REQS_PER_SEC,
            concurrency=cfg.CONCURRENCY,
            use_cache=cfg.USE_CACHE,
            cache_dir=cfg.CACHE_DIR,
            include_row_remainder=getattr(cfg, "INCLUDE_ROW_REMAINDER", True),
            allow_partner_all=getattr(cfg, "ALLOW_PARTNER_ALL", True),
            allow_product_all=getattr(cfg, "ALLOW_PRODUCT_ALL", True),
            top_k_partners=getattr(cfg, "TOP_K_PARTNERS", None),
            sector_products=list(cfg.SECTOR_PRODUCTS),
            partners_export=list(cfg.TOP_50_EXPORTERS),
            partners_import=list(cfg.TOP_50_IMPORTERS),
            partner_code_fixes=dict(getattr(cfg, "WITS_PARTNER_CODE_FIXES", {})),
        )

    def partner_universe(self, flow: Flow, reporter: str) -> list[str]:
        base = self.partners_import if flow is Flow.IMPORT else self.partners_export
        valid = (p for p in base if isinstance(p, str) and len(p) == 3 and p.isalpha())
        fixed = {self.partner_code_fixes.get(p, p) for p in valid}
        fixed.discard(reporter)
        return sorted(fixed)


@dataclass
class CollectionResult:
    reporter: str
    years: list[int]
    flow: Flow
    observations: list[Observation]
    statuses: StatusRecorder
    manifest: dict = field(default_factory=dict)


def build_client(cc: CollectionConfig) -> WitsClient:
    """Build a client whose limiter/cache are shared for the whole run."""
    limiter = TokenBucketLimiter(cc.max_reqs_per_sec)
    cache = SimpleCache(cc.cache_dir) if cc.use_cache else None
    return WitsClient(cc.base_url, cc.timeout, limiter, cache)


def _endpoint(reporter, partner, product, indicator, start, end) -> str:
    return (
        f"SDMX/V21/rest/data/{_DATASET}/"
        f"A.{reporter}.{partner}.{product}.{indicator}?startPeriod={start}&endPeriod={end}"
    )


def _fetch(client, reporter, partner, product, indicator, start, end, flow, statuses) -> list[Observation]:
    res = client.get(_endpoint(reporter, partner, product, indicator, start, end))
    if res.status is not RequestStatus.SUCCESS:
        statuses.record(res.status)
        return []
    try:
        rows = parse_sdmx(res.content, flow)
    except SdmxParseError:
        statuses.record(RequestStatus.PARSE_ERROR)
        return []
    statuses.record(RequestStatus.SUCCESS if rows else RequestStatus.AUTHORITATIVE_EMPTY)
    return rows


def _probe(client, reporter, ref_year, indicator) -> tuple[bool, bool]:
    # Capability detection only; a throwaway recorder keeps it off the failure gate.
    probe = StatusRecorder()
    partner_all = bool(
        _fetch(client, reporter, "ALL", "Total", indicator, ref_year, ref_year, Flow.EXPORT, probe)
    )
    product_all = bool(
        _fetch(client, reporter, "WLD", "ALL", indicator, ref_year, ref_year, Flow.EXPORT, probe)
    )
    return partner_all, product_all


def collect_reporter_flow(
    reporter: str,
    years: list[int],
    flow: Flow,
    *,
    cc: CollectionConfig | None = None,
    client: WitsClient | None = None,
    top_k: int | None = None,
) -> CollectionResult:
    cc = cc or CollectionConfig.from_module()
    client = client or build_client(cc)
    if top_k is None:
        top_k = cc.top_k_partners or _DEFAULT_TOP_K

    indicator = indicator_for(flow)
    yset = set(years)
    y0, y1 = min(years), max(years)
    statuses = StatusRecorder()
    manifest: dict = {
        "reporter": reporter,
        "years": sorted(yset),
        "flow": flow.value,
        "indicator": indicator,
    }

    pa, pr = _probe(client, reporter, y1, indicator)
    partner_all_ok = cc.allow_partner_all and pa
    product_all_ok = cc.allow_product_all and pr
    manifest["probe"] = {"partner_all": pa, "product_all": pr}

    # ---- Phase 1: rank partners by total across the range ----
    partner_rows: list[Observation] = []
    if partner_all_ok:
        partner_rows = _fetch(client, reporter, "ALL", "Total", indicator, y0, y1, flow, statuses)
    else:
        universe = cc.partner_universe(flow, reporter)

        def totals(p: str) -> list[Observation]:
            return _fetch(client, reporter, p, "Total", indicator, y0, y1, flow, statuses)

        with ThreadPoolExecutor(max_workers=cc.concurrency) as ex:
            for fut in as_completed({ex.submit(totals, p): p for p in universe}):
                partner_rows.extend(fut.result() or [])

    by_partner: dict[str, float] = defaultdict(float)
    for r in partner_rows:
        if r.partner and r.partner not in ("WLD", "ROW") and r.year in yset:
            by_partner[r.partner] += r.value_thousands
    ranked = [p for p, _ in sorted(by_partner.items(), key=lambda kv: kv[1], reverse=True)][:top_k]
    manifest["ranked_partners"] = len(ranked)

    # ---- Phase 2: WLD per product across the range ----
    wld: dict[str, dict[int, float]] = {}

    def wld_fetch(prod: str) -> tuple[str, dict[int, float]]:
        rows = _fetch(client, reporter, "WLD", prod, indicator, y0, y1, flow, statuses)
        return prod, {r.year: r.value_thousands for r in rows if r.year in yset}

    with ThreadPoolExecutor(max_workers=min(cc.concurrency, 6)) as ex:
        for fut in as_completed({ex.submit(wld_fetch, p): p for p in cc.sector_products}):
            prod, year_values = fut.result()
            if any(v > 0 for v in year_values.values()):
                wld[prod] = year_values
    valid_products = sorted(wld)
    valid_set = set(valid_products)
    manifest["valid_products"] = len(valid_products)

    # ---- Phase 3: bilateral history for each top-K partner ----
    observations: list[Observation] = []
    if product_all_ok:
        def partner_all_products(partner: str) -> list[Observation]:
            rows = _fetch(client, reporter, partner, "ALL", indicator, y0, y1, flow, statuses)
            return [r for r in rows if r.product in valid_set and r.year in yset]

        with ThreadPoolExecutor(max_workers=cc.concurrency) as ex:
            for fut in as_completed({ex.submit(partner_all_products, p): p for p in ranked}):
                observations.extend(fut.result() or [])
    else:
        def partner_product(partner: str, prod: str) -> list[Observation]:
            rows = _fetch(client, reporter, partner, prod, indicator, y0, y1, flow, statuses)
            return [r for r in rows if r.year in yset]

        tasks = [(p, prod) for p in ranked for prod in valid_products]
        with ThreadPoolExecutor(max_workers=cc.concurrency) as ex:
            futs = {ex.submit(partner_product, p, prod): (p, prod) for p, prod in tasks}
            for fut in as_completed(futs):
                observations.extend(fut.result() or [])

    # ---- ROW remainder per (product, year) = WLD - explicit top-K ----
    sums: dict[tuple[str, int], float] = defaultdict(float)
    for o in observations:
        sums[(o.product, o.year)] += o.value_thousands
    if cc.include_row_remainder:
        for prod, year_values in wld.items():
            for year, total in year_values.items():
                remainder = total - sums.get((prod, year), 0.0)
                if remainder > 0:
                    observations.append(Observation(year, reporter, "ROW", prod, flow, remainder))

    # ---- coverage summary (min achieved fraction across years, per product) ----
    coverage: dict[str, dict] = {}
    for prod, year_values in wld.items():
        fractions = [
            min(1.0, sums.get((prod, year), 0.0) / total)
            for year, total in year_values.items()
            if total > 0
        ]
        coverage[prod] = {"min_achieved": min(fractions) if fractions else 1.0}

    manifest["coverage"] = coverage
    manifest["wld_totals"] = {
        prod: {str(y): v for y, v in year_values.items()} for prod, year_values in wld.items()
    }
    manifest["statuses"] = statuses.as_dict()
    manifest["observations"] = len(observations)
    return CollectionResult(reporter, sorted(yset), flow, observations, statuses, manifest)
