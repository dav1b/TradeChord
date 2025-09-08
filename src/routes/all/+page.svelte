<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import BumpChart from '$components/BumpChart.svelte';
  import ChordDiagram from '$components/ChordDiagram.svelte';
  import TradeBalanceChart from '$components/TradeBalanceChart.svelte';
  import TrendingTradeBalance from '$components/TrendingTradeBalance.svelte';
  import { buildExportRankSeries } from '$lib/utils/timeSeries';

  let rawData: any[] = [];
  let reporterTotals: Array<{ reporter: string; total: number }> = [];
  let topReporters: string[] = [];
  let grids: Array<{ reporter: string; data: any }> = [];
  let chartType: 'bump' | 'trend' | 'trending' | 'chord' = 'bump';

  onMount(async () => {
    rawData = await d3.csv('/data/export-matrix.csv');
    if (!rawData) return;

    // Compute total exports per reporter across all years
    const totals = new Map<string, number>();
    (rawData as any[]).forEach((r: any) => {
      if (r.indicator !== 'XPRT-TRD-VL') return;
      const v = (parseFloat(r.value) || 0) * 1000;
      totals.set(r.reporter, (totals.get(r.reporter) || 0) + v);
    });

    reporterTotals = Array.from(totals.entries())
      .map(([reporter, total]) => ({ reporter, total }))
      .sort((a, b) => b.total - a.total);

    topReporters = reporterTotals.slice(0, 25).map((d) => d.reporter);

    rebuildGrids();
  });

  function rebuildGrids() {
    if (chartType === 'bump') {
      grids = topReporters.map((rep) => ({
        reporter: rep,
        data: buildExportRankSeries(rawData as any, rep, 10, 2002, 2022)
      }));
    } else if (chartType === 'trend') {
      // Build time series per reporter for TradeBalanceChart
      const buildSeries = (rep: string) => {
        const yearMap = new Map<number, { exports: number; imports: number }>();
        for (let y = 2002; y <= 2022; y++) yearMap.set(y, { exports: 0, imports: 0 });
        (rawData as any[]).forEach((r: any) => {
          if (r.indicator !== 'XPRT-TRD-VL') return;
          const y = parseInt(r.year);
          const v = (parseFloat(r.value) || 0) * 1000;
          if (r.reporter === rep) {
            const cur = yearMap.get(y)!; yearMap.set(y, { exports: cur.exports + v, imports: cur.imports });
          }
          if (r.partner === rep) {
            const cur = yearMap.get(y)!; yearMap.set(y, { exports: cur.exports, imports: cur.imports + v });
          }
        });
        return Array.from(yearMap.entries()).map(([year, d]) => ({ year, exports: d.exports, imports: d.imports, balance: d.exports - d.imports }));
      };
      grids = topReporters.map((rep) => ({ reporter: rep, data: buildSeries(rep) }));
    } else if (chartType === 'trending') {
      // Build time series per reporter for TrendingTradeBalance (same data as trend)
      const buildSeries = (rep: string) => {
        const yearMap = new Map<number, { exports: number; imports: number }>();
        for (let y = 2002; y <= 2022; y++) yearMap.set(y, { exports: 0, imports: 0 });
        (rawData as any[]).forEach((r: any) => {
          if (r.indicator !== 'XPRT-TRD-VL') return;
          const y = parseInt(r.year);
          const v = (parseFloat(r.value) || 0) * 1000;
          if (r.reporter === rep) {
            const cur = yearMap.get(y)!; yearMap.set(y, { exports: cur.exports + v, imports: cur.imports });
          }
          if (r.partner === rep) {
            const cur = yearMap.get(y)!; yearMap.set(y, { exports: cur.exports, imports: cur.imports + v });
          }
        });
        return Array.from(yearMap.entries()).map(([year, d]) => ({ year, exports: d.exports, imports: d.imports, balance: d.exports - d.imports }));
      };
      grids = topReporters.map((rep) => ({ reporter: rep, data: buildSeries(rep) }));
    } else if (chartType === 'chord') {
      // Build simple chord data per reporter for current year (use 2022) and topN partners
      const buildChord = (rep: string) => {
        const year = '2022';
        const filtered = (rawData as any[]).filter((r: any) => r.year === year && r.indicator === 'XPRT-TRD-VL' && (r.reporter === rep || r.partner === rep));
        // Build using same logic as buildCountryChord without importing (to keep this file self-contained)
        const counterpartTotals = new Map<string, number>();
        filtered.forEach((r: any) => {
          const v = (parseFloat(r.value) || 0) * 1000;
          if (r.reporter === rep) counterpartTotals.set(r.partner, (counterpartTotals.get(r.partner) || 0) + v);
          if (r.partner === rep) counterpartTotals.set(r.reporter, (counterpartTotals.get(r.reporter) || 0) + v);
        });
        let counterparts = Array.from(counterpartTotals.keys()).filter((c) => c !== rep && c !== 'ROW');
        counterparts.sort((a, b) => (counterpartTotals.get(b) || 0) - (counterpartTotals.get(a) || 0));
        const topN = 8;
        const top = counterparts.slice(0, topN);
        const countries = [rep, ...top, 'ROW'];
        const idx = new Map(countries.map((c, i) => [c, i]));
        const matrix: number[][] = Array(countries.length).fill(0).map(() => Array(countries.length).fill(0));
        function add(repC: string, parC: string, v: number) {
          const rk = top.includes(repC) || repC === rep ? repC : 'ROW';
          const pk = top.includes(parC) || parC === rep ? parC : 'ROW';
          const i = idx.get(rk)!; const j = idx.get(pk)!; matrix[i][j] += v;
        }
        filtered.forEach((r: any) => {
          const v = (parseFloat(r.value) || 0) * 1000;
          add(r.reporter, r.partner, v);
        });
        const labels = countries; // compact labels only codes
        return { matrix, countries, countryLabels: labels };
      };
      grids = topReporters.map((rep) => ({ reporter: rep, data: buildChord(rep) }));
    }
  }
