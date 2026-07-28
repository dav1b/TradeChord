<script lang="ts">
	import { line, scaleLinear } from 'd3';
	import { usd, usdSigned } from '$lib/format';
	import type { RelationshipHistoryPoint } from '$lib/charts/motion/relationship-types';

	let {
		reporter,
		partner,
		points,
		onpreview
	}: {
		reporter: string;
		partner: string;
		points: RelationshipHistoryPoint[];
		onpreview?: (point: RelationshipHistoryPoint | null) => void;
	} = $props();

	let width = $state(0);
	let preview = $state<RelationshipHistoryPoint | null>(null);
	const height = 235;
	const margin = { top: 20, right: 18, bottom: 30, left: 54 };
	const available = $derived(
		points.filter((point) => point.exportAvailable || point.importAvailable)
	);
	const years = $derived(available.map((point) => point.year));
	const yearDomain = $derived(
		years.length ? [Math.min(...years), Math.max(...years)] : [0, 1]
	);
	const maximum = $derived(
		Math.max(1, ...available.flatMap((point) => [point.exportsUsd, point.importsUsd]))
	);
	const x = $derived(
		scaleLinear()
			.domain(yearDomain)
			.range([margin.left, Math.max(margin.left, width - margin.right)])
	);
	const y = $derived(
		scaleLinear()
			.domain([0, maximum])
			.nice()
			.range([height - margin.bottom, margin.top])
	);
	const exportPath = $derived(
		line<RelationshipHistoryPoint>()
			.defined((point) => point.exportAvailable)
			.x((point) => x(point.year))
			.y((point) => y(point.exportsUsd))(available) ?? ''
	);
	const importPath = $derived(
		line<RelationshipHistoryPoint>()
			.defined((point) => point.importAvailable)
			.x((point) => x(point.year))
			.y((point) => y(point.importsUsd))(available) ?? ''
	);
	const segments = $derived(
		available.slice(1).flatMap((point, index) => {
			const previous = available[index];
			if (
				!previous.exportAvailable ||
				!previous.importAvailable ||
				!point.exportAvailable ||
				!point.importAvailable
			)
				return [];
			return [
				{
					key: `${previous.year}-${point.year}`,
					points: `${x(previous.year)},${y(previous.exportsUsd)} ${x(point.year)},${y(
						point.exportsUsd
					)} ${x(point.year)},${y(point.importsUsd)} ${x(previous.year)},${y(
						previous.importsUsd
					)}`,
					positive: (previous.balanceUsd ?? 0) + (point.balanceUsd ?? 0) >= 0
				}
			];
		})
	);
	const ticks = $derived(
		years.filter(
			(year, index) =>
				index === 0 || index === years.length - 1 || index % (width < 560 ? 5 : 3) === 0
		)
	);

	function setPreview(point: RelationshipHistoryPoint | null) {
		preview = point;
		onpreview?.(point);
	}

	function pointerPreview(event: PointerEvent) {
		if (!available.length) return;
		const bounds =
			event.currentTarget instanceof SVGElement
				? event.currentTarget.getBoundingClientRect()
				: null;
		if (!bounds) return;
		const year = x.invert(event.clientX - bounds.left);
		const nearest = available.reduce((best, point) =>
			Math.abs(point.year - year) < Math.abs(best.year - year) ? point : best
		);
		setPreview(nearest);
	}
</script>

