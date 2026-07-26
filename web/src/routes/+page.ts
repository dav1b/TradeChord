// Load the active release + the selected country's projection (SSR-friendly).
// Country comes from ?country=XXX so views are shareable; defaults to USA.
import { loadCountry, loadCurrent, loadOverview } from '$lib/data/load';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, url }) => {
	const current = await loadCurrent(fetch);
	const overview = await loadOverview(current.datasetVersion, fetch);
	const countries = overview.reporters.map((r) => r.code);

	const requested = url.searchParams.get('country') ?? '';
	const country = countries.includes(requested)
		? requested
		: countries.includes('USA')
			? 'USA'
			: countries[0];

	const projection = await loadCountry(current.datasetVersion, country, fetch);

	return { version: current.datasetVersion, countries, country, projection };
};
