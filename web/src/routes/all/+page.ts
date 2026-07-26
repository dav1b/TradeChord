// Overview of all reporters, from overview.json (no full-matrix load).
import { loadCurrent, loadOverview } from '$lib/data/load';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const current = await loadCurrent(fetch);
	const overview = await loadOverview(current.datasetVersion, fetch);
	return { version: current.datasetVersion, overview };
};
