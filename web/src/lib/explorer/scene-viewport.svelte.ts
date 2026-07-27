import { getContext, setContext } from 'svelte';

export type SceneViewportMode = 'compact' | 'standard' | 'wide';

export interface SceneViewport {
	readonly width: number;
	readonly mode: SceneViewportMode;
	update(width: number): void;
}

const SCENE_VIEWPORT = Symbol('tradechord-scene-viewport');

export function provideSceneViewport(): SceneViewport {
	let width = $state(0);
	const viewport: SceneViewport = {
		get width() {
			return width;
		},
		get mode() {
			return width < 340 ? 'compact' : width >= 520 ? 'wide' : 'standard';
		},
		update(nextWidth) {
			width = nextWidth;
		}
	};
	setContext(SCENE_VIEWPORT, viewport);
	return viewport;
}

export function useSceneViewport(): SceneViewport {
	const viewport = getContext<SceneViewport>(SCENE_VIEWPORT);
	if (!viewport) throw new Error('Scene viewport context is unavailable');
	return viewport;
}
