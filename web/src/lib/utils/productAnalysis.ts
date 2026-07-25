import type { TradeRecord } from './transform';

export interface ProductData {
  product: string;
  value: number;
  share: number;
  growth?: number;
}

export interface ProductTrendData {
  product: string;
  year: number;
  value: number;
  growth: number; // year-over-year growth as percentage
}

export interface ProductTreemapData {
  product: string;
  value: number;
  share: number;
  growth: number;
  trendData?: ProductTrendData[]; // Mini trend data for the treemap
}

export interface PartnerData {
  partner: string;
  value: number;
  share: number;
  growth?: number;
}

export interface PartnerTrendData {
  partner: string;
  year: number;
  value: number;
  growth: number; // year-over-year growth as percentage
}

export interface PartnerTreemapData {
  partner: string;
  value: number;
  share: number;
  growth: number;
  trendData?: PartnerTrendData[]; // Mini trend data for the treemap
}

// Get product data for a specific country and year
export function getProductDataForYear(
  data: TradeRecord[],
  countryCode: string,
  year: string
): ProductData[] {
  const filtered = data.filter(
    (r) => r.year === year && r.reporter === countryCode && r.indicator === 'XPRT-TRD-VL'
  );

  // Aggregate by product
  const productTotals = new Map<string, number>();
  filtered.forEach((r) => {
    const value = (parseFloat(r.value) || 0) * 1000;
    productTotals.set(r.product, (productTotals.get(r.product) || 0) + value);
  });

  const totalValue = Array.from(productTotals.values()).reduce((sum, val) => sum + val, 0);

  return Array.from(productTotals.entries())
    .map(([product, value]) => ({
      product,
      value,
      share: totalValue > 0 ? value / totalValue : 0
    }))
    .sort((a, b) => b.value - a.value);
}

// Get trend data for all products for a country
export function getProductTrendData(
  data: TradeRecord[],
  countryCode: string
): ProductTrendData[] {
  const filtered = data.filter(
    (r) => r.reporter === countryCode && r.indicator === 'XPRT-TRD-VL'
  );

  // Group by product and year
  const productYearData = new Map<string, Map<number, number>>();
  filtered.forEach((r) => {
    const year = parseInt(r.year);
    const value = (parseFloat(r.value) || 0) * 1000;
    
    if (!productYearData.has(r.product)) {
      productYearData.set(r.product, new Map());
    }
    const yearMap = productYearData.get(r.product)!;
    yearMap.set(year, (yearMap.get(year) || 0) + value);
  });

  const result: ProductTrendData[] = [];
  
  productYearData.forEach((yearMap, product) => {
    const years = Array.from(yearMap.keys()).sort();
    
    years.forEach((year, index) => {
      const value = yearMap.get(year)!;
      let growth = 0;
      
      if (index > 0) {
        const prevValue = yearMap.get(years[index - 1])!;
        growth = prevValue > 0 ? ((value - prevValue) / prevValue) * 100 : 0;
      }
      
      result.push({ product, year, value, growth });
    });
  });

  return result;
}

// Get trade balance trend data for all products for a country
export function getProductTradeBalanceTrendData(
  data: TradeRecord[],
  countryCode: string
): ProductTrendData[] {
  // Get exports (country as reporter)
  const exports = data.filter(
    (r) => r.reporter === countryCode && r.indicator === 'XPRT-TRD-VL'
  );

  // Get imports (country as partner)
  const imports = data.filter(
    (r) => r.partner === countryCode && r.indicator === 'XPRT-TRD-VL'
  );

  // Group exports by product and year
  const exportData = new Map<string, Map<number, number>>();
  exports.forEach((r) => {
    const year = parseInt(r.year);
    const value = (parseFloat(r.value) || 0) * 1000;
    
    if (!exportData.has(r.product)) {
      exportData.set(r.product, new Map());
    }
    const yearMap = exportData.get(r.product)!;
    yearMap.set(year, (yearMap.get(year) || 0) + value);
  });

  // Group imports by product and year
  const importData = new Map<string, Map<number, number>>();
  imports.forEach((r) => {
    const year = parseInt(r.year);
    const value = (parseFloat(r.value) || 0) * 1000;
    
    if (!importData.has(r.product)) {
      importData.set(r.product, new Map());
    }
    const yearMap = importData.get(r.product)!;
    yearMap.set(year, (yearMap.get(year) || 0) + value);
  });

  // Calculate trade balance (exports - imports) by product and year
  const allProducts = new Set([...exportData.keys(), ...importData.keys()]);
  const result: ProductTrendData[] = [];
  
  allProducts.forEach((product) => {
    const exportYears = exportData.get(product) || new Map();
    const importYears = importData.get(product) || new Map();
    const allYears = new Set([...exportYears.keys(), ...importYears.keys()]);
    const sortedYears = Array.from(allYears).sort();
    
    sortedYears.forEach((year, index) => {
      const exportValue = exportYears.get(year) || 0;
      const importValue = importYears.get(year) || 0;
      const tradeBalance = exportValue - importValue;
      
      let growth = 0;
      if (index > 0) {
        const prevExportValue = exportYears.get(sortedYears[index - 1]) || 0;
        const prevImportValue = importYears.get(sortedYears[index - 1]) || 0;
        const prevTradeBalance = prevExportValue - prevImportValue;
        growth = prevTradeBalance !== 0 ? ((tradeBalance - prevTradeBalance) / Math.abs(prevTradeBalance)) * 100 : 0;
      }
      
      result.push({ product, year, value: tradeBalance, growth });
    });
  });

  return result;
}

