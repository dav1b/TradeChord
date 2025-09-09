<script lang="ts">
  import ChordDiagram from '$components/ChordDiagram.svelte';
  import TradeBalanceChart from '$components/TradeBalanceChart.svelte';
  import BumpChart from '$components/BumpChart.svelte';
  import SlopeChart from '$components/SlopeChart.svelte';
  import ProductTreemap from '$components/ProductTreemap.svelte';
  import ProductTrendChart from '$components/ProductTrendChart.svelte';
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import { transformTradeData, buildCountryChord } from '$lib/utils/transform';
  import { buildTimeSeriesData, buildExportRankSeries, buildSlopeData, buildSlopeShareData } from '$lib/utils/timeSeries';
  import { DASHBOARD, formatWithSuffix } from '$lib/utils/config';
  import { getProductTreemapData, getProductTrendData, getAvailableCountries, getAvailableYears } from '$lib/utils/productAnalysis';
  import type { SimpleChordData, BowtieData, SankeyData } from '$lib/utils/transform';
  import type { TimeSeriesData } from '$lib/utils/timeSeries';
  import type { ProductTreemapData, ProductTrendData } from '$lib/utils/productAnalysis';

  let chordData: SimpleChordData | null = null;
  let timeSeriesData: TimeSeriesData[] = [];

  let rawData: any[] = [];
  let productData: any[] = [];
  let countries: string[] = [];
  let years: string[] = [];
  let selectedCountry = 'USA';
  let selectedYear = String(DASHBOARD.END_YEAR);
  let topN = DASHBOARD.TOP_N_PARTNERS;
  let countryStats: { exports: number, imports: number, balance: number } | null = null;
  let bumpData: any[] = [];
  let slopeData: any[] = [];
  let importSlopeData: any[] = [];
  let compareYear = String(DASHBOARD.START_YEAR);
  
  // Product analysis data
  let productTreemapData: ProductTreemapData[] = [];
  let productTrendData: ProductTrendData[] = [];

  async function rebuildCharts() {
    if (!rawData.length) return;
    chordData = buildCountryChord(rawData as any, selectedCountry, topN, selectedYear);
    timeSeriesData = buildTimeSeriesData(rawData as any, selectedCountry);
    bumpData = buildExportRankSeries(rawData as any, selectedCountry, 10, 2002, 2022);
    slopeData = buildSlopeShareData(
      rawData as any,
      selectedCountry,
      parseInt(compareYear),
      parseInt(selectedYear),
      topN,
      'exports'
    );
    importSlopeData = buildSlopeShareData(
      rawData as any,
      selectedCountry,
      parseInt(compareYear),
      parseInt(selectedYear),
      topN,
      'imports'
    );
    
    // Build product charts data (always on for dashboard)
    if (productData.length > 0) {
      productTreemapData = getProductTreemapData(productData as any, selectedCountry, selectedYear);
      productTrendData = getProductTrendData(productData as any, selectedCountry);
    }
    
    // Calculate country stats for selected year
    const yearData = rawData.filter((r: any) => r.year === selectedYear && r.indicator === 'XPRT-TRD-VL');
    const countryData = yearData.filter((r: any) => r.reporter === selectedCountry || r.partner === selectedCountry);
    
    let exports = 0;
    let imports = 0;
    
    countryData.forEach((r: any) => {
      const value = (parseFloat(r.value) || 0) * 1000;
      if (r.reporter === selectedCountry) {
        exports += value;
      }
      if (r.partner === selectedCountry) {
        imports += value;
      }
    });
    
    countryStats = {
      exports,
      imports,
      balance: exports - imports
    };
  }

  onMount(async () => {
    // Load both datasets
    rawData = await d3.csv('/data/export-matrix.csv');
    productData = await d3.csv('/data/complete_export_matrix.csv');
    
    if (rawData) {
      countries = Array.from(new Set((rawData as any[]).flatMap((r) => [r.reporter, r.partner]))).sort();
      years = Array.from(new Set((rawData as any[]).map((r) => r.year))).sort();
      await rebuildCharts();
    }
  });
</script>

