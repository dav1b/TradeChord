<script lang="ts">
	import { arc as d3arc, chord as d3chord, ribbon as d3ribbon } from 'd3';
	import { cubicOut } from 'svelte/easing';
	import { tweened } from 'svelte/motion';
	import RelationshipBridge from '$lib/charts/motion/RelationshipBridge.svelte';
	import {
		ribbonHighlight,
		type HighlightStyle
	} from '$lib/charts/motion/highlight';
	import type { RelationshipPhase } from '$lib/charts/motion/relationship-choreography';
	import { motionDuration } from '$lib/motion';
	import { partnerKey } from '$lib/explorer/entity';
	import { usd } from '$lib/format';
	import type { FlowSummary, PartnerRow } from '$lib/data/types';

	let {
		reporter,
		rows,
		summary,
		phase,
		highlightStyle,
		onselect,
		onclose
	}: {
		reporter: string;
		rows: PartnerRow[];
		summary: FlowSummary;
		phase: RelationshipPhase;
		highlightStyle: HighlightStyle;
		onselect?: (partner: string | null) => void;
		onclose?: () => void;
	} = $props();

	let width = $state(0);
	let height = $state(0);
	let selected = $state<string | null>(null);
	const emphasis = tweened<number[]>([], {
		duration: motionDuration(560),
		easing: cubicOut,
		interpolate: (from, to) => (progress) =>
			from.map((value, index) => value + ((to[index] ?? 0) - value) * progress)
	});
	const bridgeProgress = tweened(0, {
		duration: motionDuration(620),
		easing: cubicOut
	});

	$effect(() => {
		if ($emphasis.length !== rows.length) void emphasis.set(rows.map(() => 0), { duration: 0 });
	});

	$effect(() => {
		const bridgeVisible =
			phase === 'extracting' || phase === 'opening' || phase === 'relationship';
		void bridgeProgress.set(bridgeVisible ? 1 : 0, {
			duration: motionDuration(bridgeVisible ? 620 : 480)
		});
	});

	const size = $derived(Math.max(260, Math.min(width, height)));
	const outerRadius = $derived(Math.max(100, size / 2 - (size < 500 ? 34 : 28)));
	const band = $derived(size < 500 ? 9 : 13);
	const focusAmount = $derived(Math.max(0, ...$emphasis));
	const selectedRow = $derived(rows.find((row) => row.partner === selected) ?? null);

	const matrix = $derived.by(() => {
		const count = rows.length + 1;
		const result = Array.from({ length: count }, () => new Array(count).fill(0));
		rows.forEach((row, index) => {
			result[0][index + 1] = row.exportsUsd;
			result[index + 1][0] = row.importsUsd;
		});
		return result;
	});

	// D3 geometry always reflects the reported values. Selection may change visual
	// emphasis or position, but must never reweight the analytical layout.
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const layout = $derived.by((): any =>
		width && height
			? d3chord()
					.padAngle(size < 500 ? 0.035 : 0.045)
					.sortSubgroups((a, b) => b - a)(matrix)
			: null
	);
	const arc = $derived(d3arc().innerRadius(outerRadius - band).outerRadius(outerRadius));
	const ribbon = $derived(d3ribbon().radius(outerRadius - band));
	const reporterMid = $derived(
		layout ? (layout.groups[0].startAngle + layout.groups[0].endAngle) / 2 : 0
	);
	const reporterLabelRadius = $derived(outerRadius + (size < 500 ? 18 : 28));
	const reporterLabelX = $derived(Math.sin(reporterMid) * reporterLabelRadius + 8);
	const reporterLabelY = $derived(-Math.cos(reporterMid) * reporterLabelRadius);

	function partnerIndex(chord: { source: { index: number }; target: { index: number } }) {
		return (chord.source.index === 0 ? chord.target.index : chord.source.index) - 1;
	}

	function color(index: number) {
		const row = rows[index];
		if (row.partner === 'ROW' || row.balanceUsd == null) return 'var(--dj-alabaster)';
		return row.balanceUsd >= 0 ? 'var(--delta-pos)' : 'var(--delta-neg)';
	}

	function ribbonOpacity(index: number) {
		const energy = $emphasis[index] ?? 0;
		const presentation = ribbonHighlight(highlightStyle, energy, focusAmount);
		const bridgeRecession =
			selected === rows[index].partner ? 1 - $bridgeProgress * 0.82 : 1 - $bridgeProgress * 0.68;
		return presentation.opacity * bridgeRecession;
	}

	function activate(index: number) {
		const partner = rows[index].partner;
		if (partner === 'ROW') return;
		if (selected !== partner && $bridgeProgress > 0) {
			void bridgeProgress.set(0, { duration: 0 });
		}
		selected = selected === partner ? null : partner;
		void emphasis.set(
			rows.map((row) => (row.partner === selected ? 1 : 0)),
			{ duration: motionDuration(selected ? 560 : 420) }
		);
		onselect?.(selected);
	}

	function reset() {
		if (!selected && focusAmount === 0) return;
		selected = null;
		void emphasis.set(rows.map(() => 0), { duration: motionDuration(420) });
		onselect?.(null);
	}

	function keyActivate(event: KeyboardEvent, index: number) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			activate(index);
		}
	}

	function windowKey(event: KeyboardEvent) {
		if (event.key === 'Escape') reset();
	}
