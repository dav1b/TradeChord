<script lang="ts">
	// DataJockey design system: tokens, font-faces, reset, and base styles.
	// Global entry point for the whole app.
	import '$lib/theme/dj-design.css';
	import '$lib/theme/app.css';
	import TooltipLayer from '$lib/ui/TooltipLayer.svelte';
	import { navigating } from '$app/state';

	let { children } = $props();
</script>

{@render children()}
{#if navigating.to}
	<div class="loading" role="status" aria-live="polite">Loading trade data…</div>
{/if}
<TooltipLayer />

<style>
	.loading {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
		padding: 4px var(--space-3);
		background: var(--active);
		color: var(--active-ink);
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.05em;
		text-align: center;
		text-transform: uppercase;
	}
</style>
