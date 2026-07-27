import { defineConfig, devices } from '@playwright/test';

const remoteBaseURL = process.env.PLAYWRIGHT_BASE_URL;

export default defineConfig({
	testDir: './tests',
	fullyParallel: false,
	retries: process.env.CI ? 2 : 0,
	reporter: process.env.CI ? 'github' : 'list',
	use: {
		baseURL: remoteBaseURL ?? 'http://127.0.0.1:4173',
		trace: 'on-first-retry'
	},
	projects: [
		{
			name: 'chromium',
			use: { ...devices['Desktop Chrome'] }
		}
	],
	webServer: remoteBaseURL
		? undefined
		: {
				command: 'node node_modules/vite/bin/vite.js dev --host 127.0.0.1 --port 4173',
				url: 'http://127.0.0.1:4173',
				reuseExistingServer: !process.env.CI
			}
});
