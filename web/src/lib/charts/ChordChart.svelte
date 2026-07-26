<script lang="ts">
	// Reporter-centric chord on the F2 pattern: d3.chord for the layout, Svelte for
	// the SVG. A "star" matrix — reporter → partner = exports, partner → reporter =
	// imports — so each ribbon's two ends are sized by the two flows, and the whole
	// reporter arc vs the partner arcs reflects the balance. Ribbons/arcs coloured by
	// each partner's balance (teal surplus / ember deficit); reporter is navy.
	import { arc as d3arc, chord as d3chord, ribbon as d3ribbon } from 'd3';
	import { fade } from 'svelte/transition';
	import {
		countryPoint,
		hideTip,
		partnerPoint,
		showTip,
		type TradePoint
	} from '$lib/ui/tradepoint.svelte';
	import { clearSelection, selectPartner, selection } from '$lib/ui/selection.svelte';
	import { motionDuration } from '$lib/motion';
	import type { FlowSummary, PartnerRow } from '$lib/data/types';

	let {
		reporter,
		year,
		rows,
		reporterSummary,
		height = 340
	}: {
		reporter: string;
		year: number;
		rows: PartnerRow[];
		reporterSummary: FlowSummary;
		height?: number;
	} = $props();

	let width = $state(0);
	const band = 10;
	const R = $derived(Math.max(20, Math.min(width, height) / 2 - 40));

	const matrix = $derived.by(() => {
		const n = rows.length + 1;
		const m = Array.from({ length: n }, () => new Array(n).fill(0));
		rows.forEach((r, j) => {
			m[0][j + 1] = r.exportsUsd;
			m[j + 1][0] = r.importsUsd;
		});
		return m;
	});

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const layout = $derived.by((): any => {
		if (!width || !rows.length) return null;
		return d3chord().padAngle(0.045).sortSubgroups((a, b) => b - a)(matrix);
	});

	const arcGen = $derived(d3arc().innerRadius(R - band).outerRadius(R));
	const ribbonGen = $derived(d3ribbon().radius(R - band));

	function color(i: number): string {
		if (i === 0) return 'var(--dj-navy)';
		const r = rows[i - 1];
		if (r.partner === 'ROW') return 'var(--dj-alabaster)';
		return r.balanceUsd >= 0 ? 'var(--delta-pos)' : 'var(--delta-neg)';
	}
	function label(i: number): string {
		return i === 0 ? reporter : rows[i - 1].partner;
	}
	function point(i: number): TradePoint {
		return i === 0 ? countryPoint(reporter, year, reporterSummary) : partnerPoint(reporter, year, rows[i - 1]);
	}
	function recessed(i: number): boolean {
		return selection.partner != null && i !== 0 && rows[i - 1]?.partner !== selection.partner;
	}
	function clickNode(i: number) {
		if (i === 0) clearSelection();
		else selectPartner(rows[i - 1].partner);
	}
	function keyNode(e: KeyboardEvent, i: number) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			clickNode(i);
		}
	}
</script>

<div class="wrap" bind:clientWidth={width} style:height="{height}px">
	{#if layout}
		<svg {width} {height}>
			<g transform="translate({width / 2},{height / 2})">
				{#each layout as ch, i (ch.source.index + '-' + ch.target.index)}
					{@const p = ch.source.index === 0 ? ch.target.index : ch.source.index}
					<path
						class="mark"
						d={ribbonGen(ch) as unknown as string}
						fill={color(p)}
						opacity={recessed(p) ? 0.06 : 0.32}
						in:fade={{ duration: motionDuration(300), delay: i * 14 }}
						role="button"
						tabindex="-1"
						aria-label={label(p)}
						onmousemove={(e) => showTip(point(p), e)}
						onmouseleave={hideTip}
						onclick={() => clickNode(p)}
						onkeydown={(e) => keyNode(e, p)}
					/>
				{/each}
				{#each layout.groups as g (g.index)}
					{@const mid = (g.startAngle + g.endAngle) / 2}
					{@const lx = Math.sin(mid) * (R + 9)}
					{@const ly = -Math.cos(mid) * (R + 9)}
					<path
						class="mark"
						d={arcGen(g)}
						fill={color(g.index)}
						opacity={recessed(g.index) ? 0.15 : 1}
						role="button"
						tabindex="-1"
						aria-label={label(g.index)}
						onmousemove={(e) => showTip(point(g.index), e)}
						onmouseleave={hideTip}
						onclick={() => clickNode(g.index)}
						onkeydown={(e) => keyNode(e, g.index)}
					/>
					<text
						x={lx}
						y={ly}
						class="lbl"
						class:reporter={g.index === 0}
						text-anchor={Math.sin(mid) >= 0 ? 'start' : 'end'}
						dominant-baseline="middle"
					>
						{label(g.index)}
					</text>
				{/each}
			</g>
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
	.mark {
		cursor: pointer;
		transition: opacity var(--motion) var(--ease);
	}
	.mark:focus {
		outline: none;
	}
	.mark:focus-visible {
		outline: 2px solid var(--active);
	}
	.lbl {
		font-family: var(--font-body);
		font-size: 11px;
		fill: var(--text-2);
	}
	.lbl.reporter {
		font-weight: 600;
		fill: var(--text-1);
	}
</style>
