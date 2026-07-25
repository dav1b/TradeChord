<script lang="ts">
  import ChordDiagram from '$components/ChordDiagram.svelte';
  import TradeBalanceChart from '$components/TradeBalanceChart.svelte';
  import BumpChart from '$components/BumpChart.svelte';
  import SlopeChart from '$components/SlopeChart.svelte';
  import ProductTreemap from '$components/ProductTreemap.svelte';
  import ProductTrendChart from '$components/ProductTrendChart.svelte';
  import PartnerTreemap from '$components/PartnerTreemap.svelte';
  import ProductSlopeChart from '$components/ProductSlopeChart.svelte';
  import SlopeChartGeneric from '$components/SlopeChartGeneric.svelte';
  import TreemapGeneric from '$components/TreemapGeneric.svelte';
  import AICommentary from '$components/AICommentary.svelte';
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import { transformTradeData, buildCountryChord } from '$lib/utils/transform';
  import { buildTimeSeriesData, buildExportRankSeries, buildSlopeData, buildSlopeShareData, buildProductSlopeData } from '$lib/utils/timeSeries';
  import { DASHBOARD, formatWithSuffix } from '$lib/utils/config';
  import { getProductTreemapData, getProductTrendData, getPartnerTreemapData, getAvailableCountries, getAvailableYears } from '$lib/utils/productAnalysis';
  import type { SimpleChordData, BowtieData, SankeyData } from '$lib/utils/transform';
  import type { TimeSeriesData } from '$lib/utils/timeSeries';
  import type { ProductTreemapData, ProductTrendData, PartnerTreemapData } from '$lib/utils/productAnalysis';
  import TrendingTradeBalance from '$components/TrendingTradeBalance.svelte';
  import MiniLine from '$components/MiniLine.svelte';

  // Chord width is 800px in the chord component; use same width for the equation
  const CHORD_WIDTH = 800;
  const SQUARE_SIZE = Math.floor(CHORD_WIDTH / 3);
  const NUMBER_BLOCK_H = 64; // approximate vertical space used by value + label

  let chordData: SimpleChordData | null = null;
  let timeSeriesData: TimeSeriesData[] = [];

  let data: any[] = [];
  let countries: string[] = [];
  let years: string[] = [];
  let selectedCountry = 'USA';
  let selectedYear = String(DASHBOARD.END_YEAR);
  let topN = DASHBOARD.TOP_N_PARTNERS;
  let countryStats: { exports: number, imports: number, balance: number } | null = null;
  let bumpData: any[] = [];
  let slopeData: any[] = [];
  let compareYear = String(DASHBOARD.START_YEAR);
  
  // Product analysis data
  let productTreemapData: ProductTreemapData[] = [];
  let productTrendData: ProductTrendData[] = [];
  
  // Partner analysis data
  let partnerTreemapData: PartnerTreemapData[] = [];
  let productSlopeData: any[] = [];

  function rebuildCharts() {
    if (!data.length) return;
    
    console.log('Rebuilding charts for country:', selectedCountry);
    
    // Filter data for chord diagram and time series (use only "Total" product records)
    const totalData = data.filter((r: any) => r.product === 'Total');
    console.log('Total data records:', totalData.length);
    
    chordData = buildCountryChord(totalData as any, selectedCountry, topN, selectedYear);
    timeSeriesData = buildTimeSeriesData(totalData as any, selectedCountry);
    bumpData = buildExportRankSeries(totalData as any, selectedCountry, 10, 2002, 2022);
    slopeData = buildSlopeShareData(
      totalData as any,
      selectedCountry,
      parseInt(compareYear),
      parseInt(selectedYear),
      topN,
      'exports'
    );
    
    // Build product charts data (use all data for product analysis, exclude "Total")
    try {
      const productData = data.filter((r: any) => r.product !== 'Total');
      productTreemapData = getProductTreemapData(productData as any, selectedCountry, selectedYear);
      productTrendData = getProductTrendData(productData as any, selectedCountry);
    } catch (error) {
      console.error('Error building product charts data:', error);
      productTreemapData = [];
      productTrendData = [];
    }
    
    // Build partner charts data (use only "Total" product records)
    try {
      console.log('Building partner treemap for:', selectedCountry, selectedYear);
      console.log('Total data records for partner treemap:', totalData.length);
      partnerTreemapData = getPartnerTreemapData(totalData as any, selectedCountry, selectedYear);
      console.log('Partner treemap data loaded:', partnerTreemapData.length, 'partners');
      if (partnerTreemapData.length > 0) {
        console.log('Sample partner data:', partnerTreemapData[0]);
      }
    } catch (error) {
      console.error('Error building partner treemap data:', error);
      partnerTreemapData = [];
    }
    
    // Build product slope data (use all data for product analysis, exclude "Total")
    try {
      const productData = data.filter((r: any) => r.product !== 'Total');
      productSlopeData = buildProductSlopeData(
        productData as any,
        selectedCountry,
        parseInt(compareYear),
        parseInt(selectedYear),
        topN,
        'exports'
      );
      console.log('Product slope data loaded:', productSlopeData.length, 'products');
    } catch (error) {
      console.error('Error building product slope data:', error);
      productSlopeData = [];
    }
    
    // Calculate country stats for selected year (use only "Total" product records)
    const yearData = totalData.filter((r: any) => r.year === selectedYear && r.indicator === 'XPRT-TRD-VL');
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
    
    console.log('Charts rebuilt successfully');
  }

  // Rebuild charts whenever the selected country changes (and data is loaded)
  $: if (data.length && selectedCountry) {
    rebuildCharts();
  }

  // Function to create "Total" records by aggregating all products
  function createTotalRecords(productData: any[]): any[] {
    const totalRecords: any[] = [];
    const grouped = new Map<string, { year: string, reporter: string, partner: string, indicator: string, value: number }>();
    
    // Group by year, reporter, partner, indicator
    productData.forEach((record: any) => {
      if (record.product === 'product') return; // Skip header row
      
      const key = `${record.year}|${record.reporter}|${record.partner}|${record.indicator}`;
      if (!grouped.has(key)) {
        grouped.set(key, {
          year: record.year,
          reporter: record.reporter,
          partner: record.partner,
          indicator: record.indicator,
          value: 0
        });
      }
      
      const value = parseFloat(record.value) || 0;
      const existing = grouped.get(key)!;
      existing.value += value;
    });
    
    // Create total records
    grouped.forEach((data) => {
      totalRecords.push({
        year: data.year,
        reporter: data.reporter,
        partner: data.partner,
        product: 'Total',
        indicator: data.indicator,
        value: data.value.toString()
      });
    });
    
    return totalRecords;
  }

  onMount(async () => {
    try {
      // Load unified dataset
      console.log('Loading data...');
      const productData = await d3.csv('/data/complete_export_matrix.csv');
      
      console.log('Product data loaded:', productData.length, 'records');
      
      if (!productData || productData.length === 0) {
        throw new Error('No data loaded from CSV file');
      }
      
      // Filter out blocked reporters (but keep them as partners)
      const blockedReporters = new Set(['RUS', 'THA']);
      const productDataFiltered = (productData as any[]).filter(
        (r: any) => !blockedReporters.has(r.reporter)
      );
      console.log('After filtering blocked reporters (RUS, THA):', productDataFiltered.length, 'records');
      
      // Create total records for chord diagram and partner analysis
      console.log('Creating total records...');
      const totalRecords = createTotalRecords(productDataFiltered as any);
      console.log('Total records created:', totalRecords.length);
      
      // Combine product data with total records
      data = [...productDataFiltered, ...totalRecords];
      
      console.log('Combined data loaded:', data.length, 'records');
      
      if (data && data.length > 0) {
        // Get available countries and years from unified dataset
        console.log('Getting available countries...');
        countries = getAvailableCountries(data as any);
        years = Array.from(new Set((data as any[]).map((r) => r.year))).sort();
        
        console.log('Available countries:', countries.length);
        console.log('Available years:', years);
        
        // Ensure selected country is available in data
        if (!countries.includes(selectedCountry)) {
          selectedCountry = countries[0] || 'USA';
        }
        
        console.log('Selected country:', selectedCountry);
        console.log('Selected year:', selectedYear);
        
        console.log('Rebuilding charts...');
        rebuildCharts();
        console.log('Charts rebuilt successfully');
      } else {
        throw new Error('No data available after processing');
      }
    } catch (error) {
      console.error('Error loading data:', error);
      console.error('Error details:', error);
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

<label for="country">Select country (with product data):</label>
<select id="country" bind:value={selectedCountry} on:input={rebuildCharts}>
  {#each countries as c}
    <option value={c}>{c}</option>
  {/each}
</select>

<!-- Year and TopN controls removed per dashboard config. Using DASHBOARD constants. -->

<div class="dashboard">
  <div class="left-pane">
    <div class="left-header">
      {#if countryStats}
        <div class="equation-wide" style={`--sq:${SQUARE_SIZE}px; --cw:${CHORD_WIDTH}px;`}>
          <div class="eq-col">
            <div class="big-stat" style="--c:#08605F;">
              <div class="big-value center">{formatWithSuffix(countryStats.exports)}</div>
              <div class="big-label center">Exports</div>
            </div>
            <MiniLine width={SQUARE_SIZE} height={Math.max(60, SQUARE_SIZE - NUMBER_BLOCK_H)} color="#08605F" data={timeSeriesData.map(d=>({year:d.year, value:d.exports}))} />
          </div>
          <div class="eq-op">-</div>
          <div class="eq-col">
            <div class="big-stat" style="--c:#931F1D;">
              <div class="big-value center">{formatWithSuffix(countryStats.imports)}</div>
              <div class="big-label center">Imports</div>
            </div>
            <MiniLine width={SQUARE_SIZE} height={Math.max(60, SQUARE_SIZE - NUMBER_BLOCK_H)} color="#931F1D" data={timeSeriesData.map(d=>({year:d.year, value:d.imports}))} />
          </div>
          <div class="eq-op">=</div>
          <div class="eq-col">
            <div class="big-stat" style="--c:{countryStats.balance >= 0 ? '#08605F' : '#931F1D'};">
              <div class="big-value center">{countryStats.balance >= 0 ? '+' : '-'}{formatWithSuffix(Math.abs(countryStats.balance))}</div>
              <div class="big-label center">Balance</div>
            </div>
            <TrendingTradeBalance 
              data={timeSeriesData.map(d=>({year:d.year,exports:d.exports,imports:d.imports,balance:d.exports-d.imports}))}
              reporter={selectedCountry}
              width={SQUARE_SIZE}
              height={Math.max(60, SQUARE_SIZE - NUMBER_BLOCK_H)}
              margin={{top:6,right:10,bottom:14,left:10}}
            />
          </div>
        </div>
      {/if}
    </div>
    {#if chordData}
      {#key selectedCountry + '-' + selectedYear}
      <div class="chord-card">
        <ChordDiagram data={chordData} rawData={data} year={selectedYear} />
      </div>
      {/key}
    {/if}
  </div>
  <div class="right-pane">
    <div class="treemaps">
      {#if productTreemapData.length > 0}
        <div class="treemap-card">
          <h2>Product Export Breakdown — {selectedCountry} ({selectedYear})</h2>
          <TreemapGeneric 
            width={420} height={520}
            data={productTreemapData.map(p => ({
              id: p.product,
              name: p.product.replace(/^\d+-\d+_/, ''),
              value: p.value,
              share: p.share,
              latestBalance: (p.trendData && p.trendData.length) ? p.trendData[p.trendData.length-1].value : 0,
              trendData: p.trendData
            }))}
            buildTooltip={(d) => {
              const latest = d.trendData && d.trendData.length ? d.trendData[d.trendData.length-1].value : 0;
              const imports = d.value - latest; // exports - balance = imports
              return `
                <div style="font-weight:700;margin-bottom:6px;">${d.name}</div>
                <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
                  <div style=\"color:#6B7280;\">Exports</div><div style=\"color:#374151;font-weight:700;\">${(d.value/1e9).toFixed(1)}B</div>
                  <div style=\"color:#6B7280;\">Imports</div><div style=\"color:#374151;font-weight:700;\">${(imports/1e9).toFixed(1)}B</div>
                  <div style=\"color:#6B7280;\">Trade Balance</div><div style=\"color:${latest>=0?'#08605F':'#931F1D'};font-weight:700;\">${((Math.abs(latest))/1e9).toFixed(1)}B ${latest>=0?'+':'-'}</div>
                  ${d.share!=null?`<div style=\"color:#6B7280;\">Share</div><div style=\"color:#374151;font-weight:700;\">${(d.share*100).toFixed(1)}%</div>`:''}
                </div>`;
            }}
            renderMiniChart={(g, item, aw, ah) => {
              // Product: trade balance mini bars with zero line
              const maxW = Math.min(84, aw);
              const h = 16; if (maxW < 30) return;
              if (!item.trendData || item.trendData.length < 2) return;
              const data = item.trendData.slice().sort((a,b)=>a.year-b.year);
              const x = d3.scaleLinear().domain([data[0].year, data[data.length-1].year]).range([2, maxW-2]);
              const y = d3.scaleLinear().domain(d3.extent(data, d=>d.value) as [number, number]).range([h-2, 2]);
              const hasPos = d3.max(data, d=>d.value)!>0; const hasNeg = d3.min(data, d=>d.value)!<0;
              if (hasPos && hasNeg) { const zy = y(0); g.append('line').attr('x1',2).attr('x2',maxW-2).attr('y1',zy).attr('y2',zy).attr('stroke','#fff').attr('opacity',0.6).attr('stroke-width',0.5); }
              g.selectAll('rect').data(data).enter().append('rect')
                .attr('x',d=>x(d.year)-1).attr('width',3)
                .attr('y',d=> d.value>=0? y(d.value): y(0))
                .attr('height',d=> d.value>=0? y(0)-y(d.value): y(d.value)-y(0))
                .attr('fill',d=> d.value>=0? '#08605F':'#931F1D');
            }}
          />
        </div>
      {/if}
      {#if partnerTreemapData.length > 0}
        <div class="treemap-card">
          <h2>Partner Export Breakdown — {selectedCountry} ({selectedYear})</h2>
          <TreemapGeneric 
            width={420} height={520}
            data={partnerTreemapData.map(p => ({
              id: p.partner,
              name: p.partner,
              value: p.value,
              share: p.share,
              latestBalance: (p.trendData && p.trendData.length) ? p.trendData[p.trendData.length-1].value : 0,
              trendData: p.trendData
            }))}
            buildTooltip={(d) => {
              const latest = d.trendData && d.trendData.length ? d.trendData[d.trendData.length-1].value : 0;
              const imports = d.value - latest;
              return `
                <div style="font-weight:700;margin-bottom:6px;">${d.name}</div>
                <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
                  <div style=\"color:#6B7280;\">Exports</div><div style=\"color:#374151;font-weight:700;\">${(d.value/1e9).toFixed(1)}B</div>
                  <div style=\"color:#6B7280;\">Imports</div><div style=\"color:#374151;font-weight:700;\">${(imports/1e9).toFixed(1)}B</div>
                  <div style=\"color:#6B7280;\">Trade Balance</div><div style=\"color:${latest>=0?'#08605F':'#931F1D'};font-weight:700;\">${((Math.abs(latest))/1e9).toFixed(1)}B ${latest>=0?'+':'-'}</div>
                  ${d.share!=null?`<div style=\"color:#6B7280;\">Share</div><div style=\"color:#374151;font-weight:700;\">${(d.share*100).toFixed(1)}%</div>`:''}
                </div>`;
            }}
            renderMiniChart={(g, item, aw, ah) => {
              // Partner: simple line spark (colored by latest balance)
              const maxW = Math.min(84, aw); const h=16; if (maxW<30) return;
              if (!item.trendData || item.trendData.length<2) return;
              const data = item.trendData.slice().sort((a,b)=>a.year-b.year);
              const x = d3.scaleLinear().domain([data[0].year, data[data.length-1].year]).range([2,maxW-2]);
              const y = d3.scaleLinear().domain(d3.extent(data, d=>d.value) as [number,number]).range([h-2,2]);
              const line = d3.line<any>().x((d:any)=>x(d.year)).y((d:any)=>y(d.value)).curve(d3.curveMonotoneX);
              g.append('path').datum(data).attr('d',line).attr('fill','none').attr('stroke', (item.latestBalance??0)>=0? '#08605F':'#931F1D').attr('stroke-width',1.5).attr('opacity',0.8);
            }}
          />
        </div>
      {/if}
    </div>
    <div class="slopes">
      {#if slopeData.length > 0}
        <div class="slope-card">
          <h3>Top {topN} Partners — Exports {compareYear} → {selectedYear}</h3>
          <SlopeChartGeneric 
            data={slopeData}
            labelKey={'partner'}
            isPartner={true}
            rowKey={'ROW'}
            showTopNLabels={3}
            year1={parseInt(compareYear)}
            year2={parseInt(selectedYear)}
            reporter={selectedCountry}
            mode="exports"
            width={340}
            height={260}
          />
        </div>
      {/if}
      {#if productSlopeData.length > 0}
        <div class="slope-card">
          <h3>Top {topN} Products — Exports {compareYear} → {selectedYear}</h3>
          <!-- NOTE: product slope data reuses the 'partner' field to carry the product name.
               We therefore set labelKey='partner' here. If the pipeline emits a 'product'
               property in future, switch this to labelKey='product'. -->
          <SlopeChartGeneric 
            data={productSlopeData}
            labelKey={'partner'}
            isPartner={false}
            showTopNLabels={3}
            year1={parseInt(compareYear)}
            year2={parseInt(selectedYear)}
            reporter={selectedCountry}
            mode="exports"
            width={340}
            height={260}
          />
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- AI Commentary Section -->
<AICommentary 
  data={data} 
  productData={data} 
  countryCode={selectedCountry} 
  year={selectedYear} 
/>

<div class="footer">
  <div>Source: Local CSV derived from WITS/UN Comtrade. Year range {DASHBOARD.START_YEAR}–{DASHBOARD.END_YEAR}.</div>
  <div>Designed by DoC</div>
  
</div>

<style>
  .dashboard {
    display: grid;
    grid-template-columns: 820px 920px;
    gap: 20px;
    align-items: start;
    margin-top: 16px;
    max-width: 1760px;
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

  .big-stat { display: flex; align-items: baseline; gap: 8px; }
  .big-value { font-size: 36px; font-weight: 800; color: var(--c); }
  .big-label { font-size: 12px; color: #6B7280; font-weight: 600; }

  .treemaps { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .slopes { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

  .footer {
    margin-top: 16px;
    padding: 12px 8px;
    color: #6B7280;
    font-size: 12px;
    display: flex;
    justify-content: space-between;
  }

  .equation-wide{
    display:grid;
    grid-template-columns: var(--sq) 24px var(--sq) 24px var(--sq);
    align-items: start;
    gap: 8px;
    width: var(--cw);
  }
  .eq-col{ width: var(--sq); height: var(--sq); display:flex; flex-direction:column; align-items:center; justify-content:flex-start; gap:6px; }
  .eq-op{ font-size: 28px; color:#6B7280; display:flex; align-items:center; justify-content:center; }
  .center{ text-align:center; }

  @media (max-width: 900px) {
    .dashboard { grid-template-columns: 1fr; max-width: 100%; min-height: auto; }
    .treemaps { grid-template-columns: 1fr; }
    .slopes { grid-template-columns: 1fr; }
  }

</style>
