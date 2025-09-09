<script lang="ts">
  import * as d3 from 'd3';

  export let data: { partner: string; s1: number; s2: number; b1: boolean; b2: boolean; v1?: number; v2?: number; total1?: number; total2?: number }[] = [];
  export let year1: number;
  export let year2: number;
  export let width: number = 640;
  export let height: number = 420;
  export let margin = { top: 20, right: 120, bottom: 20, left: 120 } as const;
  export let reporter: string = '';
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

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

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

    // Axes labels for years (top)
    g.append('text')
      .attr('x', x(year1)!)
      .attr('y', -6)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text(year1);
    g.append('text')
      .attr('x', x(year2)!)
      .attr('y', -6)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text(year2);

    // Lines
    // vertical guides for years
    g.append('line').attr('x1', x(year1)!).attr('x2', x(year1)!).attr('y1', 0).attr('y2', innerHeight).attr('stroke', guideColor);
    g.append('line').attr('x1', x(year2)!).attr('x2', x(year2)!).attr('y1', 0).attr('y2', innerHeight).attr('stroke', guideColor);

    const groups = g.selectAll('g.row').data(data).enter().append('g').attr('class', 'row');

    groups.append('line')
      .attr('x1', x(year1)!)
      .attr('x2', x(year2)!)
      .attr('y1', d => y(d.s1))
      .attr('y2', d => y(d.s2))
      .attr('stroke', d => d.partner === 'ROW' ? '#9CA3AF' : lineColor)
      .attr('stroke-width', d => d.partner === 'ROW' ? 3 : 2)
      .attr('opacity', d => d.partner === 'ROW' ? 0.8 : 1)
      .attr('stroke-dasharray', d => d.partner === 'ROW' ? '4,2' : null);

    // Dots with tooltips
    groups.append('circle')
      .attr('cx', x(year1)!)
      .attr('cy', d => y(d.s1))
      .attr('r', d => d.partner === 'ROW' ? 4 : 3)
      .attr('fill', d => d.partner === 'ROW' ? '#9CA3AF' : (d.b1 ? posColor : negColor))
      .attr('stroke', d => d.partner === 'ROW' ? '#6B7280' : 'none')
      .attr('stroke-width', d => d.partner === 'ROW' ? 1 : 0)
      .on('mouseover', function (event, d) {
        const total = d.total1 || 0;
        const value = d.v1 || 0;
        const html = `
          <div style="font-weight:700;margin-bottom:6px;">${reporter ? reporter + ' — ' : ''}${d.partner} (${year1})</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
            <div style="color:#6B7280;">${mode === 'exports' ? 'Exports' : 'Imports'} Share</div><div style="color:#374151;font-weight:700;">${(d.s1*100).toFixed(1)}%</div>
            <div style="color:#6B7280;">Value</div><div style="color:${d.b1 ? posColor : negColor};font-weight:700;">${formatWithSuffix(value)}</div>
            <div style="color:#6B7280;">Total ${mode === 'exports' ? 'Exports' : 'Imports'}</div><div style="color:#6B7280;font-weight:700;">${formatWithSuffix(total)}</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function (event) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function () {
        tooltip.style('opacity', 0);
      });

    groups.append('circle')
      .attr('cx', x(year2)!)
      .attr('cy', d => y(d.s2))
      .attr('r', d => d.partner === 'ROW' ? 4 : 3)
      .attr('fill', d => d.partner === 'ROW' ? '#9CA3AF' : (d.b2 ? posColor : negColor))
      .attr('stroke', d => d.partner === 'ROW' ? '#6B7280' : 'none')
      .attr('stroke-width', d => d.partner === 'ROW' ? 1 : 0)
      .on('mouseover', function (event, d) {
        const total = d.total2 || 0;
        const value = d.v2 || 0;
        const html = `
          <div style="font-weight:700;margin-bottom:6px;">${reporter ? reporter + ' — ' : ''}${d.partner} (${year2})</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
            <div style="color:#6B7280;">${mode === 'exports' ? 'Exports' : 'Imports'} Share</div><div style="color:#374151;font-weight:700;">${(d.s2*100).toFixed(1)}%</div>
            <div style="color:#6B7280;">Value</div><div style="color:${d.b2 ? posColor : negColor};font-weight:700;">${formatWithSuffix(value)}</div>
            <div style="color:#6B7280;">Total ${mode === 'exports' ? 'Exports' : 'Imports'}</div><div style="color:#6B7280;font-weight:700;">${formatWithSuffix(total)}</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function (event) {
        tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
      })
      .on('mouseout', function () {
        tooltip.style('opacity', 0);
      });

    // Labels with collision detection
    const labelPadding = 12; // Minimum vertical spacing between labels
    const leftLabels: Array<{ y: number; text: any; isRow: boolean }> = [];
    const rightLabels: Array<{ y: number; text: any; isRow: boolean }> = [];

    // Left side labels
    groups.each(function(d) {
      const yPos = y(d.s1);
      const isRow = d.partner === 'ROW';
      const text = d3.select(this).append('text')
        .attr('x', x(year1)! - 8)
        .attr('y', yPos)
        .attr('dominant-baseline', 'middle')
        .attr('text-anchor', 'end')
        .style('font-size', '11px')
        .style('font-weight', isRow ? 'bold' : 'normal')
        .style('opacity', isRow ? 0.8 : 1)
        .text(`${d.partner} ${(d.s1*100).toFixed(1)}%`);
      
      leftLabels.push({ y: yPos, text, isRow });
    });

    // Right side labels
    groups.each(function(d) {
      const yPos = y(d.s2);
      const isRow = d.partner === 'ROW';
      const text = d3.select(this).append('text')
        .attr('x', x(year2)! + 8)
        .attr('y', yPos)
        .attr('dominant-baseline', 'middle')
        .attr('text-anchor', 'start')
        .style('font-size', '11px')
        .style('font-weight', isRow ? 'bold' : 'normal')
        .style('opacity', isRow ? 0.8 : 1)
        .text(`${(d.s2*100).toFixed(1)}%`);
      
      rightLabels.push({ y: yPos, text, isRow });
    });

    // Collision detection and hiding overlapping labels (but always show ROW)
    function hideOverlappingLabels(labels: Array<{ y: number; text: any; isRow: boolean }>) {
      labels.sort((a, b) => a.y - b.y);
      
      for (let i = 1; i < labels.length; i++) {
        const prev = labels[i - 1];
        const curr = labels[i];
        
        // Always show ROW labels, only hide non-ROW labels that overlap
        if (!curr.isRow && Math.abs(curr.y - prev.y) < labelPadding) {
          curr.text.style('opacity', 0);
        }
      }
    }

    hideOverlappingLabels(leftLabels);
    hideOverlappingLabels(rightLabels);
  }
</script>

<div bind:this={container}></div>

<style>
  :global(svg text) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  }
</style>