</script>

<div class="all-header">
  <h1>Top 25 Reporters</h1>
  <div class="toggle">
    <button class:active={chartType==='bump'} on:click={() => { chartType='bump'; rebuildGrids(); }} title="Bump (rank)">
      <!-- bump icon -->
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2"><path d="M3 17l5-6 4 3 5-8 4 6"/></svg>
    </button>
    <button class:active={chartType==='trend'} on:click={() => { chartType='trend'; rebuildGrids(); }} title="Trend (balance)">
      <!-- trend icon -->
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2"><path d="M3 17h18M4 16l5-5 4 3 6-7"/></svg>
    </button>
    <button class:active={chartType==='trending'} on:click={() => { chartType='trending'; rebuildGrids(); }} title="Trending (bars)">
      <!-- trending bars icon -->
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7v10M11 7v10M15 7v10M19 7v10"/></svg>
    </button>
    <button class:active={chartType==='chord'} on:click={() => { chartType='chord'; rebuildGrids(); }} title="Chord (compact)">
      <!-- chord icon -->
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3v18"/></svg>
    </button>
  </div>
</div>

<div class="grid">
  {#each grids as g}
    <div class="card">
      <div class="card-title">{g.reporter}</div>
      {#if chartType === 'bump'}
        <BumpChart data={g.data} width={380} height={220} />
      {:else if chartType === 'trend'}
        <TradeBalanceChart data={g.data} width={380} height={220} margin={{ top: 20, right: 30, bottom: 40, left: 60 }} />
      {:else if chartType === 'trending'}
        <TrendingTradeBalance data={g.data} width={380} height={220} margin={{ top: 20, right: 30, bottom: 40, left: 60 }} />
      {:else}
        <ChordDiagram data={g.data} configOverride={{ width: 380, height: 380, margin: 80, showLabels: false, showTooltip: false, rimOuterOffset: 12, padAngle: 0.02 }} />
      {/if}
    </div>
  {/each}
  {#if grids.length === 0}
    <p>Loading…</p>
  {/if}
  
</div>

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 16px;
  }

  .card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    padding: 8px 8px 0 8px;
  }

  .card-title {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin: 4px 8px 8px 8px;
  }
</style>


