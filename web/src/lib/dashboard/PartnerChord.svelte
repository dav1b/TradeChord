<script lang="ts">
	import ChordChart from '$lib/charts/ChordChart.svelte';
	import type { CountryProjection } from '$lib/data/types';

	let {
		projection,
		year,
		topN = 9
	}: { projection: CountryProjection; year: number; topN?: number } = $props();

	// Top bilateral partners by total trade (exports + imports), plus ROW.
	const rows = $derived.by(() => {
		const all = projection.partnersByYear[String(year)] ?? [];
		const named = all
			.filter((p) => p.partner !== 'ROW' && p.exportAvailable && p.importAvailable)
			.slice()
			.sort((a, b) => b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd))
			.slice(0, topN);
		const row = all.find((p) => p.partner === 'ROW');
		return row ? [...named, row] : named;
	});

	const summary = $derived(projection.summaryByYear[String(year)]);
</script>

<ChordChart reporter={projection.country} {year} {rows} reporterSummary={summary} />
