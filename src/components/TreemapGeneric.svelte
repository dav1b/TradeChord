<script context="module" lang="ts">
  export type TrendPoint = { year: number; value: number; growth?: number };
  export type Item = {
    id: string;
    name: string;
    value: number;
    share?: number;
    trendData?: TrendPoint[];
    latestBalance?: number; // used for border/label color (+/-)
  };
</script>

<script lang="ts">
  import * as d3 from 'd3';

  export let data: Item[] = [];
  export let width: number = 420;
  export let height: number = 520;
  export let margin = { top: 20, right: 20, bottom: 20, left: 20 };

  // Callbacks to customize tooltip content and click behavior
  export let buildTooltip: (d: Item) => string = (d) => `
    <div style="font-weight:700;margin-bottom:6px;">${d.name}</div>
    <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
      <div style="color:#6B7280;">Value</div><div style="color:#374151;font-weight:700;">${formatValue(d.value)}</div>
      ${d.share != null ? `<div style='color:#6B7280;'>Share</div><div style='color:#374151;font-weight:700;'>${(d.share*100).toFixed(1)}%</div>`: ''}
    </div>`;
  export let onCellClick: (d: Item) => void = () => {};
  export let renderMiniChart: (g: d3.Selection<SVGGElement, any, any, any>, item: Item, cellWidth: number, cellHeight: number) => void = () => {};

  const colors = { positive: '#08605F', negative: '#931F1D' };

  let container: HTMLDivElement;
  $: if (container && data) render();

  function formatValue(value: number): string {
    const abs = Math.abs(value);
    const units = [ { v: 1e12, s: 'T' }, { v: 1e9, s: 'B' }, { v: 1e6, s: 'M' }, { v: 1e3, s: 'K' } ];
    for (const u of units) {
      if (abs >= u.v) {
        const n = abs / u.v; const str = n < 10 ? n.toFixed(1) : Math.round(n).toString();
        return `$${str}${u.s}`;
      }
    }
    return `$${abs.toFixed(abs < 10 ? 1 : 0)}`;
  }

  function render() {
    d3.select(container).select('svg').remove();
    d3.select(container).select('.tooltip').remove();
    if (!data || data.length === 0) return;

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(container).append('svg').attr('width', width).attr('height', height);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const tooltip = d3.select(container).append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute').style('background', '#ffffff').style('color', '#111827')
      .style('border', '1px solid #E5E7EB').style('box-shadow', '0 4px 16px rgba(0,0,0,0.08)')
      .style('border-radius', '8px').style('padding', '10px 12px').style('font-size', '12px')
      .style('pointer-events', 'none').style('opacity', 0);

    const treemap = d3.treemap<Item>().size([innerWidth, innerHeight]).padding(2).round(true);

    const root = d3.hierarchy({ children: data } as any)
      .sum((d: any) => d.value)
      .sort((a: any, b: any) => (b.value || 0) - (a.value || 0));

    treemap(root);

    const cells = g.selectAll('.cell')
      .data(root.leaves())
      .enter().append('g')
      .attr('class', 'cell')
      .attr('transform', (d: any) => `translate(${d.x0},${d.y0})`);

    // White outer separator
    cells.append('rect')
      .attr('x', -1).attr('y', -1)
      .attr('width', (d: any) => d.x1 - d.x0 + 2)
      .attr('height', (d: any) => d.y1 - d.y0 + 2)
      .attr('fill', 'none').attr('stroke', '#ffffff').attr('stroke-width', 2);

    // Inner cell
    cells.append('rect')
      .attr('x', 4).attr('y', 4)
      .attr('width', (d: any) => d.x1 - d.x0 - 8)
      .attr('height', (d: any) => d.y1 - d.y0 - 8)
      .attr('fill', '#E5E7EB').attr('opacity', 0.8)
      .attr('stroke', (d: any) => (d.data.latestBalance ?? 0) >= 0 ? colors.positive : colors.negative)
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d: any) { tooltip.style('opacity', 1).html(buildTooltip(d.data)); })
      .on('mousemove', function(event) { tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px'); })
      .on('mouseout', function(){ tooltip.style('opacity', 0); })
      .on('click', function(event, d: any){ onCellClick(d.data); });

    // Labels + mini chart
    cells.each(function(d: any){
      const cell = d3.select(this);
      const cellWidth = d.x1 - d.x0; const cellHeight = d.y1 - d.y0;
      if (cellWidth <= 60 || cellHeight <= 30) return;

      const labelColor = (d.data.latestBalance ?? 0) >= 0 ? colors.positive : colors.negative;
      const availableWidth = cellWidth - 16; const availableHeight = cellHeight - 16;

      const tempSvg = d3.select('body').append('svg').style('visibility', 'hidden');
      const nameText = tempSvg.append('text').attr('font-size', '12px').attr('font-weight', '600').text(d.data.name);
      const nameNode = nameText.node(); const nameW = nameNode ? nameNode.getBBox().width : 0; const nameH = nameNode ? nameNode.getBBox().height : 0;
      const valueTextStr = `${formatValue(d.data.value)}${d.data.share != null ? ` (${(d.data.share*100).toFixed(1)}%)` : ''}`;
      const valText = tempSvg.append('text').attr('font-size', '10px').text(valueTextStr);
      const valNode = valText.node(); const valW = valNode ? valNode.getBBox().width : 0; const valH = valNode ? valNode.getBBox().height : 0;
      tempSvg.remove();

      const totalH = nameH + valH + 4; const maxW = Math.max(nameW, valW);
      if (maxW > availableWidth || totalH > availableHeight) return;

      cell.append('text')
        .attr('x', 8).attr('y', 18)
        .attr('font-size', '12px').attr('font-weight', '600')
        .attr('fill', labelColor).text(d.data.name);
      cell.append('text')
        .attr('x', 8).attr('y', 32)
        .attr('font-size', '10px').attr('fill', labelColor).attr('opacity', 0.9)
        .text(valueTextStr);

      if (cellHeight > 70 && d.data.trendData && d.data.trendData.length > 1) {
        const miniGroup = cell.append('g').attr('transform', 'translate(8,50)');
        renderMiniChart(miniGroup as any, d.data, availableWidth, availableHeight);
      }
    });
  }
</script>

<div bind:this={container}></div>

<style>
  :global(.tooltip){ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif; }
  :global(svg text){ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif; }
</style>
