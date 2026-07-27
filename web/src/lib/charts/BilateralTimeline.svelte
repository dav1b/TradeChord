<script lang="ts">
	import { line, scaleLinear } from 'd3';
	import { fade } from 'svelte/transition';
	import { flowKey, partnerKey, yearPointKey } from '$lib/explorer/entity';
	import type { PartnerHistoryPoint } from '$lib/explorer/scene-graph';
	import { receiveEntity, sendEntity } from '$lib/explorer/scene-transitions';
	import { useSceneViewport } from '$lib/explorer/scene-viewport.svelte';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import { motionDuration } from '$lib/motion';
	import { usd, usdSigned } from '$lib/format';

	let {
		reporter,
		partner,
		points
	}: {
		reporter: string;
		partner: string;
		points: PartnerHistoryPoint[];
	} = $props();

	const explorer = useExplorer();
	const viewport = useSceneViewport();
	let width = $state(0);
	const height = $derived(viewport.mode === 'wide' ? 430 : viewport.mode === 'compact' ? 310 : 360);
	const margin = $derived(
		viewport.mode === 'compact'
			? { top: 28, right: 18, bottom: 45, left: 54 }
			: { top: 30, right: 28, bottom: 48, left: 72 }
	);
	const available = $derived(
		points.filter((point) => point.exportAvailable || point.importAvailable)
	);
	const selected = $derived(
		points.find((point) => point.year === explorer.state.year) ?? available.at(-1) ?? null
	);
	const years = $derived(points.map((point) => point.year));
	const maximum = $derived(
		Math.max(1, ...available.flatMap((point) => [point.exportsUsd, point.importsUsd]))
	);
	const x = $derived(
		scaleLinear()
			.domain([Math.min(...years), Math.max(...years)])
			.range([margin.left, Math.max(margin.left, width - margin.right)])
	);
	const y = $derived(
		scaleLinear()
			.domain([0, maximum])
			.nice()
			.range([height - margin.bottom, margin.top])
	);
	const exportPath = $derived(
		line<PartnerHistoryPoint>()
			.defined((point) => point.exportAvailable)
			.x((point) => x(point.year))
			.y((point) => y(point.exportsUsd))(points) ?? ''
	);
	const importPath = $derived(
		line<PartnerHistoryPoint>()
			.defined((point) => point.importAvailable)
			.x((point) => x(point.year))
			.y((point) => y(point.importsUsd))(points) ?? ''
	);
	const ticks = $derived(
		viewport.mode === 'compact'
			? years.filter((year, index) => index === 0 || index === years.length - 1 || index % 5 === 0)
			: years.filter((year, index) => index === 0 || index === years.length - 1 || index % 2 === 0)
	);

	function returnToNetwork() {
		explorer.setRepresentation('chord');
	}

	function returnToRelationship() {
		explorer.setRepresentation('relationship');
	}

	function selectYear(year: number) {
		explorer.selectYear(year);
	}

	function keyYear(event: KeyboardEvent, index: number) {
		if (event.key === 'ArrowLeft' && index > 0) {
			event.preventDefault();
			selectYear(points[index - 1].year);
		}
		if (event.key === 'ArrowRight' && index < points.length - 1) {
			event.preventDefault();
			selectYear(points[index + 1].year);
		}
	}
</script>

<section
	class="timeline"
	aria-labelledby="timeline-title"
	tabindex="-1"
	data-entity-id={partnerKey(reporter, partner)}
