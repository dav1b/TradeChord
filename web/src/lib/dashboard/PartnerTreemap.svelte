<script lang="ts">
	import TreemapChart from '$lib/charts/TreemapChart.svelte';
	import { partnerPoint } from '$lib/ui/tradepoint.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let { projection, year }: { projection: CountryProjection; year: number } = $props();

	const items = $derived(
		(projection.partnersByYear[String(year)] ?? [])
			.filter((p) => p.exportsUsd > 0)
			.map((p) => ({
				label: p.partner,
				value: p.exportsUsd,
				point: partnerPoint(projection.country, year, p)
			}))
	);
</script>

<TreemapChart {items} />
