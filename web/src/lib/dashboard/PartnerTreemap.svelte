<script lang="ts">
	import TreemapChart from '$lib/charts/TreemapChart.svelte';
	import { partnerPoint } from '$lib/ui/tradepoint.svelte';
	import { useExplorer } from '$lib/explorer/explorer.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let { projection, year }: { projection: CountryProjection; year: number } = $props();
	const explorer = useExplorer();
	const reporter = $derived(projection.country);
	const clean = (p: string) => p.replace(/^\d+-\d+_/, '');

	const items = $derived.by(() => {
		// Cross-filtered: partners for the selected product.
		if (explorer.state.product) {
			const cells = projection.crossCells.filter(
				(c) => clean(c.product) === explorer.state.product && c.exportsUsd > 0
			);
			const total = cells.reduce((s, c) => s + c.exportsUsd, 0) || 1;
			return cells
				.map((c) => ({
					label: c.partner,
					value: c.exportsUsd,
					point: partnerPoint(
						reporter,
						projection.crossYear ?? year,
						{
							partner: c.partner,
							exportsUsd: c.exportsUsd,
							importsUsd: c.importsUsd,
							balanceUsd: c.balanceUsd,
							exportAvailable: c.exportAvailable,
							importAvailable: c.importAvailable,
							exportShare: c.exportsUsd / total
						},
						explorer.state.product ?? undefined
					)
				}))
				.sort((a, b) => b.value - a.value);
		}
		// Default: all partners.
		return (projection.partnersByYear[String(year)] ?? [])
			.filter((p) => p.exportsUsd > 0)
			.map((p) => ({ label: p.partner, value: p.exportsUsd, point: partnerPoint(reporter, year, p) }));
	});
</script>

<TreemapChart
	{items}
	selectedLabel={explorer.state.partner}
	onselect={(code) => explorer.selectPartner(code)}
/>
