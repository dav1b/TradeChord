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
	import { clearSelection, selection } from '$lib/ui/selection.svelte';
	import { motionDuration } from '$lib/motion';
	import { fade } from 'svelte/transition';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const year = $derived(data.projection.years[data.projection.years.length - 1]);
	const summary = $derived(data.projection.summaryByYear[String(year)]);
	const source = $derived(`WITS · ${year}`);

	// Reset the cross-filter when the reporter changes.
	$effect(() => {
		data.country;
		clearSelection();
	});

	const partnersTitle = $derived(
		selection.product ? `Partners · ${selection.product}` : 'Partners · exports, tinted by balance'
	);
	const productsTitle = $derived(
		selection.partner ? `Products · ${selection.partner}` : 'Products · exports, tinted by balance'
	);
	const filterLabel = $derived(selection.partner ?? selection.product);

	function selectCountry(code: string) {
		goto(`?country=${code}`, { keepFocus: true, noScroll: true });
	}
</script>

<Wordmark />

<div class="page">
	<header class="head">
		<div>
			<p class="eyebrow">Global trade · {year}</p>
			<h1>{data.country}</h1>
		</div>
		<CountrySelect value={data.country} options={data.countries} onchange={selectCountry} />
	</header>

	{#if filterLabel}
		<button class="chip" onclick={clearSelection} transition:fade={{ duration: motionDuration(140) }}>
			Filtered · {filterLabel}<span class="x">×</span>
		</button>
	{/if}

	<Hero {year} {summary} {source} />

	<div class="grid">
		<Card title="Trade network · top partners" {source}>
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
