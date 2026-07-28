import { motionDuration } from '$lib/motion';

export type RelationshipPhase =
	| 'network'
	| 'focused'
	| 'illuminating'
	| 'extracting'
	| 'opening'
	| 'relationship'
	| 'closing';

type PhaseSetter = (phase: RelationshipPhase) => void;

const openingSequence: Array<{ phase: RelationshipPhase; duration: number }> = [
	{ phase: 'illuminating', duration: 150 },
	{ phase: 'extracting', duration: 380 },
	{ phase: 'opening', duration: 220 }
];

function wait(duration: number) {
	return new Promise<void>((resolve) => window.setTimeout(resolve, motionDuration(duration)));
}

/**
 * Fulfil one OPEN_RELATIONSHIP intent through visual phases. `isCurrent`
 * invalidates stale work when the user retargets or reverses mid-transition.
 */
export async function openRelationshipSequence(
	isCurrent: () => boolean,
	setPhase: PhaseSetter
) {
	for (const step of openingSequence) {
		if (!isCurrent()) return;
		setPhase(step.phase);
		await wait(step.duration);
	}
	if (isCurrent()) setPhase('relationship');
}

export async function closeRelationshipSequence(
	isCurrent: () => boolean,
	setPhase: PhaseSetter
) {
	if (!isCurrent()) return;
	setPhase('closing');
	await wait(480);
	if (isCurrent()) setPhase('network');
}
