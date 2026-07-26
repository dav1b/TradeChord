<script lang="ts">
	// Size-aware sparkline of a value series with a zero baseline (for balance).
	import { scaleLinear } from 'd3';

	let {
		series,
		height = 40,
		color = 'var(--text-3)'
	}: {
		series: { year: number; value: number }[];
		height?: number;
		color?: string;
	} = $props();

	let width = $state(0);

	const x = $derived(
		scaleLinear()
			.domain([series[0]?.year ?? 0, series[series.length - 1]?.year ?? 1])
			.range([1, Math.max(1, width - 1)])
	);
	const y = $derived(
		scaleLinear()
			.domain([Math.min(0, ...series.map((s) => s.value)), Math.max(0, ...series.map((s) => s.value))])
			.range([height - 2, 2])
	);
	const path = $derived(
		width ? series.map((s, i) => `${i === 0 ? 'M' : 'L'}${x(s.year)},${y(s.value)}`).join(' ') : ''
	);
</script>

<div class="wrap" bind:clientWidth={width} style:height="{height}px">
	{#if width}
		<svg {width} {height} aria-hidden="true">
			<line x1="0" x2={width} y1={y(0)} y2={y(0)} class="zero" />
			<path d={path} fill="none" stroke={color} stroke-width="1.5" />
		</svg>
	{/if}
</div>

<style>
	.wrap {
		width: 100%;
	}
	svg {
		display: block;
	}
	.zero {
		stroke: var(--border-faint);
		stroke-width: 1;
	}
</style>
