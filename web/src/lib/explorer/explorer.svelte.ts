import { getContext, setContext } from 'svelte';
import {
	describeScene,
	focusForScene,
	normalizeScene,
	reduceScene,
	stateFromInput,
	transitionFor,
	type SceneAction,
	type SceneFlow,
	type SceneInput,
	type SceneLevel,
	type SceneRepresentation,
	type SceneState,
	type SceneTransition
} from './scene';

export type ExplorerRepresentation = SceneRepresentation;
export type ExplorerFlow = SceneFlow;
export type ExplorerLevel = SceneLevel;
export type ExplorerState = SceneState;
export type ExplorerInput = SceneInput;

export interface ExplorerChange {
	state: Readonly<ExplorerState>;
	transition: Readonly<SceneTransition>;
}

type OnChange = (change: ExplorerChange) => void;

export interface ExplorerController {
	readonly state: ExplorerState;
	readonly transition: SceneTransition;
	sync(input: ExplorerInput): void;
	dispatch(action: SceneAction): void;
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
	const initial = stateFromInput(input);
	const state = $state<ExplorerState>(initial);
	const transition = $state<SceneTransition>({
		revision: 0,
		action: 'sync',
		direction: 'reset',
		focusEntity: null,
		announcement: describeScene(initial)
	});

	function apply(next: ExplorerState) {
		Object.assign(state, next);
	}

	function dispatch(action: SceneAction) {
		const previous = { ...state };
		const next = reduceScene(previous, action);
		if (next === previous) return;
		apply(next);
		Object.assign(transition, transitionFor(previous, next, action, transition.revision + 1));
		onchange({ state, transition });
	}

	return {
		get state() {
			return state;
		},
		get transition() {
			return transition;
		},
		sync(nextInput) {
			const next = normalizeScene({
				...state,
				...nextInput
			});
			const changed =
				next.reporter !== state.reporter ||
				next.year !== state.year ||
				next.flow !== state.flow ||
				next.partner !== state.partner ||
				next.product !== state.product ||
				next.representation !== state.representation;
			if (!changed) return;
			const previousRepresentation = state.representation;
			apply(next);
			Object.assign(transition, {
				revision: transition.revision + 1,
				action: 'sync',
				direction:
					(previousRepresentation === 'products' && next.representation !== 'products') ||
					(previousRepresentation === 'relationship' && next.representation === 'chord')
						? 'contract'
						: next.representation === 'rank'
							? 'reorder'
							: 'select',
				focusEntity: focusForScene(next),
				announcement: describeScene(next)
			});
		},
		dispatch,
		selectPartner(code) {
			dispatch({ type: 'select-partner', partner: code });
		},
		openRelationship(code) {
			dispatch({ type: 'open-relationship', partner: code });
		},
		openProducts(flow) {
			dispatch({ type: 'open-products', flow });
		},
		selectRelationshipProduct(code) {
			dispatch({ type: 'select-relationship-product', product: code });
		},
		selectProduct(code) {
			dispatch({ type: 'select-national-product', product: code });
		},
		clearSelection() {
			dispatch({ type: 'clear-selection' });
		},
		setRepresentation(representation) {
			dispatch({ type: 'show-representation', representation });
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
