<script context="module" lang="ts">
  // NOTE:
  // This generic slope chart is used for BOTH partner and product views.
  // Our data pipeline currently reuses the field name `partner` to store the
  // product identifier/name when building product slope data (to reuse types).
  // Therefore, when rendering product slopes, we purposely pass labelKey='partner'.
  // If/when the pipeline emits an explicit `product` property, we can switch
  // the call site back to labelKey='product' without changing this component.
  export type Datum = {
    s1: number; s2: number; b1: boolean; b2: boolean;
    v1?: number; v2?: number; total1?: number; total2?: number;
    [key: string]: any;
  };
</script>

<script lang="ts">
  import * as d3 from 'd3';

  export let data: Datum[] = [];
  export let year1: number;
  export let year2: number;
  export let width: number = 640;
  export let height: number = 420;
  export let margin = { top: 20, right: 100, bottom: 20, left: 100 } as const;
  export let reporter: string = '';
  export let mode: 'exports' | 'imports' = 'exports';

  // Configurable identity and behavior
  export let labelKey: 'partner' | 'product' = 'partner';
  export let isPartner: boolean = false; // enables ROW styling
  export let rowKey: string = 'ROW';
  export let showTopNLabels: number = 3;

  let container: HTMLDivElement;
  $: if (container && data) render();

  const posColor = getComputedStyle(document.documentElement).getPropertyValue('--color-trade-positive').trim() || '#08605F';
  const negColor = getComputedStyle(document.documentElement).getPropertyValue('--color-trade-negative').trim() || '#931F1D';
  const lineColor = '#D1D5DB';
  const guideColor = '#E5E7EB';

  function cleanLabel(txt: string): string {
    // Strip numeric prefix like "01-05_Animal" -> "Animal" when showing products
    return labelKey === 'product' ? txt.replace(/^\d+-\d+_/, '') : txt;
  }

  function formatWithSuffix(value: number): string {
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

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const maxShare = Math.max(0.001, d3.max(data, (d) => Math.max(d.s1 ?? 0, d.s2 ?? 0)) || 0.001);
    const y = d3.scaleLinear().domain([0, maxShare * 1.05]).range([innerHeight, 0]);
    const x = d3.scalePoint<number>().domain([year1, year2]).range([0, innerWidth]).padding(0.5);

    const svg = d3.select(container).append('svg').attr('width', width).attr('height', height);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const tooltip = d3.select(container).append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute').style('background', '#ffffff').style('color', '#111827')
      .style('border', '1px solid #E5E7EB').style('box-shadow', '0 4px 16px rgba(0,0,0,0.08)')
      .style('border-radius', '8px').style('padding', '10px 12px').style('font-size', '12px')
      .style('pointer-events', 'none').style('opacity', 0);

    // Year guides (no axis text)
    g.append('line').attr('x1', x(year1)!).attr('x2', x(year1)!).attr('y1', 0).attr('y2', innerHeight).attr('stroke', guideColor);
    g.append('line').attr('x1', x(year2)!).attr('x2', x(year2)!).attr('y1', 0).attr('y2', innerHeight).attr('stroke', guideColor);

    const groups = g.selectAll('g.row').data(data).enter().append('g').attr('class', 'row');

    // Lines
    groups.append('line')
      .attr('x1', x(year1)!).attr('x2', x(year2)!)
      .attr('y1', d => y(d.s1)).attr('y2', d => y(d.s2))
      .attr('stroke', d => (isPartner && d[labelKey] === rowKey) ? '#9CA3AF' : lineColor)
      .attr('stroke-width', 2)
      .attr('opacity', d => (isPartner && d[labelKey] === rowKey) ? 0.8 : 1)
      .attr('stroke-dasharray', d => (isPartner && d[labelKey] === rowKey) ? '4,2' : null);

    // Dots
    groups.append('circle')
      .attr('cx', x(year1)!).attr('cy', d => y(d.s1)).attr('r', 3)
      .attr('fill', d => (isPartner && d[labelKey] === rowKey) ? '#9CA3AF' : (d.b1 ? posColor : negColor))
      .attr('stroke', d => (isPartner && d[labelKey] === rowKey) ? '#6B7280' : 'none')
      .attr('stroke-width', d => (isPartner && d[labelKey] === rowKey) ? 1 : 0)
      .on('mouseover', function (event, d: Datum) {
        const total = d.total1 || 0; const value = d.v1 || 0;
        const raw = String(d[labelKey]); const lbl = cleanLabel(raw);
        const html = `
          <div style="font-weight:700;margin-bottom:6px;">${reporter ? reporter + ' — ' : ''}${lbl} (${year1})</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
            <div style="color:#6B7280;">${mode === 'exports' ? 'Exports' : 'Imports'} Share</div><div style="color:#374151;font-weight:700;">${(d.s1*100).toFixed(1)}%</div>
            <div style="color:#6B7280;">Value</div><div style="color:${d.b1 ? posColor : negColor};font-weight:700;">${formatWithSuffix(value)}</div>
            <div style="color:#6B7280;">Total ${mode === 'exports' ? 'Exports' : 'Imports'}</div><div style="color:#6B7280;font-weight:700;">${formatWithSuffix(total)}</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function (event) { tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px'); })
      .on('mouseout', function () { tooltip.style('opacity', 0); });

    groups.append('circle')
      .attr('cx', x(year2)!).attr('cy', d => y(d.s2)).attr('r', 3)
      .attr('fill', d => (isPartner && d[labelKey] === rowKey) ? '#9CA3AF' : (d.b2 ? posColor : negColor))
      .attr('stroke', d => (isPartner && d[labelKey] === rowKey) ? '#6B7280' : 'none')
      .attr('stroke-width', d => (isPartner && d[labelKey] === rowKey) ? 1 : 0)
      .on('mouseover', function (event, d: Datum) {
        const total = d.total2 || 0; const value = d.v2 || 0;
        const raw = String(d[labelKey]); const lbl = cleanLabel(raw);
        const html = `
          <div style="font-weight:700;margin-bottom:6px;">${reporter ? reporter + ' — ' : ''}${lbl} (${year2})</div>
          <div style="display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;">
            <div style="color:#6B7280;">${mode === 'exports' ? 'Exports' : 'Imports'} Share</div><div style="color:#374151;font-weight:700;">${(d.s2*100).toFixed(1)}%</div>
            <div style="color:#6B7280;">Value</div><div style="color:${d.b2 ? posColor : negColor};font-weight:700;">${formatWithSuffix(value)}</div>
            <div style="color:#6B7280;">Total ${mode === 'exports' ? 'Exports' : 'Imports'}</div><div style="color:#6B7280;font-weight:700;">${formatWithSuffix(total)}</div>
          </div>`;
        tooltip.style('opacity', 1).html(html);
      })
      .on('mousemove', function (event) { tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px'); })
      .on('mouseout', function () { tooltip.style('opacity', 0); });

    // Label selection: only top N by s2 (ignore ROW when partner)
    const ranked = data
      .filter(d => !(isPartner && d[labelKey] === rowKey))
      .slice()
      .sort((a, b) => (b.s2 ?? 0) - (a.s2 ?? 0));
    const topSet = new Set(ranked.slice(0, showTopNLabels).map(d => String(d[labelKey])));

    // We'll also do a simple collision-avoid pass to reduce label overlap like the partner view
    const leftPlaced: Array<{ y: number; sel: d3.Selection<SVGTextElement, Datum, any, any> }> = [];
    const rightPlaced: Array<{ y: number; sel: d3.Selection<SVGTextElement, Datum, any, any> }> = [];
    const labelPadding = 12;

    groups.each(function(d: Datum) {
      const key = String(d[labelKey]); if (!topSet.has(key)) return;
      const sel = d3.select(this).append('text')
        .attr('x', x(year1)! - 8).attr('y', y(d.s1))
        .attr('dominant-baseline', 'middle').attr('text-anchor', 'end')
        .style('font-size', '11px')
        .text(`${cleanLabel(key)} ${(d.s1*100).toFixed(1)}%`) as d3.Selection<SVGTextElement, Datum, any, any>;
      leftPlaced.push({ y: y(d.s1), sel });
    });

    groups.each(function(d: Datum) {
      const key = String(d[labelKey]); if (!topSet.has(key)) return;
      const sel = d3.select(this).append('text')
        .attr('x', x(year2)! + 8).attr('y', y(d.s2))
        .attr('dominant-baseline', 'middle').attr('text-anchor', 'start')
        .style('font-size', '11px')
        .text(`${(d.s2*100).toFixed(1)}%`) as d3.Selection<SVGTextElement, Datum, any, any>;
      rightPlaced.push({ y: y(d.s2), sel });
    });

    function hideOverlaps(items: Array<{ y: number; sel: d3.Selection<SVGTextElement, Datum, any, any> }>) {
      items.sort((a, b) => a.y - b.y);
      for (let i = 1; i < items.length; i++) {
        const prev = items[i - 1];
        const curr = items[i];
        if (Math.abs(curr.y - prev.y) < labelPadding) {
          curr.sel.style('opacity', 0);
        }
      }
    }
    hideOverlaps(leftPlaced);
    hideOverlaps(rightPlaced);
  }
</script>

<div bind:this={container}></div>

<style>
  :global(.tooltip) { font-family: var(--font-family, 'Inter', sans-serif); }
  :global(svg text) { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif; }
</style>
