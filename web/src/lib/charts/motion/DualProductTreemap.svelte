<script lang="ts">
	import { hierarchy, treemap } from 'd3';
	import { productKey } from '$lib/explorer/entity';
	import { pct, usd } from '$lib/format';
	import type { CrossCell } from '$lib/data/types';

	let {
		reporter,
		partner,
		year,
		cells
	}: {
		reporter: string;
		partner: string;
		year: number | null;
		cells: CrossCell[];
	} = $props();

	let exportWidth = $state(0);
	let importWidth = $state(0);
	let hovered = $state<string | null>(null);
	let selected = $state<string | null>(null);
	const height = 210;
	const palette = [
		'var(--dj-lagoon-teal)',
		'var(--dj-ember-copper)',
		'var(--dj-honey-bronze)',
		'var(--dj-fern-green)',
		'var(--dj-plum-violet)',
		'var(--dj-navy)'
	];

	type Flow = 'export' | 'import';
	type Item = { product: string; value: number; cell: CrossCell; color: string };
	type Node = { data: Item; x0: number; y0: number; x1: number; y1: number };

	const rankedProducts = $derived(
		cells
			.slice()
			.sort(
				(a, b) =>
					b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd)
			)
			.map((cell) => cell.product)
	);
	const colorByProduct = $derived(
		new Map(rankedProducts.map((product, index) => [product, palette[index % palette.length]]))
	);
	const exportTotal = $derived(cells.reduce((total, cell) => total + cell.exportsUsd, 0));
	const importTotal = $derived(cells.reduce((total, cell) => total + cell.importsUsd, 0));
	const active = $derived(selected ?? hovered);

	function items(flow: Flow): Item[] {
		return cells
			.map((cell) => ({
				product: cell.product,
				value: flow === 'export' ? cell.exportsUsd : cell.importsUsd,
				cell,
				color: colorByProduct.get(cell.product) ?? palette[0]
			}))
			.filter((item) => item.value > 0);
	}

	function nodes(flow: Flow, width: number): Node[] {
		if (!width) return [];
		const root = hierarchy<{ children?: Item[]; value?: number }>({ children: items(flow) })
			.sum((item) => item.value ?? 0)
			.sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
		treemap<{ children?: Item[]; value?: number }>()
			.size([width, height])
			.paddingInner(2)
			.round(true)(root);
		return root.leaves() as unknown as Node[];
	}

	const exportNodes = $derived(nodes('export', exportWidth));
	const importNodes = $derived(nodes('import', importWidth));

	function toggle(product: string) {
		selected = selected === product ? null : product;
	}

	function keyTile(event: KeyboardEvent, product: string) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			toggle(product);
		}
		if (event.key === 'Escape') selected = null;
	}
</script>

