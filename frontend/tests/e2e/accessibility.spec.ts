import { expect, test } from "@playwright/test";

import { expectBasicAccessibility, mockApi } from "./fixtures";

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test("supports keyboard navigation through the primary workflow", async ({ page }) => {
  await page.goto("/");

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Overview" })).toBeFocused();

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Configuration" })).toBeFocused();
  await page.keyboard.press("Enter");

  await expect(page).toHaveURL(/\/configuration$/);
  await expect(page.getByRole("button", { name: "Start run" })).toBeVisible();
  await expectBasicAccessibility(page);
});

test("keeps loading, error, and empty states accessible", async ({ page }) => {
  await page.route("**/api/v1/health", async (route) => {
    await route.fulfill({
      status: 503,
      json: { detail: "offline" }
    });
  });

  await page.goto("/");
  await expect(page.getByText("offline")).toBeVisible();
  await expectBasicAccessibility(page);

  await page.route("**/api/v1/simulations/missing-result/result", async (route) => {
    await new Promise((resolve) => {
      setTimeout(resolve, 100);
    });
    await route.fulfill({
      status: 404,
      json: { detail: "job not found" }
    });
  });
  await page.goto("/simulations/missing-result");
  await expect(page.getByText("Loading result.")).toBeVisible();
  await expect(page.getByText("job not found")).toBeVisible();
  await expect(page.getByRole("link", { name: "Back to configuration" })).toBeVisible();
  await expectBasicAccessibility(page);
});
