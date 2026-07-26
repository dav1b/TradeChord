<script lang="ts">
	// Top partners' export-share change over the release's year range.
	import SlopeChart from '$lib/charts/SlopeChart.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let { projection, topN = 7 }: { projection: CountryProjection; topN?: number } = $props();

	const y1 = $derived(projection.years[0]);
	const y2 = $derived(projection.years[projection.years.length - 1]);

	const rows = $derived.by(() => {
		const first = new Map(projection.partnersByYear[String(y1)].map((p) => [p.partner, p]));
		return projection.partnersByYear[String(y2)]
			.filter((p) => p.partner !== 'ROW')
			.slice(0, topN)
			.map((p) => ({
				label: p.partner,
				a: first.get(p.partner)?.exportShare ?? 0,
				b: p.exportShare
			}));
	});
</script>

<SlopeChart {rows} leftLabel={String(y1)} rightLabel={String(y2)} />
