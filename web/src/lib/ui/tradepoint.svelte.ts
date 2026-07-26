// One tooltip model for the whole dashboard.
//
// Every datapoint is the selected reporter intersected with some combination of a
// partner, a product, and a year — carrying the dual-flow equation. `focus` marks
// which of those the point is *about* (what you're hovering); the remaining set
// dimensions form the breadcrumb. Built to survive cross-filtering: a product tile
// under a partner filter is simply a point with both `partner` and `product` set.
import type { FlowSummary, PartnerRow, ProductRow } from '$lib/data/types';

export interface TradePoint {
	reporter: string;
	partner?: string;
	product?: string;
	year: number;
	focus: 'country' | 'partner' | 'product';
	exportsUsd: number;
	importsUsd: number;
	balanceUsd: number;
	share?: number;
	shareOf?: 'exports' | 'imports';
}

interface TipState {
	point: TradePoint | null;
	x: number;
	y: number;
}

export const tip: TipState = $state({ point: null, x: 0, y: 0 });

export function showTip(point: TradePoint, e: { clientX: number; clientY: number }) {
	tip.point = point;
	tip.x = e.clientX;
	tip.y = e.clientY;
}
export function hideTip() {
	tip.point = null;
}

// ── Presentation ─────────────────────────────────────────────────────────────

/** The headline entity: what you're pointing at. */
export function tipTitle(p: TradePoint): string {
	if (p.focus === 'partner') return p.partner ?? p.reporter;
	if (p.focus === 'product') return p.product ?? p.reporter;
	return p.reporter;
}

/** Breadcrumb of the surrounding context (reporter + any *other* set dimensions). */
export function tipContext(p: TradePoint): string {
	if (p.focus === 'country') return `Total trade · ${p.year}`;
	const parts = [p.reporter];
	if (p.partner && p.focus !== 'partner') parts.push(`→ ${p.partner}`);
	if (p.product && p.focus !== 'product') parts.push(`· ${p.product}`);
	parts.push(`· ${p.year}`);
	return parts.join(' ');
}

// ── Builders ─────────────────────────────────────────────────────────────────

export function partnerPoint(
	reporter: string,
	year: number,
	r: PartnerRow,
	product?: string
): TradePoint {
	return {
		reporter,
		partner: r.partner,
		product,
		year,
		focus: 'partner',
		exportsUsd: r.exportsUsd,
		importsUsd: r.importsUsd,
		balanceUsd: r.balanceUsd,
		share: r.exportShare,
		shareOf: 'exports'
	};
}

export function productPoint(
	reporter: string,
	year: number,
	r: ProductRow,
	label: string,
	partner?: string
): TradePoint {
	return {
		reporter,
		product: label,
		partner,
		year,
		focus: 'product',
		exportsUsd: r.exportsUsd,
		importsUsd: r.importsUsd,
		balanceUsd: r.balanceUsd,
		share: r.exportShare,
		shareOf: 'exports'
	};
}

export function countryPoint(reporter: string, year: number, s: FlowSummary): TradePoint {
	return {
		reporter,
		year,
		focus: 'country',
		exportsUsd: s.exportsUsd,
		importsUsd: s.importsUsd,
		balanceUsd: s.balanceUsd
	};
}
