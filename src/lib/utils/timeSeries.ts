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

// ---- Slope chart builder ----
export interface SlopeDatum {
    partner: string;
    v1: number; // exports from reporter to partner in year1
    v2: number; // exports from reporter to partner in year2
}

export function buildSlopeData(
    data: TradeRecord[],
    reporterCode: string,
    year1: number,
    year2: number,
    topN: number = 10
): SlopeDatum[] {
    // Filter to reporter exports only for the two years
    const filtered = data.filter(
        (r) => r.indicator === 'XPRT-TRD-VL' && r.reporter === reporterCode && (parseInt(r.year) === year1 || parseInt(r.year) === year2)
    );

    const key = (y: number, p: string) => `${y}__${p}`;
    const valueMap = new Map<string, number>();
    filtered.forEach((r) => {
        const v = (parseFloat(r.value) || 0) * 1000;
        valueMap.set(key(parseInt(r.year), r.partner), (valueMap.get(key(parseInt(r.year), r.partner)) || 0) + v);
    });

    // Determine top partners by year2 values (most recent) and exclude ROW
    const partnersSet = new Set<string>();
    filtered.forEach((r) => { if (r.partner !== 'ROW') partnersSet.add(r.partner); });
    const partners = Array.from(partnersSet);
    partners.sort((a, b) => (valueMap.get(key(year2, b)) || 0) - (valueMap.get(key(year2, a)) || 0));
    const top = partners.slice(0, Math.max(1, topN));

    return top.map((p) => ({
        partner: p,
        v1: valueMap.get(key(year1, p)) || 0,
        v2: valueMap.get(key(year2, p)) || 0,
    }));
}

// Build slope data based on share of total exports/imports and trade-balance sign per year
export interface SlopeShareDatum {
    partner: string;
    s1: number; // share as fraction (0..1) in year1
    s2: number; // share as fraction (0..1) in year2
    b1: boolean; // trade balance >= 0 in year1
    b2: boolean; // trade balance >= 0 in year2
    v1?: number; // value in year1
    v2?: number; // value in year2
    total1?: number; // total exports/imports in year1
    total2?: number; // total exports/imports in year2
}

export function buildSlopeShareData(
    data: TradeRecord[],
    reporterCode: string,
    year1: number,
    year2: number,
    topN: number = 10,
    mode: 'exports' | 'imports' = 'exports'
): SlopeShareDatum[] {
    const y1 = year1; const y2 = year2;

    const isYear = (r: TradeRecord) => parseInt(r.year) === y1 || parseInt(r.year) === y2;
    const filtered = data.filter((r) => r.indicator === 'XPRT-TRD-VL' && isYear(r) && (r.reporter === reporterCode || r.partner === reporterCode));

    // Totals by year for reporter exports and imports
    const totals = new Map<number, { exports: number; imports: number }>();
    totals.set(y1, { exports: 0, imports: 0 }); totals.set(y2, { exports: 0, imports: 0 });

    filtered.forEach((r) => {
        const y = parseInt(r.year); const v = (parseFloat(r.value) || 0) * 1000;
        const cur = totals.get(y)!;
        if (r.reporter === reporterCode) totals.set(y, { exports: cur.exports + v, imports: cur.imports });
        if (r.partner === reporterCode) totals.set(y, { exports: cur.exports, imports: cur.imports + v });
    });

    const key = (y: number, p: string, type: 'exports' | 'imports') => `${y}__${p}__${type}`;
    const values = new Map<string, number>();

    filtered.forEach((r) => {
        const y = parseInt(r.year); const v = (parseFloat(r.value) || 0) * 1000;
        if (r.reporter === reporterCode) {
            values.set(key(y, r.partner, 'exports'), (values.get(key(y, r.partner, 'exports')) || 0) + v);
        }
        if (r.partner === reporterCode) {
            values.set(key(y, r.reporter, 'imports'), (values.get(key(y, r.reporter, 'imports')) || 0) + v);
        }
    });

    // Determine top partners by selected mode in year2
    const partnersSet = new Set<string>();
    filtered.forEach((r) => { const p = r.reporter === reporterCode ? r.partner : r.reporter; if (p !== 'ROW') partnersSet.add(p); });
    const partners = Array.from(partnersSet);
    partners.sort((a, b) => (values.get(key(y2, b, mode)) || 0) - (values.get(key(y2, a, mode)) || 0));
    const top = partners.slice(0, Math.max(1, topN));

    const result: SlopeShareDatum[] = top.map((p) => {
        const exp1 = values.get(key(y1, p, 'exports')) || 0;
        const exp2 = values.get(key(y2, p, 'exports')) || 0;
        const imp1 = values.get(key(y1, p, 'imports')) || 0;
        const imp2 = values.get(key(y2, p, 'imports')) || 0;
        const tot1 = totals.get(y1)!;
        const tot2 = totals.get(y2)!;
        const s1 = mode === 'exports' ? (tot1.exports ? exp1 / tot1.exports : 0) : (tot1.imports ? imp1 / tot1.imports : 0);
        const s2 = mode === 'exports' ? (tot2.exports ? exp2 / tot2.exports : 0) : (tot2.imports ? imp2 / tot2.imports : 0);
        const b1 = (exp1 - imp1) >= 0;
        const b2 = (exp2 - imp2) >= 0;
        const v1 = mode === 'exports' ? exp1 : imp1;
        const v2 = mode === 'exports' ? exp2 : imp2;
        const total1 = mode === 'exports' ? tot1.exports : tot1.imports;
        const total2 = mode === 'exports' ? tot2.exports : tot2.imports;
        return { partner: p, s1, s2, b1, b2, v1, v2, total1, total2 };
    });

    // Add ROW (Rest of World) - aggregate all partners not in top N
    const topSet = new Set(top);
    const remainingPartners = partners.filter(p => !topSet.has(p));
    
    if (remainingPartners.length > 0) {
        let rowExp1 = 0, rowExp2 = 0, rowImp1 = 0, rowImp2 = 0;
        
        remainingPartners.forEach(p => {
            rowExp1 += values.get(key(y1, p, 'exports')) || 0;
            rowExp2 += values.get(key(y2, p, 'exports')) || 0;
            rowImp1 += values.get(key(y1, p, 'imports')) || 0;
            rowImp2 += values.get(key(y2, p, 'imports')) || 0;
        });
        
        const tot1 = totals.get(y1)!;
        const tot2 = totals.get(y2)!;
        const s1 = mode === 'exports' ? (tot1.exports ? rowExp1 / tot1.exports : 0) : (tot1.imports ? rowImp1 / tot1.imports : 0);
        const s2 = mode === 'exports' ? (tot2.exports ? rowExp2 / tot2.exports : 0) : (tot2.imports ? rowImp2 / tot2.imports : 0);
        const b1 = (rowExp1 - rowImp1) >= 0;
        const b2 = (rowExp2 - rowImp2) >= 0;
        const v1 = mode === 'exports' ? rowExp1 : rowImp1;
        const v2 = mode === 'exports' ? rowExp2 : rowImp2;
        const total1 = mode === 'exports' ? tot1.exports : tot1.imports;
        const total2 = mode === 'exports' ? tot2.exports : tot2.imports;
        
        result.push({ partner: 'ROW', s1, s2, b1, b2, v1, v2, total1, total2 });
    }

    return result;
}