<div class="page-header">
  <h1>TradeChord: Visualizing Global Trade</h1>
  <a href="/all" class="icon-link" title="View all countries" aria-label="View all countries">
    <!-- simple grid icon -->
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="8" height="8" rx="2" fill="#374151"/>
      <rect x="13" y="3" width="8" height="8" rx="2" fill="#374151"/>
      <rect x="3" y="13" width="8" height="8" rx="2" fill="#374151"/>
      <rect x="13" y="13" width="8" height="8" rx="2" fill="#374151"/>
    </svg>
  </a>
  
</div>

<label for="country">Select country:</label>
<select id="country" bind:value={selectedCountry} on:change={rebuildCharts}>
  {#each countries as c}
    <option value={c}>{c}</option>
  {/each}
</select>

<!-- Year and TopN controls removed per dashboard config. Using DASHBOARD constants. -->

<div class="dashboard">
  <div class="left-pane">
    <div class="left-header">
      {#if countryStats}
        <div class="big-equation">
          <div class="big-stat" style="--c:#08605F;">
            <div class="big-value">{formatWithSuffix(countryStats.exports)}</div>
            <div class="big-label">Exports</div>
          </div>
          <div class="big-op">-</div>
          <div class="big-stat" style="--c:#931F1D;">
            <div class="big-value">{formatWithSuffix(countryStats.imports)}</div>
            <div class="big-label">Imports</div>
          </div>
          <div class="big-op">=</div>
          <div class="big-stat" style="--c:{countryStats.balance >= 0 ? '#08605F' : '#931F1D'};">
            <div class="big-value">{countryStats.balance >= 0 ? '+' : '-'}{formatWithSuffix(Math.abs(countryStats.balance))}</div>
            <div class="big-label">Balance</div>
          </div>
        </div>
      {/if}
    </div>
    {#if chordData}
      <div class="chord-card">
        <ChordDiagram data={chordData} />
      </div>
    {/if}
  </div>
  <div class="right-pane">
    {#if productTreemapData.length > 0}
      <div class="treemap-card">
        <h2>Product Export Breakdown — {selectedCountry} ({selectedYear})</h2>
        <ProductTreemap data={productTreemapData} width={680} height={520} />
      </div>
    {/if}
    <div class="slopes">
      {#if slopeData.length > 0}
        <div class="slope-card">
          <h3>Top {topN} Partners — Exports {compareYear} → {selectedYear}</h3>
          <SlopeChart data={slopeData} year1={parseInt(compareYear)} year2={parseInt(selectedYear)} reporter={selectedCountry} mode="exports" width={680} height={260} />
        </div>
      {/if}
      {#if importSlopeData.length > 0}
        <div class="slope-card">
          <h3>Top {topN} Partners — Imports {compareYear} → {selectedYear}</h3>
          <SlopeChart data={importSlopeData} year1={parseInt(compareYear)} year2={parseInt(selectedYear)} reporter={selectedCountry} mode="imports" width={680} height={260} />
        </div>
      {/if}
    </div>
  </div>
</div>

<div class="footer">
  <div>Source: Local CSV derived from WITS/UN Comtrade. Year range {DASHBOARD.START_YEAR}–{DASHBOARD.END_YEAR}.</div>
  <div>Designed by DoC</div>
  
</div>

<style>
  .dashboard {
    display: grid;
    grid-template-columns: 820px 1fr;
    gap: 20px;
    align-items: start;
    margin-top: 16px;
    max-width: 1500px;
    min-height: 844px;
  }

  .left-pane {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .right-pane {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .chord-card, .treemap-card, .slope-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    padding: 12px;
  }

  .treemap-card > h2, .slope-card > h3 {
    margin: 8px 8px 12px 8px;
    color: #374151;
    font-weight: 600;
    font-size: 14px;
  }

  .big-equation {
    display: flex;
    align-items: baseline;
    gap: 12px;
    flex-wrap: wrap;
  }
  .big-op { font-size: 28px; font-weight: 700; color: #374151; }
  .big-stat { display: flex; align-items: baseline; gap: 8px; }
  .big-value { font-size: 36px; font-weight: 800; color: var(--c); }
  .big-label { font-size: 12px; color: #6B7280; font-weight: 600; }

  .slopes { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

  .footer {
    margin-top: 16px;
    padding: 12px 8px;
    color: #6B7280;
    font-size: 12px;
    display: flex;
    justify-content: space-between;
  }

  @media (max-width: 900px) {
    .dashboard { grid-template-columns: 1fr; max-width: 100%; min-height: auto; }
    .slopes { grid-template-columns: 1fr; }
  }

</style>
