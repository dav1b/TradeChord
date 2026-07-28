<script lang="ts">
	import MotionChord from '$lib/charts/MotionChord.svelte';
	import type { HighlightStyle } from '$lib/charts/motion/highlight';
	import {
		openRelationshipSequence,
		type RelationshipPhase
	} from '$lib/charts/motion/relationship-choreography';
	import Wordmark from '$lib/ui/Wordmark.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let phase = $state<RelationshipPhase>('network');
	let highlightStyle = $state<HighlightStyle>('illuminate');
	let selected = $state<string | null>(null);
	let choreographyRevision = 0;

	function selectPartner(partner: string | null) {
		const revision = ++choreographyRevision;
		selected = partner;
		if (!partner) {
			phase = 'network';
			return;
		}
		void openRelationshipSequence(
			() => revision === choreographyRevision,
			(nextPhase) => (phase = nextPhase)
		);
	}

	function closeRelationship() {
		choreographyRevision += 1;
		phase = 'focused';
	}
</script>

<svelte:head>
	<title>TradeChord motion laboratory</title>
	<meta
		name="description"
		content="An isolated motion study for fluid, semantic chord-ribbon interaction."
	/>
</svelte:head>

<main class="lab">
	<Wordmark />
	<header>
		<div>
			<p>Motion laboratory · {data.year}</p>
			<h1>{data.reporterName} <span>{data.reporter}</span></h1>
		</div>
		<div class="mode" role="group" aria-label="Relationship motion study">
			<button
				class:active={highlightStyle === 'illuminate'}
				aria-pressed={highlightStyle === 'illuminate'}
				onclick={() => (highlightStyle = 'illuminate')}>Illuminate</button
			>
			<span>{phase}</span>
		</div>
	</header>

	<section class="canvas" aria-labelledby="instruction">
		<p id="instruction">
			{selected
				? phase === 'relationship'
					? `${selected} relationship · the bridge now owns the selected entity`
					: `${selected} · ${phase} · choose another ribbon to retarget`
				: 'Select a ribbon · reported geometry stays fixed while the relationship comes forward'}
		</p>
		<div class="diagram">
			<MotionChord
				reporter={data.reporter}
				rows={data.rows}
				summary={data.summary}
				{phase}
				{highlightStyle}
				onselect={selectPartner}
				onclose={closeRelationship}
			/>
		</div>
	</section>

	<footer>
		<span>WITS · release {data.version}</span>
		<span>{phase === 'relationship' ? 'Relationship bridge' : 'Fixed-geometry illumination'}</span>
	</footer>
</main>

<style>
	:global(body) {
		background: var(--bg);
	}
	.lab {
		position: relative;
		display: flex;
		flex-direction: column;
		width: 100vw;
		min-height: 100svh;
		padding: var(--space-5);
	}
	header {
		z-index: 1;
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: var(--space-5);
		padding-top: var(--space-3);
	}
	header p,
	.canvas > p,
	footer {
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-4);
	}
	h1 {
		margin-top: 4px;
		font-size: clamp(1.7rem, 4vw, 3rem);
		font-weight: 500;
		color: var(--text-1);
	}
	h1 span {
		font-family: var(--font-mono);
		font-size: 0.38em;
		color: var(--text-3);
		vertical-align: middle;
	}
	.mode {
		display: inline-flex;
		padding: 3px;
		border: 1px solid var(--border);
		border-radius: 999px;
		background: var(--surface);
	}
	.mode button {
		border: 0;
		border-radius: 999px;
		padding: 7px 11px;
		background: transparent;
		color: var(--text-3);
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		cursor: pointer;
	}
	.mode button.active {
		color: var(--text-1);
		font-weight: 700;
	}
	.mode span {
		align-self: center;
		padding: 0 9px;
		font-family: var(--font-mono);
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-4);
	}
	.mode button:focus-visible {
		outline: 2px solid var(--active);
		outline-offset: 3px;
	}
	.canvas {
		position: relative;
		display: grid;
		grid-template-rows: auto auto;
		gap: var(--space-3);
		padding-top: var(--space-6);
	}
	.canvas > p {
		z-index: 1;
		width: min(90vw, 70ch);
		margin-inline: auto;
		text-align: center;
	}
	.diagram {
		position: relative;
		width: 100%;
		height: min(90vw, 90svh, 960px);
		min-height: min(90vw, 420px);
	}
	footer {
		display: flex;
		justify-content: space-between;
		gap: var(--space-3);
		padding-top: var(--space-2);
		border-top: 1px solid var(--border-faint);
	}
	@media (max-width: 640px) {
		.lab {
			padding: var(--space-4);
		}
		header {
			align-items: flex-start;
			flex-direction: column;
			gap: var(--space-3);
		}
		.mode {
			align-self: stretch;
		}
		.mode button {
			flex: 1;
		}
		.canvas > p {
			width: 100%;
		}
		.diagram {
			height: min(92vw, 560px);
			min-height: 320px;
		}
	}
</style>
