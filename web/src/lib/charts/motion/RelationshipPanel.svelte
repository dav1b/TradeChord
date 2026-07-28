<script lang="ts">
	import BilateralHistory from '$lib/charts/motion/BilateralHistory.svelte';
	import ProductRelationshipTable from '$lib/charts/motion/ProductRelationshipTable.svelte';
	import type { RelationshipHistoryPoint } from '$lib/charts/motion/relationship-types';
	import { usd, usdSigned } from '$lib/format';
	import { flowKey, partnerKey } from '$lib/explorer/entity';
	import type { CrossCell, PartnerRow } from '$lib/data/types';

	let {
		reporter, row, history, products, peersByProduct, crossYear, progress, onclose
	}: {
		reporter:string; row:PartnerRow; history:RelationshipHistoryPoint[]; products:CrossCell[];
		peersByProduct:Record<string, CrossCell[]>; crossYear:number|null; progress:number; onclose:()=>void;
	} = $props();
	let preview = $state<RelationshipHistoryPoint | null>(null);
	const total = $derived(row.exportsUsd + row.importsUsd);
	const exportsUsd = $derived(preview?.exportsUsd ?? row.exportsUsd);
	const importsUsd = $derived(preview?.importsUsd ?? row.importsUsd);
	const balanceUsd = $derived(preview?.balanceUsd ?? row.balanceUsd);
	const displayYear = $derived(preview?.year ?? crossYear);
</script>

<section class="panel" class:visible={progress > .02} style:--panel-progress={progress}
	data-entity-id={partnerKey(reporter,row.partner)} aria-hidden={progress < .98}
	aria-label="{reporter} relationship with {row.partner}">
	<div class="sticky-header">
	<div class="intro">
		<button class="back" onclick={onclose} aria-label="Return {row.partner} to the trade network">← Network</button>
		<span>Bilateral relationship</span>
		<h2>{reporter} ↔ {row.partner}</h2>
	</div>
	</div>

	<div class="overview">
		<div class="metrics" aria-label="{reporter} bilateral trade balance with {row.partner}">
			<div class="equation-row">
			<div class="measure" data-entity-id={flowKey(reporter,row.partner,'export')}>
				<span>Reported exports</span><strong>{usd(exportsUsd)}</strong>
			</div>
			<span class="operator" aria-hidden="true">−</span>
			<div class="measure" data-entity-id={flowKey(reporter,row.partner,'import')}>
				<span>Reported imports</span><strong>{usd(importsUsd)}</strong>
			</div>
			<span class="operator" aria-hidden="true">=</span>
			<div class="measure balance">
				<span>Reported balance</span>
				<strong class:negative={(balanceUsd ?? 0) < 0}>
					{balanceUsd == null ? 'Unavailable' : usdSigned(balanceUsd)}
				</strong>
			</div>
			</div>
			<p>{displayYear ?? 'Latest'} · Total trade {usd(total)}</p>
		</div>
		<BilateralHistory {reporter} partner={row.partner} points={history} compact
			onpreview={(point) => preview = point}/>
	</div>

	<ProductRelationshipTable {reporter} partner={row.partner} year={crossYear}
		cells={products} {peersByProduct}/>
</section>

<style>
	.panel {
		position:absolute; z-index:5; top:51%; left:50%; width:min(calc(100vw - 48px),1180px);
		box-sizing:border-box;
		max-height:min(88%,860px); overflow:auto; padding:clamp(20px,2.5vw,34px);
		border:1px solid color-mix(in srgb,var(--dj-carbon) 24%,transparent);
		background:var(--surface);
		opacity:var(--panel-progress);
		transform:translate(-50%,-50%) translateY(calc((1 - var(--panel-progress))*24px))
			scale(calc(.96 + var(--panel-progress)*.04)); pointer-events:none;
	}
	.panel.visible { pointer-events:auto; }
	.sticky-header {
		position:sticky; z-index:5; top:0;
		margin:calc(clamp(20px,2.5vw,34px)*-1) calc(clamp(20px,2.5vw,34px)*-1) 0;
		padding:clamp(20px,2.5vw,34px);
		background:color-mix(in srgb,var(--surface) 98%,transparent);
		border-bottom:1px solid var(--border-faint);
	}
	.intro { min-height:clamp(110px,15vw,170px); padding-right:min(34vw,420px); }
	.back { border:0; padding:0; background:transparent; font-family:var(--font-mono);
		font-size:9px; text-transform:uppercase; color:var(--text-3); cursor:pointer; }
	.back:focus-visible { outline:2px solid var(--active); outline-offset:3px; }
	.intro>span { display:block; margin-top:28px; font-family:var(--font-mono); font-size:9px;
		text-transform:uppercase; color:var(--text-3); }
	h2 { margin-top:5px; font-family:var(--font-head); font-size:clamp(2rem,4.5vw,4rem);
		font-weight:500; color:var(--text-1); }
	.overview { display:grid; grid-template-columns:minmax(300px,.9fr) minmax(420px,1.4fr);
		align-items:center; gap:clamp(24px,5vw,72px); margin:22px 0; }
	.metrics { min-width:0; }
	.equation-row { display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) auto minmax(0,1fr); align-items:center; }
	.measure { display:flex; flex-direction:column; gap:9px; min-width:0; padding:13px 12px;
		background:transparent; }
	.operator { font-family:var(--font-head); font-size:clamp(1rem,2vw,1.6rem); color:var(--text-3); }
	.measure span,.metrics p { font-family:var(--font-mono); font-size:9px; text-transform:uppercase; color:var(--text-3); }
	.measure strong { font-family:var(--font-mono); font-size:clamp(10px,1.25vw,14px); white-space:nowrap; }
	.measure.balance strong { color:var(--delta-pos-mark); }
	.measure.balance strong.negative { color:var(--delta-neg-mark); }
	.metrics p { margin:7px 12px 0; text-transform:none; }
	@media(max-width:760px) {
		.panel { top:106%; width:min(calc(100vw - 16px),100%); max-height:82svh; padding:14px 10px; }
		.sticky-header { margin:-14px -10px 0; padding:14px 10px; }
		.intro { min-height:165px; padding-right:38%; }
		.intro>span { margin-top:24px; }
		h2 { font-size:clamp(1.9rem,10vw,3rem); white-space:nowrap; }
		.overview { grid-template-columns:1fr; gap:14px; }
		.metrics { order:0; }
		.measure { padding-inline:5px; }
		.measure span { font-size:7px; }
		.measure strong { font-size:9px; }
		.operator { font-size:1rem; }
	}
</style>
