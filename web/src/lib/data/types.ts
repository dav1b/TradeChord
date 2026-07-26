// Types for the committed data release consumed by the dashboard.
// Mirrors data/contracts/*.schema.json. All monetary values are integer current USD.

export const SUPPORTED_SCHEMA_VERSION = 1;

/** Total exports/imports/balance for one year. */
export interface FlowSummary {
	exportsUsd: number;
	importsUsd: number;
	balanceUsd: number;
}

/** One partner's dual-flow values within a year. */
export interface PartnerRow {
	partner: string;
	exportsUsd: number;
	importsUsd: number;
	balanceUsd: number;
	exportShare: number; // 0..1, share of the reporter's exports that year
}

/** One product sector's dual-flow values within a year. */
export interface ProductRow {
	product: string;
	exportsUsd: number;
	importsUsd: number;
	balanceUsd: number;
	exportShare: number;
}

/** A partner × product cell for the headline year (cross-filtering). */
export interface CrossCell {
	partner: string;
	product: string;
	exportsUsd: number;
	importsUsd: number;
	balanceUsd: number;
}

/** Per-country projection: web/static/data/<version>/countries/<CODE>.json */
export interface CountryProjection {
	schemaVersion: number;
	datasetVersion: string;
	country: string;
	years: number[];
	summaryByYear: Record<string, FlowSummary>;
	partnersByYear: Record<string, PartnerRow[]>;
	productsByYear: Record<string, ProductRow[]>;
	crossYear: number | null;
	crossCells: CrossCell[];
}

export interface ReporterYearTotals extends FlowSummary {
	year: number;
}

export interface OverviewReporter {
	code: string;
	totalsByYear: ReporterYearTotals[];
}

/** Overview projection: web/static/data/<version>/overview.json */
export interface Overview {
	schemaVersion: number;
	datasetVersion: string;
	defaultYear: number | null;
	reporters: OverviewReporter[];
}

/** Country index: web/static/data/<version>/countries.json */
export interface CountriesIndex {
	schemaVersion: number;
	datasetVersion: string;
	countries: string[];
}

/** Active-release pointer: web/static/data/current.json */
export interface CurrentPointer {
	schemaVersion: number;
	datasetVersion: string;
	manifestSha256: string;
}
