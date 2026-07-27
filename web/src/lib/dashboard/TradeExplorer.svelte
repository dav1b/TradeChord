<script lang="ts">
	import { fade } from 'svelte/transition';
	import PartnerChord from './PartnerChord.svelte';
	import PartnerTreemap from './PartnerTreemap.svelte';
	import ProductTreemap from './ProductTreemap.svelte';
	import PartnerSlope from './PartnerSlope.svelte';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import { motionDuration } from '$lib/motion';
	import type { CountryProjection } from '$lib/data/types';

	let {
		projection,
		year,
		source
	}: {
		projection: CountryProjection;
		year: number;
		source: string;
	} = $props();

	const explorer = useExplorer();
	const selected = $derived(explorer.state.partner ?? explorer.state.product);
	const question = $derived.by(() => {
		if (explorer.state.representation === 'products' && explorer.state.partner) {
			return `What makes up ${projection.country}’s ${explorer.state.flow}s with ${explorer.state.partner}?`;
		}
		if (explorer.state.representation === 'history' && explorer.state.partner) {
			return `How has ${projection.country}’s trade with ${explorer.state.partner} changed?`;
		}
		if (explorer.state.representation === 'relationship' && explorer.state.partner) {
			return `How does ${projection.country} trade with ${explorer.state.partner}?`;
		}
		if (explorer.state.representation === 'rank') {
			return `Which partners matter most to ${projection.country}?`;
		}
		return `How is ${projection.country} connected to its trading partners?`;
	});
	const sceneLabel = $derived(
		explorer.state.representation === 'products'
			? `${explorer.state.flow === 'export' ? 'Export' : 'Import'} composition`
			: explorer.state.representation === 'history'
				? 'Bilateral history'
			: explorer.state.representation === 'relationship'
				? 'Bilateral relationship'
				: explorer.state.representation === 'rank'
					? 'Ranked partner network'
					: 'National trade network'
	);
	const partnerContextTitle = $derived(
		explorer.state.product ? `Partners trading ${explorer.state.product}` : 'Partner structure'
	);
	const productContextTitle = $derived(
		`${explorer.state.partner ? `Products traded with ${explorer.state.partner}` : 'Product structure'}${
			projection.crossYear && projection.crossYear !== year
				? ` · ${projection.crossYear} detail`
				: ''
		}`
	);
</script>

