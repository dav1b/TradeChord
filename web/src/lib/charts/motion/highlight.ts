export type HighlightStyle = 'illuminate';

export type HighlightPresentation = {
	opacity: number;
	saturation: number;
	strokeOpacity: number;
};

export function ribbonHighlight(
	style: HighlightStyle,
	energy: number,
	focus: number
): HighlightPresentation {
	switch (style) {
		case 'illuminate':
			return {
				opacity: 0.3 * (1 - focus * 0.76) + energy * 0.72,
				saturation: 1 + energy * 0.3,
				strokeOpacity: energy * 0.45
			};
	}
}
