<script lang="ts">
	import MotionChord, { type MotionMode } from '$lib/charts/MotionChord.svelte';
	import Wordmark from '$lib/ui/Wordmark.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let mode = $state<MotionMode>('breathe');
	let selected = $state<string | null>(null);
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
		<div class="mode" role="group" aria-label="Ribbon motion study">
			<button
				class:active={mode === 'breathe'}
				aria-pressed={mode === 'breathe'}
				onclick={() => (mode = 'breathe')}>Focus & breathe</button
			>
			<button
				class:active={mode === 'extract'}
				aria-pressed={mode === 'extract'}
				onclick={() => (mode = 'extract')}>Ribbon extraction</button
			>
		</div>
	</header>

	<section class="canvas" aria-labelledby="instruction">
		<p id="instruction">
			{selected
				? `${selected} selected · click another ribbon to retarget · Escape to reset`
				: 'Select a ribbon · the relationship stays in place while its geometry responds'}
		</p>
		<div class="diagram">
			<MotionChord
				reporter={data.reporter}
				rows={data.rows}
				summary={data.summary}
				{mode}
				onselect={(partner) => (selected = partner)}
			/>
		</div>
	</section>

	<footer>
		<span>WITS · release {data.version}</span>
		<span>{mode === 'breathe' ? 'Geometry emphasis' : 'Spatial extraction'}</span>
	</footer>
</main>

<style>
	:global(body) {
		overflow: hidden;
		background: var(--bg);
	}
	.lab {
		position: relative;
		display: grid;
		grid-template-rows: auto auto minmax(0, 1fr) auto;
		width: 100vw;
		height: 100svh;
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
		background: var(--active);
		color: var(--active-ink);
	}
	.mode button:focus-visible {
		outline: 2px solid var(--active);
		outline-offset: 3px;
	}
	.canvas {
		position: relative;
		min-height: 0;
	}
	.canvas > p {
		position: absolute;
		top: var(--space-4);
		left: 50%;
		z-index: 1;
		width: min(90vw, 70ch);
		transform: translateX(-50%);
		text-align: center;
	}
	.diagram {
		position: absolute;
		inset: 0;
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
			top: var(--space-3);
		}
	}
</style>
