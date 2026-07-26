<script lang="ts">
	// Single cursor-following overlay, mounted once. Flips near the viewport edges.
	import Tooltip from './Tooltip.svelte';
	import { tip } from './tradepoint.svelte';

	const OFFSET = 16;
	const APPROX_W = 260;
	const APPROX_H = 170;

	const vw = $derived(typeof window === 'undefined' ? 0 : window.innerWidth);
	const vh = $derived(typeof window === 'undefined' ? 0 : window.innerHeight);
	const left = $derived(tip.x + OFFSET + APPROX_W > vw ? tip.x - OFFSET - APPROX_W : tip.x + OFFSET);
	const top = $derived(tip.y + OFFSET + APPROX_H > vh ? tip.y - OFFSET - APPROX_H : tip.y + OFFSET);
</script>

{#if tip.point}
	<div class="layer" style:left="{left}px" style:top="{top}px" aria-hidden="true">
		<Tooltip point={tip.point} />
	</div>
{/if}

<style>
	.layer {
		position: fixed;
		z-index: 100;
		pointer-events: none;
	}
</style>
