<script lang="ts">
  import * as d3 from 'd3';
  import type { ProductTreemapData, ProductTrendData } from '$lib/utils/productAnalysis';
  import ProductTrendModal from './ProductTrendModal.svelte';

  // Configuration
  const config = {
    colors: {
      positive: '#08605F',
      negative: '#931F1D',
      neutral: '#6B7280'
    },
    font: {
      family: 'Inter, sans-serif',
      size: {
        title: '12px',
        value: '10px'
      }
    },
    treemap: {
      padding: 2,
      round: true
    }
  };

  export let data: ProductTreemapData[] = [];
  export let width: number = 800;
  export let height: number = 600;
  export let margin = { top: 20, right: 20, bottom: 20, left: 20 };

  let container: HTMLDivElement;
  let modalOpen = false;
  let selectedProduct = '';
  let selectedTrendData: ProductTrendData[] = [];

  $: if (container && data) render();


  function formatValue(value: number): string {
    const abs = Math.abs(value);
    const units = [
      { v: 1e12, s: 'T' },
      { v: 1e9, s: 'B' },
      { v: 1e6, s: 'M' },
      { v: 1e3, s: 'K' }
    ];
    for (const u of units) {
      if (abs >= u.v) {
        const n = abs / u.v;
        const str = n < 10 ? n.toFixed(1) : Math.round(n).toString();
        return `$${str}${u.s}`;
      }
    }
    return `$${abs.toFixed(abs < 10 ? 1 : 0)}`;
  }

  function formatGrowth(growth: number): string {
    const sign = growth >= 0 ? '+' : '';
    return `${sign}${growth.toFixed(1)}%`;
  }

  function getGrowthColor(growth: number): string {
    if (growth > 5) return config.colors.positive;
    if (growth < -5) return config.colors.negative;
    return config.colors.neutral;
  }

  function openModal(productName: string, trendData: ProductTrendData[]) {
    selectedProduct = productName;
    selectedTrendData = trendData;
    modalOpen = true;
  }

  function closeModal() {
    modalOpen = false;
    selectedProduct = '';
    selectedTrendData = [];
  }

  function renderMiniTrendChart(cell: any, d: any) {
    if (!d.data.trendData || d.data.trendData.length < 2) return;
    
    const cellWidth = d.x1 - d.x0;
    const cellHeight = d.y1 - d.y0;
    
    // Position directly below labels (after product name, value, and growth)
    const labelBottom = 50; // Space for labels
    const miniChartHeight = 16; // Fixed height for mini chart
    const miniChartWidth = Math.min(84, cellWidth - 16); // Max 84px width, adjusted for padding
    
    // Check if there's enough space below labels
    if (cellHeight < labelBottom + miniChartHeight + 8) return; // Not enough space
    if (miniChartWidth < 30) return; // Too narrow
    
    const trendData = d.data.trendData.sort((a: any, b: any) => a.year - b.year);
    const values = trendData.map((item: any) => item.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    
    // For trade balance, we need to handle negative values properly
    const hasNegativeValues = minValue < 0;
    const hasPositiveValues = maxValue > 0;
    const zeroLine = hasNegativeValues && hasPositiveValues ? 0 : minValue;
    
    const xScale = d3.scaleLinear()
      .domain([trendData[0].year, trendData[trendData.length - 1].year])
      .range([2, miniChartWidth - 2]);
    
    const yScale = d3.scaleLinear()
      .domain([minValue, maxValue])
      .range([miniChartHeight - 2, 2]);
    
    const miniChart = cell.append('g')
      .attr('class', 'mini-trend')
      .attr('transform', `translate(8, ${labelBottom})`); // Adjusted for padding
    
    // Draw zero line if we have both positive and negative values
    if (hasNegativeValues && hasPositiveValues) {
      const zeroY = yScale(0);
      miniChart.append('line')
        .attr('x1', 2)
        .attr('x2', miniChartWidth - 2)
        .attr('y1', zeroY)
        .attr('y2', zeroY)
        .attr('stroke', '#ffffff')
        .attr('opacity', 0.6)
        .attr('stroke-width', 0.5);
    }
    
    // Draw mini bars for trade balance with tooltips
    miniChart.selectAll('.mini-bar')
      .data(trendData)
      .enter()
      .append('rect')
      .attr('class', 'mini-bar')
      .attr('x', (item: any) => xScale(item.year) - 1)
      .attr('y', (item: any) => {
        const y = yScale(item.value);
        return item.value >= 0 ? y : yScale(0); // Start from zero line for positive, end at zero line for negative
      })
      .attr('width', 3) // Thicker bars
      .attr('height', (item: any) => {
        const y = yScale(item.value);
        return item.value >= 0 ? yScale(0) - y : y - yScale(0); // Height from zero line
      })
      .attr('fill', (item: any) => item.value >= 0 ? '#08605F' : '#931F1D') // Green for positive, red for negative
      .attr('opacity', 0.9)
      .attr('stroke', 'none')
      .on('mouseover', function(event: any, item: any) {
        const tooltip = d3.select(container).select('.tooltip');
        // For mini chart tooltips, we'll show the trade balance and growth
        // The trade balance is the main focus of these mini charts
        const html = `
          <div style="font-weight:700;margin-bottom:4px;">${d.data.product} (${item.year})</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:2px;column-gap:8px;align-items:baseline;">
            <div style="color:#6B7280;">Trade Balance</div><div style="color:${item.value >= 0 ? '#08605F' : '#931F1D'};font-weight:700;">${formatValue(item.value)}</div>
            <div style="color:#6B7280;">Growth</div><div style="color:${item.growth >= 0 ? '#08605F' : '#931F1D'};font-weight:700;">${formatGrowth(item.growth)}</div>
            <div style="color:#6B7280;font-size:9px;grid-column:1/-1;margin-top:2px;border-top:1px solid #E5E7EB;padding-top:2px;">
              Trade Balance = Exports - Imports
            </div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function(event: any) {
        const tooltip = d3.select(container).select('.tooltip');
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function() {
        const tooltip = d3.select(container).select('.tooltip');
        tooltip.style('opacity', 0);
      });
  }

  function render() {
    d3.select(container).select('svg').remove();
    d3.select(container).select('.tooltip').remove();

    if (!data || data.length === 0) return;

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Tooltip
    const tooltip = d3.select(container)
      .append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('background', '#ffffff')
      .style('color', '#111827')
      .style('border', '1px solid #E5E7EB')
      .style('box-shadow', '0 4px 16px rgba(0,0,0,0.08)')
      .style('border-radius', '8px')
      .style('padding', '10px 12px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

    // Create treemap layout
    const treemap = d3.treemap<ProductTreemapData>()
      .size([innerWidth, innerHeight])
      .padding(config.treemap.padding)
      .round(config.treemap.round);

    const root = d3.hierarchy({ children: data } as any)
      .sum((d: any) => d.value)
      .sort((a: any, b: any) => (b.value || 0) - (a.value || 0));

    treemap(root);

    const cells = g.selectAll('.cell')
      .data(root.leaves())
      .enter()
      .append('g')
      .attr('class', 'cell')
      .attr('transform', (d: any) => `translate(${d.x0},${d.y0})`);

    // Add white outer border for spacing between elements
    cells.append('rect')
      .attr('x', -1) // Slight outset
      .attr('y', -1) // Slight outset
      .attr('width', (d: any) => d.x1 - d.x0 + 2) // Increased by 2 for border
      .attr('height', (d: any) => d.y1 - d.y0 + 2) // Increased by 2 for border
      .attr('fill', 'none')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2);

    // Add rectangles (lighter neutral color, no growth-based coloring) with padding
    cells.append('rect')
      .attr('x', 4) // Padding from white border
      .attr('y', 4) // Padding from white border
      .attr('width', (d: any) => d.x1 - d.x0 - 8) // Reduced by 8 for padding
      .attr('height', (d: any) => d.y1 - d.y0 - 8) // Reduced by 8 for padding
      .attr('fill', '#E5E7EB') // Lighter gray color
      .attr('opacity', 0.8)
      .attr('stroke', (d: any) => {
        // Get the latest trade balance color for the border
        const latestTrendData = d.data.trendData?.find((item: any) => 
          item.year === Math.max(...(d.data.trendData?.map((t: any) => t.year) || [0]))
        );
        const tradeBalance = latestTrendData?.value || 0;
        return tradeBalance >= 0 ? config.colors.positive : config.colors.negative;
      })
      .attr('stroke-width', 2) // Slightly thicker border for visibility
      .on('mouseover', function(event, d: any) {
        // Calculate exports and imports for this product
        const exports = d.data.value; // This is the export value
        // For imports, we need to calculate from trend data (exports - trade balance = imports)
        const latestTrendData = d.data.trendData?.find((item: any) => item.year === Math.max(...d.data.trendData.map((t: any) => t.year)));
        const tradeBalance = latestTrendData?.value || 0;
        const imports = exports - tradeBalance;
        
        const html = `
          <div style="font-weight:700;margin-bottom:6px;">${d.data.product}</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
            <div style="color:#6B7280;">Exports</div><div style="color:#374151;font-weight:700;">${formatValue(exports)}</div>
            <div style="color:#6B7280;">Imports</div><div style="color:#374151;font-weight:700;">${formatValue(imports)}</div>
            <div style="color:#6B7280;">Trade Balance</div><div style="color:${tradeBalance >= 0 ? '#08605F' : '#931F1D'};font-weight:700;">${formatValue(tradeBalance)}</div>
            <div style="color:#6B7280;">Share</div><div style="color:#374151;font-weight:700;">${(d.data.share * 100).toFixed(1)}%</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function(event) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function() {
        tooltip.style('opacity', 0);
      });

    // Add text labels and mini trend charts (only if there's enough space)
    cells.each(function(d: any) {
      const cell = d3.select(this);
      const cellWidth = d.x1 - d.x0;
      const cellHeight = d.y1 - d.y0;
      
      // Only add text if cell is large enough
      if (cellWidth > 60 && cellHeight > 30) {
        // Get the latest trade balance color
        const latestTrendData = d.data.trendData?.find((item: any) => 
          item.year === Math.max(...(d.data.trendData?.map((t: any) => t.year) || [0]))
        );
        const tradeBalance = latestTrendData?.value || 0;
        const labelColor = tradeBalance >= 0 ? config.colors.positive : config.colors.negative;
        
        // Calculate available space (accounting for padding)
        const availableWidth = cellWidth - 16; // 8px padding on each side
        const availableHeight = cellHeight - 16; // 8px padding on each side
        
        // Create temporary text elements to measure their dimensions
        const tempSvg = d3.select('body').append('svg').style('visibility', 'hidden');
        
        // Measure product name
        const productName = d.data.product.replace(/^\d+-\d+_/, '');
        const productNameText = tempSvg.append('text')
          .attr('font-family', config.font.family)
          .attr('font-size', config.font.size.title)
          .attr('font-weight', '600')
          .text(productName);
        
        const productNameNode = productNameText.node();
        const productNameWidth = productNameNode ? productNameNode.getBBox().width : 0;
        const productNameHeight = productNameNode ? productNameNode.getBBox().height : 0;
        
        // Measure value text
        const valueText = `${formatValue(d.data.value)} (${(d.data.share * 100).toFixed(1)}%)`;
        const valueTextElement = tempSvg.append('text')
          .attr('font-family', config.font.family)
          .attr('font-size', config.font.size.value)
          .text(valueText);
        
        const valueTextNode = valueTextElement.node();
        const valueTextWidth = valueTextNode ? valueTextNode.getBBox().width : 0;
        const valueTextHeight = valueTextNode ? valueTextNode.getBBox().height : 0;
        
        // Clean up temporary SVG
        tempSvg.remove();
        
        // Check if both texts fit within the available space
        const totalTextHeight = productNameHeight + valueTextHeight + 4; // 4px spacing between texts
        const maxTextWidth = Math.max(productNameWidth, valueTextWidth);
        
        // Only show labels and chart if text fits
        if (maxTextWidth <= availableWidth && totalTextHeight <= availableHeight) {
          // Product name
          cell.append('text')
            .attr('x', 8) // Adjusted for padding
            .attr('y', 18) // Adjusted for padding
            .attr('font-family', config.font.family)
            .attr('font-size', config.font.size.title)
            .attr('font-weight', '600')
            .attr('fill', labelColor) // Color based on latest trade balance
            .text(productName);
          
          // Value and Share
          cell.append('text')
            .attr('x', 8) // Adjusted for padding
            .attr('y', 32) // Adjusted for padding
            .attr('font-family', config.font.family)
            .attr('font-size', config.font.size.value)
            .attr('fill', labelColor) // Color based on latest trade balance
            .attr('opacity', 0.9)
            .text(valueText);
          
          // Add mini trend chart only if labels fit AND there's enough space and trend data
          if (cellHeight > 70 && d.data.trendData && d.data.trendData.length > 1) {
            renderMiniTrendChart(cell, d);
          }
        }
      }
    });
  }
</script>

<div bind:this={container}></div>

<!-- Product Trend Modal -->
<ProductTrendModal 
  isOpen={modalOpen}
  productName={selectedProduct}
  trendData={selectedTrendData}
  onClose={closeModal}
/>

<style>
  :global(svg text) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }
</style>
