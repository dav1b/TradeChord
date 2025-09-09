<script lang="ts">
  import * as d3 from 'd3';
  import type { ProductTrendData } from '$lib/utils/productAnalysis';

  export let data: ProductTrendData[] = [];
  export let product: string = '';
  export let width: number = 300;
  export let height: number = 200;
  export let margin = { top: 20, right: 40, bottom: 30, left: 50 };

  let container: HTMLDivElement;

  $: if (container && data) render();

  // Centralized styling configuration
  const config = {
    colors: {
      line: '#3B82F6',
      bar: '#10B981',
      barNegative: '#EF4444',
      axis: '#6B7280',
      text: '#111827',
      textSecondary: '#6B7280',
      background: '#F9FAFB'
    },
    font: {
      family: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
      size: {
        title: '12px',
        axis: '10px',
        value: '9px'
      }
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
      .style('padding', '8px 10px')
      .style('font-size', '11px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

    // Scales
    const xScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.year) as [number, number])
      .range([0, innerWidth]);

    const yValueScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value) || 0])
      .range([innerHeight, 0]);

    const yGrowthScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.growth) as [number, number])
      .range([innerHeight, 0]);

    // Line generator for values
    const line = d3.line<ProductTrendData>()
      .x(d => xScale(d.year))
      .y(d => yValueScale(d.value))
      .curve(d3.curveMonotoneX);

    // Bar width for growth bars
    const barWidth = innerWidth / (data.length - 1) * 0.6;

    // Draw growth bars (background)
    g.selectAll('.growth-bar')
      .data(data.slice(1)) // Skip first year (no growth data)
      .enter()
      .append('rect')
      .attr('class', 'growth-bar')
      .attr('x', d => xScale(d.year) - barWidth / 2)
      .attr('y', d => d.growth >= 0 ? yGrowthScale(d.growth) : yGrowthScale(0))
      .attr('width', barWidth)
      .attr('height', d => Math.abs(yGrowthScale(d.growth) - yGrowthScale(0)))
      .attr('fill', d => d.growth >= 0 ? config.colors.bar : config.colors.barNegative)
      .attr('opacity', 0.3)
      .on('mouseover', function(event, d) {
        const html = `
          <div style="font-weight:700;margin-bottom:4px;">${product} (${d.year})</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:2px;column-gap:8px;align-items:baseline;">
            <div style="color:#6B7280;">Value</div><div style="color:#374151;font-weight:700;">${formatValue(d.value)}</div>
            <div style="color:#6B7280;">Growth</div><div style="color:${d.growth >= 0 ? config.colors.bar : config.colors.barNegative};font-weight:700;">${formatGrowth(d.growth)}</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function(event) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function() {
        tooltip.style('opacity', 0);
      });

    // Draw value line
    g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', config.colors.line)
      .attr('stroke-width', 2)
      .attr('d', line);

    // Draw value dots
    g.selectAll('.value-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'value-dot')
      .attr('cx', d => xScale(d.year))
      .attr('cy', d => yValueScale(d.value))
      .attr('r', 3)
      .attr('fill', config.colors.line)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 1)
      .on('mouseover', function(event, d) {
        const html = `
          <div style="font-weight:700;margin-bottom:4px;">${product} (${d.year})</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:2px;column-gap:8px;align-items:baseline;">
            <div style="color:#6B7280;">Value</div><div style="color:#374151;font-weight:700;">${formatValue(d.value)}</div>
            <div style="color:#6B7280;">Growth</div><div style="color:${d.growth >= 0 ? config.colors.bar : config.colors.barNegative};font-weight:700;">${formatGrowth(d.growth)}</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function(event) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function() {
        tooltip.style('opacity', 0);
      });

    // Left axis (values)
    const yAxisLeft = d3.axisLeft(yValueScale)
      .tickFormat(d => formatValue(d as number))
      .ticks(4);

    g.append('g')
      .attr('class', 'y-axis-left')
      .call(yAxisLeft)
      .call(g => g.selectAll('.domain').remove())
      .call(g => g.selectAll('.tick line').remove())
      .call(g => g.selectAll('.tick text')
        .attr('font-family', config.font.family)
        .attr('font-size', config.font.size.axis)
        .attr('fill', config.colors.textSecondary));

    // Right axis (growth)
    const yAxisRight = d3.axisRight(yGrowthScale)
      .tickFormat(d => `${d}%`)
      .ticks(4);

    g.append('g')
      .attr('class', 'y-axis-right')
      .attr('transform', `translate(${innerWidth},0)`)
      .call(yAxisRight)
      .call(g => g.selectAll('.domain').remove())
      .call(g => g.selectAll('.tick line').remove())
      .call(g => g.selectAll('.tick text')
        .attr('font-family', config.font.family)
        .attr('font-size', config.font.size.axis)
        .attr('fill', config.colors.textSecondary));

    // X axis
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d => d.toString())
      .ticks(5);

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .call(g => g.selectAll('.domain').remove())
      .call(g => g.selectAll('.tick line').remove())
      .call(g => g.selectAll('.tick text')
        .attr('font-family', config.font.family)
        .attr('font-size', config.font.size.axis)
        .attr('fill', config.colors.textSecondary));

    // Zero line for growth
    g.append('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', yGrowthScale(0))
      .attr('y2', yGrowthScale(0))
      .attr('stroke', config.colors.axis)
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '2,2')
      .attr('opacity', 0.5);
  }
</script>

<div bind:this={container}></div>

<style>
  :global(svg text) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }
</style>
