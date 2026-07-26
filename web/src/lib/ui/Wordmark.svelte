<script lang="ts">
	// DataJockey wordmark, fixed upper-right per 05-dashboard-application.md:
	// 22px tall, opacity 0.7, never a click target on a data view.
	let { variant = 'navy' }: { variant?: 'navy' | 'carbon' | 'parchment' } = $props();
</script>

<img class="wordmark" src="/brand/wordmark-{variant}.svg" alt="DataJockey" />

<style>
	.wordmark {
		position: fixed;
		top: 16px;
		right: 20px;
		height: 22px;
		width: auto;
		opacity: 0.7;
		pointer-events: none;
		z-index: 50;
	}
</style>
