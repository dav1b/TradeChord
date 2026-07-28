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

	await expect(page.locator('#instruction')).toContainText('the bridge now owns');
	await expect.poll(() => first.getAttribute('d')).toBe(restingPath);

	const bridge = page.locator('.bridge');
	await expect(bridge).toHaveAttribute('aria-hidden', 'false');
	await expect(bridge.locator('[data-entity-id$="export"]')).toBeVisible();
	await expect(bridge.locator('[data-entity-id$="import"]')).toBeVisible();
	await bridge.getByRole('button', { name: /Return .* to the trade network/ }).click();
	await expect(page.locator('#instruction')).toContainText('focused');
	await expect(bridge).toHaveAttribute('aria-hidden', 'true');

	await second.dispatchEvent('click');
	await expect(second).toHaveAttribute('aria-pressed', 'true');
	await expect(first).toHaveAttribute('aria-pressed', 'false');

	await page.keyboard.press('Escape');
	await expect(second).toHaveAttribute('aria-pressed', 'false');
	await expect(page.locator('#instruction')).toContainText('Select a ribbon');

	await page.setViewportSize({ width: 390, height: 844 });
	await page.reload();
	await expect
		.poll(async () => (await chord.boundingBox())?.width)
		.toBeLessThanOrEqual(390);
	await expect
		.poll(async () => (await chord.boundingBox())?.height)
		.toBeLessThanOrEqual(844);
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