<section class="history" aria-label="{reporter} and {partner} trade through time">
	<header>
		<div>
			<span>Historical relationship</span>
			<h3>How have exports and imports changed?</h3>
		</div>
		{#if preview}
			<div class="readout">
				<strong>{preview.year}</strong>
				<span>Exports {usd(preview.exportsUsd)}</span>
				<span>Imports {usd(preview.importsUsd)}</span>
				<span>Balance {preview.balanceUsd == null ? 'Unavailable' : usdSigned(preview.balanceUsd)}</span>
			</div>
		{/if}
	</header>

	<div class="legend">
		<span class="export">Exports</span>
		<span class="import">Imports</span>
		<span>Shaded gap = reported balance</span>
	</div>

	<div class="chart" bind:clientWidth={width} style:height="{height}px">
		{#if width && available.length}
			<svg
				{width}
				{height}
				role="img"
				aria-label="{reporter} and {partner} reported exports and imports by year"
				onpointermove={pointerPreview}
				onpointerleave={() => setPreview(null)}
			>
				{#each y.ticks(3) as tick (tick)}
					<line
						class="grid"
						x1={margin.left}
						x2={width - margin.right}
						y1={y(tick)}
						y2={y(tick)}
					/>
					<text class="axis" x={margin.left - 7} y={y(tick)} text-anchor="end">
						{usd(tick, 0)}
					</text>
				{/each}
				{#each segments as segment (segment.key)}
					<polygon
						points={segment.points}
						fill={segment.positive ? 'var(--pos-dim)' : 'var(--neg-dim)'}
					/>
				{/each}
				<path class="export-line" d={exportPath} />
				<path class="import-line" d={importPath} />
				{#each ticks as tick (tick)}
					<text class="axis" x={x(tick)} y={height - 9} text-anchor="middle">{tick}</text>
				{/each}
				{#each available as point (point.year)}
					<circle
						class="year-hit"
						class:active={preview?.year === point.year}
						cx={x(point.year)}
						cy={y(Math.max(point.exportsUsd, point.importsUsd))}
						r="8"
						role="button"
						tabindex="0"
						aria-label="{point.year}: exports {usd(point.exportsUsd)}, imports {usd(
							point.importsUsd
						)}"
						onfocus={() => setPreview(point)}
						onblur={() => setPreview(null)}
					/>
				{/each}
				{#if preview}
					<line
						class="crosshair"
						x1={x(preview.year)}
						x2={x(preview.year)}
						y1={margin.top}
						y2={height - margin.bottom}
					/>
				{/if}
			</svg>
		{/if}
	</div>
</section>

<style>
	.history {
		margin-top: 18px;
		border-top: 1px solid var(--border-faint);
		padding-top: 16px;
	}
	header {
		display: flex;
		align-items: start;
		justify-content: space-between;
		gap: 16px;
	}
	header span,
	.legend,
	.axis,
	.readout {
		font-family: var(--font-mono);
		font-size: 9px;
		color: var(--text-3);
	}
	header > div > span {
		text-transform: uppercase;
	}
	h3 {
		margin-top: 3px;
		font-size: clamp(1rem, 1.7vw, 1.35rem);
		font-weight: 500;
	}
	.readout {
		display: grid;
		grid-template-columns: repeat(4, auto);
		gap: 8px;
		align-items: baseline;
	}
	.readout strong {
		font-size: 11px;
		color: var(--text-1);
	}
	.legend {
		display: flex;
		gap: 14px;
		margin: 9px 0 2px;
	}
	.legend span::before {
		content: '';
		display: inline-block;
		width: 12px;
		height: 2px;
		margin-right: 5px;
		vertical-align: middle;
		background: var(--text-4);
	}
	.legend .export::before {
		background: var(--delta-pos);
	}
	.legend .import::before {
		background: var(--delta-neg);
	}
	.chart,
	svg {
		display: block;
		width: 100%;
	}
	.grid {
		stroke: var(--border-faint);
		stroke-width: 1;
	}
	.axis {
		dominant-baseline: middle;
	}
	.export-line,
	.import-line {
		fill: none;
		stroke-width: 2.5;
	}
	.export-line {
		stroke: var(--delta-pos);
	}
	.import-line {
		stroke: var(--delta-neg);
	}
	.year-hit {
		fill: transparent;
		stroke: transparent;
		cursor: crosshair;
	}
	.year-hit.active,
	.year-hit:focus-visible {
		fill: var(--surface);
		stroke: var(--dj-carbon);
		stroke-width: 2;
		outline: none;
	}
	.crosshair {
		stroke: var(--dj-carbon);
		stroke-width: 1;
		stroke-dasharray: 3 3;
		pointer-events: none;
	}
	@media (max-width: 640px) {
		header {
			flex-direction: column;
		}
		.readout {
			grid-template-columns: repeat(2, auto);
		}
		.legend {
			flex-wrap: wrap;
		}
	}
</style>
