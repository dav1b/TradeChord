<script lang="ts">
	// Exports − Imports = Balance, the page's number-led headline (04/05-*.md).
	// Balance carries the teal/ember delta colour; exports/imports stay ink.
	import Stat from '$lib/ui/Stat.svelte';
	import { usd, usdSigned } from '$lib/format';
	import { deltaColor } from '$lib/theme/tokens';
	import type { FlowSummary } from '$lib/data/types';

	let {
		year,
		summary,
		source
	}: {
		year: number;
		summary: FlowSummary;
		source: string;
	} = $props();
</script>

<div class="hero">
	<Stat size="lg" value={usd(summary.exportsUsd)} label="Exports" />
	<div class="op" aria-hidden="true">−</div>
	<Stat size="lg" value={usd(summary.importsUsd)} label="Imports" />
	<div class="op" aria-hidden="true">=</div>
	<Stat
		size="lg"
		value={usdSigned(summary.balanceUsd)}
		valueColor={deltaColor(summary.balanceUsd)}
		label="Balance"
		delta={summary.balanceUsd >= 0 ? 'Surplus' : 'Deficit'}
		deltaColor={deltaColor(summary.balanceUsd)}
		{source}
	/>
</div>

<style>
	.hero {
		display: flex;
		align-items: flex-start;
		gap: var(--space-5);
		flex-wrap: wrap;
	}
	.op {
		font-size: 2rem;
		font-weight: 300;
		color: var(--text-3);
		line-height: 1.4;
		align-self: center;
	}
	@media (max-width: 640px) {
		.hero {
			gap: var(--space-4);
		}
		.op {
			font-size: 1.5rem;
		}
	}
</style>
