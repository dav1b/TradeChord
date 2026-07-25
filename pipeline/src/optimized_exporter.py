"""
Optimized exporter for one or more reporters/years with pruning, caching, and optional batching.

Features:
- Probe WITS endpoint for partner=ALL and product=ALL support.
- Phase 1: Fetch partner totals (product=Total) to rank partners.
- Phase 2: WLD prefilter per product to skip empty sectors.
- Phase 3: Fetch per-product bilateral data only for top-K partners.
- Token-bucket global rate limiting + retries with backoff.
- Simple on-disk cache for raw responses and zero-result markers.
- Checkpointing for resumable runs.
"""

import os
import time
import json
import math
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple, Iterable
from datetime import datetime

import requests
import sys
import os

# Ensure project root (containing config.py) is importable when running this file directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
import argparse


# ---------------------------- Utilities --------------------------------------

def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def stable_key(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class TokenBucketLimiter:
    def __init__(self, rate_per_sec: float, burst: Optional[int] = None):
        self.rate = max(rate_per_sec, 0.1)
        self.capacity = burst or max(1, int(math.ceil(self.rate)))
        self.tokens = self.capacity
        self.last = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                elapsed = now - self.last
                self.last = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
            time.sleep(0.01)


class SimpleCache:
    def __init__(self, root_dir: str):
        self.root = root_dir
        ensure_dir(self.root)

    def _path_for_key(self, key: str) -> str:
        return os.path.join(self.root, f"{key}.bin")

    def get(self, key: str) -> Optional[bytes]:
        p = self._path_for_key(key)
        if os.path.isfile(p):
            try:
                with open(p, "rb") as f:
                    return f.read()
            except Exception:
                return None
        return None

    def set(self, key: str, data: bytes) -> None:
        p = self._path_for_key(key)
        try:
            with open(p, "wb") as f:
                f.write(data)
        except Exception:
            pass


class Checkpoint:
    def __init__(self, path: str):
        self.path = path
        ensure_dir(os.path.dirname(path))
        self.lock = threading.Lock()

    def append(self, record: Dict) -> None:
        with self.lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")


# ---------------------------- HTTP Client ------------------------------------

class HTTPClient:
    def __init__(self, base_url: str, timeout: int, limiter: TokenBucketLimiter, cache: Optional[SimpleCache] = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.limiter = limiter
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/xml, text/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "User-Agent": "TradeChord-Optimizer/1.0"
        })
        self.cache = cache

    def get(self, endpoint: str) -> Optional[bytes]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        key = stable_key(url)
        if self.cache:
            cached = self.cache.get(key)
            if cached is not None:
                return cached

        retries = 3
        backoff = 0.5
        for attempt in range(retries):
            self.limiter.acquire()
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    content = resp.content
                    if self.cache:
                        self.cache.set(key, content)
                    return content
                elif resp.status_code in (429, 500, 502, 503, 504):
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    return None
            except requests.RequestException:
                time.sleep(backoff)
                backoff *= 2
        return None


# ---------------------------- Probes -----------------------------------------

def probe_all_support(client: HTTPClient, reporter: str, year: int, indicator: str) -> Tuple[bool, bool]:
    partner_all = False
    product_all = False

    # partner=ALL, product=Total
    ep_partner_all = (
        f"SDMX/V21/rest/data/df_wits_tradestats_trade/"
        f"A.{reporter}.ALL.Total.{indicator}?startPeriod={year}&endPeriod={year}"
    )
    if client.get(ep_partner_all):
        partner_all = True

    # product=ALL, partner=WLD
    ep_product_all = (
        f"SDMX/V21/rest/data/df_wits_tradestats_trade/"
        f"A.{reporter}.WLD.ALL.{indicator}?startPeriod={year}&endPeriod={year}"
    )
    if client.get(ep_product_all):
        product_all = True

    return partner_all, product_all


# ---------------------------- Parsing helpers --------------------------------

