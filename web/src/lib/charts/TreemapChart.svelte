<script lang="ts">
	// Reactive treemap on the F2 pattern: d3.treemap for the layout, Svelte for the
	// SVG. Tiles are sized by exports and tinted by trade balance (teal surplus /
	// ember deficit) with a solid delta accent bar. Size-aware; labels drop out on
	// tiles too small to carry them.
	import { hierarchy, treemap } from 'd3';
	import { fade } from 'svelte/transition';
	import { pct, usd } from '$lib/format';
	import { hideTip, showTip, type TradePoint } from '$lib/ui/tradepoint.svelte';

	export interface TreemapItem {
		label: string;
		value: number;
		point: TradePoint;
	}

	let { items, height = 300 }: { items: TreemapItem[]; height?: number } = $props();

	let width = $state(0);

	interface Node {
		data: TreemapItem;
		x0: number;
		y0: number;
		x1: number;
		y1: number;
	}

	const nodes = $derived.by((): Node[] => {
		if (!width || !items.length) return [];
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const root: any = hierarchy({ children: items } as any)
			.sum((d: any) => d.value ?? 0)
			.sort((a: any, b: any) => (b.value ?? 0) - (a.value ?? 0));
		treemap().size([width, height]).paddingInner(2).round(true)(root);
		return root.leaves() as Node[];
	});
</script>

<div class="wrap" bind:clientWidth={width} style:height="{height}px">
	{#if width > 0}
		<svg {width} {height}>
			{#each nodes as n, i (n.data.label)}
				{@const w = n.x1 - n.x0}
				{@const h = n.y1 - n.y0}
				{@const pos = n.data.point.balanceUsd >= 0}
				<g
					transform="translate({n.x0},{n.y0})"
					in:fade={{ duration: 260, delay: i * 12 }}
					role="img"
					aria-label={n.data.label}
					onmousemove={(e) => showTip(n.data.point, e)}
					onmouseleave={hideTip}
				>
					<rect
						width={w}
						height={h}
						fill={pos ? 'var(--pos-dim)' : 'var(--neg-dim)'}
						stroke="var(--border)"
					/>
					<rect width="3" height={h} fill={pos ? 'var(--delta-pos)' : 'var(--delta-neg)'} />
					{#if w > 56 && h > 30}
						<text x="8" y="17" class="name">{n.data.label}</text>
						<text x="8" y="31" class="val">{usd(n.data.value, 1)}</text>
						{#if h > 46}
							<text x="8" y="45" class="sub">{pct(n.data.point.share ?? 0)} · exports</text>
						{/if}
					{/if}
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
	}
	.name {
		font-family: var(--font-body);
		font-size: 12px;
		font-weight: 500;
		fill: var(--text-1);
	}
	.val {
		font-family: var(--font-body);
		font-size: 12px;
		fill: var(--text-2);
		font-variant-numeric: tabular-nums;
	}
	.sub {
		font-family: var(--font-mono);
		font-size: 10px;
		fill: var(--text-3);
	}
</style>
