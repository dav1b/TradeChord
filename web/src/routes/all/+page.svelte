<script lang="ts">
	import Wordmark from '$lib/ui/Wordmark.svelte';
	import MiniTrend from '$lib/charts/MiniTrend.svelte';
	import { usd, usdSigned } from '$lib/format';
	import { deltaColor } from '$lib/theme/tokens';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const reporters = $derived(
		data.overview.reporters
			.map((r) => {
				const latest = r.totalsByYear[r.totalsByYear.length - 1];
				return {
					code: r.code,
					latest,
					series: r.totalsByYear.map((t) => ({ year: t.year, value: t.balanceUsd }))
				};
			})
			.sort((a, b) => b.latest.exportsUsd - a.latest.exportsUsd)
	);
</script>

<Wordmark />

<div class="page">
	<header class="head">
		<div>
			<p class="eyebrow">Global trade · {data.overview.defaultYear}</p>
			<h1>Reporters</h1>
		</div>
		<a class="link" href="/">Single country →</a>
	</header>

	<div class="grid">
		{#each reporters as r (r.code)}
			<a class="cell" href="/?country={r.code}">
				<div class="top">
					<span class="code">{r.code}</span>
					<span class="bal" style:color={deltaColor(r.latest.balanceUsd)}>
						{usdSigned(r.latest.balanceUsd)}
					</span>
				</div>
				<MiniTrend series={r.series} color={deltaColor(r.latest.balanceUsd)} />
				<div class="sub">exp {usd(r.latest.exportsUsd)} · imp {usd(r.latest.importsUsd)}</div>
			</a>
		{/each}
	</div>

	<footer class="foot">
		<span>Source: World Bank WITS · dual-flow release {data.version}</span>
		<span>DataJockey</span>
	</footer>
</div>

<style>
	.page {
		max-width: var(--maxw);
		margin: 0 auto;
		padding: var(--space-6) var(--space-5) var(--space-8);
		display: flex;
		flex-direction: column;
		gap: var(--space-6);
	}
	.head {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: var(--space-4);
		flex-wrap: wrap;
	}
	.eyebrow {
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-3);
	}
	h1 {
		font-size: 2.5rem;
		font-weight: 500;
		color: var(--text-1);
		letter-spacing: -0.01em;
	}
	.link {
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--accent);
		text-decoration: none;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
		gap: var(--space-3);
	}
	.cell {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: var(--space-3);
		text-decoration: none;
		transition: border-color var(--motion-fast) var(--ease);
	}
	.cell:hover {
		border-color: var(--active);
	}
	.top {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
	}
	.code {
		font-size: 1.1rem;
		font-weight: 600;
		color: var(--text-1);
	}
	.bal {
		font-size: 0.9rem;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}
	.sub {
		font-family: var(--font-mono);
		font-size: 10px;
		color: var(--text-3);
	}
	.foot {
		display: flex;
		justify-content: space-between;
		gap: var(--space-3);
		flex-wrap: wrap;
		font-size: 11px;
		color: var(--text-4);
		border-top: 1px solid var(--border-faint);
		padding-top: var(--space-4);
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 2rem;
		}
		.page {
			padding: var(--space-5) var(--space-4) var(--space-6);
		}
		.head {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
