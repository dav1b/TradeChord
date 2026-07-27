<script lang="ts">
	import ChordChart from '$lib/charts/ChordChart.svelte';
	import RankedPartners from '$lib/charts/RankedPartners.svelte';
	import BilateralRelationship from '$lib/charts/BilateralRelationship.svelte';
	import ProductComposition from '$lib/charts/ProductComposition.svelte';
	import BilateralTimeline from '$lib/charts/BilateralTimeline.svelte';
	import SceneStage from '$lib/explorer/SceneStage.svelte';
	import { deriveTradeScene } from '$lib/explorer/scene-graph';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let {
		projection,
		year,
		topN = 9
	}: { projection: CountryProjection; year: number; topN?: number } = $props();
	const explorer = useExplorer();

	const graph = $derived(deriveTradeScene(projection, explorer.state, topN));
	const rows = $derived(graph.partners.map((entity) => entity.datum));
	const summary = $derived(projection.summaryByYear[String(year)]);
	const relationshipRow = $derived(graph.selectedPartner?.datum ?? null);
	const relationshipCells = $derived(graph.products.map((entity) => entity.datum));
</script>

<SceneStage {graph} transition={explorer.transition}>
	<div class="scene-controls" role="group" aria-label="Trade network representation">
		<button
			class:active={explorer.state.representation === 'chord'}
			aria-pressed={explorer.state.representation === 'chord'}
			onclick={() => explorer.setRepresentation('chord')}>Network</button
		>
		<button
			class:active={explorer.state.representation === 'rank'}
			aria-pressed={explorer.state.representation === 'rank'}
			onclick={() => explorer.setRepresentation('rank')}>Rank partners</button
		>
		{#if explorer.state.partner}
			<button
				class:active={explorer.state.representation === 'relationship'}
				aria-pressed={explorer.state.representation === 'relationship'}
				onclick={() => explorer.setRepresentation('relationship')}>Relationship</button
			>
		{/if}
		{#if explorer.state.partner && explorer.state.flow !== 'both'}
			<button
				class:active={explorer.state.representation === 'products'}
				aria-pressed={explorer.state.representation === 'products'}
				onclick={() => explorer.setRepresentation('products')}>Products</button
			>
		{/if}
		{#if explorer.state.partner}
			<button
				class:active={explorer.state.representation === 'history'}
				aria-pressed={explorer.state.representation === 'history'}
				onclick={() => explorer.setRepresentation('history')}>History</button
			>
		{/if}
	</div>

	<div class="scene">
		{#if explorer.state.representation === 'history' && explorer.state.partner}
			<BilateralTimeline
				reporter={projection.country}
				partner={explorer.state.partner}
				points={graph.history}
			/>
		{:else if explorer.state.representation === 'products' && relationshipRow}
			<ProductComposition
				reporter={projection.country}
				year={projection.crossYear ?? year}
				row={relationshipRow}
				cells={relationshipCells}
			/>
		{:else if explorer.state.representation === 'relationship' && relationshipRow}
			<BilateralRelationship reporter={projection.country} {year} row={relationshipRow} />
		{:else if explorer.state.representation === 'chord'}
			<ChordChart reporter={projection.country} {year} {rows} reporterSummary={summary} />
		{:else}
			<RankedPartners reporter={projection.country} {rows} />
		{/if}
	</div>
</SceneStage>

<style>
	.scene-controls {
		display: inline-flex;
		padding: 3px;
		border: 1px solid var(--border);
		border-radius: 999px;
		background: var(--surface-subtle, var(--dj-alabaster));
	}
	.scene-controls button {
		border: 0;
		border-radius: 999px;
		padding: 5px 10px;
		background: transparent;
		color: var(--text-3);
		font-family: var(--font-mono);
		font-size: 9px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		cursor: pointer;
	}
	.scene-controls button.active {
		background: var(--active);
		color: var(--active-ink);
	}
	.scene-controls button:focus-visible {
		outline: 2px solid var(--active);
		outline-offset: 2px;
	}
	.scene {
		min-height: 340px;
	}
</style>
