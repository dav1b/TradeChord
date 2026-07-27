<script lang="ts">
	import { page } from '$app/state';
	import Wordmark from '$lib/ui/Wordmark.svelte';
</script>

<Wordmark />
<main>
	<p class="eyebrow">Data could not be loaded</p>
	<h1>{page.status}</h1>
	<p>{page.error?.message ?? 'The selected TradeChord release is unavailable.'}</p>
	<a href="/">Return to the dashboard</a>
</main>

<style>
	main {
		max-width: 48rem;
		margin: 0 auto;
		padding: var(--space-8) var(--space-5);
	}
	.eyebrow, a {
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}
	h1 {
		margin: var(--space-2) 0;
		font-size: 3rem;
	}
	p {
		margin-bottom: var(--space-5);
		color: var(--text-3);
	}
	a {
		color: var(--accent);
	}
</style>
