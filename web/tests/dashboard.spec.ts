import { expect, test } from '@playwright/test';

test('dashboard navigation, country selection, cross-filtering, and overview', async ({ page }) => {
	const consoleErrors: string[] = [];
	page.on('console', (message) => {
		if (message.type() === 'error') consoleErrors.push(message.text());
	});

	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toContainText('United States');
	await expect(page.getByText('dual-flow release 2026-07.1')).toBeVisible();

	const reporter = page.getByLabel('Reporter');
	await expect(reporter).toHaveAttribute('data-ready', 'true');
	await reporter.selectOption('DEU');
	await expect(page).toHaveURL(/[?&]country=DEU/);
	await expect(page.getByRole('heading', { level: 1 })).toContainText('Germany');

	const partnerCard = page.locator('section.card').filter({ hasText: 'Partners · exports' });
	await partnerCard.getByRole('button').first().click();
	await expect(page.getByRole('button', { name: /Filtered ·/ })).toBeVisible();

	await page.goto('/all');
	await expect(page.getByRole('heading', { level: 1, name: 'Reporters' })).toBeVisible();
	await expect(page.locator('.cell')).toHaveCount(30);
	expect(consoleErrors).toEqual([]);
});