<section class="dual" aria-label="{partner} product composition in {year ?? 'the release year'}">
	<header>
		<div>
			<span>Product composition · {year ?? 'headline year'}</span>
			<h3>What does this relationship trade?</h3>
		</div>
		{#if active}
			<strong>{active}</strong>
		{/if}
	</header>
	<div class="maps">
		<div class="map">
			<div class="map-head"><span>Reported exports</span><strong>{usd(exportTotal)}</strong></div>
			<div class="map-canvas" bind:clientWidth={exportWidth} style:height="{height}px">
				<svg width={exportWidth} {height} aria-label="Export products">
					{#each exportNodes as node (node.data.product)}
						{@const w = node.x1 - node.x0}
						{@const h = node.y1 - node.y0}
						{@const recessed = active != null && active !== node.data.product}
						<g
							class="tile"
							class:selected={selected === node.data.product}
							transform="translate({node.x0},{node.y0})"
							opacity={recessed ? 0.2 : 1}
							role="button"
							tabindex="0"
							aria-pressed={selected === node.data.product}
							aria-label="{node.data.product}, exports {usd(node.data.value)}"
							data-entity-id={productKey(reporter, partner, 'export', node.data.product)}
							onmouseenter={() => (hovered = node.data.product)}
							onmouseleave={() => (hovered = null)}
							onfocus={() => (hovered = node.data.product)}
							onblur={() => (hovered = null)}
							onclick={() => toggle(node.data.product)}
							onkeydown={(event) => keyTile(event, node.data.product)}
						>
							<rect width={w} height={h} fill={node.data.color} />
							{#if w > 58 && h > 34}
								<text x="7" y="16">{node.data.product}</text>
								<text class="value" x="7" y="31">
									{pct(node.data.value / Math.max(exportTotal, 1))}
								</text>
							{/if}
							<title>{node.data.product}: {usd(node.data.value)}</title>
						</g>
					{/each}
				</svg>
			</div>
		</div>

		<div class="map">
			<div class="map-head"><span>Reported imports</span><strong>{usd(importTotal)}</strong></div>
			<div class="map-canvas" bind:clientWidth={importWidth} style:height="{height}px">
				<svg width={importWidth} {height} aria-label="Import products">
					{#each importNodes as node (node.data.product)}
						{@const w = node.x1 - node.x0}
						{@const h = node.y1 - node.y0}
						{@const recessed = active != null && active !== node.data.product}
						<g
							class="tile"
							class:selected={selected === node.data.product}
							transform="translate({node.x0},{node.y0})"
							opacity={recessed ? 0.2 : 1}
							role="button"
							tabindex="0"
							aria-pressed={selected === node.data.product}
							aria-label="{node.data.product}, imports {usd(node.data.value)}"
							data-entity-id={productKey(reporter, partner, 'import', node.data.product)}
							onmouseenter={() => (hovered = node.data.product)}
							onmouseleave={() => (hovered = null)}
							onfocus={() => (hovered = node.data.product)}
							onblur={() => (hovered = null)}
							onclick={() => toggle(node.data.product)}
							onkeydown={(event) => keyTile(event, node.data.product)}
						>
							<rect width={w} height={h} fill={node.data.color} />
							{#if w > 58 && h > 34}
								<text x="7" y="16">{node.data.product}</text>
								<text class="value" x="7" y="31">
									{pct(node.data.value / Math.max(importTotal, 1))}
								</text>
							{/if}
							<title>{node.data.product}: {usd(node.data.value)}</title>
						</g>
					{/each}
				</svg>
			</div>
		</div>
	</div>
	<p class="note">Equal areas compare composition within each flow; headline totals compare magnitude.</p>
</section>

<style>
	.dual {
		border-top: 1px solid var(--border-faint);
		padding-top: 16px;
	}
	header,
	.map-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 12px;
	}
	header {
		margin-bottom: 12px;
	}
	header span,
	.map-head span,
	.note {
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-3);
	}
	h3 {
		margin-top: 3px;
		font-size: clamp(1rem, 1.7vw, 1.35rem);
		font-weight: 500;
	}
	header > strong,
	.map-head strong {
		font-family: var(--font-mono);
		font-size: 11px;
	}
	.maps {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 12px;
	}
	.map-head {
		margin-bottom: 5px;
	}
	.map-canvas,
	svg {
		width: 100%;
		display: block;
	}
	.tile {
		cursor: pointer;
		transition: opacity var(--motion-fast) var(--ease);
	}
	.tile rect {
		stroke: color-mix(in srgb, var(--surface) 82%, transparent);
		stroke-width: 1;
	}
	.tile.selected rect {
		stroke: var(--dj-carbon);
		stroke-width: 3;
	}
	.tile:focus {
		outline: none;
	}
	.tile text {
		font-family: var(--font-mono);
		font-size: 9px;
		fill: var(--dj-carbon);
		pointer-events: none;
	}
	.tile .value {
		font-size: 8px;
	}
	.note {
		margin-top: 7px;
		text-transform: none;
	}
	@media (max-width: 640px) {
		.maps {
			grid-template-columns: 1fr;
		}
	}
</style>
