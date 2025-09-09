<script lang="ts">
	import { afterUpdate } from 'svelte';
	import * as d3 from 'd3';

	export let data: { year: number; exports: number; imports: number; balance: number }[];
	export let reporter: string = '';
	export let width: number = 960;
	export let height: number = 400;
	export let margin = { top: 20, right: 30, bottom: 40, left: 20 };

	let container: HTMLDivElement;

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
		// No suffix
		return `$${abs.toFixed(abs < 10 ? 1 : 0)}`;
	}

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

		// Scales
		const years = data.map(d => d.year);
		const xScale = d3.scaleBand()
			.domain(years.map(String))
			.range([0, innerWidth])
			.padding(0.1);

		const maxAbsBalance = d3.max(data, d => Math.abs(d.balance)) as number;
		const yScale = d3.scaleLinear()
			.domain([-maxAbsBalance, maxAbsBalance])
			.range([innerHeight, 0]);

		// Root SVG
		const svg = d3.select(container)
			.append('svg')
			.attr('width', widthLocal)
			.attr('height', heightLocal);

		const g = svg.append('g')
			.attr('transform', `translate(${marginLocal.left},${marginLocal.top})`);

		// Colors from CSS variables
		const positiveColor = getComputedStyle(document.documentElement).getPropertyValue('--color-trade-positive').trim() || '#08605F';
		const negativeColor = getComputedStyle(document.documentElement).getPropertyValue('--color-trade-negative').trim() || '#931F1D';

		// Zero line
		const zeroY = yScale(0);
		g.append('line')
			.attr('x1', 0)
			.attr('x2', innerWidth)
			.attr('y1', zeroY)
			.attr('y2', zeroY)
			.attr('stroke', '#9CA3AF')
			.attr('stroke-width', 1)
			.attr('stroke-dasharray', '2,2');
		// Zero label at start, vertically centered on line
		g.append('text')
			.attr('x', 0-0.03*innerWidth)
			.attr('y', zeroY)
			.attr('dominant-baseline', 'middle')
			.attr('text-anchor', 'start')
			.attr('fill', '#6B7280')
			.attr('font-size', '10px')
			.text('0');

		// Minimal x-axis: only min and max year ticks (drawn later)
		const minYear = d3.min(years)!;
		const maxYear = d3.max(years)!;

		// Faint vertical lines at min/max years (draw BEFORE bars so they appear behind)
		[minYear, maxYear].forEach((yr) => {
			const x = (xScale(String(yr)) ?? 0) + xScale.bandwidth() / 2;
			g.append('line')
				.attr('x1', x)
				.attr('x2', x)
				.attr('y1', 0)
				.attr('y2', innerHeight)
				.attr('stroke', '#EEF2F7')
				.attr('stroke-width', 1);
		});

		// Tooltip (stats card)
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

		// Bars
		g.selectAll('.bar')
			.data(data)
			.enter()
			.append('rect')
			.attr('class', 'bar')
			.attr('x', d => xScale(String(d.year))!)
			.attr('width', xScale.bandwidth())
			.attr('y', d => d.balance >= 0 ? yScale(d.balance) : zeroY)
			.attr('height', d => Math.abs(yScale(d.balance) - zeroY))
			.attr('fill', d => d.balance >= 0 ? positiveColor : negativeColor)
			.attr('opacity', 0.9)
			.on('mouseover', function (event, d) {
				const html = `
					<div style=\"font-weight:700;margin-bottom:6px;\">${reporter ? reporter + ' — ' : ''}${d.year}</div>
					<div style=\"display:grid;grid-template-columns:auto auto;row-gap:4px;column-gap:10px;align-items:baseline;\">
						<div style=\"color:#6B7280;\">Exports</div><div style=\"color:${positiveColor};font-weight:700;\">${formatWithSuffix(d.exports)}</div>
						<div style=\"color:#6B7280;\">Imports</div><div style=\"color:${negativeColor};font-weight:700;\">${formatWithSuffix(d.imports)}</div>
						<div style=\"color:#6B7280;\">Balance</div><div style=\"color:${d.balance>=0?positiveColor:negativeColor};font-weight:800;\">${formatWithSuffix(d.balance)}</div>
					</div>`;
				tooltip.style('opacity', 1).html(html);
			})
			.on('mousemove', function (event) {
				tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY - 28 + 'px');
			})
			.on('mouseout', function () {
				tooltip.style('opacity', 0);
			});

		// Label only the max magnitude bar; avoid overlap with min/max year ticks by nudging
		const maxBar = data.reduce((a, b) => Math.abs(a.balance) >= Math.abs(b.balance) ? a : b);
		const maxXCenter = (xScale(String(maxBar.year)) ?? 0) + xScale.bandwidth() / 2;
		let maxY = maxBar.balance >= 0 ? yScale(maxBar.balance) - 6 : yScale(maxBar.balance) + 12;
		if (maxBar.year === minYear || maxBar.year === maxYear) {
			maxY += maxBar.balance >= 0 ? -6 : 6;
		}
		g.append('text')
			.attr('x', maxXCenter)
			.attr('y', maxY)
			.attr('text-anchor', 'middle')
			.attr('font-size', '11px')
			.attr('fill', '#374151')
			.text(formatWithSuffix(maxBar.balance));

		// Minimal x-axis: only min and max year ticks (no tick lines)
		const xAxis = d3.axisBottom(xScale).tickValues([String(minYear), String(maxYear)]).tickFormat(d => String(d));
		g.append('g')
			.attr('transform', `translate(0,${innerHeight})`)
			.call(xAxis)
			.call(g => g.selectAll('.domain, .tick line').remove())
			.call(g => g.selectAll('.tick text').style('font-size', '11px'));
	}
</script>

<div bind:this={container}></div>
