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

// ---- Bump chart types and builder ----

export interface PartnerRankPoint {
    year: number;
    rank: number; // 1 = highest
    value: number; // export value from reporter to this partner for that year
}

export interface PartnerRankSeries {
    partner: string;
    series: PartnerRankPoint[];
}

// Build export ranking over time for top K partners (by total exports across years)
export function buildExportRankSeries(
    data: TradeRecord[],
    reporterCode: string,
    topK: number = 10,
    startYear: number = 2002,
    endYear: number = 2022
): PartnerRankSeries[] {
    // Filter to reporter exports only, XPRT-TRD-VL across years
    const filtered = data.filter(
        (r) =>
            r.indicator === 'XPRT-TRD-VL' &&
            r.reporter === reporterCode &&
            parseInt(r.year) >= startYear &&
            parseInt(r.year) <= endYear
    );

    // Sum exports by partner across all years to determine topK partners
    const totalByPartner = new Map<string, number>();
    filtered.forEach((r) => {
        const v = (parseFloat(r.value) || 0) * 1000;
        totalByPartner.set(r.partner, (totalByPartner.get(r.partner) || 0) + v);
    });

    const topPartners = Array.from(totalByPartner.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, Math.max(1, topK))
        .map(([p]) => p);

    // Build a map: year -> array of { partner, value }
    const yearToValues = new Map<number, Array<{ partner: string; value: number }>>();
    for (let y = startYear; y <= endYear; y++) {
        yearToValues.set(y, []);
    }

    filtered.forEach((r) => {
        const y = parseInt(r.year);
        if (!yearToValues.has(y)) return;
        const v = (parseFloat(r.value) || 0) * 1000;
        // Only keep entries for partners in topPartners for chart clarity
        if (topPartners.includes(r.partner)) {
            yearToValues.get(y)!.push({ partner: r.partner, value: v });
        }
    });

    // For each year, compute ranks (1 = highest). If a partner has no value, treat as 0 and rank accordingly.
    const partnerToSeries = new Map<string, PartnerRankPoint[]>();
    topPartners.forEach((p) => partnerToSeries.set(p, []));

    for (let y = startYear; y <= endYear; y++) {
        const entries = yearToValues.get(y)!;

        // Merge in zero values for missing partners in this year
        const withZeros: Array<{ partner: string; value: number }> = topPartners.map((p) => ({
            partner: p,
            value: 0
        }));
        entries.forEach((e) => {
            const idx = withZeros.findIndex((w) => w.partner === e.partner);
            if (idx >= 0) withZeros[idx].value = e.value;
        });

        // Sort descending by value to assign ranks
        const ranked = withZeros
            .slice()
            .sort((a, b) => b.value - a.value)
            .map((d, i) => ({ ...d, rank: i + 1 }));

        ranked.forEach(({ partner, value, rank }) => {
            partnerToSeries.get(partner)!.push({ year: y, rank, value });
        });
    }

    return Array.from(partnerToSeries.entries()).map(([partner, series]) => ({ partner, series }));
}
