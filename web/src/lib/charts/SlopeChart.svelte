<script lang="ts">
	// Reference reactive chart (F2 pattern): D3 computes the scale, Svelte renders
	// the SVG and owns reactivity + entrance animation. Size-aware via clientWidth.
	// Lines are Parchment "marks" coloured by direction (teal rose / ember fell).
	import { scaleLinear } from 'd3';
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';
	import { pct } from '$lib/format';
	import { deltaColor } from '$lib/theme/tokens';
	import { hideTip, showTip, type TradePoint } from '$lib/ui/tradepoint.svelte';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import { motionDuration } from '$lib/motion';

	interface Row {
		label: string;
		a: number;
		b: number;
		pointA: TradePoint;
		pointB: TradePoint;
	}

	let {
		rows,
		leftLabel,
		rightLabel,
		onselect,
		height = 280
	}: {
		rows: Row[];
		leftLabel: string;
		rightLabel: string;
		onselect?: (label: string) => void;
		height?: number;
	} = $props();
	const explorer = useExplorer();

	let width = $state(0);
	const margin = { top: 24, right: 92, bottom: 10, left: 96 };

	const maxShare = $derived(Math.max(0.0001, ...rows.flatMap((r) => [r.a, r.b])));
	const y = $derived(scaleLinear().domain([0, maxShare]).range([height - margin.bottom, margin.top]));
	const xL = $derived(margin.left);
	const xR = $derived(width - margin.right);

	// Push overlapping labels apart while preserving order (slope-chart de-collision).
	const minGap = 13;
	function dodge(ys: number[]): number[] {
		const order = ys.map((v, i) => [v, i] as [number, number]).sort((p, q) => p[0] - q[0]);
		const out = new Array<number>(ys.length);
		let last = -Infinity;
		for (const [v, i] of order) {
			const yy = Math.max(v, last + minGap);
			out[i] = yy;
			last = yy;
		}
		return out;
	}
	const leftY = $derived(dodge(rows.map((r) => y(r.a))));
	const rightY = $derived(dodge(rows.map((r) => y(r.b))));

	// Entrance: lines swing from flat (both at left value) into their slope.
	const t = tweened(1, { duration: motionDuration(550), easing: cubicOut });
	$effect(() => {
		rows; // re-animate when the data changes (e.g. country switch)
		t.set(0, { duration: 0 });
		t.set(1);
	});

	function recessed(label: string): boolean {
		return explorer.state.partner != null && label !== explorer.state.partner;
	}
	function keyselect(e: KeyboardEvent, label: string) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			activate(label);
		}
	}
	function activate(label: string) {
		if (onselect) onselect(label);
		else explorer.selectPartner(label);
	}
</script>

<div class="wrap" bind:clientWidth={width}>
	{#if width > 0 && rows.length}
		<svg {width} {height} role="img" aria-label="Partner export share, {leftLabel} to {rightLabel}">
			<text x={xL} y={11} class="axis" text-anchor="middle">{leftLabel}</text>
			<text x={xR} y={11} class="axis" text-anchor="middle">{rightLabel}</text>
			<line x1={xL} y1={margin.top} x2={xL} y2={height - margin.bottom} class="rule" />
			<line x1={xR} y1={margin.top} x2={xR} y2={height - margin.bottom} class="rule" />
			{#each rows as r, i (r.label)}
				{@const yb = y(r.a + (r.b - r.a) * $t)}
				{@const col = deltaColor(r.b - r.a, true)}
				{@const rec = recessed(r.label)}
				<line
					x1={xL}
					y1={y(r.a)}
					x2={xR}
					y2={yb}
					stroke={col}
					stroke-width="1.5"
					opacity={rec ? 0.12 : 0.85}
				/>
				<g
					class="hit"
					role="button"
					tabindex="0"
					aria-label="{r.label} {leftLabel}"
					style:opacity={rec ? 0.3 : 1}
					onmousemove={(e) => showTip(r.pointA, e)}
					onmouseleave={hideTip}
					onclick={() => activate(r.label)}
					onkeydown={(e) => keyselect(e, r.label)}
				>
					<circle cx={xL} cy={y(r.a)} r="11" fill="transparent" pointer-events="all" />
					<circle cx={xL} cy={y(r.a)} r="3" fill={col} />
					<text x={xL - 8} y={leftY[i]} class="lbl" text-anchor="end" dominant-baseline="middle">
						{r.label} · {pct(r.a)}
					</text>
				</g>
				<g
					class="hit"
					role="button"
					tabindex="0"
					aria-label="{r.label} {rightLabel}"
					style:opacity={rec ? 0.3 : 1}
					onmousemove={(e) => showTip(r.pointB, e)}
					onmouseleave={hideTip}
					onclick={() => activate(r.label)}
					onkeydown={(e) => keyselect(e, r.label)}
				>
					<circle cx={xR} cy={yb} r="11" fill="transparent" pointer-events="all" />
					<circle cx={xR} cy={yb} r="3" fill={col} />
					<text x={xR + 8} y={rightY[i]} class="val" text-anchor="start" dominant-baseline="middle">
						{pct(r.b)}
					</text>
				</g>
			{/each}
		</svg>
	{/if}
</div>

<style>
	.wrap {
		width: 100%;
	}
	svg {
		display: block;
		font-family: var(--font-body);
	}
	.axis {
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		fill: var(--text-3);
	}
	.rule {
		stroke: var(--chart-line);
		stroke-width: 1;
	}
	.hit {
		cursor: pointer;
		transition: opacity var(--motion) var(--ease);
	}
	.hit:focus {
		outline: none;
	}
	.hit:focus-visible {
		outline: 2px solid var(--active);
	}
	.lbl {
		font-size: 11px;
		fill: var(--text-2);
	}
	.val {
		font-size: 11px;
		fill: var(--text-3);
		font-variant-numeric: tabular-nums;
	}
</style>
