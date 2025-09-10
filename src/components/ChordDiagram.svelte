<script lang="ts">
	import { afterUpdate } from 'svelte';
	import * as d3 from 'd3';
	import type { SimpleChordData } from '$lib/utils/transform';

	export let data: SimpleChordData;

	// Configuration types and defaults
	type ChordConfig = {
		width: number;
		height: number;
		margin: number;
		arcStroke: string;
		arcStrokeWidth: number;
		rimInnerOffset: number;
		rimOuterOffset: number;
		rimStroke: string;
		rimStrokeWidth: number;
		ribbonStroke: string;
		ribbonStrokeWidth: number;
		ribbonOpacity: number;
		positiveBalanceColor: string;
		negativeBalanceColor: string;
		padAngle: number;
		labelOffset: number;
		labelFontSize: number;
		tooltipPadding: string;
		tooltipBorderRadius: string;
		tooltipFontSize: string;
		showLabels: boolean;
		showTooltip: boolean;
	};

	const defaultConfig: ChordConfig = {
		// Chart dimensions
		width: 800,
		height: 800,
		margin: 150,
		
		// Arc styling
		arcStroke: '#ffffff',
		arcStrokeWidth: 1,
		
		// Rim styling
		rimInnerOffset: 2,
		rimOuterOffset: 18,
		rimStroke: '#000',
		rimStrokeWidth: 1,
		
		// Ribbon styling
		ribbonStroke: '#ffffff',
		ribbonStrokeWidth: 1,
		ribbonOpacity: 0.7,
		
		// Trade balance colors
		positiveBalanceColor: '#08605F',
		negativeBalanceColor: '#931F1D',
		
		// Chord layout
		padAngle: 0.01,
		
		// Label styling
		labelOffset: 20,
		labelFontSize: 12,
		
		// Tooltip styling
		tooltipPadding: '8px',
		tooltipBorderRadius: '4px',
		tooltipFontSize: '12px',
		
		// Toggles
		showLabels: true,
		showTooltip: true
	};

	export let configOverride: Partial<ChordConfig> = {};
	const config: ChordConfig = { ...defaultConfig, ...configOverride } as ChordConfig;

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
		const width = config.width;
		const height = config.height;
		const margin = config.margin;
		const outerRadius = Math.min(width, height) / 2 - margin;
		const innerRadius = outerRadius;

		const chord = d3.chord().padAngle(config.padAngle);
		const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
		const rimArc = d3.arc().innerRadius(outerRadius + config.rimInnerOffset).outerRadius(outerRadius + config.rimOuterOffset);
		const ribbon = d3.ribbon().radius(innerRadius);
		const color = d3.scaleOrdinal(d3.schemeCategory10).domain(countries);

		const chords = chord(matrix);
		
		const countryTotals = countries.map((_, i) => 
     		matrix[i].reduce((sum, val) => sum + val, 0)
    	);

		// Calculate trade balance for each country (exports - imports)
		const tradeBalances = countries.map((_, i) => {
			const exports = matrix[i].reduce((sum, val) => sum + val, 0);
			const imports = matrix.reduce((sum, row) => sum + (row[i] || 0), 0);
			return exports - imports;
		});

		// Function to get trade balance color
		const getTradeBalanceColor = (balance: number) => {
			return balance >= 0 ? config.positiveBalanceColor : config.negativeBalanceColor;
		};

		const svg = d3
			.select(container)
			.append('svg')
			.attr('width', width)
			.attr('height', height)
			.append('g')
			.attr('transform', `translate(${width / 2},${height / 2})`);

		// Find the reporter's angle and rotate to make it horizontal
		const reporterIndex = 0; // Reporter is always first
		const reporterAngle = (chords.groups[reporterIndex].startAngle + chords.groups[reporterIndex].endAngle) / 2;
		const rotationAngle = -reporterAngle + Math.PI / 2; // Rotate to make reporter horizontal (top)

		const group = svg.append('g')
			.attr('transform', `rotate(${rotationAngle * 180 / Math.PI})`)
			.selectAll('g')
			.data(chords.groups)
			.enter()
			.append('g');

		group
			.append('path')
			.attr('d', arc as any)
			.style('fill', (d: any) => color(countries[d.index]))
			.style('stroke', config.arcStroke)
			.style('stroke-width', config.arcStrokeWidth);

		// Add rim around the chord diagram
		group
			.append('path')
			.attr('d', rimArc as any)
			.style('fill', (d: any) => getTradeBalanceColor(tradeBalances[d.index]))
			.style('stroke', config.rimStroke)
			.style('stroke-width', config.rimStrokeWidth);


		if (config.showLabels) {
			// Labels always outside the slices
			group
				.append('text')
				.attr('dy', '.35em')
				.attr('transform', (d: any) => {
					const angle = ((d.startAngle + d.endAngle) / 2) * (180 / Math.PI) - 90;
					const rotate = angle > 90 ? angle + 180 : angle;
					return `rotate(${angle}) translate(${outerRadius + config.labelOffset + 20}) ${
						rotate > 90 ? 'rotate(180)' : ''
					}`;
				})
				.style('text-anchor', (d: any) => {
					const angle = ((d.startAngle + d.endAngle) / 2) * (180 / Math.PI);
					return angle > 90 && angle < 270 ? 'end' : 'start';
				})
				.text((d: any) => countryLabels[d.index]);
		}

		const tooltipDiv = d3
			.select(container)
			.append('div')
			.attr('class', 'tooltip')
			.style('position', 'absolute')
			.style('background', '#ffffff')
			.style('color', '#111827')
			.style('border', '1px solid #E5E7EB')
			.style('box-shadow', '0 4px 16px rgba(0,0,0,0.08)')
			.style('border-radius', '8px')
			.style('padding', '12px 16px')
			.style('font-size', '12px')
			.style('pointer-events', 'none')
			.style('opacity', 0);

		svg
			.append('g')
			.attr('transform', `rotate(${rotationAngle * 180 / Math.PI})`)
			.selectAll('path')
			.data(chords)
			.enter()
			.append('path')
			.attr('d', ribbon as any)
			.style('fill', (d: any) => {
				// Use the same trade balance logic as the rim
				return getTradeBalanceColor(tradeBalances[d.source.index]);
			})
			.style('stroke', config.ribbonStroke)
			.style('stroke-width', config.ribbonStrokeWidth)
			.style('opacity', '0.7')
			.attr('opacity', '0.7')
			.on('mouseover', function (event: any, d: any) {
				if (!config.showTooltip) return;
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
					<div style="font-weight:700;margin-bottom:8px;color:#111827;">${sourceCountry} ⇄ ${targetCountry}</div>
					<div style="display:grid;grid-template-columns:auto auto;row-gap:6px;column-gap:12px;align-items:baseline;">
						<div style="color:#6B7280;">${sourceCountry} Exports</div>
						<div style="color:#374151;font-weight:700;">$${(valueSP / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;">${targetCountry} Exports</div>
						<div style="color:#374151;font-weight:700;">$${(valuePS / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;">Trade Balance</div>
						<div style="color:${tradeBalance >= 0 ? '#08605F' : '#931F1D'};font-weight:700;">${tradeBalance >= 0 ? '+' : '-'}$${(Math.abs(tradeBalance) / 1e9).toFixed(1)}B</div>
					</div>
				`;

				tooltipDiv
					.style('opacity', 1)
					.html(tooltipContent)
					.style('left', event.pageX + 10 + 'px')
					.style('top', event.pageY - 10 + 'px');
			})
			.on('mouseout', function () {
				if (!config.showTooltip) return;
				tooltipDiv.style('opacity', 0);
			});
	}
</script>

<div bind:this={container}></div>