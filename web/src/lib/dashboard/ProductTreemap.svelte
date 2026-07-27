<script lang="ts">
	import TreemapChart from '$lib/charts/TreemapChart.svelte';
	import { productPoint } from '$lib/ui/tradepoint.svelte';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let { projection, year }: { projection: CountryProjection; year: number } = $props();
	const explorer = useExplorer();
	const reporter = $derived(projection.country);
	const clean = (p: string) => p.replace(/^\d+-\d+_/, '');

	const items = $derived.by(() => {
		// Cross-filtered: products for the selected partner.
		if (explorer.state.partner) {
			const cells = projection.crossCells.filter(
				(c) => c.partner === explorer.state.partner && c.exportsUsd > 0
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
								exportAvailable: c.exportAvailable,
								importAvailable: c.importAvailable,
								exportShare: c.exportsUsd / total
							},
							label,
							explorer.state.partner ?? undefined
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

<TreemapChart
	{items}
	selectedLabel={explorer.state.product}
	onselect={(code) => explorer.selectProduct(code)}
/>
