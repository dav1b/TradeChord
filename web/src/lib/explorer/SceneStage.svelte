<script lang="ts">
	import { tick, type Snippet } from 'svelte';
	import type { TradeSceneGraph } from './scene-graph';
	import type { SceneTransition } from './scene';
	import { provideSceneViewport } from './scene-viewport.svelte';

	let {
		graph,
		transition,
		children
	}: {
		graph: TradeSceneGraph;
		transition: SceneTransition;
		children: Snippet;
	} = $props();

	let stage: HTMLElement;
	let width = $state(0);
	const viewport = provideSceneViewport();
	let handledRevision = -1;

	$effect(() => {
		viewport.update(width);
	});

	$effect(() => {
		const revision = transition.revision;
		const focusEntity = transition.focusEntity;
		if (!stage || revision <= handledRevision || revision === 0) return;
		handledRevision = revision;
		void tick().then(() => {
			if (!focusEntity || revision !== transition.revision) return;
			const started = performance.now();
			function transferFocus() {
				if (revision !== transition.revision) return;
				// During crossfade both representations may briefly share the
				// semantic ID. Prefer the newly inserted (later) element.
				const target = Array.from(
					stage.querySelectorAll<HTMLElement>('[data-entity-id]')
				)
					.reverse()
					.find((element) => element.dataset.entityId === focusEntity && !element.inert);
				if (target) {
					target.focus({ preventScroll: true });
					return;
				}
				if (performance.now() - started < 800) requestAnimationFrame(transferFocus);
			}
			transferFocus();
		});
	});
</script>

<section
	bind:this={stage}
	bind:clientWidth={width}
	class="stage"
	data-scene={graph.id}
	data-layout={viewport.mode}
	data-direction={transition.direction}
	aria-label={graph.label}
>
	<span class="announcement" aria-live="polite" aria-atomic="true">
		{transition.announcement}
	</span>
	{@render children()}
</section>

<style>
	.stage {
		min-height: 340px;
		container: trade-scene / inline-size;
	}
	.announcement {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border: 0;
	}
</style>
