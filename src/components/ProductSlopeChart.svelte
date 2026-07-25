<script lang="ts">
  import * as d3 from 'd3';

  export let data: { product: string; s1: number; s2: number; b1: boolean; b2: boolean; v1?: number; v2?: number; total1?: number; total2?: number }[] = [];
  export let year1: number;
  export let year2: number;
  export let width: number = 640;
  export let height: number = 420;
  // Bring axes a little closer together than before
  export let margin = { top: 20, right: 100, bottom: 20, left: 100 } as const;
  export let reporter: string = ''; // Used for tooltip display
  export let mode: 'exports' | 'imports' = 'exports';

  let container: HTMLDivElement;

  $: if (container && data) render();

  const posColor = getComputedStyle(document.documentElement).getPropertyValue('--color-trade-positive').trim() || '#08605F';
  const negColor = getComputedStyle(document.documentElement).getPropertyValue('--color-trade-negative').trim() || '#931F1D';
  const lineColor = '#D1D5DB';
  const guideColor = '#E5E7EB';

  // Format with dynamic suffix, decimals only when < 10 units of suffix
  function formatWithSuffix(value: number): string {
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

  function render() {
    d3.select(container).select('svg').remove();
    d3.select(container).select('.tooltip').remove();

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const maxShare = Math.max(0.001, d3.max(data, (d) => Math.max(d.s1 ?? 0, d.s2 ?? 0)) || 0.001);
    const y = d3.scaleLinear()
      .domain([0, maxShare * 1.05])
      .range([innerHeight, 0]);

    const x = d3.scalePoint<number>()
      .domain([year1, year2])
      .range([0, innerWidth])
      .padding(0.5);

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Tooltip (keep consistent with partner)
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

    // Vertical guides for years (no axis labels)
    g.append('line').attr('x1', x(year1)!).attr('x2', x(year1)!).attr('y1', 0).attr('y2', innerHeight).attr('stroke', guideColor);
    g.append('line').attr('x1', x(year2)!).attr('x2', x(year2)!).attr('y1', 0).attr('y2', innerHeight).attr('stroke', guideColor);

    // Lines: grey for all products
    const groups = g.selectAll('g.row').data(data).enter().append('g').attr('class', 'row');

    groups.append('line')
      .attr('x1', x(year1)!)
      .attr('x2', x(year2)!)
      .attr('y1', (d) => y(d.s1))
      .attr('y2', (d) => y(d.s2))
      .attr('stroke', lineColor)
      .attr('stroke-width', 2)
      .attr('opacity', 1);

    // Dots at start and end (small, colored by balance sign)
    groups.append('circle')
      .attr('cx', x(year1)!)
      .attr('cy', (d) => y(d.s1))
      .attr('r', 3)
      .attr('fill', (d) => d.b1 ? posColor : negColor);

    groups.append('circle')
      .attr('cx', x(year2)!)
      .attr('cy', (d) => y(d.s2))
      .attr('r', 3)
      .attr('fill', (d) => d.b2 ? posColor : negColor);

    // Top-3 labels only (by share in year2)
    const topThree = new Set(
      data
        .slice()
        .sort((a, b) => (b.s2 ?? 0) - (a.s2 ?? 0))
        .slice(0, 3)
        .map(d => d.product)
    );

    // Left labels with product name and share
    groups.each(function(d) {
      if (!topThree.has(d.product)) return;
      const text = d3.select(this).append('text')
        .attr('x', x(year1)! - 8)
        .attr('y', y(d.s1))
        .attr('dominant-baseline', 'middle')
        .attr('text-anchor', 'end')
        .style('font-size', '11px')
        .text(`${d.product.replace(/^\d+-\d+_/, '')} ${(d.s1*100).toFixed(1)}%`);
    });

    // Right labels with share only
    groups.each(function(d) {
      if (!topThree.has(d.product)) return;
      d3.select(this).append('text')
        .attr('x', x(year2)! + 8)
        .attr('y', y(d.s2))
        .attr('dominant-baseline', 'middle')
        .attr('text-anchor', 'start')
        .style('font-size', '11px')
        .text(`${(d.s2*100).toFixed(1)}%`);
    });

    // Tooltips on circles
    function showTooltip(event: any, d: any, yr: number, share: number, value?: number, total?: number, isPos?: boolean) {
      const html = `
        <div style="font-weight:700;margin-bottom:6px;">${reporter ? reporter + ' — ' : ''}${d.product.replace(/^\d+-\d+_/, '')} (${yr})</div>
        <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
          <div style="color:#6B7280;">${mode === 'exports' ? 'Exports' : 'Imports'} Share</div><div style="color:#374151;font-weight:700;">${(share*100).toFixed(1)}%</div>
          ${value != null ? `<div style='color:#6B7280;'>Value</div><div style='color:${isPos ? posColor : negColor};font-weight:700;'>${formatWithSuffix(value)}</div>` : ''}
          ${total != null ? `<div style='color:#6B7280;'>Total ${mode === 'exports' ? 'Exports' : 'Imports'}</div><div style='color:#6B7280;font-weight:700;'>${formatWithSuffix(total)}</div>` : ''}
        </div>`;
      tooltip.style('opacity', 1).html(html);
    }

    type Datum = { product: string; s1: number; s2: number; b1: boolean; b2: boolean; v1?: number; v2?: number; total1?: number; total2?: number };

    const circles = (groups as unknown as d3.Selection<SVGGElement, Datum, SVGGElement, unknown>)
      .selectAll<SVGCircleElement, Datum>('circle');

    circles
      .on('mouseover', function(event: any, d: Datum) {
        const isStart = d3.select(this).attr('cx') === String(x(year1)!);
        if (isStart) {
          showTooltip(event, d, year1, d.s1, d.v1, d.total1, d.b1);
        } else {
          showTooltip(event, d, year2, d.s2, d.v2, d.total2, d.b2);
        }
      })
      .on('mousemove', function(event: any) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function() { tooltip.style('opacity', 0); });
  }
</script>

<div bind:this={container}></div>

<style>
  :global(.tooltip) {
    font-family: var(--font-family, 'Inter', sans-serif);
  }
  :global(svg text) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }
</style>
