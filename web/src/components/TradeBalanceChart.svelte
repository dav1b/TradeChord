<script lang="ts">
	import { afterUpdate } from 'svelte';
	import * as d3 from 'd3';

	export let data: { year: number; exports: number; imports: number; balance: number }[];
	export let width: number = 960;
	export let height: number = 400;
	export let margin = { top: 20, right: 30, bottom: 40, left: 60 } as const;

	let container: HTMLDivElement;

	afterUpdate(() => {
		if (data && container) {
			d3.select(container).select('svg').remove();
			drawChart();
		}
	});

	function drawChart() {
		if (!container || !data || data.length === 0) return;

		const widthLocal = width;
		const heightLocal = height;
		const marginLocal = margin;
		const innerWidth = widthLocal - marginLocal.left - marginLocal.right;
		const innerHeight = heightLocal - marginLocal.top - marginLocal.bottom;

		// Create scales
		const xScale = d3.scaleLinear()
			.domain(d3.extent(data, d => d.year) as [number, number])
			.range([0, innerWidth]);

		const yScale = d3.scaleLinear()
			.domain([0, d3.max(data, d => Math.max(d.exports, d.imports)) as number])
			.range([innerHeight, 0]);

		// Create line generators
		const line = d3.line<{ year: number; exports: number; imports: number; balance: number }>()
			.x(d => xScale(d.year))
			.y(d => yScale(d.value));

		// Create area generator for the colored region
		const area = d3.area<{ year: number; exports: number; imports: number; balance: number }>()
			.x(d => xScale(d.year))
			.y0(d => yScale(d.imports))
			.y1(d => yScale(d.exports));

		// Create SVG
		const svg = d3.select(container)
			.append('svg')
			.attr('width', widthLocal)
			.attr('height', heightLocal);

		const g = svg.append('g')
			.attr('transform', `translate(${marginLocal.left},${marginLocal.top})`);

		// Add colored areas based on trade balance
		const positiveData = data.filter(d => d.balance >= 0);
		const negativeData = data.filter(d => d.balance < 0);

		if (positiveData.length > 0) {
			g.append('path')
				.datum(positiveData)
				.attr('fill', 'rgba(0, 100, 255, 0.3)')
				.attr('d', area);
		}

		if (negativeData.length > 0) {
			g.append('path')
				.datum(negativeData)
				.attr('fill', 'rgba(255, 100, 100, 0.3)')
				.attr('d', area);
		}

		// Add export line
		g.append('path')
			.datum(data)
			.attr('fill', 'none')
			.attr('stroke', '#0066cc')
			.attr('stroke-width', 2)
			.attr('d', line.y(d => yScale(d.exports)));

		// Add import line
		g.append('path')
			.datum(data)
			.attr('fill', 'none')
			.attr('stroke', '#cc6600')
			.attr('stroke-width', 2)
			.attr('d', line.y(d => yScale(d.imports)));

		// Add axes
		g.append('g')
			.attr('transform', `translate(0,${innerHeight})`)
			.call(d3.axisBottom(xScale).tickFormat(d3.format('d')));

		g.append('g')
			.call(d3.axisLeft(yScale).tickFormat(d => `$${(Number(d) / 1e9).toFixed(0)}B`));

		// Add axis labels
		g.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - marginLocal.left)
			.attr('x', 0 - (innerHeight / 2))
			.attr('dy', '1em')
			.style('text-anchor', 'middle')
			.text('Trade Value ($B)');

		g.append('text')
			.attr('transform', `translate(${innerWidth / 2}, ${innerHeight + marginLocal.bottom - 5})`)
			.style('text-anchor', 'middle')
			.text('Year');

		// Add legend
		const legend = g.append('g')
			.attr('transform', `translate(${innerWidth - 150}, 20)`);

		legend.append('rect')
			.attr('width', 12)
			.attr('height', 12)
			.attr('fill', '#0066cc');

		legend.append('text')
			.attr('x', 20)
			.attr('y', 9)
			.text('Exports');

		legend.append('rect')
			.attr('y', 20)
			.attr('width', 12)
			.attr('height', 12)
			.attr('fill', '#cc6600');

		legend.append('text')
			.attr('x', 20)
			.attr('y', 29)
			.text('Imports');

		legend.append('rect')
			.attr('y', 40)
			.attr('width', 12)
			.attr('height', 12)
			.attr('fill', 'rgba(0, 100, 255, 0.3)');

		legend.append('text')
			.attr('x', 20)
			.attr('y', 49)
			.text('Trade Surplus');

		legend.append('rect')
			.attr('y', 60)
			.attr('width', 12)
			.attr('height', 12)
			.attr('fill', 'rgba(255, 100, 100, 0.3)');

		legend.append('text')
			.attr('x', 20)
			.attr('y', 69)
			.text('Trade Deficit');
	}
</script>

<div bind:this={container}></div>
