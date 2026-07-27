import { expect, test } from '@playwright/test';

test('dashboard navigation, country selection, cross-filtering, and overview', async ({ page }) => {
	const consoleErrors: string[] = [];
	page.on('console', (message) => {
		if (message.type() === 'error') consoleErrors.push(message.text());
	});

	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toContainText('United States');
	await expect(page.getByText('dual-flow release 2026-07.1').first()).toBeVisible();
	await expect(
		page.getByRole('heading', {
			level: 2,
			name: 'How is USA connected to its trading partners?'
		})
	).toBeVisible();

	const reporter = page.getByLabel('Reporter');
	await expect(reporter).toHaveAttribute('data-ready', 'true');
	await reporter.selectOption('DEU');
	await expect(page).toHaveURL(/[?&]country=DEU/);
	await expect(page.getByRole('heading', { level: 1 })).toContainText('Germany');

	const tradeScene = page.locator('section.trade-scene');
	const firstRibbon = tradeScene.locator('svg path[role="button"][tabindex="0"]').first();
	await firstRibbon.focus();
	await firstRibbon.press('Enter');
	await expect(page).toHaveURL(/[?&]view=relationship/);
	await expect(page.getByText('Bilateral relationship · 2022').first()).toBeVisible();
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

	const partnerContext = page.locator('section.evidence-pane').first();
	await partnerContext.getByRole('button').first().click();
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

test('scene actions transfer focus and survive rapid reduced-motion reversal', async ({ page }) => {
	await page.emulateMedia({ reducedMotion: 'reduce' });
	await page.goto('/?country=DEU&view=relationship&partner=CHN');
	await expect(page.getByLabel('Reporter')).toHaveAttribute('data-ready', 'true');

	const relationship = page.locator('section.relationship');
	await expect(relationship).toBeVisible();

	await page.getByRole('button', { name: 'Open reported import product composition' }).click();
	const composition = page.locator('section.composition');
	await expect(composition).toBeVisible();
	await expect(composition).toBeFocused();
	await expect(page.locator('.announcement')).toContainText('DEU import products with CHN');

	await page.getByRole('button', { name: 'Relationship', exact: true }).click();
	await expect(relationship).toBeVisible();
	await expect(relationship).toBeFocused();

	await page.getByRole('button', { name: 'Products', exact: true }).click();
	await expect(composition).toBeVisible();
	await page
		.getByRole('group', { name: 'Trade network representation' })
		.getByRole('button', { name: 'Network', exact: true })
		.click();
	await expect(page.locator('section.stage svg path[role="button"]').first()).toBeVisible();
	await expect(page).not.toHaveURL(/[?&]view=/);

	await page.setViewportSize({ width: 390, height: 844 });
	await expect(page.locator('section.stage')).toHaveAttribute('data-layout', 'compact');
	const evidenceTray = page.locator('.evidence-grid');
	expect(
		await evidenceTray.evaluate((element) => element.scrollWidth > element.clientWidth)
	).toBe(true);
});

test('evidence opens a reversible bilateral history with one authoritative year', async ({
	page
}) => {
	await page.goto('/?country=DEU&view=relationship&partner=CHN');
	await expect(page.getByLabel('Reporter')).toHaveAttribute('data-ready', 'true');

	await page.getByRole('button', { name: 'Open CHN history' }).click();
	await expect(page).toHaveURL(/[?&]view=history/);
	await expect(page).toHaveURL(/[?&]year=2022/);
	const timeline = page.locator('section.timeline');
	await expect(timeline).toBeVisible();
	await expect(timeline).toBeFocused();
	await expect(
		page.getByRole('heading', { level: 2, name: 'How has DEU’s trade with CHN changed?' })
	).toBeVisible();

	const scrubber = page.getByRole('slider', { name: 'Scrub year' });
	await scrubber.fill('2012');
	await expect(page).toHaveURL(/[?&]year=2012/);
	await expect(scrubber).toBeFocused();
	await expect(page.getByText('Selected year').locator('..')).toContainText('2012');
	await expect(page.getByText('WITS · 2012').first()).toBeVisible();

	await page.getByRole('button', { name: 'Relationship', exact: true }).click();
	await expect(page).toHaveURL(/[?&]view=relationship/);
	await expect(page).toHaveURL(/[?&]year=2012/);
	await page.goBack();
	await expect(page).toHaveURL(/[?&]view=history/);
	await expect(page).toHaveURL(/[?&]year=2012/);

	await page.goto('/?country=DEU&view=history&partner=CHN&year=2010');
	await expect(page.getByRole('heading', { name: 'Bilateral trade through time' })).toBeVisible();
	await expect(page.getByText('Selected year').locator('..')).toContainText('2010');
});
