"""Collect one reporter-year for a single flow (export or import).

Behavior-preserving port of the legacy ``build_reporter_one_year`` collector,
generalized over :class:`Flow` and instrumented with explicit request statuses:

  Phase 1  rank partners            (partner=ALL if supported, else fan out)
  Phase 2  WLD prefilter per product to skip empty sectors
  Phase 3  bilateral per-product for ranked partners, to a coverage target,
           with a synthetic flow-specific ROW remainder

The indicator is derived from the flow, so exports and imports share one code
path (see docs/data-methodology.md).
"""

from __future__ import annotations

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


@dataclass
class CollectionConfig:
    base_url: str
    timeout: int
    max_reqs_per_sec: float
    concurrency: int
    use_cache: bool
    cache_dir: str
    coverage_target: float
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
            coverage_target=getattr(cfg, "COVERAGE_TARGET", 0.9),
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
    year: int
    flow: Flow
    observations: list[Observation]
    statuses: StatusRecorder
    manifest: dict = field(default_factory=dict)


def build_client(cc: CollectionConfig) -> WitsClient:
    """Build a client whose limiter/cache are shared for the whole run."""
    limiter = TokenBucketLimiter(cc.max_reqs_per_sec)
    cache = SimpleCache(cc.cache_dir) if cc.use_cache else None
    return WitsClient(cc.base_url, cc.timeout, limiter, cache)


def _endpoint(reporter: str, partner: str, product: str, indicator: str, year: int) -> str:
    return (
        f"SDMX/V21/rest/data/{_DATASET}/"
        f"A.{reporter}.{partner}.{product}.{indicator}?startPeriod={year}&endPeriod={year}"
    )


def _fetch(client: WitsClient, endpoint: str, flow: Flow, statuses: StatusRecorder) -> list[Observation]:
    res = client.get(endpoint)
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


def _sum(rows: list[Observation], year: int) -> float:
    return sum(r.value_thousands for r in rows if r.year == year)


def _probe(client, reporter, year, indicator) -> tuple[bool, bool]:
    # Probe outcomes are capability detection, not data completeness: an expected
    # 4xx for an unsupported ALL query must not count toward run failures. Use a
    # throwaway recorder so it never poisons the release gate.
    probe = StatusRecorder()
    partner_all = bool(
        _fetch(client, _endpoint(reporter, "ALL", "Total", indicator, year), Flow.EXPORT, probe)
    )
    product_all = bool(
        _fetch(client, _endpoint(reporter, "WLD", "ALL", indicator, year), Flow.EXPORT, probe)
    )
    return partner_all, product_all


def collect_reporter_flow(
    reporter: str,
    year: int,
    flow: Flow,
    *,
    cc: CollectionConfig | None = None,
    client: WitsClient | None = None,
    exhaustive: bool = False,
) -> CollectionResult:
    cc = cc or CollectionConfig.from_module()
    client = client or build_client(cc)
    indicator = indicator_for(flow)
    statuses = StatusRecorder()
    manifest: dict = {
        "reporter": reporter,
        "year": year,
        "flow": flow.value,
        "indicator": indicator,
    }

    partner_all_ok = cc.allow_partner_all
    product_all_ok = cc.allow_product_all
    pa, pr = _probe(client, reporter, year, indicator)
    partner_all_ok = partner_all_ok and pa
    product_all_ok = product_all_ok and pr
    manifest["probe"] = {"partner_all": pa, "product_all": pr}

    # ---- Phase 1: rank partners ----
    partner_rows: list[Observation] = []
    if partner_all_ok:
        partner_rows = _fetch(
            client, _endpoint(reporter, "ALL", "Total", indicator, year), flow, statuses
        )
    else:
        universe = cc.partner_universe(flow, reporter)

        def totals(p: str) -> list[Observation]:
            return _fetch(client, _endpoint(reporter, p, "Total", indicator, year), flow, statuses)

        with ThreadPoolExecutor(max_workers=cc.concurrency) as ex:
            for fut in as_completed({ex.submit(totals, p): p for p in universe}):
                partner_rows.extend(fut.result() or [])

    by_partner: dict[str, float] = {}
    for r in partner_rows:
        if r.partner and r.partner not in ("WLD", "ROW"):
            by_partner[r.partner] = by_partner.get(r.partner, 0.0) + r.value_thousands
    ranked = [p for p, _ in sorted(by_partner.items(), key=lambda kv: kv[1], reverse=True)]
    if cc.top_k_partners:
        ranked = ranked[: cc.top_k_partners]
    manifest["phase1_ranked_partners"] = len(ranked)

    # ---- Phase 2: WLD prefilter per product ----
    wld_totals: dict[str, float] = {}

    def product_total(prod: str) -> float:
        rows = _fetch(client, _endpoint(reporter, "WLD", prod, indicator, year), flow, statuses)
        return _sum(rows, year)

    valid_products: list[str] = []
    with ThreadPoolExecutor(max_workers=min(cc.concurrency, 6)) as ex:
        futs = {ex.submit(product_total, prod): prod for prod in cc.sector_products}
        for fut in as_completed(futs):
            prod = futs[fut]
            val = fut.result()
            wld_totals[prod] = val
            if val > 0:
                valid_products.append(prod)
    manifest["phase2_valid_products"] = len(valid_products)
    manifest["wld_totals"] = {p: wld_totals[p] for p in valid_products}

    # ---- Phase 3: bilateral per product for ranked partners ----
    observations: list[Observation] = []

    if product_all_ok:
        def partner_all_products(partner: str) -> list[Observation]:
            rows = _fetch(client, _endpoint(reporter, partner, "ALL", indicator, year), flow, statuses)
            return [r for r in rows if r.product in valid_products]

        with ThreadPoolExecutor(max_workers=cc.concurrency) as ex:
            for fut in as_completed({ex.submit(partner_all_products, p): p for p in ranked}):
                observations.extend(fut.result() or [])
    else:
        coverage: dict[str, dict] = {}
        batch_size = min(8, cc.concurrency)

        def product_partner(prod: str, partner: str) -> list[Observation]:
            return _fetch(client, _endpoint(reporter, partner, prod, indicator, year), flow, statuses)

        for prod in valid_products:
            wld_total = wld_totals.get(prod, 0.0)
            target = wld_total * cc.coverage_target
            accumulated = 0.0
            covered = 0
            idx = 0
            while idx < len(ranked):
                if not exhaustive and accumulated >= target:
                    break
                batch = ranked[idx : idx + batch_size]
                idx += batch_size
                with ThreadPoolExecutor(max_workers=batch_size) as ex:
                    for fut in as_completed({ex.submit(product_partner, prod, p): p for p in batch}):
                        rows = fut.result() or []
                        observations.extend(rows)
                        accumulated += _sum(rows, year)
                        covered += 1
            achieved = accumulated / wld_total if wld_total > 0 else 1.0
            coverage[prod] = {
                "wld_total": wld_total,
                "accumulated": accumulated,
                "achieved": achieved,
                "num_partners": covered,
            }
            if cc.include_row_remainder:
                remainder = max(0.0, wld_total - accumulated)
                if remainder > 0:
                    observations.append(
                        Observation(year, reporter, "ROW", prod, flow, remainder)
                    )
        manifest["coverage"] = coverage

    manifest["statuses"] = statuses.as_dict()
    manifest["observations"] = len(observations)
    return CollectionResult(reporter, year, flow, observations, statuses, manifest)
