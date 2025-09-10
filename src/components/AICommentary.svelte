<script lang="ts">
	import { aiCommentaryService, type AICommentary } from '$lib/services/aiCommentary';
	import { extractCountrySummary } from '$lib/utils/dataExtraction';
	import type { TradeRecord } from '$lib/utils/transform';

	export let data: TradeRecord[] = [];
	export let productData: TradeRecord[] = [];
	export let countryCode: string = '';
	export let year: string = '2022';

	let isLoading = false;
	let error = '';
	let commentary: AICommentary | null = null;
	let apiKey = '';
	let showApiKeyInput = true;

	async function generateCommentary() {
		if (!apiKey.trim()) {
			error = 'Please enter your OpenAI API key';
			return;
		}

		isLoading = true;
		error = '';
		commentary = null;

		try {
			aiCommentaryService.setApiKey(apiKey);
			const countrySummary = extractCountrySummary(data, productData, countryCode, year);
			commentary = await aiCommentaryService.generateCommentary(countrySummary);
			showApiKeyInput = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to generate commentary';
		} finally {
			isLoading = false;
		}
	}

	function resetCommentary() {
		commentary = null;
		error = '';
		showApiKeyInput = true;
		apiKey = '';
	}
</script>

<div class="ai-commentary">
	{#if showApiKeyInput}
		<div class="api-key-section">
			<h3>AI Economic Commentary</h3>
			<p>Get professional economic analysis powered by AI. Enter your OpenAI API key to continue.</p>
			<div class="input-group">
				<input
					type="password"
					bind:value={apiKey}
					placeholder="Enter your OpenAI API key"
					class="api-key-input"
					disabled={isLoading}
				/>
				<button
					on:click={generateCommentary}
					disabled={isLoading || !apiKey.trim()}
					class="generate-btn"
				>
					{isLoading ? 'Generating...' : 'Generate Commentary'}
				</button>
			</div>
		</div>
	{:else if commentary}
		<div class="commentary-section">
			<div class="commentary-header">
				<h3>AI Economic Commentary</h3>
				<button on:click={resetCommentary} class="reset-btn">New Analysis</button>
			</div>
			
			{#if error}
				<div class="error-message">{error}</div>
			{/if}

			<div class="commentary-content">
				<!-- Overall Analysis -->
				<section class="commentary-section-item">
					<h4>Overall Economic Assessment</h4>
					<div class="commentary-text">{@html commentary.overall}</div>
				</section>

				<!-- Chart-specific Analysis -->
				<section class="commentary-section-item">
					<h4>Trade Flow Network Analysis</h4>
					<div class="commentary-text">{@html commentary.chordDiagram}</div>
				</section>

				<section class="commentary-section-item">
					<h4>Export Product Analysis</h4>
					<div class="commentary-text">{@html commentary.productTreemap}</div>
				</section>

				<section class="commentary-section-item">
					<h4>Export Trends Analysis</h4>
					<div class="commentary-text">{@html commentary.exportsSlope}</div>
				</section>

				<section class="commentary-section-item">
					<h4>Import Trends Analysis</h4>
					<div class="commentary-text">{@html commentary.importsSlope}</div>
				</section>

				<!-- Key Insights -->
				{#if commentary.keyInsights && commentary.keyInsights.length > 0}
					<section class="commentary-section-item">
						<h4>Key Insights</h4>
						<ul class="insights-list">
							{#each commentary.keyInsights as insight}
								<li class="insight-item">{insight}</li>
							{/each}
						</ul>
					</section>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.ai-commentary {
		background: #f8f9fa;
		border-radius: 8px;
		padding: 20px;
		margin: 20px 0;
		border: 1px solid #e9ecef;
	}

	.api-key-section h3 {
		margin: 0 0 10px 0;
		color: #333;
		font-size: 1.2em;
	}

	.api-key-section p {
		margin: 0 0 15px 0;
		color: #666;
		font-size: 0.9em;
	}

	.input-group {
		display: flex;
		gap: 10px;
		align-items: center;
	}

	.api-key-input {
		flex: 1;
		padding: 10px;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 14px;
	}

	.generate-btn, .reset-btn {
		padding: 10px 20px;
		background: #007bff;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 14px;
		transition: background-color 0.2s;
	}

	.generate-btn:hover:not(:disabled) {
		background: #0056b3;
	}

	.generate-btn:disabled {
		background: #6c757d;
		cursor: not-allowed;
	}

	.reset-btn {
		background: #6c757d;
		font-size: 12px;
		padding: 8px 16px;
	}

	.reset-btn:hover {
		background: #545b62;
	}

	.commentary-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
	}

	.commentary-header h3 {
		margin: 0;
		color: #333;
		font-size: 1.3em;
	}

	.commentary-content {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.commentary-section-item {
		background: white;
		padding: 20px;
		border-radius: 6px;
		border-left: 4px solid #007bff;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.commentary-section-item h4 {
		margin: 0 0 15px 0;
		color: #333;
		font-size: 1.1em;
		font-weight: 600;
	}

	.commentary-text {
		line-height: 1.6;
		color: #444;
		font-size: 14px;
	}


	.insights-list {
		margin: 0;
		padding-left: 20px;
	}

	.insight-item {
		margin-bottom: 8px;
		line-height: 1.5;
		color: #444;
	}

	.error-message {
		background: #f8d7da;
		color: #721c24;
		padding: 10px;
		border-radius: 4px;
		margin-bottom: 15px;
		border: 1px solid #f5c6cb;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.input-group {
			flex-direction: column;
		}
		
		.api-key-input {
			width: 100%;
		}
		
		.commentary-header {
			flex-direction: column;
			gap: 10px;
			align-items: flex-start;
		}
	}
</style>
