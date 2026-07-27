<script lang="ts">
	import { goto } from '$app/navigation';
	import Wordmark from '$lib/ui/Wordmark.svelte';
	import CountrySelect from '$lib/ui/CountrySelect.svelte';
	import Card from '$lib/ui/Card.svelte';
	import Hero from '$lib/dashboard/Hero.svelte';
	import PartnerSlope from '$lib/dashboard/PartnerSlope.svelte';
	import PartnerTreemap from '$lib/dashboard/PartnerTreemap.svelte';
	import ProductTreemap from '$lib/dashboard/ProductTreemap.svelte';
	import PartnerChord from '$lib/dashboard/PartnerChord.svelte';
	import {
		createExplorer,
		provideExplorer,
		type ExplorerState
	} from '$lib/explorer/explorer.svelte';
	import { motionDuration } from '$lib/motion';
	import { untrack } from 'svelte';
	import { fade } from 'svelte/transition';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const year = $derived(data.projection.years[data.projection.years.length - 1]);
	const summary = $derived(data.projection.summaryByYear[String(year)]);
	const source = $derived(`WITS · ${year}`);

	function navigateExplorer(state: Readonly<ExplorerState>) {
		const params = new URLSearchParams();
		params.set('country', state.reporter);
		if (state.representation !== 'chord') params.set('view', state.representation);
		if (state.representation === 'products') params.set('flow', state.flow);
		if (state.partner) params.set('partner', state.partner);
		if (state.product) params.set('product', state.product);
		goto(`?${params}`, { keepFocus: true, noScroll: true });
	}

	const explorer = provideExplorer(
		untrack(() =>
			createExplorer(
				{
					reporter: data.country,
					year,
					flow: data.explorer.flow,
					partner: data.explorer.partner,
					product: data.explorer.product,
					representation: data.explorer.representation
				},
				navigateExplorer
			)
		)
	);

	// Apply URL/back-forward navigation to the single scene state.
	$effect(() => {
		explorer.sync({
			reporter: data.country,
			year,
			flow: data.explorer.flow,
			partner: data.explorer.partner,
			product: data.explorer.product,
			representation: data.explorer.representation
		});
	});

	const partnersTitle = $derived(
		explorer.state.product
			? `Partners · ${explorer.state.product}`
			: 'Partners · exports, tinted by balance'
	);
	const productsTitle = $derived(
		explorer.state.partner
			? `Products · ${explorer.state.partner}`
			: 'Products · exports, tinted by balance'
	);
	const filterLabel = $derived(explorer.state.partner ?? explorer.state.product);
	const networkTitle = $derived(
		explorer.state.partner &&
			(explorer.state.representation === 'relationship' ||
				explorer.state.representation === 'products')
			? explorer.state.representation === 'products'
				? `${explorer.state.flow === 'export' ? 'Export' : 'Import'} products · ${explorer.state.partner}`
				: `Bilateral trade · ${explorer.state.partner}`
			: 'Trade network · top partners'
	);

	function selectCountry(code: string) {
		const view = explorer.state.representation === 'rank' ? '&view=rank' : '';
		goto(`?country=${code}${view}`, { keepFocus: true, noScroll: true });
	}
</script>

<Wordmark />

<div class="page">
	<header class="head">
		<div>
			<p class="eyebrow">Global trade · {year}</p>
			<h1>{data.projection.countryName} <span>{data.country}</span></h1>
		</div>
		<CountrySelect value={data.country} options={data.countries} onchange={selectCountry} />
	</header>

	{#if filterLabel}
		<button
			class="chip"
			onclick={() => explorer.clearSelection()}
			transition:fade={{ duration: motionDuration(140) }}
		>
			Filtered · {filterLabel}<span class="x">×</span>
		</button>
	{/if}

	<Hero {year} {summary} {source} />

	<div class="grid">
		<Card title={networkTitle} {source}>
			<PartnerChord projection={data.projection} {year} />
		</Card>
		<Card title={partnersTitle} {source}>
			<PartnerTreemap projection={data.projection} {year} />
		</Card>
		<Card title={productsTitle} {source}>
			<ProductTreemap projection={data.projection} {year} />
		</Card>
		<Card title="Partner export share · {data.projection.years[0]}→{year}" {source}>
			<PartnerSlope projection={data.projection} />
		</Card>
	</div>

	<footer class="foot">
		<span>Source: World Bank WITS · dual-flow release {data.version}</span>
		<span>DataJockey</span>
	</footer>
	<details class="method">
		<summary>How to read the data</summary>
		<p>
			National exports and imports are directly reported WITS flows. Named bilateral partners
			represent explicitly collected top-partner flows; remaining trade is reconciled to the
			reporter’s world total under synthetic ROW. A bilateral balance is shown only when both
			flows were explicitly collected.
		</p>
	</details>
</div>

<style>
	.page {
		max-width: var(--maxw);
		margin: 0 auto;
		padding: var(--space-6) var(--space-5) var(--space-8);
		display: flex;
		flex-direction: column;
		gap: var(--space-6);
	}
	.head {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: var(--space-4);
		flex-wrap: wrap;
	}
	.chip {
		align-self: flex-start;
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--active-ink);
		background: var(--active);
		border: none;
		border-radius: 999px;
		padding: 6px 12px;
		cursor: pointer;
	}
	.chip .x {
		font-size: 14px;
		line-height: 1;
	}
	.eyebrow {
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-3);
	}
	h1 {
		font-size: 2.5rem;
		font-weight: 500;
		color: var(--text-1);
		letter-spacing: -0.01em;
	}
	h1 span {
		font-family: var(--font-mono);
		font-size: 0.42em;
		color: var(--text-3);
		vertical-align: middle;
	}
	.method {
		font-size: 12px;
		color: var(--text-3);
		max-width: 72ch;
	}
	.method summary {
		cursor: pointer;
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}
	.method p {
		margin-top: var(--space-2);
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
		gap: var(--space-4);
	}
	.foot {
		display: flex;
		justify-content: space-between;
		gap: var(--space-3);
		flex-wrap: wrap;
		font-size: 11px;
		color: var(--text-4);
		border-top: 1px solid var(--border-faint);
		padding-top: var(--space-4);
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 2rem;
		}
		.page {
			padding: var(--space-5) var(--space-4) var(--space-6);
		}
		.head {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
