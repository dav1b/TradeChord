// Load the active release + the selected country's projection (SSR-friendly).
// Country comes from ?country=XXX so views are shareable; defaults to USA.
import { loadCountry, loadCurrent, loadOverview } from '$lib/data/load';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, url }) => {
	const current = await loadCurrent(fetch);
	const overview = await loadOverview(current.datasetVersion, fetch);
	const countries = overview.reporters.map((r) => ({ code: r.code, name: r.name }));
	const countryCodes = countries.map((country) => country.code);

	const requested = url.searchParams.get('country') ?? '';
	const country = countryCodes.includes(requested)
		? requested
		: countryCodes.includes('USA')
			? 'USA'
			: countryCodes[0];

	const projection = await loadCountry(current.datasetVersion, country, fetch);
	const latestYear = projection.years.at(-1) ?? 0;
	const yearParam = Number(url.searchParams.get('year'));
	const year = projection.years.includes(yearParam) ? yearParam : latestYear;
	const view = url.searchParams.get('view');
	const flowParam = url.searchParams.get('flow');
	const partnerParam = url.searchParams.get('partner');
	const productParam = url.searchParams.get('product');
	const partnerCodes = new Set(
		projection.years.flatMap((candidateYear) =>
			(projection.partnersByYear[String(candidateYear)] ?? []).map((row) => row.partner)
		)
	);
	const productCodes = new Set(
		projection.years.flatMap((candidateYear) =>
			(projection.productsByYear[String(candidateYear)] ?? []).map((row) =>
				row.product.replace(/^\d+-\d+_/, '')
			)
		)
	);
	const partner = partnerParam && partnerCodes.has(partnerParam) ? partnerParam : null;
	const product = productParam && productCodes.has(productParam) ? productParam : null;
	const flow: 'export' | 'import' | 'both' =
		flowParam === 'export' || flowParam === 'import' ? flowParam : 'both';
	const representation: 'rank' | 'chord' | 'relationship' | 'products' | 'history' =
		view === 'rank'
			? 'rank'
			: view === 'history' && partner
				? 'history'
			: view === 'products' && partner && flow !== 'both'
				? 'products'
				: view === 'relationship' && partner
					? 'relationship'
					: 'chord';

	return {
		version: current.datasetVersion,
		countries,
		country,
		projection,
		explorer: { representation, year, flow, partner, product }
	};
};
