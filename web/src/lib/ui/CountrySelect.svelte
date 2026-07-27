<script lang="ts">
	// Country picker. Brand input: solid 1px rule, 2px navy border on focus.
	import { onMount } from 'svelte';

	let ready = $state(false);
	onMount(() => {
		ready = true;
	});
	let {
		value,
		options,
		onchange
	}: {
		value: string;
		options: Array<{ code: string; name: string }>;
		onchange: (code: string) => void;
	} = $props();
</script>

<label class="wrap">
	<span class="eyebrow">Reporter</span>
	<select
		{value}
		data-ready={ready}
		onchange={(e) => onchange((e.currentTarget as HTMLSelectElement).value)}
	>
		{#each options as option (option.code)}
			<option value={option.code}>{option.name} · {option.code}</option>
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
