<script lang="ts">
	import { partnerKey } from '$lib/explorer/entity';

	export type RibbonBounds = { x: number; y: number; width: number; height: number };
	export type ExtractedRibbonGeometry = {
		partner: string;
		path: string;
		fill: string;
		bounds: RibbonBounds;
	};

	let {
		reporter,
		geometry,
		width,
		height,
		progress
	}: {
		reporter: string;
		geometry: ExtractedRibbonGeometry;
		width: number;
		height: number;
		progress: number;
	} = $props();

	const compact = $derived(width < 640);
	const targetWidth = $derived(compact ? width * 0.46 : Math.min(width * 0.3, 390));
	const targetHeight = $derived(compact ? height * 0.15 : Math.min(height * 0.22, 190));
	const targetScale = $derived(
		Math.min(
			0.72,
			targetWidth / Math.max(geometry.bounds.width, 1),
			targetHeight / Math.max(geometry.bounds.height, 1)
		)
	);
	const anchorX = $derived(compact ? 14 : Math.max(24, width * 0.045));
	const anchorY = $derived(compact ? 18 : Math.max(28, height * 0.055));
	const targetX = $derived(anchorX - geometry.bounds.x * targetScale);
	const targetY = $derived(anchorY - geometry.bounds.y * targetScale);
	const translateX = $derived(width / 2 + (targetX - width / 2) * progress);
	const translateY = $derived(height / 2 + (targetY - height / 2) * progress);
	const scale = $derived(1 + (targetScale - 1) * progress);
</script>

<svg
	class="extracted-layer"
	{width}
	{height}
	role="img"
	aria-label="Extracted {geometry.partner} relationship ribbon"
	data-entity-id={partnerKey(reporter, geometry.partner)}
	data-progress={progress}
>
	<g transform="translate({translateX},{translateY}) scale({scale})">
		<path
			class="extracted-ribbon"
			d={geometry.path}
			fill={geometry.fill}
			stroke="color-mix(in srgb, var(--dj-carbon) 45%, transparent)"
		/>
	</g>
	<text
		class="extracted-label"
		x={anchorX}
		y={anchorY + geometry.bounds.height * targetScale + 24}
		opacity={progress}
	>
		{geometry.partner}
	</text>
</svg>

<style>
	.extracted-layer {
		position: absolute;
		inset: 0;
		z-index: 4;
		overflow: visible;
		pointer-events: none;
	}
	.extracted-ribbon {
		stroke-width: 2;
		filter: saturate(1.24);
	}
	.extracted-label {
		font-family: var(--font-head);
		font-size: clamp(1.2rem, 2.5vw, 2rem);
		font-weight: 500;
		fill: var(--text-1);
	}
</style>
