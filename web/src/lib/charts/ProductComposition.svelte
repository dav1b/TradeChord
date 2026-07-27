<script lang="ts">
	import { hierarchy, treemap } from 'd3';
	import { fade } from 'svelte/transition';
	import { flowKey, productKey } from '$lib/explorer/entity';
	import {
		choreography,
		receiveEntity,
		sendEntity
	} from '$lib/explorer/scene-transitions';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import type { RectGeometry } from '$lib/explorer/geometry';
	import { useSceneViewport } from '$lib/explorer/scene-viewport.svelte';
	import { motionDuration } from '$lib/motion';
	import { pct, usd } from '$lib/format';
	import type { CrossCell, PartnerRow } from '$lib/data/types';

	let {
		reporter,
		year,
		row,
		cells
	}: {
		reporter: string;
		year: number;
		row: PartnerRow;
		cells: CrossCell[];
	} = $props();

	const explorer = useExplorer();
	const viewport = useSceneViewport();
	const height = $derived(viewport.mode === 'compact' ? 260 : viewport.mode === 'wide' ? 400 : 320);
	const timing = $derived(choreography(explorer.transition.direction));
	let width = $state(0);

	const flow = $derived(explorer.state.flow === 'import' ? 'import' : 'export');
	const flowLabel = $derived(flow === 'export' ? 'Reported exports' : 'Reported imports');
	const flowTotal = $derived(flow === 'export' ? row.exportsUsd : row.importsUsd);
	const available = $derived(flow === 'export' ? row.exportAvailable : row.importAvailable);
	const clean = (product: string) => product.replace(/^\d+-\d+_/, '');

	const products = $derived.by(() =>
		cells
			.filter((cell) => (flow === 'export' ? cell.exportAvailable : cell.importAvailable))
			.map((cell) => ({
				code: clean(cell.product),
				rawCode: cell.product,
				value: flow === 'export' ? cell.exportsUsd : cell.importsUsd
			}))
			.filter((product) => product.value > 0)
			.sort((a, b) => b.value - a.value)
	);
	const detailTotal = $derived(products.reduce((sum, product) => sum + product.value, 0));
	const coverage = $derived(flowTotal > 0 ? Math.min(1, detailTotal / flowTotal) : 0);

	interface ProductNode extends RectGeometry {
		data: (typeof products)[number];
		x0: number;
		y0: number;
		x1: number;
		y1: number;
	}

	const nodes = $derived.by((): ProductNode[] => {
		if (!width || !products.length) return [];
		// D3 owns layout only; Svelte owns and keys the rendered controls.
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const root: any = hierarchy({ children: products } as any)
			.sum((datum: any) => datum.value ?? 0)
			.sort((a: any, b: any) => (b.value ?? 0) - (a.value ?? 0));
		treemap().size([width, height]).paddingInner(3).round(true)(root);
		return (root.leaves() as ProductNode[]).map((node) => ({
			...node,
			x: node.x0,
			y: node.y0,
			width: node.x1 - node.x0,
			height: node.y1 - node.y0
		}));
	});

	function returnToRelationship() {
		explorer.setRepresentation('relationship');
	}

	function returnToNetwork() {
		explorer.setRepresentation('chord');
	}
</script>

<section
	class="composition"
	aria-labelledby="composition-title"
	tabindex="-1"
	data-entity-id={flowKey(reporter, row.partner, flow)}
