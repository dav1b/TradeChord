<script lang="ts">
	import { afterUpdate } from 'svelte';
	import * as d3 from 'd3';
	import type { SimpleChordData } from '$lib/utils/transform';

	export let data: SimpleChordData;

	let container: HTMLDivElement;

	afterUpdate(() => {
		if (data && container) {
			d3.select(container).select('svg').remove();
			d3.select(container).select('.tooltip').remove();
			drawChordDiagram();
		}
	});

	function drawChordDiagram() {
		if (!container || !data) return;

		const { matrix, countries, countryLabels } = data;

		const width = 960,
			height = width,
			margin = 150;
		const outerRadius = Math.min(width, height) / 2 - margin;
		const innerRadius = outerRadius;

		const chord = d3.chord().padAngle(0.05).sortSubgroups(d3.descending);
		const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
		const ribbon = d3.ribbon().radius(innerRadius);
		const color = d3.scaleOrdinal(d3.schemeCategory10).domain(countries);

		const chords = chord(matrix);
		
		const countryTotals = countries.map((_, i) => 
      		matrix[i].reduce((sum, val) => sum + val, 0)
    	);

		const svg = d3
			.select(container)
			.append('svg')
			.attr('width', width)
			.attr('height', height)
			.append('g')
			.attr('transform', `translate(${width / 2},${height / 2})`);

		const group = svg.append('g').selectAll('g').data(chords.groups).enter().append('g');

		group
			.append('path')
			.attr('d', arc as any)
			.style('fill', (d: any) => color(countries[d.index]))
			.style('stroke', '#000');

		group
			.append('text')
			.attr('dy', '.35em')
			.attr('transform', (d: any) => {
				const angle = ((d.startAngle + d.endAngle) / 2) * (180 / Math.PI) - 90;
				const rotate = angle > 90 ? angle + 180 : angle;
				return `rotate(${angle}) translate(${outerRadius + 20}) ${
					rotate > 90 ? 'rotate(180)' : ''
				}`;
			})
			.style('text-anchor', (d: any) => {
				const angle = ((d.startAngle + d.endAngle) / 2) * (180 / Math.PI);
				return angle > 90 && angle < 270 ? 'end' : 'start';
			})
			.text((d: any) => countryLabels[d.index]);

		const tooltipDiv = d3
			.select(container)
			.append('div')
			.attr('class', 'tooltip')
			.style('position', 'absolute')
			.style('background', 'rgba(0, 0, 0, 0.8)')
			.style('color', 'white')
			.style('padding', '8px')
			.style('border-radius', '4px')
			.style('font-size', '12px')
			.style('pointer-events', 'none')
			.style('opacity', 0);

		svg
			.append('g')
			.selectAll('path')
			.data(chords)
			.enter()
			.append('path')
			.attr('d', ribbon as any)
			.style('fill', (d: any) => color(countries[d.source.index]))
			.style('opacity', 0.7)
			.on('mouseover', function (event: any, d: any) {
				const sourceCountry = countries[d.source.index];
				const targetCountry = countries[d.target.index];
				const valueSP = d.source.value; // source -> partner
				const valuePS = matrix[d.target.index][d.source.index]; // partner -> source
				const tradeBalance = valueSP - valuePS; // reporter exports - partner exports
				const sourceTotal = countryTotals[d.source.index];
				const targetTotal = countryTotals[d.target.index];

				const spPct = sourceTotal > 0 ? ((valueSP / sourceTotal) * 100).toFixed(1) : '0.0';
				const psPct = targetTotal > 0 ? ((valuePS / targetTotal) * 100).toFixed(1) : '0.0';

				const tooltipContent = `
					<strong>${sourceCountry} ⇄ ${targetCountry}</strong><br/>
					${sourceCountry} → ${targetCountry}: $${(valueSP / 1e9).toFixed(2)}B (${spPct}%)<br/>
					${targetCountry} → ${sourceCountry}: $${(valuePS / 1e9).toFixed(2)}B (${psPct}%)<br/>
					Balance (reporter - partner): $${(tradeBalance / 1e9).toFixed(2)}B
				`;

				tooltipDiv
					.style('opacity', 1)
					.html(tooltipContent)
					.style('left', event.pageX + 10 + 'px')
					.style('top', event.pageY - 10 + 'px');
			})
			.on('mouseout', function () {
				tooltipDiv.style('opacity', 0);
			});
	}
</script>

<div bind:this={container}></div>