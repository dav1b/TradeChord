// Formatting helpers for integer-USD values from the release.

/** Compact USD, e.g. 2062089832731 -> "$2.06T". */
export function usd(value: number, digits = 2): string {
	const abs = Math.abs(value);
	const sign = value < 0 ? '-' : '';
	const units: [number, string][] = [
		[1e12, 'T'],
		[1e9, 'B'],
		[1e6, 'M'],
		[1e3, 'K']
	];
	for (const [scale, suffix] of units) {
		if (abs >= scale) {
			const n = abs / scale;
			return `${sign}$${n.toFixed(n < 10 ? digits : digits > 0 ? 1 : 0)}${suffix}`;
		}
	}
	return `${sign}$${abs.toFixed(0)}`;
}

/** Signed compact USD, e.g. "+$0.88T" / "-$1.31T". */
export function usdSigned(value: number, digits = 2): string {
	const s = usd(Math.abs(value), digits);
	return `${value >= 0 ? '+' : '-'}${s}`;
}

/** Fraction 0..1 -> "12.3%". */
export function pct(fraction: number, digits = 1): string {
	return `${(fraction * 100).toFixed(digits)}%`;
}
