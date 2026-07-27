import { getContext, setContext } from 'svelte';

export type ExplorerRepresentation = 'chord' | 'rank';
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
	'reporter' | 'year' | 'partner' | 'product' | 'representation'
>;

type OnChange = (state: Readonly<ExplorerState>) => void;

export interface ExplorerController {
	readonly state: ExplorerState;
	sync(input: ExplorerInput): void;
	selectPartner(code: string): void;
	selectProduct(code: string): void;
	clearSelection(): void;
	setRepresentation(representation: ExplorerRepresentation): void;
}

const EXPLORER = Symbol('tradechord-explorer');

export function createExplorer(input: ExplorerInput, onchange: OnChange): ExplorerController {
	const state = $state<ExplorerState>({
		...input,
		comparisonYear: null,
		flow: 'both',
		level: input.partner ? 'relationship' : input.product ? 'product' : 'country'
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
			state.partner = next.partner;
			state.product = next.product;
			state.representation = next.representation;
			state.level = next.partner ? 'relationship' : next.product ? 'product' : 'country';
		},
		selectPartner(code) {
			state.partner = state.partner === code ? null : code;
			state.product = null;
			state.level = state.partner ? 'relationship' : 'country';
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
			state.level = 'country';
			changed();
		},
		setRepresentation(representation) {
			if (state.representation === representation) return;
			state.representation = representation;
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
