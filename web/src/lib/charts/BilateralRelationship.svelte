<script lang="ts">
	import { fade, fly } from 'svelte/transition';
	import { partnerKey, flowKey } from '$lib/explorer/entity';
	import { receiveEntity, sendEntity } from '$lib/explorer/scene-transitions';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import { motionDuration } from '$lib/motion';
	import { usd, usdSigned } from '$lib/format';
	import type { PartnerRow } from '$lib/data/types';

	let {
		reporter,
		year,
		row
	}: {
		reporter: string;
		year: number;
		row: PartnerRow;
	} = $props();

	const explorer = useExplorer();
	const total = $derived(row.exportsUsd + row.importsUsd);
	const maximum = $derived(Math.max(row.exportsUsd, row.importsUsd, 1));
	const exportFraction = $derived(total ? row.exportsUsd / total : 0);

	function returnToNetwork() {
		explorer.setRepresentation('chord');
	}
</script>

<section class="relationship" aria-labelledby="relationship-title">
	<nav class="trail" aria-label="Analytical path">
		<button onclick={returnToNetwork}>← Network</button>
		<span>{reporter}</span>
		<span aria-hidden="true">→</span>
		<strong>{row.partner}</strong>
	</nav>

	<div class="heading">
		<div>
			<p class="kicker">Bilateral relationship · {year}</p>
			<h4 id="relationship-title">{reporter} ↔ {row.partner}</h4>
		</div>
		<div class="total">
			<span>Total trade</span>
			<strong>{usd(total)}</strong>
		</div>
	</div>

	<div
		class="relationship-band"
		in:receiveEntity={{ key: partnerKey(reporter, row.partner) }}
		out:sendEntity={{ key: partnerKey(reporter, row.partner) }}
		aria-hidden="true"
	>
		<span class="export-segment" style:width={`${exportFraction * 100}%`}></span>
		<span class="import-segment"></span>
	</div>

	<div class="flows">
		<div
			class="flow"
			in:fly={{ y: 10, duration: motionDuration(260), delay: motionDuration(180) }}
			out:fade={{ duration: motionDuration(100) }}
		>
			<div class="flow-head">
				<span>Reported exports</span>
				<strong>{row.exportAvailable ? usd(row.exportsUsd) : 'Unavailable'}</strong>
			</div>
			<div class="track">
				<span
					class="export-bar"
					style:width={`${(row.exportsUsd / maximum) * 100}%`}
					data-entity-id={flowKey(reporter, row.partner, 'export')}
				></span>
			</div>
			<p>{reporter} reported exports to {row.partner}</p>
		</div>

		<div
			class="flow"
			in:fly={{ y: 10, duration: motionDuration(260), delay: motionDuration(260) }}
			out:fade={{ duration: motionDuration(100) }}
		>
			<div class="flow-head">
				<span>Reported imports</span>
				<strong>{row.importAvailable ? usd(row.importsUsd) : 'Unavailable'}</strong>
			</div>
			<div class="track">
				<span
					class="import-bar"
					style:width={`${(row.importsUsd / maximum) * 100}%`}
					data-entity-id={flowKey(reporter, row.partner, 'import')}
				></span>
			</div>
			<p>{reporter} reported imports from {row.partner}</p>
		</div>
	</div>

	<div
		class:positive={(row.balanceUsd ?? 0) >= 0}
		class:unavailable={row.balanceUsd == null}
		class="balance"
		in:fade={{ duration: motionDuration(180), delay: motionDuration(480) }}
	>
		<span>Reported balance</span>
		<strong>{row.balanceUsd == null ? 'Unavailable' : usdSigned(row.balanceUsd)}</strong>
		<p>Exports minus imports for {reporter} in {year}</p>
	</div>
</section>

<style>
	.relationship {
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
	.trail button:focus-visible {
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
	.flow-head span,
	.balance > span {
		font-family: var(--font-mono);
		font-size: 9px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--text-4);
	}
	h4 {
		margin-top: 2px;
		font-size: 1.7rem;
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
		font-size: 1.15rem;
		color: var(--text-1);
	}
	.relationship-band {
		display: flex;
		height: 18px;
		margin: var(--space-4) 0 var(--space-5);
		overflow: hidden;
		border-radius: 2px;
		background: var(--dj-alabaster);
	}
	.export-segment,
	.export-bar {
		background: var(--delta-pos);
	}
	.import-segment,
	.import-bar {
		background: var(--delta-neg);
	}
	.import-segment {
		flex: 1;
	}
	.flows {
		display: grid;
		gap: var(--space-4);
	}
	.flow-head {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: var(--space-3);
	}
	.flow-head strong {
		font-size: 1rem;
		color: var(--text-1);
	}
	.track {
		height: 11px;
		margin-top: 5px;
		background: var(--surface-subtle, var(--dj-alabaster));
		overflow: hidden;
	}
	.track span {
		display: block;
		height: 100%;
		min-width: 2px;
	}
	.flow p,
	.balance p {
		margin-top: 4px;
		font-size: 10px;
		color: var(--text-4);
	}
	.balance {
		margin-top: var(--space-5);
		padding-top: var(--space-3);
		border-top: 1px solid var(--border-faint);
	}
	.balance > span,
	.balance > strong {
		display: block;
	}
	.balance > strong {
		margin-top: 2px;
		color: var(--delta-neg);
		font-size: 1.15rem;
	}
	.balance.positive > strong {
		color: var(--delta-pos);
	}
	.balance.unavailable > strong {
		color: var(--text-4);
	}
	@media (max-width: 520px) {
		.heading {
			align-items: start;
		}
		h4 {
			font-size: 1.4rem;
		}
	}
</style>
