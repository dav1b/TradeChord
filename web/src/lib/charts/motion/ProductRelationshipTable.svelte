<script lang="ts">
	import { flip } from 'svelte/animate';
	import { cubicOut } from 'svelte/easing';
	import { productKey } from '$lib/explorer/entity';
	import { usd, usdSigned } from '$lib/format';
	import type { CrossCell } from '$lib/data/types';

	let {
		reporter, partner, year, cells, peersByProduct
	}: {
		reporter: string; partner: string; year: number | null; cells: CrossCell[];
		peersByProduct: Record<string, CrossCell[]>;
	} = $props();

	let selected = $state<string | null>(null);
	const ranked = $derived(cells.slice().sort((a, b) => {
		if (a.product === selected) return -1;
		if (b.product === selected) return 1;
		return b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd);
	}).slice(0, selected ? 10 : 8));
	const maxFlow = $derived(Math.max(1, ...cells.flatMap((d) => [d.exportsUsd, d.importsUsd])));
	const maxBalance = $derived(Math.max(1, ...cells.map((d) => Math.abs(d.balanceUsd ?? 0))));
	const barWidth = (value: number) => `${Math.max(1, value / maxFlow * 46)}%`;
	const balancePosition = (value: number | null) => `${50 + (value ?? 0) / maxBalance * 43}%`;

	function toggle(product: string) { selected = selected === product ? null : product; }
	function keyRow(event: KeyboardEvent, product: string) {
		if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(product); }
		if (event.key === 'Escape') selected = null;
	}
	function peers(product: string) {
		return (peersByProduct[product] ?? []).filter((d) => d.partner !== 'ROW').slice().sort(
			(a, b) => b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd)
		).slice(0, 6);
	}
	function peerWidth(cell: CrossCell, product: string) {
		const largest = Math.max(1, ...peers(product).map((d) => d.exportsUsd + d.importsUsd));
		return `${Math.max(3, (cell.exportsUsd + cell.importsUsd) / largest * 100)}%`;
	}
</script>

