import OpenAI from 'openai';

// Types for structured data extraction
export interface ChartData {
	chartType: string;
	title: string;
	data: any;
	insights: string[];
}

export interface CountrySummary {
	countryCode: string;
	countryName: string;
	year: string;
	totalExports: number;
	totalImports: number;
	tradeBalance: number;
	topPartners: Array<{
		country: string;
		exports: number;
		imports: number;
		balance: number;
	}>;
	chartData: ChartData[];
}

export interface AICommentary {
	overall: string;
	chordDiagram: string;
	productTreemap: string;
	exportsSlope: string;
	importsSlope: string;
	keyInsights: string[];
}

class AICommentaryService {
	private openai: OpenAI | null = null;
	private apiKey: string | null = null;

	constructor() {
		// API key will be set via environment variable or user input
		this.apiKey = import.meta.env.VITE_OPENAI_API_KEY || null;
		if (this.apiKey) {
			this.openai = new OpenAI({
				apiKey: this.apiKey,
				dangerouslyAllowBrowser: true // For client-side usage
			});
		}
	}

	setApiKey(apiKey: string) {
		this.apiKey = apiKey;
		this.openai = new OpenAI({
			apiKey: this.apiKey,
			dangerouslyAllowBrowser: true
		});
	}

	async generateCommentary(countrySummary: CountrySummary): Promise<AICommentary> {
		if (!this.openai) {
			throw new Error('OpenAI API key not set. Please provide your API key.');
		}

		const prompt = this.buildPrompt(countrySummary);
		
		try {
			const completion = await this.openai.chat.completions.create({
				model: "gpt-4",
				messages: [
					{
						role: "system",
						// content: "You are a world-class economics journalist. Given structured trade data for a specific country, write a concise but insightful overview paragraph, and four chart-specific commentary blocks that correspond to the dashboard visualizations. Use clear, punchy newspaper prose. Focus on trends, turning points, and strategic implications. You must Include references to notable events, major trading partners, and product shifts. The tone should be professional, informative, and accessible. The dashboard covers trade flows from 2002–2022."
                        content: `You are an investigative economics journalist and trade analyst for a high-quality publication like The Economist or Financial Times. Your job is to generate engaging, story-driven commentary for a trade dashboard based on structured trade data covering 2002 to 2022.
The dashboard includes:
	•	A chord diagram of trade flows between countries
	•	A product breakdown of exports and imports (with growth rates)
	•	A slope chart of top export partners over time
	•	A slope chart of top import partners over time

The user will provide structured inputs about a specific country, including:
	•	Trade values and balances
	•	Top partners and product categories
	•	Growth or decline of relationships over time
	•	Contextual metadata (notable events, major companies, trade agreements, political changes)

You must write:
	1.	A Top-Level Commentary summarizing that country’s trade story over 20 years
	2.	Four Chart-Specific Commentaries (one per chart)

Your tone should be narrative, engaging, sharp, and curious, like a Sunday magazine feature.
The writing should not simply describe the numbers—it should connect them to real-world events, such as:
	•	Major trade deals (e.g., WTO accession, CPTPP)
	•	Political events (e.g., sanctions, revolutions, elections)
	•	Corporate shifts (e.g., rise of Samsung in Vietnam, Tesla’s Gigafactory in Germany)
	•	Geopolitical tensions (e.g., US-China tariffs, Brexit)
	•	Natural disasters or pandemics (e.g., 2008 crisis, COVID-19)

Do not hedge too much. Be bold. Infer plausible connections where the evidence is strong. Your job is not to be neutral—it is to be insightful and tell the story behind the numbers.

Write for an audience of curious policymakers, economists, and business leaders who want to understand how the real world shaped this trade data—and what it might mean for the future.`


                    },
					{
						role: "user",
						content: prompt
					}
				],
				temperature: 0.7,
				max_tokens: 2000
			});

			const response = completion.choices[0]?.message?.content;
			if (!response) {
				throw new Error('No response from OpenAI');
			}

			return this.parseResponse(response);
		} catch (error) {
			console.error('Error generating AI commentary:', error);
			throw new Error('Failed to generate AI commentary. Please check your API key and try again.');
		}
	}

	private buildPrompt(countrySummary: CountrySummary): string {
		return `
Analyze the following international trade data for ${countrySummary.countryName} (${countrySummary.countryCode}) in ${countrySummary.year}:

## Trade Overview
- Total Exports: $${(countrySummary.totalExports / 1e9).toFixed(1)}B
- Total Imports: $${(countrySummary.totalImports / 1e9).toFixed(1)}B
- Trade Balance: $${(countrySummary.tradeBalance / 1e9).toFixed(1)}B

## Top Trading Partners
${countrySummary.topPartners.map(partner => 
	`- ${partner.country}: Exports $${(partner.exports / 1e9).toFixed(1)}B, Imports $${(partner.imports / 1e9).toFixed(1)}B, Balance $${(partner.balance / 1e9).toFixed(1)}B`
).join('\n')}

## Chart Analysis
${countrySummary.chartData.map(chart => 
	`### ${chart.title} (${chart.chartType})
${chart.insights.join('\n')}`
).join('\n\n')}

Please provide a comprehensive economic analysis in the following JSON format:
{
	"overall": "Overall economic assessment of the country's trade position...",
	"chordDiagram": "Analysis of the chord diagram showing trade relationships...",
	"productTreemap": "Analysis of the product breakdown and export composition...",
	"exportsSlope": "Analysis of export trends and partner concentration...",
	"importsSlope": "Analysis of import trends and supplier diversification...",
	"keyInsights": [
		"Key insight 1",
		"Key insight 2",
		"Key insight 3"
	]
}

Focus on:
1. Trade balance implications for economic health
2. Geographic concentration risks and opportunities
3. Product diversification and competitiveness
4. Trends and year-over-year changes
5. Strategic implications for policymakers and businesses
6. Comparison to global trade patterns
`;
	}

	private parseResponse(response: string): AICommentary {
		try {
			// Try to extract JSON from the response
			const jsonMatch = response.match(/\{[\s\S]*\}/);
			if (jsonMatch) {
				return JSON.parse(jsonMatch[0]);
			}
			
			// Fallback: create a structured response from plain text
			return {
				overall: response,
				chordDiagram: "Analysis not available",
				productTreemap: "Analysis not available", 
				exportsSlope: "Analysis not available",
				importsSlope: "Analysis not available",
				keyInsights: ["Analysis generated successfully"]
			};
		} catch (error) {
			console.error('Error parsing AI response:', error);
			return {
				overall: response,
				chordDiagram: "Analysis not available",
				productTreemap: "Analysis not available",
				exportsSlope: "Analysis not available", 
				importsSlope: "Analysis not available",
				keyInsights: ["Analysis generated successfully"]
			};
		}
	}
}

export const aiCommentaryService = new AICommentaryService();
