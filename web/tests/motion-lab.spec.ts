import { expect, test } from '@playwright/test';

test('motion laboratory focuses, bridges, reverses, retargets, and resets one chord', async ({
	page
}) => {
	await page.goto('/motion-lab');

	await expect(page.getByRole('heading', { level: 1 })).toContainText('Germany');
	const chord = page.getByRole('img', { name: /DEU trade chord/ });
	await expect(chord).toHaveCount(1);

	const ribbons = chord.locator('path.ribbon[tabindex="0"]');
	await expect(ribbons.first()).toBeVisible();
	const ribbonCount = await ribbons.count();
	const first = ribbons.nth(ribbonCount - 1);
	const second = ribbons.nth(ribbonCount - 2);
	const restingPath = await first.getAttribute('d');

	await first.dispatchEvent('click');
	await expect(first).toHaveAttribute('aria-pressed', 'true');
	await expect(page.locator('#instruction')).toContainText('illuminating');
	await expect.poll(() => first.getAttribute('d')).toBe(restingPath);
	const selectedLabel = chord.locator('text.partner-label.selected');
	const reporterLabel = chord.locator('text.reporter-code');
	await expect(selectedLabel).toBeVisible();
	const reporterType = await reporterLabel.evaluate((element) => {
		const style = getComputedStyle(element);
		return [style.fontFamily, style.fontSize, style.fontWeight];
	});
	await expect
		.poll(() =>
			selectedLabel.evaluate((element) => {
				const style = getComputedStyle(element);
				return [style.fontFamily, style.fontSize, style.fontWeight];
			})
		)
		.toEqual(reporterType);

	await expect(page.locator('#instruction')).toContainText('anchored upper-right');
	await expect.poll(() => first.getAttribute('d')).toBe(restingPath);

	const extracted = page.locator('.extracted-layer');
	await expect(extracted).toHaveAttribute('data-progress', '1');
	await expect(extracted.locator('path.extracted-ribbon')).toHaveAttribute('d', restingPath ?? '');
	await expect(first).toHaveAttribute('opacity', '0');

	const panel = page.locator('.panel');
	await expect(panel).toHaveAttribute('aria-hidden', 'false');
	await expect(panel.locator('[data-entity-id$="export"]')).toBeVisible();
	await expect(panel.locator('[data-entity-id$="import"]')).toBeVisible();
	await expect(panel.getByRole('heading', { name: 'What drives this relationship?' })).toBeVisible();
	await expect(
		panel.getByRole('img', { name: /reported exports and imports by year/ })
	).toBeVisible();
	const stickyTop = await panel.locator('.sticky-header').evaluate((element) =>
		element.getBoundingClientRect().top
	);
	const ribbonTop = await extracted.evaluate((element) => element.getBoundingClientRect().top);
	await panel.evaluate((element) => (element.scrollTop = 420));
	await expect
		.poll(() =>
			panel.locator('.sticky-header').evaluate((element) => element.getBoundingClientRect().top)
		)
		.toBeCloseTo(stickyTop, 0);
	await expect
		.poll(() => extracted.evaluate((element) => element.getBoundingClientRect().top))
		.toBeCloseTo(ribbonTop, 0);
	await panel.evaluate((element) => (element.scrollTop = 0));

	const productRow = panel.locator('.product-row').first();
	await productRow.getByRole('button').click();
	await expect(productRow.getByRole('button')).toHaveAttribute('aria-expanded', 'true');
	await expect(productRow.getByText(/Where else does DEU trade this product/)).toBeVisible();
	const yearPoint = panel.locator('circle.year-hit').first();
	await yearPoint.focus();
	await panel.getByRole('button', { name: /Return .* to the trade network/ }).click();
	await expect(page.locator('#instruction')).toContainText('closing');
	await expect(page.locator('#instruction')).toContainText('Select a ribbon');
	await expect(panel).toHaveCount(0);
	await expect(extracted).toHaveCount(0);
	await expect(first).toHaveAttribute('aria-pressed', 'false');

	await second.dispatchEvent('click');
	await expect(second).toHaveAttribute('aria-pressed', 'true');
	await expect(first).toHaveAttribute('aria-pressed', 'false');

	await page.keyboard.press('Escape');
	await expect(second).toHaveAttribute('aria-pressed', 'false');
	await expect(page.locator('#instruction')).toContainText('Select a ribbon');

	await page.setViewportSize({ width: 320, height: 700 });
	await page.reload();
	await expect
		.poll(async () => (await chord.boundingBox())?.width)
		.toBeLessThanOrEqual(320);
	await expect
		.poll(async () => (await chord.boundingBox())?.height)
		.toBeLessThanOrEqual(700);
	await ribbons.first().dispatchEvent('click');
	await expect(page.locator('.panel')).toBeVisible();
	await expect
		.poll(async () => (await page.locator('.panel').boundingBox())?.width)
		.toBeLessThanOrEqual(320);
});

test('motion laboratory remains operable with keyboard and reduced motion', async ({ page }) => {
	await page.emulateMedia({ reducedMotion: 'reduce' });
	await page.goto('/motion-lab');

	const ribbon = page.getByRole('img', { name: /DEU trade chord/ }).locator('path.ribbon').first();
	await ribbon.focus();
	expect(await ribbon.evaluate((element) => getComputedStyle(element).outlineStyle)).toBe('none');
	await ribbon.press('Enter');
	await expect(ribbon).toHaveAttribute('aria-pressed', 'true');
	await ribbon.press('Enter');
	await expect(ribbon).toHaveAttribute('aria-pressed', 'false');
});
