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
  
  return currentYearData.map(({ product, value, share }) => {
    const prevValue = prevYearMap.get(product) || 0;
    const growth = prevValue > 0 ? ((value - prevValue) / prevValue) * 100 : 0;
    
    return {
      product,
      value,
      share,
      growth
    };
  });
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
