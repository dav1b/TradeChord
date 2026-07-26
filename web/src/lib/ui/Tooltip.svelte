<script lang="ts">
	// The one tooltip, identical everywhere: context breadcrumb, focal title, and the
	// exports − imports = balance equation for the intersection.
	import { usd, usdSigned, pct } from '$lib/format';
	import { deltaColor } from '$lib/theme/tokens';
	import { tipContext, tipTitle, type TradePoint } from './tradepoint.svelte';

	let { point }: { point: TradePoint } = $props();
</script>

<div class="tt">
	<div class="ctx">{tipContext(point)}</div>
	<div class="title">{tipTitle(point)}</div>
	<dl class="eq">
		<dt>Exports</dt>
		<dd>{usd(point.exportsUsd)}</dd>
		<dt>Imports</dt>
		<dd>{usd(point.importsUsd)}</dd>
		<dt class="bal">Balance</dt>
		<dd class="bal" style:color={deltaColor(point.balanceUsd)}>{usdSigned(point.balanceUsd)}</dd>
	</dl>
	{#if point.share != null}
		<div class="share">{pct(point.share)} of {point.shareOf ?? 'exports'}</div>
	{/if}
</div>

<style>
	.tt {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: var(--space-3);
		min-width: 180px;
		max-width: 260px;
	}
	.ctx {
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--text-3);
	}
	.title {
		font-size: 1.05rem;
		font-weight: 500;
		color: var(--text-1);
		margin: 2px 0 8px;
	}
	.eq {
		display: grid;
		grid-template-columns: 1fr auto;
		gap: 3px 16px;
		align-items: baseline;
		margin: 0;
	}
	dt {
		font-size: 12px;
		color: var(--text-3);
	}
	dd {
		margin: 0;
		font-size: 12px;
		color: var(--text-2);
		font-variant-numeric: tabular-nums;
		text-align: right;
	}
	.bal {
		font-weight: 600;
		border-top: 1px solid var(--border-faint);
		padding-top: 4px;
		margin-top: 2px;
	}
	dt.bal {
		color: var(--text-2);
	}
	.share {
		margin-top: 8px;
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--text-3);
	}
</style>
