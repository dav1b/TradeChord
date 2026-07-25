<script lang="ts">
  import * as d3 from 'd3';

  export let data: { year: number; value: number }[] = [];
  export let width: number = 120;
  export let height: number = 28;
  export let color: string = '#374151';
  export let strokeWidth: number = 1.5;
  export let margin = { top: 4, right: 6, bottom: 4, left: 6 } as const;

  let container: HTMLDivElement;
  $: if (container && data && data.length) render();

  function render() {
    d3.select(container).select('svg').remove();
    if (!data || data.length < 2) return;

    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const sorted = data.slice().sort((a,b)=>a.year-b.year);
    const x = d3.scaleLinear().domain([sorted[0].year, sorted[sorted.length-1].year]).range([0, innerW]);
    const y = d3.scaleLinear().domain(d3.extent(sorted, d=>d.value) as [number,number]).nice().range([innerH, 0]);

    const svg = d3.select(container).append('svg').attr('width', width).attr('height', height);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const line = d3.line<{year:number;value:number}>()
      .x(d=>x(d.year)).y(d=>y(d.value)).curve(d3.curveMonotoneX);

    // faint baseline
    g.append('line').attr('x1',0).attr('x2',innerW).attr('y1',innerH).attr('y2',innerH)
      .attr('stroke','#E5E7EB').attr('stroke-width',1);

    g.append('path').datum(sorted).attr('d', line)
      .attr('fill','none').attr('stroke', color).attr('stroke-width', strokeWidth).attr('opacity', 0.9);
  }
</script>

<div bind:this={container}></div>
