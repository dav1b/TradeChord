<script lang="ts">
	// Country picker. Brand input: solid 1px rule, 2px navy border on focus.
	let {
		value,
		options,
		onchange
	}: {
		value: string;
		options: string[];
		onchange: (code: string) => void;
	} = $props();
</script>

<label class="wrap">
	<span class="eyebrow">Reporter</span>
	<select {value} onchange={(e) => onchange((e.currentTarget as HTMLSelectElement).value)}>
		{#each options as code (code)}
			<option value={code}>{code}</option>
		{/each}
	</select>
</label>

<style>
	.wrap {
		display: inline-flex;
		flex-direction: column;
		gap: var(--space-1);
	}
	.eyebrow {
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-3);
	}
	select {
		font-family: var(--font-body);
		font-size: 1rem;
		font-weight: 500;
		color: var(--text-1);
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: var(--space-2) var(--space-3);
		min-width: 8rem;
		cursor: pointer;
	}
	select:focus {
		outline: none;
		border: 2px solid var(--active);
		padding: calc(var(--space-2) - 1px) calc(var(--space-3) - 1px);
	}
</style>
