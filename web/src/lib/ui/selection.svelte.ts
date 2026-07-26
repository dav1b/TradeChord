// Cross-filter selection: a partner XOR a product (mutually exclusive in v1).
// Selecting a partner recomputes the product view for that partner (and vice
// versa) and lights it across the other charts; the rest recede.

interface Selection {
	partner: string | null;
	product: string | null;
}

export const selection: Selection = $state({ partner: null, product: null });

export function selectPartner(code: string) {
	const on = selection.partner === code;
	selection.partner = on ? null : code;
	selection.product = null;
}

export function selectProduct(code: string) {
	const on = selection.product === code;
	selection.product = on ? null : code;
	selection.partner = null;
}

export function clearSelection() {
	selection.partner = null;
	selection.product = null;
}

export function hasSelection(): boolean {
	return selection.partner !== null || selection.product !== null;
}
