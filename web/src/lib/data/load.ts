// Typed loaders for the committed data release.
//
// The dashboard reads small per-country projections (not the full matrix). The
// active release is named by /data/current.json; everything else lives under
// /data/<version>/.

import {
	SUPPORTED_SCHEMA_VERSION,
	type CountriesIndex,
	type CountryProjection,
	type CurrentPointer,
	type Overview
} from './types';

type Fetch = typeof globalThis.fetch;

const BASE = '/data';

async function fetchJson<T extends { schemaVersion: number }>(
	url: string,
	fetchFn: Fetch
): Promise<T> {
	const res = await fetchFn(url);
	if (!res.ok) {
		throw new Error(`Failed to load ${url}: HTTP ${res.status}`);
	}
	const data = (await res.json()) as T;
	if (data.schemaVersion !== SUPPORTED_SCHEMA_VERSION) {
		throw new Error(
			`Unsupported schemaVersion ${data.schemaVersion} at ${url} ` +
				`(expected ${SUPPORTED_SCHEMA_VERSION})`
		);
	}
	return data;
}

/** Resolve the active release version from the pointer file. */
export async function loadCurrent(fetchFn: Fetch = fetch): Promise<CurrentPointer> {
	return fetchJson<CurrentPointer>(`${BASE}/current.json`, fetchFn);
}

export async function loadOverview(version: string, fetchFn: Fetch = fetch): Promise<Overview> {
	return fetchJson<Overview>(`${BASE}/${version}/overview.json`, fetchFn);
}

export async function loadCountriesIndex(
	version: string,
	fetchFn: Fetch = fetch
): Promise<CountriesIndex> {
	return fetchJson<CountriesIndex>(`${BASE}/${version}/countries.json`, fetchFn);
}

export async function loadCountry(
	version: string,
	code: string,
	fetchFn: Fetch = fetch
): Promise<CountryProjection> {
	return fetchJson<CountryProjection>(`${BASE}/${version}/countries/${code}.json`, fetchFn);
}
