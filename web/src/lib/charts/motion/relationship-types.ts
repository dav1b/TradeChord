export type RelationshipHistoryPoint = {
	year: number;
	exportsUsd: number;
	importsUsd: number;
	balanceUsd: number | null;
	exportAvailable: boolean;
	importAvailable: boolean;
};