>
	<nav class="trail" aria-label="Analytical path">
		<button onclick={returnToNetwork}>Network</button>
		<span aria-hidden="true">→</span>
		<button onclick={returnToRelationship}>{partner}</button>
		<span aria-hidden="true">→</span>
		<strong>History</strong>
	</nav>

	<div class="heading">
		<div>
			<p class="kicker">{reporter} ↔ {partner}</p>
			<h4 id="timeline-title">Bilateral trade through time</h4>
		</div>
		{#if selected}
			<div class="selected-year">
				<span>Selected year</span>
				<strong>{selected.year}</strong>
			</div>
		{/if}
	</div>

	{#if selected}
		<div class="values" in:fade={{ duration: motionDuration(160) }}>
			<div><span>Reported exports</span><strong>{selected.exportAvailable ? usd(selected.exportsUsd) : 'Unavailable'}</strong></div>
			<div><span>Reported imports</span><strong>{selected.importAvailable ? usd(selected.importsUsd) : 'Unavailable'}</strong></div>
			<div><span>Reported balance</span><strong>{selected.balanceUsd == null ? 'Unavailable' : usdSigned(selected.balanceUsd)}</strong></div>
		</div>
	{/if}

	<div class="chart" bind:clientWidth={width} style:height="{height}px">
		{#if width > 0 && points.length}
			<svg {width} {height} role="img" aria-label="{reporter} and {partner} bilateral trade history">
				{#each y.ticks(4) as tick (tick)}
					<line
						x1={margin.left}
						x2={width - margin.right}
						y1={y(tick)}
						y2={y(tick)}
						class="gridline"
					/>
					<text x={margin.left - 8} y={y(tick)} class="axis-value" text-anchor="end">
						{usd(tick, 0)}
					</text>
				{/each}
				{#each ticks as tick (tick)}
					<text x={x(tick)} y={height - 15} class="axis-year" text-anchor="middle">{tick}</text>
				{/each}

				{#if selected}
					<line
						x1={x(selected.year)}
						x2={x(selected.year)}
						y1={margin.top}
						y2={height - margin.bottom}
						class="selection-rule"
					/>
				{/if}

				<path
					d={exportPath}
					class="series exports"
					in:receiveEntity={{ key: flowKey(reporter, partner, 'export') }}
					out:sendEntity={{ key: flowKey(reporter, partner, 'export') }}
				/>
				<path
					d={importPath}
					class="series imports"
					in:receiveEntity={{ key: flowKey(reporter, partner, 'import') }}
					out:sendEntity={{ key: flowKey(reporter, partner, 'import') }}
				/>

				{#each points as point, index (point.year)}
					{#if point.exportAvailable}
						<circle
							cx={x(point.year)}
							cy={y(point.exportsUsd)}
							r={selected?.year === point.year ? 6 : 3}
							class="point exports"
							role="button"
							tabindex={selected?.year === point.year ? 0 : -1}
							data-entity-id={yearPointKey(reporter, partner, 'export', point.year)}
							aria-label="{point.year}, reported exports {usd(point.exportsUsd)}"
							onclick={() => selectYear(point.year)}
							onkeydown={(event) => keyYear(event, index)}
						/>
					{/if}
					{#if point.importAvailable}
						<circle
							cx={x(point.year)}
							cy={y(point.importsUsd)}
							r={selected?.year === point.year ? 6 : 3}
							class="point imports"
							role="button"
							tabindex="-1"
							data-entity-id={yearPointKey(reporter, partner, 'import', point.year)}
							aria-label="{point.year}, reported imports {usd(point.importsUsd)}"
							onclick={() => selectYear(point.year)}
							onkeydown={(event) => keyYear(event, index)}
						/>
					{/if}
				{/each}
			</svg>
		{/if}
	</div>

	<label class="scrubber">
		<span>Scrub year</span>
		<input
			type="range"
			min={Math.min(...years)}
			max={Math.max(...years)}
			step="1"
			value={explorer.state.year}
			aria-valuetext={String(explorer.state.year)}
			oninput={(event) => selectYear(Number(event.currentTarget.value))}
		/>
	</label>

	<div class="legend" aria-hidden="true">
		<span><i class="export-key"></i>Reported exports</span>
		<span><i class="import-key"></i>Reported imports</span>
	</div>
</section>

<style>
	.timeline {
		min-height: 440px;
		padding-top: var(--space-2);
	}
	.timeline:focus {
		outline: none;
	}
	.trail {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		margin-bottom: var(--space-4);
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--text-4);
		text-transform: uppercase;
	}
	.trail button {
		border: 0;
		padding: 0;
		background: transparent;
		color: var(--active);
		font: inherit;
		text-transform: inherit;
		cursor: pointer;
	}
	.trail button:focus-visible,
	.scrubber input:focus-visible {
		outline: 2px solid var(--active);
		outline-offset: 3px;
	}
	.trail strong {
		color: var(--text-1);
	}
	.heading {
		display: flex;
		align-items: end;
		justify-content: space-between;
		gap: var(--space-4);
	}
	.kicker,
	.selected-year span,
	.values span,
	.scrubber span,
	.legend {
		font-family: var(--font-mono);
		font-size: 9px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--text-4);
	}
	h4 {
		margin-top: 2px;
		font-size: 1.65rem;
		font-weight: 500;
		color: var(--text-1);
	}
	.selected-year {
		text-align: right;
	}
	.selected-year span,
	.selected-year strong {
		display: block;
	}
	.selected-year strong {
		font-size: 1.35rem;
		color: var(--active);
	}
	.values {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: var(--space-4);
		margin-top: var(--space-4);
		padding: var(--space-3) 0;
		border-top: 1px solid var(--border-faint);
		border-bottom: 1px solid var(--border-faint);
	}
	.values span,
	.values strong {
		display: block;
	}
	.values strong {
		margin-top: 2px;
		font-size: 1rem;
		color: var(--text-1);
	}
	.chart {
		width: 100%;
		margin-top: var(--space-3);
	}
	svg {
		display: block;
		overflow: visible;
	}
	.gridline {
		stroke: var(--border-faint);
	}
	.axis-value,
	.axis-year {
		font-family: var(--font-mono);
		font-size: 9px;
		fill: var(--text-4);
		dominant-baseline: middle;
	}
	.selection-rule {
		stroke: var(--active);
		stroke-width: 1;
		stroke-dasharray: 3 3;
		opacity: 0.55;
	}
	.series {
		fill: none;
		stroke-width: 3;
		stroke-linejoin: round;
		stroke-linecap: round;
	}
	.series.exports,
	.point.exports {
		stroke: var(--delta-pos);
	}
	.series.imports,
	.point.imports {
		stroke: var(--delta-neg);
	}
	.point {
		fill: var(--surface);
		stroke-width: 2;
		cursor: pointer;
		transition: r var(--motion) var(--ease);
	}
	.point:focus {
		outline: none;
		stroke-width: 4;
	}
	.scrubber {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		align-items: center;
		gap: var(--space-3);
		margin-top: var(--space-2);
	}
	.scrubber input {
		width: 100%;
		accent-color: var(--active);
	}
	.legend {
		display: flex;
		justify-content: flex-end;
		gap: var(--space-4);
		margin-top: var(--space-3);
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.legend i {
		width: 18px;
		height: 3px;
	}
	.export-key {
		background: var(--delta-pos);
	}
	.import-key {
		background: var(--delta-neg);
	}
	@media (max-width: 520px) {
		h4 {
			font-size: 1.3rem;
		}
		.values {
			grid-template-columns: 1fr;
			gap: var(--space-2);
		}
		.values > div {
			display: flex;
			justify-content: space-between;
			align-items: baseline;
		}
		.legend {
			justify-content: flex-start;
			flex-wrap: wrap;
		}
	}
</style>
