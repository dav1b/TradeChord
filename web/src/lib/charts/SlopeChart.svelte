<script lang="ts">
	// Reference reactive chart (F2 pattern): D3 computes the scale, Svelte renders
	// the SVG and owns reactivity + entrance animation. Size-aware via clientWidth.
	// Lines are Parchment "marks" coloured by direction (teal rose / ember fell).
	import { scaleLinear } from 'd3';
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';
	import { pct } from '$lib/format';
	import { deltaColor } from '$lib/theme/tokens';

	let {
		rows,
		leftLabel,
		rightLabel,
		height = 280
	}: {
		rows: { label: string; a: number; b: number }[];
		leftLabel: string;
		rightLabel: string;
		height?: number;
	} = $props();

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
	const t = tweened(1, { duration: 550, easing: cubicOut });
	$effect(() => {
		rows; // re-animate when the data changes (e.g. country switch)
		t.set(0, { duration: 0 });
		t.set(1);
	});
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
				<line x1={xL} y1={y(r.a)} x2={xR} y2={yb} stroke={col} stroke-width="1.5" opacity="0.85" />
				<circle cx={xL} cy={y(r.a)} r="3" fill={col} />
				<circle cx={xR} cy={yb} r="3" fill={col} />
				<text x={xL - 8} y={leftY[i]} class="lbl" text-anchor="end" dominant-baseline="middle">
					{r.label} · {pct(r.a)}
				</text>
				<text x={xR + 8} y={rightY[i]} class="val" text-anchor="start" dominant-baseline="middle">
					{pct(r.b)}
				</text>
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
