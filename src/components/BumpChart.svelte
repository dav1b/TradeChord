<script lang="ts">
  import * as d3 from 'd3';
  import type { PartnerRankSeries } from '$lib/utils/timeSeries';

  export let data: PartnerRankSeries[] = [];
  export let width: number = 400;
  export let height: number = 240;
  export let margin = { top: 24, right: 64, bottom: 24, left: 48 } as const;

  let container: HTMLDivElement;

  $: if (container && data && data.length) {
    render();
  }

  function render() {
    d3.select(container).select('svg').remove();


    const years = Array.from(
      new Set(data.flatMap((s) => s.series.map((p) => p.year)))
    ).sort((a, b) => a - b);

    const partners = data.map((d) => d.partner);

    const x = d3
      .scalePoint<number>()
      .domain(years)
      .range([margin.left, width - margin.right])
      .padding(0.5);

    const maxRank = d3.max(data, (s) => d3.max(s.series, (p) => p.rank)) ?? 1;
    const y = d3
      .scaleLinear()
      .domain([1, maxRank])
      .range([margin.top, height - margin.bottom]);

    const color = d3.scaleOrdinal<string, string>(d3.schemeTableau10).domain(partners);

    const line = d3
      .line<{ year: number; rank: number }>()
      .x((d) => x(d.year)!)
      .y((d) => y(d.rank))
      .curve(d3.curveMonotoneX);

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Axes
    svg
      .append('g')
      .attr('transform', `translate(0,${margin.top})`)
      .call(d3.axisTop(x).tickFormat((d) => String(d)))
      .call((g) => g.selectAll('text').style('font-size', '12px'));

    svg
      .append('g')
      .attr('transform', `translate(${margin.left},0)`) 
      .call(d3.axisLeft(y).ticks(maxRank).tickFormat((d) => String(d)))
      .call((g) => g.selectAll('text').style('font-size', '12px'));

    // Series lines
    const series = svg
      .append('g')
      .attr('fill', 'none')
      .attr('stroke-width', 2);

    series
      .selectAll('path')
      .data(data)
      .join('path')
      .attr('stroke', (d) => color(d.partner))
      .attr('d', (d) => line(d.series));

    // End labels on the right
    svg
      .append('g')
      .selectAll('text')
      .data(data)
      .join('text')
      .attr('x', x(years[years.length - 1])! + 6)
      .attr('y', (d) => y(d.series[d.series.length - 1].rank))
      .attr('dy', '0.32em')
      .style('font-size', '12px')
      .text((d) => `${d.partner}`);

    // Points and tooltips
    const tooltip = d3
      .select(container)
      .append('div')
      .style('position', 'absolute')
      .style('background', 'rgba(0,0,0,0.8)')
      .style('color', '#fff')
      .style('padding', '6px 8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

    svg
      .append('g')
      .selectAll('g')
      .data(data)
      .join('g')
      .attr('fill', (d) => color(d.partner))
      .selectAll('circle')
      .data((d) => d.series.map((p) => ({ partner: d.partner, ...p })))
      .join('circle')
      .attr('cx', (d) => x(d.year)!)
      .attr('cy', (d) => y(d.rank))
      .attr('r', 3)
      .on('mouseover', function (event, d) {
        tooltip
          .style('opacity', 1)
          .html(
            `<div><strong>${d.partner}</strong></div>` +
              `<div>Year: ${d.year}</div>` +
              `<div>Rank: ${d.rank}</div>` +
              `<div>Exports: $${(d.value / 1e9).toFixed(1)}B</div>`
          );
      })
      .on('mousemove', function (event) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function () {
        tooltip.style('opacity', 0);
      });
  }
</script>

<div bind:this={container} style="position: relative;"></div>

<style>
  :global(svg text) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }
</style>


