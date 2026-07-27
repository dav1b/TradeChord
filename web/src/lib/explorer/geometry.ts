import type { TradeEntityId } from './entity';

export interface Point {
	x: number;
	y: number;
}

export interface RectGeometry {
	x: number;
	y: number;
	width: number;
	height: number;
}

export interface PathGeometry {
	path: string;
	centroid?: Point;
}

export interface LineGeometry {
	points: Point[];
}

export interface SceneMark<G> {
	entityId: TradeEntityId;
	geometry: G;
	opacity: number;
	order: number;
}

export interface SceneGeometry {
	rects: SceneMark<RectGeometry>[];
	paths: SceneMark<PathGeometry>[];
	lines: SceneMark<LineGeometry>[];
}
