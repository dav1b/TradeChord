<script lang="ts">
	import TreemapChart from '$lib/charts/TreemapChart.svelte';
	import { productPoint } from '$lib/ui/tradepoint.svelte';
	import { selectProduct, selection } from '$lib/ui/selection.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let { projection, year }: { projection: CountryProjection; year: number } = $props();
	const reporter = $derived(projection.country);
	const clean = (p: string) => p.replace(/^\d+-\d+_/, '');

	const items = $derived.by(() => {
		// Cross-filtered: products for the selected partner.
		if (selection.partner) {
			const cells = projection.crossCells.filter(
				(c) => c.partner === selection.partner && c.exportsUsd > 0
			);
			const total = cells.reduce((s, c) => s + c.exportsUsd, 0) || 1;
			return cells
				.map((c) => {
					const label = clean(c.product);
					return {
						label,
						value: c.exportsUsd,
						point: productPoint(
							reporter,
							projection.crossYear ?? year,
							{
								product: c.product,
								exportsUsd: c.exportsUsd,
								importsUsd: c.importsUsd,
								balanceUsd: c.balanceUsd,
								exportShare: c.exportsUsd / total
							},
							label,
							selection.partner ?? undefined
						)
					};
				})
				.sort((a, b) => b.value - a.value);
		}
		// Default: all products.
		return (projection.productsByYear[String(year)] ?? [])
			.filter((p) => p.exportsUsd > 0)
			.map((p) => {
				const label = clean(p.product);
				return { label, value: p.exportsUsd, point: productPoint(reporter, year, p, label) };
			});
	});
</script>

<TreemapChart {items} selectedLabel={selection.product} onselect={selectProduct} />
