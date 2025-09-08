<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let data: { country: string, exports: number, imports: number }[];

  let container: HTMLDivElement;

  onMount(() => {
    console.log('Data received in DivergingBarChart:', data);
    if (data && container) {
      drawChart();
    }
  });

  function drawChart() {
    const margin = { top: 30, right: 60, bottom: 10, left: 60 };
    const width = 960 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const svg = d3.select(container)
      .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    const top10Data = data.slice(0, 10);

    const y = d3.scaleBand()
      .domain(top10Data.map(d => d.country))
      .range([0, height])
      .padding(0.1);

    const maxExports = d3.max(top10Data, d => d.exports) || 0;
    const maxImports = d3.max(top10Data, d => d.imports) || 0;
    const maxVal = Math.max(maxExports, maxImports);

    const x = d3.scaleLinear()
      .domain([-maxVal, maxVal])
      .range([0, width]);

    // Center line
    svg.append('line')
      .attr('x1', x(0))
      .attr('x2', x(0))
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', 'black');

    // Export bars (left)
    svg.selectAll('.bar.export')
      .data(top10Data)
      .enter().append('rect')
        .attr('class', 'bar export')
        .attr('y', d => y(d.country)!)
        .attr('height', y.bandwidth())
        .attr('x', d => x(-d.exports))
        .attr('width', d => x(0) - x(-d.exports))
        .attr('fill', 'steelblue');

    // Import bars (right)
    svg.selectAll('.bar.import')
      .data(top10Data)
      .enter().append('rect')
        .attr('class', 'bar import')
        .attr('y', d => y(d.country)!)
        .attr('height', y.bandwidth())
        .attr('x', x(0))
        .attr('width', d => x(d.imports) - x(0))
        .attr('fill', 'tomato');
    
    // Country labels
    svg.selectAll('.label')
        .data(top10Data)
        .enter().append('text')
        .attr('class', 'label')
        .attr('x', width / 2)
        .attr('y', d => y(d.country)! + y.bandwidth() / 2)
        .attr('dy', '0.35em')
        .style('text-anchor', 'middle')
        .text(d => d.country);

    // Add titles
    svg.append('text')
        .attr('x', x(-maxVal / 2))
        .attr('y', -10)
        .style('text-anchor', 'middle')
        .text('Exports From');

    svg.append('text')
        .attr('x', x(maxVal / 2))
        .attr('y', -10)
        .style('text-anchor', 'middle')
        .text('Exports To');
  }
</script>

<div bind:this={container}></div>

<style>
  .bar.export {
    shape-rendering: crispEdges;
  }
  .bar.import {
    shape-rendering: crispEdges;
  }
  .label {
    font-size: 12px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }
</style> 