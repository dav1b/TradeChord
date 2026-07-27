import type { CountryProjection, CrossCell, PartnerRow } from '$lib/data/types';
import { countryKey, flowKey, partnerKey, productKey, type TradeEntityId } from './entity';
import { describeScene, type SceneState } from './scene';

export interface SceneEntity<T> {
	id: TradeEntityId;
	kind: 'country' | 'partner' | 'flow' | 'product';
	label: string;
	parentId: TradeEntityId | null;
	selected: boolean;
	available: boolean;
	value: number;
	datum: T;
}

export interface TradeSceneGraph {
	id: string;
	label: string;
	country: SceneEntity<CountryProjection>;
	partners: SceneEntity<PartnerRow>[];
	selectedPartner: SceneEntity<PartnerRow> | null;
	flows: SceneEntity<PartnerRow>[];
	products: SceneEntity<CrossCell>[];
	path: TradeEntityId[];
}

export function deriveTradeScene(
	projection: CountryProjection,
	state: SceneState,
	topN = 9
): TradeSceneGraph {
	const yearRows = projection.partnersByYear[String(state.year)] ?? [];
	const named = yearRows
		.filter((row) => row.partner !== 'ROW' && row.exportAvailable && row.importAvailable)
		.slice()
		.sort((a, b) => b.exportsUsd + b.importsUsd - (a.exportsUsd + a.importsUsd))
		.slice(0, topN);
	const rest = yearRows.find((row) => row.partner === 'ROW');
	const visibleRows = rest ? [...named, rest] : named;
	const countryId = countryKey(state.reporter);

	const partners = visibleRows.map(
		(row): SceneEntity<PartnerRow> => ({
			id: partnerKey(state.reporter, row.partner),
			kind: 'partner',
			label: row.partner === 'ROW' ? 'Other countries' : row.partner,
			parentId: countryId,
			selected: row.partner === state.partner,
			available: row.exportAvailable || row.importAvailable,
			value: row.exportsUsd + row.importsUsd,
			datum: row
		})
	);

	const selectedRow = state.partner
		? (yearRows.find((row) => row.partner === state.partner) ?? null)
		: null;
	const selectedPartner = selectedRow
		? {
				id: partnerKey(state.reporter, selectedRow.partner),
				kind: 'partner' as const,
				label: selectedRow.partner,
				parentId: countryId,
				selected: true,
				available: selectedRow.exportAvailable || selectedRow.importAvailable,
				value: selectedRow.exportsUsd + selectedRow.importsUsd,
				datum: selectedRow
			}
		: null;

	const flows: SceneEntity<PartnerRow>[] = selectedRow
		? [
				{
					id: flowKey(state.reporter, selectedRow.partner, 'export'),
					kind: 'flow',
					label: 'Reported exports',
					parentId: partnerKey(state.reporter, selectedRow.partner),
					selected: state.flow === 'export',
					available: selectedRow.exportAvailable,
					value: selectedRow.exportsUsd,
					datum: selectedRow
				},
				{
					id: flowKey(state.reporter, selectedRow.partner, 'import'),
					kind: 'flow',
					label: 'Reported imports',
					parentId: partnerKey(state.reporter, selectedRow.partner),
					selected: state.flow === 'import',
					available: selectedRow.importAvailable,
					value: selectedRow.importsUsd,
					datum: selectedRow
				}
			]
		: [];

	const detailFlow = state.flow === 'export' ? 'export' : 'import';
	const products =
		state.partner && state.flow !== 'both'
			? projection.crossCells
					.filter((cell) => cell.partner === state.partner)
					.map(
						(cell): SceneEntity<CrossCell> => {
							const label = cell.product.replace(/^\d+-\d+_/, '');
							const available =
								detailFlow === 'export' ? cell.exportAvailable : cell.importAvailable;
							return {
								id: productKey(state.reporter, state.partner, detailFlow, label),
								kind: 'product',
								label,
								parentId: flowKey(state.reporter, state.partner!, detailFlow),
								selected: label === state.product,
								available,
								value: detailFlow === 'export' ? cell.exportsUsd : cell.importsUsd,
								datum: cell
							};
						}
					)
					.filter((entity) => entity.available && entity.value > 0)
					.sort((a, b) => b.value - a.value)
			: [];

	const path = [countryId];
	if (selectedPartner) path.push(selectedPartner.id);
	if (state.flow !== 'both' && flows.length) {
		const selectedFlow = flows.find((entity) => entity.selected);
		if (selectedFlow) path.push(selectedFlow.id);
	}
	const selectedProduct = products.find((entity) => entity.selected);
	if (selectedProduct) path.push(selectedProduct.id);

	return {
		id: `${state.reporter}:${state.year}:${state.representation}`,
		label: describeScene(state),
		country: {
			id: countryId,
			kind: 'country',
			label: projection.countryName,
			parentId: null,
			selected: !state.partner && !state.product,
			available: true,
			value:
				(projection.summaryByYear[String(state.year)]?.exportsUsd ?? 0) +
				(projection.summaryByYear[String(state.year)]?.importsUsd ?? 0),
			datum: projection
		},
		partners,
		selectedPartner,
		flows,
		products,
		path
	};
}
