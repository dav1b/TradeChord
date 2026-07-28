import { expect, test } from '@playwright/test';

test('motion laboratory focuses, retargets, extracts, and resets one chord', async ({ page }) => {
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
	await expect(page.locator('#instruction')).toContainText('selected');
	await expect.poll(() => first.getAttribute('d')).toBe(restingPath);

	const focusedTransform = await first.getAttribute('transform');
	await page.getByRole('button', { name: 'Ribbon extraction' }).click();
	await expect(page.getByRole('button', { name: 'Ribbon extraction' })).toHaveAttribute(
		'aria-pressed',
		'true'
	);
	await expect
		.poll(() => first.getAttribute('transform'))
		.not.toBe(focusedTransform);

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
	await ribbon.press('Enter');
	await expect(ribbon).toHaveAttribute('aria-pressed', 'true');
	await ribbon.press('Enter');
	await expect(ribbon).toHaveAttribute('aria-pressed', 'false');
});