<section class="trade-scene" aria-labelledby="trade-scene-title">
	<header class="scene-head">
		<div>
			<p class="scene-label">{sceneLabel} · {year}</p>
			<h2 id="trade-scene-title">{question}</h2>
		</div>
		<div class="scene-status">
			<span>{selected ? 'Active context' : 'Reporter'}</span>
			<strong>{selected ?? projection.country}</strong>
		</div>
	</header>

	<div class="primary-scene">
		<PartnerChord {projection} {year} />
	</div>

	<aside class="evidence" aria-labelledby="evidence-title">
		<div class="evidence-head">
			<div>
				<p class="scene-label">Contextual evidence</p>
				<h3 id="evidence-title">
					{selected ? `What else changes with ${selected}?` : 'Read the network from another angle'}
				</h3>
			</div>
			<p>One selection drives every view. Scroll the tray to compare supporting evidence.</p>
		</div>

		<div class="evidence-grid" transition:fade={{ duration: motionDuration(160) }}>
			<section class="evidence-pane" aria-labelledby="partner-context-title">
				<h4 id="partner-context-title">{partnerContextTitle}</h4>
				<PartnerTreemap {projection} {year} />
			</section>
			<section class="evidence-pane" aria-labelledby="product-context-title">
				<h4 id="product-context-title">{productContextTitle}</h4>
				<ProductTreemap {projection} {year} />
			</section>
			<section class="evidence-pane trend" aria-labelledby="trend-context-title">
				<div class="pane-heading">
					<h4 id="trend-context-title">
						Partner history · {projection.years[0]}→{projection.years.at(-1)}
					</h4>
					{#if explorer.state.partner}
						<button onclick={() => explorer.openHistory()}>
							Open {explorer.state.partner} history
						</button>
					{/if}
				</div>
				<PartnerSlope {projection} onselect={(partner) => explorer.openHistory(partner)} />
			</section>
		</div>
	</aside>

	<footer class="scene-source">{source} · dual-flow release {projection.datasetVersion}</footer>
</section>

<style>
	.trade-scene {
		overflow: hidden;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
	}
	.scene-head {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: var(--space-5);
		padding: var(--space-5) var(--space-5) var(--space-4);
		border-bottom: 1px solid var(--border-faint);
	}
	.scene-label,
	.scene-status span,
	.scene-source {
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-4);
	}
	h2 {
		max-width: 30ch;
		margin-top: 4px;
		font-size: clamp(1.35rem, 2.4vw, 2.1rem);
		font-weight: 500;
		line-height: 1.08;
		color: var(--text-1);
	}
	.scene-status {
		flex: 0 0 auto;
		text-align: right;
	}
	.scene-status span,
	.scene-status strong {
		display: block;
	}
	.scene-status strong {
		margin-top: 3px;
		font-size: 1.2rem;
		color: var(--active);
	}
	.primary-scene {
		padding: var(--space-4) var(--space-5) var(--space-5);
	}
	.evidence {
		border-top: 1px solid var(--border);
		background: var(--surface-subtle, var(--dj-alabaster));
	}
	.evidence-head {
		display: flex;
		justify-content: space-between;
		align-items: end;
		gap: var(--space-5);
		padding: var(--space-4) var(--space-5);
	}
	.evidence-head h3 {
		margin-top: 3px;
		font-size: 1rem;
		font-weight: 500;
		color: var(--text-1);
	}
	.evidence-head > p {
		max-width: 50ch;
		font-size: 11px;
		color: var(--text-4);
		text-align: right;
	}
	.evidence-grid {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(260px, 0.8fr);
		border-top: 1px solid var(--border-faint);
	}
	.evidence-pane {
		min-width: 0;
		padding: var(--space-4) var(--space-5) var(--space-5);
		background: var(--surface);
	}
	.evidence-pane + .evidence-pane {
		border-left: 1px solid var(--border-faint);
	}
	.evidence-pane h4 {
		margin-bottom: var(--space-3);
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 400;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--text-3);
	}
	.pane-heading {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: var(--space-3);
	}
	.pane-heading button {
		border: 0;
		padding: 0;
		background: transparent;
		color: var(--active);
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		cursor: pointer;
	}
	.pane-heading button:focus-visible {
		outline: 2px solid var(--active);
		outline-offset: 3px;
	}
	.scene-source {
		padding: var(--space-3) var(--space-5);
		border-top: 1px solid var(--border-faint);
	}
	@media (max-width: 900px) {
		.evidence-grid {
			grid-template-columns: 1fr 1fr;
		}
		.evidence-pane.trend {
			grid-column: 1 / -1;
			border-top: 1px solid var(--border-faint);
			border-left: 0;
		}
	}
	@media (max-width: 640px) {
		.scene-head,
		.evidence-head {
			align-items: flex-start;
			flex-direction: column;
		}
		.scene-status,
		.evidence-head > p {
			text-align: left;
		}
		.primary-scene,
		.scene-head,
		.evidence-head,
		.evidence-pane {
			padding-left: var(--space-4);
			padding-right: var(--space-4);
		}
		.evidence-grid {
			display: flex;
			overflow-x: auto;
			scroll-snap-type: x mandatory;
			overscroll-behavior-x: contain;
		}
		.evidence-pane {
			flex: 0 0 min(86vw, 340px);
			scroll-snap-align: start;
		}
		.evidence-pane + .evidence-pane,
		.evidence-pane.trend {
			grid-column: auto;
			border-top: 0;
			border-left: 1px solid var(--border-faint);
		}
	}
</style>
