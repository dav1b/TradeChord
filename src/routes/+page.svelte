<script lang="ts">
  import ChordDiagram from '$components/ChordDiagram.svelte';
  import DivergingBarChart from '$components/DivergingBarChart.svelte';
  import TradeBalanceChart from '$components/TradeBalanceChart.svelte';
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import { transformTradeData, buildCountryChord } from '$lib/utils/transform';
  import { buildTimeSeriesData } from '$lib/utils/timeSeries';
  import type { SimpleChordData, BowtieData, SankeyData } from '$lib/utils/transform';
  import type { TimeSeriesData } from '$lib/utils/timeSeries';

  let barChartData: { country: string, exports: number, imports: number }[] = [];
  let chordData: SimpleChordData | null = null;
  let timeSeriesData: TimeSeriesData[] = [];

  let rawData: any[] = [];
  let countries: string[] = [];
  let selectedCountry = 'USA';
  let topN = 10;

  async function rebuildCharts() {
    if (!rawData.length) return;
    chordData = buildCountryChord(rawData as any, selectedCountry, topN);
    timeSeriesData = buildTimeSeriesData(rawData as any, selectedCountry);
  }

  onMount(async () => {
    rawData = await d3.csv('/data/export-matrix.csv');
    if (rawData) {
      const transformed = transformTradeData(rawData as any);
      barChartData = transformed.barChartData;
      countries = Array.from(new Set((rawData as any[]).flatMap((r) => [r.reporter, r.partner]))).sort();
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

<label for="topN" style="margin-left:1rem;">Top N partners:</label>
<input id="topN" type="number" min="1" max="50" bind:value={topN} on:change={rebuildCharts} style="width:4rem;" />

{#if chordData}
  <ChordDiagram data={chordData} />
{/if}
{#if barChartData.length > 0}
  <DivergingBarChart data={barChartData} />
{/if}
{#if timeSeriesData.length > 0}
  <TradeBalanceChart data={timeSeriesData} />
{/if}