>
	<nav class="trail" aria-label="Analytical path">
		<button onclick={returnToNetwork}>Network</button>
		<span aria-hidden="true">→</span>
		<button onclick={returnToRelationship}>{row.partner}</button>
		<span aria-hidden="true">→</span>
		<strong>{flow === 'export' ? 'Exports' : 'Imports'}</strong>
	</nav>

	<div class="heading">
		<div>
			<p class="kicker">{reporter} → {row.partner} · {year}</p>
			<h4 id="composition-title">{flowLabel} by product</h4>
		</div>
		<div class="total">
			<span>{available ? 'Bilateral total' : 'Flow status'}</span>
			<strong>{available ? usd(flowTotal) : 'Unavailable'}</strong>
		</div>
	</div>

	<div
		class:imports={flow === 'import'}
		class="flow-band"
		in:receiveEntity={{ key: flowKey(reporter, row.partner, flow) }}
		out:sendEntity={{ key: flowKey(reporter, row.partner, flow) }}
		aria-hidden="true"
	></div>

	{#if products.length}
		<p class="summary">
			{products.length} published product groups · {pct(coverage)} of the bilateral flow represented
		</p>
		<div class="treemap" bind:clientWidth={width} style:height="{height}px">
			{#each nodes as node, index (productKey(reporter, row.partner, flow, node.data.code))}
				{@const tileWidth = node.width}
				{@const tileHeight = node.height}
				{@const share = detailTotal ? node.data.value / detailTotal : 0}
				{@const selected = explorer.state.product === node.data.code}
				<button
					class:selected
					class:recessed={explorer.state.product != null && !selected}
					class:imports={flow === 'import'}
					style:left="{node.x}px"
					style:top="{node.y}px"
					style:width="{tileWidth}px"
					style:height="{tileHeight}px"
					data-entity-id={productKey(reporter, row.partner, flow, node.data.code)}
					aria-pressed={selected}
					aria-label="{node.data.code}, {usd(node.data.value)}, {pct(share)} of detailed {flow}s"
					onclick={() => explorer.selectRelationshipProduct(node.data.code)}
				>
					{#if tileWidth > 64 && tileHeight > 34}
						<span
							class="label"
							in:fade={{
								duration: motionDuration(180),
								delay: motionDuration(timing.label + index * 12)
							}}
						>
							<strong>{node.data.code}</strong>
							<small>{usd(node.data.value)} · {pct(share)}</small>
						</span>
					{/if}
				</button>
			{/each}
		</div>
	{:else}
		<div class="empty" role="status">
			Product detail is unavailable for this bilateral {flow} flow.
		</div>
	{/if}
</section>

<style>
	.composition {
		min-height: 320px;
		padding-top: var(--space-2);
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
	.treemap button:focus-visible {
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
	.total span,
	.summary {
		font-family: var(--font-mono);
		font-size: 9px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--text-4);
	}
	h4 {
		margin-top: 2px;
		font-size: 1.45rem;
		font-weight: 500;
		color: var(--text-1);
	}
	.total {
		text-align: right;
	}
	.total span,
	.total strong {
		display: block;
	}
	.total strong {
		font-size: 1.05rem;
		color: var(--text-1);
	}
	.flow-band {
		height: 12px;
		margin: var(--space-3) 0;
		border-radius: 2px;
		background: var(--delta-pos);
	}
	.flow-band.imports {
		background: var(--delta-neg);
	}
	.summary {
		margin-bottom: var(--space-3);
	}
	.treemap {
		position: relative;
		width: 100%;
	}
	.treemap button {
		position: absolute;
		overflow: hidden;
		border: 1px solid var(--border);
		border-left: 4px solid var(--delta-pos);
		padding: 8px;
		background: var(--pos-dim);
		color: var(--text-1);
		text-align: left;
		cursor: pointer;
		transition:
			opacity var(--motion) var(--ease),
			left var(--motion) var(--ease),
			top var(--motion) var(--ease),
			width var(--motion) var(--ease),
			height var(--motion) var(--ease);
	}
	.treemap button.imports {
		border-left-color: var(--delta-neg);
		background: var(--neg-dim);
	}
	.treemap button.selected {
		z-index: 1;
		border-color: var(--active);
		box-shadow: inset 0 0 0 1px var(--active);
	}
	.treemap button.recessed {
		opacity: 0.25;
	}
	.label {
		display: flex;
		flex-direction: column;
		gap: 3px;
	}
	.label strong {
		overflow: hidden;
		font-size: 11px;
		text-overflow: ellipsis;
	}
	.label small {
		font-family: var(--font-mono);
		font-size: 9px;
		color: var(--text-3);
	}
	.empty {
		display: grid;
		min-height: 220px;
		place-items: center;
		color: var(--text-3);
		font-size: 12px;
		text-align: center;
	}
	@media (max-width: 520px) {
		.heading {
			align-items: start;
		}
		h4 {
			font-size: 1.25rem;
		}
	}
</style>
