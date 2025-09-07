<script lang="ts">
	import { afterUpdate } from 'svelte';
	import * as d3 from 'd3';
	import { sankey as d3Sankey, sankeyLinkHorizontal as d3SankeyLinkHorizontal } from 'd3-sankey';
	import type { SankeyData } from '$lib/utils/transform';

	export let data: SankeyData;

	let container: HTMLDivElement;

	afterUpdate(() => {
		if (data && container) {
			d3.select(container).select('svg').remove();
			drawChart();
		}
	});

	function drawChart() {
		if (!container || !data || !data.nodes.length) return;

		const width = 960;
		const height = 600;

		const svg = d3
			.select(container)
			.append('svg')
			.attr('width', width)
			.attr('height', height)
			.attr('viewBox', [0, 0, width, height])
			.style('width', '100%')
			.style('height', 'auto');

		const sankey = d3Sankey()
			.nodeWidth(15)
			.nodePadding(10)
			.nodeSort(null)
			.extent([
				[1, 5],
				[width - 1, height - 5]
			]);

		const graph = sankey(data as any);

		const color = d3.scaleOrdinal(d3.schemeCategory10);

		svg
			.append('g')
			.attr('stroke', '#000')
			.selectAll('rect')
			.data(graph.nodes)
			.join('rect')
			.attr('x', (d: any) => d.x0)
			.attr('y', (d: any) => d.y0)
			.attr('height', (d: any) => d.y1 - d.y0)
			.attr('width', (d: any) => d.x1 - d.x0)
			.attr('fill', (d: any) => color(d.name.split(' ')[0]));

		svg
			.append('g')
			.attr('fill', 'none')
			.attr('stroke-opacity', 0.5)
			.selectAll('g')
			.data(graph.links)
			.join('path')
			.attr('d', d3SankeyLinkHorizontal())
			.attr('stroke', (d: any) => color(d.source.name.split(' ')[0]))
			.attr('stroke-width', (d: any) => Math.max(1, d.width));

		svg
			.append('g')
			.style('font', '10px sans-serif')
			.selectAll('text')
			.data(graph.nodes)
			.join('text')
			.attr('x', (d: any) => (d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6))
			.attr('y', (d: any) => (d.y1 + d.y0) / 2)
			.attr('dy', '0.35em')
			.attr('text-anchor', (d: any) => (d.x0 < width / 2 ? 'start' : 'end'))
			.text((d: any) => d.name.split(' ')[0]);
	}
</script>

<div bind:this={container}></div> 