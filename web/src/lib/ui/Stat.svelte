<script lang="ts">
	// Number-led single fact (04-components.md): metric first, small label,
	// optional delta line, optional source/freshness line. Tabular figures.
	let {
		value,
		label,
		delta,
		deltaColor = 'var(--text-3)',
		source,
		size = 'md'
	}: {
		value: string;
		label: string;
		delta?: string;
		/** Colour for the delta line — e.g. deltaColor(balance) from theme/tokens. */
		deltaColor?: string;
		source?: string;
		size?: 'md' | 'lg';
	} = $props();
</script>

<div class="stat" class:lg={size === 'lg'}>
	<div class="value">{value}</div>
	<div class="label">{label}</div>
	{#if delta}<div class="delta" style:color={deltaColor}>{delta}</div>{/if}
	{#if source}<div class="source">{source}</div>{/if}
</div>

<style>
	.stat {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.value {
		font-size: 2rem;
		font-weight: 500;
		color: var(--text-1);
		line-height: 1.05;
		font-variant-numeric: tabular-nums;
	}
	.stat.lg .value {
		font-size: 2.75rem;
	}
	.label {
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-3);
	}
	.delta {
		font-size: 0.9rem;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}
	.source {
		font-size: 11px;
		color: var(--text-4);
		margin-top: 2px;
	}
</style>
