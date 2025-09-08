<script lang="ts">
  import ChordDiagram from '$components/ChordDiagram.svelte';
  import TradeBalanceChart from '$components/TradeBalanceChart.svelte';
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import { transformTradeData, buildCountryChord } from '$lib/utils/transform';
  import { buildTimeSeriesData } from '$lib/utils/timeSeries';
  import type { SimpleChordData, BowtieData, SankeyData } from '$lib/utils/transform';
  import type { TimeSeriesData } from '$lib/utils/timeSeries';

  let chordData: SimpleChordData | null = null;
  let timeSeriesData: TimeSeriesData[] = [];

  let rawData: any[] = [];
  let countries: string[] = [];
  let years: string[] = [];
  let selectedCountry = 'USA';
  let selectedYear = '2022';
  let topN = 10;
  let countryStats: { exports: number, imports: number, balance: number } | null = null;

  async function rebuildCharts() {
    if (!rawData.length) return;
    chordData = buildCountryChord(rawData as any, selectedCountry, topN, selectedYear);
    timeSeriesData = buildTimeSeriesData(rawData as any, selectedCountry);
    
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
    rawData = await d3.csv('/data/export-matrix.csv');
    if (rawData) {
      countries = Array.from(new Set((rawData as any[]).flatMap((r) => [r.reporter, r.partner]))).sort();
      years = Array.from(new Set((rawData as any[]).map((r) => r.year))).sort();
      await rebuildCharts();
    }
  });
</script>

<h1>TradeChord: Visualizing Global Trade</h1>

<label for="country">Select country:</label>
<select id="country" bind:value={selectedCountry} on:change={rebuildCharts}>
  {#each countries as c}
    <option value={c}>{c}</option>
  {/each}
</select>

<label for="year" style="margin-left:1rem;">Year:</label>
<select id="year" bind:value={selectedYear} on:change={rebuildCharts}>
  {#each years as y}
    <option value={y}>{y}</option>
  {/each}
</select>

<label for="topN" style="margin-left:1rem;">Top N partners:</label>
<input id="topN" type="number" min="1" max="50" bind:value={topN} on:change={rebuildCharts} style="width:4rem;" />

{#if chordData}
  <div class="chord-container">
    {#if countryStats}
      <div class="trade-equation">
        <div class="equation-part">
          <span class="equation-label">Exports</span>
          <span class="equation-value" style="color: #08605F;">${(countryStats.exports / 1e9).toFixed(1)}B</span>
        </div>
        <div class="equation-operator">-</div>
        <div class="equation-part">
          <span class="equation-label">Imports</span>
          <span class="equation-value" style="color: #931F1D;">${(countryStats.imports / 1e9).toFixed(1)}B</span>
        </div>
        <div class="equation-operator">=</div>
        <div class="equation-part">
          <span class="equation-label">Balance</span>
          <span class="equation-value" style="color: {countryStats.balance >= 0 ? '#08605F' : '#931F1D'};">${(countryStats.balance / 1e9).toFixed(1)}B</span>
        </div>
      </div>
    {/if}
    <ChordDiagram data={chordData} />
  </div>
{/if}

{#if timeSeriesData.length > 0}
  <TradeBalanceChart data={timeSeriesData} />
{/if}
