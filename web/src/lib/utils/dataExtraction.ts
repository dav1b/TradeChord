import type { TradeRecord } from './transform';
import type { ChartData, CountrySummary } from '../services/aiCommentary';
import { buildCountryChord } from './transform';
import { getProductTreemapData, getProductTrendData } from './productAnalysis';
import { buildSlopeShareData } from './timeSeries';

export function extractCountrySummary(
	data: TradeRecord[],
	productData: TradeRecord[],
	countryCode: string,
	year: string = '2022'
): CountrySummary {
	// Get country name (you might want to add a mapping)
	const countryName = getCountryName(countryCode);
	
	// Calculate trade totals
	const countryData = data.filter(r => 
		r.year === year && 
		r.indicator === 'XPRT-TRD-VL' && 
		(r.reporter === countryCode || r.partner === countryCode)
	);
	
	let totalExports = 0;
	let totalImports = 0;
	const partnerData = new Map<string, { exports: number; imports: number }>();
	
	countryData.forEach(record => {
		const value = (parseFloat(record.value) || 0) * 1000;
		
		if (record.reporter === countryCode) {
			totalExports += value;
			const partner = record.partner;
			const current = partnerData.get(partner) || { exports: 0, imports: 0 };
			current.exports += value;
			partnerData.set(partner, current);
		} else if (record.partner === countryCode) {
			totalImports += value;
			const partner = record.reporter;
			const current = partnerData.get(partner) || { exports: 0, imports: 0 };
			current.imports += value;
			partnerData.set(partner, current);
		}
	});
	
	const tradeBalance = totalExports - totalImports;
	
	// Get top partners
	const topPartners = Array.from(partnerData.entries())
		.map(([country, data]) => ({
			country,
			exports: data.exports,
			imports: data.imports,
			balance: data.exports - data.imports
		}))
		.sort((a, b) => (b.exports + b.imports) - (a.exports + a.imports))
		.slice(0, 10);
	
	// Extract chart data
	const chartData = extractChartData(data, productData, countryCode, year);
	
	return {
		countryCode,
		countryName,
		year,
		totalExports,
		totalImports,
		tradeBalance,
		topPartners,
		chartData
	};
}

function extractChartData(
	data: TradeRecord[],
	productData: TradeRecord[],
	countryCode: string,
	year: string
): ChartData[] {
	const charts: ChartData[] = [];
	
	// Chord Diagram Data
	const chordData = buildCountryChord(data, countryCode, 10, year);
	charts.push({
		chartType: 'chord',
		title: 'Trade Flow Network',
		data: {
			countries: chordData.countries,
			matrix: chordData.matrix,
			totalFlows: chordData.matrix.flat().reduce((sum, val) => sum + val, 0)
		},
		insights: [
			`Shows trade relationships between ${countryCode} and ${chordData.countries.length - 1} partners`,
			`Total trade volume: $${(chordData.matrix.flat().reduce((sum, val) => sum + val, 0) / 1e9).toFixed(1)}B`,
			`Largest flows: ${getLargestFlows(chordData.matrix, chordData.countries)}`
		]
	});
	
	// Product Treemap Data
	const treemapData = getProductTreemapData(productData, countryCode, year);
	charts.push({
		chartType: 'treemap',
		title: 'Export Product Breakdown',
		data: {
			products: treemapData,
			totalValue: treemapData.reduce((sum, item) => sum + item.value, 0)
		},
		insights: [
			`${treemapData.length} product categories exported`,
			`Top product: ${treemapData[0]?.product || 'N/A'} (${((treemapData[0]?.value || 0) / treemapData.reduce((sum, item) => sum + item.value, 0) * 100).toFixed(1)}%)`,
			`Product diversification: ${calculateDiversification(treemapData)}`
		]
	});
	
	// Exports Slope Chart Data
	const exportsSlopeData = buildSlopeShareData(data, countryCode, 2002, 2022, 10, 'exports');
	charts.push({
		chartType: 'slope',
		title: 'Export Share Trends (2002-2022)',
		data: {
			partners: exportsSlopeData,
			year1: '2002',
			year2: '2022'
		},
		insights: [
			`Shows how export shares to top partners changed over 20 years`,
			`Most significant changes: ${getSignificantChanges(exportsSlopeData)}`,
			`Concentration trend: ${getConcentrationTrend(exportsSlopeData)}`
		]
	});
	
	// Imports Slope Chart Data
	const importsSlopeData = buildSlopeShareData(data, countryCode, 2002, 2022, 10, 'imports');
	charts.push({
		chartType: 'slope',
		title: 'Import Share Trends (2002-2022)',
		data: {
			partners: importsSlopeData,
			year1: '2002',
			year2: '2022'
		},
		insights: [
			`Shows how import shares from top suppliers changed over 20 years`,
			`Most significant changes: ${getSignificantChanges(importsSlopeData)}`,
			`Supplier diversification: ${getSupplierDiversification(importsSlopeData)}`
		]
	});
	
	return charts;
}

// Helper functions
function getCountryName(countryCode: string): string {
	const countryNames: Record<string, string> = {
		'USA': 'United States',
		'CHN': 'China',
		'DEU': 'Germany',
		'JPN': 'Japan',
		'GBR': 'United Kingdom',
		'FRA': 'France',
		'ITA': 'Italy',
		'CAN': 'Canada',
		'IND': 'India',
		'BRA': 'Brazil',
		'ROW': 'Rest of World'
	};
	return countryNames[countryCode] || countryCode;
}

function getLargestFlows(matrix: number[][], countries: string[]): string {
	const flows: Array<{ from: string; to: string; value: number }> = [];
	
	for (let i = 0; i < matrix.length; i++) {
		for (let j = 0; j < matrix[i].length; j++) {
			if (matrix[i][j] > 0) {
				flows.push({
					from: countries[i],
					to: countries[j],
					value: matrix[i][j]
				});
			}
		}
	}
	
	flows.sort((a, b) => b.value - a.value);
	const top = flows.slice(0, 3);
	return top.map(f => `${f.from}→${f.to}`).join(', ');
}

function calculateDiversification(data: any[]): string {
	if (data.length === 0) return 'No data';
	
	const total = data.reduce((sum, item) => sum + item.value, 0);
	const shares = data.map(item => item.value / total);
	
	// Calculate Herfindahl-Hirschman Index
	const hhi = shares.reduce((sum, share) => sum + share * share, 0);
	
	if (hhi > 0.25) return 'Low (concentrated)';
	if (hhi > 0.15) return 'Medium';
	return 'High (diversified)';
}

function getSignificantChanges(data: any[]): string {
	const changes = data
		.map(d => ({
			partner: d.partner,
			change: Math.abs(d.s2 - d.s1) * 100
		}))
		.sort((a, b) => b.change - a.change)
		.slice(0, 3);
	
	return changes.map(c => `${c.partner} (${c.change.toFixed(1)}pp)`).join(', ');
}

function getConcentrationTrend(data: any[]): string {
	const totalChange = data.reduce((sum, d) => sum + Math.abs(d.s2 - d.s1), 0);
	return totalChange > 0.2 ? 'High volatility' : 'Stable';
}

function getSupplierDiversification(data: any[]): string {
	const rowData = data.find(d => d.partner === 'ROW');
	if (!rowData) return 'No ROW data';
	
	const rowShare = rowData.s2;
	return rowShare > 0.3 ? 'High (many small suppliers)' : 'Low (few large suppliers)';
}
