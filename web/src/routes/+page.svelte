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
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const year = $derived(data.projection.years[data.projection.years.length - 1]);
	const summary = $derived(data.projection.summaryByYear[String(year)]);
	const source = $derived(`WITS · ${year}`);

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

	<Hero {year} {summary} {source} />

	<div class="grid">
		<Card title="Trade network · top partners" {source}>
			<PartnerChord projection={data.projection} {year} />
		</Card>
		<Card title="Partners · exports, tinted by balance" {source}>
			<PartnerTreemap projection={data.projection} {year} />
		</Card>
		<Card title="Products · exports, tinted by balance" {source}>
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
	}
</style>