</script>

<svelte:window onkeydown={windowKey} />

<div class="chord-stage" bind:clientWidth={width} bind:clientHeight={height}>
	{#if layout}
		<svg
			{width}
			{height}
			role="img"
			aria-label="{reporter} trade chord. Select a ribbon to preview its motion."
		>
			<g transform="translate({width / 2},{height / 2})">
				{#each layout as chord (partnerKey(reporter, rows[partnerIndex(chord)].partner))}
					{@const index = partnerIndex(chord)}
					{@const partnerGroup = layout.groups[index + 1]}
					{@const mid = (partnerGroup.startAngle + partnerGroup.endAngle) / 2}
					{@const presentation = ribbonHighlight(
						highlightStyle,
						$emphasis[index] ?? 0,
						focusAmount
					)}
					<path
						class="ribbon"
						class:selected={selected === rows[index].partner}
						d={ribbon(chord) as unknown as string}
						fill={color(index)}
						opacity={ribbonOpacity(index)}
						style:filter="saturate({presentation.saturation})"
						stroke="color-mix(in srgb, var(--dj-carbon) {presentation.strokeOpacity * 100}%, transparent)"
						role="button"
						tabindex={rows[index].partner === 'ROW' ? -1 : 0}
						aria-pressed={selected === rows[index].partner}
						aria-label="{rows[index].partner}, total trade {usd(
							rows[index].exportsUsd + rows[index].importsUsd
						)}"
						data-partner={rows[index].partner}
						onclick={(event) => {
							event.stopPropagation();
							activate(index);
							event.currentTarget.blur();
						}}
						onkeydown={(event) => keyActivate(event, index)}
					/>
				{/each}

				{#each layout.groups as group (group.index)}
					{@const index = group.index - 1}
					{@const mid = (group.startAngle + group.endAngle) / 2}
					<path
						class="arc"
						class:reporter={group.index === 0}
						class:selected={group.index > 0 && selected === rows[index].partner}
						d={arc(group)}
						fill={group.index === 0 ? 'var(--dj-navy)' : color(index)}
						opacity={
							group.index === 0
								? 1
								: (1 - focusAmount * 0.62 + ($emphasis[index] ?? 0) * 0.62) *
									(1 - $bridgeProgress * 0.72)
						}
					/>
					{#if group.index > 0}
						{@const labelRadius = outerRadius + (size < 500 ? 12 : 18)}
						<text
							x={Math.sin(mid) * labelRadius}
							y={-Math.cos(mid) * labelRadius}
							class:selected={selected === rows[index].partner}
							class="partner-label"
							text-anchor={Math.sin(mid) >= 0 ? 'start' : 'end'}
							dominant-baseline="middle"
							opacity={1 - focusAmount * 0.72 + ($emphasis[index] ?? 0) * 0.72}
						>
							{rows[index].partner}
						</text>
					{/if}
				{/each}

				<text
					class="reporter-code"
					x={reporterLabelX}
					y={reporterLabelY - 8}
					text-anchor="start">{reporter}</text
				>
				<text
					class="reporter-total"
					x={reporterLabelX}
					y={reporterLabelY + 14}
					text-anchor="start"
				>
					{usd(summary.exportsUsd + summary.importsUsd)}
				</text>
			</g>
		</svg>
	{/if}
	{#if selectedRow}
		<RelationshipBridge
			{reporter}
			row={selectedRow}
			{width}
			{height}
			progress={$bridgeProgress}
			onclose={() => onclose?.()}
		/>
	{/if}
</div>

<style>
	.chord-stage {
		width: 100%;
		height: 100%;
		min-height: 320px;
	}
	svg {
		display: block;
		overflow: visible;
	}
	.ribbon,
	.arc,
	.partner-label {
		transition:
			filter var(--motion-fast) var(--ease),
			stroke var(--motion-fast) var(--ease);
	}
	.ribbon {
		cursor: pointer;
		stroke: transparent;
		stroke-width: 2;
		transform-box: fill-box;
		transform-origin: center;
	}
	.ribbon:hover,
	.ribbon:focus,
	.ribbon:focus-visible {
		filter: saturate(1.3) brightness(0.95);
		stroke: var(--dj-carbon);
		outline: none !important;
		box-shadow: none;
	}
	.ribbon.selected {
		filter: saturate(1.25);
		stroke: color-mix(in srgb, var(--dj-carbon) 45%, transparent);
	}
	.arc {
		pointer-events: none;
	}
	.partner-label {
		font-family: var(--font-mono);
		font-size: clamp(9px, 1vw, 12px);
		fill: var(--text-2);
		pointer-events: none;
		transition:
			font-size var(--motion-slow) var(--ease),
			opacity var(--motion-base) var(--ease);
	}
	.partner-label.selected {
		font-family: var(--font-head);
		font-size: clamp(1.4rem, 3vw, 2.5rem);
		font-weight: 500;
		fill: var(--text-1);
	}
	.reporter-code {
		font-family: var(--font-head);
		font-size: clamp(1.4rem, 3vw, 2.5rem);
		font-weight: 500;
		fill: var(--text-1);
	}
	.reporter-total {
		font-family: var(--font-mono);
		font-size: clamp(9px, 1vw, 12px);
		fill: var(--text-3);
	}
</style>
