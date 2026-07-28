<script lang="ts">
	import BilateralHistory from '$lib/charts/motion/BilateralHistory.svelte';
	import DualProductTreemap from '$lib/charts/motion/DualProductTreemap.svelte';
	import type { RelationshipHistoryPoint } from '$lib/charts/motion/relationship-types';
	import { usd, usdSigned } from '$lib/format';
	import { flowKey, partnerKey } from '$lib/explorer/entity';
	import type { CrossCell, PartnerRow } from '$lib/data/types';

	let {
		reporter,
		row,
		history,
		products,
		crossYear,
		progress,
		onclose
	}: {
		reporter: string;
		row: PartnerRow;
		history: RelationshipHistoryPoint[];
		products: CrossCell[];
		crossYear: number | null;
		progress: number;
		onclose: () => void;
	} = $props();

	let preview = $state<RelationshipHistoryPoint | null>(null);
	const total = $derived(row.exportsUsd + row.importsUsd);
	const exportsUsd = $derived(preview?.exportsUsd ?? row.exportsUsd);
	const importsUsd = $derived(preview?.importsUsd ?? row.importsUsd);
	const balanceUsd = $derived(preview?.balanceUsd ?? row.balanceUsd);
	const displayYear = $derived(preview?.year ?? crossYear);
</script>

<section
	class="panel"
	class:visible={progress > 0.02}
	style:--panel-progress={progress}
	data-entity-id={partnerKey(reporter, row.partner)}
	aria-hidden={progress < 0.98}
	aria-label="{reporter} relationship with {row.partner}"
>
	<button class="back" onclick={onclose} aria-label="Return {row.partner} to the trade network">
		← Network
	</button>
	<header>
		<div>
			<span>Bilateral relationship</span>
			<h2>{reporter} ↔ {row.partner}</h2>
		</div>
		<div class="headline">
			<strong>{usd(total)}</strong>
			<span>{displayYear ?? 'Latest available year'}</span>
		</div>
	</header>
	<div class="equation" aria-label="{reporter} bilateral trade balance with {row.partner}">
		<div
			class="measure export"
			data-entity-id={flowKey(reporter, row.partner, 'export')}
		>
			<span>Reported exports</span>
			<strong>{usd(exportsUsd)}</strong>
		</div>
		<span class="operator" aria-hidden="true">−</span>
		<div
			class="measure import"
			data-entity-id={flowKey(reporter, row.partner, 'import')}
		>
			<span>Reported imports</span>
			<strong>{usd(importsUsd)}</strong>
		</div>
		<span class="operator" aria-hidden="true">=</span>
		<div class="measure balance">
			<span>Reported balance</span>
			<strong class:negative={(balanceUsd ?? 0) < 0}>
				{balanceUsd == null ? 'Unavailable' : usdSigned(balanceUsd)}
			</strong>
		</div>
	</div>
	<DualProductTreemap
		{reporter}
		partner={row.partner}
		year={crossYear}
		cells={products}
	/>
	<BilateralHistory
		{reporter}
		partner={row.partner}
		points={history}
		onpreview={(point) => (preview = point)}
	/>
</section>

<style>
	.panel {
		position: absolute;
		z-index: 5;
		top: 54%;
		left: 50%;
		width: min(82%, 1080px);
		max-height: min(78%, 760px);
		overflow: auto;
		padding: clamp(16px, 2.4vw, 28px);
		border: 1px solid color-mix(in srgb, var(--dj-carbon) 24%, transparent);
		background: color-mix(in srgb, var(--surface) 97%, transparent);
		opacity: var(--panel-progress);
		transform: translate(-50%, -50%)
			translateY(calc((1 - var(--panel-progress)) * 24px))
			scale(calc(0.94 + var(--panel-progress) * 0.06));
		pointer-events: none;
	}
	.panel.visible {
		pointer-events: auto;
	}
	.back {
		border: 0;
		padding: 0;
		background: transparent;
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-3);
		cursor: pointer;
	}
	.back:focus-visible {
		outline: 2px solid var(--active);
		outline-offset: 3px;
	}
	header {
		display: flex;
		align-items: end;
		justify-content: space-between;
		gap: 16px;
		margin: 18px 0 22px;
	}
	header span {
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-3);
	}
	h2 {
		margin-top: 4px;
		font-family: var(--font-head);
		font-size: clamp(1.5rem, 3.6vw, 3rem);
		font-weight: 500;
		color: var(--text-1);
	}
	.headline {
		display: grid;
		justify-items: end;
		gap: 3px;
	}
	.headline strong {
		font-family: var(--font-mono);
		font-size: clamp(0.9rem, 1.6vw, 1.2rem);
	}
	.headline span {
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-3);
	}
	.equation {
		display: grid;
		grid-template-columns: 1fr auto 1fr auto 1fr;
		align-items: stretch;
		margin-bottom: 18px;
	}
	.measure {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		gap: 8px;
		min-width: 0;
		padding: 12px;
		color: var(--dj-carbon);
	}
	.measure span {
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
	}
	.measure strong {
		font-family: var(--font-mono);
		font-size: clamp(10px, 1.3vw, 14px);
	}
	.measure strong.negative {
		color: var(--delta-neg);
	}
	.operator {
		align-self: center;
		padding: 0 9px;
		font-family: var(--font-head);
		font-size: 1.35rem;
		color: var(--text-3);
	}
	.export {
		background: color-mix(in srgb, var(--delta-pos) 78%, var(--surface));
	}
	.import {
		background: color-mix(in srgb, var(--delta-neg) 72%, var(--surface));
	}
	.balance {
		border: 1px solid var(--border);
		background: var(--surface);
	}
	@media (max-width: 640px) {
		.panel {
			top: 62%;
			width: calc(100% - 28px);
			max-height: 72%;
		}
		header {
			align-items: start;
			flex-direction: column;
			gap: 8px;
		}
		.headline {
			justify-items: start;
		}
		.equation {
			grid-template-columns: 1fr;
		}
		.operator {
			display: none;
		}
	}
</style>