def parse_series_values(xml_bytes: Optional[bytes]) -> List[Dict]:
    if not xml_bytes:
        return []
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_bytes)
        ns = {"mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
              "gen": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"}
        rows: List[Dict] = []
        for series in root.findall(".//gen:Series", ns):
            dim = {}
            for elem in series.findall("gen:SeriesKey/gen:Value", ns):
                key = (elem.attrib.get("id") or "").lower()
                dim[key] = elem.attrib.get("value")
            # debug one sample of keys
            if not rows and dim:
                print(f"[debug] series keys: {list(dim.keys())[:6]}")
            for obs in series.findall("gen:Obs", ns):
                time_period = obs.find("gen:ObsDimension", ns)
                value = obs.find("gen:ObsValue", ns)
                if time_period is None or value is None:
                    continue
                rows.append({
                    "year": time_period.attrib.get("value"),
                    "reporter": dim.get("reporter") or dim.get("ref_area") or dim.get("reporter_code"),
                    "partner": dim.get("partner") or dim.get("counterpart_area") or dim.get("partner_code"),
                    "product": dim.get("product") or dim.get("product_code") or dim.get("productcode"),
                    "indicator": dim.get("indicator") or dim.get("measure"),
                    "value": value.attrib.get("value"),
                })
        return rows
    except Exception:
        return []


def sum_total_value(rows: List[Dict], year: int) -> float:
    total = 0.0
    for r in rows:
        if str(year) == str(r.get("year")):
            try:
                total += float(r.get("value") or 0)
            except Exception:
                pass
    return total


# ---------------------------- Core algorithm ---------------------------------

def build_reporter_one_year(reporter: str, year: int, indicator: str = None, products: Optional[List[str]] = None, top_k_partners: Optional[int] = None, manifest: Optional[Dict] = None, exhaustive: bool = False) -> List[Dict]:
    indicator = indicator or config.INDICATOR
    products = products or list(config.SECTOR_PRODUCTS)
    top_k_partners = top_k_partners if top_k_partners is not None else config.TOP_K_PARTNERS

    limiter = TokenBucketLimiter(rate_per_sec=config.MAX_REQS_PER_SEC)
    cache = SimpleCache(config.CACHE_DIR) if config.USE_CACHE else None
    client = HTTPClient(config.WITS_BASE_URL, config.REQUEST_TIMEOUT, limiter, cache)

    partner_all_ok = config.ALLOW_PARTNER_ALL
    product_all_ok = config.ALLOW_PRODUCT_ALL
    try:
        pa, pr = probe_all_support(client, reporter, year, indicator)
        print(f"[probe] partner=ALL supported: {pa}, product=ALL supported: {pr}")
        partner_all_ok = partner_all_ok and pa
        product_all_ok = product_all_ok and pr
    except Exception as e:
        print(f"[probe] probe failed: {e}")

    # Phase 1: partner totals to rank partners
    rows_partner_totals: List[Dict] = []
    if partner_all_ok:
        ep = f"SDMX/V21/rest/data/df_wits_tradestats_trade/A.{reporter}.ALL.Total.{indicator}?startPeriod={year}&endPeriod={year}"
        xml = client.get(ep)
        print(f"[phase1] partner=ALL fetch bytes: {len(xml) if xml else 0}")
        rows_partner_totals = parse_series_values(xml)
    else:
        # Build partner universe strictly from TOP_50_EXPORTERS (country ISO3s only)
        base = set(config.TOP_50_EXPORTERS)
        if reporter in base:
            base.remove(reporter)
        partners = sorted([p for p in base if isinstance(p, str) and len(p) == 3 and p.isalpha()])
        print(f"[phase1] fetching totals individually for {len(partners)} partners")
        def fetch_partner_total(p: str) -> List[Dict]:
            ep = f"SDMX/V21/rest/data/df_wits_tradestats_trade/A.{reporter}.{p}.Total.{indicator}?startPeriod={year}&endPeriod={year}"
            return parse_series_values(client.get(ep))

        with ThreadPoolExecutor(max_workers=config.CONCURRENCY) as ex:
            futures = {ex.submit(fetch_partner_total, p): p for p in partners}
            for f in as_completed(futures):
                rows_partner_totals.extend(f.result() or [])

    print(f"[phase1] rows_partner_totals: {len(rows_partner_totals)}")

    # Rank partners by total value
    by_partner: Dict[str, float] = {}
    for r in rows_partner_totals:
        partner_code = r.get("partner")
        if partner_code and partner_code not in ("WLD", "ROW"):
            by_partner[partner_code] = by_partner.get(partner_code, 0.0) + float(r.get("value") or 0)
    ranked_partners = [p for p, _ in sorted(by_partner.items(), key=lambda kv: kv[1], reverse=True)]
    if top_k_partners is not None and top_k_partners > 0:
        ranked_partners = ranked_partners[:top_k_partners]
    print(f"[phase1] ranked_partners: {len(ranked_partners)} (top_k={top_k_partners})")
    if manifest is not None:
        manifest.setdefault("phase1", {})["ranked_partners"] = len(ranked_partners)

    # Phase 2: WLD prefilter per product and coverage target planning
    def product_has_value(prod: str) -> bool:
        ep = f"SDMX/V21/rest/data/df_wits_tradestats_trade/A.{reporter}.WLD.{prod}.{indicator}?startPeriod={year}&endPeriod={year}"
        rows = parse_series_values(client.get(ep))
        val = sum_total_value(rows, year)
        wld_totals[prod] = val
        return val > 0

    valid_products: List[str] = []
    wld_totals: Dict[str, float] = {}
    with ThreadPoolExecutor(max_workers=min(config.CONCURRENCY, 6)) as ex:
        futures = {ex.submit(product_has_value, prod): prod for prod in products}
        for f in as_completed(futures):
            prod = futures[f]
            try:
                if f.result():
                    valid_products.append(prod)
            except Exception:
                pass
    print(f"[phase2] valid_products after WLD prefilter: {len(valid_products)} / {len(products)}")
    if manifest is not None:
        manifest.setdefault("phase2", {})["valid_products"] = len(valid_products)
        manifest["phase2"]["wld_totals"] = {p: wld_totals.get(p, 0.0) for p in valid_products}

    # Phase 3: bilateral per-product for ranked partners
    results: List[Dict] = []

    if product_all_ok:
        # Batch per partner (all products)
        print(f"[phase3] product=ALL batching enabled for {len(ranked_partners)} partners")
        def fetch_partner_all_products(partner: str) -> List[Dict]:
            ep = f"SDMX/V21/rest/data/df_wits_tradestats_trade/A.{reporter}.{partner}.ALL.{indicator}?startPeriod={year}&endPeriod={year}"
            rows = parse_series_values(client.get(ep))
            return [r for r in rows if r.get("product") in valid_products]

        with ThreadPoolExecutor(max_workers=config.CONCURRENCY) as ex:
            futures = {ex.submit(fetch_partner_all_products, p): p for p in ranked_partners}
            for f in as_completed(futures):
                try:
                    results.extend(f.result() or [])
                except Exception:
                    pass
    else:
        # No product batching; fetch each product for each partner
        mode = "exhaustive" if exhaustive else "coverage"
        print(f"[phase3] {mode}-based fetch for {len(ranked_partners)} partners x {len(valid_products)} products")

        # Sort partners by total (from phase1); already ranked. For each product, walk partners until coverage target met
        def fetch_product_partner(prod: str, partner: str) -> List[Dict]:
            ep = f"SDMX/V21/rest/data/df_wits_tradestats_trade/A.{reporter}.{partner}.{prod}.{indicator}?startPeriod={year}&endPeriod={year}"
            return parse_series_values(client.get(ep))

        for prod in valid_products:
            wld_total = wld_totals.get(prod, 0.0)
            target = wld_total * float(getattr(config, "COVERAGE_TARGET", 0.9))
            accumulated = 0.0
            covered_partners: List[str] = []
            # Fetch partners sequentially in ranked order but in small concurrent batches for throughput
            batch_size = min(8, config.CONCURRENCY)
            idx = 0
            while idx < len(ranked_partners):
                if not exhaustive and accumulated >= target:
                    break
                batch = ranked_partners[idx: idx + batch_size]
                idx += batch_size
                with ThreadPoolExecutor(max_workers=batch_size) as ex:
                    futures = {ex.submit(fetch_product_partner, prod, p): p for p in batch}
                    for f in as_completed(futures):
                        try:
                            rows = f.result() or []
                            results.extend(rows)
                            val = sum_total_value(rows, year)
                            accumulated += val
                            covered_partners.append(futures[f])
                        except Exception:
                            pass
            # Coverage check and remainder
            achieved = accumulated / wld_total if wld_total > 0 else 1.0
            if manifest is not None:
                manifest.setdefault("coverage", {})[prod] = {
                    "wld_total": wld_total,
                    "accumulated": accumulated,
                    "achieved": achieved,
                    "num_partners": len(covered_partners)
                }
            if not exhaustive and achieved + 1e-9 < float(getattr(config, "COVERAGE_TARGET", 0.9)):
                print(f"[warn] coverage for {prod} below target: {achieved:.3f}")
            if getattr(config, "INCLUDE_ROW_REMAINDER", True):
                remainder = max(0.0, wld_total - accumulated)
                if remainder > 0:
                    results.append({
                        "year": str(year),
                        "reporter": reporter,
                        "partner": "ROW",
                        "product": prod,
                        "indicator": indicator,
                        "value": str(remainder)
                    })

    print(f"[done] total rows collected: {len(results)}")

    return results


def save_results(rows: List[Dict], reporter: str, year: int, indicator: str) -> str:
    import csv
    ensure_dir(config.OUTPUT_DIR)
    out_path = os.path.join(config.OUTPUT_DIR, f"optimized_exports_{reporter}_{indicator}_{year}.csv")
    fieldnames = ["year", "reporter", "partner", "product", "indicator", "value"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    return out_path


def parse_years(expr: str) -> List[int]:
    expr = expr.strip()
    parts: List[int] = []
    for token in expr.split(","):
        token = token.strip()
        if "-" in token:
            a, b = token.split("-", 1)
            parts.extend(list(range(int(a), int(b) + 1)))
        else:
            parts.append(int(token))
    return sorted(set(parts))


def main():
    parser = argparse.ArgumentParser(description="Optimized WITS export collector")
    parser.add_argument("--reporters", type=str, default="ONE", help="ONE|TOP50|ISO3,ISO3,...")
    parser.add_argument("--years", type=str, default=str(config.SINGLE_YEAR or config.END_YEAR), help="Year list or ranges, e.g. 2002-2005,2010")
    parser.add_argument("--indicator", type=str, default=config.INDICATOR)
    parser.add_argument("--coverage-target", type=float, default=getattr(config, "COVERAGE_TARGET", 0.9))
    parser.add_argument("--exhaustive", action="store_true", help="Fetch all partners (ignore coverage short-circuit)")
    parser.add_argument("--concurrency", type=int, default=config.CONCURRENCY)
    parser.add_argument("--max-rps", type=float, default=config.MAX_REQS_PER_SEC)
    args = parser.parse_args()

    # Apply overrides
    config.CONCURRENCY = args.concurrency
    config.MAX_REQS_PER_SEC = args.max_rps
    if hasattr(config, "COVERAGE_TARGET"):
        config.COVERAGE_TARGET = args.coverage_target

    # Determine reporters
    if args.reporters.upper() == "ONE":
        reporters: List[str] = [config.REPORTER]
    elif args.reporters.upper() == "TOP50":
        reporters = list(config.TOP_50_EXPORTERS)
    else:
        reporters = [r.strip().upper() for r in args.reporters.split(",") if r.strip()]

    years = parse_years(args.years)

    # Start timing
    start_time = time.time()
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[start] {start_datetime} - reporters={len(reporters)}, years={years}, indicator={args.indicator}")
    print(f"[config] MAX_REQS_PER_SEC={config.MAX_REQS_PER_SEC}, CONCURRENCY={config.CONCURRENCY}, COVERAGE_TARGET={getattr(config,'COVERAGE_TARGET',None)}")

    total_rows = 0
    total_files = 0
    reporter_times = {}
    
    # Validate partner whitelist logic: partners will be drawn from TOP_50_EXPORTERS inside builder when not using ALL
    for reporter in reporters:
        reporter_start = time.time()
        reporter_rows = 0
        
        for year in years:
            year_start = time.time()
            manifest: Dict = {"reporter": reporter, "year": year, "indicator": args.indicator}
            rows = build_reporter_one_year(reporter, year, args.indicator, manifest=manifest, exhaustive=args.exhaustive)
            out = save_results(rows, reporter, year, args.indicator)
            
            # Write manifest alongside
            mpath = out.replace(".csv", ".manifest.json")
            try:
                with open(mpath, "w", encoding="utf-8") as mf:
                    json.dump(manifest, mf, indent=2)
            except Exception:
                pass
            
            year_time = time.time() - year_start
            reporter_rows += len(rows)
            total_rows += len(rows)
            total_files += 1
            
            print(f"[{reporter}-{year}] {len(rows)} rows in {year_time:.1f}s -> {out}")
        
        reporter_time = time.time() - reporter_start
        reporter_times[reporter] = reporter_time
        print(f"[{reporter}] completed {reporter_rows} rows in {reporter_time:.1f}s")
    
    # Final timing summary
    total_time = time.time() - start_time
    end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n[SUMMARY] {end_datetime}")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"Total rows: {total_rows:,}")
    print(f"Total files: {total_files}")
    print(f"Average time per reporter: {total_time/len(reporters):.1f}s")
    print(f"Average time per year: {total_time/len(years):.1f}s")
    print(f"Rows per second: {total_rows/total_time:.1f}")
    
    for reporter, reporter_time in reporter_times.items():
        print(f"  {reporter}: {reporter_time:.1f}s")


if __name__ == "__main__":
    main()


