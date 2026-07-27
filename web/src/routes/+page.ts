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

	return { version: current.datasetVersion, countries, country, projection };
};
