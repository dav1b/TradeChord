<script lang="ts">
	// DataJockey design system: tokens, font-faces, reset, and base styles.
	// Global entry point for the whole app.
	import '$lib/theme/dj-design.css';
	import '$lib/theme/app.css';
	import TooltipLayer from '$lib/ui/TooltipLayer.svelte';

	let { children } = $props();
</script>

{@render children()}
<TooltipLayer />
