import { loadCountry, loadCurrent, loadOverview } from '$lib/data/load';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const current = await loadCurrent(fetch);
	const overview = await loadOverview(current.datasetVersion, fetch);
	const reporter = overview.reporters.some((entry) => entry.code === 'DEU')
		? 'DEU'
		: overview.reporters[0].code;
	const projection = await loadCountry(current.datasetVersion, reporter, fetch);
	const year = projection.years.at(-1) ?? 0;
	const all = projection.partnersByYear[String(year)] ?? [];
	const named = all
		.filter((row) => row.partner !== 'ROW' && row.exportAvailable && row.importAvailable)
		.slice()
		.sort((a, b) => b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd))
		.slice(0, 10);
	const rest = all.find((row) => row.partner === 'ROW');

	return {
		reporter,
		reporterName: projection.countryName,
		year,
		rows: rest ? [...named, rest] : named,
		summary: projection.summaryByYear[String(year)],
		version: current.datasetVersion
	};
};