// Get treemap data for latest year with growth calculation
export function getProductTreemapData(
  data: TradeRecord[],
  countryCode: string,
  latestYear: string
): ProductTreemapData[] {
  const currentYearData = getProductDataForYear(data, countryCode, latestYear);
  const prevYear = (parseInt(latestYear) - 1).toString();
  const prevYearData = getProductDataForYear(data, countryCode, prevYear);
  
  const prevYearMap = new Map(prevYearData.map(d => [d.product, d.value]));
  
  // Get trade balance trend data for each product
  const trendData = getProductTradeBalanceTrendData(data, countryCode);
  const trendDataMap = new Map<string, ProductTrendData[]>();
  trendData.forEach(item => {
    if (!trendDataMap.has(item.product)) {
      trendDataMap.set(item.product, []);
    }
    trendDataMap.get(item.product)!.push(item);
  });
  
  return currentYearData.map(({ product, value, share }) => {
    const prevValue = prevYearMap.get(product) || 0;
    const growth = prevValue > 0 ? ((value - prevValue) / prevValue) * 100 : 0;
    
    return {
      product,
      value,
      share,
      growth,
      trendData: trendDataMap.get(product) || []
    };
  });
}

// ===== PARTNER ANALYSIS FUNCTIONS =====

// Get partner data for a specific country and year
export function getPartnerDataForYear(
  data: TradeRecord[],
  countryCode: string,
  year: string
): PartnerData[] {
  const filtered = data.filter(
    (r) => r.year === year && r.reporter === countryCode && r.indicator === 'XPRT-TRD-VL'
  );

  // Aggregate by partner
  const partnerTotals = new Map<string, number>();
  filtered.forEach((r) => {
    const value = (parseFloat(r.value) || 0) * 1000;
    partnerTotals.set(r.partner, (partnerTotals.get(r.partner) || 0) + value);
  });

  const totalValue = Array.from(partnerTotals.values()).reduce((sum, val) => sum + val, 0);

  return Array.from(partnerTotals.entries())
    .map(([partner, value]) => ({
      partner,
      value,
      share: totalValue > 0 ? value / totalValue : 0
    }))
    .sort((a, b) => b.value - a.value);
}

// Get partner trend data over time
export function getPartnerTrendData(
  data: TradeRecord[],
  countryCode: string
): PartnerTrendData[] {
  const filtered = data.filter(
    (r) => r.reporter === countryCode && r.indicator === 'XPRT-TRD-VL'
  );

  // Group by partner and year
  const partnerYearData = new Map<string, Map<number, number>>();
  
  filtered.forEach((r) => {
    const year = parseInt(r.year);
    const value = (parseFloat(r.value) || 0) * 1000;
    
    if (!partnerYearData.has(r.partner)) {
      partnerYearData.set(r.partner, new Map());
    }
    
    const yearData = partnerYearData.get(r.partner)!;
    yearData.set(year, (yearData.get(year) || 0) + value);
  });

  const result: PartnerTrendData[] = [];
  
  partnerYearData.forEach((yearData, partner) => {
    const years = Array.from(yearData.keys()).sort();
    
    years.forEach((year, index) => {
      const value = yearData.get(year)!;
      const prevValue = index > 0 ? yearData.get(years[index - 1])! : 0;
      const growth = prevValue > 0 ? ((value - prevValue) / prevValue) * 100 : 0;
      
      result.push({
        partner,
        year,
        value,
        growth
      });
    });
  });

  return result;
}

