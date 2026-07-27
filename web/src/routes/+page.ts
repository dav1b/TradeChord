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
	const representation: 'rank' | 'chord' =
		url.searchParams.get('view') === 'rank' ? 'rank' : 'chord';
	const partnerParam = url.searchParams.get('partner');
	const productParam = url.searchParams.get('product');
	const partnerCodes = new Set(
		(projection.partnersByYear[String(projection.years.at(-1))] ?? []).map((row) => row.partner)
	);
	const productCodes = new Set(
		(projection.productsByYear[String(projection.years.at(-1))] ?? []).map((row) =>
			row.product.replace(/^\d+-\d+_/, '')
		)
	);
	const partner = partnerParam && partnerCodes.has(partnerParam) ? partnerParam : null;
	const product = productParam && productCodes.has(productParam) ? productParam : null;

	return {
		version: current.datasetVersion,
		countries,
		country,
		projection,
		explorer: { representation, partner, product }
	};
};
