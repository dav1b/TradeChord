import { getContext, setContext } from 'svelte';

export type ExplorerRepresentation = 'chord' | 'rank' | 'relationship' | 'products';
export type ExplorerFlow = 'export' | 'import' | 'both';
export type ExplorerLevel = 'country' | 'relationship' | 'product' | 'history' | 'change' | 'quality';

export interface ExplorerState {
	reporter: string;
	year: number;
	comparisonYear: number | null;
	flow: ExplorerFlow;
	partner: string | null;
	product: string | null;
	level: ExplorerLevel;
	representation: ExplorerRepresentation;
}

export type ExplorerInput = Pick<
	ExplorerState,
	'reporter' | 'year' | 'flow' | 'partner' | 'product' | 'representation'
>;

type OnChange = (state: Readonly<ExplorerState>) => void;

export interface ExplorerController {
	readonly state: ExplorerState;
	sync(input: ExplorerInput): void;
	selectPartner(code: string): void;
	openRelationship(code: string): void;
	openProducts(flow: 'export' | 'import'): void;
	selectRelationshipProduct(code: string): void;
	selectProduct(code: string): void;
	clearSelection(): void;
	setRepresentation(representation: ExplorerRepresentation): void;
}

const EXPLORER = Symbol('tradechord-explorer');

export function createExplorer(input: ExplorerInput, onchange: OnChange): ExplorerController {
	const state = $state<ExplorerState>({
		...input,
		comparisonYear: null,
		level:
			input.representation === 'products' && input.product
				? 'product'
				: input.partner
					? 'relationship'
					: input.product
						? 'product'
						: 'country'
	});

	function changed() {
		onchange(state);
	}

	return {
		get state() {
			return state;
		},
		sync(next) {
			state.reporter = next.reporter;
			state.year = next.year;
			state.flow = next.flow;
			state.partner = next.partner;
			state.product = next.product;
			state.representation = next.representation;
			state.level =
				next.representation === 'products' && next.product
					? 'product'
					: next.partner
						? 'relationship'
						: next.product
							? 'product'
							: 'country';
		},
		selectPartner(code) {
			state.partner = state.partner === code ? null : code;
			state.product = null;
			state.flow = 'both';
			state.level = state.partner ? 'relationship' : 'country';
			changed();
		},
		openRelationship(code) {
			state.partner = code;
			state.product = null;
			state.flow = 'both';
			state.level = 'relationship';
			state.representation = 'relationship';
			changed();
		},
		openProducts(flow) {
			if (!state.partner) return;
			state.flow = flow;
			state.product = null;
			state.level = 'product';
			state.representation = 'products';
			changed();
		},
		selectRelationshipProduct(code) {
			if (!state.partner || state.representation !== 'products') return;
			state.product = state.product === code ? null : code;
			state.level = state.product ? 'product' : 'relationship';
			changed();
		},
		selectProduct(code) {
			state.product = state.product === code ? null : code;
			state.partner = null;
			state.level = state.product ? 'product' : 'country';
			changed();
		},
		clearSelection() {
			state.partner = null;
			state.product = null;
			state.flow = 'both';
			state.level = 'country';
			changed();
		},
		setRepresentation(representation) {
			if (state.representation === representation) return;
			if ((representation === 'relationship' || representation === 'products') && !state.partner)
				return;
			state.representation = representation;
			state.level =
				representation === 'products'
					? state.product
						? 'product'
						: 'relationship'
					: representation === 'relationship' && state.partner
						? 'relationship'
						: 'country';
			changed();
		}
	};
}

export function provideExplorer(controller: ExplorerController): ExplorerController {
	setContext(EXPLORER, controller);
	return controller;
}

export function useExplorer(): ExplorerController {
	const controller = getContext<ExplorerController>(EXPLORER);
	if (!controller) throw new Error('Explorer context is unavailable');
	return controller;
}
