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

	const networkCard = page.locator('section.card').filter({ hasText: 'Trade network · top partners' });
	const firstRibbon = networkCard.locator('svg path[role="button"][tabindex="0"]').first();
	await firstRibbon.focus();
	await firstRibbon.press('Enter');
	await expect(page).toHaveURL(/[?&]view=relationship/);
	await expect(page.getByText('Bilateral relationship · 2022')).toBeVisible();
	await expect(page.getByText('Reported exports', { exact: true })).toBeVisible();
	await expect(page.getByText('Reported imports', { exact: true })).toBeVisible();
	await page.getByRole('button', { name: 'Network', exact: true }).first().click();
	await expect(page).not.toHaveURL(/[?&]view=relationship/);
	const retainedFilter = page.getByRole('button', { name: /Filtered ·/ });
	await expect(retainedFilter).toBeVisible();
	await retainedFilter.click();

	await page.getByRole('button', { name: 'Rank partners' }).click();
	await expect(page).toHaveURL(/[?&]view=rank/);
	const ranking = page.getByRole('list', { name: 'Partners ranked by total trade' });
	await expect(ranking).toBeVisible();
	const rankedPartner = ranking.getByRole('button').first();
	await rankedPartner.click();
	await expect(page).toHaveURL(/[?&]partner=/);
	await expect(rankedPartner).toHaveAttribute('aria-pressed', 'true');

	await page.goBack();
	await expect(page).toHaveURL(/[?&]view=rank/);
	await expect(page).not.toHaveURL(/[?&]partner=/);

	await page.getByRole('button', { name: 'Network', exact: true }).click();
	await expect(page).not.toHaveURL(/[?&]view=rank/);

	const partnerCard = page.locator('section.card').filter({ hasText: 'Partners · exports' });
	await partnerCard.getByRole('button').first().click();
	await expect(page.getByRole('button', { name: /Filtered ·/ })).toBeVisible();

	await page.goto('/?country=DEU&view=rank&partner=CHN');
	await expect(page.getByRole('button', { name: 'Rank partners' })).toHaveAttribute(
		'aria-pressed',
		'true'
	);
	await expect(page.getByRole('list', { name: 'Partners ranked by total trade' })).toBeVisible();

	await page.goto('/?country=DEU&view=relationship&partner=CHN');
	await expect(page.getByText('DEU ↔ CHN')).toBeVisible();
	await expect(page.getByText('Reported balance')).toBeVisible();
	await page.getByRole('button', { name: 'Open reported import product composition' }).click();
	await expect(page).toHaveURL(/[?&]view=products/);
	await expect(page).toHaveURL(/[?&]flow=import/);
	await expect(page.getByRole('heading', { name: 'Reported imports by product' })).toBeVisible();
	const productMap = page.locator('.treemap');
	const firstProduct = productMap.getByRole('button').first();
	await expect(firstProduct).toBeVisible();
	await firstProduct.focus();
	await firstProduct.press('Enter');
	await expect(firstProduct).toHaveAttribute('aria-pressed', 'true');
	await expect(page).toHaveURL(/[?&]product=/);
	await page
		.getByRole('navigation', { name: 'Analytical path' })
		.getByRole('button', { name: 'CHN', exact: true })
		.click();
	await expect(page).toHaveURL(/[?&]view=relationship/);
	await expect(page.getByText('DEU ↔ CHN')).toBeVisible();

	await page.goto('/?country=DEU&view=products&partner=CHN&flow=import&product=MachElec');
	await expect(page.getByRole('heading', { name: 'Reported imports by product' })).toBeVisible();
	await expect(page.locator('[data-entity-id$=\"MachElec\"]')).toHaveAttribute(
		'aria-pressed',
		'true'
	);

	await page.goto('/all');
	await expect(page.getByRole('heading', { level: 1, name: 'Reporters' })).toBeVisible();
	await expect(page.locator('.cell')).toHaveCount(30);
	expect(consoleErrors).toEqual([]);
});
