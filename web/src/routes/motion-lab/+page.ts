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
	const rows = rest ? [...named, rest] : named;
	const namedPartners = new Set(named.map((row) => row.partner));
	const historyByPartner = Object.fromEntries(
		named.map((row) => [
			row.partner,
			projection.years.map((candidateYear) => {
				const candidate = (projection.partnersByYear[String(candidateYear)] ?? []).find(
					(entry) => entry.partner === row.partner
				);
				return {
					year: candidateYear,
					exportsUsd: candidate?.exportsUsd ?? 0,
					importsUsd: candidate?.importsUsd ?? 0,
					balanceUsd: candidate?.balanceUsd ?? null,
					exportAvailable: candidate?.exportAvailable ?? false,
					importAvailable: candidate?.importAvailable ?? false
				};
			})
		])
	);
	const productsByPartner = projection.crossCells
		.filter((cell) => namedPartners.has(cell.partner))
		.reduce<Record<string, typeof projection.crossCells>>((grouped, cell) => {
			(grouped[cell.partner] ??= []).push(cell);
			return grouped;
		}, {});

	return {
		reporter,
		reporterName: projection.countryName,
		year,
		rows,
		summary: projection.summaryByYear[String(year)],
		crossYear: projection.crossYear,
		historyByPartner,
		productsByPartner,
		version: current.datasetVersion
	};
};
