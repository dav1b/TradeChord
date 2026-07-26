<script lang="ts">
	import TreemapChart from '$lib/charts/TreemapChart.svelte';
	import { productPoint } from '$lib/ui/tradepoint.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let { projection, year }: { projection: CountryProjection; year: number } = $props();

	const items = $derived(
		(projection.productsByYear[String(year)] ?? [])
			.filter((p) => p.exportsUsd > 0)
			.map((p) => {
				const label = p.product.replace(/^\d+-\d+_/, '');
				return {
					label,
					value: p.exportsUsd,
					point: productPoint(projection.country, year, p, label)
				};
			})
	);
</script>

<TreemapChart {items} />
