/** Stable semantic IDs shared by every visual representation. */
export type TradeEntityId = string;

export function countryKey(reporter: string): TradeEntityId {
	return `country:${reporter}`;
}

export function partnerKey(reporter: string, partner: string): TradeEntityId {
	return `partner:${reporter}:${partner}`;
}

export function flowKey(
	reporter: string,
	partner: string,
	flow: 'export' | 'import'
): TradeEntityId {
	return `flow:${reporter}:${partner}:${flow}`;
}

export function productKey(
	reporter: string,
	partner: string | null,
	flow: 'export' | 'import' | 'both',
	product: string
): TradeEntityId {
	return `product:${reporter}:${partner ?? 'all'}:${flow}:${product}`;
}
