<script lang="ts">
	import { flip } from 'svelte/animate';
	import { fade } from 'svelte/transition';
	import { partnerKey } from '$lib/explorer/entity';
	import { receiveEntity, sendEntity } from '$lib/explorer/scene-transitions';
	import { motionDuration } from '$lib/motion';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import { usd } from '$lib/format';
	import type { PartnerRow } from '$lib/data/types';

	let { reporter, rows }: { reporter: string; rows: PartnerRow[] } = $props();
	const explorer = useExplorer();

	const ranked = $derived.by(() =>
		rows.slice().sort((a, b) => {
			if (a.partner === explorer.state.partner) return -1;
			if (b.partner === explorer.state.partner) return 1;
			if (a.partner === 'ROW') return 1;
			if (b.partner === 'ROW') return -1;
			return b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd);
		})
	);
	const maximum = $derived(
		Math.max(1, ...ranked.map((row) => row.exportsUsd + row.importsUsd))
	);

	function activate(row: PartnerRow) {
		if (row.partner !== 'ROW') explorer.selectPartner(row.partner);
	}

	function keyActivate(event: KeyboardEvent, row: PartnerRow) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			activate(row);
		}
	}
</script>

<ol class="ranking" aria-label="Partners ranked by total trade">
	{#each ranked as row, index (partnerKey(reporter, row.partner))}
		{@const total = row.exportsUsd + row.importsUsd}
		{@const selected = explorer.state.partner === row.partner}
		<li
			class:selected
			class:recessed={explorer.state.partner != null && !selected}
			animate:flip={{ duration: motionDuration(420) }}
		>
			<button
				onclick={() => activate(row)}
				onkeydown={(event) => keyActivate(event, row)}
				disabled={row.partner === 'ROW'}
				data-entity-id={partnerKey(reporter, row.partner)}
				aria-pressed={selected}
				aria-label="{row.partner}, rank {index + 1}, total trade {usd(total)}"
			>
				<span class="rank">{String(index + 1).padStart(2, '0')}</span>
				<span class="name">{row.partner === 'ROW' ? 'Other countries' : row.partner}</span>
				<span class="value">{usd(total)}</span>
				<span
					class="bar"
					style:width={`${Math.max(2, (total / maximum) * 100)}%`}
					in:receiveEntity={{ key: partnerKey(reporter, row.partner) }}
					out:sendEntity={{ key: partnerKey(reporter, row.partner) }}
				>
					<span
						class="exports"
						style:width={`${total ? (row.exportsUsd / total) * 100 : 0}%`}
					></span>
					<span class="imports"></span>
				</span>
				<span class="shares" in:fade={{ duration: motionDuration(180), delay: motionDuration(360) }}>
					<span>EX {total ? Math.round((row.exportsUsd / total) * 100) : 0}%</span>
					<span>IM {total ? Math.round((row.importsUsd / total) * 100) : 0}%</span>
				</span>
			</button>
		</li>
	{/each}
</ol>

<div class="legend" aria-hidden="true">
	<span><i class="export-key"></i>Exports</span>
	<span><i class="import-key"></i>Imports</span>
</div>

<style>
	.ranking {
		list-style: none;
		margin: 0;
		padding: var(--space-2) 0 0;
		display: flex;
		flex-direction: column;
		gap: 7px;
		min-height: 300px;
	}
	li {
		transition: opacity var(--motion) var(--ease);
	}
	li.recessed {
		opacity: 0.28;
	}
	button {
		position: relative;
		width: 100%;
		min-height: 25px;
		display: grid;
		grid-template-columns: 28px 76px 72px 1fr;
		align-items: center;
		gap: var(--space-2);
		border: 0;
		padding: 0;
		background: transparent;
		color: var(--text-2);
		text-align: left;
		cursor: pointer;
	}
	button:disabled {
		cursor: default;
	}
	button:focus-visible {
		outline: 2px solid var(--active);
		outline-offset: 3px;
	}
	.rank,
	.value,
	.shares {
		font-family: var(--font-mono);
		font-size: 10px;
	}
	.rank {
		color: var(--text-4);
	}
	.name {
		font-weight: 600;
		color: var(--text-1);
	}
	.value {
		text-align: right;
		color: var(--text-3);
	}
	.bar {
		height: 12px;
		display: flex;
		overflow: hidden;
		border-radius: 2px;
		background: var(--dj-alabaster);
		transform-origin: left center;
	}
	.exports {
		height: 100%;
		background: var(--delta-pos);
	}
	.imports {
		flex: 1;
		background: var(--delta-neg);
	}
	.shares {
		position: absolute;
		right: 4px;
		display: flex;
		gap: 8px;
		color: var(--text-4);
		mix-blend-mode: multiply;
		pointer-events: none;
	}
	.selected .name {
		color: var(--active);
	}
	.legend {
		display: flex;
		justify-content: flex-end;
		gap: var(--space-3);
		margin-top: var(--space-2);
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-4);
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 5px;
	}
	.legend i {
		width: 14px;
		height: 5px;
	}
	.export-key {
		background: var(--delta-pos);
	}
	.import-key {
		background: var(--delta-neg);
	}
	@media (max-width: 520px) {
		button {
			grid-template-columns: 24px 58px 58px 1fr;
		}
		.shares {
			display: none;
		}
	}
</style>
