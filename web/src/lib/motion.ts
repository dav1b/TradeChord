// Respect the user's reduced-motion preference for JS-driven animation
// (CSS transitions already honour it via the --motion token in app.css).

export function prefersReducedMotion(): boolean {
	return (
		typeof window !== 'undefined' &&
		typeof window.matchMedia === 'function' &&
		window.matchMedia('(prefers-reduced-motion: reduce)').matches
	);
}

/** Duration that collapses to 0 when reduced motion is requested. */
export function motionDuration(ms: number): number {
	return prefersReducedMotion() ? 0 : ms;
}
