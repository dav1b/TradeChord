export const DASHBOARD = {
	START_YEAR: 2002,
	END_YEAR: 2022,
	TOP_N_PARTNERS: 10,
	CANVAS: { WIDTH: 1500, HEIGHT: 844 }
} as const;

// Shared number formatter: dynamic suffix with decimals only when < 10 units
export function formatWithSuffix(value: number): string {
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
	return `$${abs.toFixed(abs < 10 ? 1 : 0)}`;
}

