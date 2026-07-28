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
	const targetWidth = $derived(compact ? width * 0.46 : Math.min(width * 0.24, 300));
	const targetHeight = $derived(compact ? height * 0.15 : Math.min(height * 0.18, 150));
	const targetScale = $derived(
		Math.min(
			0.72,
			targetWidth / Math.max(geometry.bounds.width, 1),
			targetHeight / Math.max(geometry.bounds.height, 1)
		)
	);
	const anchorX = $derived(
		compact ? width - targetWidth - 22 : width * 0.91 - targetWidth - 20
	);
	const anchorY = $derived(compact ? Math.max(22, height * 0.13) : Math.max(26, height * 0.08));
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
</svg>

<style>
	.extracted-layer {
		position: absolute;
		inset: 0;
		z-index: 6;
		overflow: visible;
		pointer-events: none;
	}
	.extracted-ribbon {
		stroke-width: 2;
		filter: saturate(1.24);
	}
</style>
