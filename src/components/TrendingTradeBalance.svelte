<script lang="ts">
	import { afterUpdate } from 'svelte';
	import * as d3 from 'd3';

	export let data: { year: number; exports: number; imports: number; balance: number }[];
	export let width: number = 960;
	export let height: number = 400;
	export let margin = { top: 20, right: 30, bottom: 40, left: 60 };

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
		const xScale = d3.scaleBand()
			.domain(data.map(d => d.year.toString()))
			.range([0, innerWidth])
			.padding(0.1);

		const maxAbsBalance = d3.max(data, d => Math.abs(d.balance)) as number;
		const yScale = d3.scaleLinear()
			.domain([-maxAbsBalance, maxAbsBalance])
			.range([innerHeight, 0]);

		// Create SVG
		const svg = d3.select(container)
			.append('svg')
			.attr('width', widthLocal)
			.attr('height', heightLocal);

		const g = svg.append('g')
			.attr('transform', `translate(${marginLocal.left},${marginLocal.top})`);

		// Add zero line
		const zeroY = yScale(0);
		g.append('line')
			.attr('x1', 0)
			.attr('x2', innerWidth)
			.attr('y1', zeroY)
			.attr('y2', zeroY)
			.attr('stroke', '#666')
			.attr('stroke-width', 1)
			.attr('stroke-dasharray', '2,2');

		// Add bars
		const bars = g.selectAll('.bar')
			.data(data)
			.enter()
			.append('g')
			.attr('class', 'bar')
			.attr('transform', d => `translate(${xScale(d.year.toString())}, 0)`);

		// Draw bars
		bars.each(function(d) {
			const barGroup = d3.select(this);
			const barWidth = xScale.bandwidth();
			const barHeight = Math.abs(yScale(d.balance) - zeroY);
			const barY = d.balance >= 0 ? zeroY - barHeight : zeroY;
			
			// Bar rectangle
			barGroup.append('rect')
				.attr('x', 0)
				.attr('y', barY)
				.attr('width', barWidth)
				.attr('height', barHeight)
				.attr('fill', d.balance >= 0 ? '#22c55e' : '#ef4444')
				.attr('opacity', 0.8);

			// Arrow head for positive values (pointing up)
			if (d.balance > 0) {
				const arrowSize = Math.min(barWidth * 0.3, 8);
				const arrowPath = `M ${barWidth/2 - arrowSize/2} ${barY} L ${barWidth/2} ${barY - arrowSize} L ${barWidth/2 + arrowSize/2} ${barY} Z`;
				barGroup.append('path')
					.attr('d', arrowPath)
					.attr('fill', '#22c55e');
			}
			
			// Arrow head for negative values (pointing down)
			if (d.balance < 0) {
				const arrowSize = Math.min(barWidth * 0.3, 8);
				const arrowPath = `M ${barWidth/2 - arrowSize/2} ${barY + barHeight} L ${barWidth/2} ${barY + barHeight + arrowSize} L ${barWidth/2 + arrowSize/2} ${barY + barHeight} Z`;
				barGroup.append('path')
					.attr('d', arrowPath)
					.attr('fill', '#ef4444');
			}

			// Value labels for significant values
			if (Math.abs(d.balance) > maxAbsBalance * 0.1) {
				const labelY = d.balance >= 0 ? barY - 5 : barY + barHeight + 15;
				barGroup.append('text')
					.attr('x', barWidth / 2)
					.attr('y', labelY)
					.attr('text-anchor', 'middle')
					.attr('font-size', '10px')
					.attr('fill', '#374151')
					.text(`$${(Math.abs(d.balance) / 1e9).toFixed(1)}B`);
			}
		});

		// Add axes
		g.append('g')
			.attr('transform', `translate(0,${innerHeight})`)
			.call(d3.axisBottom(xScale).tickFormat(d => d));

		g.append('g')
			.attr('transform', `translate(0,0)`)
			.call(d3.axisLeft(yScale).tickFormat(d => `$${(Number(d) / 1e9).toFixed(0)}B`));

		// Add axis labels
		g.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - marginLocal.left)
			.attr('x', 0 - (innerHeight / 2))
			.attr('dy', '1em')
			.style('text-anchor', 'middle')
			.style('font-size', '12px')
			.text('Trade Balance ($B)');

		g.append('text')
			.attr('transform', `translate(${innerWidth / 2}, ${innerHeight + marginLocal.bottom - 5})`)
			.style('text-anchor', 'middle')
			.style('font-size', '12px')
			.text('Year');

		// Add legend
		const legend = g.append('g')
			.attr('transform', `translate(${innerWidth - 120}, 20)`);

		// Positive balance legend
		legend.append('rect')
			.attr('width', 12)
			.attr('height', 12)
			.attr('fill', '#22c55e')
			.attr('opacity', 0.8);

		legend.append('text')
			.attr('x', 20)
			.attr('y', 9)
			.attr('font-size', '11px')
			.text('Trade Surplus');

		// Negative balance legend
		legend.append('rect')
			.attr('y', 20)
			.attr('width', 12)
			.attr('height', 12)
			.attr('fill', '#ef4444')
			.attr('opacity', 0.8);

		legend.append('text')
			.attr('x', 20)
			.attr('y', 29)
			.attr('font-size', '11px')
			.text('Trade Deficit');
	}
</script>

<div bind:this={container}></div>
