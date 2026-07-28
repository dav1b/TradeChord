<script lang="ts">
	import { usd } from '$lib/format';
	import { flowKey, partnerKey } from '$lib/explorer/entity';
	import type { PartnerRow } from '$lib/data/types';

	let {
		reporter,
		row,
		progress,
		onclose
	}: {
		reporter: string;
		row: PartnerRow;
		progress: number;
		onclose: () => void;
	} = $props();

	const total = $derived(row.exportsUsd + row.importsUsd);
	const exportShare = $derived(total ? row.exportsUsd / total : 0.5);
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
		<strong>{usd(total)}</strong>
	</header>
	<div class="flows" aria-label="{reporter} bilateral trade with {row.partner}">
		<div
			class="flow export"
			style:flex={Math.max(exportShare, 0.08)}
			data-entity-id={flowKey(reporter, row.partner, 'export')}
		>
			<span>Exports</span>
			<strong>{usd(row.exportsUsd)}</strong>
		</div>
		<div
			class="flow import"
			style:flex={Math.max(1 - exportShare, 0.08)}
			data-entity-id={flowKey(reporter, row.partner, 'import')}
		>
			<span>Imports</span>
			<strong>{usd(row.importsUsd)}</strong>
		</div>
	</div>
</section>

<style>
	.panel {
		position: absolute;
		z-index: 5;
		top: 50%;
		left: 50%;
		width: min(72%, 720px);
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
	header span,
	.flow span {
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
	header > strong {
		font-family: var(--font-mono);
		font-size: clamp(0.9rem, 1.6vw, 1.2rem);
	}
	.flows {
		display: flex;
		height: clamp(58px, 8vw, 82px);
	}
	.flow {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		min-width: 0;
		padding: 12px;
		color: var(--dj-carbon);
	}
	.flow strong {
		font-family: var(--font-mono);
		font-size: clamp(10px, 1.3vw, 14px);
	}
	.export {
		background: color-mix(in srgb, var(--delta-pos) 78%, var(--surface));
	}
	.import {
		background: color-mix(in srgb, var(--delta-neg) 72%, var(--surface));
	}
	@media (max-width: 640px) {
		.panel {
			top: 58%;
			width: calc(100% - 28px);
		}
		header {
			align-items: start;
			flex-direction: column;
			gap: 8px;
		}
		.flows {
			flex-direction: column;
			height: auto;
		}
	}
</style>
