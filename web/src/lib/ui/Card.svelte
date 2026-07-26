<script lang="ts">
	// Surface container for a chart or grouped content.
	// Brand: white surface, solid 1px rule, no drop shadow. Optional eyebrow title
	// and a mandatory-by-convention source/freshness line (04/05-*.md).
	import type { Snippet } from 'svelte';

	let {
		title,
		source,
		theme,
		children
	}: {
		title?: string;
		source?: string;
		/** Surface-theme band, e.g. 'navy' | 'carbon' | 'alabaster'. */
		theme?: 'navy' | 'carbon' | 'alabaster';
		children: Snippet;
	} = $props();
</script>

<section class="card" class:dj-theme-navy={theme === 'navy'} class:dj-theme-carbon={theme === 'carbon'} class:dj-theme-alabaster={theme === 'alabaster'}>
	{#if title}<h3 class="eyebrow">{title}</h3>{/if}
	<div class="body">{@render children()}</div>
	{#if source}<p class="source">{source}</p>{/if}
</section>

<style>
	.card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: var(--space-4);
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}
	.eyebrow {
		font-family: var(--font-mono);
		font-weight: 400;
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-3);
	}
	.body {
		flex: 1;
		min-width: 0;
	}
	.source {
		font-size: 11px;
		color: var(--text-4);
	}
</style>
