<script lang="ts">
	import { arc as d3arc, chord as d3chord, ribbon as d3ribbon } from 'd3';
	import { cubicOut } from 'svelte/easing';
	import { tweened } from 'svelte/motion';
	import { motionDuration } from '$lib/motion';
	import { partnerKey } from '$lib/explorer/entity';
	import { usd } from '$lib/format';
	import type { FlowSummary, PartnerRow } from '$lib/data/types';

	export type MotionMode = 'breathe' | 'extract';

	let {
		reporter,
		rows,
		summary,
		mode,
		onselect
	}: {
		reporter: string;
		rows: PartnerRow[];
		summary: FlowSummary;
		mode: MotionMode;
		onselect?: (partner: string | null) => void;
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
	const extraction = tweened(0, {
		duration: motionDuration(420),
		easing: cubicOut
	});

	$effect(() => {
		if ($emphasis.length !== rows.length) void emphasis.set(rows.map(() => 0), { duration: 0 });
	});

	$effect(() => {
		void extraction.set(mode === 'extract' ? 1 : 0, { duration: motionDuration(420) });
	});

	const size = $derived(Math.max(260, Math.min(width, height)));
	const outerRadius = $derived(Math.max(100, size / 2 - (size < 500 ? 34 : 28)));
	const band = $derived(size < 500 ? 9 : 13);
	const focusAmount = $derived(Math.max(0, ...$emphasis));

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

	function offset(index: number, angle: number) {
		const energy = $emphasis[index] ?? 0;
		const distance = 32 * $extraction * energy;
		return {
			x: Math.sin(angle) * distance,
			y: -Math.cos(angle) * distance
		};
	}

	function ribbonOpacity(index: number) {
		const energy = $emphasis[index] ?? 0;
		return 0.3 * (1 - focusAmount * 0.76) + energy * 0.72;
	}

	function activate(index: number) {
		const partner = rows[index].partner;
		if (partner === 'ROW') return;
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
					{@const movement = offset(index, mid)}
					<path
						class="ribbon"
						class:selected={selected === rows[index].partner}
						d={ribbon(chord) as unknown as string}
						fill={color(index)}
						opacity={ribbonOpacity(index)}
						transform="translate({movement.x},{movement.y})"
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
						}}
						onkeydown={(event) => keyActivate(event, index)}
					/>
				{/each}

				{#each layout.groups as group (group.index)}
					{@const index = group.index - 1}
					{@const mid = (group.startAngle + group.endAngle) / 2}
					{@const movement = group.index === 0 ? { x: 0, y: 0 } : offset(index, mid)}
					<path
						class="arc"
						class:reporter={group.index === 0}
						class:selected={group.index > 0 && selected === rows[index].partner}
						d={arc(group)}
						fill={group.index === 0 ? 'var(--dj-navy)' : color(index)}
						opacity={
							group.index === 0
								? 1
								: 1 - focusAmount * 0.62 + ($emphasis[index] ?? 0) * 0.62
						}
						transform="translate({movement.x},{movement.y})"
					/>
					{#if group.index > 0}
						{@const labelRadius = outerRadius + (size < 500 ? 12 : 18)}
						<text
							x={Math.sin(mid) * labelRadius + movement.x}
							y={-Math.cos(mid) * labelRadius + movement.y}
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
	.ribbon:focus-visible {
		filter: saturate(1.3) brightness(0.95);
		stroke: var(--dj-carbon);
		outline: none;
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
		font-weight: 600;
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
