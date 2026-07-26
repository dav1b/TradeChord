// DataJockey design tokens for use in JS/D3.
//
// The CSS custom properties in dj-design.css are the source of truth. For SVG
// fills you can use the `var(--…)` strings directly; for D3 colour scales that
// need concrete values (interpolation), resolve them at runtime with `token()`.

/** CSS custom-property names, so call sites never hardcode a hex value. */
export const TOKEN = {
	// brand carriers
	navy: '--dj-navy',
	carbon: '--dj-carbon',
	parchment: '--dj-parchment',
	alabaster: '--dj-alabaster',
	// semantic
	protagonist: '--protagonist',
	accent: '--accent',
	accentHighlight: '--accent-highlight',
	// delta / directional (fills + parchment marks)
	deltaPos: '--delta-pos',
	deltaNeg: '--delta-neg',
	deltaPosMark: '--delta-pos-mark',
	deltaNegMark: '--delta-neg-mark',
	// chart internals
	chartLabel: '--chart-label',
	chartValue: '--chart-value',
	chartFaint: '--chart-faint',
	chartLine: '--chart-line',
	ghost: '--ghost-stroke'
} as const;

export const SEQUENTIAL = [
	'--sequential-1',
	'--sequential-2',
	'--sequential-3',
	'--sequential-4',
	'--sequential-5'
] as const;

export const DIVERGING = [
	'--diverging-neg-2',
	'--diverging-neg-1',
	'--diverging-mid',
	'--diverging-pos-1',
	'--diverging-pos-2'
] as const;

/** As a `var()` reference, safe for CSS and SVG `fill`/`stroke` attributes. */
export function cssVar(name: string): string {
	return `var(${name})`;
}

/**
 * Resolve a custom property to its computed value (browser only). Pass an
 * element to read a themed value (e.g. inside a `.dj-theme-navy` band);
 * defaults to `:root`.
 */
export function token(name: string, el?: Element): string {
	if (typeof window === 'undefined') return '';
	const target = el ?? document.documentElement;
	return getComputedStyle(target).getPropertyValue(name).trim();
}

/** Resolve a list of custom properties (e.g. a colour ramp) to concrete values. */
export function tokens(names: readonly string[], el?: Element): string[] {
	return names.map((n) => token(n, el));
}

/** Directional colour for a value: teal (positive) / ember (negative). */
export function deltaColor(value: number, asMark = false): string {
	if (asMark) return cssVar(value >= 0 ? TOKEN.deltaPosMark : TOKEN.deltaNegMark);
	return cssVar(value >= 0 ? TOKEN.deltaPos : TOKEN.deltaNeg);
}
