<script lang="ts">
  import * as d3 from 'd3';
  import type { ProductTreemapData } from '$lib/utils/productAnalysis';

  export let data: ProductTreemapData[] = [];
  export let width: number = 800;
  export let height: number = 600;
  export let margin = { top: 20, right: 20, bottom: 20, left: 20 };

  let container: HTMLDivElement;

  $: if (container && data) render();

  // Centralized styling configuration
  const config = {
    colors: {
      positive: '#08605F',
      negative: '#931F1D',
      neutral: '#6B7280',
      background: '#F9FAFB',
      text: '#111827',
      textSecondary: '#6B7280'
    },
    font: {
      family: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
      size: {
        title: '14px',
        value: '12px',
        growth: '10px'
      }
    },
    treemap: {
      padding: 2,
      round: true
    }
  };

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

    // Add rectangles
    cells.append('rect')
      .attr('width', (d: any) => d.x1 - d.x0)
      .attr('height', (d: any) => d.y1 - d.y0)
      .attr('fill', (d: any) => getGrowthColor(d.data.growth))
      .attr('opacity', 0.8)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 1)
      .on('mouseover', function(event, d: any) {
        const html = `
          <div style="font-weight:700;margin-bottom:6px;">${d.data.product}</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
            <div style="color:#6B7280;">Value</div><div style="color:#374151;font-weight:700;">${formatValue(d.data.value)}</div>
            <div style="color:#6B7280;">Share</div><div style="color:#374151;font-weight:700;">${(d.data.share * 100).toFixed(1)}%</div>
            <div style="color:#6B7280;">Growth</div><div style="color:${getGrowthColor(d.data.growth)};font-weight:700;">${formatGrowth(d.data.growth)}</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function(event) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function() {
        tooltip.style('opacity', 0);
      });

    // Add text labels (only if there's enough space)
    cells.each(function(d: any) {
      const cell = d3.select(this);
      const cellWidth = d.x1 - d.x0;
      const cellHeight = d.y1 - d.y0;
      
      // Only add text if cell is large enough
      if (cellWidth > 60 && cellHeight > 30) {
        // Product name
        cell.append('text')
          .attr('x', 4)
          .attr('y', 14)
          .attr('font-family', config.font.family)
          .attr('font-size', config.font.size.title)
          .attr('font-weight', '600')
          .attr('fill', '#ffffff')
          .text(d.data.product.replace(/^\d+-\d+_/, '')); // Remove numeric prefix
        
        // Value
        cell.append('text')
          .attr('x', 4)
          .attr('y', 28)
          .attr('font-family', config.font.family)
          .attr('font-size', config.font.size.value)
          .attr('fill', '#ffffff')
          .attr('opacity', 0.9)
          .text(formatValue(d.data.value));
        
        // Growth (only if there's space)
        if (cellHeight > 40) {
          cell.append('text')
            .attr('x', 4)
            .attr('y', 42)
            .attr('font-family', config.font.family)
            .attr('font-size', config.font.size.growth)
            .attr('fill', '#ffffff')
            .attr('opacity', 0.8)
            .text(formatGrowth(d.data.growth));
        }
      }
    });
  }
</script>

<div bind:this={container}></div>

<style>
  :global(svg text) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }
</style>