// Get partner trade balance trend data (exports - imports per partner)
export function getPartnerTradeBalanceTrendData(
  data: TradeRecord[],
  countryCode: string
): PartnerTrendData[] {
  const filtered = data.filter(
    (r) => r.indicator === 'XPRT-TRD-VL' && 
           (r.reporter === countryCode || r.partner === countryCode)
  );

  // Group by partner and year
  const partnerYearData = new Map<string, Map<number, { exports: number; imports: number }>>();
  
  filtered.forEach((r) => {
    const year = parseInt(r.year);
    const value = (parseFloat(r.value) || 0) * 1000;
    
    // Determine which partner we're tracking
    const partner = r.reporter === countryCode ? r.partner : r.reporter;
    
    if (!partnerYearData.has(partner)) {
      partnerYearData.set(partner, new Map());
    }
    
    const yearData = partnerYearData.get(partner)!;
    if (!yearData.has(year)) {
      yearData.set(year, { exports: 0, imports: 0 });
    }
    
    const current = yearData.get(year)!;
    if (r.reporter === countryCode) {
      // This country is exporting to partner
      yearData.set(year, { ...current, exports: current.exports + value });
    } else {
      // This country is importing from partner
      yearData.set(year, { ...current, imports: current.imports + value });
    }
  });

  const result: PartnerTrendData[] = [];
  
  partnerYearData.forEach((yearData, partner) => {
    const years = Array.from(yearData.keys()).sort();
    
    years.forEach((year, index) => {
      const yearDataItem = yearData.get(year)!;
      const value = yearDataItem.exports - yearDataItem.imports; // Trade balance
      
      const prevData = index > 0 ? yearData.get(years[index - 1])! : { exports: 0, imports: 0 };
      const prevValue = prevData.exports - prevData.imports;
      const growth = prevValue !== 0 ? ((value - prevValue) / Math.abs(prevValue)) * 100 : 0;
      
      result.push({
        partner,
        year,
        value,
        growth
      });
    });
  });

  return result;
}

// Get partner treemap data with growth and trend information
export function getPartnerTreemapData(
  data: TradeRecord[],
  countryCode: string,
  year: string
): PartnerTreemapData[] {
  const currentYearData = getPartnerDataForYear(data, countryCode, year);
  const prevYear = String(parseInt(year) - 1);
  const prevYearData = getPartnerDataForYear(data, countryCode, prevYear);
  
  // Create map for previous year data
  const prevYearMap = new Map<string, number>();
  prevYearData.forEach(({ partner, value }) => {
    prevYearMap.set(partner, value);
  });
  
  // Get trade balance trend data for each partner
  const trendData = getPartnerTradeBalanceTrendData(data, countryCode);
  const trendDataMap = new Map<string, PartnerTrendData[]>();
  trendData.forEach(item => {
    if (!trendDataMap.has(item.partner)) {
      trendDataMap.set(item.partner, []);
    }
    trendDataMap.get(item.partner)!.push(item);
  });
  
  return currentYearData.map(({ partner, value, share }) => {
    const prevValue = prevYearMap.get(partner) || 0;
    const growth = prevValue > 0 ? ((value - prevValue) / prevValue) * 100 : 0;
    
    return {
      partner,
      value,
      share,
      growth,
      trendData: trendDataMap.get(partner) || []
    };
  });
}

// Get partner trend data for slope charts
export function getPartnerTrendDataForSlope(
  data: TradeRecord[],
  countryCode: string
): PartnerTrendData[] {
  return getPartnerTrendData(data, countryCode);
}

// Get available countries from the dataset
export function getAvailableCountries(data: TradeRecord[]): string[] {
  return Array.from(new Set(data.map(r => r.reporter))).sort();
}

// Get available years from the dataset
export function getAvailableYears(data: TradeRecord[]): string[] {
  return Array.from(new Set(data.map(r => r.year))).sort();
}

// Get available products from the dataset
export function getAvailableProducts(data: TradeRecord[]): string[] {
  return Array.from(new Set(data.map(r => r.product))).sort();
}
