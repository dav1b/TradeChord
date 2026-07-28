<script lang="ts">
	import { usd } from '$lib/format';
	import { flowKey, partnerKey } from '$lib/explorer/entity';
	import type { PartnerRow } from '$lib/data/types';

	let {
		reporter,
		row,
		width,
		height,
		progress,
		onclose
	}: {
		reporter: string;
		row: PartnerRow;
		width: number;
		height: number;
		progress: number;
		onclose: () => void;
	} = $props();

	const compact = $derived(width < 640);
	const bandWidth = $derived(compact ? Math.min(width * 0.92, 520) : Math.min(width * 0.44, 620));
	const bandHeight = $derived(width < 560 ? 96 : 116);
	const startX = $derived((width - bandWidth) / 2);
	const startY = $derived((height - bandHeight) / 2);
	const targetX = $derived(compact ? (width - bandWidth) / 2 : width * 0.055);
	const targetY = $derived(compact ? 18 : Math.max(28, height * 0.08));
	const x = $derived(startX + (targetX - startX) * progress);
	const y = $derived(startY + (targetY - startY) * progress);
	const contentProgress = $derived(Math.max(0, Math.min(1, (progress - 0.42) / 0.58)));
	const total = $derived(row.exportsUsd + row.importsUsd);
	const exportShare = $derived(total ? row.exportsUsd / total : 0.5);
	const ribbonColor = $derived(
		row.partner === 'ROW' || row.balanceUsd == null
			? 'var(--dj-alabaster)'
			: row.balanceUsd >= 0
				? 'var(--delta-pos)'
				: 'var(--delta-neg)'
	);
</script>

<div
	class="bridge"
	class:visible={progress > 0.02}
	style:--bridge-progress={progress}
	style:--content-progress={contentProgress}
	style:--bridge-x="{x}px"
	style:--bridge-y="{y}px"
	style:--bridge-width="{bandWidth}px"
	style:--bridge-height="{bandHeight}px"
	style:--ribbon-color={ribbonColor}
	data-entity-id={partnerKey(reporter, row.partner)}
	aria-hidden={progress < 0.98}
>
	<div class="ribbon-surrogate" aria-hidden="true"></div>
	<button class="back" onclick={onclose} aria-label="Return {row.partner} to the trade network">
		← Network
	</button>
	<div class="identity">
		<span>{reporter}</span>
		<strong>{row.partner}</strong>
		<em>{usd(total)}</em>
	</div>
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
</div>

<style>
	.bridge {
		position: absolute;
		z-index: 4;
		left: var(--bridge-x);
		top: var(--bridge-y);
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		grid-template-rows: auto 1fr;
		gap: 8px 18px;
		width: var(--bridge-width);
		height: var(--bridge-height);
		padding: 12px 14px;
		background: color-mix(in srgb, var(--surface) 94%, transparent);
		border: 1px solid color-mix(in srgb, var(--dj-carbon) 22%, transparent);
		opacity: var(--bridge-progress);
		transform: translateY(calc((1 - var(--bridge-progress)) * 36px))
			scaleX(calc(0.72 + var(--bridge-progress) * 0.28))
			scaleY(calc(0.16 + var(--content-progress) * 0.84));
		transform-origin: center;
		pointer-events: none;
	}
	.ribbon-surrogate {
		position: absolute;
		inset: 0;
		z-index: 0;
		background: var(--ribbon-color);
		opacity: calc(1 - var(--content-progress));
	}
	.back,
	.identity,
	.flows {
		position: relative;
		z-index: 1;
	}
	.bridge.visible {
		pointer-events: auto;
	}
	.back {
		align-self: start;
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
	.identity {
		display: flex;
		align-items: baseline;
		justify-content: flex-end;
		gap: 9px;
		opacity: var(--content-progress);
		transform: translateY(calc((1 - var(--content-progress)) * 8px));
	}
	.identity span,
	.identity em,
	.flow span {
		font-family: var(--font-mono);
		font-size: 9px;
		font-style: normal;
		text-transform: uppercase;
		color: var(--text-3);
	}
	.identity strong {
		font-family: var(--font-head);
		font-size: clamp(1.25rem, 2.6vw, 2rem);
		font-weight: 500;
	}
	.flows {
		grid-column: 1 / -1;
		display: flex;
		min-width: 0;
		height: 42px;
		opacity: var(--content-progress);
		transform: scaleX(calc(0.82 + var(--content-progress) * 0.18));
		transform-origin: left;
	}
	.flow {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		min-width: 0;
		padding: 8px 10px;
		color: var(--dj-carbon);
	}
	.flow strong {
		font-family: var(--font-mono);
		font-size: clamp(10px, 1.2vw, 13px);
	}
	.export {
		background: color-mix(in srgb, var(--delta-pos) 78%, var(--surface));
	}
	.import {
		background: color-mix(in srgb, var(--delta-neg) 72%, var(--surface));
	}
	@media (max-width: 560px) {
		.bridge {
			grid-template-columns: 1fr;
			grid-template-rows: auto auto 1fr;
			gap: 5px;
			padding: 10px;
		}
		.identity {
			justify-content: space-between;
		}
		.flows {
			grid-column: 1;
		}
		.flow {
			padding-inline: 7px;
		}
		.flow span {
			display: none;
		}
	}
</style>
