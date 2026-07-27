<script lang="ts">
	import ChordChart from '$lib/charts/ChordChart.svelte';
	import RankedPartners from '$lib/charts/RankedPartners.svelte';
	import BilateralRelationship from '$lib/charts/BilateralRelationship.svelte';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let {
		projection,
		year,
		topN = 9
	}: { projection: CountryProjection; year: number; topN?: number } = $props();
	const explorer = useExplorer();

	// Top bilateral partners by total trade (exports + imports), plus ROW.
	const rows = $derived.by(() => {
		const all = projection.partnersByYear[String(year)] ?? [];
		const named = all
			.filter((p) => p.partner !== 'ROW' && p.exportAvailable && p.importAvailable)
			.slice()
			.sort((a, b) => b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd))
			.slice(0, topN);
		const row = all.find((p) => p.partner === 'ROW');
		return row ? [...named, row] : named;
	});

	const summary = $derived(projection.summaryByYear[String(year)]);
	const relationshipRow = $derived(
		(projection.partnersByYear[String(year)] ?? []).find(
			(row) => row.partner === explorer.state.partner
		) ?? null
	);
</script>

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
</div>

<div class="scene" aria-live="polite">
	{#if explorer.state.representation === 'relationship' && relationshipRow}
		<BilateralRelationship
			reporter={projection.country}
			{year}
			row={relationshipRow}
		/>
	{:else if explorer.state.representation === 'chord'}
		<ChordChart reporter={projection.country} {year} {rows} reporterSummary={summary} />
	{:else}
		<RankedPartners reporter={projection.country} {rows} />
	{/if}
</div>

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
