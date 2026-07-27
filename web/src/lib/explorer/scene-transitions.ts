import { crossfade } from 'svelte/transition';
import { motionDuration } from '$lib/motion';

/** Shared send/receive pair lets one semantic entity move between scene containers. */
export const [sendEntity, receiveEntity] = crossfade({
	duration: (distance) => motionDuration(Math.min(650, Math.max(220, Math.sqrt(distance * 500)))),
	fallback: (_node, _params, intro) => ({
		duration: motionDuration(180),
		css: (t) => `opacity: ${intro ? t : 1 - t}`
	})
});
