<script lang="ts">
	// Top partners' export-share change over the release's year range.
	import SlopeChart from '$lib/charts/SlopeChart.svelte';
	import { partnerPoint } from '$lib/ui/tradepoint.svelte';
	import type { CountryProjection, PartnerRow } from '$lib/data/types';

	let { projection, topN = 7 }: { projection: CountryProjection; topN?: number } = $props();

	const reporter = $derived(projection.country);
	const y1 = $derived(projection.years[0]);
	const y2 = $derived(projection.years[projection.years.length - 1]);

	const rows = $derived.by(() => {
		const first = new Map(projection.partnersByYear[String(y1)].map((p) => [p.partner, p]));
		return projection.partnersByYear[String(y2)]
			.filter((p) => p.partner !== 'ROW')
			.slice(0, topN)
			.map((p) => {
				const fa: PartnerRow = first.get(p.partner) ?? {
					partner: p.partner,
					exportsUsd: 0,
					importsUsd: 0,
					balanceUsd: null,
					exportAvailable: false,
					importAvailable: false,
					exportShare: 0
				};
				return {
					label: p.partner,
					a: fa.exportShare,
					b: p.exportShare,
					pointA: partnerPoint(reporter, y1, fa),
					pointB: partnerPoint(reporter, y2, p)
				};
			});
	});
</script>

<SlopeChart {rows} leftLabel={String(y1)} rightLabel={String(y2)} />
