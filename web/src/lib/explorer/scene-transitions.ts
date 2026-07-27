import { crossfade } from 'svelte/transition';
import { motionDuration } from '$lib/motion';
import type { SceneDirection } from './scene';

export interface SceneChoreography {
	dim: number;
	transform: number;
	reveal: number;
	label: number;
}

/** One shared visual grammar: selected geometry moves before supporting labels. */
export function choreography(direction: SceneDirection): SceneChoreography {
	if (direction === 'reset') return { dim: 0, transform: 120, reveal: 220, label: 320 };
	if (direction === 'reorder') return { dim: 0, transform: 420, reveal: 360, label: 520 };
	return { dim: 120, transform: 420, reveal: 560, label: 700 };
}

/** Shared send/receive pair lets one semantic entity move between scene containers. */
export const [sendEntity, receiveEntity] = crossfade({
	duration: (distance) => motionDuration(Math.min(650, Math.max(220, Math.sqrt(distance * 500)))),
	fallback: (_node, _params, intro) => ({
		duration: motionDuration(180),
		css: (t) => `opacity: ${intro ? t : 1 - t}`
	})
});