<section class="products" aria-labelledby="product-heading">
	<header>
		<div>
			<span>Product relationship · {year ?? 'headline year'}</span>
			<h3 id="product-heading">What drives this relationship?</h3>
		</div>
		<div class="key" aria-label="Product chart legend">
			<span class="export">Exports</span><span class="import">Imports</span>
			<span class="surplus">Surplus</span><span class="deficit">Deficit</span>
		</div>
	</header>
	<div class="column-head" aria-hidden="true">
		<span>Product</span><span>Reported exports ← · → reported imports</span><span>Value</span>
	</div>
	<div class="rows">
		{#each ranked as cell (cell.product)}
			<div class="product-row" class:selected={selected === cell.product}
				animate:flip={{ duration: 420, easing: cubicOut }}
				data-entity-id={productKey(reporter, partner, 'both', cell.product)}>
				<button class="row-main" aria-expanded={selected === cell.product}
					aria-label="{cell.product}: exports {usd(cell.exportsUsd)}, imports {usd(cell.importsUsd)}"
					onclick={() => toggle(cell.product)} onkeydown={(e) => keyRow(e, cell.product)}>
					<span class="product-name">{cell.product}</span>
					<span class="diverging" aria-hidden="true">
						<span class="zero"></span>
						<span class="bar export-bar" style:width={barWidth(cell.exportsUsd)}></span>
						<span class="bar import-bar" style:width={barWidth(cell.importsUsd)}></span>
						{#if cell.balanceUsd != null}
							<span class="balance-mark" class:negative={cell.balanceUsd < 0}
								style:left={balancePosition(cell.balanceUsd)}></span>
						{/if}
					</span>
					<span class="value"><strong>{usd(cell.exportsUsd + cell.importsUsd)}</strong>
						<small>{year ?? 'One year'} only</small></span>
				</button>
				{#if selected === cell.product}
					<div class="detail">
						<div class="selection">
							<span class="eyebrow">Selected product</span><strong>{cell.product}</strong>
							<p>Balance <b class:negative={(cell.balanceUsd ?? 0) < 0}>
								{cell.balanceUsd == null ? 'unavailable' : usdSigned(cell.balanceUsd)}
							</b></p>
						</div>
						<div class="peers">
							<span class="eyebrow">Where else does {reporter} trade this product?</span>
							{#each peers(cell.product) as peer, index (peer.partner)}
								<div class="peer" class:pinned={peer.partner === partner}>
									<span>{index + 1}</span><strong>{peer.partner}</strong>
									<i style:width={peerWidth(peer, cell.product)}></i>
									<small>{usd(peer.exportsUsd + peer.importsUsd)}</small>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{/each}
	</div>
	<p class="data-note">Product history is not inferred: sparklines activate when the release publishes partner × product × year detail.</p>
</section>

<style>
	.products { border-top: 1px solid var(--border); padding-top: 18px; }
	header { display:flex; align-items:end; justify-content:space-between; gap:20px; margin-bottom:12px; }
	header span,.eyebrow,.column-head,.data-note { font-family:var(--font-mono); font-size:9px; color:var(--text-3); }
	header>div:first-child>span,.eyebrow,.column-head { text-transform:uppercase; }
	h3 { margin-top:3px; font-size:clamp(1rem,1.7vw,1.35rem); font-weight:500; }
	.key { display:flex; flex-wrap:wrap; justify-content:end; gap:10px; }
	.key span::before { content:''; display:inline-block; width:12px; height:3px; margin-right:4px; vertical-align:middle; background:var(--text-3); }
	.key .export::before { background:var(--dj-carbon); } .key .import::before { background:color-mix(in srgb,var(--dj-carbon) 58%,var(--surface)); }
	.key .surplus::before { background:var(--delta-pos); } .key .deficit::before { background:var(--delta-neg); }
	.column-head,.row-main { display:grid; grid-template-columns:minmax(145px,.9fr) minmax(300px,2.4fr) minmax(110px,.8fr); align-items:center; }
	.column-head { padding:0 12px 6px; } .column-head span:nth-child(2) { text-align:center; } .column-head span:last-child { text-align:right; }
	.product-row { border-top:1px solid var(--border-faint); background:transparent; }
	.product-row.selected { background:color-mix(in srgb,var(--dj-alabaster) 22%,transparent); }
	.row-main { width:100%; min-height:68px; border:0; padding:10px 12px; background:transparent; color:var(--text-1); text-align:left; cursor:pointer; }
	.row-main:hover,.row-main:focus-visible { background:color-mix(in srgb,var(--dj-alabaster) 32%,transparent); outline:none; }
	.product-name { padding-right:16px; font-size:clamp(.85rem,1.25vw,1.05rem); }
	.diverging { position:relative; display:block; height:28px; }
	.zero { position:absolute; inset-block:0; left:50%; width:1px; background:var(--text-3); }
	.bar { position:absolute; top:6px; height:16px; } .export-bar { right:50%; background:var(--dj-carbon); }
	.import-bar { left:50%; background:color-mix(in srgb,var(--dj-carbon) 58%,var(--surface)); }
	.balance-mark { position:absolute; z-index:1; inset-block:1px; width:4px; background:var(--delta-pos); transform:translateX(-2px); }
	.balance-mark.negative { background:var(--delta-neg); }
	.value { display:grid; justify-items:end; font-family:var(--font-mono); } .value strong { font-size:10px; }
	.value small { margin-top:3px; font-size:8px; color:var(--text-3); text-transform:uppercase; }
	.detail { display:grid; grid-template-columns:minmax(150px,.7fr) minmax(300px,2fr); gap:24px; padding:14px 12px 20px; border-top:1px dashed var(--border); }
	.selection { display:grid; align-content:start; gap:6px; } .selection p { font-family:var(--font-mono); font-size:10px; }
	.selection b { color:var(--delta-pos-mark); } .selection b.negative { color:var(--delta-neg-mark); }
	.peers { display:grid; gap:5px; } .peer { display:grid; grid-template-columns:20px 45px 1fr 68px; align-items:center; gap:7px; min-height:20px; font-family:var(--font-mono); font-size:9px; }
	.peer i { display:block; height:5px; background:var(--dj-alabaster); } .peer small { text-align:right; }
	.peer.pinned strong { color:var(--dj-navy); } .peer.pinned i { background:var(--dj-navy); }
	.data-note { padding:9px 12px 0; text-transform:none; }
	@media(max-width:640px) {
		header { align-items:start; flex-direction:column; } .key { justify-content:start; } .column-head { display:none; }
		.row-main { grid-template-columns:minmax(0,27%) minmax(0,1fr) minmax(48px,18%); padding-inline:4px; }
		.product-name { overflow:hidden; font-size:.78rem; text-overflow:ellipsis; white-space:nowrap; }
		.value strong { font-size:8px; } .value small { font-size:7px; } .detail { grid-template-columns:1fr; padding-inline:6px; }
		.peer { grid-template-columns:16px 38px minmax(0,1fr) 58px; gap:4px; }
	}
</style>
