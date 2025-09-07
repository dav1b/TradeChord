import type { TradeRecord } from './transform';

export interface TimeSeriesData {
	year: number;
	exports: number;
	imports: number;
	balance: number;
}

export function buildTimeSeriesData(data: TradeRecord[], countryCode: string): TimeSeriesData[] {
	// Filter data for the selected country and all years 2002-2022
	const filtered = data.filter(
		(r) => 
			r.indicator === 'XPRT-TRD-VL' && 
			(r.reporter === countryCode || r.partner === countryCode) &&
			parseInt(r.year) >= 2002 && parseInt(r.year) <= 2022
	);

	// Group by year
	const yearData = new Map<number, { exports: number; imports: number }>();
	
	// Initialize all years 2002-2022
	for (let year = 2002; year <= 2022; year++) {
		yearData.set(year, { exports: 0, imports: 0 });
	}

	// Aggregate data by year
	filtered.forEach((r) => {
		const year = parseInt(r.year);
		const value = (parseFloat(r.value) || 0) * 1000;
		
		if (r.reporter === countryCode) {
			// This country is exporting
			const current = yearData.get(year)!;
			yearData.set(year, { ...current, exports: current.exports + value });
		}
		if (r.partner === countryCode) {
			// This country is importing
			const current = yearData.get(year)!;
			yearData.set(year, { ...current, imports: current.imports + value });
		}
	});

	// Convert to array and calculate balance
	return Array.from(yearData.entries())
		.map(([year, data]) => ({
			year,
			exports: data.exports,
			imports: data.imports,
			balance: data.exports - data.imports
		}))
		.sort((a, b) => a.year - b.year);
}
