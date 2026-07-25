<script lang="ts">
	import { afterUpdate } from 'svelte';
	import * as d3 from 'd3';
	import type { SimpleChordData } from '$lib/utils/transform';

	export let data: SimpleChordData;
	export let rawData: any[] = []; // Raw trade data for global calculations
	export let year: string = '2022'; // Year for global trade calculations

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

		// Create country code to index mapping for consistent indexing
		const countryIndexMap = new Map(countries.map((country, i) => [country, i]));

		// Function to get trade balance color
		const getTradeBalanceColor = (balance: number) => {
			return balance >= 0 ? config.positiveBalanceColor : config.negativeBalanceColor;
		};

		// Function to calculate bilateral trade balance between two countries
		const getBilateralTradeBalance = (sourceIndex: number, targetIndex: number) => {
			const sourceToTarget = matrix[sourceIndex][targetIndex];
			const targetToSource = matrix[targetIndex][sourceIndex];
			return sourceToTarget - targetToSource;
		};

		// Function to get ribbon color based on bilateral trade balance
		const getRibbonColor = (d: any) => {
			const bilateralBalance = getBilateralTradeBalance(d.source.index, d.target.index);
			return getTradeBalanceColor(bilateralBalance);
		};

		// Function to get ribbon opacity based on trade flow volume
		const getRibbonOpacity = (d: any) => {
			const maxFlow = Math.max(...matrix.flat());
			const currentFlow = d.source.value;
			// Scale opacity from 0.3 to 0.8 based on flow volume
			return 0.3 + (currentFlow / maxFlow) * 0.5;
		};

		// Function to calculate global trade totals for a country
		const getGlobalTradeTotals = (countryCode: string, year: string) => {
			if (!rawData.length) return { exports: 0, imports: 0, balance: 0 };
			
			const yearData = rawData.filter(record => record.year === year);
			
			// Calculate total exports (this country as reporter)
			const exports = yearData
				.filter(record => record.reporter === countryCode && record.indicator === 'XPRT-TRD-VL')
				.reduce((sum, record) => sum + parseFloat(record.value || '0'), 0);
			
			// Calculate total imports (this country as partner)
			const imports = yearData
				.filter(record => record.partner === countryCode && record.indicator === 'XPRT-TRD-VL')
				.reduce((sum, record) => sum + parseFloat(record.value || '0'), 0);
			
			return {
				exports,
				imports,
				balance: exports - imports
			};
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
			.style('fill', (d: any) => {
				// Use consistent indexing for rim colors
				return getTradeBalanceColor(tradeBalances[d.index]);
			})
			.style('stroke', config.rimStroke)
			.style('stroke-width', config.rimStrokeWidth)
			.style('cursor', 'pointer')
			.on('mouseover', function (event: any, d: any) {
				if (!config.showTooltip) return;
				const countryCode = countries[d.index];
				const countryLabel = countryLabels[d.index];
				
				// Get global trade totals for this country
				const globalTotals = getGlobalTradeTotals(countryCode, year);
				const { exports, imports, balance } = globalTotals;
				const totalTrade = exports + imports;
				
				// Calculate trade balance percentage
				const balancePct = totalTrade > 0 ? ((balance / totalTrade) * 100) : 0;
				
				// Calculate export/import ratios
				const exportRatio = totalTrade > 0 ? ((exports / totalTrade) * 100) : 0;
				const importRatio = totalTrade > 0 ? ((imports / totalTrade) * 100) : 0;

				const tooltipContent = `
					<div style="font-weight:700;margin-bottom:8px;color:#111827;">${countryLabel} (${countryCode}) - Global Trade ${year}</div>
					<div style="display:grid;grid-template-columns:auto auto;row-gap:6px;column-gap:12px;align-items:baseline;">
						<div style="color:#6B7280;">Global Exports</div>
						<div style="color:#374151;font-weight:700;">$${(exports / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;">Global Imports</div>
						<div style="color:#374151;font-weight:700;">$${(imports / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;">Global Balance</div>
						<div style="color:${balance >= 0 ? '#08605F' : '#931F1D'};font-weight:700;">${balance >= 0 ? '+' : '-'}$${(Math.abs(balance) / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;font-size:10px;grid-column:1/-1;margin-top:4px;border-top:1px solid #E5E7EB;padding-top:4px;">
							Exports: ${exportRatio.toFixed(1)}% • Imports: ${importRatio.toFixed(1)}% • Balance: ${balancePct >= 0 ? '+' : ''}${balancePct.toFixed(1)}%
						</div>
						<div style="color:#6B7280;font-size:10px;grid-column:1/-1;margin-top:2px;">
							Rim color shows global trade balance
						</div>
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
				// Use bilateral trade balance for ribbon colors
				return getRibbonColor(d);
			})
			.style('stroke', config.ribbonStroke)
			.style('stroke-width', config.ribbonStrokeWidth)
			.style('opacity', (d: any) => {
				// Use dynamic opacity based on trade flow volume
				return getRibbonOpacity(d);
			})
			.attr('opacity', (d: any) => getRibbonOpacity(d))
			.on('mouseover', function (event: any, d: any) {
				if (!config.showTooltip) return;
				const sourceCountry = countries[d.source.index];
				const targetCountry = countries[d.target.index];
				const valueSP = d.source.value; // source -> partner
				const valuePS = matrix[d.target.index][d.source.index]; // partner -> source
				const bilateralBalance = valueSP - valuePS; // bilateral trade balance
				const sourceTotal = countryTotals[d.source.index];
				const targetTotal = countryTotals[d.target.index];

				const spPct = sourceTotal > 0 ? ((valueSP / sourceTotal) * 100).toFixed(1) : '0.0';
				const psPct = targetTotal > 0 ? ((valuePS / targetTotal) * 100).toFixed(1) : '0.0';

				const tooltipContent = `
					<div style="font-weight:700;margin-bottom:8px;color:#111827;">${sourceCountry} ⇄ ${targetCountry}</div>
					<div style="display:grid;grid-template-columns:auto auto;row-gap:6px;column-gap:12px;align-items:baseline;">
						<div style="color:#6B7280;">${sourceCountry} → ${targetCountry}</div>
						<div style="color:#374151;font-weight:700;">$${(valueSP / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;">${targetCountry} → ${sourceCountry}</div>
						<div style="color:#374151;font-weight:700;">$${(valuePS / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;">Bilateral Balance</div>
						<div style="color:${bilateralBalance >= 0 ? '#08605F' : '#931F1D'};font-weight:700;">${bilateralBalance >= 0 ? '+' : '-'}$${(Math.abs(bilateralBalance) / 1e9).toFixed(1)}B</div>
						<div style="color:#6B7280;font-size:10px;grid-column:1/-1;margin-top:4px;border-top:1px solid #E5E7EB;padding-top:4px;">
							Ribbon color shows bilateral balance • Opacity shows flow volume
						</div>
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