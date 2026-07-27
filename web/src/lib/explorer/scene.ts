import { flowKey, partnerKey, productKey, type TradeEntityId } from './entity';

export type SceneRepresentation = 'chord' | 'rank' | 'relationship' | 'products' | 'history';
export type SceneFlow = 'export' | 'import' | 'both';
export type SceneLevel = 'country' | 'relationship' | 'product' | 'history' | 'change' | 'quality';
export type SceneDirection = 'expand' | 'contract' | 'reorder' | 'select' | 'reset';

export interface SceneState {
	reporter: string;
	year: number;
	comparisonYear: number | null;
	flow: SceneFlow;
	partner: string | null;
	product: string | null;
	level: SceneLevel;
	representation: SceneRepresentation;
}

export type SceneInput = Pick<
	SceneState,
	'reporter' | 'year' | 'flow' | 'partner' | 'product' | 'representation'
>;

export type SceneAction =
	| { type: 'select-partner'; partner: string }
	| { type: 'open-relationship'; partner: string }
	| { type: 'open-products'; flow: 'export' | 'import' }
	| { type: 'open-history'; partner?: string }
	| { type: 'select-year'; year: number }
	| { type: 'select-relationship-product'; product: string }
	| { type: 'select-national-product'; product: string }
	| { type: 'show-representation'; representation: SceneRepresentation }
	| { type: 'clear-selection' };

export interface SceneTransition {
	revision: number;
	action: SceneAction['type'] | 'sync';
	direction: SceneDirection;
	focusEntity: TradeEntityId | null;
	announcement: string;
}

export function stateFromInput(input: SceneInput): SceneState {
	return normalizeScene({
		...input,
		comparisonYear: null,
		level: 'country'
	});
}

export function normalizeScene(state: SceneState): SceneState {
	const next = { ...state };
	if (
		!next.partner &&
		(next.representation === 'relationship' ||
			next.representation === 'products' ||
			next.representation === 'history')
	) {
		next.representation = 'chord';
	}
	if (next.representation === 'products' && next.flow === 'both') {
		next.representation = next.partner ? 'relationship' : 'chord';
	}
	if (!next.partner && next.flow !== 'both') next.flow = 'both';
	next.level =
		next.representation === 'history'
			? 'history'
			: next.representation === 'products' && next.product
			? 'product'
			: next.partner
				? 'relationship'
				: next.product
					? 'product'
					: 'country';
	return next;
}

export function reduceScene(state: SceneState, action: SceneAction): SceneState {
	const next = { ...state };
	switch (action.type) {
		case 'select-partner':
			next.partner = next.partner === action.partner ? null : action.partner;
			next.product = null;
			next.flow = 'both';
			break;
		case 'open-relationship':
			next.partner = action.partner;
			next.product = null;
			next.flow = 'both';
			next.representation = 'relationship';
			break;
		case 'open-products':
			if (!next.partner) return state;
			next.flow = action.flow;
			next.product = null;
			next.representation = 'products';
			break;
		case 'open-history':
			if (action.partner) next.partner = action.partner;
			if (!next.partner) return state;
			next.product = null;
			next.flow = 'both';
			next.representation = 'history';
			break;
		case 'select-year':
			next.year = action.year;
			break;
		case 'select-relationship-product':
			if (!next.partner || next.representation !== 'products') return state;
			next.product = next.product === action.product ? null : action.product;
			break;
		case 'select-national-product':
			next.product = next.product === action.product ? null : action.product;
			next.partner = null;
			next.flow = 'both';
			break;
		case 'show-representation':
			if (
				(action.representation === 'relationship' ||
					action.representation === 'products' ||
					action.representation === 'history') &&
				!next.partner
			)
				return state;
			if (action.representation === 'products' && next.flow === 'both') return state;
			next.representation = action.representation;
			break;
		case 'clear-selection':
			next.partner = null;
			next.product = null;
			next.flow = 'both';
			next.representation =
				next.representation === 'relationship' ||
				next.representation === 'products' ||
				next.representation === 'history'
					? 'chord'
					: next.representation;
			break;
	}
	return normalizeScene(next);
}

export function transitionFor(
	previous: SceneState,
	next: SceneState,
	action: SceneAction,
	revision: number
): SceneTransition {
	let direction: SceneDirection = 'select';
	if (
		action.type === 'open-relationship' ||
		action.type === 'open-products' ||
		action.type === 'open-history'
	)
		direction = 'expand';
	if (
		action.type === 'show-representation' &&
		(previous.representation === 'relationship' ||
			previous.representation === 'products' ||
			previous.representation === 'history') &&
		(next.representation === 'chord' || next.representation === 'relationship')
	)
		direction = 'contract';
	if (action.type === 'show-representation' && next.representation === 'rank') direction = 'reorder';
	if (action.type === 'clear-selection') direction = 'reset';

	return {
		revision,
		action: action.type,
		direction,
		focusEntity: action.type === 'select-year' ? null : focusForScene(next),
		announcement: describeScene(next)
	};
}

export function focusForScene(state: SceneState): TradeEntityId | null {
	return state.representation === 'products' && state.partner && state.flow !== 'both'
		? state.product
			? productKey(state.reporter, state.partner, state.flow, state.product)
			: flowKey(state.reporter, state.partner, state.flow)
		: state.partner
			? partnerKey(state.reporter, state.partner)
			: null;
}

export function describeScene(state: SceneState): string {
	if (state.representation === 'products' && state.partner && state.flow !== 'both') {
		const selected = state.product ? `, ${state.product} selected` : '';
		return `${state.reporter} ${state.flow} products with ${state.partner}, ${state.year}${selected}`;
	}
	if (state.representation === 'history' && state.partner) {
		return `${state.reporter} bilateral history with ${state.partner}, ${state.year} selected`;
	}
	if (state.representation === 'relationship' && state.partner) {
		return `${state.reporter} bilateral relationship with ${state.partner}, ${state.year}`;
	}
	if (state.representation === 'rank') {
		return `${state.reporter} partners ranked by total trade, ${state.year}`;
	}
	return `${state.reporter} trade network, ${state.year}`;
}
